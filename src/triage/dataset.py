"""Construção do dataset de triagem: features de contexto, rótulos e divisão temporal.

Tudo PURO (sem rede): o I/O (buscar preços, ler o CSV de notícias) vive em
scripts/build_dataset.py. Convenção temporal fixada (ML_PLAN §2), com d = dia do evento:

- vol20      = desvio-padrão dos 20 log-retornos que terminam no fecho de d−1  (regime pré-notícia)
- mom5       = log-retorno acumulado dos 5 dias que terminam no fecho de d−1
- ret_event  = log-retorno d−1 → d (a reação imediata; conhecida no fecho de d)
- rótulo     = |retorno anormal em (d, d+h]| ≥ τ  (janela começa no fecho de d)

Não há sobreposição entre features e janela do rótulo, e nenhuma feature usa dados
posteriores ao fecho de d — o teste anti-lookahead em tests/test_triage_dataset.py
verifica exatamente isto.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from src.correlation_engine.event_study import abnormal_returns

# Mapa canónico ticker → setor (igual a scripts/evaluate.py — não alterar um sem o outro).
SECTORS = {
    "AAPL": "tech", "MSFT": "tech", "AMZN": "tech", "GOOGL": "tech", "NVDA": "tech",
    "TSLA": "tech", "META": "tech",
    "JPM": "banking", "BAC": "banking",
    "XOM": "energy", "CVX": "energy",
    "JNJ": "health", "PFE": "health",
    "WMT": "consumer", "KO": "consumer",
}

# Mínimo de histórico para calcular vol20 (20 retornos ⇒ 21 fechos antes do evento).
MIN_HISTORY = 21


def event_features(close: pd.Series, event_idx: int,
                   vol_window: int = 20, mom_window: int = 5) -> dict[str, float] | None:
    """Features de contexto de mercado no dia do evento (só dados ≤ fecho de event_idx).

    Devolve None se não houver histórico suficiente (event_idx < vol_window + 1).
    """
    if event_idx < vol_window + 1 or event_idx >= len(close):
        return None
    c = np.asarray(close, dtype="float64")
    log_r = np.diff(np.log(c))  # log_r[i] = retorno do fecho i → i+1
    # Retornos que terminam em d−1: índices [d−1−vol_window, d−1) na série de retornos.
    pre = log_r[event_idx - 1 - vol_window : event_idx - 1]
    vol20 = float(np.std(pre, ddof=1))
    mom5 = float(math.log(c[event_idx - 1] / c[event_idx - 1 - mom_window]))
    ret_event = float(math.log(c[event_idx] / c[event_idx - 1]))
    return {"vol20": vol20, "mom5": mom5, "ret_event": ret_event}


def abnormal_label(close: pd.Series, market_close: pd.Series, event_idx: int,
                   tau: float, horizon: int) -> int | None:
    """Rótulo binário: 1 se |retorno anormal em (d, d+h]| ≥ τ; None se o futuro não existe."""
    ar = abnormal_returns(close, market_close, event_idx, (horizon,))[horizon]
    if ar != ar:  # NaN — a janela ultrapassa a série (evento demasiado recente)
        return None
    return int(abs(ar) >= tau)


def assign_splits(dates: pd.Series, train_frac: float = 0.70, val_frac: float = 0.15,
                  embargo_days: int = 5) -> pd.Series:
    """Divisão TEMPORAL por dias únicos (70/15/15) com embargo entre blocos.

    Todas as linhas do mesmo dia ficam no mesmo bloco (evita fuga por notícias do mesmo dia).
    O embargo remove `embargo_days` dias únicos APÓS cada fronteira (rotulados "embargo",
    excluídos do treino e da avaliação) — protege contra sobreposição das janelas de rótulo
    (h≤5) entre blocos.
    """
    d = pd.to_datetime(pd.Series(dates).reset_index(drop=True))
    unique_days = np.array(sorted(d.unique()))
    n = len(unique_days)
    i1 = int(n * train_frac)
    i2 = int(n * (train_frac + val_frac))
    train_days = set(unique_days[:i1])
    emb1 = set(unique_days[i1 : i1 + embargo_days])
    val_days = set(unique_days[i1 + embargo_days : i2])
    emb2 = set(unique_days[i2 : i2 + embargo_days])
    test_days = set(unique_days[i2 + embargo_days :])

    def _tag(day) -> str:
        if day in train_days:
            return "train"
        if day in val_days:
            return "val"
        if day in test_days:
            return "test"
        if day in emb1 or day in emb2:
            return "embargo"
        return "embargo"  # inalcançável; defensivo

    return d.map(_tag)
