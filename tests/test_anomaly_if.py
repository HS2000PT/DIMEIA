"""Testes do Isolation Forest causal (M4): determinismo, região pontuada, anti-lookahead."""

from __future__ import annotations

import numpy as np

from src.evaluation.anomaly_eval import isolation_forest_flags


def _returns_com_pico(n: int = 400, pico_em: int = 350, seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    r = rng.normal(0, 0.01, n)
    r[pico_em] = 0.12  # movimento absurdo (12%) na região de teste
    return r


def test_deterministico_com_a_mesma_seed():
    r = _returns_com_pico()
    f1, s1 = isolation_forest_flags(r, window=20, train_days=250, seed=42)
    f2, s2 = isolation_forest_flags(r, window=20, train_days=250, seed=42)
    assert np.array_equal(f1, f2) and np.array_equal(s1, s2)


def test_regiao_pontuada_e_pico_detetado():
    r = _returns_com_pico(pico_em=350)
    flags, scored = isolation_forest_flags(r, window=20, train_days=250)
    assert not scored[:270].any() and scored[270:].all()  # só pontua após janela+treino
    assert not flags[~scored].any()                       # nunca sinaliza fora da região
    assert flags[350]                                     # o pico de 12% é apanhado


def test_anti_lookahead_mutar_o_futuro_nao_muda_o_passado():
    r1 = _returns_com_pico()
    r2 = r1.copy()
    r2[380:] = 0.20  # futuro absurdo depois do dia 379
    f1, _ = isolation_forest_flags(r1, window=20, train_days=250, seed=42)
    f2, _ = isolation_forest_flags(r2, window=20, train_days=250, seed=42)
    assert np.array_equal(f1[:380], f2[:380])  # nada antes do dia 380 muda


def test_serie_curta_devolve_tudo_falso():
    flags, scored = isolation_forest_flags(np.zeros(100), window=20, train_days=250)
    assert not flags.any() and not scored.any()
