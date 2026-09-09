"""Linha de base BM25 para a recuperação de precedentes (Robertson e Zaragoza 2009).

Porque existe
-------------
A §5.3.2 da dissertação declara que a linha lexical avaliada é «a forma mais simples dessa
família: contagem de palavras projetada por dispersão e comparada pelo cosseno, sem ponderação
pela raridade dos termos, sem saturação da frequência e sem normalização pelo comprimento do
texto», e conclui que «a comparação com uma função de ordenação bem parametrizada constitui
trabalho por realizar, e é a que tornaria esta conclusão mais forte».

O BM25 acrescenta exatamente as três peças em falta:

1. **raridade do termo** — via IDF;
2. **saturação da frequência** — via k1, de modo que repetir um termo rende cada vez menos;
3. **normalização pelo comprimento** — via b, de modo que um documento longo não pontue mais
   só por ser longo.

Formulação adotada
------------------
    IDF(t)     = ln( (N - n(t) + 0,5) / (n(t) + 0,5) + 1 )
    score(q,d) = Σ_{t ∈ q} IDF(t) · f(t,d)·(k1 + 1) / ( f(t,d) + k1·(1 - b + b·|d|/avgdl) )

com k1 = 1,5 e b = 0,75, que são os valores convencionais. A variante «+1» do IDF é a
não-negativa: a forma clássica torna-se negativa quando um termo ocorre em mais de metade dos
documentos, o que inverteria a ordenação para palavras muito comuns.

Os termos da consulta entram uma única vez cada (sem saturação do lado da consulta, o parâmetro
k3 da formulação original), por as consultas serem manchetes curtas.

Desempate
---------
Uma função lexical produz empates com frequência, e a §5.4.4 desta dissertação documenta o que
sucede quando um empate é resolvido pela ordem do ficheiro: mede-se a ordem alfabética das
empresas e toma-se isso por uma referência aleatória. Para que o mesmo não se repita aqui, os
empates são resolvidos por uma **permutação aleatória fixa** dos candidatos, com semente
declarada. O resultado continua determinístico e a cauda da ordenação é honestamente aleatória
em vez de alfabética.

Tudo puro NumPy e SciPy esparso, determinístico, sem estado global.
"""

from __future__ import annotations

import re
from collections import Counter

import numpy as np
from scipy import sparse

__all__ = ["Bm25Index", "bm25_precision_at_k", "tokenize"]

_TOKEN = re.compile(r"[a-z0-9]+")

#: Semente da permutação que resolve empates. Fixada aqui e não passada por argumento,
#: para que dois usos independentes do índice desempatem da mesma maneira.
TIEBREAK_SEED = 42


def tokenize(text: str) -> list[str]:
    """Minúsculas e sequências alfanuméricas. Determinístico e sem dependências."""
    return _TOKEN.findall(str(text).lower())


