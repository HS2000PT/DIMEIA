"""Treina e avalia os modelos de triagem de materialidade (M2/M3 do ML_PLAN).

Lê o dataset de scripts/build_dataset.py, treina as famílias (always/vol/context/text/full/gbm)
com split temporal, calibra na validação (Platt) e avalia no teste. Grava:
- models/triage_lr.joblib (+ .json) e models/triage_gbm.joblib (+ .json)
- models/triage_context_lr.joblib (+ .json) — variante SÓ-CONTEXTO para a stack leve
  (runner/app na nuvem não têm SBERT; ver src/triage/infer.py)
- docs/evaluation/evaluation_triage.md  (tabela de resultados; NÃO editar à mão)
- thesis/figures/eval_triage_pr.pdf e eval_triage_calibration.pdf

Uso:
    python scripts/train_triage.py                          # SBERT (precisa da stack --ml)
    python scripts/train_triage.py --embedder hashing       # offline (fumo/testes)
    python scripts/train_triage.py --note "SMOKE (corpus 4 semanas)"
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.console import force_utf8_stdout  # noqa: E402
from src.triage.features import assemble  # noqa: E402
from src.triage.model import (  # noqa: E402
    fit_platt,
    make_model,
    metrics,
    precision_at_daily_budget,
    save_bundle,
    scores_of,
)

REPO = Path(__file__).resolve().parents[1]

# Que bloco de features alimenta cada família (ablação por construção).
BLOCK_OF = {"vol": "context", "context": "context", "text": "text", "full": "full", "gbm": "full"}
LABELS = {
    "always": "Alertar-sempre (chão)",
    "vol": "LR só-volatilidade (baseline)",
    "context": "LR só-contexto",
    "text": "LR só-texto",
    "full": "LR contexto+texto (principal)",
    "gbm": "Gradient boosting (contexto+texto)",
}


def _get_embedder(name: str):
    if name == "hashing":
        from src.historical_kb.embedder import HashingEmbedder

        return HashingEmbedder(dim=64)
    from src.historical_kb.embedder import SbertEmbedder

    return SbertEmbedder()


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Treino da triagem de materialidade")
    ap.add_argument("--dataset", default=str(REPO / "data" / "triage_dataset.csv"))
    ap.add_argument("--embedder", choices=["sbert", "hashing"], default="sbert")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--daily-budget", type=int, default=5)
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    rng_tag = f"seed={args.seed}, embedder={args.embedder}"
    df = pd.read_csv(args.dataset)
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    print(f"Dataset: {len(df)} linhas úteis ({rng_tag})")

    embedder = _get_embedder(args.embedder)
    blocks = {}
    for split in ["train", "val", "test"]:
        part = df[df["split"] == split].reset_index(drop=True)
        blocks[split] = (part, assemble(part, embedder))
        pos = part["label"].mean()
        print(f"  {split}: {len(part)} linhas, {pos:.1%} positivos")

    results: dict[str, dict[str, float]] = {}
    bundles: dict[str, tuple] = {}
    y = {s: blocks[s][0]["label"].to_numpy() for s in blocks}
    test_df = blocks["test"][0]

    # Chão: alertar-sempre (score constante 1) — PR-AUC = prevalência do teste.
    always_scores = np.ones(len(test_df))
    results["always"] = {
        **metrics(y["test"], always_scores),
        "p_at_budget": precision_at_daily_budget(
            test_df["date"].to_numpy(), y["test"], always_scores, args.daily_budget
        ),
    }

    for name in ["vol", "context", "text", "full", "gbm"]:
        block = BLOCK_OF[name]
        xtr, names = blocks["train"][1][block]
        xva, _ = blocks["val"][1][block]
        xte, _ = blocks["test"][1][block]
        if name == "vol":  # só a coluna vol20 (posição 0 do bloco de contexto)
            xtr, xva, xte = xtr[:, :1], xva[:, :1], xte[:, :1]
            names = names[:1]
        model = make_model(name, seed=args.seed)
        model.fit(xtr, y["train"])
        cal = fit_platt(scores_of(model, xva), y["val"], seed=args.seed)
        s_te = cal(scores_of(model, xte))
        results[name] = {
            **metrics(y["test"], s_te),
            "p_at_budget": precision_at_daily_budget(
                test_df["date"].to_numpy(), y["test"], s_te, args.daily_budget
            ),
        }
        bundles[name] = (model, cal, names, s_te)
        print(f"  treinado: {name:8s} PR-AUC={results[name]['pr_auc']:.3f}")

    # ── Persistir os dois modelos de produção ────────────────────────────────
    meta_common = {
        "gerado": datetime.now(UTC).isoformat(timespec="seconds"),
        "dataset": str(args.dataset),
        "linhas": {s: int(len(blocks[s][0])) for s in blocks},
        "positivos": {s: float(y[s].mean()) for s in blocks},
        "seed": args.seed,
        "embedder": args.embedder,
        "nota": args.note,
    }
    for name, fname in [("full", "triage_lr.joblib"), ("gbm", "triage_gbm.joblib"),
                        ("context", "triage_context_lr.joblib")]:
        model, cal, names, _ = bundles[name]
        save_bundle(REPO / "models" / fname, model, cal, names,
                    {**meta_common, "modelo": name, "metricas_teste": results[name]})

    # ── Figuras (PR + calibração) ────────────────────────────────────────────
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import precision_recall_curve

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    for name in ["vol", "context", "text", "full", "gbm"]:
        s = bundles[name][3]
        prec, rec, _ = precision_recall_curve(y["test"], s)
        ax.plot(rec, prec, label=f"{LABELS[name]} (AP={results[name]['pr_auc']:.3f})")
    ax.axhline(y["test"].mean(), ls="--", c="grey",
               label=f"Alertar-sempre (prevalência={y['test'].mean():.3f})")
    ax.set_xlabel("Recall"), ax.set_ylabel("Precision")
    ax.set_title("Triagem de materialidade — curvas PR (teste)")
    ax.legend(fontsize=7), fig.tight_layout()
    fig.savefig(REPO / "thesis" / "figures" / "eval_triage_pr.pdf")

    fig2, ax2 = plt.subplots(figsize=(5.4, 4.0))
    s_full = bundles["full"][3]
    bins = np.linspace(0, 1, 11)
    mids, fracs = [], []
    for lo, hi in zip(bins[:-1], bins[1:], strict=True):
        m = (s_full >= lo) & (s_full < hi)
        if m.sum() >= 5:
            mids.append(s_full[m].mean()), fracs.append(y["test"][m].mean())
    ax2.plot([0, 1], [0, 1], "--", c="grey", label="calibração perfeita")
    ax2.plot(mids, fracs, "o-", label="LR contexto+texto (calibrada)")
    ax2.set_xlabel("Probabilidade prevista"), ax2.set_ylabel("Fração observada")
    ax2.set_title("Curva de calibração (teste)")
    ax2.legend(), fig2.tight_layout()
    fig2.savefig(REPO / "thesis" / "figures" / "eval_triage_calibration.pdf")

    # ── Markdown de resultados ───────────────────────────────────────────────
    md = REPO / "docs" / "evaluation" / "evaluation_triage.md"
    lines = [
        "# evaluation_triage.md — Triagem de materialidade (RQ4; reprodutível)",
        "",
        "> Gerado por `scripts/train_triage.py`. **Não editar à mão.**",
        f"> {args.note}" if args.note else "",
        "",
        f"- **Dataset:** `{args.dataset}` — treino {len(blocks['train'][0])} / "
        f"val {len(blocks['val'][0])} / teste {len(blocks['test'][0])} linhas "
        f"(positivos: {y['train'].mean():.1%} / {y['val'].mean():.1%} / {y['test'].mean():.1%}).",
        "- **Protocolo:** split temporal por dias únicos + embargo; calibração Platt na "
        f"validação; {rng_tag}; orçamento de alertas = {args.daily_budget}/dia.",
        f"- **Gerado:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC.",
        "",
        "| Modelo | PR-AUC | ROC-AUC | Brier | Precisão@orçamento |",
        "|---|---|---|---|---|",
    ]
    for name in ["always", "vol", "context", "text", "full", "gbm"]:
        r = results[name]
        lines.append(
            f"| {LABELS[name]} | {r['pr_auc']:.3f} | {r['roc_auc']:.3f} | "
            f"{r['brier']:.3f} | {r['p_at_budget']:.3f} |"
        )
    lines += [
        "",
        "**Leitura honesta:** a comparação decisiva é `full` (e `gbm`) vs `vol` — se o modelo "
        "aprendido não superar a baseline de volatilidade, isso é reportado como está. "
        "PR-AUC do alertar-sempre = prevalência do teste (chão).",
        "",
        "**Caveats:** rótulo = |retorno anormal vs SPY| ≥ τ no horizonte primário (proxy "
        "de materialidade, não julgamento humano); títulos do mesmo (ticker, dia) partilham "
        "o rótulo (clustering — split por dias únicos mitiga fuga, não a correlação); corpus "
        "recente curto ⇒ possível desvio de regime entre blocos (ver positivos por split).",
    ]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nEscrito: {md}")
    print("Figuras: thesis/figures/eval_triage_pr.pdf + eval_triage_calibration.pdf")
    print("Modelos: models/triage_lr.joblib + triage_gbm.joblib + triage_context_lr.joblib")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
