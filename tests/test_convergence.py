"""Testes da convergência multi-sinal.

O que interessa proteger: que a normalização viaje com os pesos (separá-las produz um score
plausível e errado), que as contribuições sejam **exatas** e não aproximadas, e que o `driver`
não aponte para um sinal que empurrou o score para BAIXO.
"""

from __future__ import annotations

import numpy as np
import pytest

from investigator.convergence import (
    SIGNALS,
    ConvergenceWeights,
    agreement_count,
    score_matrix,
    score_one,
)


def _pesos(coefs=(1.0, 1.0, 0.5, 2.0), intercept=0.0) -> ConvergenceWeights:
    return ConvergenceWeights(
        coefficients=coefs,
        intercept=intercept,
        means=(0.0, 0.0, 0.0, 0.5),
        stds=(1.0, 1.0, 1.0, 0.25),
    )


# ── Contrato dos pesos ────────────────────────────────────────────────────────
def test_pesos_rejeitam_comprimento_errado() -> None:
    with pytest.raises(ValueError, match="coefficients"):
        ConvergenceWeights(
            coefficients=(1.0, 2.0), intercept=0.0,
            means=(0.0,) * 4, stds=(1.0,) * 4,
        )


def test_persistencia_ida_e_volta() -> None:
    w = _pesos()
    volta = ConvergenceWeights.from_dict(w.to_dict())
    assert volta.names == w.names
    assert volta.coefficients == w.coefficients
    sonda = np.array([[1.0, 2.0, 3.0, 0.7]])
    assert score_matrix(sonda, volta) == pytest.approx(score_matrix(sonda, w))


# ── Pontuação ─────────────────────────────────────────────────────────────────
def test_score_esta_sempre_em_zero_um() -> None:
    w = _pesos()
    linhas = np.array([[-50.0, -50.0, -50.0, 0.0], [50.0, 50.0, 50.0, 1.0], [0.0, 0.0, 0.0, 0.5]])
    s = score_matrix(linhas, w)
    assert ((s >= 0.0) & (s <= 1.0)).all()


def test_mais_sinais_altos_produz_score_mais_alto() -> None:
    """A propriedade que dá nome ao módulo: convergência tem de valer mais do que um sinal só."""
    w = _pesos()
    so_preco = score_matrix(np.array([[3.0, 0.0, 0.0, 0.5]]), w)[0]
    dois = score_matrix(np.array([[3.0, 3.0, 0.0, 0.5]]), w)[0]
    todos = score_matrix(np.array([[3.0, 3.0, 3.0, 1.0]]), w)[0]
    assert so_preco < dois < todos


def test_score_matrix_rejeita_numero_errado_de_sinais() -> None:
    with pytest.raises(ValueError, match="esperados"):
        score_matrix(np.array([[1.0, 2.0]]), _pesos())


def test_normalizacao_viaja_com_os_pesos() -> None:
    """Aplicar pesos ajustados sobre sinais estandardizados a sinais BRUTOS dá outra coisa.

    Este teste existe para fixar que a média/desvio fazem parte do artefacto: se alguém os
    separar, o score continua a parecer razoável e passa a estar errado em silêncio.
    """
    valores = np.array([[0.0, 0.0, 0.0, 1.0]])
    centrado = _pesos()  # triage_p tem média 0,5 e desvio 0,25
    deslocado = ConvergenceWeights(
        coefficients=centrado.coefficients, intercept=centrado.intercept,
        means=(0.0, 0.0, 0.0, 0.0), stds=(1.0, 1.0, 1.0, 1.0),
    )
    assert score_matrix(valores, centrado)[0] != pytest.approx(
        score_matrix(valores, deslocado)[0]
    )


# ── Explicabilidade ───────────────────────────────────────────────────────────
def test_contribuicoes_somam_exatamente_ao_logit() -> None:
    """Exatas, não aproximadas: é linear no log-odds, logo a soma tem de fechar."""
    w = _pesos(intercept=-0.4)
    valores = {"price_z": 2.0, "volume_z": -1.0, "news_intensity": 3.0, "triage_p": 0.8}
    res = score_one(valores, w)
    logit = sum(res.contributions.values()) + w.intercept
    assert res.score == pytest.approx(1.0 / (1.0 + np.exp(-logit)))


def test_driver_ignora_sinais_que_empurraram_para_baixo() -> None:
    """O motor tem de ser um sinal que SUBIU o score.

    Mesmo erro que foi corrigido na decomposição de retornos: escolher o maior em módulo dizia
    "foi o setor" quando o setor puxava ao contrário.
    """
    w = _pesos(coefs=(1.0, 1.0, 1.0, 1.0))
    valores = {"price_z": 0.5, "volume_z": -9.0, "news_intensity": 0.0, "triage_p": 0.5}
    res = score_one(valores, w)
    assert res.contributions["volume_z"] < 0  # é o maior em MÓDULO…
    assert res.driver == "price_z"  # …mas não pode ser o motor


def test_driver_e_none_quando_nada_empurra_para_cima() -> None:
    w = _pesos(coefs=(1.0, 1.0, 1.0, 1.0))
    valores = {"price_z": -1.0, "volume_z": -1.0, "news_intensity": -1.0, "triage_p": 0.0}
    assert score_one(valores, w).driver == "none"


def test_score_one_exige_todos_os_sinais() -> None:
    with pytest.raises(ValueError, match="em falta"):
        score_one({"price_z": 1.0}, _pesos())


def test_valores_nao_finitos_nao_contaminam_o_score() -> None:
    """Um sinal em falta (NaN) tem de ficar neutro, não deitar o score inteiro a perder."""
    w = _pesos()
    res = score_one(
        {"price_z": float("nan"), "volume_z": 2.0, "news_intensity": 1.0, "triage_p": 0.6}, w
    )
    assert np.isfinite(res.score)
    assert res.contributions["price_z"] == 0.0


# ── A leitura humana ──────────────────────────────────────────────────────────
def test_agreement_count_conta_sinais_acima_do_limiar() -> None:
    valores = {"price_z": 2.5, "volume_z": 1.0, "news_intensity": 4.0, "triage_p": 0.7}
    limiares = {"price_z": 1.5, "volume_z": 2.0, "news_intensity": 3.0, "triage_p": 0.5}
    assert agreement_count(valores, limiares) == 3  # volume fica de fora


def test_agreement_count_ignora_ausentes_e_nao_finitos() -> None:
    valores = {"price_z": float("nan"), "volume_z": 5.0}
    limiares = {"price_z": 1.0, "volume_z": 2.0, "news_intensity": 1.0}
    assert agreement_count(valores, limiares) == 1


def test_ordem_dos_sinais_e_parte_do_contrato() -> None:
    assert SIGNALS == ("price_z", "volume_z", "news_intensity", "triage_p")
