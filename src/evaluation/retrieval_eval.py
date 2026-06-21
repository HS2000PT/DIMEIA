"""Avaliação da recuperação de precedentes (Pergunta A, docs/evaluation_design.md §2).

Métrica: **precision@k por setor**, em recuperação **cross-ticker** — para cada notícia
(consulta) recuperam-se os k vizinhos mais semelhantes vindos de OUTRAS empresas e mede-se a
fração que pertence ao mesmo setor. Isto testa se os embeddings captam analogia temática
(ex.: notícia da Tesla → outras de tecnologia/EV), e não apenas o nome da empresa.

Baselines (para mostrar que os embeddings acrescentam valor sobre alternativas triviais):
- **aleatório / taxa-base:** fração esperada de candidatos do mesmo setor (exato, sem ruído);
- **recência:** os k candidatos mais recentes permitidos.

Tudo puro NumPy e determinístico. Assume embeddings normalizados (L2) → produto interno = cosseno
(o SBERT e o HashingEmbedder já normalizam). Sem lookahead na métrica em si; a coerência temporal
do impacto é tratada no event study (Pergunta B).
"""

from __future__ import annotations

import numpy as np


def _normalize_rows(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def same_ticker_forbid(query_tickers: np.ndarray, cand_tickers: np.ndarray) -> np.ndarray:
    """Máscara (q, n): True onde o candidato é da MESMA empresa da consulta (a excluir)."""
    return query_tickers[:, None] == cand_tickers[None, :]


def retrieval_precision_at_k(
    query_emb: np.ndarray,
    cand_emb: np.ndarray,
    query_sectors: np.ndarray,
    cand_sectors: np.ndarray,
    k: int = 5,
    forbid: np.ndarray | None = None,
) -> float:
    """Precision@k média: fração dos k vizinhos mais semelhantes no mesmo setor da consulta.

    `forbid` (q, n) marca candidatos proibidos (ex.: mesma empresa) — recebem similaridade -inf.
    """
    q = _normalize_rows(np.asarray(query_emb, dtype="float64"))
    c = _normalize_rows(np.asarray(cand_emb, dtype="float64"))
    sims = q @ c.T  # (q, n) cosseno
    if forbid is not None:
        sims = np.where(forbid, -np.inf, sims)
    n = sims.shape[1]
    kk = min(k, n)
    # top-k por linha (sem necessidade de ordenar — precision@k é sobre o conjunto)
    topk = np.argpartition(-sims, kth=kk - 1, axis=1)[:, :kk]
    hits = cand_sectors[topk] == query_sectors[:, None]  # (q, kk)
    return float(hits.mean())


def expected_random_precision(
    query_sectors: np.ndarray,
    cand_sectors: np.ndarray,
    forbid: np.ndarray | None = None,
) -> float:
    """Taxa-base: fração média de candidatos permitidos que partilham o setor da consulta.

    É a precision esperada de uma recuperação aleatória (valor exato, sem amostragem).
    """
    q_sec = np.asarray(query_sectors)
    c_sec = np.asarray(cand_sectors)
    rates = []
    for i in range(len(q_sec)):
        allowed = np.ones(len(c_sec), dtype=bool)
        if forbid is not None:
            allowed = ~forbid[i]
        if not allowed.any():
            continue
        rates.append(float(np.mean(c_sec[allowed] == q_sec[i])))
    return float(np.mean(rates)) if rates else float("nan")


def recency_precision_at_k(
    query_sectors: np.ndarray,
    cand_sectors: np.ndarray,
    cand_dates: np.ndarray,
    k: int = 5,
    forbid: np.ndarray | None = None,
) -> float:
    """Precision@k da baseline de recência: os k candidatos permitidos mais recentes."""
    c_sec = np.asarray(cand_sectors)
    order = np.argsort(np.asarray(cand_dates), kind="stable")[::-1]  # mais recente primeiro
    q_sec = np.asarray(query_sectors)
    precs = []
    for i in range(len(q_sec)):
        chosen, count = [], 0
        for j in order:
            if forbid is not None and forbid[i, j]:
                continue
            chosen.append(j)
            count += 1
            if count >= k:
                break
        if chosen:
            precs.append(float(np.mean(c_sec[chosen] == q_sec[i])))
    return float(np.mean(precs)) if precs else float("nan")
