"""Registo de uma notícia na base de conhecimento histórica (FNSPID).

Um `NewsRecord` guarda o mínimo necessário para o motor de correlação e para a explicação:
a data e o ticker, o título da notícia, o impacto pós-evento medido (event study) e o
embedding do título (para recuperar precedentes semelhantes). É serializável em JSON.

Governança (§5.4): guardamos só o TÍTULO (não o texto integral de terceiros) na KB que
versionamos em amostras; o corpo completo fica nos dados gitignored, se necessário.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class NewsRecord:
    """Notícia datada + impacto medido + embedding do título."""

    date: str  # ISO 'YYYY-MM-DD' (dia da notícia)
    ticker: str  # símbolo (ex.: 'AAPL')
    headline: str  # título da notícia
    impacts: dict[str, float] = field(default_factory=dict)  # {'1': r+1d, '3': r+3d, '5': r+5d}
    embedding: list[float] | None = None  # vetor do título (None até ser calculado)

    def to_dict(self) -> dict:
        """Forma serializável (JSON) do registo."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> NewsRecord:
        """Reconstrói um registo a partir de um dict (ex.: linha de JSONL)."""
        impacts_raw = d.get("impacts") or {}
        embedding = d.get("embedding")
        return cls(
            date=str(d["date"]),
            ticker=str(d["ticker"]),
            headline=str(d["headline"]),
            impacts={str(k): float(v) for k, v in impacts_raw.items()},
            embedding=[float(x) for x in embedding] if embedding is not None else None,
        )
