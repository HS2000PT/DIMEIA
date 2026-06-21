"""Testes da similaridade do cosseno (puros, determinísticos)."""

import numpy as np
import pytest

from src.correlation_engine.similarity import (
    cosine_similarities,
    cosine_similarity,
    top_k_similar,
)


def test_vetores_identicos_dao_um():
    assert cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(1.0)


def test_vetores_ortogonais_dao_zero():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_vetores_opostos_dao_menos_um():
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)


def test_vetor_nulo_da_zero():
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_similaridades_vetorizadas():
    matrix = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    sims = cosine_similarities([1.0, 0.0], matrix)
    assert sims[0] == pytest.approx(1.0)
    assert sims[1] == pytest.approx(0.0)
    assert sims[2] == pytest.approx(1 / np.sqrt(2))


def test_top_k_ordena_por_semelhanca():
    matrix = np.array([[0.0, 1.0], [1.0, 1.0], [1.0, 0.0]])
    hits = top_k_similar([1.0, 0.0], matrix, k=2)
    # o mais semelhante a [1,0] é a linha 2 ([1,0], sim=1), depois a linha 1 ([1,1])
    assert [i for i, _ in hits] == [2, 1]
    assert hits[0][1] == pytest.approx(1.0)


def test_top_k_limita_ao_tamanho():
    matrix = np.array([[1.0, 0.0], [0.0, 1.0]])
    assert len(top_k_similar([1.0, 0.0], matrix, k=10)) == 2
    assert top_k_similar([1.0, 0.0], matrix, k=0) == []
