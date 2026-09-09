"""O manifesto dos preços é a prova de proveniência que faltava.

O corpus de notícias estava fixado por `sha256`; os preços não estavam fixados por nada. Pior
do que a falta de fixação era a falta de registo: por baixo do `load_close_series` há uma
cadeia de cinco fontes, e se o yfinance falhasse num ticker outra servia — sem que isso
aparecesse em lado nenhum. A mesma janela podia ser servida por fontes diferentes em execuções
diferentes, e o resultado seria indistinguível.

`docs/design/precos_manifest.json` é versionado, e regista por série a fonte, a dimensão, os
extremos e a soma de controlo do ficheiro. Este teste garante que o registo é internamente
coerente e que descreve o que a tese usa. Os valores em si ficam guardados pelo git: qualquer
alteração aparece no diff, que é onde tem de aparecer.

Ver `docs/design/reproducao_corpus_2026-09-09.md`, secção 10.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MANIFESTO = RAIZ / "docs" / "design" / "precos_manifest.json"
CACHE = RAIZ / "data" / "prices"

#: As catorze empresas do corpus da tese — ver `tests/test_corpus_canonico.py`.
TICKERS = {"TSLA", "NVDA", "AAPL", "MSFT", "WMT", "CVX", "XOM",
           "KO", "AMZN", "JPM", "GOOGL", "JNJ", "PFE", "BAC"}
JANELA = ("2018-01-01", "2023-12-26")  # fim = última notícia + 10 dias, margem para o +5d


def carregar() -> dict:
    assert MANIFESTO.exists(), (
        f"manifesto ausente: {MANIFESTO.relative_to(RAIZ)} — "
        "corre `python -m scripts.build_kb --news data/fnspid_news_subset.csv --sbert`")
    return json.loads(MANIFESTO.read_text(encoding="utf-8"))


def test_ha_uma_serie_por_empresa_do_corpus() -> None:
    m = carregar()
    obtidos = {nome.split("_", 1)[0] for nome in m["series"]}
    assert obtidos == TICKERS, f"em falta: {TICKERS - obtidos} · a mais: {obtidos - TICKERS}"


def test_a_janela_e_a_do_corpus() -> None:
    m = carregar()
    assert (m["janela"]["inicio"], m["janela"]["fim"]) == JANELA
    for nome in m["series"]:
        _, inicio, fim = nome.split("_")
        assert (inicio, fim) == JANELA, f"{nome} está fora da janela do corpus"


def test_a_proveniencia_esta_registada_serie_a_serie() -> None:
    """Se alguma série vier de uma fonte de recurso, isso tem de estar escrito."""
    m = carregar()
    for nome, reg in m["series"].items():
        assert reg["fonte"], f"{nome} sem fonte registada"
        assert reg["dias"] > 0
        assert reg["primeiro"] and reg["ultimo"]
        assert len(reg["sha256"]) == 64


def test_todas_as_series_vieram_da_mesma_fonte() -> None:
    """Não é uma exigência de desenho — é um facto a vigiar.

    A 2026-09-09 as catorze séries vieram todas do yfinance. Se uma passar a vir do Stooq ou
    do Alpha Vantage, os preços deixam de ser homogéneos e isso tem de ser uma decisão, não uma
    surpresa. Este teste falha para obrigar a olhar.
    """
    m = carregar()
    fontes = {reg["fonte"] for reg in m["series"].values()}
    assert fontes == {"yfinance"}, f"séries servidas por fontes diferentes: {sorted(fontes)}"


@pytest.mark.skipif(not CACHE.exists(), reason="cache local ausente (data/** é gitignored)")
def test_os_ficheiros_em_disco_batem_com_as_somas_registadas() -> None:
    from investigator.market_data import price_cache

    problemas = price_cache.verificar(CACHE)
    assert not problemas, "\n".join(problemas)
