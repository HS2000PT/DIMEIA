"""Deteção de anomalias: z-score do retorno vs. média/desvio móveis (transparente, XAI).

Sem lookahead (§6.5): a média e o desvio são calculados sobre a janela de dias ANTERIORES
ao dia avaliado; o dia avaliado não entra no cálculo da norma.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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


def detect_all(
    returns, window: int = 20, threshold: float = 2.0
) -> list[tuple[Any, AnomalyResult]]:
    """Todos os dias anómalos da série (a norma sem lookahead de `detect_latest`,
    aplicada a cada dia). É o motor do "replay histórico": a deteção da RQ1 corrida sobre o
    passado para povoar o gráfico com os eventos que o método realmente detetaria.

    Devolve [(rótulo_do_índice, AnomalyResult), …] para cada dia com |z| > threshold. Preserva
    o índice da série (datas), para mapear diretamente aos pontos do gráfico.
    """
    r = pd.Series(returns, dtype="float64").dropna()
    vals = r.to_numpy()
    idx = list(r.index)
    out: list[tuple[Any, AnomalyResult]] = []
    for i in range(window, len(vals)):
        recent = r.iloc[i - window : i]  # janela ANTES do dia i (sem lookahead)
        mu = float(recent.mean())
        sigma = float(recent.std(ddof=1))
        z = (float(vals[i]) - mu) / sigma if sigma > 0 else 0.0
        if abs(z) > threshold:
            out.append((idx[i], AnomalyResult(
                is_anomaly=True, z_score=z, last_return=float(vals[i]),
                mean=mu, std=sigma, window=window, threshold=threshold,
            )))
    return out
