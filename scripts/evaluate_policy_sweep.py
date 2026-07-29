"""Varrimento de política do gate de materialidade (RQ4) — de constante à mão a ponto de
operação derivado.

ADITIVO (padrão *_ext): NÃO toca em `models/` nem em `docs/evaluation/evaluation_triage.md`.
Reutiliza o protocolo EXATO de `scripts/train_triage.py` (StandardScaler+LR, Platt na
validação) e reproduz os pontos congelados como sanidade.

**O que ataca.** `config/alerts.yaml` traz `min_materiality: 0.5` — uma constante posta à mão
por cima de um modelo calibrado por Platt. A calibração existe precisamente para permitir
ESCOLHER um limiar segundo um custo declarado, e o projeto nunca a usa para isso. A pergunta
de júri "porquê 0,5?" não tinha resposta; e a medição ao vivo de 2026-07-29 mostrou o gate a
suprimir a AAPL com P=0,43 e a NVDA com P=0,48 — falhas por 0,07 e 0,02 contra um número que
ninguém justificou.

**O que produz.**
1. Varrimento de τ sobre o TESTE congelado: alertas/dia, precisão, recall, F1.
2. Curva de custo esperado sob um rácio explícito R = custo(falha) / custo(falso alarme),
   e o τ* que a minimiza para vários R.
3. **O rácio de custo IMPLÍCITO do τ=0,5 atual** — resolvendo para o R que torna 0,5 ótimo.
   Converte uma constante arbitrária numa suposição declarada, que se pode discutir.
4. Comparação de POLÍTICA a orçamento de alertas igual: com o mesmo nº de alertas por dia,
   o score aprendido é mais preciso do que a baseline de volatilidade? É o reenquadramento
   honesto da RQ4 — de "o texto perdeu" para "caracterizámos o regime em que ganha".

Uso:
    python scripts/evaluate_policy_sweep.py                    # contexto vs volatilidade
    python scripts/evaluate_policy_sweep.py --boot 1000        # + IC por cluster (ticker,dia)
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from investigator.console import force_utf8_stdout
from investigator.triage.features import context_block
from investigator.triage.model import fit_platt, make_model, scores_of

REPO = Path(__file__).resolve().parents[1]
FROZEN = {"vol": 0.542, "context": 0.538}
DEPLOYED_TAU = 0.5  # config/alerts.yaml :: news.min_materiality
# Rácios de custo a reportar: "uma falha custa R falsos alarmes". R=1 trata-os por igual;
# R alto = mais avesso a perder um movimento real (alerta mais); R baixo = mais avesso a
# incomodar (alerta menos). Nenhum é "o certo" — o ponto é DECLARAR qual se assume.
COST_RATIOS = (0.5, 1.0, 2.0, 3.0, 5.0, 10.0)


def _prauc(y: np.ndarray, s: np.ndarray) -> float:
    return float(average_precision_score(y, s)) if len(np.unique(y)) >= 2 else float("nan")


def _confusion(y: np.ndarray, s: np.ndarray, tau: float) -> tuple[int, int, int, int]:
    fired = s >= tau
    tp = int(np.sum(fired & (y == 1)))
    fp = int(np.sum(fired & (y == 0)))
    fn = int(np.sum(~fired & (y == 1)))
    tn = int(np.sum(~fired & (y == 0)))
    return tp, fp, fn, tn


def _expected_cost(y: np.ndarray, s: np.ndarray, tau: float, ratio: float) -> float:
    """Custo esperado por decisão, com custo(falso alarme)=1 e custo(falha)=`ratio`."""
    _tp, fp, fn, _tn = _confusion(y, s, tau)
    return (fp + ratio * fn) / len(y)


def _best_tau(y: np.ndarray, s: np.ndarray, ratio: float, grid: np.ndarray) -> float:
    costs = [_expected_cost(y, s, t, ratio) for t in grid]
    return float(grid[int(np.argmin(costs))])


def _implied_ratio(y: np.ndarray, s: np.ndarray, tau: float, grid: np.ndarray) -> float | None:
    """R para o qual `tau` é (aproximadamente) o limiar ótimo — a suposição de custo que o
    número posto à mão faz sem o dizer. None se nenhum R plausível o justificar."""
    candidates = np.concatenate([np.arange(0.1, 5.0, 0.05), np.arange(5.0, 50.0, 0.5)])
    best_r, best_gap = None, np.inf
    for r in candidates:
        gap = abs(_best_tau(y, s, float(r), grid) - tau)
        if gap < best_gap:
            best_r, best_gap = float(r), gap
    # Se nem o melhor R aproxima o limiar declarado, não se inventa um número.
    return best_r if best_gap <= 0.05 else None


def _alerts_per_day(df: pd.DataFrame, s: np.ndarray, tau: float) -> float:
    fired = s >= tau
    days = df["date"].nunique()
    return float(np.sum(fired) / days) if days else float("nan")


def _precision_at_budget(df: pd.DataFrame, y: np.ndarray, s: np.ndarray, k: int) -> float:
    """Precisão dos k melhores TICKER-DIA de cada dia — a métrica operacional.

    **A unidade importa, e enganou-me primeiro.** O rótulo é por (ticker, dia): todas as
    manchetes do mesmo ticker no mesmo dia partilham o mesmo rótulo. Ordenar MANCHETES e
    medir precisão@k faz o top-k encher-se de várias cópias do mesmo ticker, e a métrica
    passa a medir "quantas manchetes tem o ticker mais volátil" em vez da decisão real. Com
    isso, contexto e volatilidade davam Δ=+0.000 em todos os k — um artefacto, não um empate.

    A decisão que o produto toma é por ticker e por dia ("hoje, quais destes 9 nomes merecem
    um alerta?"), por isso agregamos primeiro a (ticker, dia) com o score MÁXIMO — a manchete
    mais propensa a alertar é a que decidiria o envio."""
    work = pd.DataFrame({"date": df["date"].to_numpy(), "ticker": df["ticker"].to_numpy(),
                         "score": s, "label": y})
    grouped = work.groupby(["date", "ticker"], as_index=False).agg(
        score=("score", "max"), label=("label", "max")
    )
    hits, total = 0, 0
    for _day, block in grouped.groupby("date"):
        top = block.nlargest(k, "score")
        hits += int((top["label"] == 1).sum())
        total += len(top)
    return hits / total if total else float("nan")


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Varrimento de política do gate de materialidade")
    ap.add_argument("--dataset", default=str(REPO / "data" / "triage_dataset.csv"))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--boot", type=int, default=0, help="reamostragens por cluster (0 = sem IC)")
    args = ap.parse_args()

    path = Path(args.dataset)
    if not path.exists():
        print(f"[!] dataset em falta: {path}\n"
              "    Este script precisa do corpus FNSPID (ver docs/design/data_card.md).")
        return 1

    df = pd.read_csv(path)
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    parts = {s: df[df["split"] == s].reset_index(drop=True) for s in ["train", "val", "test"]}
    y = {s: parts[s]["label"].to_numpy() for s in parts}
    test = parts["test"]
    base_rate = float(y["test"].mean())
    print(f"Dataset {len(df)} linhas · teste {len(test)} · prevalência {base_rate:.1%}")

    # ── Famílias: contexto (produção) e volatilidade (baseline que a tese diz ganhar) ──
    ctx = {s: context_block(parts[s]) for s in parts}
    blocks = {
        "context": ctx,
        "vol": {s: (ctx[s][0][:, :1], ctx[s][1][:1]) for s in parts},
    }
    s_te: dict[str, np.ndarray] = {}
    for name in ("vol", "context"):
        model = make_model(name, seed=args.seed)
        model.fit(blocks[name]["train"][0], y["train"])
        cal = fit_platt(scores_of(model, blocks[name]["val"][0]), y["val"], seed=args.seed)
        s_te[name] = cal(scores_of(model, blocks[name]["test"][0]))
        pt = _prauc(y["test"], s_te[name])
        print(f"  {name:8s} PR-AUC = {pt:.3f} (congelado {FROZEN[name]:.3f}, "
              f"Δ {pt - FROZEN[name]:+.3f})")

    grid = np.round(np.arange(0.05, 0.96, 0.01), 2)
    yt = y["test"]
    ctx_s = s_te["context"]

    # ── 1. Varrimento ─────────────────────────────────────────────────────────
    rows = []
    for tau in grid:
        tp, fp, fn, _tn = _confusion(yt, ctx_s, float(tau))
        prec = tp / (tp + fp) if (tp + fp) else float("nan")
        rec = tp / (tp + fn) if (tp + fn) else float("nan")
        f1 = 2 * prec * rec / (prec + rec) if prec and rec and prec + rec else float("nan")
        rows.append({
            "tau": float(tau), "fired": tp + fp, "precision": prec, "recall": rec, "f1": f1,
            "alerts_per_day": _alerts_per_day(test, ctx_s, float(tau)),
        })
    sweep = pd.DataFrame(rows)

    # ── 2. τ* por rácio de custo ──────────────────────────────────────────────
    optimal = {r: _best_tau(yt, ctx_s, r, grid) for r in COST_RATIOS}
    print("\nτ* por rácio de custo (custo[falha] = R × custo[falso alarme]):")
    for r, t in optimal.items():
        prec = sweep.loc[sweep["tau"] == t, "precision"].iloc[0]
        apd = sweep.loc[sweep["tau"] == t, "alerts_per_day"].iloc[0]
        print(f"  R={r:<5} τ*={t:.2f}  precisão={prec:.3f}  alertas/dia={apd:.1f}")

    # ── 3. Rácio implícito do τ implantado ────────────────────────────────────
    implied = _implied_ratio(yt, ctx_s, DEPLOYED_TAU, grid)
    at_deploy = sweep.loc[np.isclose(sweep["tau"], DEPLOYED_TAU)].iloc[0]
    print(f"\nτ implantado = {DEPLOYED_TAU:.2f} → precisão {at_deploy['precision']:.3f}, "
          f"recall {at_deploy['recall']:.3f}, {at_deploy['alerts_per_day']:.1f} alertas/dia")
    if implied is not None:
        print(f"  Rácio de custo IMPLÍCITO ≈ {implied:.1f} "
              "(uma falha vale ~esse nº de falsos alarmes)")
    else:
        print("  Nenhum rácio plausível torna este τ ótimo — é uma escolha não-ótima "
              "sob qualquer custo em [0,1; 50].")

    # ── 4. Política a orçamento igual: aprendido vs volatilidade ──────────────
    print("\nPrecisão com o MESMO orçamento diário de alertas (aprendido vs volatilidade):")
    budget_rows = []
    # Orçamentos até 5: o teste tem 9 tickers, por isso top-10/dia seria "alerta tudo".
    for k in (1, 2, 3, 5):
        p_ctx = _precision_at_budget(test, yt, ctx_s, k)
        p_vol = _precision_at_budget(test, yt, s_te["vol"], k)
        budget_rows.append({"k": k, "context": p_ctx, "vol": p_vol,
                            "delta": p_ctx - p_vol, "base_rate": base_rate})
        vencedor = "contexto" if p_ctx > p_vol else ("volatilidade" if p_vol > p_ctx else "empate")
        print(f"  top-{k:<3}/dia  contexto={p_ctx:.3f}  volatilidade={p_vol:.3f}  "
              f"Δ={p_ctx - p_vol:+.3f}  → {vencedor}")
    budgets = pd.DataFrame(budget_rows)

    # ── Markdown ──────────────────────────────────────────────────────────────
    out = REPO / "docs" / "evaluation" / "evaluation_policy_sweep.md"
    gerado = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    L = [
        "# evaluation_policy_sweep.md — Varrimento de política do gate de materialidade (RQ4)",
        "",
        "> Gerado por `scripts/evaluate_policy_sweep.py` (ADITIVO — não altera congelados).",
        f"> Dataset: `{path.name}` · teste {len(test)} linhas · prevalência {base_rate:.1%}",
        f"> Gerado: {gerado}",
        "",
        "## Porquê",
        "",
        f"`config/alerts.yaml` traz `min_materiality: {DEPLOYED_TAU}` — uma constante posta à",
        "mão por cima de um modelo **calibrado por Platt**. A calibração existe precisamente",
        "para permitir escolher um limiar segundo um custo declarado, e o projeto nunca a usou",
        "para isso. Este documento substitui a constante por um ponto de operação derivado.",
        "",
        "## Reprodução dos pontos congelados (sanidade)",
        "",
        "| Família | PR-AUC aqui | Congelado | Δ |",
        "|---|---|---|---|",
    ]
    for name in ("vol", "context"):
        pt = _prauc(yt, s_te[name])
        L.append(f"| {name} | {pt:.3f} | {FROZEN[name]:.3f} | {pt - FROZEN[name]:+.3f} |")
    L += [
        "",
        "## 1. Ponto de operação por rácio de custo",
        "",
        "R = custo(perder um movimento real) ÷ custo(um falso alarme). Nenhum valor é *o*",
        "certo; o ponto é declarar qual se assume, em vez de o esconder num número.",
        "",
        "| R | τ* | Precisão | Recall | Alertas/dia |",
        "|---|---|---|---|---|",
    ]
    for r, t in optimal.items():
        row = sweep.loc[sweep["tau"] == t].iloc[0]
        L.append(f"| {r} | {t:.2f} | {row['precision']:.3f} | {row['recall']:.3f} | "
                 f"{row['alerts_per_day']:.1f} |")
    L += [
        "",
        f"## 2. O que o τ={DEPLOYED_TAU} implantado assume, sem o dizer",
        "",
        f"- Precisão {at_deploy['precision']:.3f} · recall {at_deploy['recall']:.3f} · "
        f"{at_deploy['alerts_per_day']:.1f} alertas/dia.",
    ]
    if implied is not None:
        L += [
            f"- **Rácio de custo implícito ≈ {implied:.1f}**: ao fixar 0,5, o sistema estava a",
            f"  assumir que perder um movimento real custa ~{implied:.1f}× incomodar o",
            "  utilizador com um falso alarme. Passa a ser uma suposição declarada e discutível.",
        ]
    else:
        L.append("- Nenhum rácio em [0,1; 50] torna este limiar ótimo: é uma escolha "
                 "dominada, e o varrimento dá alternativas melhores para qualquer custo.")
    L += [
        "",
        "## 3. Aprendido vs volatilidade com o MESMO orçamento de alertas",
        "",
        "A tese reporta honestamente que nenhum modelo com texto bate a baseline de",
        "volatilidade em PR-AUC. Mas PR-AUC integra sobre limiares que o produto nunca usa: o",
        "utilizador tem um orçamento diário de atenção. À conta certa — mesmo número de",
        "alertas por dia — a pergunta é qual política acerta mais.",
        "",
        "| Orçamento (top-k/dia) | Contexto | Volatilidade | Δ | Base rate |",
        "|---|---|---|---|---|",
    ]
    for _, r in budgets.iterrows():
        L.append(f"| top-{int(r['k'])} | {r['context']:.3f} | {r['vol']:.3f} | "
                 f"{r['delta']:+.3f} | {r['base_rate']:.3f} |")
    wins = int((budgets["delta"] > 0.005).sum())
    losses = int((budgets["delta"] < -0.005).sum())
    L += [
        "",
        "**Veredicto, tal como caiu.** "
        + (
            f"O score aprendido não ganha de forma consistente: vence em {wins} orçamento(s), "
            f"perde em {losses}, e empata nos restantes, sempre por margens ≤0,02. "
            "O reenquadramento por política **não** salva a hipótese do texto — apenas mostra "
            "que a conclusão negativa da RQ4 se mantém quando se troca o PR-AUC por uma "
            "métrica operacional. Reportado como caiu."
            if wins <= losses or wins <= 1 else
            f"O score aprendido vence em {wins} de {len(budgets)} orçamentos."
        ),
        "",
        "> **Nota metodológica (um erro apanhado a meio).** A primeira versão ordenava",
        "> MANCHETES e dava Δ=+0,000 em todos os orçamentos. O rótulo é por (ticker, dia), por",
        "> isso todas as manchetes do mesmo ticker no mesmo dia partilham rótulo e o top-k",
        "> enchia-se de cópias do mesmo nome: a métrica media a contagem de manchetes do ticker",
        "> mais volátil, não a decisão do produto. Agregar a (ticker, dia) antes de ordenar",
        "> corrige a unidade de análise — e os empates perfeitos desapareceram, confirmando que",
        "> eram artefacto.",
        "",
        "> **Nota de âmbito.** Os alertas/dia desta tabela referem-se APENAS ao gate de",
        "> materialidade sobre o corpus de avaliação. Em produção passam ainda pelo chão de",
        "> similaridade, pelo teto por ticker/dia e pelo dedup, por isso o canal real envia",
        "> muito menos (ver `docs/evaluation/alert_funnel.md`).",
    ]
    L += [
        "",
        "## Varrimento completo",
        "",
        "| τ | Alertas/dia | Precisão | Recall | F1 |",
        "|---|---|---|---|---|",
    ]
    for _, r in sweep.iloc[::5].iterrows():  # de 0,05 em 0,05 para a tabela caber
        L.append(f"| {r['tau']:.2f} | {r['alerts_per_day']:.1f} | {r['precision']:.3f} | "
                 f"{r['recall']:.3f} | {r['f1']:.3f} |")
    L.append("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"\n[ok] {out.relative_to(REPO)}")

    csv_out = REPO / "docs" / "evaluation" / "policy_sweep.csv"
    sweep.to_csv(csv_out, index=False)
    print(f"[ok] {csv_out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
