"""Estado da sessão regular do mercado US (NYSE/NASDAQ) em tempo real, para a UI.

Puro e testável: recebe/assume um instante UTC e devolve se o mercado está ABERTO ou FECHADO
e quando muda a seguir. Usa `zoneinfo` (stdlib) para converter para hora de Nova Iorque, por
isso o horário de verão/inverno (DST) é tratado automaticamente — a sessão regular é sempre
09:30–16:00 ET, mude ou não o offset para UTC.

Nota honesta: trata fins de semana e horário; NÃO trata feriados da bolsa (aproximação
assinalada na UI). É um indicador de conveniência, distinto do guarda de alertas
`is_us_market_session` do runner (que usa uma janela larga de propósito).

Desenhado para estender a outras bolsas: `_STATUS` genérico + um mapa de (fuso, abertura,
fecho) por bolsa quando quisermos Xetra/Euronext/LSE.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

_UTC = ZoneInfo("UTC")


@dataclass(frozen=True)
class MarketStatus:
    """Estado de uma sessão: aberto?, etiqueta, detalhe humano e o próximo instante de mudança."""

    is_open: bool
    label: str          # "Open" | "Closed"
    detail: str         # ex.: "closes in 3h 12m" | "opens Mon 09:30 EDT"
    next_change_utc: datetime
    minutes_to_change: int


@dataclass(frozen=True)
class Exchange:
    """Uma bolsa: código, rótulo curto para a UI, fuso e horário da sessão regular."""

    code: str
    name: str
    tz: str
    open: time
    close: time


# US + principais bolsas europeias. Horário da sessão regular; feriados NÃO tratados
# (aproximação, assinalada na UI). A ordem é a que aparece na app; a 1.ª (US) é o mercado
# dos alertas — as europeias são informativas por agora.
EXCHANGES: list[Exchange] = [
    Exchange("US", "US (NYSE/Nasdaq)", "America/New_York", time(9, 30), time(16, 0)),
    Exchange("XETRA", "Xetra", "Europe/Berlin", time(9, 0), time(17, 30)),
    Exchange("EURONEXT", "Euronext", "Europe/Paris", time(9, 0), time(17, 30)),
    Exchange("LSE", "London", "Europe/London", time(8, 0), time(16, 30)),
]


def _humanize(minutes: int) -> str:
    """Minutos → "3h 12m" / "45m" / "2d 4h" (compacto, para o rótulo)."""
    if minutes < 60:
        return f"{minutes}m"
    if minutes < 60 * 24:
        h, m = divmod(minutes, 60)
        return f"{h}h {m}m" if m else f"{h}h"
    d, rem = divmod(minutes, 60 * 24)
    h = rem // 60
    return f"{d}d {h}h" if h else f"{d}d"


def _next_open(local_dt: datetime, open_t: time) -> datetime:
    """Próxima abertura num dia útil, na hora local dada: hoje se ainda antes da abertura,
    senão o próximo dia útil."""
    today_open = local_dt.replace(hour=open_t.hour, minute=open_t.minute, second=0, microsecond=0)
    if local_dt.weekday() < 5 and local_dt < today_open:
        return today_open
    day = local_dt + timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day.replace(hour=open_t.hour, minute=open_t.minute, second=0, microsecond=0)


def exchange_status(ex: Exchange, now_utc: datetime | None = None) -> MarketStatus:
    """Estado atual da sessão regular de `ex` (DST tratado via zoneinfo). `now_utc` p/ testes."""
    if now_utc is None:
        now_utc = datetime.now(tz=_UTC)
    elif now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=_UTC)
    loc = now_utc.astimezone(ZoneInfo(ex.tz))
    open_l = loc.replace(hour=ex.open.hour, minute=ex.open.minute, second=0, microsecond=0)
    close_l = loc.replace(hour=ex.close.hour, minute=ex.close.minute, second=0, microsecond=0)

    if loc.weekday() < 5 and open_l <= loc < close_l:
        mins = max(0, int((close_l - loc).total_seconds() // 60))
        return MarketStatus(True, "Open", f"closes in {_humanize(mins)}",
                            close_l.astimezone(_UTC), mins)

    nxt = _next_open(loc, ex.open)
    mins = max(0, int((nxt - loc).total_seconds() // 60))
    if nxt.date() == loc.date():
        detalhe = f"opens in {_humanize(mins)}"
    else:
        hhmm = f"{ex.open.hour:02d}:{ex.open.minute:02d}"
        detalhe = f"opens {nxt:%a} {hhmm} {nxt.tzname()} (in {_humanize(mins)})"
    return MarketStatus(False, "Closed", detalhe, nxt.astimezone(_UTC), mins)


def us_market_status(now_utc: datetime | None = None) -> MarketStatus:
    """Estado da sessão regular US (compat: a 1.ª bolsa de `EXCHANGES`)."""
    return exchange_status(EXCHANGES[0], now_utc)


def all_exchange_status(now_utc: datetime | None = None) -> list[tuple[Exchange, MarketStatus]]:
    """Estado de todas as bolsas suportadas, pela ordem de `EXCHANGES`."""
    return [(ex, exchange_status(ex, now_utc)) for ex in EXCHANGES]


# ── Fase do dia (para o "vibe" da app: mascote e saudação sincronizadas com a hora) ──────
@dataclass(frozen=True)
class DayPhase:
    phase: str        # "morning" | "afternoon" | "evening" | "night"
    is_night: bool    # escolhe a mascote (noite = crocodilo a dormitar + lua)
    emoji: str        # ☀️/🌅/🌆/🌙
    greeting: str     # saudação com personalidade do "investigador"


def day_phase(now_utc: datetime | None = None, tz: str = "Europe/Lisbon") -> DayPhase:
    """Fase do dia na hora LOCAL do aluno (default Lisboa). Puro; `now_utc` para testes."""
    if now_utc is None:
        now_utc = datetime.now(tz=_UTC)
    elif now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=_UTC)
    h = now_utc.astimezone(ZoneInfo(tz)).hour
    if 5 <= h < 12:
        return DayPhase("morning", False, "🌅",
                        "Good morning — the gator's eyeing the open.")
    if 12 <= h < 18:
        return DayPhase("afternoon", False, "☀️",
                        "Good afternoon — the gator's on watch.")
    if 18 <= h < 21:
        return DayPhase("evening", True, "🌆",
                        "Good evening — winding down the session.")
    return DayPhase("night", True, "🌙",
                    "Night watch — the gator never really sleeps.")
