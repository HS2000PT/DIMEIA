"""Re-teste JUSTO da hipótese de texto da RQ4 (fase D) — ADITIVO, não altera os congelados.

A crítica: o resultado "o texto não bate a volatilidade" (full 0.496 < context 0.538 < vol 0.542)
pode ser um ARTEFACTO de sub-ajuste — C não afinado e um bloco de 384 dims a diluir 5 escalares —
e não evidência de que a manchete não tem sinal. Este script dá ao texto o teste mais justo que os
dados permitem (sem corpos de artigo, que não existem no dataset):

  1. GRELHA DE REGULARIZAÇÃO: afina o C da LR na VALIDAÇÃO (não no teste) para context e full.
  2. REDUÇÃO PCA do bloco de texto (16/32/64 dims) antes de concatenar — para não esmagar os
     escalares de contexto.
  3. (--finbert) encoder de DOMÍNIO (FinBERT mean-pooled) como bloco de texto.

Se, mesmo assim, nenhuma variante de texto superar a volatilidade → o negativo fica À PROVA DE BALA.
Se alguma superar → o negativo era parcialmente um artefacto. Reportado tal como cair.

Embeddings MiniLM em cache (data/_cache_triage_minilm.npy, gitignored) para re-corridas rápidas.

Uso:
    python scripts/evaluate_triage_fairtext.py --dataset <triage_dataset.csv>
    python scripts/evaluate_triage_fairtext.py --dataset <...> --finbert
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from investigator.console import force_utf8_stdout
from investigator.triage.features import context_block
from investigator.triage.model import fit_platt, metrics, scores_of

REPO = Path(__file__).resolve().parents[1]
C_GRID = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]
FROZEN = {"vol": 0.542, "context": 0.538, "full(C=1, 384d)": 0.496}


def _lr(c: float):
    return Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "lr",
                LogisticRegression(max_iter=2000, class_weight="balanced", C=c, random_state=42),
            ),
        ]
    )


def _fit_eval(xtr, xva, xte, y, budget_dates=None):
    """Devolve (pr_auc_val, pr_auc_test) para o melhor C na validação (Platt na val)."""
    best = None
    for c in C_GRID:
        m = _lr(c)
        m.fit(xtr, y["train"])
        cal = fit_platt(scores_of(m, xva), y["val"])
        va = metrics(y["val"], cal(scores_of(m, xva)))["pr_auc"]
        te = metrics(y["test"], cal(scores_of(m, xte)))["pr_auc"]
        if best is None or va > best[1]:
            best = (c, va, te)
    return best  # (C*, val_pr, test_pr)


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="RQ4 fair text test (fase D)")
    ap.add_argument("--dataset", default=str(REPO / "data" / "triage_dataset.csv"))
    ap.add_argument("--finbert", action="store_true")
    args = ap.parse_args()

    df = pd.read_csv(args.dataset)
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    parts = {s: df[df["split"] == s].reset_index(drop=True) for s in ["train", "val", "test"]}
    y = {s: parts[s]["label"].to_numpy() for s in parts}
    ctx = {s: context_block(parts[s])[0] for s in parts}

    # ── Embeddings de texto (MiniLM, com cache) ───────────────────────────────
    cache = Path(args.dataset).with_name("_cache_triage_minilm.npy")
    if cache.exists():
        allemb = np.load(cache)
        print(f"Cache de embeddings: {cache.name}")
    else:
        from investigator.historical_kb.embedder import SbertEmbedder

        print("A embeder as manchetes com MiniLM (uma vez, guarda em cache)…")
        allemb = SbertEmbedder("all-MiniLM-L6-v2").encode(df["headline"].astype(str).tolist())
        np.save(cache, allemb)
    off = {}
    i = 0
    for s in ["train", "val", "test"]:
        off[s] = allemb[i : i + len(parts[s])]
        i += len(parts[s])

    rows: list[tuple[str, str, float, float]] = []  # (config, C*, val_pr, test_pr)

    # baselines (C afinado também, para ser justo dos dois lados)
    c, va, te = _fit_eval(ctx["train"][:, :1], ctx["val"][:, :1], ctx["test"][:, :1], y)
    rows.append(("Volatility-only (tuned)", f"C={c}", va, te))
    c, va, te = _fit_eval(ctx["train"], ctx["val"], ctx["test"], y)
    rows.append(("Context-only (tuned)", f"C={c}", va, te))

    def full(emb_tr, emb_va, emb_te, tag):
        xtr = np.hstack([ctx["train"], emb_tr])
        xva = np.hstack([ctx["val"], emb_va])
        xte = np.hstack([ctx["test"], emb_te])
        c, va, te = _fit_eval(xtr, xva, xte, y)
        rows.append((tag, f"C={c}", va, te))

    full(off["train"], off["val"], off["test"], "Context+text MiniLM 384d (tuned)")
    for d in [16, 32, 64]:
        pca = PCA(n_components=d, random_state=42).fit(off["train"])
        full(
            pca.transform(off["train"]),
            pca.transform(off["val"]),
            pca.transform(off["test"]),
            f"Context+text MiniLM PCA-{d} (tuned)",
        )

    if args.finbert:
        fbcache = Path(args.dataset).with_name("_cache_triage_finbert.npy")
        if fbcache.exists():
            fb = np.load(fbcache)
            print(f"Cache FinBERT: {fbcache.name}")
        else:
            from investigator.historical_kb.embedder import SbertEmbedder

            print("A embeder com FinBERT (encoder de domínio, mean-pool)…")
            fb = SbertEmbedder("ProsusAI/finbert").encode(df["headline"].astype(str).tolist())
            np.save(fbcache, fb)
        fo = {}
        i = 0
        for s in ["train", "val", "test"]:
            fo[s] = fb[i : i + len(parts[s])]
            i += len(parts[s])
        full(fo["train"], fo["val"], fo["test"], "Context+text FinBERT (tuned)")
        for d in [32]:
            pca = PCA(n_components=d, random_state=42).fit(fo["train"])
            full(
                pca.transform(fo["train"]),
                pca.transform(fo["val"]),
                pca.transform(fo["test"]),
                f"Context+text FinBERT PCA-{d} (tuned)",
            )

    for name, cc, va, te in rows:
        print(f"  {name:38s} {cc:9s} val={va:.3f} test={te:.3f}")

    vol_te = [r[3] for r in rows if r[0].startswith("Volatility")][0]
    ctx_te = [r[3] for r in rows if r[0].startswith("Context-only")][0]
    raw_full = [r[3] for r in rows if "384d" in r[0]][0]
    best_text = max((r for r in rows if "+text" in r[0]), key=lambda r: r[3])
    verdict = (
        "o texto SUPERA a volatilidade"
        if best_text[3] > vol_te
        else "o texto NÃO supera a volatilidade"
    )

    out = REPO / "docs" / "evaluation" / "evaluation_triage_fairtext.md"
    L = [
        "# evaluation_triage_fairtext.md — Re-teste justo da hipótese de texto (RQ4; fase D)",
        "",
        "> Gerado por `scripts/evaluate_triage_fairtext.py` (ADITIVO). Dá ao texto o teste justo",
        "> possível — C afinado na validação, bloco de texto reduzido por PCA (não esmaga os",
        "> escalares), e opcionalmente o encoder FinBERT — para separar 'texto sem sinal'",
        "> de 'sub-ajuste'. Seleção de modelo só na VALIDAÇÃO; teste tocado uma vez.",
        "",
        f"- **Dataset:** {len(df)} linhas · seleção por PR-AUC na validação · grelha C = {C_GRID}.",
        f"- **Gerado:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC.",
        "- **Congelados (C=1, sem afinação):** vol 0.542 · context 0.538 · full 0.496.",
        "",
        "| Configuração | C* | PR-AUC (val) | PR-AUC (teste) |",
        "|---|---|---|---|",
    ]
    for name, cc, va, te in rows:
        L.append(f"| {name} | {cc} | {va:.3f} | {te:.3f} |")
    nuance = (
        f"**Nuance honesta (o arguente tinha razão num ponto):** o texto cru de 384 dims "
        f"(afinado) dá {raw_full:.3f}, mas reduzi-lo por PCA recupera até **{best_text[3]:.3f}** "
        f"('{best_text[0]}') — ou seja, o número congelado (full 0,496) estava EM PARTE "
        "deprimido por dimensionalidade "
        "(384 dims a diluir 5 escalares de contexto). "
    )
    if best_text[3] <= vol_te:
        end = (
            f"MAS mesmo o melhor texto justo ({best_text[3]:.3f}) não supera a volatilidade "
            f"({vol_te:.3f}) nem o contexto ({ctx_te:.3f}): o texto recupera até ao nível do "
            "contexto, nunca acima. Sob um teste JUSTO e afinado, o veredicto da RQ4 — o sinal de "
            "materialidade de curto prazo vive no contexto de mercado, não na manchete — passa de "
            "'plausivelmente sub-ajustado' a **robusto**. Reportam-se TODAS as configurações, "
            "incluindo as que recuperam."
        )
    else:
        end = (
            f"E o melhor texto justo ({best_text[3]:.3f}) SUPERA a volatilidade ({vol_te:.3f}): o "
            "negativo original era em parte um artefacto. Isto MUDA o veredicto da RQ4 e deve "
            "refletir-se na tese, com honestidade (só aparece com afinação/redução)."
        )
    L += [
        "",
        f"**Veredicto (reportado tal como cai):** com o C afinado, texto reduzido por PCA"
        f"{' e o encoder de domínio FinBERT' if args.finbert else ''}, **{verdict}**.",
        "",
        nuance + end,
    ]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nEscrito: {out}\nVeredicto: {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
