"""Filtro de relevância de manchetes — a correção do maior problema real do produto.

Diagnóstico (2026-07-11, sobre 27 alertas reais do canal): o endpoint company-news do
Finnhub devolve manchetes mal etiquetadas — uma notícia sobre um escritório de advogados
marcada como "AMD"; resumos genéricos de mercado ("Top S&P500 movers", "Stay informed about
the most active stocks…") etiquetados para vários tickers ao mesmo tempo. Sem filtro, o
alerta parecia aleatório e os precedentes semânticos pareciam errados (lixo à entrada).

Regra simples e explicável (coerente com a postura XAI do sistema):
1. a manchete tem de MENCIONAR a empresa (nome/alias ou o próprio ticker), e
2. não pode ser "boilerplate" de mercado (padrões de resumo genérico).

Puro, sem dependências — testado em tests/test_relevance.py.
"""

from __future__ import annotations

import re

# Aliases por ticker (minúsculas; comparação é case-insensitive). Cobre a watchlist do
# produto (config/alerts.yaml) + SPY. Um ticker fora do mapa cai no fallback honesto:
# só o próprio símbolo conta como menção.
COMPANY_NAMES: dict[str, list[str]] = {
    "AAPL": ["apple", "iphone", "tim cook"],
    "MSFT": ["microsoft", "azure", "satya nadella"],
    "NVDA": ["nvidia", "jensen huang", "geforce"],
    "TSLA": ["tesla", "elon musk", "cybertruck"],
    "AMZN": ["amazon", "aws", "bezos"],
    "GOOGL": ["google", "alphabet", "gemini", "android"],
    "META": ["meta", "facebook", "instagram", "whatsapp", "zuckerberg"],
    "JPM": ["jpmorgan", "jp morgan", "jamie dimon", "chase"],
    "AMD": ["amd", "advanced micro devices", "ryzen", "radeon", "lisa su"],
    "NFLX": ["netflix"],
}

# Resumos genéricos de mercado que o Finnhub etiqueta para QUALQUER ticker — nunca são
# notícia DA empresa, mesmo que mencionem o nome de passagem numa lista.
_BOILERPLATE = [
    r"s&p\s*500 movers",
    r"most active stocks",
    r"biggest movers",
    r"sector update",
    r"stocks to (buy|watch|invest)",
    r"top analyst calls",
    r"stay informed about",
    r"mid-day market update",
    r"market update:",
    r"stock market today",
    r"what's going on in today's session",
]
_BOILERPLATE_RE = re.compile("|".join(_BOILERPLATE), re.IGNORECASE)


def _mentions(headline_lower: str, term: str) -> bool:
    """Menção por palavra inteira (evita 'meta' dentro de 'metal', 'AMD' dentro de 'Amsterdam')."""
    return re.search(rf"\b{re.escape(term)}\b", headline_lower) is not None


def is_relevant(headline: str, ticker: str) -> bool:
    """True se a manchete é plausivelmente SOBRE esta empresa (e não boilerplate de mercado)."""
    if not headline or not headline.strip():
        return False
    low = headline.lower()
    if _BOILERPLATE_RE.search(low):
        return False
    terms = [ticker.lower()] + COMPANY_NAMES.get(ticker.upper(), [])
    return any(_mentions(low, t) for t in terms)
