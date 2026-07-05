"""Testes do runner de alertas — a parte pura (sem rede)."""

from __future__ import annotations

from investigator.anomaly_detector.detector import AnomalyResult
from scripts.run_alerts import build_market_alerts, load_config, scan_market


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


def test_news_is_fresh_anti_repeticao():
    from datetime import date

    from scripts.run_alerts import news_is_fresh

    hoje = date(2026, 7, 6)  # segunda
    assert news_is_fresh("2026-07-06", hoje) is True   # de hoje
    assert news_is_fresh("2026-07-04", hoje) is True   # sábado → ainda alerta na segunda
    assert news_is_fresh("2026-07-03", hoje) is False  # 3 dias → já alertou na altura
    assert news_is_fresh("2026-07-07", hoje) is False  # futuro (dados tortos) → não
    assert news_is_fresh("data-invalida", hoje) is False


def test_bar_is_fresh_anti_duplicado():
    from datetime import date

    from scripts.run_alerts import bar_is_fresh

    assert bar_is_fresh(date(2026, 7, 6), date(2026, 7, 6)) is True   # sessão de hoje
    assert bar_is_fresh(date(2026, 7, 3), date(2026, 7, 6)) is False  # feriado: barra de sexta
