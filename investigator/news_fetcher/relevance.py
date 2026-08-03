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

# Nome de exibição por ticker — usado nos alertas e na app ("Apple (AAPL)"): um leigo não
# devia precisar de saber símbolos de bolsa para ler um alerta.
COMPANY_DISPLAY: dict[str, str] = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA", "TSLA": "Tesla",
    "AMZN": "Amazon", "GOOGL": "Alphabet", "META": "Meta", "JPM": "JPMorgan",
    "AMD": "AMD", "NFLX": "Netflix", "XOM": "Exxon Mobil", "JNJ": "Johnson & Johnson",
}


def display_name(ticker: str) -> str:
    """Nome amigável ('Apple'); o próprio símbolo quando não há mapeamento."""
    return COMPANY_DISPLAY.get(ticker.upper(), ticker.upper())


# Setor por ticker — a MESMA taxonomia de 5 setores usada na tese (avaliação de retrieval e
# dataset da triagem, investigator/triage/dataset.py::SECTORS), estendida aos tickers da
# watchlist do produto que não estão nesse mapa (AMD, NFLX). Serve a linha "Sector check"
# dos alertas de mercado: empresas do mesmo setor movem-se juntas — ver docs §sector.
SECTOR_OF: dict[str, str] = {
    "AAPL": "tech", "MSFT": "tech", "AMZN": "tech", "GOOGL": "tech", "NVDA": "tech",
    "TSLA": "tech", "META": "tech", "AMD": "tech", "NFLX": "tech",
    "JPM": "banking", "BAC": "banking",
    "XOM": "energy", "CVX": "energy",
    "JNJ": "health", "PFE": "health",
    "WMT": "consumer", "KO": "consumer",
}

# Rótulo legível do setor (para o texto do alerta).
SECTOR_LABEL: dict[str, str] = {
    "tech": "technology", "banking": "banking", "energy": "energy",
    "health": "healthcare", "consumer": "consumer",
}

# ETF representativo de cada setor — o "fator de setor" da decomposição
# (`correlation_engine/decomposition.py`). São os SPDR Select Sector, os mais líquidos e com
# histórico longo, disponíveis em qualquer fonte de preços gratuita.
# O índice de mercado é o SPY. Um ticker sem setor mapeado decompõe-se só contra o mercado.
MARKET_INDEX = "SPY"
SECTOR_ETF: dict[str, str] = {
    "tech": "XLK", "banking": "XLF", "energy": "XLE",
    "health": "XLV", "consumer": "XLP",
}


def sector_etf(ticker: str) -> str:
    """ETF do setor deste ticker ("" quando o setor não está mapeado)."""
    return SECTOR_ETF.get(SECTOR_OF.get(ticker.upper(), ""), "")


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
    # Os dois nomes não-tecnológicos (2026-08-03). Sem aliases, o filtro de relevância cai
    # no fallback honesto — só o símbolo conta como menção — e uma manchete que diz
    # "Exxon" mas não "XOM" seria descartada. Praticamente nenhuma manchete escreve o
    # símbolo, portanto o cartão viria vazio sem que nada avisasse porquê.
    "XOM": ["exxon", "exxonmobil", "exxon mobil"],
    "JNJ": ["johnson & johnson", "johnson and johnson", "j&j", "janssen"],
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