class Bm25Index:
    """Índice BM25 sobre uma coleção fixa de documentos.

    O peso do lado do documento é pré-calculado uma única vez, pelo que pontuar uma consulta
    se reduz a somar colunas de uma matriz esparsa.
    """

    def __init__(
        self,
        documents: list[str],
        k1: float = 1.5,
        b: float = 0.75,
        tiebreak_seed: int = TIEBREAK_SEED,
    ) -> None:
        if k1 < 0:
            raise ValueError("k1 tem de ser não-negativo.")
        if not 0.0 <= b <= 1.0:
            raise ValueError("b tem de estar entre 0 e 1.")

        self.k1 = float(k1)
        self.b = float(b)
        self.n_docs = len(documents)

        tokenized = [tokenize(d) for d in documents]
        lengths = np.array([len(t) for t in tokenized], dtype="float64")
        # Um corpus de documentos todos vazios não tem comprimento médio definido; usa-se 1,0
        # para que a normalização fique neutra em vez de produzir uma divisão por zero.
        self.avgdl = float(lengths.mean()) if lengths.size and lengths.sum() > 0 else 1.0

        vocab: dict[str, int] = {}
        rows: list[int] = []
        cols: list[int] = []
        freqs: list[float] = []
        doc_freq: Counter[int] = Counter()

        for i, toks in enumerate(tokenized):
            for term, f in Counter(toks).items():
                j = vocab.setdefault(term, len(vocab))
                rows.append(i)
                cols.append(j)
                freqs.append(float(f))
                doc_freq[j] += 1

        self.vocabulary = vocab
        n_terms = len(vocab)

        idf = np.zeros(n_terms, dtype="float64")
        for j, n_t in doc_freq.items():
            idf[j] = np.log((self.n_docs - n_t + 0.5) / (n_t + 0.5) + 1.0)
        self.idf = idf

        # Peso BM25 do lado do documento, elemento a elemento sobre os pares (doc, termo)
        # efetivamente presentes. A parte da consulta é apenas a seleção de colunas.
        f_arr = np.asarray(freqs, dtype="float64")
        r_arr = np.asarray(rows, dtype="int64")
        c_arr = np.asarray(cols, dtype="int64")
        norm = self.k1 * (1.0 - self.b + self.b * lengths[r_arr] / self.avgdl)
        weight = idf[c_arr] * (f_arr * (self.k1 + 1.0)) / (f_arr + norm)

        # float64: a matriz esparsa tem poucos milhões de elementos não-nulos e ocupa alguns
        # megabytes, pelo que não há memória a poupar aqui. Em float32 o valor devolvido
        # afasta-se do cálculo exato na sétima casa, e os testes verificam-no contra valores
        # calculados à mão. O consumo real de memória está no bloco denso de pontuações.
        self._weights = sparse.csr_matrix(
            (weight, (r_arr, c_arr)),
            shape=(self.n_docs, max(n_terms, 1)),
        )
        # Permutação fixa que resolve empates — ver a nota do cabeçalho do módulo.
        self._perm = np.random.default_rng(tiebreak_seed).permutation(self.n_docs)

    # -- consulta ----------------------------------------------------------

    def idf_of(self, term: str) -> float:
        """IDF de um termo; zero se o termo não estiver no vocabulário."""
        j = self.vocabulary.get(term)
        return 0.0 if j is None else float(self.idf[j])

    def _query_matrix(self, queries: list[str]) -> sparse.csr_matrix:
        rows: list[int] = []
        cols: list[int] = []
        for i, q in enumerate(queries):
            for term in set(tokenize(q)):
                j = self.vocabulary.get(term)
                if j is not None:
                    rows.append(i)
                    cols.append(j)
        data = np.ones(len(rows), dtype="float64")
        return sparse.csr_matrix(
            (data, (rows, cols)),
            shape=(len(queries), self._weights.shape[1]),
        )

    def scores(self, queries: list[str]) -> np.ndarray:
        """Matriz densa (n_consultas, n_documentos) de pontuações BM25, na ordem original."""
        q = self._query_matrix(list(queries))
        return np.asarray((q @ self._weights.T).todense(), dtype="float64")

    def top_k(
        self,
        queries: list[str],
        k: int = 5,
        forbid: np.ndarray | None = None,
        block: int = 500,
    ) -> np.ndarray:
        """Índices dos k documentos mais bem pontuados por consulta, com empates aleatorizados.

        `forbid` (n_consultas, n_documentos) marca candidatos proibidos, que recebem -inf.
        A avaliação é feita em blocos de consultas apenas por memória; o resultado não depende
        de `block`, propriedade que o conjunto de testes verifica.
        """
        queries = list(queries)
        kk = min(k, self.n_docs)
        out = np.empty((len(queries), kk), dtype="int64")
        perm = self._perm

        for start in range(0, len(queries), block):
            stop = min(start + block, len(queries))
            s = self.scores(queries[start:stop])
            if forbid is not None:
                s = np.where(forbid[start:stop], -np.inf, s)
            # Reordenar as colunas pela permutação fixa faz com que um empate seja resolvido
            # por ela, e não pela ordem em que os documentos estão no ficheiro.
            s_perm = s[:, perm]
            part = np.argpartition(-s_perm, kth=kk - 1, axis=1)[:, :kk]
            out[start:stop] = perm[part]
        return out

    def zero_score_fraction(
        self,
        queries: list[str],
        k: int = 5,
        forbid: np.ndarray | None = None,
        block: int = 500,
    ) -> float:
        """Fração dos k recuperados cuja pontuação é exatamente zero.

        Diagnóstico honesto: um valor elevado significa que o BM25 não encontrou termos comuns
        e que a posição foi preenchida pelo desempate aleatório, e não por correspondência.
        """
        queries = list(queries)
        kk = min(k, self.n_docs)
        zeros = 0
        total = 0
        perm = self._perm
        for start in range(0, len(queries), block):
            stop = min(start + block, len(queries))
            s = self.scores(queries[start:stop])
            if forbid is not None:
                s = np.where(forbid[start:stop], -np.inf, s)
            s_perm = s[:, perm]
            part = np.argpartition(-s_perm, kth=kk - 1, axis=1)[:, :kk]
            chosen = np.take_along_axis(s_perm, part, axis=1)
            zeros += int((chosen == 0.0).sum())
            total += chosen.size
        return float(zeros) / total if total else float("nan")


def bm25_precision_at_k(
    index: Bm25Index,
    query_texts: list[str],
    query_sectors: np.ndarray,
    cand_sectors: np.ndarray,
    k: int = 5,
    forbid: np.ndarray | None = None,
    block: int = 500,
) -> float:
    """Precision@k do BM25 sob o mesmo protocolo de `retrieval_precision_at_k`.

    Devolve a fração média dos k documentos recuperados que partilham o setor da consulta.
    """
    top = index.top_k(query_texts, k=k, forbid=forbid, block=block)
    hits = np.asarray(cand_sectors)[top] == np.asarray(query_sectors)[:, None]
    return float(hits.mean())
