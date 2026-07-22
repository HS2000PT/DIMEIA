"""Testes da montagem de features estendidas (RQ4-ext) — aditivas e frozen-safe."""

from __future__ import annotations

import numpy as np
import pandas as pd

from investigator.historical_kb.embedder import HashingEmbedder
from investigator.triage.features import (
    CONTEXT_COLS,
    CONTEXT_EXT_COLS,
    EXT_COLS,
    assemble,
    context_block,
    context_ext_block,
    numeric_context_block,
)


def _df(n: int = 12, ext: bool = False, seed: int = 3) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    base = {
        "sector": rng.choice(["tech", "banking", "energy"], size=n),
        "headline": ["earnings guidance" for _ in range(n)],
        "headline_len": rng.integers(10, 80, size=n),
        "vol20": rng.normal(0.02, 0.005, n),
        "mom5": rng.normal(0, 0.01, n),
        "ret_event": rng.normal(0, 0.01, n),
        "label": rng.integers(0, 2, size=n),
    }
    if ext:
        for c in EXT_COLS:
            base[c] = rng.normal(0, 0.01, n)
    return pd.DataFrame(base)


def test_context_block_frozen_inalterado():
    """O bloco de contexto v1 tem de continuar byte-idêntico (modelos congelados dependem dele)."""
    df = _df()
    x, names = context_block(df)
    xn, namesn = numeric_context_block(df, CONTEXT_COLS)
    assert np.array_equal(x, xn) and names == namesn
    # 4 colunas numéricas + 5 setores (ordem fixa), independentemente dos setores presentes.
    assert names == CONTEXT_COLS + ["sector_banking", "sector_consumer", "sector_energy",
                                    "sector_health", "sector_tech"]
    assert x.shape == (len(df), 9)


def test_context_ext_block_inclui_as_5_features():
    df = _df(ext=True)
    x, names = context_ext_block(df)
    assert names[:len(CONTEXT_EXT_COLS)] == CONTEXT_EXT_COLS
    assert set(EXT_COLS) <= set(names)
    assert x.shape == (len(df), len(CONTEXT_EXT_COLS) + 5)  # 9 numéricas + 5 setores
    # A parte v1 é exatamente o bloco congelado (aditividade real).
    xc, _ = context_block(df)
    assert np.array_equal(x[:, :len(CONTEXT_COLS)], xc[:, :len(CONTEXT_COLS)])


def test_assemble_sem_colunas_ext_e_o_caminho_congelado():
    """Sem as colunas estendidas, assemble devolve EXATAMENTE os blocos de produção."""
    df = _df(ext=False)
    blocks = assemble(df, HashingEmbedder(dim=8))
    assert set(blocks) == {"context", "text", "full"}  # nada acrescentado


def test_assemble_com_colunas_ext_acrescenta_sem_alterar():
    df = _df(ext=True)
    emb = HashingEmbedder(dim=8)
    blocks = assemble(df, emb)
    assert {"context", "text", "full", "context_ext", "full_ext"} == set(blocks)
    # Os blocos existentes ficam byte-iguais aos do caminho congelado.
    xc, nc = context_block(df)
    assert np.array_equal(blocks["context"][0], xc) and blocks["context"][1] == nc
    # full_ext = context_ext | text (mesmas colunas de texto que full).
    xce, nce = context_ext_block(df)
    assert blocks["context_ext"][1] == nce
    assert blocks["full_ext"][0].shape[1] == xce.shape[1] + blocks["text"][0].shape[1]
