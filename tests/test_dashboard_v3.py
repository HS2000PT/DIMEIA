"""O portão da promoção: os critérios da v3 que só se verificam com a app a correr.

**Porque é que este ficheiro existe.** `docs/design/dashboard_acceptance.md` diz que a v1
fica no ar até a v3 passar **todos** os critérios. Metade deles — V1, V2, V6, V7, V8, H1,
H4, C1, C2 — nunca tinham sido verificados: os testes existentes cobrem a camada pura
(`test_verdict.py`, `test_tables.py`), que é onde vivem V3/V4/V5/H2/H3, mas ninguém tinha
posto a app a correr e perguntado se a página cumpre o que o documento promete.

Sem isto, "a v3 passa os critérios" seria uma opinião. A condição de paragem deste projecto
já falhou seis vezes por ser estética; a diferença desta vez é ter uma resposta executável.

Os preços são substituídos por séries determinísticas (o mesmo padrão de
`test_app_triage.py`) e a rede é desligada, para o portão medir a **página** e não o estado
do mercado nem a disponibilidade do GitHub.
"""

from __future__ import annotations

import re
import zlib

import numpy as np
import pandas as pd
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

PAINEL = "app/dashboard.py"
TIMEOUT = 300


def _fake_history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """Um ano de barras por ticker, com semente estável no nome.

    Um ano e não 60 dias de propósito: a contagem de raridade exige ≥30 observações e o
    veredicto muda de forma conforme houver ou não história. Um stub curto testaria um
    caminho que o utilizador nunca vê.
    """
    # `hash` de strings e aleatorizado por processo (PYTHONHASHSEED) — ver a nota
    # em test_app_triage.py. crc32 e estavel entre processos e maquinas.
    rng = np.random.default_rng(zlib.crc32(ticker.encode()) % 1000)
    n = 260
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.012, n)))
    volume = rng.integers(1_000_000, 5_000_000, n)
    if interval.endswith(("m", "h")):
        idx = pd.date_range(end=pd.Timestamp.now().floor("5min"), periods=n, freq="5min")
    else:
        idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n, freq="B")
    return pd.DataFrame({"Close": close, "Volume": volume}, index=idx)


@pytest.fixture(autouse=True)
def _isola(monkeypatch):
    """Sem rede e sem caches herdadas.

    Os caches do Streamlit são globais ao processo e sobrevivem entre AppTests — sem os
    limpar, o stub de um teste vaza para o seguinte e o resultado deixa de significar nada.
    """
    st.cache_data.clear()
    st.cache_resource.clear()
    monkeypatch.setenv("INVESTIGATOR_OFFLINE", "1")
    monkeypatch.setenv("INVESTIGATOR_NO_PLOTLY", "1")
    import investigator.market_data.prices as prices

    monkeypatch.setattr(prices, "get_price_history", _fake_history)
    yield


def _html(at: AppTest) -> str:
    """O que o utilizador vê. Blocos `<style>` fora.

    Sem os retirar, um teste de "nada de português visível" apanha os **comentários do
    CSS**, que estão em PT-PT por convenção do projecto e que ninguém lê no ecrã. Falhar
    por causa deles seria o teste a medir o código-fonte em vez da página.
    """
    bruto = " ".join(str(m.value) for m in at.markdown)
    bruto = re.sub(r"<style>.*?</style>", " ", bruto, flags=re.S)
    return re.sub(r"<!--.*?-->", " ", bruto, flags=re.S)


def _corre(**params) -> AppTest:
    at = AppTest.from_file(PAINEL, default_timeout=TIMEOUT)
    for chave, valor in params.items():
        at.query_params[chave] = valor
    at.run()
    assert not at.exception, f"a página levantou: {[str(e.value)[:300] for e in at.exception]}"
    return at


# ── V1: a grelha abre com tudo, nada privilegiado ────────────────────────────────────

def test_v1_a_grelha_abre_com_a_watchlist_inteira() -> None:
    at = _corre()
    html = _html(at)
    assert html.count('class="card ') >= 10, "a grelha não desenhou os cartões"
    assert html.count('class="verdict"') == html.count('class="card '), (
        "todo o cartão tem de abrir com um veredicto — é a lei de desenho §6.2")


def test_v1_nenhuma_empresa_esta_seleccionada_ao_abrir() -> None:
    """Abrir num ticker seria escolher por ele. A grelha não privilegia ninguém."""
    html = _html(_corre())
    assert "All companies" not in html, "isto é a vista de detalhe, não a grelha"


# ── V8: ligação profunda ─────────────────────────────────────────────────────────────

def test_v8_o_url_isola_uma_empresa() -> None:
    at = _corre(t="NVDA")
    html = _html(at)
    assert "NVDA" in html
    assert 'class="card ' not in html, "a vista de detalhe não desenha a grelha"
    assert "All companies" in html, "sem regresso, o detalhe é um beco"


def test_v8_um_ticker_invalido_cai_na_grelha_sem_rebentar() -> None:
    """Falhar aberto: um URL adulterado mostra a grelha, não um traceback."""
    html = _html(_corre(t="NAOEXISTE"))
    assert 'class="card ' in html


# ── V7: a avaliação vive numa página, fora do caminho do produto ─────────────────────

_NUMEROS_DE_AVALIACAO = ("PR-AUC", "precision@", "P@5")


def test_v7_a_avaliacao_nao_polui_a_grelha_nem_o_detalhe() -> None:
    for params in ({}, {"t": "NVDA"}):
        html = _html(_corre(**params))
        for termo in _NUMEROS_DE_AVALIACAO:
            assert termo not in html, (
                f"'{termo}' é conteúdo de avaliação e o público é o investidor: "
                f"pertence a ?view=method, não a esta vista")


