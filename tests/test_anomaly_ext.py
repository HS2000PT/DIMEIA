"""Testes das extensões do CS1 (2026-07-13): LOF causal + z-score com σ EWMA.

Mesmas garantias exigidas ao Isolation Forest (test_anomaly_if.py): determinismo,
região pontuada respeitada, pico apanhado, anti-lookahead, série curta segura.
"""

from __future__ import annotations

import numpy as np

from investigator.evaluation.anomaly_eval import ewma_zscore_flags, lof_flags


def _returns_com_pico(n: int = 400, pico_em: int = 350, seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    r = rng.normal(0, 0.01, n)
    r[pico_em] = 0.12  # movimento absurdo (12%) na região de teste
    return r


# ── LOF ─────────────────────────────────────────────────────────────────────────
def test_lof_deterministico():
    r = _returns_com_pico()
    f1, s1 = lof_flags(r, window=20, train_days=250)
    f2, s2 = lof_flags(r, window=20, train_days=250)
    assert np.array_equal(f1, f2) and np.array_equal(s1, s2)


def test_lof_regiao_pontuada_e_pico_detetado():
    r = _returns_com_pico(pico_em=350)
    flags, scored = lof_flags(r, window=20, train_days=250)
    assert not scored[:270].any() and scored[270:].all()  # só pontua após janela+treino
    assert not flags[~scored].any()                       # nunca sinaliza fora da região
    assert flags[350]                                     # o pico de 12% é apanhado


def test_lof_anti_lookahead():
    r1 = _returns_com_pico()
    r2 = r1.copy()
    r2[380:] = 0.20  # futuro absurdo depois do dia 379
    f1, _ = lof_flags(r1, window=20, train_days=250)
    f2, _ = lof_flags(r2, window=20, train_days=250)
    assert np.array_equal(f1[:380], f2[:380])  # nada antes do dia 380 muda


def test_lof_serie_curta_devolve_tudo_falso():
    flags, scored = lof_flags(np.zeros(100), window=20, train_days=250)
    assert not flags.any() and not scored.any()


# ── z-score com σ EWMA ──────────────────────────────────────────────────────────
def test_ewma_calmo_nao_dispara_pico_dispara():
    rng = np.random.default_rng(7)
    calmo = rng.normal(0, 0.01, 300)
    assert not ewma_zscore_flags(calmo, threshold=6.0).any()  # limiar alto: nada em ruído
    com_pico = calmo.copy()
    com_pico[250] = 0.15
    flags = ewma_zscore_flags(com_pico, threshold=3.0)
    assert flags[250]


def test_ewma_so_sinaliza_apos_a_janela_inicial():
    r = np.zeros(60)
    r[5] = 0.5  # dentro da janela de inicialização → nunca sinalizado
    flags = ewma_zscore_flags(r, window=20)
    assert not flags[:20].any()


def test_ewma_anti_lookahead():
    r1 = _returns_com_pico()
    r2 = r1.copy()
    r2[380:] = 0.20
    f1 = ewma_zscore_flags(r1, threshold=3.0)
    f2 = ewma_zscore_flags(r2, threshold=3.0)
    assert np.array_equal(f1[:380], f2[:380])


def test_ewma_reage_mais_depressa_a_mudanca_de_regime():
    """A motivação do EWMA (λ=0.94): após um choque de volatilidade, a σ EWMA adapta-se
    mais depressa que a σ rolling de 20 dias — dispara MENOS re-alertas nos dias seguintes
    ao choque (o choque entra na norma quase de imediato)."""
    from investigator.evaluation.anomaly_eval import rolling_zscore_flags

    rng = np.random.default_rng(11)
    r = np.concatenate([rng.normal(0, 0.005, 200), rng.normal(0, 0.03, 40)])  # regime muda
    pos_choque = slice(201, 240)
    n_ewma = ewma_zscore_flags(r, threshold=3.0)[pos_choque].sum()
    n_roll = rolling_zscore_flags(r, 20, 3.0)[pos_choque].sum()
    assert n_ewma <= n_roll  # adapta-se pelo menos tão depressa
