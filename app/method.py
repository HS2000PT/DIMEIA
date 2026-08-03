"""Os números congelados da avaliação, num sítio só e **amarrados à sua fonte**.

**O problema que este módulo resolve.** A página do método mostra os resultados da
dissertação. Escrevê-los à mão no HTML significaria que, no dia em que uma avaliação for
recorrida, o produto passaria a afirmar um número que os documentos já não sustentam — e
não haveria nada a assinalá-lo. É a mesma classe de defeito que este projecto já apanhou
noutros sítios: não o teste que falha, o número que envelhece em silêncio.

**A solução, que é barata.** Cada número guarda a **cadeia exacta de caracteres** com que
aparece no `.md` congelado que o produziu, mais o caminho desse ficheiro. O teste em
`tests/test_method.py` abre cada ficheiro e exige lá a cadeia. Se alguém recorrer uma
avaliação e o valor mudar, a suite parte — que é exactamente o que tem de acontecer.

Não se lê o `.md` em tempo de execução de propósito: obrigaria a analisar prosa e tabelas
num caminho que tem de falhar aberto, e um analisador que falha aberto devolveria uma
página sem números em vez de um erro. Assim o risco vive nos testes, onde falhar é útil.
"""

from __future__ import annotations

from dataclasses import dataclass

EVAL = "docs/evaluation"


@dataclass(frozen=True)
class Number:
    """Um resultado congelado: o rótulo que o utilizador lê, o valor, e de onde veio."""

    label: str
    value: str      # exactamente como aparece no ficheiro de origem
    source: str     # caminho relativo à raiz do repositório
    note: str = ""


# ── RQ2 · recuperar precedentes ──────────────────────────────────────────────────────
RETRIEVAL: tuple[Number, ...] = (
    Number("Semantic (MiniLM) — the model in this product", "0.514",
           f"{EVAL}/evaluation_results.md"),
    Number("Semantic (MPNet) — larger, not deployed", "0.538",
           f"{EVAL}/evaluation_results.md"),
    Number("Word overlap (lexical baseline)", "0.346", f"{EVAL}/evaluation_results.md"),
    Number("Most recent (recency baseline)", "0.126", f"{EVAL}/evaluation_results.md"),
    Number("Random (chance)", "0.240", f"{EVAL}/evaluation_results.md"),
    Number("Semantic, at scale on 80k headlines", "0.595",
           f"{EVAL}/evaluation_retrieval_fnspid.md",
           "Higher than the preliminary figure, on a far larger corpus."),
)

# ── RQ1 · detectar movimentos invulgares ─────────────────────────────────────────────
ANOMALY: tuple[Number, ...] = (
    Number("Rolling z-score — spread in firing rate across companies", "0.015",
           f"{EVAL}/evaluation_anomaly.md",
           "Near-constant: it fires as often for a calm stock as for a volatile one."),
    Number("Fixed percentage threshold — same spread", "0.344",
           f"{EVAL}/evaluation_anomaly.md",
           "Twenty times wider: it would drown one company and ignore another."),
)

# ── RQ4 · decidir o que merece um alerta ─────────────────────────────────────────────
TRIAGE: tuple[Number, ...] = (
    Number("Volatility only (the simple baseline)", "0.542", f"{EVAL}/evaluation_triage.md"),
    Number("Context only", "0.538", f"{EVAL}/evaluation_triage.md"),
    Number("Context + text (the main model)", "0.496", f"{EVAL}/evaluation_triage.md"),
    Number("Gradient boosting on context + text", "0.469", f"{EVAL}/evaluation_triage.md"),
    Number("Alert on everything (floor)", "0.378", f"{EVAL}/evaluation_triage.md"),
)

# A conclusão que estes números obrigam, escrita como ela é. Não é uma ressalva: é o
# resultado. Um produto que mostrasse só as vitórias da sua própria avaliação estaria a
# fazer marketing com números académicos.
TRIAGE_VERDICT = (
    "No text model beat the volatility baseline. That is the answer, reported as it fell. "
    "The mechanism still earns its place: at the same alert budget it picks 0.632 useful "
    "days against 0.163 for alerting on everything."
)
TRIAGE_BUDGET: tuple[Number, ...] = (
    Number("Useful days picked, at a fixed alert budget", "0.632",
           f"{EVAL}/evaluation_triage.md"),
    Number("Same budget, alerting on everything", "0.163", f"{EVAL}/evaluation_triage.md"),
)

ALL_NUMBERS: tuple[Number, ...] = (
    *RETRIEVAL, *ANOMALY, *TRIAGE, *TRIAGE_BUDGET,
)
