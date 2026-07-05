"""Testes do bot interativo (Fase B): store SQLite + comandos puros + parsing de updates.

Tudo offline (SQLite em tmp_path; zero rede). O poller em si é I/O fino e fica de fora,
como o HTTP do news_fetcher.
"""

from __future__ import annotations

import pytest

from investigator.telegram_bot import store
from investigator.telegram_bot.commands import HELP, MAX_WATCH, handle_command
from investigator.telegram_bot.interactive import extract_command


@pytest.fixture()
def conn(tmp_path):
    return store.connect(tmp_path / "bot_users.db")


# ── store ─────────────────────────────────────────────────────────────────────
def test_subscribe_e_watchlist(conn):
    assert store.subscribe(conn, "1", "tsla") is True  # normaliza para maiúsculas
    assert store.subscribe(conn, "1", "TSLA") is False  # duplicado
    assert store.subscribe(conn, "1", "AAPL") is True
    assert store.watchlist(conn, "1") == ["AAPL", "TSLA"]


def test_unsubscribe(conn):
    store.subscribe(conn, "1", "TSLA")
    assert store.unsubscribe(conn, "1", "TSLA") is True
    assert store.unsubscribe(conn, "1", "TSLA") is False
    assert store.watchlist(conn, "1") == []


def test_subscribers_of_so_ativos(conn):
    store.subscribe(conn, "1", "TSLA")
    store.subscribe(conn, "2", "TSLA")
    store.subscribe(conn, "3", "AAPL")
    assert store.subscribers_of(conn, "TSLA") == ["1", "2"]
    store.deactivate_chat(conn, "2")  # /stop tira dos envios mas guarda a watchlist
    assert store.subscribers_of(conn, "TSLA") == ["1"]
    store.ensure_chat(conn, "2")  # /start reativa
    assert store.subscribers_of(conn, "TSLA") == ["1", "2"]


def test_ticker_invalido_rejeitado(conn):
    with pytest.raises(ValueError):
        store.subscribe(conn, "1", "not a ticker")
    assert store.valid_ticker("BRK.B") is True
    assert store.valid_ticker("TSLA") is True
    assert store.valid_ticker("toolong7") is False
    assert store.valid_ticker("") is False


# ── comandos ──────────────────────────────────────────────────────────────────
def test_start_help_e_desconhecido(conn):
    assert HELP in handle_command("/start", "9", conn)
    assert handle_command("/help", "9", conn) == HELP
    assert "help" in handle_command("/xyz", "9", conn)
    assert "commands" in handle_command("olá bot", "9", conn)


def test_watch_unwatch_list_fluxo(conn):
    assert "empty" in handle_command("/list", "9", conn)
    assert "TSLA added" in handle_command("/watch tsla", "9", conn)
    assert "already" in handle_command("/watch TSLA", "9", conn)
    assert "TSLA" in handle_command("/list", "9", conn)
    assert "TSLA removed" in handle_command("/unwatch TSLA", "9", conn)
    assert "not on" in handle_command("/unwatch TSLA", "9", conn)


def test_watch_valida_e_limita(conn):
    assert "does not look like" in handle_command("/watch 123!", "9", conn)
    assert "Usage" in handle_command("/watch", "9", conn)
    for i in range(MAX_WATCH):
        # tickers sintáticos válidos (A, B, …); chega para exercer o limite
        handle_command(f"/watch {chr(65 + i % 26)}{chr(65 + i // 26)}", "9", conn)
    assert "Limit" in handle_command("/watch ZZZZ", "9", conn)


def test_stop_pausa_e_guarda(conn):
    handle_command("/watch TSLA", "9", conn)
    assert "paused" in handle_command("/stop", "9", conn)
    assert store.subscribers_of(conn, "TSLA") == []  # não recebe
    assert store.watchlist(conn, "9") == ["TSLA"]  # mas a lista fica
    handle_command("/start", "9", conn)
    assert store.subscribers_of(conn, "TSLA") == ["9"]


def test_comando_com_sufixo_de_grupo(conn):
    assert "TSLA added" in handle_command("/watch@InvestiGatorBot TSLA", "9", conn)


# ── parsing de updates ────────────────────────────────────────────────────────
def test_extract_command():
    upd = {"update_id": 7, "message": {"chat": {"id": 42}, "text": "/watch TSLA"}}
    assert extract_command(upd) == ("42", "/watch TSLA")
    assert extract_command({"update_id": 8}) is None  # sem mensagem
    assert extract_command({"message": {"chat": {"id": 1}, "photo": []}}) is None  # sem texto
