"""A porta que teria apanhado o desastre da primeira tentativa da QI4.

Os valores reais medidos a 2026-09-09 estão nos testes, para que a porta seja calibrada contra
o que aconteceu de facto e não contra um número inventado:

- `all-MiniLM-L6-v2` sem ajuste, sobre 1500 manchetes do bloco de teste:
  cosseno médio entre manchetes diferentes **0,2234**, norma do vetor médio **0,4732**;
- os dois braços colapsados: cosseno **0,9929** e **0,9912**, norma **0,9964** e **0,9956**.
"""

from __future__ import annotations

import numpy as np
import pytest

from investigator.qi4 import colapso as C


def normalizar(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def saudavel(n: int = 200, d: int = 16, semente: int = 0) -> np.ndarray:
    return normalizar(np.random.default_rng(semente).normal(size=(n, d)))


def colapsado(n: int = 200, d: int = 16, ruido: float = 0.02,
              semente: int = 0) -> np.ndarray:
    rng = np.random.default_rng(semente)
    base = rng.normal(size=(1, d))
    return normalizar(np.repeat(base, n, axis=0) + rng.normal(scale=ruido, size=(n, d)))


def test_vetores_saudaveis_nao_sao_dados_como_colapsados():
    p = C.perfil(saudavel())
    assert not p["colapsou"]
    assert p["cosseno_medio"] < 0.2
    assert p["norma_do_vetor_medio"] < 0.3


def test_vetores_colapsados_sao_apanhados():
    p = C.perfil(colapsado())
    assert p["colapsou"]
    assert p["cosseno_medio"] > 0.99
    assert p["norma_do_vetor_medio"] > 0.99


def test_o_limiar_deixa_passar_o_modelo_da_tese_e_barra_o_colapsado():
    """Calibração contra os valores medidos, não contra um palpite."""
    assert 0.2234 < C.LIMIAR_COLAPSO, "o SBERT da tese teria sido dado como colapsado"
    assert 0.9912 > C.LIMIAR_COLAPSO, "o braço colapsado teria passado"


def test_o_perfil_recusa_um_unico_vetor():
    with pytest.raises(ValueError):
        C.perfil(saudavel(1))


def test_comparar_deteta_que_nada_mudou():
    v = saudavel()
    c = C.comparar(v, v)
    assert c["cosseno_medio_base_ajustado"] == pytest.approx(1.0)
    assert c["correlacao_das_geometrias"] == pytest.approx(1.0)


def test_comparar_deteta_geometria_destruida():
    a, b = saudavel(semente=1), saudavel(semente=2)
    c = C.comparar(a, b)
    assert abs(c["cosseno_medio_base_ajustado"]) < 0.2
    assert abs(c["correlacao_das_geometrias"]) < 0.2


def test_comparar_recusa_formas_diferentes():
    with pytest.raises(ValueError, match="formas"):
        C.comparar(saudavel(10), saudavel(20))
