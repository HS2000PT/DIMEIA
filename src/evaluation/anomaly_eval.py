"""Avaliação do detetor de anomalias (Pergunta 1, docs/design/evaluation_design.md §1).

Duas evidências honestas:
1. **Consistência da taxa de disparo entre tickers** (argumento principal, não circular): um limiar
   fixo em % dispara muitíssimo mais em ações voláteis (TSLA, NVDA) do que em calmas (KO), logo não
   é um detetor universal; o **z-score** normaliza pela volatilidade recente, pelo que dispara a uma
   taxa ~constante em todos os tickers. Medimos a dispersão da taxa de disparo entre tickers.
2. **Precision/recall/F1 vs um rótulo-proxy** (suporte, com caveat): rótulo = movimento extremo
   (|retorno| >= percentil alto, por ticker). É uma definição operacional (proxy), não verdade
   absoluta — assumido como limitação.

Tudo puro NumPy e sem lookahead: o z-score de cada dia usa apenas a janela de dias ANTERIORES.
"""

from __future__ import annotations

import numpy as np


def rolling_zscore_flags(returns, window: int = 20, threshold: float = 3.0) -> np.ndarray:
    """Sinaliza anomalias por z-score com janela móvel (mesma regra do detetor, sem lookahead).

    Para cada dia i (a partir de `window`), z = (r_i − média) / desvio da janela i-window..i-1
    (dias estritamente anteriores → sem lookahead). Marca True se |z| > threshold.
    """
    r = np.asarray(returns, dtype="float64")
    flags = np.zeros(len(r), dtype=bool)
    for i in range(window, len(r)):
        w = r[i - window:i]
        sd = w.std(ddof=1)
        if sd > 0 and abs((r[i] - w.mean()) / sd) > threshold:
            flags[i] = True
    return flags


def fixed_threshold_flags(returns, pct: float = 0.03) -> np.ndarray:
    """Baseline ingénua: marca dias com |retorno| >= `pct` (limiar fixo global, igual p/ todos)."""
    return np.abs(np.asarray(returns, dtype="float64")) >= pct


def label_extreme_moves(returns, q: float = 0.99) -> np.ndarray:
    """Rótulo-proxy de 'anomalia verdadeira': |retorno| no percentil >= q DESTE ticker."""
    r = np.abs(np.asarray(returns, dtype="float64"))
    if len(r) == 0:
        return np.zeros(0, dtype=bool)
    return r >= np.quantile(r, q)


def precision_recall_f1(pred, label) -> tuple[float, float, float]:
    """Precision, recall e F1 entre previsões e rótulos booleanos (divisões por zero → 0)."""
    pred = np.asarray(pred, dtype=bool)
    label = np.asarray(label, dtype=bool)
    tp = int((pred & label).sum())
    fp = int((pred & ~label).sum())
    fn = int((~pred & label).sum())
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f1


def firing_rate(flags) -> float:
    """Fração de dias sinalizados."""
    f = np.asarray(flags, dtype=bool)
    return float(f.mean()) if len(f) else 0.0
