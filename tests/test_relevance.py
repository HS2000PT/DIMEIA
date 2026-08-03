"""Testes do filtro de relevância — casos REAIS do canal (2026-07-09/10) como fixtures."""

from __future__ import annotations

from pathlib import Path

from investigator.news_fetcher.relevance import (
    COMPANY_DISPLAY,
    COMPANY_NAMES,
    is_relevant,
)


def test_rejeita_lixo_real_do_canal():
    """Manchetes que o Finnhub etiquetou mal e que REALMENTE alertaram no canal."""
    assert not is_relevant(
        "Six Months In, AZA Law Firm's Dallas Office Tracks Toward Its Year-One Plan", "AMD")
    assert not is_relevant("Top S&P500 movers in Thursday's session", "AMD")
    assert not is_relevant(
        "Stay informed about the most active stocks in the S&P500 index on Friday's session.",
        "TSLA")
    assert not is_relevant("Sector Update: Tech Stocks Gain Late Afternoon", "META")
    assert not is_relevant(
        "Micron downgraded, Five Below upgraded: Wall Street's top analyst calls", "TSLA")


def test_aceita_noticias_genuinas_do_canal():
    assert is_relevant("Meta's new AI chips will begin production in September", "META")
    assert is_relevant("EU orders Meta to make apps less 'addictive'", "META")
    assert is_relevant("Price Prediction: Up 144% YTD, Where Will AMD Be In 2027?", "AMD")
    assert is_relevant(
        "Elon Musk Lost His Trillionaire Status as SpaceX Shares Dropped 26%. "
        "Are Tesla and SpaceX Stock Still a Buy?", "TSLA")


def test_alias_e_ticker_contam_como_mencao():
    assert is_relevant("Facebook parent beats earnings expectations", "META")
    assert is_relevant("NFLX pops on subscriber growth", "NFLX")
    assert is_relevant("Alphabet unveils new Gemini model", "GOOGL")


def test_palavra_inteira_evita_falsos_positivos():
    assert not is_relevant("Heavy metal exports rise in Q3", "META")  # 'metal' ≠ 'meta'
    assert not is_relevant("Amsterdam hosts chip conference", "AMD")  # 'Amsterdam' ≠ 'AMD'


def test_case_insensitive_e_vazios():
    assert is_relevant("APPLE ANNOUNCES RECORD BUYBACK", "AAPL")
    assert not is_relevant("", "AAPL")
    assert not is_relevant("   ", "AAPL")


def test_ticker_fora_do_mapa_usa_so_o_simbolo():
    """O fallback honesto: sem aliases, só o próprio símbolo conta como menção.

    Era demonstrado com a XOM, que entretanto entrou na watchlist e ganhou aliases. Passou
    para a CVX, que continua fora do mapa — se um dia entrar também, este teste falha em
    vez de deixar de testar o que diz que testa.
    """
    assert "CVX" not in COMPANY_NAMES, "escolher outro ticker fora do mapa para este teste"
    assert is_relevant("CVX raises dividend after strong quarter", "CVX")
    assert not is_relevant("Chevron raises dividend after strong quarter", "CVX")


def test_watchlist_completa_tem_aliases():
    """Todo o ticker do produto tem pelo menos um alias — o filtro nunca fica cego.

    A watchlist é lida do `config/alerts.yaml` e não escrita à mão aqui. A lista fixa que
    estava neste teste tinha dez nomes e continuaria a passar depois de a watchlist crescer
    para doze: teria deixado de cobrir os dois nomes novos sem falhar uma única vez, que é
    a pior maneira de um teste morrer.
    """
    import yaml

    caminho = Path(__file__).resolve().parents[1] / "config" / "alerts.yaml"
    cfg = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    watchlist = cfg.get("market", {}).get("tickers") or []
    assert len(watchlist) >= 10, "watchlist não foi lida do ficheiro"
    for t in watchlist:
        assert COMPANY_NAMES.get(t), f"{t} sem aliases"
        assert COMPANY_DISPLAY.get(t), f"{t} sem nome legível"
