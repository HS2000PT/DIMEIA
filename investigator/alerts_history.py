"""Histórico partilhado de alertas — a peça que faz a app mostrar EXATAMENTE o que o
Telegram recebeu, nunca um recálculo independente.

Puro: só lê/escreve JSONL local e sabe classificar/aparar entradas. Onde esse ficheiro fica
persistido de forma partilhada (branch `alerts-history` do repo, escrita pelo workflow) é
decisão de `scripts/run_alerts.py` e `.github/workflows/alerts.yml`
(ver `docs/design/going_live.md`) — este módulo não sabe nada de git nem de rede.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class HistoryEntry:
    """Um alerta realmente enviado. `text` é o texto EXATO (plain_text) que o Telegram
    recebeu — nem a app nem ninguém o recalcula, só o mostram."""

    date: str  # ISO (YYYY-MM-DD), dia do evento
    ticker: str
    kind: str  # "market" | "news"
    text: str


def classify_kind(text: str) -> str:
    """Deriva o tipo a partir de marcadores estáveis do próprio texto (já testados em
    tests/test_explainer.py — fidelidade XAI exige exatamente estas frases)."""
    return "market" if "Anomaly detected for" in text else "news"


def load_jsonl(path: str | Path) -> list[HistoryEntry]:
    """Lê o histórico; ficheiro em falta ou linha inválida não são erro fatal (fail-open)."""
    p = Path(path)
    if not p.exists():
        return []
    entries: list[HistoryEntry] = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(HistoryEntry(**json.loads(line)))
            except (json.JSONDecodeError, TypeError):
                continue
    return entries


def save_jsonl(entries: list[HistoryEntry], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(asdict(e), ensure_ascii=False) + "\n")


def append_and_trim(
    existing: list[HistoryEntry], new: list[HistoryEntry], max_entries: int = 500
) -> list[HistoryEntry]:
    """Acrescenta `new` a `existing` e apara ao limite, mantendo as entradas mais recentes.

    O limite existe para o ficheiro (e a branch git que o guarda) não crescer sem fim —
    a app só precisa de um histórico recente, não de um arquivo completo.
    """
    combined = existing + new
    return combined[-max_entries:] if max_entries > 0 else combined
