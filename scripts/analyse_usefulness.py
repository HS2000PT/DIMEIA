"""Analisa o estudo de utilidade (RQ3) e escreve o documento de avaliação.

Lê `docs/study/responses.csv` (preenchido à mão pelo facilitador) e produz
`docs/evaluation/evaluation_usefulness.md` — a tabela do Estudo de Caso 5.

**Disciplina estatística, deliberada e declarada.** Com N pequeno o objetivo NÃO é
significância: é evidência dirigida e deteção de problemas de usabilidade.
- H1/H2 (compreensão, calibração) são proporções → reportadas com intervalo de Wilson, que se
  comporta bem em amostras pequenas, ao contrário do intervalo normal.
- H3 (Likert) → mediana e média, e **teste de Wilcoxon emparelhado apenas se N ≥ 8**, o limiar
  que o próprio protocolo fixou ANTES de haver dados. Abaixo disso, só descritivo.
- Nunca se declara "significativo" sem teste, e o documento diz sempre que é um piloto.

Uso:
    python scripts/analyse_usefulness.py
    python scripts/analyse_usefulness.py --responses docs/study/responses.csv
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from investigator.console import force_utf8_stdout

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO / "docs" / "study" / "responses.csv"
OUT_MD = REPO / "docs" / "evaluation" / "evaluation_usefulness.md"

OBJETIVAS = [("p1_detected", "Identified what was detected"),
             ("p1_why", "Identified why it was flagged"),
             ("p1_not_prediction", "Recognised it is NOT a prediction")]
LIKERT = [("q1_clear", "Clear"), ("q2_complete", "Complete"), ("q3_actionable", "Actionable"),
          ("q4_calibrated", "Calibrated trust"), ("q5_preference", "Preferred over a bare number")]
WILCOXON_MIN_N = 8  # fixado no protocolo ANTES de haver dados


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confiança de Wilson — apropriado a proporções com N pequeno."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    margem = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centro - margem), min(1.0, centro + margem))


def _wilcoxon(pares: list[tuple[float, float]]) -> tuple[float, float] | None:
    """Wilcoxon signed-rank emparelhado. Devolve (W, p aproximado) ou None se inaplicável."""
    difs = [b - a for a, b in pares if b != a]
    n = len(difs)
    if n < 6:  # aproximação normal deixa de ser razoável
        return None
    ordenadas = sorted(difs, key=abs)
    postos: list[float] = []
    i = 0
    while i < len(ordenadas):
        j = i
        while j + 1 < len(ordenadas) and abs(ordenadas[j + 1]) == abs(ordenadas[i]):
            j += 1
        posto_medio = (i + j) / 2 + 1  # média dos postos empatados
        postos += [posto_medio] * (j - i + 1)
        i = j + 1
    w_mais = sum(p for d, p in zip(ordenadas, postos, strict=True) if d > 0)
    w_menos = sum(p for d, p in zip(ordenadas, postos, strict=True) if d < 0)
    w = min(w_mais, w_menos)
    mu = n * (n + 1) / 4
    sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    if sigma == 0:
        return None
    z = (w - mu) / sigma
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return (w, min(1.0, p))


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Análise do estudo de utilidade (RQ3)")
    ap.add_argument("--responses", default=str(DEFAULT_CSV))
    args = ap.parse_args()

    path = Path(args.responses)
    if not path.exists():
        print(f"[!] {path} não existe.\n"
              "    Correr primeiro `python scripts/build_usefulness_pack.py`, recrutar os\n"
              "    participantes, e copiar responses_template.csv → responses.csv preenchido.")
        return 1

    linhas = [r for r in csv.DictReader(path.open(encoding="utf-8"))
              if (r.get("condition") or "").strip() in ("A", "B")]
    preenchidas = [r for r in linhas if (r.get("p1_detected") or "").strip() != ""]
    if not preenchidas:
        print(f"[!] {path} está vazio (só o template). Nada a analisar.")
        return 1

    participantes = sorted({r["participant"] for r in preenchidas})
    n = len(participantes)
    print(f"{len(preenchidas)} respostas · {n} participante(s)")

    def _num(r: dict, campo: str) -> float | None:
        v = (r.get(campo) or "").strip()
        try:
            return float(v)
        except ValueError:
            return None

    # ── H1/H2: proporções objetivas por condição ──────────────────────────────
    objetivas: dict[str, dict[str, list[int]]] = {c: defaultdict(list) for c in "AB"}
    for r in preenchidas:
        for campo, _rot in OBJETIVAS:
            v = _num(r, campo)
            if v is not None:
                objetivas[r["condition"]][campo].append(int(v))

    # ── H3: Likert, emparelhado por participante (média por condição) ─────────
    likert: dict[str, dict[str, list[float]]] = {c: defaultdict(list) for c in "AB"}
    por_part: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: {"A": defaultdict(list), "B": defaultdict(list)})
    for r in preenchidas:
        for campo, _rot in LIKERT:
            v = _num(r, campo)
            if v is not None:
                likert[r["condition"]][campo].append(v)
                por_part[r["participant"]][r["condition"]][campo].append(v)

    gerado = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    L = [
        "# evaluation_usefulness.md — Estudo-piloto de utilidade (RQ3, metade em aberto)",
        "",
        "> Gerado por `scripts/analyse_usefulness.py` a partir de `docs/study/responses.csv`.",
        f"> Protocolo: `docs/design/usefulness_study.md` · N = **{n}** participante(s) · {gerado}",
        "",
        "**Enquadramento honesto.** Isto é um PILOTO. Com este N o objetivo não é significância",
        "estatística: é evidência dirigida sobre compreensão e calibração de confiança, e",
        "deteção de problemas de usabilidade. Não generaliza para a população de retalho, e não",
        "mede decisões de investimento reais — por desenho, já que a tese recusa previsão.",
        "",
        "## H1/H2 — Compreensão objetiva (proporção de acertos)",
        "",
        "Condição **A** = só o facto nu. Condição **B** = o alerta completo do InvestiGator.",
        "Intervalos de Wilson a 95% (apropriados a proporções com N pequeno).",
        "",
        "| Question | A (bare fact) | B (full alert) | Difference |",
        "|---|---|---|---|",
    ]
    for campo, rot in OBJETIVAS:
        a, b = objetivas["A"][campo], objetivas["B"][campo]
        if not a and not b:
            continue
        pa = sum(a) / len(a) if a else float("nan")
        pb = sum(b) / len(b) if b else float("nan")
        la, ha = _wilson(sum(a), len(a))
        lb, hb = _wilson(sum(b), len(b))
        dif = (pb - pa) if a and b else float("nan")
        L.append(f"| {rot} | {pa:.0%} [{la:.0%}–{ha:.0%}] (n={len(a)}) | "
                 f"{pb:.0%} [{lb:.0%}–{hb:.0%}] (n={len(b)}) | {dif:+.0%} |")

    L += ["", "## H3 — Perceção (Likert 1–5)", "",
          "| Item | A mean | A median | B mean | B median | Difference |",
          "|---|---|---|---|---|---|"]
    for campo, rot in LIKERT:
        a, b = likert["A"][campo], likert["B"][campo]
        if not a and not b:
            continue
        ma = sum(a) / len(a) if a else float("nan")
        mb = sum(b) / len(b) if b else float("nan")
        meda = sorted(a)[len(a) // 2] if a else float("nan")
        medb = sorted(b)[len(b) // 2] if b else float("nan")
        L.append(f"| {rot} | {ma:.2f} | {meda:.1f} | {mb:.2f} | {medb:.1f} | {mb - ma:+.2f} |")

    # ── Teste emparelhado, só se o protocolo o permitir ───────────────────────
    L += ["", "### Teste emparelhado", ""]
    if n < WILCOXON_MIN_N:
        L.append(f"N = {n} < {WILCOXON_MIN_N}: **nenhum teste de significância é reportado**. "
                 "O limiar foi fixado no protocolo *antes* de existirem dados, e reportar um "
                 "p-value com este N seria sobre-interpretação.")
    else:
        pares_globais: list[tuple[float, float]] = []
        for p in participantes:
            a_vals = [v for vs in por_part[p]["A"].values() for v in vs]
            b_vals = [v for vs in por_part[p]["B"].values() for v in vs]
            if a_vals and b_vals:
                pares_globais.append((sum(a_vals) / len(a_vals), sum(b_vals) / len(b_vals)))
        res = _wilcoxon(pares_globais)
        if res is None:
            L.append("Pares insuficientes (ou todos empatados) para um Wilcoxon fiável — "
                     "reportado só o descritivo acima.")
        else:
            w, pv = res
            L.append(f"Wilcoxon signed-rank sobre a média Likert por participante "
                     f"(n={len(pares_globais)} pares): W = {w:.1f}, p ≈ {pv:.3f}. "
                     "Não-paramétrico, apropriado a Likert e a amostras pequenas.")

    comentarios = [(r["participant"], (r.get("open_comment") or "").strip())
                   for r in preenchidas if (r.get("open_comment") or "").strip()]
    L += ["", "## O que faltou ou confundiu (qualitativo)", ""]
    if comentarios:
        vistos = set()
        for p, c in comentarios:
            if c not in vistos:
                L.append(f"- *{p}*: “{c}”")
                vistos.add(c)
    else:
        L.append("(sem comentários registados)")

    L += [
        "",
        "## Limitações declaradas",
        "",
        f"- **Piloto de conveniência**, N = {n}. Não generaliza.",
        "- *Utilidade* está operacionalizada como compreensão + perceção, **não** como retorno",
        "  financeiro — coerente com a recusa de previsão que define o sistema.",
        "- Participantes lusófonos a ler alertas em inglês: registar se a língua atrapalhou.",
        "- O facilitador conhece as hipóteses; o guião é fixo e não há ajuda durante a tarefa,",
        "  mas o enviesamento do experimentador não pode ser excluído num piloto.",
        "",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"[ok] {OUT_MD.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
