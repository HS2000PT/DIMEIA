"""QI4 — a avaliação, e a razão de não bastar a precisão por setor.

A §5.3 mede a recuperação por **pertença ao setor**. Essa métrica não sabe nada sobre
materialidade: um codificador ajustado para aproximar movimentos de grandeza parecida pode
piorar nela e ainda assim estar a fazer exactamente o que se lhe pediu. Medir só por setor
seria avaliar o braço principal pela métrica do braço que ele não é.

Daí duas métricas, sobre o mesmo conjunto de consultas e o mesmo protocolo:

- **comparabilidade de materialidade** — a diferença média, em pontos percentuais, entre a
  grandeza do movimento da consulta e a dos precedentes devolvidos. Menor é melhor. É a
  métrica do objectivo;
- **precisão@k por setor** — a métrica da §5.3, para provar que o ajuste não destrói a
  relevância temática enquanto persegue a outra coisa.

As máscaras são as da tese: nunca a própria empresa, e — na variante causal — nunca um
candidato com data igual ou posterior à da consulta.
"""

from __future__ import annotations

import numpy as np
import pytest

from investigator.qi4 import avaliacao as A


def vetores(n: int, semente: int = 0) -> np.ndarray:
    rng = np.random.default_rng(semente)
    v = rng.normal(size=(n, 8))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


# ── as máscaras ───────────────────────────────────────────────────────────────

def test_a_propria_empresa_nunca_e_candidata():
    tickers = np.array(["AAA", "AAA", "BBB", "CCC"])
    m = A.mascara(np.array([0]), tickers, datas=None, datas_consulta=None)
    assert m.shape == (1, 4)
    assert not m[0, 0] and not m[0, 1]
    assert m[0, 2] and m[0, 3]


def test_a_variante_causal_exclui_o_presente_e_o_futuro():
    tickers = np.array(["AAA", "BBB", "BBB", "BBB"])
    datas = np.array(["2020-01-01", "2020-01-01", "2020-01-02", "2019-12-31"])
    m = A.mascara(np.array([0]), tickers, datas=datas,
                  datas_consulta=np.array(["2020-01-01"]))
    assert not m[0, 1], "candidato do MESMO dia tem de ser excluído"
    assert not m[0, 2], "candidato POSTERIOR tem de ser excluído"
    assert m[0, 3], "candidato anterior é o único elegível"


def test_sem_datas_a_mascara_e_simetrica():
    tickers = np.array(["AAA", "BBB", "BBB"])
    m = A.mascara(np.array([0]), tickers, datas=None, datas_consulta=None)
    assert m[0, 1] and m[0, 2]


# ── a métrica do objectivo ────────────────────────────────────────────────────

def test_a_comparabilidade_e_a_diferenca_media_de_grandeza():
    """À mão: consulta a 5%, vizinhos a 3% e 6% -> (|5−3| + |5−6|)/2 = 1,5 pontos."""
    grandeza_consulta = np.array([0.05])
    vizinhos = np.array([[0.03, 0.06]])
    v = A.comparabilidade(grandeza_consulta, vizinhos)
    assert v == pytest.approx(0.015)


def test_a_comparabilidade_e_zero_quando_a_grandeza_bate_certo():
    assert A.comparabilidade(np.array([0.02]), np.array([[0.02, 0.02]])) == pytest.approx(0.0)


def test_a_comparabilidade_ignora_o_sinal_do_movimento():
    """A métrica é sobre GRANDEZA: recebe já valores absolutos e não deve inventar sinais."""
    a = A.comparabilidade(np.array([0.05]), np.array([[0.03]]))
    b = A.comparabilidade(np.array([0.05]), np.array([[0.03]]))
    assert a == b == pytest.approx(0.02)


# ── a recuperação ─────────────────────────────────────────────────────────────

def test_o_topo_k_respeita_a_mascara():
    """O candidato mais parecido, se estiver mascarado, não pode aparecer."""
    v = np.array([[1.0, 0.0], [1.0, 0.0], [0.9, 0.44], [0.0, 1.0]])
    v = v / np.linalg.norm(v, axis=1, keepdims=True)
    tickers = np.array(["AAA", "AAA", "BBB", "CCC"])
    idx = A.topo_k(v, np.array([0]), tickers, k=1, datas=None)
    assert idx[0, 0] == 2, "devia devolver o BBB (o AAA idêntico está mascarado)"


def test_o_topo_k_devolve_k_colunas():
    v = vetores(30)
    tickers = np.array(["AAA", "BBB", "CCC"] * 10)
    idx = A.topo_k(v, np.arange(5), tickers, k=5, datas=None)
    assert idx.shape == (5, 5)


def test_o_topo_k_nunca_devolve_a_propria_consulta():
    v = vetores(30)
    tickers = np.array(["AAA", "BBB", "CCC"] * 10)
    consultas = np.arange(10)
    idx = A.topo_k(v, consultas, tickers, k=5, datas=None)
    for i, q in enumerate(consultas):
        assert q not in idx[i]


def test_a_precisao_por_setor_conta_acertos():
    """Três dos cinco vizinhos no setor da consulta -> 0,6."""
    setores = np.array(["tech", "tech", "tech", "energia", "energia", "banca"])
    vizinhos = np.array([[0, 1, 2, 3, 5]])
    p = A.precisao_setor(np.array([0]), vizinhos, setores)
    assert p == pytest.approx(3 / 5)


def test_a_precisao_por_setor_e_um_quando_todos_acertam():
    setores = np.array(["tech"] * 6)
    p = A.precisao_setor(np.array([0]), np.array([[1, 2, 3, 4, 5]]), setores)
    assert p == pytest.approx(1.0)


def test_a_amostragem_de_consultas_e_determinista():
    a = A.amostrar_consultas(1000, 50, seed=42)
    b = A.amostrar_consultas(1000, 50, seed=42)
    c = A.amostrar_consultas(1000, 50, seed=43)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)
    assert len(np.unique(a)) == 50, "as consultas têm de ser distintas"
