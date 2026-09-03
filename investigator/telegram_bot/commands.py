"""Fase B — interpretação PURA dos comandos do bot (testável sem rede).

`handle_command(texto, chat_id, conn)` devolve a resposta a enviar. Toda a lógica de
estado vive em `store.py`; aqui só se interpreta texto e se compõem respostas (EN,
coerente com a língua dos alertas). O envio (I/O) fica no poller (`interactive.py`).
"""

from __future__ import annotations

import sqlite3

from investigator.telegram_bot import store

HELP = (
    "🐊 <b>InvestiGator</b> — market alerts that explain themselves.\n\n"
    "<b>Your watchlist</b>\n"
    "/watch TSLA — add a ticker\n"
    "/unwatch TSLA — remove it\n"
    "/list — see your list\n\n"
    "<b>Alerts</b>\n"
    "/stop — pause (your list is kept)\n"
    "/start — resume\n\n"
    "<b>Feedback privacy</b>\n"
    "/deletefeedback — withdraw your previous feedback from the analysis\n\n"
    "<i>Every alert shows its evidence (unusual move or similar past news). "
    "Never a forecast, never advice.</i>"
)

MAX_WATCH = 20  # produto responsável: limita a fadiga de alertas (e abusos)


def handle_command(text: str, chat_id: str, conn: sqlite3.Connection) -> str:
    """Interpreta um comando e devolve a resposta (string pronta a enviar)."""
    parts = (text or "").strip().split()
    if not parts or not parts[0].startswith("/"):
        return "I only understand commands - try /help."
    cmd = parts[0].split("@")[0].lower()  # aceita /watch@NomeDoBot em grupos
    arg = parts[1].strip().upper() if len(parts) > 1 else ""

    if cmd == "/start":
        store.ensure_chat(conn, chat_id)
        return "Welcome! Your alerts are active.\n\n" + HELP
    if cmd == "/help":
        return HELP
    if cmd == "/stop":
        store.deactivate_chat(conn, chat_id)
        return "Alerts paused. Your watchlist was kept - send /start to resume."
    if cmd == "/list":
        tickers = store.watchlist(conn, chat_id)
        if not tickers:
            return "Your watchlist is empty - add one with /watch TSLA."
        return "Your watchlist: " + ", ".join(tickers)
    if cmd == "/watch":
        if not arg:
            return "Usage: /watch TSLA"
        if not store.valid_ticker(arg):
            import html

            return f"'{html.escape(arg)}' does not look like a US ticker (e.g. TSLA, BRK.B)."
        if len(store.watchlist(conn, chat_id)) >= MAX_WATCH:
            return f"Limit of {MAX_WATCH} tickers reached - /unwatch one first."
        novo = store.subscribe(conn, chat_id, arg)
        return (f"{arg} added. You will get its alerts after each scheduled scan."
                if novo else f"{arg} was already on your watchlist.")
    if cmd == "/unwatch":
        if not arg:
            return "Usage: /unwatch TSLA"
        return (f"{arg} removed." if store.unsubscribe(conn, chat_id, arg)
                else f"{arg} was not on your watchlist.")
    return "Unknown command - try /help."
