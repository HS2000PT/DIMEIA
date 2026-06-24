"""Camada live: preços de mercado (NYSE/NASDAQ) via yfinance.

A deteção de anomalias trabalha sobre RETORNOS (não preços) — ver docs/decisions/learning.md.
O import do yfinance é tardio (dentro da função) para os testes unitários não dependerem da rede.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def get_price_history(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Descarrega o histórico recente de preços de um ticker (camada live)."""
    import yfinance as yf

    df = yf.Ticker(ticker).history(period=period, interval=interval)
    if df is None or df.empty:
        raise RuntimeError(f"Sem dados de preços para o ticker '{ticker}'.")
    return df


def log_returns(close: pd.Series) -> pd.Series:
    """Retornos logarítmicos a partir da série de preços de fecho."""
    return np.log(close / close.shift(1)).dropna()
