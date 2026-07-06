"""Envio de alertas via Telegram Bot API (gratuito). Segredos só do .env (investigator/config)."""

from __future__ import annotations

import requests

from investigator import config


def send_message(text: str, token: str | None = None, chat_id: str | None = None,
                 timeout: int = 10, parse_mode: str | None = "HTML") -> dict:
    """Envia uma mensagem via Telegram Bot API. Devolve a resposta JSON.

    `parse_mode="HTML"` por defeito (revisão UX): os alertas usam <b>/<i> para hierarquia
    visual; todo o conteúdo dinâmico é escapado nos construtores (explainer/commands).
    Se o Telegram rejeitar o HTML (400), reenvia UMA vez em texto puro — entregar vale mais
    do que formatar.
    """
    token = token or config.TELEGRAM_BOT_TOKEN
    chat_id = chat_id or config.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        raise RuntimeError(
            "Telegram não configurado: define TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env."
        )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    resp = requests.post(url, data=payload, timeout=timeout)
    if resp.status_code == 400 and parse_mode:
        resp = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
