"""O instrumento que a avaliacao de 17/09 vai usar, testado ANTES de haver dados.

Um script que so' e' exercitado no dia em que os dados chegam e' um script que se descobre
partido no pior momento. Estes testes verificam as quatro regras que o protocolo impoe, e
sobretudo que ele PRODUZ numeros quando o bloco e' suficiente -- porque hoje ele recusa, e uma
recusa e' indistinguivel de uma avaria.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import numpy as np
import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "ranking_prod", RAIZ / "scripts" / "evaluate_ranking_producao.py")
rp = importlib.util.module_from_spec(_spec)
sys.modules["ranking_prod"] = rp
_spec.loader.exec_module(rp)


def _linha(ticker, data, as_of, prob, vol, headline="h"):
    return {"news_date": data, "ticker": ticker, "headline": headline, "prob": prob,
            "feature_snapshot": {"as_of": as_of, "values": {"vol20": vol}}}


def test_regra_da_treinabilidade_exclui_barra_posterior():
    """as_of DEPOIS da noticia descreve um mercado que ja viu o desfecho."""
    linhas = [
        _linha("NVDA", "2026-09-01", "2026-08-31", 0.4, 0.02, "antes"),
        _linha("NVDA", "2026-09-01", "2026-09-01", 0.4, 0.02, "igual"),
        _linha("NVDA", "2026-09-01", "2026-09-05", 0.4, 0.02, "depois"),
    ]
    ok = {d["headline"] for d in rp.utilizaveis(linhas)}
    assert ok == {"antes", "igual"}


def test_deduplica_o_mesmo_titulo():
    """O varrimento repontua de 60 em 60 s; o peso de uma empresa nao pode ser isso."""
    linhas = [_linha("NVDA", "2026-09-01", "2026-08-31", 0.4, 0.02) for _ in range(7)]
    assert len(rp.utilizaveis(linhas)) == 1


def test_linha_sem_snapshot_ou_sem_prob_nao_entra():
    sem_snap = {"news_date": "2026-09-01", "ticker": "NVDA", "headline": "x", "prob": 0.4}
    sem_prob = _linha("NVDA", "2026-09-01", "2026-08-31", None, 0.02)
    assert rp.utilizaveis([sem_snap, sem_prob]) == []


def _clusters_sinteticos(n_clusters, sinal):
    """n clusters (empresa, dia), duas decisoes cada, com o rotulo ligado ao sinal ou nao."""
    rng = np.random.default_rng(7)
    clusters = {}
    for i in range(n_clusters):
        y = int(rng.random() < 0.4)
        chave = ("T" + str(i % 12), "2026-07-" + str(i % 28 + 1).zfill(2))
        if chave in clusters:
            continue
        entradas = []
        for _ in range(2):
            p = (0.3 + 0.4 * y + rng.normal(0, 0.05)) if sinal else rng.random()
            entradas.append({"label": y, "prob": float(p), "vol": float(rng.random())})
        clusters[chave] = entradas
    return clusters


def test_bootstrap_distingue_sinal_de_acaso():
    """Se o instrumento nao vir sinal quando ele existe, nao serve para 17/09."""
    rng = np.random.default_rng(1)
    com = _clusters_sinteticos(120, sinal=True)
    sem = _clusters_sinteticos(120, sinal=False)
    v_com = rp.bootstrap(com, sorted(com), rp.auc, "prob", rng)
    v_sem = rp.bootstrap(sem, sorted(sem), rp.auc, "prob", rng)
    assert v_com[0] > 0.85, "nao viu um sinal forte: " + str(v_com[0])
    assert v_com[1] > 0.5, "o intervalo do sinal devia estar acima do acaso"
    assert v_sem[1] < 0.5 < v_sem[2], "sem sinal, o intervalo tem de conter o acaso"


def test_auc_e_pr_auc_em_casos_conhecidos():
    """Controlos onde a resposta se sabe de cor."""
    y = np.array([0, 0, 1, 1])
    assert rp.auc(y, np.array([0.1, 0.2, 0.8, 0.9])) == pytest.approx(1.0)
    assert rp.auc(y, np.array([0.9, 0.8, 0.2, 0.1])) == pytest.approx(0.0)
    assert rp.pr_auc(y, np.array([0.1, 0.2, 0.8, 0.9])) == pytest.approx(1.0)


def test_recusa_abaixo_do_minimo_e_nao_publica_metrica(tmp_path, monkeypatch):
    """A recusa e' o mecanismo que impede alguem de citar um numero cedo demais."""
    saida = tmp_path / "r.md"
    monkeypatch.setattr(rp, "SAIDA", saida)
    rp.escreve_insuficiente(33, 80, 574, 41477)
    texto = saida.read_text(encoding="utf-8")
    assert "Bloco insuficiente" in texto
    assert "33" in texto and "80" in texto
    for proibido in ("ROC-AUC", "PR-AUC", "IC 95%"):
        assert proibido not in texto, "publicou " + proibido + " abaixo do minimo"


def test_projecao_avisa_quando_a_recolha_nao_chega(tmp_path, monkeypatch):
    """O controlo no sentido oposto: um minimo que so se descobre inalcancavel na vespera
    nao serve de minimo."""
    saida = tmp_path / "r.md"
    monkeypatch.setattr(rp, "SAIDA", saida)
    hoje = __import__("datetime").date.today()
    prazo = (hoje + __import__("datetime").timedelta(days=7)).isoformat()
    # ritmo de 1 par por dia contra um minimo de 500: nao chega de forma nenhuma
    rp.escreve_insuficiente(3, 500, 9, 100,
                            por_dia={"2026-09-0" + str(i): {"T"} for i in (1, 2, 3)},
                            prazo=prazo)
    texto = saida.read_text(encoding="utf-8")
    assert "não chega ao mínimo a tempo" in texto
    assert "ROC-AUC" not in texto


def test_projecao_diz_no_caminho_certo_quando_chega(tmp_path, monkeypatch):
    saida = tmp_path / "r.md"
    monkeypatch.setattr(rp, "SAIDA", saida)
    hoje = __import__("datetime").date.today()
    prazo = (hoje + __import__("datetime").timedelta(days=30)).isoformat()
    rp.escreve_insuficiente(3, 20, 60, 100,
                            por_dia={"2026-09-0" + str(i): {"A", "B", "C"} for i in (1, 2, 3)},
                            prazo=prazo)
    texto = saida.read_text(encoding="utf-8")
    assert "no caminho certo" in texto
