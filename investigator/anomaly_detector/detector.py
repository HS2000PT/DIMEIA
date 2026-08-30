"""Deteção de anomalias: z-score do retorno vs. média/desvio móveis (transparente, XAI).

Sem lookahead (§6.5): a média e o desvio são calculados sobre a janela de dias ANTERIORES
ao dia avaliado; o dia avaliado não entra no cálculo da norma.
"""

from __future__ import annotations

import math
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
    zero_variance: bool = False

    @property
    def score_magnitude(self) -> float:
        """Magnitude para ordenação, incluindo o caso em que o z não está definido."""
        if self.zero_variance and self.is_anomaly:
            return math.inf
        return abs(self.z_score)

    @property
    def reported_z(self) -> float | None:
        """Z publicável; `None` quando a divisão por desvio-padrão não existe."""
        return None if self.zero_variance else self.z_score

    @property
    def baseline_direction(self) -> int:
        """Sinal do afastamento à média, útil quando não existe sinal de z-score."""
        return 1 if self.last_return > self.mean else -1 if self.last_return < self.mean else 0


def _score(last: float, mu: float, sigma: float, threshold: float) -> tuple[float, bool, bool]:
    """Calcula o z e resolve explicitamente uma norma com variância nula.

    Se a janela anterior for constante, o z-score não está definido. Manter o mesmo valor não é
    anómalo; afastar-se dele é sinalizado sem inventar um z finito. `z_score=0.0` fica apenas como
    sentinela compatível, e `zero_variance` obriga os consumidores a explicar o caso pelo nome.
    """
    if sigma > 0.0:
        z = (last - mu) / sigma
        return z, abs(z) > threshold, False
    moved = not math.isclose(last, mu, rel_tol=0.0, abs_tol=1e-15)
    return 0.0, moved, True


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
    z, is_anomaly, zero_variance = _score(last, mu, sigma, threshold)
    return AnomalyResult(
        is_anomaly=is_anomaly,
        z_score=z,
        last_return=last,
        mean=mu,
        std=sigma,
        window=window,
        threshold=threshold,
        zero_variance=zero_variance,
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
    last = float(running_return)
    z, is_anomaly, zero_variance = _score(last, mu, sigma, threshold)
    return AnomalyResult(
        is_anomaly=is_anomaly,
        z_score=z,
        last_return=last,
        mean=mu,
        std=sigma,
        window=window,
        threshold=threshold,
        zero_variance=zero_variance,
    )


def detect_all(
    returns, window: int = 20, threshold: float = 2.0
) -> list[tuple[Any, AnomalyResult]]:
    """Todos os dias anómalos da série (a norma sem lookahead de `detect_latest`,
    aplicada a cada dia). É o motor do "replay histórico": a deteção da RQ1 corrida sobre o
    passado para povoar o gráfico com os eventos que o método realmente detetaria.

    Devolve [(rótulo_do_índice, AnomalyResult), …] para cada dia sinalizado. Além de
    |z| > threshold, isto inclui um movimento após uma janela de variância nula. Preserva o índice
    da série (datas), para mapear diretamente aos pontos do gráfico.
    """
    r = pd.Series(returns, dtype="float64").dropna()
    vals = r.to_numpy()
    idx = list(r.index)
    out: list[tuple[Any, AnomalyResult]] = []
    for i in range(window, len(vals)):
        recent = r.iloc[i - window : i]  # janela ANTES do dia i (sem lookahead)
        mu = float(recent.mean())
        sigma = float(recent.std(ddof=1))
        last = float(vals[i])
        z, is_anomaly, zero_variance = _score(last, mu, sigma, threshold)
        if is_anomaly:
            out.append((idx[i], AnomalyResult(
                is_anomaly=True, z_score=z, last_return=last,
                mean=mu, std=sigma, window=window, threshold=threshold,
                zero_variance=zero_variance,
            )))
    return out
