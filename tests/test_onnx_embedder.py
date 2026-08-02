"""Testes do embedder semântico leve (MiniLM em ONNX) e do fail-open do produto.

Offline por desenho: a matemática do pooling e o contrato de erro/fallback correm em
qualquer máquina; os testes que precisam do MODELO real saltam-se sozinhos quando a cache
local (`models/onnx/`) não existe (ex.: CI leve) — nenhum teste descarrega nada.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from investigator.historical_kb import onnx_embedder as oe


def _model_cached() -> bool:
    return all((oe._CACHE_DIR / name).exists() for name in oe._FILES)


# ── Matemática pura (corre sempre) ──────────────────────────────────────────


def test_masked_mean_pool_ignora_padding_e_normaliza():
    """Mean pooling com máscara: o token de padding não conta; o resultado tem norma 1."""
    hidden = np.array([[[1.0, 2.0], [3.0, 4.0], [100.0, 100.0]]])  # último token = padding
    mask = np.array([[1, 1, 0]])
    out = oe.masked_mean_pool(hidden, mask)
    esperado = np.array([2.0, 3.0]) / np.linalg.norm([2.0, 3.0])
    assert np.allclose(out[0], esperado)
    assert np.isclose(np.linalg.norm(out[0]), 1.0)


def test_ensure_model_offline_falha_com_instrucoes(tmp_path):
    """Sem cache e sem auto_download, o erro diz exatamente como resolver (nunca toca a rede)."""
    with pytest.raises(FileNotFoundError, match="Modelo ONNX em falta"):
        oe.ensure_model(cache_dir=tmp_path, auto_download=False)


# ── Contrato do kb_query_embedder / product_retrieval (corre sempre) ────────


def _escrever_kb(tmp_path, dim: int):
    kb = tmp_path / "kb.jsonl"
    rec = {"date": "2020-01-02", "ticker": "T", "headline": "x",
           "impacts": {"1": 0.0, "3": 0.0, "5": 0.0}, "embedding": [0.1] * dim}
    kb.write_text(json.dumps(rec) + "\n", encoding="utf-8")
    return kb


def test_kb_query_embedder_dim_generica_usa_hashing(tmp_path):
    from investigator.main import kb_query_embedder

    embedder = kb_query_embedder(_escrever_kb(tmp_path, 5))
    assert embedder.dim == 5
    assert getattr(embedder, "semantic", False) is False


def test_kb_384_nunca_cai_em_hashing(tmp_path, monkeypatch):
    """Uma KB semântica (384-d) NUNCA é consultada por hashing (espaços diferentes dariam
    vizinhos plausíveis mas errados): sem modelo disponível, levanta — não finge."""
    from investigator.main import kb_query_embedder

    monkeypatch.setattr(oe, "_CACHE_DIR", tmp_path / "vazio")
    with pytest.raises(FileNotFoundError):
        kb_query_embedder(_escrever_kb(tmp_path, 384), auto_download=False)


def test_product_retrieval_fail_open_sem_modelo(tmp_path, monkeypatch, capsys):
    """Sem modelo ONNX, o produto degrada para a KB-amostra word-overlap e diz porquê."""
    from investigator.main import product_retrieval

    monkeypatch.setattr(oe, "_CACHE_DIR", tmp_path / "vazio")
    kb_path, embedder = product_retrieval(auto_download=False)
    assert kb_path.name == "kb_sample.jsonl"
    assert embedder.dim == 64
    assert getattr(embedder, "semantic", False) is False
    assert "fallback" in capsys.readouterr().out


# ── Modelo real (salta-se sozinho sem a cache local) ────────────────────────


@pytest.mark.skipif(not _model_cached(), reason="modelo ONNX não descarregado nesta máquina")
def test_onnx_encode_e_semantica_real():
    """Embeddings 384-d, norma 1, e semântica de verdade: 'chip shortage' fica mais perto
    de 'semiconductor supply' do que de 'dividend' (o hashing falharia — zero palavras comuns)."""
    emb = oe.OnnxMiniLMEmbedder()
    m = emb.encode([
        "Chip shortage hits carmakers worldwide",
        "Semiconductor supply struggles to meet demand",
        "Company raises quarterly dividend",
    ])
    assert m.shape == (3, 384)
    assert np.allclose(np.linalg.norm(m, axis=1), 1.0, atol=1e-6)
    assert m[0] @ m[1] > m[0] @ m[2]


@pytest.mark.skipif(not _model_cached(), reason="modelo ONNX não descarregado nesta máquina")
def test_kb_384_usa_onnx_quando_ha_modelo(tmp_path):
    from investigator.main import kb_query_embedder

    embedder = kb_query_embedder(_escrever_kb(tmp_path, 384))
    assert embedder.dim == 384
    assert embedder.semantic is True


@pytest.mark.skipif(not _model_cached(), reason="modelo ONNX não descarregado nesta máquina")
def test_sessao_e_mono_thread_e_sem_arena():
    """Regressão de PRODUÇÃO: a sessão tem de ser mono-thread e sem arena de memória.

    Por omissão o onnxruntime dimensiona pools de threads e arena pelo número de CPUs que a
    máquina REPORTA. Num contentor pequeno isso é desastroso, porque o contentor vê os cores
    do hospedeiro mas só tem a sua fatia de RAM. Medido em 2026-08-02: 96 MB numa máquina de
    4 cores contra >1,2 GB num dyno Heroku Basic de 512 MB, onde o worker entrava em ciclo de
    crash por R15 antes de completar uma varredura.

    Sem este teste, alguém que reconstrua a sessão sem `SessionOptions` reintroduz a falha, e
    ela só aparece no deploy.
    """
    emb = oe.OnnxMiniLMEmbedder()
    opts = emb._session.get_session_options()
    assert opts.intra_op_num_threads == 1
    assert opts.inter_op_num_threads == 1
    assert opts.enable_cpu_mem_arena is False


def test_encode_fatia_em_lotes(monkeypatch):
    """O `encode` tem de fatiar: o pico de memória cresce linearmente com o lote.

    Não precisa do modelo real — conta as chamadas ao passo interno.
    """
    chamadas = []

    class Falso(oe.OnnxMiniLMEmbedder):
        def __init__(self):  # não carrega modelo nenhum
            pass

        def _encode_batch(self, texts):
            chamadas.append(len(texts))
            return np.zeros((len(texts), 384))

    monkeypatch.setattr(oe, "_ENCODE_BATCH", 32)
    saida = Falso().encode([f"t{i}" for i in range(100)])
    assert saida.shape == (100, 384)
    assert chamadas == [32, 32, 32, 4], f"não fatiou como esperado: {chamadas}"


@pytest.mark.skipif(not _model_cached(), reason="modelo ONNX não descarregado nesta máquina")
def test_embedder_e_sensivel_ao_padding_e_isso_esta_documentado():
    """Fixa uma propriedade REAL e contra-intuitiva, medida a 2026-08-02.

    Seria natural assumir que o *mean pooling* mascarado torna o resultado independente do
    padding. Não torna: o modelo é quantizado em int8 e as posições de padding influenciam as
    outras. O mesmo texto sozinho e ao lado de uma frase longa difere em ~0.02.

    O teste existe para que ninguém volte a assumir invariância ao lote e construa em cima
    disso (por exemplo, a comparar embeddings gerados em corridas com lotes diferentes).
    """
    emb = oe.OnnxMiniLMEmbedder()
    curto = "Stock up"
    longo = (
        "Regulator opens a wide ranging antitrust investigation into the market practices "
        "of this firm following complaints from rivals and consumer groups worldwide"
    )
    sozinho = emb.encode([curto])[0]
    acompanhado = emb.encode([curto, longo])[0]
    cos = float(sozinho @ acompanhado)
    assert cos < 0.9999, "se isto passar a ser invariante, atualizar a docstring de encode()"
    assert cos > 0.95, f"divergência maior do que a medida ({cos:.4f}) — investigar"