def test_v7_a_pagina_do_metodo_existe_e_tem_os_numeros() -> None:
    html = _html(_corre(view="method"))
    assert any(t in html for t in _NUMEROS_DE_AVALIACAO), (
        "a página do método é onde os números congelados vivem")


# ── H1: a promessa aparece exactamente uma vez ───────────────────────────────────────

_PROMESSA = "never a forecast"


@pytest.mark.parametrize("params", [{}, {"t": "NVDA"}])
def test_h1_a_promessa_aparece_uma_vez_nas_vistas_de_produto(params: dict) -> None:
    """Repetida lê-se como defensiva; ausente, o leitor não sabe o que isto recusa fazer."""
    assert _html(_corre(**params)).count(_PROMESSA) == 1


def test_h1_a_pagina_do_metodo_nao_repete_a_promessa_curta() -> None:
    """H1 proíbe **repetir**, não obriga cada página a recitar.

    A página do método declara a posição por extenso, na secção "what this system never
    does" — que é mais forte e mais específica do que a frase curta do rodapé. Somar as
    duas seria exactamente a repetição defensiva que o critério existe para travar.
    """
    html = _html(_corre(view="method"))
    assert html.count(_PROMESSA) <= 1
    assert "No price targets" in html, "a posição tem de estar declarada nalgum lado"


# ── H2: zero previsões, agora na página inteira e não só nas frases ──────────────────

_PROIBIDO_NA_PAGINA = (
    "will rise", "will fall", "we expect", "price target", "recommend",
    "should buy", "should sell", "bullish", "bearish", "projected to",
)


@pytest.mark.parametrize("params", [{}, {"t": "NVDA"}])
def test_h2_as_vistas_de_produto_nao_prometem_nada(params: dict) -> None:
    html = _html(_corre(**params)).lower()
    for palavra in _PROIBIDO_NA_PAGINA:
        assert palavra not in html, f"'{palavra}' apareceu na vista {params or 'grelha'}"


def test_h2_a_pagina_do_metodo_usa_os_termos_para_os_NEGAR() -> None:
    """Aqui uma lista de palavras proibidas dá falso positivo, e a razão interessa.

    A página do método escreve *"No price targets, no buy or sell calls"* — o sistema a
    declarar o que **nunca** faz. Uma lista de proibições apanha a frase e não vê a
    negação: é a mesma lição que o red team do narrador já tinha dado a este projecto
    (uma blocklist de linguagem natural perde sempre, e perde nos dois sentidos).

    Por isso a regra aqui é ao contrário: exige-se a **declaração**, em vez de se proibir
    o termo.
    """
    html = _html(_corre(view="method"))
    assert "No price targets" in html
    assert "no buy or sell calls" in html


# ── H4: nenhum score que a medição não sustente ──────────────────────────────────────

def test_h4_o_score_fundido_de_convergencia_nao_aparece() -> None:
    """Ganha em 1 de 3 orçamentos (`evaluation_convergence.md`). Fica fora, por regra."""
    for params in ({}, {"t": "NVDA"}):
        html = _html(_corre(**params)).lower()
        assert "convergence score" not in html
        assert "of 4 signals" not in html, (
            "um dos quatro sinais é a probabilidade da triagem, que H2 proíbe no produto")


def test_h4_nao_ha_cracha_de_tipo_de_evento() -> None:
    """Silhueta 0,084 e rubrica a cobrir 15,1% — um crachá errado é pior do que nenhum."""
    html = _html(_corre(t="NVDA")).lower()
    for rotulo in ("event type", "earnings event", "regulatory event"):
        assert rotulo not in html


# ── V6: os precedentes existem no produto ────────────────────────────────────────────

def test_v6_o_detalhe_fala_de_precedentes() -> None:
    """A pergunta 3 da tese. Não aparecia em NENHUMA das duas apps até à v3."""
    html = _html(_corre(t="NVDA")).lower()
    assert "precedent" in html or "past case" in html or "similar" in html


def test_v6_a_moldura_tema_diferente_de_direccao_acompanha_sempre() -> None:
    """H3: parecido no tema não é parecido na direcção. É o CS3 da tese, e é uma força."""
    html = _html(_corre(t="NVDA")).lower()
    if "precedent" in html or "past case" in html:
        assert "direction" in html, (
            "mostrar precedentes sem a moldura convida a lê-los como previsão")


# ── Degradação honesta ───────────────────────────────────────────────────────────────

def test_sem_precos_a_pagina_diz_isso_e_nao_rebenta(monkeypatch) -> None:
    """A fonte de preços em baixo tem de dar uma mensagem, nunca um traceback."""
    import investigator.market_data.prices as prices

    def _morre(*_a, **_k):
        raise RuntimeError("fonte em baixo")

    monkeypatch.setattr(prices, "get_price_history", _morre)
    at = AppTest.from_file(PAINEL, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception, "uma fonte em baixo não pode derrubar a página"
    assert "No market data" in _html(at)


# ── N2 herdado: nada de português visível ────────────────────────────────────────────

@pytest.mark.parametrize("params", [{}, {"t": "NVDA"}, {"view": "method"}])
def test_n2_a_interface_esta_toda_em_ingles(params: dict) -> None:
    """O código e os comentários são PT-PT; o que o utilizador lê é EN, sem excepção."""
    html = _html(_corre(**params)).lower()
    for palavra in (" não ", " está ", "empresa", "movimento", "notícia", " dias ",
                    "veredicto", "grelha"):
        assert palavra not in html, f"português visível: {palavra!r}"
