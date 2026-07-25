"""Testes do indicador de estado do mercado US (puro, com DST tratado via zoneinfo)."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from investigator.market_data.market_hours import us_market_status

_UTC = ZoneInfo("UTC")


def _utc(y, m, d, hh, mm=0):
    return datetime(y, m, d, hh, mm, tzinfo=_UTC)


def test_aberto_verao_edt():
    # 15 Jul 2026 (quarta), 14:00 UTC = 10:00 EDT → sessão aberta (09:30–16:00 ET).
    s = us_market_status(_utc(2026, 7, 15, 14, 0))
    assert s.is_open and s.label == "Open"
    assert "closes in" in s.detail


def test_fechado_antes_da_abertura_verao():
    # 15 Jul 2026, 13:00 UTC = 09:00 EDT → antes da abertura (09:30).
    s = us_market_status(_utc(2026, 7, 15, 13, 0))
    assert not s.is_open and s.label == "Closed"
    assert "opens in" in s.detail


def test_fechado_depois_do_fecho_verao():
    # 15 Jul 2026, 20:30 UTC = 16:30 EDT → depois do fecho (16:00).
    s = us_market_status(_utc(2026, 7, 15, 20, 30))
    assert not s.is_open
    assert s.next_change_utc > _utc(2026, 7, 15, 20, 30)  # abre no dia seguinte


def test_dst_inverno_est_offset_diferente():
    # 15 Jan 2026 (quinta), 14:00 UTC = 09:00 EST → ainda FECHADO (abre 14:30 UTC no inverno).
    assert not us_market_status(_utc(2026, 1, 15, 14, 0)).is_open
    # 15:00 UTC = 10:00 EST → ABERTO.
    assert us_market_status(_utc(2026, 1, 15, 15, 0)).is_open


def test_fim_de_semana_fechado_abre_segunda():
    # Sábado 18 Jul 2026, meio-dia UTC → fechado; próxima mudança é uma abertura de segunda.
    s = us_market_status(_utc(2026, 7, 18, 12, 0))
    assert not s.is_open
    nxt_et = s.next_change_utc.astimezone(ZoneInfo("America/New_York"))
    assert nxt_et.weekday() == 0 and nxt_et.hour == 9 and nxt_et.minute == 30


def test_naive_datetime_tratado_como_utc():
    s = us_market_status(datetime(2026, 7, 15, 14, 0))  # sem tzinfo
    assert s.is_open


def test_day_phase_manha_tarde_noite():
    from investigator.market_data.market_hours import day_phase

    # 09:00 Lisboa (verão = UTC+1) → 08:00 UTC = manhã, não noite.
    manha = day_phase(_utc(2026, 7, 15, 8, 0))
    assert manha.phase == "morning" and not manha.is_night
    # 15:00 Lisboa = 14:00 UTC → tarde.
    assert day_phase(_utc(2026, 7, 15, 14, 0)).phase == "afternoon"
    # 23:00 Lisboa = 22:00 UTC → noite (mascote noturna).
    noite = day_phase(_utc(2026, 7, 15, 22, 0))
    assert noite.phase == "night" and noite.is_night
    # 20:00 Lisboa = 19:00 UTC → fim de tarde, já conta como noite para a mascote.
    assert day_phase(_utc(2026, 7, 15, 19, 0)).is_night
