"""Quantificação de incerteza da triagem (RQ4) — bootstrap por cluster (ticker, dia).

ADITIVO (padrão *_ext): NÃO toca em models/ nem em docs/evaluation/evaluation_triage.md.
Reutiliza o protocolo exato de scripts/train_triage.py (StandardScaler+LR, Platt na validação),
reproduz os pontos congelados como sanidade, e ataca a crítica do arguente estatístico:
"0.542 vs 0.538 vs 0.496 a 3 casas decimais, single-seed, sem intervalos, com amostras
correlacionadas (mesmo (ticker,dia) partilha rótulo)".

O bootstrap reamostra CLUSTERS (ticker, dia) do TESTE com reposição (os modelos ficam fixos —
treinados no train, calibrados na val), o que respeita a correlação intra-cluster que o número
de linhas esconde. Reporta IC 95% por família e diferenças emparelhadas (vol−contexto,
vol−full, contexto−full) com P(Δ>0).

Uso:
    python scripts/evaluate_triage_uncertainty.py --dataset <triage_dataset.csv>          # vol/context (rápido, sem SBERT)
    python scripts/evaluate_triage_uncertainty.py --dataset <...> --with-text             # + text/full/gbm (SBERT)
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from investigator.console import force_utf8_stdout
from investigator.triage.features import context_block, text_block
from investigator.triage.model import fit_platt, make_model, scores_of

REPO = Path(__file__).resolve().parents[1]
FROZEN = {"vol": 0.542, "context": 0.538, "text": 0.439, "full": 0.496, "gbm": 0.469}
LABELS = {
    "always": "Alert-always (floor)", "vol": "Volatility-only LR", "context": "Context-only LR",
    "text": "Text-only LR", "full": "Context+text LR", "gbm": "Gradient boosting",
}


def _prauc(y: np.ndarray, s: np.ndarray) -> float:
    return float(average_precision_score(y, s)) if len(np.unique(y)) >= 2 else float("nan")


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Incerteza da triagem (bootstrap por cluster)")
    ap.add_argument("--dataset", default=str(REPO / "data" / "triage_dataset.csv"))
    ap.add_argument("--with-text", action="store_true", help="inclui text/full/gbm (precisa de SBERT)")
    ap.add_argument("--embedder", choices=["sbert", "hashing"], default="sbert")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.dataset)
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    parts = {s: df[df["split"] == s].reset_index(drop=True) for s in ["train", "val", "test"]}
    y = {s: parts[s]["label"].to_numpy() for s in parts}
    test = parts["test"]
    print(f"Dataset: {len(df)} linhas · teste {len(test)} · positivos teste {y['test'].mean():.1%}")

    # ── Blocos de features ────────────────────────────────────────────────────
    families = ["vol", "context"]
    ctx = {s: context_block(parts[s]) for s in parts}          # (X, nomes) — sem SBERT
    blocks = {"context": ctx, "vol": {s: (ctx[s][0][:, :1], ctx[s][1][:1]) for s in parts}}
    if args.with_text:
        families += ["text", "full", "gbm"]
        if args.embedder == "hashing":
            from investigator.historical_kb.embedder import HashingEmbedder
            emb = HashingEmbedder(dim=64)
        else:
            from investigator.historical_kb.embedder import SbertEmbedder
            emb = SbertEmbedder()
        print("A embeder o bloco de texto (SBERT)…" if args.embedder == "sbert" else "hashing…")
        txt = {s: text_block(parts[s], emb) for s in parts}
        blocks["text"] = txt
        blocks["full"] = {s: (np.hstack([ctx[s][0], txt[s][0]]), ctx[s][1] + txt[s][1]) for s in parts}
        blocks["gbm"] = blocks["full"]

    # ── Treinar+calibrar cada família → scores de teste fixos ─────────────────
    s_te: dict[str, np.ndarray] = {}
    for name in families:
        xtr = blocks[name]["train"][0]; xva = blocks[name]["val"][0]; xte = blocks[name]["test"][0]
        model = make_model(name, seed=args.seed)
        model.fit(xtr, y["train"])
        cal = fit_platt(scores_of(model, xva), y["val"], seed=args.seed)
        s_te[name] = cal(scores_of(model, xte))
        pt = _prauc(y["test"], s_te[name])
        tag = f" (congelado {FROZEN[name]:.3f}, Δ {pt - FROZEN[name]:+.3f})" if name in FROZEN else ""
        print(f"  {name:8s} PR-AUC ponto = {pt:.3f}{tag}")

    # ── Bootstrap por cluster (ticker, dia) ───────────────────────────────────
    key = list(zip(test["ticker"].to_numpy(), test["date"].to_numpy(), strict=True))
    groups: dict[object, list[int]] = {}
    for i, k in enumerate(key):
        groups.setdefault(k, []).append(i)
    cluster_rows = [np.asarray(v) for v in groups.values()]
    n_cl = len(cluster_rows)
    rng = np.random.default_rng(args.seed)
    print(f"Bootstrap: {args.boot} reamostragens de {n_cl} clusters (ticker,dia) no teste…")

    boot: dict[str, list[float]] = {f: [] for f in families}
    diffs = {"vol−context": [], "vol−full": [], "context−full": []}
    have_full = "full" in families
    for _ in range(args.boot):
        draw = rng.integers(0, n_cl, size=n_cl)
        idx = np.concatenate([cluster_rows[j] for j in draw])
        yb = y["test"][idx]
        pr = {f: _prauc(yb, s_te[f][idx]) for f in families}
        for f in families:
            boot[f].append(pr[f])
        diffs["vol−context"].append(pr["vol"] - pr["context"])
        if have_full:
            diffs["vol−full"].append(pr["vol"] - pr["full"])
            diffs["context−full"].append(pr["context"] - pr["full"])

    def ci(v: list[float]) -> tuple[float, float, float]:
        a = np.asarray([x for x in v if x == x])  # tira NaN
        return float(np.mean(a)), float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))

    # ── Markdown ──────────────────────────────────────────────────────────────
    out = REPO / "docs" / "evaluation" / "evaluation_triage_uncertainty.md"
    L = [
        "# evaluation_triage_uncertainty.md — Incerteza da triagem (RQ4; bootstrap por cluster)",
        "",
        "> Gerado por `scripts/evaluate_triage_uncertainty.py` (ADITIVO; não altera os congelados).",
        "> Responde à crítica: as PR-AUC da RQ4 vinham single-seed, a 3 casas, sem intervalos e com",
        "> amostras correlacionadas. Aqui os modelos ficam fixos (train+val) e reamostram-se os",
        f"> CLUSTERS (ticker,dia) do teste com reposição ({args.boot}×), IC 95% percentil.",
        "",
        f"- **Teste:** {len(test)} linhas em {n_cl} clusters (ticker,dia); prevalência {y['test'].mean():.3f}.",
        f"- **Gerado:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC · seed {args.seed}"
        f"{' · SBERT' if args.with_text and args.embedder == 'sbert' else ''}.",
        "",
        "| Modelo | PR-AUC (ponto) | IC 95% (bootstrap) |",
        "|---|---|---|",
    ]
    for f in families:
        m, lo, hi = ci(boot[f])
        L.append(f"| {LABELS[f]} | {_prauc(y['test'], s_te[f]):.3f} | [{lo:.3f}, {hi:.3f}] |")
    L += ["", "## Diferenças emparelhadas (o que a comparação decisiva realmente suporta)", "",
          "| Diferença | Δ médio | IC 95% | P(Δ>0) |", "|---|---|---|---|"]
    for name, v in diffs.items():
        if not v:
            continue
        a = np.asarray([x for x in v if x == x])
        m, lo, hi = float(a.mean()), float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))
        L.append(f"| {name} | {m:+.4f} | [{lo:+.4f}, {hi:+.4f}] | {float((a > 0).mean()):.2f} |")
    L += [
        "",
        "**Leitura honesta:** se o IC de `vol−context` contém 0, então volatilidade e contexto são "
        "**estatisticamente indistinguíveis** — a ordenação a 3 casas não era defensável, mas o "
        "veredicto qualitativo (o texto não acrescenta) mantém-se se `vol−full` e `context−full` "
        "ficarem ≥0 com P(Δ>0) alto. Reportado tal como cai.",
    ]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nEscrito: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
