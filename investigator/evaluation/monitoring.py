"""Leitura das métricas de topo do relatório de pós-validação (`live_monitoring.md`).

Puro e testável: extrai a precisão das decisões mantidas e a base rate do markdown gerado
por `post_validate.py`, para a app mostrar a "prova de vida" (o mecanismo a bater a base rate
ao vivo, fora da amostra) num relance, sem depender do formato exato de toda a prosa.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_KEPT = re.compile(r"decis[õo]es mantidas\s*\|\s*([0-9]*\.?[0-9]+)", re.IGNORECASE)
_BASE = re.compile(r"Base rate[^|]*\|\s*([0-9]*\.?[0-9]+)", re.IGNORECASE)


@dataclass(frozen=True)
class LiveHealth:
    kept_precision: float   # precisão das decisões que a triagem MANTEVE
    base_rate: float        # taxa-base de todas as decisões maturadas

    @property
    def lift_points(self) -> float:
        """Diferença em pontos percentuais (kept − base). Positivo = a triagem ajuda."""
        return (self.kept_precision - self.base_rate) * 100.0


def parse_live_monitoring(md: str | None) -> LiveHealth | None:
    """Extrai (kept_precision, base_rate) do markdown. None se ausente/ilegível (fail-open)."""
    if not md:
        return None
    k, b = _KEPT.search(md), _BASE.search(md)
    if not (k and b):
        return None
    try:
        return LiveHealth(float(k.group(1)), float(b.group(1)))
    except ValueError:
        return None
