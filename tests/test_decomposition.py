"""Testes da decomposição mercado/setor/empresa — puro NumPy, sem rede."""

from __future__ import annotations

import numpy as np
import pytest

from investigator.correlation_engine.decomposition import (
    MIN_WINDOW,
    decompose_move,
    describe,
)


def _rng():
    return np.random.default_rng(7)


def test_componentes_somam_sempre_o_movimento_observado():
    """Propriedade fundamental: a repartição tem de fechar, senão a linha do alerta mente."""
    rng = _rng()
    m = rng.normal(0, 0.01, 60)
    s = 1.2 * m + rng.normal(0, 0.004, 60)
    t = 0.8 * m + 0.9 * (s - 1.2 * m) + rng.normal(0, 0.003, 60)
    d = decompose_move(t, m, s)
    assert d.market + d.sector + d.idiosyncratic == pytest.approx(d.total, abs=1e-12)


def test_ticker_que_e_o_dobro_do_mercado_da_beta_2_e_especifico_quase_nulo():
    """Caso construído: sem ruído, o ticker é exatamente 2× o mercado."""
    rng = _rng()
    m = rng.normal(0, 0.01, 60)
    t = 2.0 * m
    d = decompose_move(t, m)
    assert d.beta_market == pytest.approx(2.0, abs=1e-6)
    assert d.idiosyncratic == pytest.approx(0.0, abs=1e-9)
    assert d.driver == "market"


def test_movimento_puramente_idiossincratico_e_atribuido_a_empresa():
    """O mercado esteve parado e a ação caiu 8% — isto é da empresa, não do mercado."""
    rng = _rng()
    m = rng.normal(0, 0.001, 60)
    t = rng.normal(0, 0.001, 60)
    t[-1] = -0.08
    m[-1] = 0.0
    d = decompose_move(t, m)
    assert d.idiosyncratic == pytest.approx(-0.08, abs=5e-3)
    assert d.driver == "company"
    assert d.idiosyncratic_share > 0.9


def test_queda_de_mercado_nao_e_atribuida_a_empresa():
    """O cenário que motiva a feature: dia mau do mercado, a ação seguiu-o."""
    rng = _rng()
    m = rng.normal(0, 0.01, 60)
    t = 1.0 * m + rng.normal(0, 0.0005, 60)
    m[-1] = -0.03
    t[-1] = -0.031
    d = decompose_move(t, m)
    assert d.driver == "market"
    assert abs(d.idiosyncratic) < 0.01          # quase nada sobra para a empresa
    assert "with the whole market" in describe(d)


def test_setor_e_ortogonalizado_contra_o_mercado():
    """Sem ortogonalizar, mercado e ETF de setor são colineares e a atribuição perde sentido."""
    rng = _rng()
    m = rng.normal(0, 0.01, 80)
    setor_puro = rng.normal(0, 0.005, 80)
    s = 1.1 * m + setor_puro                    # setor = mercado + componente própria
    t = 1.0 * m + 1.5 * setor_puro + rng.normal(0, 0.0005, 80)
    d = decompose_move(t, m, s)
    assert d.beta_market == pytest.approx(1.0, abs=0.15)
    assert d.beta_sector == pytest.approx(1.5, abs=0.2)


def test_janela_curta_cai_para_beta_1_e_ASSUME_O(caplog):
    """O fallback tem de ser explícito: um beta=1 silencioso seria um número errado."""
    t = np.array([0.01, -0.02, 0.03, -0.04])
    m = np.array([0.005, -0.01, 0.02, -0.02])
    d = decompose_move(t, m)
    assert d.fallback is True
    assert d.beta_market == 1.0
    assert d.market == pytest.approx(-0.02)
    assert d.idiosyncratic == pytest.approx(-0.02)
    assert "beta 1.0" in describe(d)            # o utilizador é avisado


def test_mercado_constante_nao_rebenta():
    """Série de mercado degenerada (feriado, dados em falta) não pode levantar."""
    t = np.concatenate([np.full(30, 0.001), [-0.05]])
    m = np.zeros(31)
    d = decompose_move(t, m)
    assert d.fallback is True
    assert np.isfinite(d.idiosyncratic)


def test_beta_absurdo_e_rejeitado():
    """Janela quase sem variância no mercado produz betas explosivos — artefacto, não economia."""
    rng = _rng()
    m = np.concatenate([np.full(25, 1e-9), [0.02]])
    t = np.concatenate([rng.normal(0, 0.02, 25), [-0.05]])
    d = decompose_move(t, m)
    assert d.fallback or abs(d.beta_market) <= 4.0


def test_sem_setor_a_componente_de_setor_e_zero():
    rng = _rng()
    m = rng.normal(0, 0.01, 40)
    t = 1.1 * m + rng.normal(0, 0.002, 40)
    d = decompose_move(t, m)
    assert d.sector == 0.0
    assert d.beta_sector == 0.0


