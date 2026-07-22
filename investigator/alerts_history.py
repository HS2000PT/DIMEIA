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
    recebeu — nem a app nem ninguém o recalcula, só o mostram.

    `key` (opcional) é a chave de dedup entre produtores (VM + Actions): a mesma que
    `scripts/run_alerts.py::news_key` calcula — sha1(ticker|plain_text)[:12]. Entradas
    antigas sem key continuam válidas (a leitura recalcula quando precisa)."""

    date: str  # ISO (YYYY-MM-DD), dia do evento
    ticker: str
    kind: str  # "market" | "news" | "summary" | "open"
    text: str
    key: str = ""


def classify_kind(text: str) -> str:
    """Deriva o tipo a partir do EMOJI de cabeçalho (marcador estável e robusto à reescrita
    do texto): 📊 resumo · 🔺/🔻 mercado · 📰 notícia. Isto corrige um bug latente — os
    alertas intradiários ("Unusual intraday move for…") não continham "Anomaly detected for"
    e eram classificados como notícia. Fallback por frase para entradas antigas sem emoji."""
    t = text.lstrip()
    if t.startswith("📊"):
        return "summary"
    if t.startswith("🔔"):
        return "open"
    if t.startswith(("🔺", "🔻")):
        return "market"
    if t.startswith("📰"):
        return "news"
    # Legado / textos sem emoji (histórico antigo, literais de teste)
    if "Daily close summary" in text:
        return "summary"
    if "Market open" in text:
        return "open"
    if "Anomaly detected for" in text or "intraday move for" in text:
        return "market"
    return "news"


def parse_jsonl_lines(lines: list[str]) -> list[HistoryEntry]:
    """Interpreta linhas JSONL já em memória; linhas inválidas são ignoradas (fail-open)."""
    entries: list[HistoryEntry] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(HistoryEntry(**json.loads(line)))
        except (json.JSONDecodeError, TypeError):
            continue
    return entries


def load_jsonl(path: str | Path) -> list[HistoryEntry]:
    """Lê o histórico local; ficheiro em falta não é erro fatal (fail-open)."""
    p = Path(path)
    if not p.exists():
        return []
    return parse_jsonl_lines(p.read_text(encoding="utf-8").splitlines())


def fetch_remote(url: str, timeout: float = 5.0) -> list[HistoryEntry]:
    """Vai buscar o histórico partilhado a um URL raw (ex.: GitHub) — é o que a app pública usa.

    Fail-open TOTAL: rede em baixo, 404, timeout ou JSON inválido devolvem lista vazia em vez
    de levantar — a app tem de continuar a funcionar mesmo sem histórico partilhado disponível.
    """
    import requests

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return parse_jsonl_lines(resp.text.splitlines())
    except Exception:
        return []


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
