"""Pós-validação das decisões registadas (M5.5) — fecha o loop da ideia "RL" do aluno.

O runner (`scripts/run_alerts.py`) regista cada decisão do gatilho de notícias em
`data/predictions_log.jsonl`. Este script, corrido dias depois (ex.: 1x/semana), busca os
preços REAIS, rotula as decisões cuja janela (d, d+h] já fechou — com o MESMO rótulo de
materialidade do treino — e escreve `docs/evaluation/live_monitoring.md`: precisão das
decisões mantidas vs base rate, Brier/calibração das probabilidades e a receita de retreino.

Uso:
    python scripts/run_alerts.py --dry-run     # (com news.enabled: true) gera decisões
    python scripts/post_validate.py            # dias depois: rotula + relatório

Preços buscados FRESCOS (sem a cache de data/prices/): a pós-validação precisa dos dias
mais recentes por definição. Sem log ainda, sai com 0 e explica o que falta.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.console import force_utf8_stdout  # noqa: E402
from src.triage.postval import (  # noqa: E402
    dedup_decisions,
    label_decision,
    live_report,
    read_log,
)

REPO = Path(__file__).resolve().parents[1]
MARKET = "SPY"


def _fetch_fresh(ticker: str, start: str) -> pd.Series:
    """Fechos diários desde `start` até hoje, SEM cache (a pós-validação exige dados atuais)."""
    import yfinance as yf

    hist = yf.Ticker(ticker).history(start=start, interval="1d")
    if hist is None or hist.empty:
        raise RuntimeError(f"Sem preços para {ticker}.")
    s = hist["Close"]
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    return s


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Pós-validação das decisões de triagem (M5.5)")
    ap.add_argument("--log", default=str(REPO / "data" / "predictions_log.jsonl"))
    ap.add_argument("--tau", type=float, default=0.02, help="mesmo τ do treino (rótulo primário)")
    ap.add_argument("--horizon", type=int, default=3, help="mesmo h do treino (rótulo primário)")
    ap.add_argument("--out", default=str(REPO / "docs" / "evaluation" / "live_monitoring.md"))
    args = ap.parse_args()

    raw = read_log(args.log)
    if not raw:
        print(f"Sem decisões em {args.log}.")
        print("Para gerar: liga `news.enabled: true` no config/alerts.yaml e corre "
              "`python scripts/run_alerts.py --dry-run` (ou espera pelo cron).")
        return 0

    decisions = dedup_decisions(raw)
    start = (pd.to_datetime(min(d["news_date"] for d in decisions))
             - pd.DateOffset(days=60)).strftime("%Y-%m-%d")
    spy = _fetch_fresh(MARKET, start)

    matured: list[dict] = []
    pendentes = 0
    sem_precos = 0
    closes: dict[str, pd.Series] = {}
    for d in decisions:
        t = d["ticker"]
        if t not in closes:
            try:
                closes[t] = _fetch_fresh(t, start)
            except Exception as exc:  # noqa: BLE001  (um ticker sem preços não pára o loop)
                print(f"[saltar {t}] {type(exc).__name__}: {exc}")
                closes[t] = pd.Series(dtype="float64")
        if closes[t].empty:
            sem_precos += 1
            continue
        label = label_decision(d, closes[t], spy, tau=args.tau, horizon=args.horizon)
        if label is None:
            pendentes += 1
        else:
            matured.append({**d, "label": label})

    rep = live_report(matured)
    agora = datetime.now(UTC).strftime("%Y-%m-%d %H:%M")

    def _f(x: float) -> str:
        return "n/a" if x != x else f"{x:.3f}"

    lines = [
        "# live_monitoring.md — Pós-validação das decisões ao vivo (M5.5; reprodutível)",
        "",
        "> Gerado por `scripts/post_validate.py` a partir de `data/predictions_log.jsonl`.",
        "> **Não editar à mão.** O loop: o runner regista decisões → dias depois este script",
        "> rotula-as com o resultado REAL (mesmo rótulo do treino) → métricas ao vivo → retreino.",
        "",
        f"- **Gerado:** {agora} UTC · rótulo |retorno anormal vs SPY em (d, d+{args.horizon}]| "
        f"≥ {args.tau:g} (o primário do treino).",
        f"- **Decisões:** {len(raw)} registadas · {len(decisions)} únicas · "
        f"{len(matured)} maturadas · {pendentes} ainda pendentes · {sem_precos} sem preços.",
        "",
        "| Métrica ao vivo | Valor |",
        "|---|---|",
        f"| Precisão das decisões mantidas | {_f(rep['precisao_mantidas'])} "
        f"({rep['n_mantidas']} mantidas) |",
        f"| Base rate (todas as decisões maturadas) | {_f(rep['base_rate'])} ({rep['n']}) |",
        f"| Brier das probabilidades | {_f(rep['brier'])} |",
    ]
    if rep["calibracao"]:
        lines += ["", "Calibração (previsto vs observado):", "",
                  "| P prevista (média) | Fração observada | n |", "|---|---|---|"]
        for p, obs, n in rep["calibracao"]:
            lines.append(f"| {p:.2f} | {obs:.2f} | {n} |")
    lines += [
        "",
        "**Retreino com os dados acumulados** (quando houver decisões maturadas suficientes):",
        "`python scripts/build_dataset.py` → `python scripts/train_triage.py` (stack `--ml`;",
        "os joblib novos substituem os de `models/` — reprodutível, mesma seed).",
        "",
        "**Caveats honestos:** o log vive na máquina onde o runner corre — no cron do GitHub",
        "Actions o runner é efémero, por isso o loop completo corre na máquina do aluno",
        "(persistir o log na nuvem = Fase B, ver `docs/design/going_live.md`); decisões de",
        "`--dry-run` também contam (são decisões, não envios); amostras pequenas ⇒ ler as",
        "métricas como monitorização, não como avaliação (essa é `evaluation_triage.md`).",
    ]
    out = Path(args.out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Decisões: {len(raw)} registadas, {len(decisions)} únicas, "
          f"{len(matured)} maturadas, {pendentes} pendentes.")
    print(f"Escrito: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
