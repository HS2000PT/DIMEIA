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

# ── Webhook do Telegram ───────────────────────────────────────────────────────────────────
# O bot passou de long-polling a webhook para que a recolha de feedback não dependa de uma
# máquina ligada. ⚠️ O Telegram não permite os dois: com webhook registado, o `getUpdates`
# devolve 409. Por isso esta variável é o interruptor único — quando está a 1, o runner deixa
# de chamar `getUpdates` e o `api/main.py` abre a rota.
TELEGRAM_WEBHOOK_ENABLED: bool = os.environ.get("TELEGRAM_WEBHOOK_ENABLED") == "1"

# Segredo do cabeçalho `X-Telegram-Bot-Api-Secret-Token`. Sem ele a rota fica FECHADA, e não
# aberta: um webhook público sem verificação aceita votos de quem descobrir o endereço, e a
# amostra deixaria de significar o que a tese diz que significa.
TELEGRAM_WEBHOOK_SECRET: str | None = os.environ.get("TELEGRAM_WEBHOOK_SECRET")

# Sal do resumo criptográfico do votante. Recai no token do bot, que já é secreto e já existe,
# para que a funcionalidade não fique dependente de mais uma variável por configurar; definir
# um próprio é melhor, porque desliga a rotação do token da estabilidade dos resumos.
FEEDBACK_SALT: str = (os.environ.get("FEEDBACK_SALT")
                      or os.environ.get("TELEGRAM_BOT_TOKEN") or "")


def feedback_ready() -> bool:
    """Verdadeiro se o webhook pode receber e gravar votos com identidade estável."""
    return bool(TELEGRAM_WEBHOOK_ENABLED and TELEGRAM_WEBHOOK_SECRET and FEEDBACK_SALT)
