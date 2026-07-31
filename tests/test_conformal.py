"""Testes da predição conformal split.

A propriedade que interessa não é "o código corre" — é **a garantia**: com dados
permutáveis, a cobertura empírica tem de bater no nominal. Um teste que só verificasse
formatos deixaria passar uma implementação que não garante nada.
"""

from __future__ import annotations

import numpy as np
import pytest

from investigator.triage.conformal import (
    ConformalReport,
    conformal_quantile,
    empirical_coverage,
    nonconformity,
    prediction_sets,
    run_split_conformal,
    set_sizes,
)


# ── Não-conformidade ──────────────────────────────────────────────────────────
def test_nonconformity_e_o_erro_na_classe_verdadeira() -> None:
    probs = np.array([0.9, 0.9, 0.2])
    labels = np.array([1, 0, 0])
    # y=1 com p=0.9 → 1-0.9 = 0.1 (o modelo acertou, pontuação baixa)
    # y=0 com p=0.9 → 1-0.1 = 0.9 (o modelo enganou-se, pontuação alta)
    # y=0 com p=0.2 → 1-0.8 = 0.2
    assert np.allclose(nonconformity(probs, labels), [0.1, 0.9, 0.2])


def test_nonconformity_rejeita_formatos_diferentes() -> None:
    with pytest.raises(ValueError, match="formatos diferentes"):
        nonconformity(np.array([0.5, 0.5]), np.array([1]))


# ── O quantil ─────────────────────────────────────────────────────────────────
def test_quantil_usa_a_correcao_de_amostra_finita() -> None:
    """Com n=9 e alpha=0.1, o posto é ceil(10*0.9)=9, ou seja o MAIOR ponto.

    O quantil empírico simples daria o 9.º de 9 também aqui, mas com n=19 a diferença
    aparece: ceil(20*0.9)=18 e não 17. É esse ``+1`` que dá a garantia.
    """
    scores = np.arange(1, 10, dtype=float)  # 1..9
    assert conformal_quantile(scores, 0.1) == 9.0
    scores19 = np.arange(1, 20, dtype=float)  # 1..19
    assert conformal_quantile(scores19, 0.1) == 18.0


def test_quantil_devolve_um_quando_n_e_pequeno_demais() -> None:
    """Com 5 pontos não há limiar finito que garanta 99% de cobertura.

    Devolver 1.0 (conjunto contém tudo) é honesto; devolver o máximo em silêncio seria
    prometer uma garantia que a amostra não sustenta.
    """
    assert conformal_quantile(np.array([0.1, 0.2, 0.3, 0.4, 0.5]), 0.01) == 1.0


def test_quantil_rejeita_alpha_invalido() -> None:
    for mau in (0.0, 1.0, -0.1, 1.5):
        with pytest.raises(ValueError, match="alpha"):
            conformal_quantile(np.array([0.5]), mau)


def test_quantil_rejeita_calibracao_vazia() -> None:
    with pytest.raises(ValueError, match="calibração"):
        conformal_quantile(np.array([]), 0.1)


# ── Conjuntos de predição ─────────────────────────────────────────────────────
def test_conjunto_inclui_classe_quando_a_probabilidade_chega() -> None:
    # qhat=0.3 → uma classe entra se p(classe) >= 0.7
    sets = prediction_sets(np.array([0.95, 0.5, 0.05]), qhat=0.3)
    assert list(sets[0]) == [False, True]  # só a classe 1
    assert list(sets[1]) == [False, False]  # nenhuma chega a 0.7 → vazio
    assert list(sets[2]) == [True, False]  # só a classe 0


def test_qhat_alto_produz_conjuntos_com_as_duas_classes() -> None:
    """qhat=1.0 é o caso degenerado: tudo entra, cobertura trivialmente 1."""
    sets = prediction_sets(np.array([0.9, 0.1, 0.5]), qhat=1.0)
    assert (set_sizes(sets) == 2).all()


def test_set_sizes_conta_zero_um_e_dois() -> None:
    sets = np.array([[False, False], [True, False], [True, True]])
    assert list(set_sizes(sets)) == [0, 1, 2]


# ── Cobertura ─────────────────────────────────────────────────────────────────
def test_cobertura_conta_a_classe_verdadeira() -> None:
    sets = np.array([[False, True], [True, False], [False, True]])
    # verdades 1, 0, 0 → coberto, coberto, NÃO coberto
    assert empirical_coverage(sets, np.array([1, 0, 0])) == pytest.approx(2 / 3)


def test_cobertura_rejeita_desalinhamento() -> None:
    with pytest.raises(ValueError, match="conjuntos"):
        empirical_coverage(np.array([[True, False]]), np.array([0, 1]))


