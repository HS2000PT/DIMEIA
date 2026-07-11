"""Deteção de anomalias: z-score do retorno vs. média/desvio móveis (transparente, XAI).

Sem lookahead (§6.5): a média e o desvio são calculados sobre a janela de dias ANTERIORES
ao dia avaliado; o dia avaliado não entra no cálculo da norma.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class AnomalyResult:
    """Resultado da deteção para o dia mais recente."""

    is_anomaly: bool
    z_score: float
    last_return: float
    mean: float
    std: float
    window: int
    threshold: float


def detect_latest(returns, window: int = 20, threshold: float = 3.0) -> AnomalyResult:
    """Avalia se o retorno mais recente é anómalo via z-score sobre a janela anterior.

    Args:
        returns: série/sequência de retornos (o último elemento é o dia a avaliar).
        window: nº de dias anteriores usados para média/desvio (a norma).
        threshold: limiar de |z| acima do qual se sinaliza anomalia.
    """
    r = pd.Series(list(returns), dtype="float64").dropna().reset_index(drop=True)
    if len(r) < window + 1:
        raise ValueError(f"São precisos pelo menos {window + 1} retornos (recebidos {len(r)}).")

    recent = r.iloc[-window - 1 : -1]  # janela ANTES do último (sem lookahead)
    last = float(r.iloc[-1])
    mu = float(recent.mean())
    sigma = float(recent.std(ddof=1))
    z = (last - mu) / sigma if sigma > 0 else 0.0
    return AnomalyResult(
        is_anomaly=abs(z) > threshold,
        z_score=z,
        last_return=last,
        mean=mu,
        std=sigma,
        window=window,
        threshold=threshold,
    )


def detect_intraday(running_return: float, returns, window: int = 20,
                    threshold: float = 3.0) -> AnomalyResult:
    """Avalia o retorno DE HOJE em curso (cotação ao vivo vs fecho anterior) contra a
    norma dos retornos DIÁRIOS anteriores — o mesmo z-score transparente, mais cedo.

    "Caiu 4,8% em 12 minutos" não devia esperar pelo fecho: se o movimento em curso já é
    anómalo face à volatilidade típica da ação, o alerta pode sair AGORA. Sem lookahead:
    a norma usa só dias completos anteriores; o dia de hoje (parcial) nunca entra nela.
    """
    r = pd.Series(list(returns), dtype="float64").dropna().reset_index(drop=True)
    if len(r) < window:
        raise ValueError(f"São precisos pelo menos {window} retornos (recebidos {len(r)}).")
    recent = r.iloc[-window:]  # os últimos `window` dias COMPLETOS (hoje não está na série)
    mu = float(recent.mean())
    sigma = float(recent.std(ddof=1))
    z = (float(running_return) - mu) / sigma if sigma > 0 else 0.0
    return AnomalyResult(
        is_anomaly=abs(z) > threshold,
        z_score=z,
        last_return=float(running_return),
        mean=mu,
        std=sigma,
        window=window,
        threshold=threshold,
    )
