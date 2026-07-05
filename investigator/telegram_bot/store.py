"""Fase B — armazenamento de subscritores do bot (SQLite, stdlib, zero dependências novas).

Cada utilizador (chat privado com o bot) tem uma watchlist própria de tickers. O runner
usa `subscribers_of(ticker)` para distribuir alertas por quem vigia esse ticker.

Desenho honesto (ver docs/design/going_live.md, Fase B): sem servidor não há webhook — o
bot corre em *long-polling* na máquina do aluno (`scripts/run_bot.py`); a base fica em
`data/bot_users.db` (gitignored). Fail-open em todo o lado: sem base, o runner comporta-se
como sempre (só canal).
"""

from __future__ import annotations

import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "bot_users.db"

# Ticker US plausível: 1–6 maiúsculas, ponto opcional (ex.: BRK.B). Valida INPUT do utilizador.
_TICKER_RE = re.compile(r"^[A-Z]{1,6}(\.[A-Z]{1,2})?$")


def valid_ticker(text: str) -> bool:
    """True se o texto tem forma de ticker US (não confirma que existe na bolsa)."""
    return bool(_TICKER_RE.match(text.strip().upper()))


def connect(path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    """Abre (e cria se preciso) a base de subscritores; devolve a ligação."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS chats ("
        " chat_id TEXT PRIMARY KEY, active INTEGER NOT NULL DEFAULT 1,"
        " started_at TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS watches ("
        " chat_id TEXT NOT NULL, ticker TEXT NOT NULL,"
        " added_at TEXT NOT NULL, PRIMARY KEY (chat_id, ticker))"
    )
    conn.commit()
    return conn


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def ensure_chat(conn: sqlite3.Connection, chat_id: str) -> None:
    """Regista o chat (idempotente) e marca-o ativo."""
    conn.execute(
        "INSERT INTO chats (chat_id, active, started_at) VALUES (?, 1, ?)"
        " ON CONFLICT(chat_id) DO UPDATE SET active = 1",
        (str(chat_id), _now()),
    )
    conn.commit()


def deactivate_chat(conn: sqlite3.Connection, chat_id: str) -> None:
    """/stop — o chat deixa de receber alertas (a watchlist fica guardada)."""
    conn.execute("UPDATE chats SET active = 0 WHERE chat_id = ?", (str(chat_id),))
    conn.commit()


def subscribe(conn: sqlite3.Connection, chat_id: str, ticker: str) -> bool:
    """Adiciona o ticker à watchlist do chat. Devolve True se era novo."""
    ticker = ticker.strip().upper()
    if not valid_ticker(ticker):
        raise ValueError(f"Ticker inválido: {ticker!r}")
    ensure_chat(conn, chat_id)
    cur = conn.execute(
        "INSERT OR IGNORE INTO watches (chat_id, ticker, added_at) VALUES (?, ?, ?)",
        (str(chat_id), ticker, _now()),
    )
    conn.commit()
    return cur.rowcount > 0


def unsubscribe(conn: sqlite3.Connection, chat_id: str, ticker: str) -> bool:
    """Remove o ticker da watchlist. Devolve True se existia."""
    cur = conn.execute(
        "DELETE FROM watches WHERE chat_id = ? AND ticker = ?",
        (str(chat_id), ticker.strip().upper()),
    )
    conn.commit()
    return cur.rowcount > 0


def watchlist(conn: sqlite3.Connection, chat_id: str) -> list[str]:
    """Tickers vigiados por este chat, ordenados."""
    rows = conn.execute(
        "SELECT ticker FROM watches WHERE chat_id = ? ORDER BY ticker", (str(chat_id),)
    ).fetchall()
    return [r[0] for r in rows]


def subscribers_of(conn: sqlite3.Connection, ticker: str) -> list[str]:
    """Chats ATIVOS que vigiam este ticker (para o runner distribuir alertas)."""
    rows = conn.execute(
        "SELECT w.chat_id FROM watches w JOIN chats c ON c.chat_id = w.chat_id"
        " WHERE w.ticker = ? AND c.active = 1 ORDER BY w.chat_id",
        (ticker.strip().upper(),),
    ).fetchall()
    return [r[0] for r in rows]
