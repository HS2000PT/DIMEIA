"""Pacote de evidência — o que o gerador vê, e a única coisa que ele pode afirmar.

## O contrato

Um `Bundle` é um conjunto de `Fact`, e um `Fact` é um facto **que um motor calculou**, com um
identificador curto (`f1`, `f2`, …), a sua proveniência e o valor. O gerador recebe os factos
serializados e é obrigado a citar identificadores. Depois:

- a **guarda** verifica que nenhum número no texto está fora dos factos;
- a **interface** resolve cada `[f3]` de volta ao facto, para o utilizador poder abrir a
  evidência por trás de qualquer frase.

Sem identificadores, "AI explicável" seria uma promessa. Com identificadores, é uma
travessia: frase → facto → motor → ficheiro.

## Porque é que os factos carregam `origin`

Porque as três origens têm valor probatório diferente e o produto tem de as distinguir no
ecrã (é o requisito de proveniência, e é também o que separa esta tese de um wrapper de LLM):

- `measured`   — saiu de dados de mercado ou de um carimbo de uma fonte. Verificável.
- `computed`   — saiu de uma fórmula determinística sobre `measured`. Reproduzível.
- `model`      — saiu de um modelo treinado (triagem calibrada, recuperação semântica).
                 Tem incerteza, e a incerteza está publicada na avaliação.

Nenhum facto tem origem `generated`: **o gerador não produz factos**, só prosa.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

Origin = Literal["measured", "computed", "model"]

# Âmbitos que o produto sabe explicar. Cada um monta um pacote diferente porque a pergunta é
# diferente — "o que se passa no mercado" e "o que se passa com a NVDA" não partilham evidência.
Scope = Literal["market", "asset", "event", "period"]


@dataclass(frozen=True)
class Fact:
    """Um facto citável. `fid` é o que aparece entre parênteses rectos no texto gerado."""

    fid: str
    kind: str
    label: str          # legível por humanos — é o que a interface mostra no chip
    value: Any
    origin: Origin
    detail: dict[str, Any] = field(default_factory=dict)

    def as_line(self) -> str:
        """A serialização que o LLM vê. Curta de propósito: cada token custa latência."""
        return f"[{self.fid}] {self.label}: {self.value}"

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.fid,
            "kind": self.kind,
            "label": self.label,
            "value": self.value,
            "origin": self.origin,
            "detail": self.detail,
        }


@dataclass
class Bundle:
    """Os factos de um âmbito, mais o vocabulário numérico que a guarda vai exigir."""

    scope: Scope
    subject: str                       # "market" ou o ticker
    facts: list[Fact] = field(default_factory=list)
    generated_at: str = ""
    as_of: str = ""                    # o carimbo dos DADOS, que não é o de agora
    notes: list[str] = field(default_factory=list)

    _n: int = 0

    def add(self, kind: str, label: str, value: Any, origin: Origin,
            **detail: Any) -> Fact:
        self._n += 1
        f = Fact(f"f{self._n}", kind, label, value, origin, detail)
        self.facts.append(f)
        return f

    def by_id(self, fid: str) -> Fact | None:
        return next((f for f in self.facts if f.fid == fid), None)

    def of_kind(self, kind: str) -> list[Fact]:
        return [f for f in self.facts if f.kind == kind]

    def evidence_block(self) -> str:
        return "\n".join(f.as_line() for f in self.facts)

    def numeric_vocabulary(self) -> set[str]:
        """Todos os números que o texto gerado pode conter.

        Construído a partir dos VALORES dos factos, não do texto que os descreve: é o mesmo
        princípio do narrador de alertas, e é o que impede o gerador de combinar dois números
        verdadeiros num terceiro que ninguém calculou.
        """
        vocab: set[str] = set()
        for f in self.facts:
            _collect_numbers(f.value, vocab)
            for v in f.detail.values():
                _collect_numbers(v, vocab)
        return vocab

    def to_json(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "subject": self.subject,
            "as_of": self.as_of,
            "generated_at": self.generated_at,
            "facts": [f.to_json() for f in self.facts],
            "notes": self.notes,
        }


def _fmt(x: float, places: int = 2) -> str:
    """Formatação única para todo o pacote.

    Existir **uma** função é o que torna o vocabulário numérico correcto: se um sítio
    escrevesse `2.1` e outro `2.10`, a guarda rejeitaria texto fiel — que é o falso positivo
    que faz desligar guardas.
    """
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x:+.{places}f}" if places and abs(x) < 1000 else f"{x:.{places}f}"


def _safe_quote(text: str) -> str:
    """Normaliza aspas duplas INTERIORES para apóstrofos.

    Manchetes reais contêm aspas, e aspas aninhadas partem a detecção de citações (a regex não
    aninha): o conteúdo interior ficava FORA de qualquer citação e a isenção falhava. Mesma
    função e mesma razão que em `narrator/core.py`.
    """
    return text.replace('"', "'").replace("“", "'").replace("”", "'")


def _collect_numbers(value: Any, out: set[str]) -> None:
    """Junta ao vocabulário todas as formas em que um valor pode legitimamente aparecer."""
    if isinstance(value, bool) or value is None:
        return
    if isinstance(value, int | float):
        if isinstance(value, float) and math.isnan(value):
            return
        for places in (0, 1, 2, 3):
            s = f"{float(value):.{places}f}"
            out.add(s)
            out.add(s.lstrip("+"))
            if not s.startswith("-"):
                out.add(f"+{s}")
        out.add(str(int(value)) if float(value).is_integer() else str(value))
        return
    if isinstance(value, str):
        # Valores compostos são a regra, não a excepção: a decomposição é uma frase inteira
        # ("market -0.34%, sector -0.96%, company +0.13%") e cada número lá dentro foi
        # calculado por um motor. Extrair só quando a string INTEIRA é numérica deixava esses
        # números fora do vocabulário, e a guarda rejeitava texto fiel — apanhado no primeiro
        # ensaio, e é o falso positivo que faz desligar guardas.
        for tok in re.findall(r"[+-]?\d+(?:\.\d+)?", value):
            out.add(tok)
            out.add(tok.lstrip("+"))
            if not tok.startswith(("-", "+")):
                out.add(f"+{tok}")
            # A mesma quantidade com outra precisão continua a ser a mesma quantidade.
            try:
                for places in (0, 1, 2, 3):
                    s = f"{float(tok):.{places}f}"
                    out.add(s)
                    out.add(s.lstrip("+"))
                    if not s.startswith("-"):
                        out.add(f"+{s}")
            except ValueError:
                pass
        return
    if isinstance(value, list | tuple):
        for v in value:
            _collect_numbers(v, out)
    elif isinstance(value, dict):
        for v in value.values():
            _collect_numbers(v, out)


# ── Construtores de pacote ────────────────────────────────────────────────────

def build_market_bundle(rows: list[dict], as_of: str, threshold: float = 1.5,
                        window: int = 20) -> Bundle:
    """O pacote que responde a "o que se passa neste momento?".

    Agrega o que o painel já calculava e nunca somava. O estudo de mercado registou isto como
    a maior lacuna de percurso: *"Every ingredient of that sentence is already computed…
    Nobody has ever summed them."*
    """
    b = Bundle(scope="market", subject="market",
               generated_at=datetime.now(UTC).isoformat(timespec="seconds"), as_of=as_of)

    live = [r for r in rows if r.get("z") is not None]
    flagged = [r for r in live if abs(float(r["z"])) >= threshold]
    b.add("coverage", "Names watched", len(live), "measured")
    b.add("flagged_count", f"Names flagged today (|z| >= {threshold})", len(flagged),
          "computed", threshold=threshold, window=window,
          tickers=[r["ticker"] for r in flagged])

    # Direcção agregada: quantos subiram, quantos desceram. Contagem, não média — uma média de
    # doze retornos não é um facto sobre nenhum deles.
    up = [r for r in live if float(r.get("move") or 0) > 0]
    down = [r for r in live if float(r.get("move") or 0) < 0]
    b.add("breadth", "Names up / down today", f"{len(up)} up, {len(down)} down", "computed",
          up=len(up), down=len(down))

    # Quem é que o mercado explica. É a segunda pergunta do trabalho, agora ao nível do painel.
    drivers = [r["decomp"]["driver"] for r in live if r.get("decomp")]
    if drivers:
        counts = {d: drivers.count(d) for d in set(drivers)}
        top = max(counts, key=lambda k: counts[k])
        b.add("driver_mix", "Dominant source of today's moves, counted across names",
              ", ".join(f"{k}: {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])),
              "computed", counts=counts, top=top)

    for r in sorted(live, key=lambda r: -abs(float(r.get("z") or 0)))[:6]:
        _add_asset_core(b, r, threshold, window, prefix=f"{r['ticker']} ")

    b.notes.append(
        "Every number above was computed by the system's own engines from market data. "
        "No number here is forecast."
    )
    return b


def build_asset_bundle(row: dict, as_of: str, threshold: float = 1.5, window: int = 20,
                       headlines: list[dict] | None = None,
                       precedents: list[dict] | None = None,
                       triage: dict | None = None,
                       gate: dict | None = None,
                       market_row: dict | None = None) -> Bundle:
    """O pacote de um activo: tudo o que o sistema sabe sobre um nome, agora."""
    t = row.get("ticker", "?")
    b = Bundle(scope="asset", subject=t,
               generated_at=datetime.now(UTC).isoformat(timespec="seconds"), as_of=as_of)

    _add_asset_core(b, row, threshold, window)

    if market_row and market_row.get("move") is not None:
        b.add("market_context", "Broad market move on the same day",
              f"{_fmt(float(market_row['move']) * 100)}%", "measured",
              symbol=market_row.get("ticker", "SPY"))

    for h in (headlines or [])[:6]:
        # ENTRE ASPAS, e não é cosmético. O valor citado é a fronteira entre **o que a fonte
        # disse** e **o que nós afirmamos** — a guarda usa exactamente essa marca para julgar
        # as duas com réguas diferentes (ver `guard._mask_exempt`). Sem as aspas, uma manchete
        # que contenha a previsão de um analista faria o sistema rejeitar o seu próprio texto.
        b.add("headline", f"Headline captured for {t}",
              f'"{_safe_quote(h.get("headline", ""))}"', "measured",
              headline=h.get("headline", ""),
              source=h.get("source", ""), published_at=h.get("published_at") or h.get("date"),
              url=h.get("url", ""))

    for p in (precedents or [])[:5]:
        # O facto mais forte que o sistema tem, e o que nenhum LLM sabe de cor: uma manchete
        # parecida do passado COM O DESFECHO MEDIDO a +5 dias.
        b.add("precedent", "Similar past headline, with its measured 5-day outcome",
              f'"{p.get("headline", "")}" ({p.get("date", "")}) -> '
              f'{_fmt(float(p.get("impact_pct", 0.0)))}% after 5 trading days',
              "model",
              similarity=round(float(p.get("similarity", 0.0)), 3),
              date=p.get("date", ""), impact_pct=round(float(p.get("impact_pct", 0.0)), 2),
              headline=p.get("headline", ""))

    if triage and triage.get("prob") is not None:
        b.add("triage", "Learned triage score: calibrated probability of an unusually large "
              "move in either direction over the next few days",
              f"{float(triage['prob']) * 100:.0f}%", "model",
              contributions=triage.get("contributions", {}),
              model="logistic regression + Platt calibration, context features only")

    if gate:
        b.add("gate", "Why the system stayed silent on this name",
              gate.get("reason", ""), "computed", margin=gate.get("margin"),
              stage=gate.get("stage", ""))

    b.notes.append(
        "Precedent outcomes are measured history over 80k+ archived headlines, not forecasts. "
        "The triage score estimates whether the market reacts, never which way."
    )
    return b


def _add_asset_core(b: Bundle, row: dict, threshold: float, window: int,
                    prefix: str = "") -> None:
    """Os factos que qualquer âmbito precisa de um activo. Um só sítio, para o mercado e o
    activo não poderem divergir na forma como descrevem o mesmo nome."""
    t = row.get("ticker", "?")
    if row.get("move") is not None:
        b.add("price_move", f"{prefix}Move on the latest completed session",
              f"{_fmt(float(row['move']) * 100)}%", "measured", ticker=t)
    if row.get("z") is not None:
        z = float(row["z"])
        b.add("zscore", f"{prefix}z-score against its own {window}-day norm",
              _fmt(z), "computed", ticker=t, threshold=threshold, window=window,
              flagged=abs(z) >= threshold)
    rar = row.get("rarity")
    if rar and rar.get("n"):
        b.add("rarity", f"{prefix}Days in the last {rar['n']} trading days that moved at "
              f"least this much", rar["count"], "computed", ticker=t,
              count=rar["count"], n=rar["n"])
    d = row.get("decomp")
    if d:
        b.add("decomposition",
              f"{prefix}Move split into market / sector / company-specific",
              f"market {_fmt(float(d['market']) * 100)}%, "
              f"sector {_fmt(float(d['sector']) * 100)}%, "
              f"company {_fmt(float(d['company']) * 100)}%", "computed",
              ticker=t, driver=d.get("driver", ""),
              method="two-factor, sector orthogonalised, Vasicek-shrunk betas from prior data")
    if row.get("vol_ratio"):
        b.add("volume", f"{prefix}Trading volume against its usual level",
              f"{float(row['vol_ratio']):.1f}x", "computed", ticker=t)
