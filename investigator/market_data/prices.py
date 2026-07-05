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


def load_close_series(tickers: list[str], start: str, end: str) -> dict[str, pd.Series]:
    """Fechos diários por ticker numa janela (para construir KBs/datasets).

    Índice tz-naive e ordenado — pronto para `searchsorted` contra datas de notícias.
    Tickers sem dados são avisados e ignorados (best-effort, como o resto da camada live).
    """
    import yfinance as yf

    prices: dict[str, pd.Series] = {}
    for ticker in tickers:
        df = yf.Ticker(ticker).history(start=start, end=end, interval="1d")
        if df is None or df.empty:
            print(f"  [!] sem precos para {ticker} - ignorado")
            continue
        close = df["Close"].copy()
        close.index = pd.to_datetime(close.index).tz_localize(None)
        prices[ticker] = close.sort_index()
        print(f"  [ok] {ticker}: {len(close)} dias")
    return prices
