"""Testes do parser das métricas de pós-validação ao vivo (puro)."""

from __future__ import annotations

from investigator.evaluation.monitoring import parse_live_monitoring

_MD = """# live_monitoring.md — Pós-validação das decisões ao vivo

- **Decisões:** 76 registadas · 53 únicas · 33 maturadas.

| Métrica ao vivo | Valor |
|---|---|
| Precisão das decisões mantidas | 0.667 (12 mantidas) |
| Base rate (todas as decisões maturadas) | 0.455 (33) |
| Brier das probabilidades | 0.229 |
"""


def test_extrai_precisao_e_base_rate():
    h = parse_live_monitoring(_MD)
    assert h is not None
    assert abs(h.kept_precision - 0.667) < 1e-9
    assert abs(h.base_rate - 0.455) < 1e-9
    assert round(h.lift_points, 1) == 21.2  # a triagem bate a base rate ao vivo


def test_none_quando_vazio_ou_ilegivel():
    assert parse_live_monitoring(None) is None
    assert parse_live_monitoring("") is None
    assert parse_live_monitoring("# relatório sem a tabela de métricas") is None