# ── A garantia, que é o ponto de tudo isto ────────────────────────────────────
def _coberturas_repetidas(alpha: float, *, inutil: bool = False, reps: int = 60):
    """Cobertura sobre muitas divisões independentes.

    A garantia conformal é **marginal**: vale em média sobre a aleatoriedade do conjunto de
    calibração, não em toda e qualquer divisão isolada. Exigir cobertura numa única divisão é
    exigir mais do que o teorema promete — e foi exatamente o que aconteceu ao escrever isto
    pela primeira vez: com α=0,2 e uma semente fixa, a cobertura caiu em 0,780 contra 0,800
    nominal (2,2 erros-padrão abaixo, ~1% de probabilidade) e o teste acusou uma avaria que
    não existia. A média sobre repetições testa a propriedade que de facto é garantida.
    """
    n = 2000
    saidas = []
    for semente in range(reps):
        rng = np.random.default_rng(semente)
        if inutil:
            labels = rng.integers(0, 2, size=n)
            probs = rng.uniform(size=n)  # ruído puro, sem relação com a verdade
        else:
            latente = rng.normal(size=n)
            labels = (latente + rng.normal(scale=1.5, size=n) > 0).astype(int)
            # Informativo, longe de perfeito: a garantia não pode depender de o modelo ser bom.
            probs = 1.0 / (1.0 + np.exp(-0.8 * latente))
        meio = n // 2
        saidas.append(
            run_split_conformal(
                probs[:meio], labels[:meio], probs[meio:], labels[meio:], alpha
            )
        )
    return saidas


@pytest.mark.parametrize("alpha", [0.05, 0.1, 0.2])
def test_a_garantia_de_cobertura_verifica_se_em_dados_permutaveis(alpha: float) -> None:
    """A propriedade central: sob permutabilidade, a cobertura MÉDIA atinge 1−α."""
    relatorios = _coberturas_repetidas(alpha)
    media = float(np.mean([r.coverage for r in relatorios]))
    assert media >= (1.0 - alpha) - 0.005, (
        f"cobertura média {media:.4f} abaixo do nominal {1 - alpha:.2f}"
    )


def test_a_garantia_aguenta_um_modelo_completamente_inutil() -> None:
    """Probabilidades aleatórias, sem relação nenhuma com a verdade.

    A cobertura tem de continuar a atingir o nominal — só que paga em conjuntos maiores. É
    exatamente esta a troca que a predição conformal faz, e vale a pena tê-la fixada: um
    modelo mau não quebra a garantia, fica é inútil de forma **visível**.
    """
    relatorios = _coberturas_repetidas(0.1, inutil=True)
    media = float(np.mean([r.coverage for r in relatorios]))
    tamanho = float(np.mean([r.avg_set_size for r in relatorios]))
    assert media >= 0.9 - 0.005, f"cobertura média {media:.4f}"
    assert tamanho > 1.5, "um modelo inútil devia pagar em conjuntos grandes"


def test_um_modelo_bom_paga_menos_que_um_inutil() -> None:
    """A eficiência é o que distingue os dois: ambos cobrem, um usa conjuntos mais pequenos."""
    bom = float(np.mean([r.avg_set_size for r in _coberturas_repetidas(0.1)]))
    inutil = float(np.mean([r.avg_set_size for r in _coberturas_repetidas(0.1, inutil=True)]))
    assert bom < inutil


def test_conjuntos_encolhem_quando_alpha_cresce() -> None:
    """Menos exigência de cobertura → conjuntos mais pequenos. A troca, verificada."""
    rng = np.random.default_rng(3)
    n = 3000
    latente = rng.normal(size=n)
    labels = (latente + rng.normal(scale=1.0, size=n) > 0).astype(int)
    probs = 1.0 / (1.0 + np.exp(-1.5 * latente))
    meio = n // 2
    tamanhos = [
        run_split_conformal(
            probs[:meio], labels[:meio], probs[meio:], labels[meio:], a
        ).avg_set_size
        for a in (0.05, 0.2, 0.4)
    ]
    assert tamanhos[0] >= tamanhos[1] >= tamanhos[2]


# ── O relatório ───────────────────────────────────────────────────────────────
def test_relatorio_expoe_nominal_e_veredicto() -> None:
    rel = ConformalReport(
        alpha=0.1, qhat=0.5, coverage=0.91, avg_set_size=1.2,
        frac_singleton=0.8, frac_both=0.2, frac_empty=0.0, n_cal=1000, n_eval=1000,
    )
    assert rel.nominal == pytest.approx(0.9)
    assert rel.covers


def test_relatorio_deteta_cobertura_em_falta() -> None:
    """Uma cobertura muito abaixo do nominal tem de ser sinalizada, não arredondada."""
    rel = ConformalReport(
        alpha=0.1, qhat=0.5, coverage=0.70, avg_set_size=1.0,
        frac_singleton=1.0, frac_both=0.0, frac_empty=0.0, n_cal=1000, n_eval=1000,
    )
    assert not rel.covers
