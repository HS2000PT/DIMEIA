"""Testes da taxonomia de tipos de evento.

Duas coisas a proteger, e são diferentes: a **rubrica** (referência de alta precisão, que
tem de calar-se quando não sabe) e a **taxonomia aprendida** (centróides + atribuição, que
tem de ser aritmética honesta).
"""

from __future__ import annotations

import numpy as np
import pytest

from investigator.historical_kb.taxonomy import (
    EVENT_TYPES,
    EventTaxonomy,
    l2_normalise,
    majority_labels,
    purity,
    rubric_label,
    rubric_labels,
)


# ── A rubrica ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    ("headline", "expected"),
    [
        ("Apple Reports Q1 2019 Earnings Per Share Of $4.18", "earnings"),
        ("Nvidia Raises FY Guidance After Strong Demand", "guidance"),
        ("Goldman Downgrades Tesla To Sell, Price Target Cut", "analyst"),
        ("Microsoft Unveils New Surface Laptop", "product"),
        ("FTC Opens Antitrust Probe Into Amazon", "legal_regulatory"),
        ("Salesforce Agrees To Buy Slack In $27B Deal", "ma"),
        ("Intel Names New CEO After Chairman Steps Down", "personnel"),
        ("Close Update: Wall Street Rally As Treasury Yields Fall", "macro_market"),
    ],
)
def test_rubrica_apanha_cada_tipo(headline: str, expected: str) -> None:
    assert rubric_label(headline) == expected


def test_rubrica_cala_se_quando_ambigua() -> None:
    """Resultados **e** ação de analista na mesma manchete é genuinamente ambíguo.

    Uma referência que resolvesse isto pela ordem da lista estaria a inventar precisão.
    """
    ambigua = "Apple Q1 Earnings Beat; Morgan Stanley Raises Price Target"
    assert rubric_label(ambigua) is None


@pytest.mark.parametrize(
    "ruido",
    [
        "PreMarket Opening NYSE Imbalance Update: Bank Of America 157k Shares To Buy",
        "PreMarket Opening General Electric 148k Shares To Sell; Bank Of America 113k To Buy",
        "5 Blue-Chip Stocks to Buy in January",
        "7 Cheap Stocks To Buy Right Now",
    ],
)
def test_rubrica_nao_confunde_ordens_e_listas_com_aquisicoes(ruido: str) -> None:
    """Regressão: um ``to buy`` nu apanhava 89% do balde ``ma`` com lixo.

    O corpus está cheio de desequilíbrios de ordens ("157k Shares To Buy") e de listas de
    sugestões ("5 Stocks to Buy"). Nenhuma delas é uma aquisição. Com o padrão antigo, ``ma``
    era o maior balde da referência e 5.032 dos seus 5.657 matches eram ruído — o que teria
    corrompido em silêncio todos os números de pureza a jusante.
    """
    assert rubric_label(ruido) != "ma"


def test_rubrica_continua_a_apanhar_aquisicoes_genuinas() -> None:
    """O outro lado da mesma correção: apertar não pode cegar."""
    assert rubric_label("Salesforce Agrees To Buy Slack In $27B Deal") == "ma"
    assert rubric_label("Shell Buys Stake in Silicon Ranch") == "ma"
    assert rubric_label("ExxonMobil to Divest Terra Nova Project") == "ma"
    assert rubric_label("Biogen to Acquire a Phase 2b Ready Asset from Pfizer") == "ma"


def test_rubrica_cala_se_quando_nao_reconhece() -> None:
    assert rubric_label("Benzinga's Bulls And Bears Of The Week") is None
    assert rubric_label("") is None


def test_rubrica_e_insensivel_a_maiusculas() -> None:
    assert rubric_label("intel names new ceo") == "personnel"
    assert rubric_label("INTEL NAMES NEW CEO") == "personnel"


def test_rubrica_so_devolve_tipos_da_taxonomia() -> None:
    amostra = [
        "Apple Reports Q1 Earnings",
        "Fed Holds Interest Rates Steady",
        "algo completamente diferente",
    ]
    for rotulo in rubric_labels(amostra):
        assert rotulo is None or rotulo in EVENT_TYPES


# ── Álgebra ───────────────────────────────────────────────────────────────────
def test_l2_normalise_produz_normas_unitarias() -> None:
    saida = l2_normalise(np.array([[3.0, 4.0], [1.0, 0.0]]))
    assert np.allclose(np.linalg.norm(saida, axis=1), 1.0)


