"""Figura reprodutível (2026-07-13): projeção 2D REAL do espaço de embeddings da KB.

A tese tinha só uma figura CONCEPTUAL do espaço de embeddings (fig:embedding_concept);
esta mostra o espaço VERDADEIRO: PCA (SVD, numpy puro — sem dependências novas) dos
2 016 registos 384-d da KB do produto (data/samples/kb_fnspid_light.jsonl, versionada),
coloridos por setor, com a query da demo ("Nvidia demand surges on AI chip orders",
embedded com o MESMO MiniLM-ONNX do produto) marcada como estrela e os seus top-3
vizinhos por cosseno circundados. Sem rede quando o modelo ONNX já está em cache.

Saída: thesis/figures/embedding_projection.pdf
Uso: python scripts/figures/fig_embedding_projection.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent.parent

# A MESMA taxonomia de 5 setores da tese (investigator/triage/dataset.py::SECTORS).
from investigator.triage.dataset import SECTORS  # noqa: E402

SECTOR_TITLE = {"tech": "Technology", "banking": "Banking", "energy": "Energy",
                "health": "Health", "consumer": "Consumer"}
# Ordem fixa de cores (nunca ciclada): as cores por omissão do matplotlib — a mesma
# linguagem visual das restantes figuras da tese.
SECTOR_COLOR = {"tech": "C0", "banking": "C1", "energy": "C2",
                "health": "C3", "consumer": "C4"}


def load_kb(path: Path) -> tuple[np.ndarray, list[str], list[str]]:
    embs, tickers, headlines = [], [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            embs.append(rec["embedding"])
            tickers.append(rec["ticker"])
            headlines.append(rec["headline"])
    return np.asarray(embs, dtype="float64"), tickers, headlines


def pca_2d(x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """PCA por SVD (numpy puro): devolve (projeção n×2, componentes 2×d, % variância)."""
    mu = x.mean(axis=0)
    xc = x - mu
    _, s, vt = np.linalg.svd(xc, full_matrices=False)
    var = (s**2) / (s**2).sum()
    return xc @ vt[:2].T, vt[:2], var[:2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Projeção 2D real do espaço da KB (figura).")
    parser.add_argument("--kb", default="data/samples/kb_fnspid_light.jsonl")
    parser.add_argument("--query", default="Nvidia demand surges on AI chip orders")
    parser.add_argument("--out", default="thesis/figures/embedding_projection.pdf")
    args = parser.parse_args()

    embs, tickers, headlines = load_kb(REPO / args.kb)
    # Embeddings da KB são L2-normalizados (cosseno = produto interno).
    proj, comps, var = pca_2d(embs)
    print(f"KB: {len(embs)} registos, {embs.shape[1]}-d; PC1+PC2 explicam "
          f"{var.sum() * 100:.1f}% da variância.")

    # Query com o MESMO embedder do produto (ONNX MiniLM; fail-open → sem estrela).
    q2 = top3 = None
    try:
        from investigator.main import product_retrieval

        _, embedder = product_retrieval(auto_download=True)
        if getattr(embedder, "semantic", False):
            q = np.asarray(embedder.encode([args.query])[0], dtype="float64")
            sims = embs @ q / (np.linalg.norm(embs, axis=1) * np.linalg.norm(q))
            top3 = np.argsort(-sims)[:3]
            q2 = (q - embs.mean(axis=0)) @ comps.T
            for i in top3:
                print(f"  vizinho: sim {sims[i]:.2f} · {tickers[i]} · {headlines[i][:70]}")
        else:
            print("  [!] embedder semântico indisponível — figura sem a query.")
    except Exception as exc:  # noqa: BLE001
        print(f"  [!] query saltada ({type(exc).__name__}: {exc}) — figura só com a KB.")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5.2))
    for sec in ("tech", "banking", "energy", "health", "consumer"):
        idx = [i for i, t in enumerate(tickers) if SECTORS.get(t) == sec]
        ax.scatter(proj[idx, 0], proj[idx, 1], s=7, alpha=0.45,
                   color=SECTOR_COLOR[sec], label=f"{SECTOR_TITLE[sec]} ({len(idx)})",
                   linewidths=0)
    if q2 is not None:
        ax.scatter(proj[top3, 0], proj[top3, 1], s=90, facecolors="none",
                   edgecolors="black", linewidths=1.4, zorder=4,
                   label="Top-3 retrieved neighbours")
        ax.scatter(*q2, marker="*", s=260, color="black", zorder=5,
                   label='Query: "Nvidia demand surges…"')
    ax.set_xlabel(f"PC1 ({var[0] * 100:.1f}% of variance)")
    ax.set_ylabel(f"PC2 ({var[1] * 100:.1f}% of variance)")
    ax.set_title("The product knowledge base, projected to 2-D (PCA of real "
                 "MiniLM embeddings)", fontsize=11)
    ax.legend(fontsize=8, loc="best", framealpha=0.9)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    out = REPO / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
