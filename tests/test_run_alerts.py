"""Testes do runner de alertas — a parte pura (sem rede)."""

from __future__ import annotations

from scripts.run_alerts import build_market_alerts, load_config, scan_market
from src.anomaly_detector.detector import AnomalyResult


def _res(is_anomaly: bool, z: float) -> AnomalyResult:
    return AnomalyResult(
        is_anomaly=is_anomaly, z_score=z, last_return=0.05, mean=0.0,
        std=0.01, window=20, threshold=3.0,
    )


def test_build_market_alerts_so_para_anomalias():
    results = [("AAPL", _res(False, 0.5)), ("TSLA", _res(True, 7.6))]
    alerts = build_market_alerts(results)
    assert len(alerts) == 1
    assert "TSLA" in alerts[0]


def test_build_market_alerts_vazio_quando_nao_ha_anomalia():
    assert build_market_alerts([("AAPL", _res(False, 0.1))]) == []


def test_scan_market_desligado_devolve_vazio():
    assert scan_market({"market": {"enabled": False}}) == []


def test_load_config_le_a_watchlist():
    cfg = load_config()
    assert cfg["market"]["tickers"]  # watchlist não vazia
    assert "threshold" in cfg["market"]
