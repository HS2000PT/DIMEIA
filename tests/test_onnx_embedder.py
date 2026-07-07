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
