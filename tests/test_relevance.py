"""Testes do filtro de relevância — casos REAIS do canal (2026-07-09/10) como fixtures."""

from __future__ import annotations

from investigator.news_fetcher.relevance import COMPANY_NAMES, is_relevant


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
    assert is_relevant("XOM raises dividend after strong quarter", "XOM")
    assert not is_relevant("Exxon raises dividend after strong quarter", "XOM")  # sem alias


def test_watchlist_completa_tem_aliases():
    """Todos os 10 tickers do produto têm pelo menos um alias (o filtro nunca fica cego)."""
    watchlist = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "JPM", "AMD", "NFLX"]
    for t in watchlist:
        assert COMPANY_NAMES.get(t), f"{t} sem aliases"
