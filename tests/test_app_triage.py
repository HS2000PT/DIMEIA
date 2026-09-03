"""AppTest do dashboard — os testes SÃO os critérios de aceitação, em forma executável.

Cada teste nomeia o critério que verifica em `docs/design/app_acceptance.md`. Esse documento
foi escrito ANTES do código precisamente porque a app já tinha sido redesenhada 4× e rejeitada
sempre por critério estético — que não tem condição de paragem. Isto é a condição de paragem:
quando estes testes estiverem verdes, a app está feita.

Corre só onde o streamlit está instalado; no CI leve é saltado. Preços simulados; o histórico
partilhado NUNCA toca a rede real.
"""

from __future__ import annotations

import zlib

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("streamlit")

import streamlit as st  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from investigator.alerts_history import HistoryEntry  # noqa: E402

APP = "app/streamlit_app.py"


def _fake_history(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Série determinística por ticker (a semente vem do nome → movimentos distintos).

    ⚠️ A semente vinha de `hash(ticker)`, e isso **não era determinístico**: o Python
    aleatoriza o hash de strings por processo (PYTHONHASHSEED), portanto cada corrida da suite
    gerava preços diferentes. Era isso que fazia o teste F2 falhar de vez em quando e passar
    sozinho a seguir — a série mudava, um ticker às vezes destacava-se e às vezes não.
    `crc32` é estável entre processos e entre máquinas, que é o que "determinístico" tem de
    querer dizer num teste.
    """
    rng = np.random.default_rng(zlib.crc32(ticker.encode()) % 1000)
    n = 60
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.012, n)))
    if interval.endswith(("m", "h")):
        idx = pd.date_range(end=pd.Timestamp.now().floor("5min"), periods=n, freq="5min")
    else:
        idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n, freq="D")
    return pd.DataFrame({"Close": close}, index=idx)


@pytest.fixture(autouse=True)
def _isola(monkeypatch):
    """Os caches do Streamlit persistem entre AppTests no mesmo processo — sem limpar, o
    monkeypatch de um teste vaza para outro."""
    st.cache_data.clear()
    st.cache_resource.clear()
    monkeypatch.setenv("INVESTIGATOR_OFFLINE", "1")
    monkeypatch.setenv("INVESTIGATOR_NO_PLOTLY", "1")
    import investigator.market_data.prices as prices

    monkeypatch.setattr(prices, "get_price_history", _fake_history)
    yield


def _com_historico(monkeypatch, entries):
    import investigator.alerts_history as ah

    monkeypatch.setattr(ah, "fetch_remote", lambda *a, **k: entries)


def _texto(at) -> str:
    """Todo o texto visível da página, para asserções de conteúdo."""
    partes: list[str] = []
    for coll in (at.markdown, at.caption, at.subheader, at.info, at.success,
                 at.warning, at.error):
        partes += [str(el.value) for el in coll]
    partes += [str(e.label) for e in at.expander]
    return "\n".join(partes)


# ── F1 / F6: abre em Today, sem cliques, sem estado vazio, sem traceback ────────
def test_F1_abre_em_today_sem_estado_vazio(monkeypatch):
    _com_historico(monkeypatch, [])
    at = AppTest.from_file(APP, default_timeout=90).run()
    assert not at.exception
    txt = _texto(at)
    assert "Today" in txt
    assert ("stood out" in txt) or ("Quiet" in txt) or ("unavailable" in txt)


def test_F6_sem_dados_de_preco_degrada_com_mensagem_honesta(monkeypatch):
    import investigator.market_data.prices as prices

    def _morto(*a, **k):
        raise RuntimeError("todas as fontes em baixo")

    monkeypatch.setattr(prices, "get_price_history", _morto)
    _com_historico(monkeypatch, [])
    at = AppTest.from_file(APP, default_timeout=90).run()
    assert not at.exception  # nunca traceback
    assert "unavailable" in _texto(at).lower()


# ── F3: a promessa aparece EXATAMENTE uma vez ───────────────────────────────────
def test_F3_promessa_aparece_uma_unica_vez(monkeypatch):
    _com_historico(monkeypatch, [])
    at = AppTest.from_file(APP, default_timeout=90).run()
    texto = _texto(at)
    assert texto.count("Markets move. We investigate.") == 1
    assert texto.count("never predicts prices and never gives advice") == 1


# ── F4: zero previsões e zero conselho em texto visível, em TODAS as vistas ─────
@pytest.mark.parametrize("vista", ["📊 Today", "🔎 Ticker", "📐 Method"])
def test_F4_sem_previsao_nem_conselho(monkeypatch, vista):
    _com_historico(monkeypatch, [HistoryEntry("2026-07-28", "AAPL", "market", "📉 AAPL -2.10%")])
    at = AppTest.from_file(APP, default_timeout=90).run()
    at.sidebar.radio[0].set_value(vista).run()
    assert not at.exception
    low = _texto(at).lower()
    for proibido in ("will rise", "will fall", "we recommend", "should buy", "should sell",
                     "price target", "guaranteed", "bullish", "bearish"):
        assert proibido not in low, f"{proibido!r} apareceu em {vista}"


# ── F2 / F5: cada vista responde à SUA pergunta ─────────────────────────────────
def test_F2_today_mostra_a_decomposicao_na_propria_linha(monkeypatch):
    """O diferenciador do produto tem de estar visível SEM clicar."""
    _com_historico(monkeypatch, [])
    at = AppTest.from_file(APP, default_timeout=90).run()
    txt = _texto(at)
    if "stood out" in txt:  # dia calmo também é estado válido
        assert "market ·" in txt and "sector ·" in txt


def test_volume_invulgar_aparece_como_racio_legivel(monkeypatch):
    """A segunda metade de "isto é invulgar?": com quanta gente a negociar.

    Duas regras de produto ao mesmo tempo: quando o volume é invulgar mostra-se como **rácio**
    ("3,2× usual volume"), porque um z-score do log do volume não comunica a ninguém; e quando é
    normal **não se diz nada**, porque anunciar "1,0× o habitual" em cada linha seria ruído.
    """
    import re

    _com_historico(monkeypatch, [])
    at = AppTest.from_file(APP, default_timeout=90).run()
    assert not at.exception
    txt = _texto(at)
    for achado in re.findall(r"([\d.]+)× usual volume", txt):
        # Se apareceu, é porque passou o limiar — nunca pode ser um valor banal.
        assert float(achado) > 1.0, f"volume de {achado}× não devia ter sido anunciado"


def test_F5_ticker_responde_empresa_ou_mercado(monkeypatch):
    _com_historico(monkeypatch, [])
    at = AppTest.from_file(APP, default_timeout=90).run()
    at.sidebar.radio[0].set_value("🔎 Ticker").run()
    assert not at.exception
    assert "Is it the company or the market?" in _texto(at)


def test_F5_method_expoe_os_congelados_incluindo_o_negativo(monkeypatch):
    _com_historico(monkeypatch, [])
    at = AppTest.from_file(APP, default_timeout=90).run()
    at.sidebar.radio[0].set_value("📐 Method").run()
    assert not at.exception
    txt = _texto(at)
    assert "reproducible" in txt
    assert "No text model beat the volatility baseline" in txt


# ── N1: uma interação renderiza UM ticker (desempenho) ──────────────────────────
def test_N1_ticker_view_renderiza_apenas_um_ticker(monkeypatch):
    """A regra de desempenho é 'só o ticker escolhido é renderizado', não 'só uma métrica':
    o painel de decomposição acrescenta legitimamente 3 métricas AO MESMO ticker. O que não
    pode acontecer é aparecer um SEGUNDO ticker da watchlist (era o custo do st.tabs antigo,
    que renderizava os 10 a cada interação)."""
    _com_historico(monkeypatch, [])
    at = AppTest.from_file(APP, default_timeout=90).run()
    at.sidebar.radio[0].set_value("🔎 Ticker").run()
    escolhido = at.radio(key="ticker_picker").value
    outros = [t for t in at.radio(key="ticker_picker").options if t != escolhido]
    rotulos = " ".join(str(m.label) for m in at.metric)
    presentes = [t for t in outros if t in rotulos]
    assert not presentes, f"renderizou tickers não escolhidos: {presentes}"


# ── N2: nada em português no texto visível ──────────────────────────────────────
def test_N2_sem_portugues_visivel(monkeypatch):
    _com_historico(monkeypatch, [])
    at = AppTest.from_file(APP, default_timeout=90).run()
    low = _texto(at).lower()
    for pt in (" não ", " está ", " mercado ", " ação ", "notícia", " ontem "):
        assert pt not in low, f"português visível: {pt!r}"


# ── Espelho do canal: a app mostra, nunca recalcula ─────────────────────────────
def test_eventos_sao_o_texto_exato_do_canal(monkeypatch):
    exato = "📉 AAPL (Apple) · -2.10% today\nSplit: -1.85% market"
    _com_historico(monkeypatch, [HistoryEntry("2026-07-28", "AAPL", "market", exato)])
    at = AppTest.from_file(APP, default_timeout=90).run()
    at.sidebar.radio[0].set_value("🔎 Ticker").run()
    at.radio(key="ticker_picker").set_value("AAPL").run()
    assert any(exato in str(el.value) for el in at.text)


def test_sem_historico_di_lo_honestamente(monkeypatch):
    _com_historico(monkeypatch, [])
    at = AppTest.from_file(APP, default_timeout=90).run()
    at.sidebar.radio[0].set_value("🔎 Ticker").run()
    assert "No alerts recorded" in _texto(at)


# ── Latência: só aparece quando foi MEDIDA ──────────────────────────────────────
def test_latencia_ausente_sem_carimbos(monkeypatch):
    _com_historico(monkeypatch, [HistoryEntry("2026-07-28", "AAPL", "market", "x")])
    at = AppTest.from_file(APP, default_timeout=90).run()
    assert "Median time from event to delivery" not in _texto(at)


def test_latencia_mostrada_com_carimbos(monkeypatch):
    _com_historico(monkeypatch, [
        HistoryEntry("2026-07-28", "AAPL", "market", "x",
                     event_at="2026-07-28T13:00:00Z", sent_at="2026-07-28T13:00:45Z"),
    ])
    at = AppTest.from_file(APP, default_timeout=90).run()
    assert "Median time from event to delivery" in _texto(at)
