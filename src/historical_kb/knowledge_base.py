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

from src.correlation_engine.event_study import post_event_returns
from src.correlation_engine.similarity import top_k_similar
from src.historical_kb.embedder import Embedder
from src.historical_kb.record import NewsRecord


class HistoricalKB:
    """Coleção de `NewsRecord` com construção, persistência e recuperação de precedentes."""

    def __init__(self, records: list[NewsRecord] | None = None):
        self.records: list[NewsRecord] = list(records) if records else []

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
        usable = [r for r in self.records if r.embedding is not None]
        if not usable:
            return []
        query = embedder.encode([query_text])[0]
        matrix = np.array([r.embedding for r in usable], dtype="float64")
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
    def load(cls, path: str | Path) -> HistoricalKB:
        """Carrega a KB de um ficheiro JSONL."""
        records: list[NewsRecord] = []
        with Path(path).open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(NewsRecord.from_dict(json.loads(line)))
        return cls(records)
