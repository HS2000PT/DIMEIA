"""Pós-validação das decisões registadas (M5.5) — fecha o loop da ideia "RL" do aluno.

O runner (`scripts/run_alerts.py`) regista cada decisão do gatilho de notícias em
`predictions_log.jsonl`. Este script, corrido dias depois (ex.: ao fecho, 1x/dia), busca os
preços REAIS, rotula as decisões cuja janela (d, d+h] já fechou — com o MESMO rótulo de
materialidade do treino — e escreve `live_monitoring.md`: precisão das decisões mantidas vs
base rate, Brier/calibração das probabilidades e a receita de retreino.

2026-07-22 (loop de pós-fecho tornado zero-ops):
  - os preços vêm agora da CADEIA DE FALLBACK multi-fonte (`load_close_series`), por isso o
    script corre nos runners do GitHub Actions, onde o yfinance está bloqueado;
  - os caminhos por defeito seguem a branch partilhada quando `INVESTIGATOR_HISTORY_PATH`
    está definido (workflow) — o log persiste na nuvem e este relatório é regenerado ao fecho.

Uso:
    python scripts/run_alerts.py --dry-run     # (com news.enabled: true) gera decisões
    python scripts/post_validate.py            # dias depois: rotula + relatório
"""

from __future__ import annotations

import argparse
import os
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pandas as pd

from investigator.console import force_utf8_stdout
from investigator.triage.postval import (
    dedup_decisions,
    label_decision,
    live_report,
    read_log,
)

REPO = Path(__file__).resolve().parents[1]
MARKET = "SPY"


def _default_paths() -> tuple[str, str]:
    """(log, out) por defeito — na branch partilhada no workflow, senão em data/ e docs/."""
    hist = os.environ.get("INVESTIGATOR_HISTORY_PATH")
    if hist:
        base = Path(hist).parent
        return str(base / "predictions_log.jsonl"), str(base / "live_monitoring.md")
    return (str(REPO / "data" / "predictions_log.jsonl"),
            str(REPO / "docs" / "evaluation" / "live_monitoring.md"))


def _load_all(tickers: list[str], start: str) -> dict[str, pd.Series]:
    """Fechos diários frescos com a cadeia de fallback (funciona nos runners do Actions, onde
    o yfinance bloqueia). Índice normalizado a data — pronto para `searchsorted` de datas."""
    from investigator.market_data.prices import load_close_series

    end = (date.today() + timedelta(days=1)).isoformat()
    out: dict[str, pd.Series] = {}
    for ticker, serie in load_close_series(tickers, start, end).items():
        serie = serie.copy()
        serie.index = pd.to_datetime(serie.index).normalize()
        out[ticker] = serie
    return out


def main() -> int:
    force_utf8_stdout()
    log_def, out_def = _default_paths()
    ap = argparse.ArgumentParser(description="Pós-validação das decisões de triagem (M5.5)")
    ap.add_argument("--log", default=log_def)
    ap.add_argument("--tau", type=float, default=0.02, help="mesmo τ do treino (rótulo primário)")
    ap.add_argument("--horizon", type=int, default=3, help="mesmo h do treino (rótulo primário)")
    ap.add_argument("--out", default=out_def)
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
    tickers = sorted({d["ticker"] for d in decisions} | {MARKET})
    closes = _load_all(tickers, start)
    spy = closes.get(MARKET, pd.Series(dtype="float64"))
    if spy.empty:
        print(f"[aviso] sem preços de {MARKET} (mercado de referência) — decisões ficam pendentes.")

    matured: list[dict] = []
    pendentes = 0
    sem_precos = 0
    for d in decisions:
        serie = closes.get(d["ticker"], pd.Series(dtype="float64"))
        if serie.empty or spy.empty:
            sem_precos += 1
            continue
        label = label_decision(d, serie, spy, tau=args.tau, horizon=args.horizon)
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
        "> Gerado por `scripts/post_validate.py` a partir de `predictions_log.jsonl`.",
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
        "**Notas honestas:** o log de decisões é PERSISTIDO na branch partilhada `alerts-history`",
        "(`predictions_log.jsonl`), por isso o loop acumula na nuvem e este relatório é regenerado",
        "ao fecho pelo workflow do Actions (preços via cadeia de fallback). Decisões de "
        "`--dry-run` também contam (são decisões, não envios); amostras pequenas ⇒ ler como",
        "monitorização, não como avaliação (essa é `evaluation_triage.md`).",
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Decisões: {len(raw)} registadas, {len(decisions)} únicas, "
          f"{len(matured)} maturadas, {pendentes} pendentes.")
    print(f"Escrito: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
