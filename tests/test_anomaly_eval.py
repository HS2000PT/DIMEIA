"""Testes da avaliação do detetor de anomalias (puros, determinísticos)."""

import numpy as np
import pytest

from investigator.evaluation.anomaly_eval import (
    firing_rate,
    fixed_threshold_flags,
    label_extreme_moves,
    precision_recall_f1,
    rolling_zscore_flags,
)


def test_rolling_zscore_assinala_o_pico():
    # retornos pequenos alternados + um pico grande no fim
    returns = [0.001 if i % 2 == 0 else -0.001 for i in range(30)] + [0.06]
    flags = rolling_zscore_flags(returns, window=20, threshold=3.0)
    assert flags[-1]  # o pico é anomalia
    assert flags[:20].sum() == 0  # antes da janela não há sinal


def test_fixed_threshold_flags():
    flags = fixed_threshold_flags([0.01, -0.05, 0.02, 0.10], pct=0.03)
    assert list(flags) == [False, True, False, True]


def test_label_extreme_moves():
    returns = [0.01] * 99 + [0.5]
    label = label_extreme_moves(returns, q=0.99)
    assert label[-1]  # o movimento de 0.5 é extremo
    assert label[:99].sum() == 0


def test_precision_recall_f1():
    pred = [True, True, False, False]
    label = [True, False, False, True]
    p, r, f1 = precision_recall_f1(pred, label)
    assert p == pytest.approx(0.5)   # 1 TP / (1 TP + 1 FP)
    assert r == pytest.approx(0.5)   # 1 TP / (1 TP + 1 FN)
    assert f1 == pytest.approx(0.5)


def test_firing_rate():
    assert firing_rate([True, False, True, False]) == pytest.approx(0.5)
    assert firing_rate([]) == 0.0


def test_zscore_normaliza_volatilidade():
    """A taxa de disparo do z-score é parecida entre séries de volatilidades diferentes;
    a do limiar fixo não."""
    rng = np.random.default_rng(0)
    calmo = rng.normal(0, 0.005, 2000)
    volatil = rng.normal(0, 0.05, 2000)
    z_calmo = firing_rate(rolling_zscore_flags(calmo, 20, 3.0))
    z_vol = firing_rate(rolling_zscore_flags(volatil, 20, 3.0))
    f_calmo = firing_rate(fixed_threshold_flags(calmo, 0.03))
    f_vol = firing_rate(fixed_threshold_flags(volatil, 0.03))
    # z-score: taxas próximas (normaliza); limiar fixo: muito diferentes
    assert abs(z_calmo - z_vol) < 0.02
    assert (f_vol - f_calmo) > 0.1
