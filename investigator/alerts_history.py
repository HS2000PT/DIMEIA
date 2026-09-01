"""Histórico partilhado de alertas — a peça que faz a app mostrar EXATAMENTE o que o
Telegram recebeu, nunca um recálculo independente.

Puro: só lê/escreve JSONL local e sabe classificar/aparar entradas. Onde esse ficheiro fica
persistido de forma partilhada (branch `alerts-history` do repo, escrita pelo workflow) é
decisão de `scripts/run_alerts.py` e `.github/workflows/alerts.yml`
(ver `docs/design/going_live.md`) — este módulo não sabe nada de git nem de rede.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class HistoryEntry:
    """Um alerta realmente enviado. `text` é o texto EXATO (plain_text) que o Telegram
    recebeu — nem a app nem ninguém o recalcula, só o mostram.

    `key` (opcional) é a chave de dedup entre produtores (VM + Actions): a mesma que
    `scripts/run_alerts.py::news_key` calcula — sha1(ticker|plain_text)[:12]. Entradas
    antigas sem key continuam válidas (a leitura recalcula quando precisa).

    **Instrumentação de tempo (2026-07-29).** `date` é o dia do evento — granularidade
    insuficiente para afirmar seja o que for sobre LATÊNCIA. Sem os dois carimbos abaixo o
    sistema não consegue produzir um único número de latência, nem retroativamente. São
    opcionais e retrocompatíveis: entradas antigas (sem eles) continuam a ler-se na mesma.

    - `event_at`: instante UTC em que o FACTO aconteceu segundo a fonte (para notícias, a
      hora de publicação que o Finnhub devolve). É o carimbo que interessa: `event_at →
      sent_at` é a latência que o utilizador sente e que a queixa "chegam tarde" nomeia;
    - `detected_at`: instante UTC (ISO 8601) em que o ciclo detetou o evento;
    - `sent_at`: instante UTC em que a entrega ao Telegram foi confirmada;
    - `price_source`: qual das 5 fontes da cadeia serviu o preço (`yfinance`, `tiingo`,
      `polygon`, `stooq`, `alphavantage`) — a cadeia já sabe, mas o valor era deitado fora.
    """

    date: str  # ISO (YYYY-MM-DD), dia do evento
    ticker: str
    kind: str  # "market" | "news" | "summary" | "open"
    text: str
    key: str = ""
    event_at: str = ""  # ISO 8601 UTC — quando o facto aconteceu (publicação da notícia)
    detected_at: str = ""  # ISO 8601 UTC, ex.: "2026-07-29T14:32:07Z"
    sent_at: str = ""  # ISO 8601 UTC
    price_source: str = ""  # fonte que serviu o preço (só alertas de mercado)
    # ── Identidade da mensagem no Telegram (2026-09-01) ──────────────────────────────────
    # ⚠️ Sem estes dois, uma mensagem já entregue é INALCANÇÁVEL: não há como lhe acrescentar
    # a análise que chegou oito segundos depois, nem o desfecho observado que só existe cinco
    # dias depois. Guardá-los no momento do envio é a única oportunidade — o Telegram não
    # oferece maneira de reencontrar uma mensagem pelo conteúdo.
    # Opcionais e retrocompatíveis: as entradas antigas continuam a ler-se na mesma.
    message_id: int = 0
    chat_id: str = ""
    # ⚠️ O HTML EXATO que o Telegram recebeu, e não o `text`, que é a versão sem tags para a
    # consola e para o painel. Sem este campo não é possível **editar** a mensagem mais tarde
    # sem a degradar: o `plain_text` tira o negrito e desfaz as entidades HTML, portanto
    # reenviar o `text` perderia a formatação e, numa manchete com «<» ou «&», produziria HTML
    # inválido que o Telegram rejeita. Vazio nas entradas anteriores a 2026-09-01, e é por isso
    # que a anotação de desfecho as ignora — são inalcançáveis de qualquer maneira, por não
    # terem `message_id`.
    text_html: str = ""
    # Estado da mensagem: "" (o de sempre, texto completo à partida), "esboco" (foi entregue o
    # cabeçalho e a análise ainda não chegou), "completo" (a edição com a análise foi aceite),
    # "anotado" (já leva o desfecho observado).
    estado: str = ""

    def _delta(self, start: str) -> float | None:
        if not start or not self.sent_at:
            return None
        try:
            t0 = datetime.fromisoformat(start.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(self.sent_at.replace("Z", "+00:00"))
        except ValueError:
            return None
        return (t1 - t0).total_seconds()

    def pipeline_seconds(self) -> float | None:
        """Segundos entre deteção e entrega — latência INTERNA (tipicamente ~1 s). Útil para
        provar que o custo não está no nosso lado. None quando falta carimbo."""
        return self._delta(self.detected_at)

    def latency_seconds(self) -> float | None:
        """Segundos entre o FACTO e a entrega — a latência que o utilizador sente. É este o
        número honesto a reportar na tese. None em entradas antigas (sem carimbos)."""
        return self._delta(self.event_at)


def utc_stamp(now: datetime | None = None) -> str:
    """Carimbo UTC ISO 8601 com sufixo Z. `now` injetável para testes deterministas."""
    moment = now or datetime.now(UTC)
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def classify_kind(text: str) -> str:
    """Deriva o tipo a partir do EMOJI de cabeçalho (marcador estável e robusto à reescrita
    do texto): 📊 resumo · 📈/📉 mercado · 📰 notícia. Isto corrige um bug latente — os
    alertas intradiários ("Unusual intraday move for…") não continham "Anomaly detected for"
    e eram classificados como notícia. Fallback por frase para entradas antigas sem emoji.
    Aceita ainda o 🔺/🔻 legado (histórico antigo, antes das setas verdes/vermelhas)."""
    t = text.lstrip()
    if t.startswith("📊"):
        return "summary"
    if t.startswith("🔔"):
        return "open"
    if t.startswith(("📈", "📉", "🔺", "🔻")):
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


_KNOWN_FIELDS = frozenset(f.name for f in fields(HistoryEntry))


def parse_jsonl_lines(lines: list[str]) -> list[HistoryEntry]:
    """Interpreta linhas JSONL já em memória; linhas inválidas são ignoradas (fail-open).

    **Campos desconhecidos são descartados em vez de rebentar.** Sem isto, acrescentar um
    campo ao esquema partia TODOS os leitores mais antigos ainda em produção: o
    `HistoryEntry(**payload)` levantava `TypeError` e a linha era silenciosamente saltada —
    ou seja, durante um rollout a app implantada deixava de ver os alertas NOVOS, sem
    qualquer erro visível. Tolerar o excedente torna o esquema extensível para sempre.
    """
    entries: list[HistoryEntry] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(payload, dict):
            continue
        try:
            entries.append(HistoryEntry(**{k: v for k, v in payload.items() if k in _KNOWN_FIELDS}))
        except TypeError:
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


# Campos acrescentados em 2026-07-29: só são escritos quando têm valor, para o JSONL (e a
# branch git que o guarda) não encher de `"detected_at": ""` em cada linha. O formato das
# entradas antigas fica byte-igual.
_OMIT_WHEN_EMPTY = ("event_at", "detected_at", "sent_at", "price_source")


def save_jsonl(entries: list[HistoryEntry], path: str | Path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for e in entries:
            payload = {
                k: v for k, v in asdict(e).items() if v or k not in _OMIT_WHEN_EMPTY
            }
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def append_and_trim(
    existing: list[HistoryEntry], new: list[HistoryEntry], max_entries: int = 500
) -> list[HistoryEntry]:
    """Acrescenta `new` a `existing` e apara ao limite, mantendo as entradas mais recentes.

    O limite existe para o ficheiro (e a branch git que o guarda) não crescer sem fim —
    a app só precisa de um histórico recente, não de um arquivo completo.
    """
    combined = existing + new
    return combined[-max_entries:] if max_entries > 0 else combined
