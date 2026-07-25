"""AppTest do dashboard (visão 2026-07-12): vista Live (uma aba por empresa, gráfico grande
com eventos + tabela) e vista About (tudo o resto). Read-only por desenho.

Corre só onde o streamlit está instalado (local, stack app); no CI leve é saltado.
Os preços são simulados (monkeypatch) e o histórico partilhado NUNCA toca a rede real.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("streamlit")

import streamlit as st  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from investigator.alerts_history import HistoryEntry  # noqa: E402

APP = "app/streamlit_app.py"


def _fake_history(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    rng = np.random.default_rng(1)
    n = 60
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    if interval.endswith(("m", "h")):  # intraday: barras de hoje
        idx = pd.date_range(end=pd.Timestamp.now().floor("5min"), periods=n, freq="5min")
    else:
        idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n, freq="D")
    return pd.DataFrame({"Close": close}, index=idx)


@pytest.fixture(autouse=True)
def _limpa_caches_streamlit():
    # st.cache_data/cache_resource persistem entre instâncias de AppTest no mesmo processo —
    # sem isto, o monkeypatch de um teste podia "vazar" para o histórico/preços de outro.
    st.cache_data.clear()
    st.cache_resource.clear()
    yield


def _run(monkeypatch, history: list[HistoryEntry] | None = None) -> AppTest:
    import investigator.alerts_history as alerts_history
    import investigator.market_data.prices as prices

    monkeypatch.setattr(prices, "get_price_history", _fake_history)
    monkeypatch.setattr(alerts_history, "fetch_remote",
                        lambda url, timeout=5.0: history or [])
    at = AppTest.from_file(APP)
    at.run(timeout=120)
    return at


def _texto_visivel(at: AppTest) -> str:
    """Todo o texto renderizado (markdown + labels de expander + captions) — a tabela de
    eventos passou a ser uma lista expansível (2026-07-22), já não um dataframe."""
    partes: list[str] = []
    partes += [str(m.value) for m in at.markdown]
    partes += [str(e.label) for e in at.expander]
    partes += [str(c.value) for c in at.caption]
    return "\n".join(partes)


def test_admin_desbloqueado_mostra_painel_de_definicoes(monkeypatch):
    """Com admin desbloqueado, o painel de definições renderiza os sliders dos tunables
    (guest, o default dos outros testes, não os mostra)."""
    import investigator.alerts_history as alerts_history
    import investigator.market_data.prices as prices

    monkeypatch.setattr(prices, "get_price_history", _fake_history)
    monkeypatch.setattr(alerts_history, "fetch_remote", lambda url, timeout=5.0: [])
    at = AppTest.from_file(APP)
    at.session_state["admin_ok"] = True   # já autenticado (salta o botão Unlock)
    at.secrets["admin_password"] = "x"
    at.run(timeout=120)
    assert not at.exception
    assert len(at.slider) >= 5   # threshold, similaridade, materialidade, teto, half-life
    assert any("Alert settings" in str(e.label) for e in at.expander)


def test_precos_nan_degrada_com_graca(monkeypatch):
    """Um fetch de preços a devolver NaN não pode mostrar '$nan / +nan%': cai no aviso
    gracioso 'Not enough data' (bug visto num screenshot ao vivo com o yfinance a falhar)."""
    import investigator.alerts_history as alerts_history
    import investigator.market_data.prices as prices

    def nan_hist(ticker, **kw):
        idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=30, freq="D")
        return pd.DataFrame({"Close": [np.nan] * 30}, index=idx)

    monkeypatch.setattr(prices, "get_price_history", nan_hist)
    monkeypatch.setattr(alerts_history, "fetch_remote", lambda url, timeout=5.0: [])
    at = AppTest.from_file(APP)
    at.run(timeout=120)
    assert not at.exception
    assert any("Not enough data" in str(w.value) for w in at.warning)


def test_vista_live_sem_excecoes_uma_aba_por_empresa(monkeypatch):
    at = _run(monkeypatch)
    assert not at.exception
    # seletor de empresa (substitui st.tabs: só a escolhida é renderizada → app leve);
    # o radio das vistas fica na sidebar, o de empresa + o de intervalo no corpo
    radios = {tuple(r.options) for r in at.radio}
    assert any(len(ops) >= 10 for ops in radios)  # 10 tickers da watchlist
    assert len(at.sidebar.radio) == 1
    assert list(at.sidebar.radio[0].options) == ["📊 Live", "ℹ️ About"]
    # só UMA empresa renderizada por interação (a razão do ganho de velocidade)
    assert len(at.metric) == 1


def test_risco_de_fundo_e_caption_compacta(monkeypatch):
    at = _run(monkeypatch)
    assert not at.exception
    captions = [c.value for c in at.caption]
    assert any("Background risk" in c for c in captions)


def test_risco_ausente_sem_modelo_nao_rebenta(monkeypatch):
    import investigator.triage.infer as infer

    monkeypatch.setattr(infer, "load_context_bundle", lambda path=None: None)
    at = _run(monkeypatch)
    assert not at.exception
    captions = [c.value for c in at.caption]
    assert not any("Background risk" in c for c in captions)


def test_eventos_do_canal_aparecem_na_lista_expansivel(monkeypatch):
    hist = [HistoryEntry(date="2026-07-08", ticker="AAPL", kind="market",
                         text="Anomaly detected for AAPL: a very specific unique marker text")]
    at = _run(monkeypatch, history=hist)
    assert not at.exception
    # tabela única expansível: o facto está no cabeçalho da linha (label do expander)
    assert "a very specific unique marker text" in _texto_visivel(at)
    assert any("Alert history" in c.value for c in at.subheader)


def test_sem_historico_mostra_aviso_gracioso(monkeypatch):
    at = _run(monkeypatch, history=[])
    assert not at.exception
    captions = [c.value for c in at.caption]
    assert any("No shared event history reachable" in c for c in captions)


def test_resumo_diario_do_canal_em_expander(monkeypatch):
    hist = [HistoryEntry(date="2026-07-10", ticker="MARKET", kind="summary",
                         text="Daily close summary\n• AAPL: +0.10% (z +0.05)")]
    at = _run(monkeypatch, history=hist)
    assert not at.exception
    labels = [e.label for e in at.expander]
    assert any("Daily close summary" in lbl for lbl in labels)


def test_vista_about_tem_metodo_avaliacao_e_demo(monkeypatch):
    at = _run(monkeypatch)
    at.sidebar.radio[0].set_value("ℹ️ About").run(timeout=120)
    assert not at.exception
    titles = [t.value for t in at.title]
    assert any("About" in t for t in titles)
    headers = [h.value for h in at.header]
    assert any("Evaluation" in h for h in headers)
    labels = [e.label for e in at.expander]
    assert any("retrieval engine" in lbl for lbl in labels)  # a única "ação", fora da Live


def test_overview_line_formata_chips_por_direcao():
    """Faixa 'Market now' (2026-07-13): formatter PURO — verde/vermelho por direção, ordem
    da watchlist, tickers sem dados omitidos. (A busca em lote respeita INVESTIGATOR_OFFLINE
    e é fail-open: sem dados, a faixa não aparece — coberto pelos AppTests acima.)"""
    import importlib.util

    spec = importlib.util.spec_from_file_location("streamlit_app_puro", APP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # bare mode: as chamadas st.* de topo são no-ops

    moves = {"NVDA": -0.045, "AAPL": 0.004, "MSFT": None}
    linha = mod._overview_line(moves, ["AAPL", "MSFT", "NVDA", "ZZZZ"])
    assert ":green[**AAPL** +0.4%]" in linha
    assert ":red[**NVDA** -4.5%]" in linha or ":red[**NVDA** −4.5%]" in linha
    assert "MSFT" not in linha and "ZZZZ" not in linha  # sem dados → sem chip
    assert linha.index("AAPL") < linha.index("NVDA")    # ordem da watchlist
    assert mod._overview_line({}, ["AAPL"]) == ""


def test_app_boota_sem_plotly(monkeypatch):
    """A app NUNCA cai por causa do gráfico: sem plotly, degrada para line_chart."""
    import investigator.alerts_history as alerts_history
    import investigator.market_data.prices as prices

    monkeypatch.setenv("INVESTIGATOR_NO_PLOTLY", "1")
    monkeypatch.setattr(prices, "get_price_history", _fake_history)
    monkeypatch.setattr(alerts_history, "fetch_remote", lambda url, timeout=5.0: [])
    at = AppTest.from_file(APP)
    at.run(timeout=120)
    assert not at.exception
    captions = [c.value for c in at.caption]
    assert any("Interactive chart unavailable" in c for c in captions)
