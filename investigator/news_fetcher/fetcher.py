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
    pouca informação semântica)."""

    date: str  # 'YYYY-MM-DD'
    ticker: str
    headline: str
    url: str = ""
    source: str = ""
    summary: str = ""


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
        date = datetime.fromtimestamp(int(ts), tz=UTC).strftime("%Y-%m-%d")
        items.append(
            NewsItem(
                date=date,
                ticker=ticker.upper(),
                headline=headline,
                url=str(art.get("url", "")),
                source=str(art.get("source", "finnhub")),
                summary=str(art.get("summary", "") or "").strip(),
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
