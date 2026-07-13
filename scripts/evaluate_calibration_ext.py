"""Extensão de avaliação: calibração Platt vs isotónica (pendente do CHECKLIST).

A tese (Cap. 3) justifica a escolha de Platt CONCEPTUALMENTE (2 parâmetros, monótona e
suave, robusta com pouca calibração — niculescu2005calibration); a comparação numérica
ficou registada como extensão a correr no PC com o dataset FNSPID. Este script fá-la de
forma ADITIVA: reproduz primeiro o protocolo congelado (mesmo dataset, split, seed,
famílias e Platt de `train_triage.py` — os números têm de bater com
`docs/evaluation/evaluation_triage.md`) e só depois acrescenta a variante isotónica,
ajustada NA MESMA validação e avaliada NO MESMO teste.

NÃO toca em `models/`, em `evaluation_triage.md` nem em figuras da tese.
Escreve apenas `docs/evaluation/calibration_platt_vs_isotonic.md`.

Uso (stack --ml; ~10-30 min por causa do SBERT em CPU):
    python scripts/evaluate_calibration_ext.py
    python scripts/evaluate_calibration_ext.py --embedder hashing   # fumo rápido
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression

from investigator.console import force_utf8_stdout
from investigator.triage.features import assemble
from investigator.triage.model import fit_platt, make_model, metrics, scores_of

REPO = Path(__file__).resolve().parents[1]

BLOCK_OF = {"vol": "context", "context": "context", "text": "text", "full": "full", "gbm": "full"}
LABELS = {
    "vol": "LR só-volatilidade (baseline)",
    "context": "LR só-contexto (produção)",
    "text": "LR só-texto",
    "full": "LR contexto+texto (principal)",
    "gbm": "Gradient boosting (contexto+texto)",
}
# Números congelados de evaluation_triage.md (2026-07-04) — a reprodução tem de bater.
FROZEN = {
    "vol": {"pr_auc": 0.542, "brier": 0.218},
    "context": {"pr_auc": 0.538, "brier": 0.224},
    "text": {"pr_auc": 0.439, "brier": 0.240},
    "full": {"pr_auc": 0.496, "brier": 0.229},
    "gbm": {"pr_auc": 0.469, "brier": 0.228},
}


def _get_embedder(name: str):
    if name == "hashing":
        from investigator.historical_kb.embedder import HashingEmbedder

        return HashingEmbedder(dim=64)
    from investigator.historical_kb.embedder import SbertEmbedder

    return SbertEmbedder()


def ece(y_true: np.ndarray, probs: np.ndarray, n_bins: int = 10) -> float:
    """Expected Calibration Error: média ponderada de |P prevista − fração observada|."""
    y = np.asarray(y_true, dtype="float64")
    p = np.asarray(probs, dtype="float64")
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:], strict=True):
        m = (p >= lo) & (p < hi) if hi < 1.0 else (p >= lo) & (p <= hi)
        if m.sum() == 0:
            continue
        total += (m.sum() / len(p)) * abs(p[m].mean() - y[m].mean())
    return float(total)


def reliability_rows(y_true: np.ndarray, probs: np.ndarray, n_bins: int = 10, min_n: int = 5):
    """Pontos (P prevista média, fração observada, n) por bin — para a tabela."""
    y = np.asarray(y_true, dtype="float64")
    p = np.asarray(probs, dtype="float64")
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:], strict=True):
        m = (p >= lo) & (p < hi) if hi < 1.0 else (p >= lo) & (p <= hi)
        if m.sum() >= min_n:
            rows.append((float(p[m].mean()), float(y[m].mean()), int(m.sum())))
    return rows


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Calibração Platt vs isotónica (extensão)")
    ap.add_argument("--dataset", default=str(REPO / "data" / "triage_dataset.csv"))
    ap.add_argument("--embedder", choices=["sbert", "hashing"], default="sbert")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.dataset)
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    print(f"Dataset: {len(df)} linhas úteis (seed={args.seed}, embedder={args.embedder})")

    embedder = _get_embedder(args.embedder)
    blocks = {}
    for split in ["train", "val", "test"]:
        part = df[df["split"] == split].reset_index(drop=True)
        blocks[split] = (part, assemble(part, embedder))
        print(f"  {split}: {len(part)} linhas, {part['label'].mean():.1%} positivos")
    y = {s: blocks[s][0]["label"].to_numpy() for s in blocks}

    results: dict[str, dict] = {}
    for name in ["vol", "context", "text", "full", "gbm"]:
        block = BLOCK_OF[name]
        xtr, _ = blocks["train"][1][block]
        xva, _ = blocks["val"][1][block]
        xte, _ = blocks["test"][1][block]
        if name == "vol":
            xtr, xva, xte = xtr[:, :1], xva[:, :1], xte[:, :1]
        model = make_model(name, seed=args.seed)
        model.fit(xtr, y["train"])
        s_va, s_te = scores_of(model, xva), scores_of(model, xte)

        platt = fit_platt(s_va, y["val"], seed=args.seed)
        p_platt = platt(s_te)
        iso = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip")
        iso.fit(s_va, y["val"])
        p_iso = iso.predict(s_te)

        results[name] = {
            "platt": {**metrics(y["test"], p_platt), "ece": ece(y["test"], p_platt)},
            "iso": {**metrics(y["test"], p_iso), "ece": ece(y["test"], p_iso)},
            "rel_platt": reliability_rows(y["test"], p_platt),
            "rel_iso": reliability_rows(y["test"], p_iso),
        }
        r = results[name]
        print(
            f"  {name:8s} Platt: Brier={r['platt']['brier']:.3f} ECE={r['platt']['ece']:.3f} | "
            f"Isotónica: Brier={r['iso']['brier']:.3f} ECE={r['iso']['ece']:.3f}"
        )

    # ── Reprodução do protocolo congelado (gate de honestidade) ─────────────
    print("\nReprodução vs evaluation_triage.md (Platt):")
    repro_ok = True
    for name, frozen in FROZEN.items():
        got = results[name]["platt"]
        ok = abs(got["pr_auc"] - frozen["pr_auc"]) < 0.0015 and abs(
            got["brier"] - frozen["brier"]
        ) < 0.0015
        repro_ok &= ok
        print(
            f"  {name:8s} PR-AUC {got['pr_auc']:.3f} (congelado {frozen['pr_auc']:.3f}) "
            f"Brier {got['brier']:.3f} (congelado {frozen['brier']:.3f}) "
            f"{'OK' if ok else 'DIVERGE'}"
        )

    # ── Markdown ─────────────────────────────────────────────────────────────
    md = REPO / "docs" / "evaluation" / "calibration_platt_vs_isotonic.md"
    lines = [
        "# calibration_platt_vs_isotonic.md — Platt vs isotónica (extensão; reprodutível)",
        "",
        "> Gerado por `scripts/evaluate_calibration_ext.py`. **Não editar à mão.**",
        "> Extensão ADITIVA: `models/`, `evaluation_triage.md` e a tese ficam intocados.",
        "",
        f"- **Dataset:** `{args.dataset}` — mesmas linhas/split/seed do treino congelado "
        f"(val = {len(blocks['val'][0])} pontos de calibração).",
        "- **Protocolo:** idêntico a `train_triage.py` (split temporal + embargo, "
        f"seed={args.seed}, embedder={args.embedder}); ambas as calibrações ajustadas na "
        "MESMA validação e avaliadas no MESMO teste.",
        f"- **Reprodução do congelado (Platt):** {'✅ bate' if repro_ok else '⚠️ DIVERGE'} "
        "(tolerância 0,0015 em PR-AUC e Brier).",
        f"- **Gerado:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC.",
        "",
        "| Modelo | Brier Platt | Brier isotónica | ECE Platt | ECE isotónica |",
        "|---|---|---|---|---|",
    ]
    for name in ["vol", "context", "text", "full", "gbm"]:
        r = results[name]
        lines.append(
            f"| {LABELS[name]} | {r['platt']['brier']:.4f} | {r['iso']['brier']:.4f} | "
            f"{r['platt']['ece']:.4f} | {r['iso']['ece']:.4f} |"
        )
    lines += [
        "",
        "Curva de fiabilidade do modelo de produção (LR só-contexto), teste:",
        "",
        "| Bin | P prevista (Platt) | Observada | n | P prevista (iso) | Observada | n |",
        "|---|---|---|---|---|---|---|",
    ]
    rp, ri = results["context"]["rel_platt"], results["context"]["rel_iso"]
    for i in range(max(len(rp), len(ri))):
        a = f"{rp[i][0]:.2f} | {rp[i][1]:.2f} | {rp[i][2]}" if i < len(rp) else "— | — | —"
        b = f"{ri[i][0]:.2f} | {ri[i][1]:.2f} | {ri[i][2]}" if i < len(ri) else "— | — | —"
        lines.append(f"| {i + 1} | {a} | {b} |")
    # Veredicto calculado dos próprios números (tolerância 0,0005 = empate).
    fams = ["vol", "context", "text", "full", "gbm"]
    iso_b = sum(1 for n in fams if results[n]["iso"]["brier"] < results[n]["platt"]["brier"] - 5e-4)
    pla_b = sum(1 for n in fams if results[n]["platt"]["brier"] < results[n]["iso"]["brier"] - 5e-4)
    iso_e = sum(1 for n in fams if results[n]["iso"]["ece"] < results[n]["platt"]["ece"] - 5e-4)
    pla_e = sum(1 for n in fams if results[n]["platt"]["ece"] < results[n]["iso"]["ece"] - 5e-4)
    if iso_b == 0:
        verdict = (
            f"**Veredicto (tal como caiu):** no Brier, a Platt ganha ou empata em TODAS as "
            f"{len(fams)} famílias (ganha {pla_b}, empata {len(fams) - pla_b - iso_b}); no ECE "
            f"o quadro é misto ({iso_e} para a isotónica, {pla_e} para a Platt) e por margens "
            "pequenas. Mesmo com validação farta — o cenário teoricamente favorável à "
            "isotónica (niculescu2005calibration) — a flexibilidade extra não paga: a escolha "
            "de Platt na tese (2 parâmetros, sigmóide monótona e suave, explicável) fica "
            "validada EMPIRICAMENTE, não só conceptualmente. Não há caso para mudar a produção."
        )
    else:
        verdict = (
            f"**Veredicto (tal como caiu):** a isotónica melhora o Brier em {iso_b} de "
            f"{len(fams)} famílias e o ECE em {iso_e}; a Platt vence no Brier em {pla_b} e no "
            f"ECE em {pla_e}. A produção continua Platt (é o que os bundles de `models/` "
            "contêm e o que a tese descreve); a adoção da isotónica fica como decisão futura "
            "já medida empiricamente."
        )
    lines += [
        "",
        verdict,
        "",
        "**Caveats:** a isotónica pode criar patamares (empates) nas probabilidades — o "
        "ranking fino perde granularidade; ECE com 10 bins de largura igual; nenhum destes "
        "números substitui os congelados da tese.",
        "",
    ]
    md.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nEscrito: {md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
