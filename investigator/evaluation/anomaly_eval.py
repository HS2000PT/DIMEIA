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


def ewma_zscore_flags(returns, lam: float = 0.94, threshold: float = 3.0,
                      window: int = 20) -> np.ndarray:
    """z-score com volatilidade EWMA (RiskMetrics, λ=0.94) — o degrau entre a σ rolling e
    um GARCH completo (CS1-ext, 2026-07-13).

    Responde empiricamente ao "porquê rolling-std e não GARCH?": o EWMA pondera o passado
    recente exponencialmente (reage mais depressa a mudanças de regime) sem estimar
    parâmetros por ticker. Causal como o rolling: σ²_i usa APENAS retornos ≤ i−1
    (σ²_i = λ·σ²_{i−1} + (1−λ)·r²_{i−1}, média zero como no RiskMetrics clássico);
    inicializa com a variância dos primeiros `window` dias e só sinaliza a partir daí
    (mesma região do rolling → comparável).
    """
    r = np.asarray(returns, dtype="float64")
    n = len(r)
    flags = np.zeros(n, dtype=bool)
    if n <= window:
        return flags
    var = float(np.var(r[:window], ddof=1))
    for i in range(window, n):
        var = lam * var + (1.0 - lam) * r[i - 1] ** 2
        sd = np.sqrt(var)
        if sd > 0 and abs(r[i] / sd) > threshold:
            flags[i] = True
    return flags


def lof_flags(returns, window: int = 20, train_days: int = 250,
              contamination: float = 0.02, n_neighbors: int = 20,
              ) -> tuple[np.ndarray, np.ndarray]:
    """Detetor APRENDIDO nº 2 — Local Outlier Factor, causal e comparável (CS1-ext).

    A tese citava o LOF como alternativa mas só o Isolation Forest tinha sido testado.
    MESMO protocolo do IF (isolation_forest_flags): features causais [retorno, vol20
    anterior], treino nos primeiros `train_days` dias válidos, pontuação dos seguintes
    (novelty=True — o modelo nunca vê o futuro), `contamination` igual. Determinístico
    (o LOF não tem aleatoriedade). Devolve (flags, scored) como o IF.
    """
    from sklearn.neighbors import LocalOutlierFactor  # import tardio

    r = np.asarray(returns, dtype="float64")
    n = len(r)
    flags = np.zeros(n, dtype=bool)
    scored = np.zeros(n, dtype=bool)
    if n < window + train_days + 1:
        return flags, scored
    feats = np.zeros((n, 2), dtype="float64")
    for i in range(window, n):
        w = r[i - window : i]
        feats[i] = (r[i], w.std(ddof=1))
    train_idx = np.arange(window, window + train_days)
    model = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination,
                               novelty=True)
    model.fit(feats[train_idx])
    test_idx = np.arange(window + train_days, n)
    flags[test_idx] = model.predict(feats[test_idx]) == -1
    scored[test_idx] = True
    return flags, scored


def isolation_forest_flags(returns, window: int = 20, train_days: int = 250,
                           contamination: float = 0.02, seed: int = 42,
                           ) -> tuple[np.ndarray, np.ndarray]:
    """Detetor APRENDIDO (Isolation Forest, não-supervisionado) — causal e comparável (M4).

    Comparação "estatístico vs aprendido" com a mesma informação do z-score: cada dia i tem
    features [retorno_i, vol20_i] (vol dos 20 dias ANTERIORES — causal). O modelo treina nos
    primeiros `train_days` dias válidos (só passado) e pontua os dias seguintes — nunca vê o
    futuro, como o z-score. `contamination` fixa a taxa de disparo alvo (comparável ao z-score).

    Returns:
        (flags, scored): flags[i] True se anomalia; scored[i] True nos dias efetivamente
        pontuados (após janela + treino). Métricas devem comparar SÓ na região `scored`.
    """
    from sklearn.ensemble import IsolationForest  # import tardio (evita custo quando não usado)

    r = np.asarray(returns, dtype="float64")
    n = len(r)
    flags = np.zeros(n, dtype=bool)
    scored = np.zeros(n, dtype=bool)
    if n < window + train_days + 1:
        return flags, scored
    feats = np.zeros((n, 2), dtype="float64")
    for i in range(window, n):
        w = r[i - window : i]
        feats[i] = (r[i], w.std(ddof=1))
    train_idx = np.arange(window, window + train_days)
    model = IsolationForest(n_estimators=200, contamination=contamination, random_state=seed)
    model.fit(feats[train_idx])
    test_idx = np.arange(window + train_days, n)
    flags[test_idx] = model.predict(feats[test_idx]) == -1
    scored[test_idx] = True
    return flags, scored