def test_series_desalinhadas_levantam():
    with pytest.raises(ValueError, match="desalinhadas"):
        decompose_move(np.zeros(10), np.zeros(9))
    with pytest.raises(ValueError, match="desalinhadas"):
        decompose_move(np.zeros(10), np.zeros(10), np.zeros(8))


def test_series_vazias_levantam():
    with pytest.raises(ValueError, match="vazias"):
        decompose_move(np.array([]), np.array([]))


def test_nao_ha_lookahead_o_dia_explicado_nao_entra_nos_betas():
    """Mudar SÓ o último dia não pode alterar os betas — senão a explicação usava o futuro."""
    rng = _rng()
    m = rng.normal(0, 0.01, 60)
    t = 1.3 * m + rng.normal(0, 0.002, 60)
    d1 = decompose_move(t, m)
    t2, m2 = t.copy(), m.copy()
    t2[-1] = -0.25                              # dia final radicalmente diferente
    d2 = decompose_move(t2, m2)
    assert d1.beta_market == pytest.approx(d2.beta_market, abs=1e-12)
    assert d1.window == d2.window


def test_window_limita_o_historico_usado():
    rng = _rng()
    m = rng.normal(0, 0.01, 200)
    t = 1.0 * m + rng.normal(0, 0.002, 200)
    assert decompose_move(t, m, window=20).window == 20
    assert decompose_move(t, m, window=MIN_WINDOW).window == MIN_WINDOW


def test_describe_nunca_preve():
    rng = _rng()
    m = rng.normal(0, 0.01, 40)
    t = 1.0 * m + rng.normal(0, 0.002, 40)
    texto = describe(decompose_move(t, m), ticker="NVDA")
    assert "NVDA" in texto and "today" in texto
    for proibido in ("will", "expect", "forecast", "predict", "should buy", "target"):
        assert proibido not in texto.lower()


# ── Correções apanhadas na validação com dados reais (2026-07-29) ─────────────
def test_driver_ignora_componentes_que_puxam_ao_contrario():
    """Bug real: NVDA +0,25% = +0,38% mercado · −1,54% setor · +1,41% empresa. A maior em
    módulo era o SETOR, mas puxou ao contrário — dizer "foi o setor" seria falso."""
    rng = _rng()
    m = rng.normal(0, 0.01, 60)
    s = 1.1 * m + rng.normal(0, 0.005, 60)
    t = 1.0 * m + 1.0 * (s - 1.1 * m) + rng.normal(0, 0.002, 60)
    d = decompose_move(t, m, s)
    # Constrói-se o caso à mão para garantir sinais opostos.
    from investigator.correlation_engine.decomposition import MoveDecomposition

    caso = MoveDecomposition(
        total=0.0025, market=0.0038, sector=-0.0154, idiosyncratic=0.0141,
        beta_market=d.beta_market, beta_sector=d.beta_sector,
        window=20, r_squared=0.3, fallback=False,
    )
    assert caso.driver == "company"        # não "sector", apesar de |−1,54%| ser o maior
    assert caso.opposed == ["sector"]
    assert "sector moved the other way" in describe(caso, "NVDA")


def test_encolhimento_nao_toca_num_beta_estimado_sem_ruido():
    """Um peso FIXO (Blume 2/3) dava β=1,67 num caso exato de 2× o mercado, atribuindo à
    empresa um movimento que é do mercado. Ponderar pela precisão preserva o β=2."""
    rng = _rng()
    m = rng.normal(0, 0.01, 60)
    d = decompose_move(2.0 * m, m)
    assert d.beta_market == pytest.approx(2.0, abs=1e-6)


def test_encolhimento_puxa_beta_ruidoso_para_o_prior():
    """Janela muito ruidosa: o beta bruto explode, e o encolhido tem de ficar mais perto de 1."""
    from investigator.correlation_engine.decomposition import _ols, _shrink

    rng = np.random.default_rng(3)
    m = rng.normal(0, 0.002, 25)
    t = rng.normal(0, 0.06, 25)          # quase todo idiossincrático
    (b_raw,), _a, se = _ols(m, t)
    b_adj = _shrink(float(b_raw), float(se[0]), 1.0)
    assert abs(b_adj - 1.0) < abs(float(b_raw) - 1.0)


def test_beta_alto_mas_bem_estimado_sobrevive():
    """Regressão do corte antigo: β=4,43 da AMD caía para o fallback e atribuía TUDO à
    empresa. Com um ajuste apertado, um beta alto é economia, não artefacto."""
    rng = _rng()
    m = rng.normal(0, 0.01, 60)
    t = 3.5 * m + rng.normal(0, 0.0005, 60)
    d = decompose_move(t, m)
    assert d.fallback is False
    assert d.beta_market > 3.0
