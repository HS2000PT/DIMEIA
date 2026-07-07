"""Embedders de texto para o motor de correlação.

Um *embedder* transforma texto (o título de uma notícia) num vetor numérico, para que
notícias semanticamente parecidas fiquem próximas no espaço (similaridade do cosseno).

Define-se a interface `Embedder` (Protocol) e duas implementações:
- `HashingEmbedder`: determinístico e SEM dependências (truque de hashing de tokens). Não
  capta semântica como o SBERT, mas é reprodutível e serve de *baseline* para a avaliação
  (ablação) e para testar todo o pipeline sem a stack pesada de ML.
- `SbertEmbedder`: SBERT via `sentence-transformers` — a abordagem metodológica da tese
  (Reimers & Gurevych, 2019). O import é TARDIO (dentro do __init__) para que o núcleo e
  os testes não dependam de torch/transformers.

Como explico ao júri (3 frases): "Represento cada notícia por um vetor. O SBERT coloca
notícias com significado parecido perto umas das outras. Assim, dada uma notícia nova,
procuro as históricas mais próximas e mostro o que aconteceu ao mercado a seguir."
"""

from __future__ import annotations

import hashlib
from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class Embedder(Protocol):
    """Interface mínima: `dim` (dimensão) e `encode(textos) -> matriz (n, dim)`."""

    dim: int

    def encode(self, texts: list[str]) -> np.ndarray: ...


class HashingEmbedder:
    """Embedding determinístico por hashing de tokens (bag-of-words + truque de hashing).

    Cada palavra é mapeada para uma posição do vetor por hash (md5 % dim); contam-se as
    ocorrências e normaliza-se (L2). É um *baseline* lexical: capta sobreposição de palavras,
    não significado. Útil para reprodutibilidade, testes e comparação na avaliação.
    """

    semantic = False  # baseline lexical — a UI descreve o motor em uso com honestidade

    def __init__(self, dim: int = 64):
        self.dim = int(dim)

    def _embed_one(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dim, dtype="float64")
        for token in text.lower().split():
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)  # hash não-cripto
            vec[h % self.dim] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype="float64")
        return np.vstack([self._embed_one(t) for t in texts])


class SbertEmbedder:
    """SBERT via sentence-transformers (import tardio). Modelo default: all-MiniLM-L6-v2.

    Embeddings normalizados (L2) → o produto interno já é a similaridade do cosseno.
    """

    semantic = True

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer  # import tardio (stack pesada)

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        # sentence-transformers >=5 renomeou o método; suportamos ambos.
        if hasattr(self._model, "get_embedding_dimension"):
            self.dim = int(self._model.get_embedding_dimension())
        else:
            self.dim = int(self._model.get_sentence_embedding_dimension())

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype="float64")
        emb = self._model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        return np.asarray(emb, dtype="float64")
