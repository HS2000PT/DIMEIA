"""Camada live: obtenção de notícias financeiras (Gatilho 2) via Finnhub e RSS.

Desenho (igual ao `market_data`/`telegram_bot`): separamos o **parsing** (puro, testável sem
rede) do **HTTP** (invólucros finos, import/chamada tardios). Cada notícia é normalizada para o
MESMO esquema da KB histórica (`date`, `ticker`, `headline`) para poder ser comparada por
similaridade com os precedentes (ver `investigator/historical_kb/`).

APIs gratuitas (ver docs/design/free_apis.md): Finnhub `/company-news` (60 req/min)
e feeds RSS públicos.
A chave do Finnhub vive só no `.env` (`FINNHUB_API_KEY`).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from investigator import config


@dataclass
class NewsItem:
    """Notícia normalizada (mesmo esquema da KB: data ISO, ticker, título).

    `summary` (opcional): o resumo curto que o Finnhub devolve — não é mostrado ao
    utilizador, mas enriquece o EMBEDDING na KB viva (uma frase de manchete sozinha é
    pouca informação semântica).

    `published_at` (opcional, 2026-07-29): instante EXATO da publicação (ISO 8601 UTC). O
    Finnhub devolve um epoch em segundos e o código truncava-o a `YYYY-MM-DD`, deitando fora
    a hora — sem ela é impossível medir quanto tempo passa entre a manchete sair e o alerta
    chegar ao telemóvel, que é precisamente a queixa "os alertas chegam tarde". `date`
    mantém-se intocado (alinhamento anti-lookahead, dedup e KB dependem dele)."""

    date: str  # 'YYYY-MM-DD'
    ticker: str
    headline: str
    url: str = ""
    source: str = ""
    summary: str = ""
    published_at: str = ""  # ISO 8601 UTC, ex.: "2026-07-29T13:41:02Z"


# ── Parsing (puro, testável) ───────────────────────────────────────────────────
def parse_finnhub_news(payload: list[dict], ticker: str) -> list[NewsItem]:
    """Converte a resposta JSON do Finnhub `/company-news` numa lista de `NewsItem`.

    Campos usados: `datetime` (epoch em segundos, UTC), `headline`, `url`, `source`,
    `summary`. Entradas sem data ou sem título são ignoradas.
    """
    items: list[NewsItem] = []
    for art in payload:
        ts = art.get("datetime")
        headline = (art.get("headline") or "").strip()
        if not ts or not headline:
            continue
        moment = datetime.fromtimestamp(int(ts), tz=UTC)
        items.append(
            NewsItem(
                date=moment.strftime("%Y-%m-%d"),
                ticker=ticker.upper(),
                headline=headline,
                url=str(art.get("url", "")),
                source=str(art.get("source", "finnhub")),
                summary=str(art.get("summary", "") or "").strip(),
                published_at=moment.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
        )
    return items


def _rss_date_to_iso(pub_date: str) -> str:
    """Converte uma data RSS (RFC 822, ex.: 'Wed, 02 Oct 2002 13:00:00 GMT') para 'YYYY-MM-DD'."""
    pub_date = (pub_date or "").strip()
    if not pub_date:
        return ""
    try:
        return parsedate_to_datetime(pub_date).strftime("%Y-%m-%d")
    except (TypeError, ValueError):
        return ""


def _rss_date_to_stamp(pub_date: str) -> str:
    """Instante exato da publicação RSS em ISO 8601 UTC ("" quando ilegível ou ausente).

    Par de `_rss_date_to_iso`, que só guarda o dia. Feeds sem fuso horário são tratados como
    UTC — aproximação assumida e documentada, preferível a deitar a hora fora."""
    pub_date = (pub_date or "").strip()
    if not pub_date:
        return ""
    try:
        moment = parsedate_to_datetime(pub_date)
    except (TypeError, ValueError):
        return ""
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_rss(xml_text: str | bytes, ticker: str = "") -> list[NewsItem]:
    """Extrai itens de um feed RSS 2.0 (`<item>`: `title`, `pubDate`, `link`).

    Parsing com a biblioteca padrão (sem dependências novas). Itens sem título são ignorados.
    Aceita `bytes` (o corpo cru da resposta): feeds reais abrem com uma declaração de
    codificação `<?xml ... encoding="UTF-8"?>`, que o ElementTree rejeita se lhe passarem
    uma `str` mas aceita a partir de `bytes`.
    """
    import xml.etree.ElementTree as ET

    root = ET.fromstring(xml_text)
    items: list[NewsItem] = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        if not title:
            continue
        items.append(
            NewsItem(
                date=_rss_date_to_iso(item.findtext("pubDate") or ""),
                ticker=ticker.upper(),
                headline=title,
                url=(item.findtext("link") or "").strip(),
                source="rss",
                published_at=_rss_date_to_stamp(item.findtext("pubDate") or ""),
            )
        )
    return items


# ── HTTP (invólucros finos, tardios) ───────────────────────────────────────────
def fetch_finnhub_company_news(
    ticker: str, start: str, end: str, api_key: str | None = None, timeout: int = 10
) -> list[NewsItem]:
    """Notícias de uma empresa no Finnhub entre `start` e `end` (datas 'YYYY-MM-DD')."""
    import requests

    api_key = api_key or config.FINNHUB_API_KEY
    if not api_key:
        raise RuntimeError("FINNHUB_API_KEY não configurada (ver .env).")
    resp = requests.get(
        "https://finnhub.io/api/v1/company-news",
        params={"symbol": ticker, "from": start, "to": end, "token": api_key},
        timeout=timeout,
    )
    resp.raise_for_status()
    return parse_finnhub_news(resp.json(), ticker)


# ── Segunda e terceira fontes ─────────────────────────────────────────────────
#
# ⚠️ Existem por MEDIÇÃO, e a medição está em `docs/evaluation/evaluation_news_sources.md`.
# Sobre a watchlist inteira e três dias, contando só as manchetes que sobrevivem ao filtro de
# relevância que já está em produção:
#
#   | fonte         | relevantes | precisão | frescura (mediana) | cobertura | exclusivas |
#   |---------------|-----------:|---------:|-------------------:|----------:|-----------:|
#   | Finnhub       |        432 |      35% |             15,8 h |     12/12 |        401 |
#   | Alpha Vantage |        141 |      24% |          **9,3 h** |     12/12 |        119 |
#   | Polygon       |        429 |      27% |             52,6 h |      8/12 |    **418** |
#
# Três fontes gratuitas com três forças diferentes, e é isso que justifica somá-las em vez de
# escolher a melhor: o Finnhub etiqueta melhor, a Alpha Vantage é a **mais fresca** (que é o que
# ataca a queixa "os alertas chegam tarde"), e o Polygon traz mais manchetes que mais nenhuma
# traz — mas com 52,6 h de mediana, ou seja, serve para **encher a base de casos** e não para
# alertar. Juntas dão 970 manchetes relevantes distintas contra as 432 do Finnhub sozinho: mais
# **125%**.
#
# Rejeitadas, e fica escrito porquê: o **Tiingo** devolve HTTP 403 no endpoint de notícias (exige
# plano pago) e o **GNews** não é por empresa — é pesquisa por palavras, e usá-lo obrigaria a
# inferir a empresa a partir do texto, acrescentando um erro que estas três não têm.


def parse_alphavantage_news(payload: dict, ticker: str) -> list[NewsItem]:
    """Converte a resposta do Alpha Vantage `NEWS_SENTIMENT` em `NewsItem`.

    O carimbo vem como `20260815T203300`, sem separadores — daí a conversão à mão.
    """
    items: list[NewsItem] = []
    for art in (payload or {}).get("feed", []) or []:
        titulo = (art.get("title") or "").strip()
        q = str(art.get("time_published") or "")
        if not titulo or len(q) != 15:
            continue
        items.append(
            NewsItem(
                date=f"{q[:4]}-{q[4:6]}-{q[6:8]}",
                ticker=ticker.upper(),
                headline=titulo,
                url=str(art.get("url", "")),
                source=str(art.get("source", "alphavantage")),
                summary=str(art.get("summary", "") or "").strip(),
                published_at=f"{q[:4]}-{q[4:6]}-{q[6:8]}T{q[9:11]}:{q[11:13]}:00Z",
            )
        )
    return items


def parse_polygon_news(payload: dict, ticker: str) -> list[NewsItem]:
    """Converte a resposta do Polygon `/v2/reference/news` em `NewsItem`."""
    items: list[NewsItem] = []
    for art in (payload or {}).get("results", []) or []:
        titulo = (art.get("title") or "").strip()
        quando = str(art.get("published_utc") or "")
        if not titulo or len(quando) < 10:
            continue
        items.append(
            NewsItem(
                date=quando[:10],
                ticker=ticker.upper(),
                headline=titulo,
                url=str(art.get("article_url", "")),
                source=str((art.get("publisher") or {}).get("name", "polygon")),
                summary=str(art.get("description", "") or "").strip(),
                published_at=quando.replace("+00:00", "Z"),
            )
        )
    return items


def fetch_alphavantage_news(
    ticker: str, api_key: str | None = None, limit: int = 50, timeout: int = 15
) -> list[NewsItem]:
    """Notícias de uma empresa no Alpha Vantage. Levanta sem chave, como as outras."""
    import requests

    api_key = api_key or config.ALPHAVANTAGE_API_KEY
    if not api_key:
        raise RuntimeError("ALPHAVANTAGE_API_KEY não configurada (ver .env).")
    resp = requests.get(
        "https://www.alphavantage.co/query",
        params={"function": "NEWS_SENTIMENT", "tickers": ticker,
                "limit": limit, "apikey": api_key},
        timeout=timeout,
    )
    resp.raise_for_status()
    return parse_alphavantage_news(resp.json(), ticker)


def fetch_polygon_news(
    ticker: str, api_key: str | None = None, limit: int = 50, timeout: int = 15
) -> list[NewsItem]:
    """Notícias de uma empresa no Polygon."""
    import requests

    api_key = api_key or getattr(config, "POLYGON_API_KEY", "")
    if not api_key:
        raise RuntimeError("POLYGON_API_KEY não configurada (ver .env).")
    resp = requests.get(
        "https://api.polygon.io/v2/reference/news",
        params={"ticker": ticker, "limit": limit, "apiKey": api_key},
        timeout=timeout,
    )
    resp.raise_for_status()
    return parse_polygon_news(resp.json(), ticker)


def fetch_rss_feed(feed_url: str, ticker: str = "", timeout: int = 10) -> list[NewsItem]:
    """Descarrega e parseia um feed RSS público."""
    import requests

    resp = requests.get(feed_url, timeout=timeout)
    resp.raise_for_status()
    # `resp.content` (bytes), não `resp.text`: um feed conforme abre com uma declaração de
    # codificação, e ET.fromstring levanta ValueError se receber uma str que a contenha.
    return parse_rss(resp.content, ticker)


def fetch_finnhub_quote(ticker: str, api_key: str | None = None,
                        timeout: int = 10) -> tuple[float, float]:
    """Cotação em (quase) tempo real do Finnhub `/quote`: (preço atual, fecho anterior).

    É a fonte da deteção INTRADIÁRIA no modo --watch: cotações US em tempo real no free
    tier (60/min — 10 tickers/ciclo fica muito abaixo). Levanta em erro/sem chave — quem
    chama decide o fail-open.
    """
    import requests

    api_key = api_key or config.FINNHUB_API_KEY
    if not api_key:
        raise RuntimeError("FINNHUB_API_KEY não configurada (ver .env).")
    resp = requests.get(
        "https://finnhub.io/api/v1/quote",
        params={"symbol": ticker, "token": api_key},
        timeout=timeout,
    )
    resp.raise_for_status()
    d = resp.json()
    atual, fecho_anterior = float(d.get("c") or 0.0), float(d.get("pc") or 0.0)
    if atual <= 0 or fecho_anterior <= 0:
        raise RuntimeError(f"Cotação inválida para {ticker}: c={atual}, pc={fecho_anterior}")
    return atual, fecho_anterior
