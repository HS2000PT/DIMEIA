"""Testes unitários do detetor de anomalias (puros, sem rede nem Telegram)."""

import pytest

from src.anomaly_detector.detector import detect_latest


def _base_returns(n: int = 30) -> list[float]:
    """Retornos pequenos alternados (média ~0, desvio pequeno > 0)."""
    return [0.001 if i % 2 == 0 else -0.001 for i in range(n)]


def test_deteta_movimento_anomalo():
    returns = _base_returns(30) + [0.05]  # spike grande no último dia
    res = detect_latest(returns, window=20, threshold=3.0)
    assert res.is_anomaly is True
    assert res.z_score > 3.0
    assert res.last_return == pytest.approx(0.05)


def test_nao_sinaliza_movimento_normal():
    returns = _base_returns(30) + [0.0009]  # dentro da norma
    res = detect_latest(returns, window=20, threshold=3.0)
    assert res.is_anomaly is False
    assert abs(res.z_score) <= 3.0


def test_dados_insuficientes_levanta_erro():
    with pytest.raises(ValueError):
        detect_latest([0.001, -0.001, 0.002], window=20)


def test_sem_lookahead_usa_janela_anterior():
    # O último valor não deve afetar a média/desvio da norma (janela anterior).
    returns = _base_returns(20) + [0.10]
    res = detect_latest(returns, window=10, threshold=3.0)
    # média/desvio calculados sobre os 10 dias anteriores (todos ~±0.001), não sobre o spike
    assert abs(res.mean) < 0.01
    assert res.std < 0.01
