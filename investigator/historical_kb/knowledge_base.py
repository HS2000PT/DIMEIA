"""Base de conhecimento histórica: notícias datadas + impacto pós-evento + embeddings.

A `HistoricalKB` é o coração do motor de correlação notícia–mercado. Constrói-se a partir
de notícias datadas e dos preços de fecho por ticker:
  1. para cada notícia, localiza o dia de negociação do evento (1.º dia >= data da notícia);
  2. mede o impacto pós-evento (+1/+3/+5d) com `event_study` (o que aconteceu DEPOIS — é
     evidência, não previsão; ver nota anti-lookahead em event_study.py);
  3. calcula o embedding do título (para recuperar precedentes semelhantes).

Dada uma notícia NOVA, `find_precedents` devolve as históricas mais parecidas (cosseno) e
o seu impacto — exatamente o que a explicação XAI mostra ao investidor ("no passado, notícias
semelhantes foram seguidas, em média, de X%").

Persistência: JSONL (uma notícia por linha) — legível, versionável em amostras, sem binários.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from investigator.correlation_engine.event_study import post_event_returns
from investigator.correlation_engine.similarity import top_k_similar
from investigator.historical_kb.embedder import Embedder
from investigator.historical_kb.record import NewsRecord


class HistoricalKB:
    """Coleção de `NewsRecord` com construção, persistência e recuperação de precedentes."""

    def __init__(self, records: list[NewsRecord] | None = None,
                 matrix: np.ndarray | None = None):
        self.records: list[NewsRecord] = list(records) if records else []
        # Matriz de vectores em float32, alinhada linha a linha com `records`. Só existe no
        # formato compacto; a `None` mantém-se o caminho antigo, byte a byte.
        self._matrix: np.ndarray | None = matrix

    def __len__(self) -> int:
        return len(self.records)

    # ── Construção ────────────────────────────────────────────────────────────
    @classmethod
    def build(
        cls,
        news: pd.DataFrame,
        prices: dict[str, pd.Series],
        embedder: Embedder,
        horizons: tuple[int, ...] = (1, 3, 5),
    ) -> HistoricalKB:
        """Constrói a KB a partir de notícias e preços.

        Args:
            news: DataFrame com colunas 'date', 'ticker', 'headline'.
            prices: dict ticker -> série de fecho indexada por datas ORDENADAS (DatetimeIndex).
            embedder: implementação de `Embedder` (ex.: HashingEmbedder, SbertEmbedder).
            horizons: horizontes do impacto pós-evento, em dias de negociação.

        Notícias sem preços para o ticker, ou cuja data fica depois do último preço, são
        ignoradas (não há impacto observável).
        """
        pending: list[tuple[str, str, str, dict[str, float]]] = []
        headlines: list[str] = []
        for _, row in news.iterrows():
            ticker = str(row["ticker"])
            headline = str(row["headline"])
            date = pd.Timestamp(row["date"])
            series = prices.get(ticker)
            if series is None or len(series) == 0:
                continue
            # 1.º dia de negociação >= data da notícia (evita lookahead: o evento "entra" no
            # primeiro dia em que o mercado pôde reagir).
            event_idx = int(series.index.searchsorted(date))
            if event_idx >= len(series):
                continue
            impacts_int = post_event_returns(
                series.reset_index(drop=True), event_idx, tuple(horizons)
            )
            impacts = {str(h): v for h, v in impacts_int.items()}
            pending.append((date.strftime("%Y-%m-%d"), ticker, headline, impacts))
            headlines.append(headline)

        embeddings = (
            embedder.encode(headlines) if headlines else np.zeros((0, embedder.dim))
        )
        records = [
            NewsRecord(
                date=date,
                ticker=ticker,
                headline=headline,
                impacts=impacts,
                embedding=[float(x) for x in emb],
            )
            for (date, ticker, headline, impacts), emb in zip(pending, embeddings, strict=True)
        ]
        return cls(records)

    # ── Recuperação de precedentes ────────────────────────────────────────────
    def find_precedents(
        self, query_text: str, embedder: Embedder, top_k: int = 5
    ) -> list[tuple[NewsRecord, float]]:
        """Devolve os `top_k` precedentes mais semelhantes ao texto, com o score de cosseno."""
        # Caminho compacto: a matriz já existe em float32 e os registos não trazem vector
        # nenhum. É o que permite uma base de dezenas de milhares de casos caber num
        # contentor pequeno — ver `load_compact`.
        if self._matrix is not None:
            if not len(self.records):
                return []
            query = np.asarray(embedder.encode([query_text])[0], dtype="float32")
            if query.shape[0] != self._matrix.shape[1]:
                raise ValueError(
                    f"Embedding dim mismatch: query has {query.shape[0]} dims but the "
                    f"knowledge base stores {self._matrix.shape[1]}. Query with the same "
                    "embedder used to build the KB."
                )
            hits = top_k_similar(query, self._matrix, k=top_k)
            return [(self.records[i], score) for i, score in hits]

        usable = [r for r in self.records if r.embedding is not None]
        if not usable:
            return []
        query = np.asarray(embedder.encode([query_text])[0], dtype="float64")
        matrix = np.array([r.embedding for r in usable], dtype="float64")
        if query.shape[0] != matrix.shape[1]:
            raise ValueError(
                f"Embedding dim mismatch: query has {query.shape[0]} dims but the knowledge base "
                f"stores {matrix.shape[1]}. Query with the same embedder used to build the KB."
            )
        hits = top_k_similar(query, matrix, k=top_k)
        return [(usable[i], score) for i, score in hits]

    # ── Persistência (JSONL) ──────────────────────────────────────────────────
    def save(self, path: str | Path) -> None:
        """Grava a KB em JSONL (uma notícia por linha)."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for record in self.records:
                f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    @classmethod
    def load(cls, path: str | Path, *, lean: bool = False) -> HistoricalKB:
        """Carrega a KB de um ficheiro JSONL.

        `lean=True` guarda os vectores numa matriz float32 única e **larga as listas de
        `float` de Python** de cada registo. O ficheiro não muda; o que muda é a forma em
        memória.

        ⚠️ Existe pela mesma medição que criou o formato compacto, aplicada onde ela nunca
        tinha sido aplicada. Medido a 2026-09-04 sobre a base viva real: **10 968 registos
        custavam 136,7 MB** em JSONL, contra 21,7 MB para os **38 214** do formato compacto —
        12,46 MB por mil registos contra 0,57, ou seja **22×**. O contentor tem 512 MB e o
        worker corria entre 518 e 970, com `R14` a cada poucos minutos. E a base viva é
        justamente a que **cresce**: deixá-la em listas de Python é escolher que o problema
        piore sozinho.

        Fica opt-in de propósito. `scripts/curate_kb_light.py` lê `record.embedding` depois de
        carregar, e mudar o comportamento por defeito partia-o em silêncio.
        """
        records: list[NewsRecord] = []
        with Path(path).open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(NewsRecord.from_dict(json.loads(line)))
        if lean and records and all(r.embedding is not None for r in records):
            matrix = np.asarray([r.embedding for r in records], dtype="float32")
            for r in records:  # a matriz passa a ser a única cópia dos vectores
                r.embedding = None
            return cls(records, matrix=matrix)
        return cls(records)

    # ── Persistência compacta (metadados + matriz float32) ────────────────────
    #
    # ⚠️ Existe por uma medição, não por elegância. Uma base de 38 214 casos guardada em
    # JSONL custa **655 MB de RAM** ao ser carregada, e o contentor de produção tem 512 MB —
    # ou seja, a base não cabia e a razão não era o volume dos dados. As mesmas
    # 38 214 × 384 posições ocupam 56 MB em float32: são **11,7×**, e vêm do custo de objecto
    # de cada `float` de Python guardado numa lista.
    #
    # Além disso, `find_precedents` reconstruía a matriz inteira **a cada consulta**. Aqui ela
    # é carregada uma vez e reutilizada.
    #
    # O formato são dois ficheiros: um JSONL só com metadados (sem vectores) e um `.npy` com
    # a matriz. Ficam separados de propósito — os metadados continuam legíveis por uma pessoa,
    # que é metade da razão de o projecto usar JSONL.

    def save_compact(self, meta_path: str | Path, vec_path: str | Path) -> None:
        """Grava metadados e vectores em separado; os vectores em float32."""
        meta_path, vec_path = Path(meta_path), Path(vec_path)
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        usable = [r for r in self.records if r.embedding is not None]
        if not usable:
            raise ValueError("nenhum registo tem embedding — não há matriz para gravar.")
        matrix = np.asarray([r.embedding for r in usable], dtype="float32")
        with meta_path.open("w", encoding="utf-8") as f:
            for r in usable:
                d = r.to_dict()
                d.pop("embedding", None)
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        np.save(vec_path, matrix)

    @classmethod
    def load_compact(cls, meta_path: str | Path, vec_path: str | Path) -> HistoricalKB:
        """Carrega o formato compacto. A matriz entra em modo `mmap`: fica no disco e só as
        páginas realmente tocadas vão para memória."""
        records: list[NewsRecord] = []
        with Path(meta_path).open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(NewsRecord.from_dict(json.loads(line)))
        matrix = np.load(Path(vec_path), mmap_mode="r")
        if matrix.shape[0] != len(records):
            raise ValueError(
                f"metadados e matriz não batem certo: {len(records)} registos contra "
                f"{matrix.shape[0]} vectores. Regenerar os dois a partir da mesma fonte."
            )
        return cls(records, matrix=matrix)
