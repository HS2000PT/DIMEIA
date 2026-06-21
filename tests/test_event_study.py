"""Testes do event study (impacto pós-evento), puros e determinísticos."""

import pandas as pd
import pytest

from src.correlation_engine.event_study import mean_impact, post_event_returns


def test_retornos_pos_evento():
    # preços: evento no índice 2 (=100); +1->110 (+10%), +3->121 (+21%)
    close = pd.Series([90, 95, 100, 110, 105, 121])
    out = post_event_returns(close, event_idx=2, horizons=(1, 3))
    assert out[1] == pytest.approx(0.10)
    assert out[3] == pytest.approx(0.21)


def test_horizonte_fora_da_serie_da_nan():
    close = pd.Series([100, 101, 102])
    out = post_event_returns(close, event_idx=2, horizons=(1, 3))
    assert out[1] != out[1]  # NaN (102 -> índice 3 não existe)
    assert out[3] != out[3]  # NaN


def test_event_idx_invalido_levanta():
    with pytest.raises(IndexError):
        post_event_returns(pd.Series([100.0, 101.0]), event_idx=5)


def test_impacto_medio_ignora_nan():
    impactos = [{1: 0.10}, {1: 0.20}, {1: float("nan")}]
    assert mean_impact(impactos, horizon=1) == pytest.approx(0.15)
