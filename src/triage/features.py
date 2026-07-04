"""Montagem de features para a triagem: blocos de contexto + texto (embedding).

Devolve BLOCOS separados para permitir as ablações (só-contexto / só-texto / ambos) sem
recomputar nada. O embedder é injetado (Protocol `Embedder`) — nos testes usa-se o
`HashingEmbedder` (offline); no treino real o SBERT MiniLM.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.historical_kb.embedder import Embedder
from src.triage.dataset import SECTORS

# Ordem fixa (determinística) das colunas de contexto e dos setores no one-hot.
CONTEXT_COLS = ["vol20", "mom5", "ret_event", "headline_len"]
SECTOR_ORDER = sorted(set(SECTORS.values()))  # ['banking', 'consumer', 'energy', 'health', 'tech']


def context_block(df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    """Bloco de contexto: colunas numéricas + one-hot do setor. Devolve (X, nomes)."""
    num = df[CONTEXT_COLS].to_numpy(dtype="float64")
    onehot = np.zeros((len(df), len(SECTOR_ORDER)), dtype="float64")
    for j, sec in enumerate(SECTOR_ORDER):
        onehot[:, j] = (df["sector"] == sec).to_numpy(dtype="float64")
    names = CONTEXT_COLS + [f"sector_{s}" for s in SECTOR_ORDER]
    return np.hstack([num, onehot]), names


def text_block(df: pd.DataFrame, embedder: Embedder) -> tuple[np.ndarray, list[str]]:
    """Bloco de texto: embedding do título (L2-normalizado pelo embedder). Devolve (X, nomes)."""
    emb = embedder.encode(df["headline"].astype(str).tolist())
    emb = np.asarray(emb, dtype="float64")
    names = [f"emb_{i}" for i in range(emb.shape[1])]
    return emb, names


def assemble(df: pd.DataFrame, embedder: Embedder) -> dict[str, tuple[np.ndarray, list[str]]]:
    """Todos os blocos de uma vez: {'context': (X,nomes), 'text': (X,nomes), 'full': (X,nomes)}."""
    xc, nc = context_block(df)
    xt, nt = text_block(df, embedder)
    return {
        "context": (xc, nc),
        "text": (xt, nt),
        "full": (np.hstack([xc, xt]), nc + nt),
    }
