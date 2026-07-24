"""KB VIVA — a base de conhecimento que cresce com as notícias que o runner vê todos os dias.

Problema real (feedback do aluno, 2026-07-11): a KB histórica é FNSPID 2018–2023 — o
precedente mais recente tem ~2,5 anos, de outro regime de mercado ("timeline matters").
Solução: cada manchete RELEVANTE que o scan vê entra num ficheiro de pendentes; dias depois,
quando o impacto (+1/+3/+5d) já é observável, o caso "matura" e entra na KB viva — no MESMO
formato `NewsRecord` de sempre. O retrieval passa a fundir as duas KBs com DECAIMENTO por
idade: o cosseno decide a relevância temática, a idade desempata a favor do recente.

Governança (§5.4): o `summary` do Finnhub NUNCA é persistido (texto de terceiros) — é usado
só em memória para enriquecer o embedding no momento da captura; guardamos título + vetor.

Honestidade XAI: o decaimento afeta APENAS a ordenação; a similaridade mostrada ao
utilizador é sempre o cosseno real, e cada precedente mostra a sua data/idade.

Puro e testável (tests/test_live_kb.py); a persistência partilhada (branch alerts-history)
é decidida por scripts/run_alerts.py, como no histórico de alertas.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from investigator.correlation_engine.event_study import post_event_returns
from investigator.historical_kb.record import NewsRecord

_HORIZONS = (1, 3, 5)
# Dias de CALENDÁRIO antes de tentar maturar: 8 garante ≥5 dias úteis observáveis na
# maioria das semanas (fins de semana + 1 feriado); se ainda faltar barra, fica pendente.
MIN_AGE_DAYS = 8


@dataclass(frozen=True)
class PendingNews:
    """Manchete relevante à espera de maturação. O embedding já vem calculado (captura)."""

    date: str  # ISO, dia da notícia
    ticker: str
    headline: str
    key: str  # dedup (news_key do runner)
    embedding: list[float]


def embed_text(headline: str, summary: str = "") -> str:
    """Texto usado para o embedding: manchete + resumo (só em memória, nunca persistido)."""
    headline = (headline or "").strip()
    summary = (summary or "").strip()
    return f"{headline}. {summary}" if summary else headline


# ── Persistência JSONL (mesmo estilo de alerts_history) ────────────────────────


def load_pending(path: str | Path) -> list[PendingNews]:
    p = Path(path)
    if not p.exists():
        return []
    out: list[PendingNews] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(PendingNews(**json.loads(line)))
        except (json.JSONDecodeError, TypeError):
            continue
    return out


def save_pending(entries: list[PendingNews], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(asdict(e), ensure_ascii=False) + "\n")


def add_pending(existing: list[PendingNews], new: list[PendingNews]) -> list[PendingNews]:
    """Puro: acrescenta sem duplicar (dedup pela `key`)."""
    seen = {e.key for e in existing}
    merged = list(existing)
    for e in new:
        if e.key not in seen:
            merged.append(e)
            seen.add(e.key)
    return merged


def append_records(records: list[NewsRecord], path: str | Path) -> None:
    """Acrescenta casos maturados à KB viva (JSONL, formato NewsRecord de sempre)."""
    if not records:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")


# ── Maturação (pura) ────────────────────────────────────────────────────────────


def mature_entry(entry: PendingNews, closes: pd.Series) -> NewsRecord | None:
    """Matura UM pendente: alinha ao 1.º dia de negociação ≥ data e mede +1/+3/+5d.

    Devolve None se o impacto ainda não for totalmente observável (falta a barra +5d) —
    o pendente fica para o próximo ciclo. Mesma regra de alinhamento da KB da tese
    (knowledge_base.build): sem lookahead, medir o desfecho ≠ prever.
    """
    if closes is None or len(closes) == 0:
        return None
    event_idx = int(closes.index.searchsorted(pd.Timestamp(entry.date)))
    if event_idx >= len(closes) or event_idx + max(_HORIZONS) >= len(closes):
        return None  # evento fora da série ou +5d ainda não observável
    impacts_int = post_event_returns(closes.reset_index(drop=True), event_idx, _HORIZONS)
    impacts = {str(h): float(v) for h, v in impacts_int.items()}
    if any(v != v for v in impacts.values()):  # NaN — não deveria acontecer com o guard acima
        return None
    return NewsRecord(date=entry.date, ticker=entry.ticker, headline=entry.headline,
                      impacts=impacts, embedding=[round(float(x), 5) for x in entry.embedding])


def mature_ready(pending: list[PendingNews], closes_by_ticker: dict[str, pd.Series],
                 today: date, max_batch: int = 30,
                 ) -> tuple[list[NewsRecord], list[PendingNews]]:
    """Puro: matura os pendentes prontos; devolve (maturados, ainda_pendentes)."""
    matured: list[NewsRecord] = []
    still: list[PendingNews] = []
    for e in pending:
        if len(matured) >= max_batch:
            still.append(e)
            continue
        try:
            old_enough = (today - date.fromisoformat(e.date)).days >= MIN_AGE_DAYS
        except ValueError:
            continue  # data inválida: descarta (nunca maturaria)
        if not old_enough:
            still.append(e)
            continue
        rec = mature_entry(e, closes_by_ticker.get(e.ticker))
        if rec is None:
            still.append(e)
        else:
            matured.append(rec)
    return matured, still


def fetch_remote_records(url: str, timeout: float = 5.0) -> list[NewsRecord]:
    """KB viva publicada (branch alerts-history) lida por URL raw — é o que a app usa.

    Fail-open total (como alerts_history.fetch_remote): rede em baixo/404/linha inválida
    devolvem o que der (ou lista vazia) — a app nunca cai por causa da KB viva.
    """
    import requests

    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except Exception:  # noqa: BLE001
        return []
    out: list[NewsRecord] = []
    for line in resp.text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(NewsRecord.from_dict(json.loads(line)))
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            continue
    return out


# ── Retrieval fundido com decaimento por idade (puro) ──────────────────────────


def recency_weight(record_date: str, today: date, half_life_days: float) -> float:
    """0.5^(idade/half_life): 1.0 hoje, 0.5 há um half-life, 0.25 há dois…"""
    try:
        age = max(0, (today - date.fromisoformat(record_date)).days)
    except ValueError:
        return 0.0
    return math.pow(0.5, age / max(1.0, half_life_days))


def _within_age(record_date: str, today: date, max_age_days: int) -> bool:
    """True se `record_date` (ISO) está dentro de [hoje-max_age_days, hoje]. Fail-open:
    uma data corrompida na KB é descartada (False), como em `recency_weight` — nunca
    derruba a recuperação (o mesmo padrão tolerante do resto do módulo)."""
    try:
        age = (today - date.fromisoformat(record_date)).days
    except ValueError:
        return False
    return 0 <= age <= max_age_days


def merged_precedents(query: str, kbs: list, embedder, top_k: int, today: date,
                      half_life_days: float = 365.0,
                      max_age_days: int | None = None) -> list[tuple[NewsRecord, float]]:
    """Junta candidatos de várias KBs e reordena por cosseno × decaimento de idade.

    Devolve pares (registo, COSENO REAL) — o decaimento só ordena, nunca é mostrado como
    se fosse similaridade (honestidade XAI). `max_age_days` corta precedentes antigos
    (o "botão dos 6 meses" do aluno — útil quando a KB viva tiver meses de dados).
    """
    candidatos: list[tuple[NewsRecord, float]] = []
    for kb in kbs:
        if kb is not None and len(kb) > 0:
            candidatos.extend(kb.find_precedents(query, embedder, top_k=top_k * 3))
    vistos: set[tuple[str, str, str]] = set()
    unicos: list[tuple[NewsRecord, float]] = []
    for rec, score in candidatos:
        chave = (rec.date, rec.ticker, rec.headline)
        if chave not in vistos:
            vistos.add(chave)
            unicos.append((rec, score))
    if max_age_days is not None:
        unicos = [(r, s) for r, s in unicos if _within_age(r.date, today, max_age_days)]
    unicos.sort(key=lambda rs: -(rs[1] * recency_weight(rs[0].date, today, half_life_days)))
    return unicos[:top_k]