def test_l2_normalise_nao_produz_nan_em_linha_nula() -> None:
    """Um vetor nulo não tem direção; propagar NaN partiria o agrupamento em silêncio."""
    saida = l2_normalise(np.array([[0.0, 0.0], [3.0, 4.0]]))
    assert not np.isnan(saida).any()
    assert np.allclose(saida[0], 0.0)


def test_l2_normalise_rejeita_dimensao_errada() -> None:
    with pytest.raises(ValueError, match="2-D"):
        l2_normalise(np.array([1.0, 2.0, 3.0]))


# ── A taxonomia aprendida ─────────────────────────────────────────────────────
def _taxonomia_brinquedo() -> EventTaxonomy:
    centroides = l2_normalise(np.array([[1.0, 0.0], [0.0, 1.0]]))
    return EventTaxonomy(centroids=centroides, labels=("earnings", "analyst"))


def test_assign_escolhe_o_centroide_mais_proximo() -> None:
    tax = _taxonomia_brinquedo()
    assert list(tax.assign(np.array([[0.9, 0.1], [0.1, 0.9]]))) == [0, 1]


def test_label_of_devolve_nomes() -> None:
    tax = _taxonomia_brinquedo()
    assert tax.label_of(np.array([[5.0, 0.0]])) == ["earnings"]


def test_confidence_e_o_cosseno_ao_centroide_atribuido() -> None:
    tax = _taxonomia_brinquedo()
    # Exatamente em cima do primeiro centróide → cosseno 1.
    assert tax.confidence(np.array([[2.0, 0.0]]))[0] == pytest.approx(1.0)
    # A 45° dos dois → cosseno 1/sqrt(2) para o vencedor.
    assert tax.confidence(np.array([[1.0, 1.0]]))[0] == pytest.approx(2**-0.5)


def test_assign_rejeita_dimensao_incompativel() -> None:
    tax = _taxonomia_brinquedo()
    with pytest.raises(ValueError, match="dimensão"):
        tax.assign(np.array([[1.0, 2.0, 3.0]]))


def test_rotulos_fora_da_taxonomia_sao_rejeitados() -> None:
    with pytest.raises(ValueError, match="fora da taxonomia"):
        EventTaxonomy(centroids=np.eye(2), labels=("earnings", "inventado"))


def test_contagem_de_rotulos_tem_de_bater_com_centroides() -> None:
    with pytest.raises(ValueError, match="centróides"):
        EventTaxonomy(centroids=np.eye(3), labels=("earnings", "analyst"))


def test_persistencia_ida_e_volta(tmp_path) -> None:
    tax = _taxonomia_brinquedo()
    destino = tmp_path / "tax.json"
    tax.save(destino)
    recarregada = EventTaxonomy.load(destino)
    assert recarregada.labels == tax.labels
    assert np.allclose(recarregada.centroids, tax.centroids)
    # E continua a atribuir da mesma maneira, que é o que de facto interessa.
    sonda = np.array([[0.8, 0.2], [0.2, 0.8]])
    assert list(recarregada.assign(sonda)) == list(tax.assign(sonda))


# ── Métricas ──────────────────────────────────────────────────────────────────
def test_purity_ignora_referencias_ausentes() -> None:
    pureza, n = purity([0, 0, 1, 1], ["earnings", None, "analyst", "analyst"])
    assert n == 3  # o None não conta
    assert pureza == pytest.approx(1.0)


def test_purity_conta_a_maioria_nao_a_perfeicao() -> None:
    # Grupo 0: 2 earnings + 1 analyst → maioria acerta 2 em 3.
    pureza, n = purity([0, 0, 0], ["earnings", "earnings", "analyst"])
    assert n == 3
    assert pureza == pytest.approx(2 / 3)


def test_purity_sem_referencia_nenhuma_devolve_zero() -> None:
    assert purity([0, 1], [None, None]) == (0.0, 0)


def test_majority_labels_usa_fallback_em_grupo_sem_referencia() -> None:
    rotulos = majority_labels([0, 0], ["earnings", "earnings"], n_clusters=2)
    assert rotulos[0] == "earnings"
    assert rotulos[1] == "macro_market"  # grupo 1 nunca foi tocado pela rubrica
