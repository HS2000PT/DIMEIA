"""Testes unitários do detetor de anomalias (puros, sem rede nem Telegram)."""

import pandas as pd
import pytest

from investigator.anomaly_detector.detector import detect_all, detect_latest


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


def test_detect_all_encontra_todas_as_anomalias_e_ignora_normais():
    """O motor do replay histórico: encontra os dias anómalos (e só esses) numa série."""
    vals = _base_returns(45)
    vals[25] = 0.06   # spike a subir
    vals[40] = -0.05  # spike a descer
    found = detect_all(pd.Series(vals), window=20, threshold=3.0)
    idxs = [i for i, _ in found]
    assert 25 in idxs and 40 in idxs
    assert all(i in (25, 40) for i in idxs)  # nenhum dia normal é sinalizado


def test_detect_all_consistente_com_detect_latest_sem_lookahead():
    """O z de cada dia no replay = o que `detect_latest` daria nesse ponto (mesma norma)."""
    vals = _base_returns(45)
    vals[30] = 0.07
    res_all = next(r for i, r in detect_all(pd.Series(vals), window=20, threshold=3.0) if i == 30)
    ref = detect_latest(vals[:31], window=20, threshold=3.0)  # série até ao dia 30 inclusive
    assert res_all.z_score == pytest.approx(ref.z_score)
    assert res_all.last_return == pytest.approx(ref.last_return)
