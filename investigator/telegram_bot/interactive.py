"""Fase B — poller do bot (long-polling do Telegram; sem servidor, sem webhook).

Porquê *polling* e não webhook: o webhook exige um host público sempre ligado (Fase B
"completa", ver going_live.md); o `getUpdates` com `timeout` longo funciona em qualquer
máquina atrás de NAT, de graça. O loop é o único sítio com rede; a interpretação dos
comandos é pura (`commands.py`) e o estado é SQLite (`store.py`).

Uso:  python scripts/run_bot.py   (Ctrl+C para parar)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from investigator import config
from investigator.telegram_bot import store
from investigator.telegram_bot.commands import handle_command
from investigator.telegram_bot.sender import send_message

_API = "https://api.telegram.org/bot{token}/{method}"


def extract_command(update: dict[str, Any]) -> tuple[str, str] | None:
    """(chat_id, texto) de um update do Telegram, ou None se não for mensagem de texto.

    Puro e testável: aceita o JSON de `getUpdates` tal como a API o devolve.
    """
    msg = update.get("message") or update.get("edited_message")
    if not isinstance(msg, dict):
        return None
    chat = msg.get("chat") or {}
    text = msg.get("text")
    if not text or "id" not in chat:
        return None
    return str(chat["id"]), str(text)


def poll_updates(token: str, offset: int | None, timeout_s: int = 50) -> list[dict[str, Any]]:
    """Uma chamada `getUpdates` (long-poll). HTTP tardio, como no news_fetcher."""
    import requests

    resp = requests.get(
        _API.format(token=token, method="getUpdates"),
        params={"timeout": timeout_s, **({"offset": offset} if offset is not None else {})},
        timeout=timeout_s + 10,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram getUpdates falhou: {data}")
    return list(data.get("result", []))


def run_polling(db_path: str | Path = store.DEFAULT_DB, token: str | None = None) -> None:
    """Loop principal: recebe comandos, responde, persiste subscrições. Ctrl+C para sair."""
    token = token or config.TELEGRAM_BOT_TOKEN
    if not token:
        raise RuntimeError("Telegram não configurado: define TELEGRAM_BOT_TOKEN no .env.")
    conn = store.connect(db_path)
    offset: int | None = None
    print(f"[bot] a ouvir (long-polling); base: {db_path}. Ctrl+C para parar.")
    while True:
        try:
            updates = poll_updates(token, offset)
        except KeyboardInterrupt:
            raise
        except Exception as exc:  # rede/API: regista e continua (nunca morre por 1 falha)
            print(f"[bot] getUpdates falhou (continuo): {exc}")
            continue
        for upd in updates:
            offset = int(upd.get("update_id", 0)) + 1
            par = extract_command(upd)
            if par is None:
                continue
            chat_id, text = par
            reply = handle_command(text, chat_id, conn)
            try:
                send_message(reply, chat_id=chat_id)
                print(f"[bot] {chat_id}: {text!r} -> ok")
            except Exception as exc:
                print(f"[bot] resposta a {chat_id} falhou (continuo): {exc}")
