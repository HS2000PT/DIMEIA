"""Similaridade entre embeddings (cosseno) — base do motor de correlação.

Puro NumPy, sem dependências pesadas, para ser determinístico, rápido e testável.
A similaridade do cosseno mede o ângulo entre dois vetores (1 = mesma direção/idênticos,
0 = ortogonais/não relacionados, -1 = opostos). É a métrica padrão para comparar embeddings
de texto (ver docs/learning.md). Aqui usamo-la para encontrar notícias históricas semelhantes
a uma notícia nova (recuperação de precedentes).
"""

from __future__ import annotations

import numpy as np


def cosine_similarity(a, b) -> float:
    """Similaridade do cosseno entre dois vetores 1D. Vetor nulo → 0.0 (sem direção)."""
    a = np.asarray(a, dtype="float64")
    b = np.asarray(b, dtype="float64")
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def cosine_similarities(query, matrix) -> np.ndarray:
    """Similaridade do cosseno entre um vetor `query` (1D) e cada linha de `matrix` (2D).

    Vetorizado: devolve um array (n_amostras,) com a similaridade de cada linha ao query.
    Linhas nulas (ou query nulo) recebem 0.0.
    """
    query = np.asarray(query, dtype="float64")
    matrix = np.asarray(matrix, dtype="float64")
    if matrix.ndim != 2:
        raise ValueError("`matrix` tem de ser 2D (n_amostras, dim).")
    if query.ndim != 1 or query.shape[0] != matrix.shape[1]:
        raise ValueError("dimensões incompatíveis entre `query` e `matrix`.")
    qn = float(np.linalg.norm(query))
    row_norms = np.linalg.norm(matrix, axis=1)
    denom = row_norms * qn
    dots = matrix @ query
    out = np.zeros_like(dots, dtype="float64")
    nz = denom > 0
    out[nz] = dots[nz] / denom[nz]
    return out


def top_k_similar(query, matrix, k: int = 5) -> list[tuple[int, float]]:
    """Índices e scores das `k` linhas mais semelhantes ao `query` (ordem decrescente).

    Devolve uma lista de (índice, score). Ordenação estável (desempates pela ordem original).
    """
    if k <= 0:
        return []
    sims = cosine_similarities(query, matrix)
    k = min(k, len(sims))
    # argsort decrescente e estável: ordena por -score, mantendo a ordem em empates.
    order = np.argsort(-sims, kind="stable")[:k]
    return [(int(i), float(sims[i])) for i in order]
