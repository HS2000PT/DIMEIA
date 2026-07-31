"""Testes da deteção de deriva.

O que tem de ser protegido: que uma distribuição **igual** dê deriva ~0, que uma distribuição
**deslocada** dê deriva alta, e que os casos degenerados (intervalos vazios, feature constante)
não produzam `inf` nem exceções — porque é aí que uma métrica de deriva costuma partir-se em
silêncio e passar a reportar números sem sentido.
"""

from __future__ import annotations

import numpy as np
import pytest

from investigator.evaluation.drift import (
    PSI_MODERATE,
    PSI_STABLE,
    compare_distributions,
    ks_statistic,
    population_stability_index,
    psi_band,
)


# ── PSI ───────────────────────────────────────────────────────────────────────
def test_psi_e_praticamente_zero_para_a_mesma_distribuicao() -> None:
    rng = np.random.default_rng(0)
    a = rng.normal(size=20_000)
    b = rng.normal(size=20_000)
    assert population_stability_index(a, b) < PSI_STABLE


def test_psi_cresce_com_o_tamanho_da_deslocacao() -> None:
    rng = np.random.default_rng(1)
    ref = rng.normal(size=20_000)
    pequena = population_stability_index(ref, rng.normal(loc=0.2, size=20_000))
    grande = population_stability_index(ref, rng.normal(loc=1.5, size=20_000))
    assert pequena < grande
    assert grande > PSI_MODERATE


def test_psi_nao_explode_quando_a_amostra_atual_nao_visita_intervalos() -> None:
    """Uma amostra atual concentrada num canto deixa intervalos vazios.

    Sem o epsilon isto daria ``inf`` e apagaria todo o restante sinal do relatório.
    """
    rng = np.random.default_rng(2)
    ref = rng.normal(size=5_000)
    cur = rng.normal(loc=10.0, scale=0.01, size=500)  # completamente noutro sítio
    psi = population_stability_index(ref, cur)
    assert np.isfinite(psi)
    assert psi > PSI_MODERATE


def test_psi_lida_com_feature_constante_na_referencia() -> None:
    psi = population_stability_index(np.full(1000, 3.0), np.full(1000, 3.0))
    assert np.isfinite(psi)


def test_psi_e_nan_sem_dados() -> None:
    assert np.isnan(population_stability_index(np.array([]), np.array([1.0, 2.0])))


def test_psi_ignora_nao_finitos() -> None:
    rng = np.random.default_rng(3)
    limpo = rng.normal(size=5_000)
    sujo = np.concatenate([rng.normal(size=5_000), [np.nan, np.inf, -np.inf]])
    assert np.isfinite(population_stability_index(limpo, sujo))


def test_bandas_do_psi() -> None:
    assert psi_band(0.05) == "estável"
    assert psi_band(0.15) == "moderada"
    assert psi_band(0.40) == "significativa"
    assert psi_band(float("nan")) == "n/a"


# ── KS ────────────────────────────────────────────────────────────────────────
def test_ks_d_e_pequeno_para_a_mesma_distribuicao() -> None:
    rng = np.random.default_rng(4)
    d, _ = ks_statistic(rng.normal(size=10_000), rng.normal(size=10_000))
    assert d < 0.05


def test_ks_d_e_grande_para_distribuicoes_separadas() -> None:
    rng = np.random.default_rng(5)
    d, _ = ks_statistic(rng.normal(size=5_000), rng.normal(loc=3.0, size=5_000))
    assert d > 0.8


def test_ks_d_esta_sempre_em_zero_um() -> None:
    rng = np.random.default_rng(6)
    for loc in (0.0, 0.5, 5.0):
        d, _ = ks_statistic(rng.normal(size=2_000), rng.normal(loc=loc, size=2_000))
        assert 0.0 <= d <= 1.0


# ── A comparação completa ─────────────────────────────────────────────────────
def test_compare_ordena_pela_deriva_mais_grave() -> None:
    rng = np.random.default_rng(8)
    ref = {"estavel": rng.normal(size=8_000), "derivada": rng.normal(size=8_000)}
    cur = {"estavel": rng.normal(size=8_000), "derivada": rng.normal(loc=2.0, size=8_000)}
    saida = compare_distributions(ref, cur)
    assert saida[0].name == "derivada"
    assert saida[0].band == "significativa"
    assert saida[1].band == "estável"


def test_compare_rejeita_features_desemparelhadas() -> None:
    with pytest.raises(ValueError, match="desemparelhadas"):
        compare_distributions({"a": np.zeros(10)}, {"b": np.zeros(10)})


def test_deslocacao_da_media_e_em_desvios_padrao_da_referencia() -> None:
    """Comparável entre features com unidades diferentes — é esse o ponto."""
    rng = np.random.default_rng(9)
    ref = {"x": rng.normal(loc=0.0, scale=2.0, size=20_000)}
    cur = {"x": rng.normal(loc=2.0, scale=2.0, size=20_000)}
    (f,) = compare_distributions(ref, cur)
    assert f.mean_shift_sd == pytest.approx(1.0, abs=0.05)


def test_deslocacao_e_nan_com_referencia_constante() -> None:
    ref = {"x": np.full(1_000, 5.0)}
    cur = {"x": np.full(1_000, 7.0)}
    (f,) = compare_distributions(ref, cur)
    assert np.isnan(f.mean_shift_sd)
