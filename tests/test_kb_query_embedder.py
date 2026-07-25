"""Regressão: kb_query_embedder deve inferir a dimensão de um embedding REAL, não do
1.º registo do ficheiro. Se o primeiro registo não tiver embedding, antes escolhia
HashingEmbedder(64) por defeito e a recuperação rebentava com 'dim mismatch' numa KB
bem-formada a partir da 2.ª linha."""

from __future__ import annotations

import json

from investigator.historical_kb.embedder import HashingEmbedder
from investigator.main import kb_query_embedder


def test_kb_query_embedder_salta_registos_sem_embedding(tmp_path):
    kb = tmp_path / "kb.jsonl"
    kb.write_text(
        json.dumps({"headline": "sem embedding", "embedding": None}) + "\n"
        + json.dumps({"headline": "embedding vazio", "embedding": []}) + "\n"
        + json.dumps({"headline": "com embedding", "embedding": [0.1, 0.2, 0.3]}) + "\n",
        encoding="utf-8",
    )
    emb = kb_query_embedder(kb, auto_download=False)
    assert isinstance(emb, HashingEmbedder)
    assert emb.dim == 3  # lê a 3.ª linha, não fica preso nos 64 por defeito


def test_kb_query_embedder_default_sem_nenhum_embedding(tmp_path):
    """Ficheiro sem qualquer embedding → cai no default 64 (comportamento antigo intacto)."""
    kb = tmp_path / "kb.jsonl"
    kb.write_text(json.dumps({"headline": "so texto"}) + "\n", encoding="utf-8")
    emb = kb_query_embedder(kb, auto_download=False)
    assert isinstance(emb, HashingEmbedder)
    assert emb.dim == 64
