"""Testes do news_fetcher (parsing puro, sem rede)."""

from investigator.news_fetcher.fetcher import (
    NewsItem,
    _rss_date_to_iso,
    parse_finnhub_news,
    parse_rss,
)


def test_parse_finnhub_news():
    payload = [
        {"datetime": 1685000000, "headline": "Nvidia surges on AI demand",
         "url": "http://x", "source": "Reuters"},
        {"datetime": 0, "headline": "sem timestamp"},      # ts falsy → ignorado
        {"datetime": 1685100000, "headline": "   "},        # título vazio → ignorado
    ]
    items = parse_finnhub_news(payload, "nvda")
    assert len(items) == 1
    it = items[0]
    assert isinstance(it, NewsItem)
    assert it.ticker == "NVDA"
    assert it.date == "2023-05-25"
    assert it.headline == "Nvidia surges on AI demand"
    assert it.source == "Reuters"


def test_parse_rss():
    xml = """<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item>
        <title>Apple hits record high</title>
        <pubDate>Wed, 02 Oct 2002 13:00:00 GMT</pubDate>
        <link>http://a</link>
      </item>
      <item><title></title><pubDate>Thu, 03 Oct 2002 13:00:00 GMT</pubDate></item>
    </channel></rss>"""
    items = parse_rss(xml, ticker="aapl")
    assert len(items) == 1
    it = items[0]
    assert it.headline == "Apple hits record high"
    assert it.date == "2002-10-02"
    assert it.ticker == "AAPL"
    assert it.url == "http://a"
    assert it.source == "rss"


def test_rss_date_invalida_da_vazio():
    assert _rss_date_to_iso("") == ""
    assert _rss_date_to_iso("não é uma data") == ""
    assert _rss_date_to_iso("Wed, 02 Oct 2002 13:00:00 GMT") == "2002-10-02"


def test_parse_rss_aceita_bytes_com_declaracao_de_codificacao():
    """Regressão: feeds RSS reais abrem com `<?xml ... encoding="UTF-8"?>`. Passar a str
    crua a ET.fromstring levanta ValueError; a partir de bytes (o `resp.content` que o
    fetch_rss_feed agora usa) funciona — provado aqui com uma declaração de codificação."""
    xml_bytes = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<rss version="2.0"><channel>'
        b"<item><title>Tesla recalls vehicles</title>"
        b"<pubDate>Wed, 02 Oct 2002 13:00:00 GMT</pubDate><link>http://t</link></item>"
        b"</channel></rss>"
    )
    items = parse_rss(xml_bytes, ticker="tsla")
    assert len(items) == 1
    assert items[0].headline == "Tesla recalls vehicles"
    assert items[0].ticker == "TSLA"
    assert items[0].date == "2002-10-02"
