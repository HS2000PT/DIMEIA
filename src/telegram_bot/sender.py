"""Envio de alertas via Telegram Bot API (gratuito). Segredos só do .env (src/config)."""

from __future__ import annotations

import requests

from src import config


def send_message(text: str, token: str | None = None, chat_id: str | None = None,
                 timeout: int = 10) -> dict:
    """Envia uma mensagem de texto via Telegram Bot API. Devolve a resposta JSON."""
    token = token or config.TELEGRAM_BOT_TOKEN
    chat_id = chat_id or config.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        raise RuntimeError(
            "Telegram não configurado: define TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env."
        )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    resp = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
