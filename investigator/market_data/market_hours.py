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
_ET = ZoneInfo("America/New_York")
_OPEN = time(9, 30)
_CLOSE = time(16, 0)


@dataclass(frozen=True)
class MarketStatus:
    """Estado de uma sessão: aberto?, etiqueta, detalhe humano e o próximo instante de mudança."""

    is_open: bool
    label: str          # "Open" | "Closed"
    detail: str         # ex.: "closes in 3h 12m" | "opens Mon 09:30 ET"
    next_change_utc: datetime
    minutes_to_change: int


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


def _next_open_et(et: datetime) -> datetime:
    """Próxima abertura (09:30 ET) num dia útil: hoje se ainda antes da abertura, senão o
    próximo dia útil."""
    today_open = et.replace(hour=9, minute=30, second=0, microsecond=0)
    if et.weekday() < 5 and et < today_open:
        return today_open
    day = et + timedelta(days=1)
    while day.weekday() >= 5:
        day += timedelta(days=1)
    return day.replace(hour=9, minute=30, second=0, microsecond=0)


def us_market_status(now_utc: datetime | None = None) -> MarketStatus:
    """Estado atual da sessão regular US. `now_utc` para testes (default: agora)."""
    if now_utc is None:
        now_utc = datetime.now(tz=_UTC)
    elif now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=_UTC)
    et = now_utc.astimezone(_ET)

    open_et = et.replace(hour=_OPEN.hour, minute=_OPEN.minute, second=0, microsecond=0)
    close_et = et.replace(hour=_CLOSE.hour, minute=_CLOSE.minute, second=0, microsecond=0)
    is_weekday = et.weekday() < 5

    if is_weekday and open_et <= et < close_et:
        change = close_et
        mins = max(0, int((change - et).total_seconds() // 60))
        return MarketStatus(True, "Open", f"closes in {_humanize(mins)}",
                            change.astimezone(_UTC), mins)

    nxt = _next_open_et(et)
    mins = max(0, int((nxt - et).total_seconds() // 60))
    # Detalhe: "opens in 2h" no mesmo dia; senão "opens Mon 09:30 ET".
    if nxt.date() == et.date():
        detalhe = f"opens in {_humanize(mins)}"
    else:
        detalhe = f"opens {nxt:%a} 09:30 ET (in {_humanize(mins)})"
    return MarketStatus(False, "Closed", detalhe, nxt.astimezone(_UTC), mins)
