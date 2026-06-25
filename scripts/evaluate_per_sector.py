"""Avaliação da recuperação POR SETOR (aprofundamento da Pergunta A).

Para cada setor, mede a precision@k (cross-ticker, mesmo setor) usando TODAS as notícias desse
setor como consultas (população completa → determinístico, sem amostragem). Mostra em que setores
a recuperação semântica funciona melhor e o seu *lift* sobre a taxa-base aleatória.

Modelo: SBERT all-MiniLM-L6-v2 (o default da tese).
Saída: docs/evaluation/evaluation_per_sector.md
       + figura thesis/figures/eval_retrieval_per_sector.pdf.
Uso: python scripts/evaluate_per_sector.py --news data/finnhub_news.csv
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.evaluation.retrieval_eval import (  # noqa: E402
    expected_random_precision,
    retrieval_precision_at_k,
    same_ticker_forbid,
)

SECTORS = {
    "AAPL": "tech", "MSFT": "tech", "AMZN": "tech", "GOOGL": "tech", "NVDA": "tech",
    "TSLA": "tech", "META": "tech",
    "JPM": "banking", "BAC": "banking",
    "XOM": "energy", "CVX": "energy",
    "JNJ": "health", "PFE": "health",
    "WMT": "consumer", "KO": "consumer",
}
SECTOR_LABEL = {"tech": "Technology", "banking": "Banking", "energy": "Energy",
                "health": "Health", "consumer": "Consumer"}
REPO = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Recuperação de precedentes por setor.")
    parser.add_argument("--news", required=True)
    parser.add_argument("--k", type=int, nargs="+", default=[5, 10])
    parser.add_argument("--model", default="all-MiniLM-L6-v2")
    parser.add_argument("--out", default="docs/evaluation/evaluation_per_sector.md")
    parser.add_argument("--fig", default="thesis/figures/eval_retrieval_per_sector.pdf")
    args = parser.parse_args()

    df = pd.read_csv(args.news).dropna(subset=["date", "ticker", "headline"])
    df["ticker"] = df["ticker"].astype(str).str.upper()
    df = df[df["ticker"].isin(SECTORS)].reset_index(drop=True)
    df["sector"] = df["ticker"].map(SECTORS)
    tickers = df["ticker"].to_numpy()
    sectors = df["sector"].to_numpy()
    headlines = df["headline"].astype(str).tolist()
    print(f"Notícias: {len(df):,} | setores: {sorted(set(sectors))}")

    from src.historical_kb.embedder import SbertEmbedder
    print(f"A calcular embeddings ({args.model})…")
    emb = SbertEmbedder(args.model).encode(headlines)

    ks = sorted(set(args.k))
    order = ["tech", "banking", "energy", "health", "consumer"]
    rows: dict[str, dict] = {}
    for sec in order:
        mask = sectors == sec
        q_emb, q_sec, q_tick = emb[mask], sectors[mask], tickers[mask]
        forbid = same_ticker_forbid(q_tick, tickers)
        rec = {"n": int(mask.sum()),
               "random": expected_random_precision(q_sec, sectors, forbid)}
        for k in ks:
            rec[f"p{k}"] = retrieval_precision_at_k(q_emb, emb, q_sec, sectors, k=k, forbid=forbid)
        rows[sec] = rec
        print(f"  {sec:9s} n={rec['n']:4d} " +
              " ".join(f"P@{k}={rec[f'p{k}']:.3f}" for k in ks) + f" (random {rec['random']:.3f})")

    _write_md(args.out, rows, ks, order)
    _write_fig(args.fig, rows, order)


def _write_md(path, rows, ks, order) -> None:
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# evaluation_per_sector.md — Recuperação por setor (reprodutível)",
        "",
        "> Gerado por `scripts/evaluate_per_sector.py`. **Não editar à mão.**",
        "",
        f"- **Gerado:** {now}. Modelo: SBERT all-MiniLM-L6-v2. População completa por setor "
        "(cross-ticker, sem amostragem).",
        "",
        "| Setor | N | " + " | ".join(f"P@{k}" for k in ks) + " | Aleatório (base) | Lift P@5 |",
        "|---|---|" + "|".join("---" for _ in ks) + "|---|---|",
    ]
    for sec in order:
        r = rows[sec]
        lift = r["p5"] - r["random"]
        lines.append(
            f"| {SECTOR_LABEL[sec]} | {r['n']} | "
            + " | ".join(f"{r[f'p{k}']:.3f}" for k in ks)
            + f" | {r['random']:.3f} | {lift:+.3f} |"
        )
    lines += [
        "",
        "**Leitura:** a recuperação semântica supera a taxa-base aleatória em todos os setores; "
        "o *lift* é maior na energia e na saúde (vocabulário distintivo) e menor no consumo. "
        "A tecnologia tem a P@5 bruta mais alta apenas por dominar o corpus (taxa-base elevada). "
        "Avaliação preliminar (corpus recente do Finnhub).",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Resultados escritos em {path}")


def _write_fig(path, rows, order) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [SECTOR_LABEL[s] for s in order]
    p5 = [rows[s]["p5"] for s in order]
    rnd = [rows[s]["random"] for s in order]
    x = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x - 0.2, p5, 0.4, label="SBERT (MiniLM) P@5")
    ax.bar(x + 0.2, rnd, 0.4, label="Random (base rate)")
    ax.set_xticks(x, labels, rotation=20, ha="right")
    ax.set_ylabel("Precision@5 (same sector, cross-ticker)")
    ax.set_title("Precedent retrieval by sector: SBERT versus random base rate")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out = REPO / path if not Path(path).is_absolute() else Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"Figura escrita em {out}")


if __name__ == "__main__":
    main()
