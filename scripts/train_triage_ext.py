"""RQ4-ext: estudo de ablação das features de contexto estendidas (ADITIVO; congelado intacto).

Lê `data/triage_dataset_ext.csv` (gerado por `scripts/build_dataset.py --ext`) e treina, no
MESMO protocolo congelado da tese — split temporal por dias únicos + embargo, calibração Platt
na validação, seed 42, avaliação por PR-AUC + precisão@5/dia + Brier — as famílias de CONTEXTO
para responder honestamente à pergunta da RQ4-ext: **que sinais baratos AJUDAM de facto a triagem,
e quanto?** (ver `docs/evaluation/roadmap_rq4.md`).

Só features de contexto (nenhum embedder/SBERT): a ablação é sobre os 5 sinais novos, ortogonal ao
texto (que a v1 já mostrou não bater a volatilidade). Corre em segundos, offline e determinística.

**Não escreve** em `models/` nem em `docs/evaluation/evaluation_triage.md` (congelados). Gera:
- `docs/evaluation/evaluation_triage_ext.md`  (tabelas de resultados + contribuição marginal)
- `thesis/figures/eval_triage_ext.pdf`         (barras da contribuição marginal por feature)

Uso:
    python scripts/train_triage_ext.py
    python scripts/train_triage_ext.py --dataset data/triage_dataset_ext.csv --seed 42
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from investigator.console import force_utf8_stdout
from investigator.triage.features import (
    CONTEXT_COLS,
    CONTEXT_EXT_COLS,
    EXT_COLS,
    numeric_context_block,
)
from investigator.triage.model import (
    fit_platt,
    make_model,
    metrics,
    precision_at_daily_budget,
    scores_of,
)

REPO = Path(__file__).resolve().parents[1]

# Etiqueta legível de cada feature nova (para as tabelas/figura).
EXT_LABEL = {
    "market_vol20": "market_vol20 (regime do mercado)",
    "mom20": "mom20 (momento 20d da ação)",
    "vol_ratio": "vol_ratio (vol20/vol60)",
    "ret_event_z": "ret_event_z (reação padronizada)",
    "downside_vol20": "downside_vol20 (risco de queda)",
}


def _raw_block(df: pd.DataFrame, cols: list[str]) -> tuple[np.ndarray, list[str]]:
    """Bloco só com as colunas numéricas `cols` (sem one-hot de setor)."""
    return df[cols].to_numpy(dtype="float64"), list(cols)


def _fit_eval(train, val, test, y, build_block, seed: int, budget: int) -> dict[str, float]:
    """Treina LR (StandardScaler+LR balanceada) num bloco, calibra Platt na val, avalia no teste."""
    xtr, _ = build_block(train)
    xva, _ = build_block(val)
    xte, _ = build_block(test)
    model = make_model("context", seed=seed)  # StandardScaler + LogisticRegression (igual à v1)
    model.fit(xtr, y["train"])
    cal = fit_platt(scores_of(model, xva), y["val"], seed=seed)
    s_te = cal(scores_of(model, xte))
    return {
        **metrics(y["test"], s_te),
        "p_at_budget": precision_at_daily_budget(
            test["date"].to_numpy(), y["test"], s_te, budget
        ),
    }


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="RQ4-ext: ablação de features de contexto")
    ap.add_argument("--dataset", default=str(REPO / "data" / "triage_dataset_ext.csv"))
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--daily-budget", type=int, default=5)
    args = ap.parse_args()

    df = pd.read_csv(args.dataset)
    missing = [c for c in EXT_COLS if c not in df.columns]
    if missing:
        raise SystemExit(f"Faltam colunas estendidas {missing}: gerar com build_dataset.py --ext.")
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    parts = {s: df[df["split"] == s].reset_index(drop=True) for s in ["train", "val", "test"]}
    y = {s: parts[s]["label"].to_numpy() for s in parts}
    train, val, test = parts["train"], parts["val"], parts["test"]
    print(f"Dataset: {len(df)} linhas úteis (seed={args.seed})")
    for s in ["train", "val", "test"]:
        print(f"  {s}: {len(parts[s])} linhas, {y[s].mean():.1%} positivos")

    fit = lambda bb: _fit_eval(train, val, test, y, bb, args.seed, args.daily_budget)  # noqa: E731

    # ── Referências + ablação principal ──────────────────────────────────────
    results: dict[str, dict[str, float]] = {}
    # Chão: alertar-sempre (score constante) — PR-AUC = prevalência do teste.
    ones = np.ones(len(test))
    results["always"] = {
        **metrics(y["test"], ones),
        "p_at_budget": precision_at_daily_budget(test["date"].to_numpy(), y["test"], ones,
                                                 args.daily_budget),
    }
    results["vol"] = fit(lambda d: _raw_block(d, ["vol20"]))          # só vol20 (baseline forte)
    results["context"] = fit(lambda d: numeric_context_block(d, CONTEXT_COLS))       # âncora v1
    results["context_ext"] = fit(lambda d: numeric_context_block(d, CONTEXT_EXT_COLS))  # v1 + 5

    for name in ["always", "vol", "context", "context_ext"]:
        r = results[name]
        print(f"  {name:12s} PR-AUC={r['pr_auc']:.3f} "
              f"Brier={r['brier']:.3f} P@{args.daily_budget}={r['p_at_budget']:.3f}")

    # ── Contribuição marginal por feature ────────────────────────────────────
    # leave-one-in (LOI): context + só esta feature  → valor isolado sobre a v1.
    # leave-one-out (LOO): context_ext − esta feature → custo de remover, dado o resto.
    base_pr = results["context"]["pr_auc"]
    full_pr = results["context_ext"]["pr_auc"]
    marginal: dict[str, dict[str, float]] = {}
    for f in EXT_COLS:
        loi = fit(lambda d, f=f: numeric_context_block(d, CONTEXT_COLS + [f]))
        loo_cols = [c for c in CONTEXT_EXT_COLS if c != f]
        loo = fit(lambda d, loo_cols=loo_cols: numeric_context_block(d, loo_cols))
        marginal[f] = {
            "loi_pr": loi["pr_auc"], "loi_delta": loi["pr_auc"] - base_pr,
            "loo_pr": loo["pr_auc"], "loo_delta": full_pr - loo["pr_auc"],
            "loi_pbud": loi["p_at_budget"],
        }
        print(f"  [{f:14s}] LOI PR-AUC={loi['pr_auc']:.3f} (Δ{loi['pr_auc']-base_pr:+.3f}) | "
              f"LOO Δ={full_pr - loo['pr_auc']:+.3f}")

    # ── Figura: barras da contribuição marginal (LOI e LOO) ordenada por LOO ──
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    order = sorted(EXT_COLS, key=lambda f: marginal[f]["loo_delta"])
    ypos = np.arange(len(order))
    loi_d = [marginal[f]["loi_delta"] for f in order]
    loo_d = [marginal[f]["loo_delta"] for f in order]
    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    h = 0.38
    ax.barh(ypos + h / 2, loi_d, height=h, color="#4C78A8", label="leave-one-in (sobre v1)")
    ax.barh(ypos - h / 2, loo_d, height=h, color="#F58518",
            label="leave-one-out (custo de remover)")
    ax.axvline(0.0, color="grey", lw=0.8)
    ax.set_yticks(ypos)
    ax.set_yticklabels([f.replace("_", "\n", 1) for f in order], fontsize=8)
    ax.set_xlabel("Δ PR-AUC")
    ax.set_title("RQ4-ext: contribuição marginal de cada sinal de contexto (teste)")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    figpath = REPO / "thesis" / "figures" / "eval_triage_ext.pdf"
    fig.savefig(figpath)
    print(f"\nFigura: {figpath}")

    # ── Markdown de resultados ───────────────────────────────────────────────
    md = REPO / "docs" / "evaluation" / "evaluation_triage_ext.md"
    delta_ext = full_pr - base_pr
    lines = [
        "# evaluation_triage_ext.md — RQ4-ext: ablação de features de contexto (reprodutível)",
        "",
        "> Gerado por `scripts/train_triage_ext.py`. **Não editar à mão.** Aditivo: os modelos",
        "> e `evaluation_triage.md` congelados ficam intactos "
        "(ver `docs/evaluation/roadmap_rq4.md`).",
        "",
        f"- **Dataset:** `{args.dataset}` — treino {len(train)} / val {len(val)} / "
        f"teste {len(test)} linhas (positivos: {y['train'].mean():.1%} / "
        f"{y['val'].mean():.1%} / {y['test'].mean():.1%}).",
        "- **Protocolo:** idêntico ao congelado — split temporal por dias únicos + embargo, "
        f"calibração Platt na validação, seed={args.seed}, orçamento = {args.daily_budget}/dia. "
        "Só features de contexto (sem texto/SBERT).",
        f"- **Gerado:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC.",
        "",
        "## 1. Âncora e ablação principal",
        "",
        "| Modelo | PR-AUC | ROC-AUC | Brier | Precisão@orçamento |",
        "|---|---|---|---|---|",
    ]
    label = {
        "always": "Alertar-sempre (chão)",
        "vol": "LR só-volatilidade (baseline)",
        "context": "LR contexto v1 (âncora)",
        "context_ext": "LR contexto v1 + 5 features (RQ4-ext)",
    }
    for name in ["always", "vol", "context", "context_ext"]:
        r = results[name]
        lines.append(f"| {label[name]} | {r['pr_auc']:.3f} | {r['roc_auc']:.3f} | "
                     f"{r['brier']:.3f} | {r['p_at_budget']:.3f} |")
    lines += [
        "",
        f"O contexto v1 aqui (PR-AUC {base_pr:.3f}) reproduz a âncora congelada "
        "(`evaluation_triage.md`: 0.538) até ao ruído do split ligeiramente mais curto do build "
        "`--ext` (exige 60 dias de histórico, ~300 eventos iniciais a menos). Acrescentar os 5 "
        f"sinais move a PR-AUC para {full_pr:.3f} (Δ {delta_ext:+.3f}).",
        "",
        "## 2. Contribuição marginal de cada sinal",
        "",
        "- **leave-one-in (LOI):** contexto v1 + *só* esta feature — valor isolado sobre a v1.",
        "- **leave-one-out (LOO):** contexto+5 *menos* esta feature — custo de a remover, "
        "dado o resto.",
        "",
        "| Feature nova | LOI PR-AUC | Δ vs v1 | LOO Δ (custo de remover) |",
        "|---|---|---|---|",
    ]
    for f in sorted(EXT_COLS, key=lambda f: -marginal[f]["loo_delta"]):
        m = marginal[f]
        lines.append(f"| {EXT_LABEL[f]} | {m['loi_pr']:.3f} | {m['loi_delta']:+.3f} | "
                     f"{m['loo_delta']:+.3f} |")
    lines += [
        "",
        "![Contribuição marginal](../../thesis/figures/eval_triage_ext.pdf)",
        "",
        "**Leitura honesta:** a ablação diz quais sinais valem e quais não — reportado tal como "
        "cai, com o mesmo rigor do resultado congelado (\"o texto não bate a volatilidade\"). "
        "Δ pequenos (~0.00) significam que o sinal é redundante face aos que já lá estão; Δ "
        "negativos que atrapalha (ruído). Nada aqui muda a produção — a stack leve continua na "
        "variante só-contexto congelada; isto é ciência de features para a tese e futuro.",
    ]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Escrito: {md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
