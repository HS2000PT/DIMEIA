"""Montagem de features para a triagem: blocos de contexto + texto (embedding).

Devolve BLOCOS separados para permitir as ablações (só-contexto / só-texto / ambos) sem
recomputar nada. O embedder é injetado (Protocol `Embedder`) — nos testes usa-se o
`HashingEmbedder` (offline); no treino real o SBERT MiniLM.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from investigator.historical_kb.embedder import Embedder
from investigator.triage.dataset import SECTORS

# Ordem fixa (determinística) das colunas de contexto e dos setores no one-hot.
CONTEXT_COLS = ["vol20", "mom5", "ret_event", "headline_len"]
SECTOR_ORDER = sorted(set(SECTORS.values()))  # ['banking', 'consumer', 'energy', 'health', 'tech']

# Features estendidas (RQ4-ext; ver docs/evaluation/roadmap_rq4.md). Só existem no dataset
# construído com `build_dataset.py --ext` (event_features_ext); o dataset congelado da tese
# não as tem, por isso `assemble` nunca produz o bloco "context_ext" no caminho de produção.
EXT_COLS = ["market_vol20", "mom20", "vol_ratio", "ret_event_z", "downside_vol20"]
CONTEXT_EXT_COLS = CONTEXT_COLS + EXT_COLS


def numeric_context_block(df: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, list[str]]:
    """Bloco de contexto genérico: colunas numéricas `cols` + one-hot do setor. Devolve (X, nomes).

    Permite as ablações da RQ4-ext (subconjuntos arbitrários de features) sem recomputar nada.
    """
    num = df[cols].to_numpy(dtype="float64")
    onehot = np.zeros((len(df), len(SECTOR_ORDER)), dtype="float64")
    for j, sec in enumerate(SECTOR_ORDER):
        onehot[:, j] = (df["sector"] == sec).to_numpy(dtype="float64")
    names = list(cols) + [f"sector_{s}" for s in SECTOR_ORDER]
    return np.hstack([num, onehot]), names


def context_block(df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    """Bloco de contexto (v1, congelado): numéricas + one-hot do setor. Devolve (X, nomes)."""
    return numeric_context_block(df, CONTEXT_COLS)


def context_ext_block(df: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    """Bloco de contexto ESTENDIDO (v1 + 5 features baratas da RQ4-ext) + one-hot do setor."""
    return numeric_context_block(df, CONTEXT_EXT_COLS)


def text_block(df: pd.DataFrame, embedder: Embedder) -> tuple[np.ndarray, list[str]]:
    """Bloco de texto: embedding do título (L2-normalizado pelo embedder). Devolve (X, nomes)."""
    emb = embedder.encode(df["headline"].astype(str).tolist())
    emb = np.asarray(emb, dtype="float64")
    names = [f"emb_{i}" for i in range(emb.shape[1])]
    return emb, names


def assemble(df: pd.DataFrame, embedder: Embedder) -> dict[str, tuple[np.ndarray, list[str]]]:
    """Todos os blocos de uma vez: {'context': (X,nomes), 'text': (X,nomes), 'full': (X,nomes)}.

    Se o dataframe tiver as colunas estendidas (RQ4-ext), acrescenta também 'context_ext' e
    'full_ext' — aditivo, nunca altera os blocos existentes (o dataset congelado não tem essas
    colunas, por isso o caminho de produção fica byte-idêntico).
    """
    xc, nc = context_block(df)
    xt, nt = text_block(df, embedder)
    blocks = {
        "context": (xc, nc),
        "text": (xt, nt),
        "full": (np.hstack([xc, xt]), nc + nt),
    }
    if all(c in df.columns for c in EXT_COLS):
        xce, nce = context_ext_block(df)
        blocks["context_ext"] = (xce, nce)
        blocks["full_ext"] = (np.hstack([xce, xt]), nce + nt)
    return blocks
