"""Funil de gates — onde é que cada ticker morreu, em cada varredura.

**Porque existe.** `docs/evaluation/alert_funnel.md` mostra o resultado agregado do funil
(944 manchetes relevantes → 42 alertas) e um facto que salta à vista: cinco dos dez tickers
receberam ZERO alertas apesar de 135 (AAPL), 91 (AMZN), 83 (NFLX), 75 (MSFT) e 71 (GOOGL)
manchetes relevantes. A pergunta óbvia — *qual dos gates os matou?* — não tinha resposta:
o registo de decisões (`triage/postval.py`) só é escrito DEPOIS dos gates de frescura e de
similaridade, por isso tudo o que morre antes nunca era registado. Os dados retroativos não
existem; este módulo garante que passam a existir.

Puro: só constrói e resume registos. Quem os persiste (e onde) é `scripts/run_alerts.py`.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

# Etapas do funil, pela ordem em que o runner as aplica. A ordem importa: é a ordem do
# relatório e a ordem em que um ticker pode "morrer".
STAGES: tuple[str, ...] = (
    "no_news",            # a fonte não devolveu nada para este ticker
    "none_relevant",      # veio notícia, mas nenhuma passou o filtro de relevância
    "stale",              # a mais recente relevante é antiga demais (max_age_days)
    "weak_precedent",     # nenhum precedente com cosseno >= min_similarity
    "triage_suppressed",  # o modelo aprendido pontuou abaixo de min_materiality
    "error",              # exceção no processamento deste ticker (fail-open)
    "alerted",            # sobreviveu a tudo e gerou alerta
)

_TERMINAL_OK = "alerted"


@dataclass(frozen=True)
class GateRecord:
    """Um ticker, uma varredura, a etapa onde parou.

    `detail` guarda o número que justificou a paragem (ex.: "sim 0.31 < 0.45") — é o que
    transforma uma contagem numa explicação defensável."""

    date: str
    ticker: str
    stage: str
    detail: str = ""

    def __post_init__(self) -> None:
        if self.stage not in STAGES:
            raise ValueError(f"etapa desconhecida: {self.stage!r} (esperado: {STAGES})")


def summarise(records: list[GateRecord]) -> dict[str, int]:
    """Contagem por etapa, com TODAS as etapas presentes (zeros incluídos).

    Os zeros são deliberados: um relatório onde a etapa simplesmente desaparece quando não
    dispara esconde precisamente a informação que se quer ler."""
    counts = Counter(r.stage for r in records)
    return {stage: counts.get(stage, 0) for stage in STAGES}


def per_ticker(records: list[GateRecord]) -> dict[str, dict[str, int]]:
    """Contagem por ticker → etapa. Responde a 'o que mata a AAPL?' diretamente."""
    out: dict[str, dict[str, int]] = {}
    for r in records:
        out.setdefault(r.ticker, {stage: 0 for stage in STAGES})[r.stage] += 1
    return out


def attrition_table(records: list[GateRecord]) -> list[tuple[str, int, str]]:
    """Por ticker: (ticker, nº de varreduras que alertaram, etapa que mais o matou).

    Ordenado por alertas ascendente — os tickers silenciosos aparecem primeiro, que é
    exatamente a lista que interessa investigar."""
    rows: list[tuple[str, int, str]] = []
    for ticker, counts in per_ticker(records).items():
        alerted = counts[_TERMINAL_OK]
        blockers = {s: n for s, n in counts.items() if s != _TERMINAL_OK and n > 0}
        top = max(blockers, key=lambda s: blockers[s]) if blockers else "-"
        rows.append((ticker, alerted, top))
    return sorted(rows, key=lambda r: (r[1], r[0]))


def append_jsonl(records: list[GateRecord], path: str | Path, max_entries: int = 5000) -> None:
    """Acrescenta ao ficheiro e apara (o mesmo contrato de `alerts_history`). Fail-open:
    um erro aqui nunca pode travar um ciclo de alertas."""
    if not records:
        return
    p = Path(path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        existing = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
        new = [json.dumps(asdict(r), ensure_ascii=False) for r in records]
        combined = (existing + new)[-max_entries:] if max_entries > 0 else existing + new
        p.write_text("\n".join(combined) + "\n", encoding="utf-8")
    except OSError:
        return


def load_jsonl(path: str | Path) -> list[GateRecord]:
    """Lê o funil; ficheiro em falta ou linhas inválidas não são erro (fail-open)."""
    p = Path(path)
    if not p.exists():
        return []
    out: list[GateRecord] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            out.append(GateRecord(**{k: payload[k] for k in ("date", "ticker", "stage")
                                     if k in payload},
                                  detail=str(payload.get("detail", ""))))
        except (json.JSONDecodeError, TypeError, ValueError, KeyError):
            continue
    return out
