"""Configuração: carrega variáveis de ambiente do .env (segredos vivem APENAS no .env).

Nunca versionar valores. O .env está no .gitignore; os NOMES estão no .env.example.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()  # carrega o .env local, se existir (não falha se não existir)

TELEGRAM_BOT_TOKEN: str | None = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID: str | None = os.environ.get("TELEGRAM_CHAT_ID")
FINNHUB_API_KEY: str | None = os.environ.get("FINNHUB_API_KEY")

# Cadeia de fallback de preços diários (yfinance → Stooq → Tiingo → Polygon → Alpha Vantage).
# Todas opcionais: fontes sem chave são saltadas (o Stooq nem precisa de chave).
TIINGO_API_KEY: str | None = os.environ.get("TIINGO_API_KEY")
POLYGON_API_KEY: str | None = os.environ.get("POLYGON_API_KEY")
ALPHAVANTAGE_API_KEY: str | None = os.environ.get("ALPHAVANTAGE_API_KEY")

# Narrador (opcional). Duas por desenho: uma defesa ao vivo não pode morrer num rate limit,
# por isso há sempre um segundo fornecedor e, por baixo dos dois, o texto por template.
GEMINI_API_KEY: str | None = os.environ.get("GEMINI_API_KEY")
GROQ_API_KEY: str | None = os.environ.get("GROQ_API_KEY")


def narrator_providers() -> list[str]:
    """Fornecedores de LLM configurados, por ordem de preferência (vazio = só template)."""
    return [n for n, k in (("gemini", GEMINI_API_KEY), ("groq", GROQ_API_KEY)) if k]


def telegram_ready() -> bool:
    """Verdadeiro se o token e o chat id do Telegram estão configurados."""
    return bool(TELEGRAM_BOT_TOKEN) and bool(TELEGRAM_CHAT_ID)
