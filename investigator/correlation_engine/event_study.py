"""Event study: impacto observado de um evento (notícia) via retornos pós-evento.

Mede o retorno cumulativo do preço entre o dia do evento e +h dias (ex.: +1, +3, +5).
Isto é a EVIDÊNCIA/medida de impacto (o "outcome" posterior), não uma feature — não viola a
regra anti-lookahead (§6.5), que proíbe usar o futuro para PREVER; aqui apenas medimos o que
aconteceu depois, para apresentar como precedente histórico.
"""

from __future__ import annotations

import pandas as pd


def post_event_returns(close: pd.Series, event_idx: int,
                       horizons: tuple[int, ...] = (1, 3, 5)) -> dict[int, float]:
    """Retorno cumulativo do fecho em +h dias após o evento, para cada horizonte.

    Args:
        close: série de preços de fecho (índice posicional 0..n-1).
        event_idx: posição do dia do evento.
        horizons: horizontes em dias (ex.: (1, 3, 5)).

    Returns:
        dict {h: retorno cumulativo de event_idx até event_idx+h}; NaN se ultrapassar a série.
    """
    if event_idx < 0 or event_idx >= len(close):
        raise IndexError(f"event_idx {event_idx} fora da série (len={len(close)}).")
    p0 = float(close.iloc[event_idx])
    out: dict[int, float] = {}
    for h in horizons:
        j = event_idx + h
        out[h] = float(close.iloc[j] / p0 - 1.0) if 0 <= j < len(close) else float("nan")
    return out


def mean_impact(impacts: list[dict[int, float]], horizon: int) -> float:
    """Impacto médio (entre vários eventos/precedentes) para um dado horizonte, ignorando NaN."""
    vals = [d[horizon] for d in impacts if horizon in d and d[horizon] == d[horizon]]  # exclui NaN
    if not vals:
        return float("nan")
    return sum(vals) / len(vals)


def abnormal_returns(close: pd.Series, market_close: pd.Series, event_idx: int,
                     horizons: tuple[int, ...] = (1, 3, 5)) -> dict[int, float]:
    """Retorno ANORMAL pós-evento: retorno do ticker menos o retorno do mercado (ajuste de mercado).

    Operacionaliza a discussão raw-vs-CAR do Cap. 3: subtrair o movimento do mercado (ex.: SPY)
    isola o que é específico da empresa. As duas séries têm de estar ALINHADAS pelo chamador
    (mesmas datas, mesmo comprimento, índice posicional) — ver scripts/build_dataset.py.

    Returns:
        dict {h: retorno_ticker − retorno_mercado}; NaN propaga se qualquer janela sair da série.
    """
    if len(close) != len(market_close):
        raise ValueError(
            f"Séries desalinhadas: ticker tem {len(close)} pontos, mercado tem {len(market_close)}."
        )
    own = post_event_returns(close, event_idx, horizons)
    mkt = post_event_returns(market_close, event_idx, horizons)
    return {h: own[h] - mkt[h] for h in horizons}
