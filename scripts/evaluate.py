"""Avalia a recuperação de precedentes: SBERT vs baseline lexical vs aleatório/recência.

Pergunta A (docs/design/evaluation_design.md §2): os precedentes recuperados são mesmo análogos?
Métrica: precision@k por SETOR em recuperação cross-ticker (ver src/evaluation/retrieval_eval.py).

Entrada: CSV de notícias (date, ticker, headline) — ex.: o de scripts/fetch_finnhub_news.py.
Saída: tabela em docs/evaluation/evaluation_results.md
       + figura em thesis/figures/eval_retrieval_precision.pdf.

Uso:
    python scripts/evaluate.py --news data/finnhub_news.csv
    python scripts/evaluate.py --news data/finnhub_news.csv --queries 500 --k 5 10
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
    recency_precision_at_k,
    retrieval_precision_at_k,
    same_ticker_forbid,
)

# Setores dos 15 tickers (data_card.md). Proxy automático de "analogia".
SECTORS = {
    "AAPL": "tech", "MSFT": "tech", "AMZN": "tech", "GOOGL": "tech", "NVDA": "tech",
    "TSLA": "tech", "META": "tech",
    "JPM": "banking", "BAC": "banking",
    "XOM": "energy", "CVX": "energy",
    "JNJ": "health", "PFE": "health",
    "WMT": "consumer", "KO": "consumer",
}

REPO = Path(__file__).resolve().parent.parent


def _short(model: str) -> str:
    """Nome curto do modelo para rótulos (ex.: all-MiniLM-L6-v2 → MiniLM)."""
    m = model.lower()
    if "minilm" in m:
        return "MiniLM"
    if "mpnet" in m:
        return "MPNet"
    return model.split("/")[-1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Avaliação da recuperação de precedentes.")
    parser.add_argument("--news", required=True)
    parser.add_argument("--queries", type=int, default=500, help="nº de consultas amostradas")
    parser.add_argument("--k", type=int, nargs="+", default=[5, 10])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--repeats", type=int, default=5,
                        help="nº de amostragens (seeds) para média ± desvio")
    parser.add_argument("--sbert-models", nargs="+", default=["all-MiniLM-L6-v2"],
                        help="modelos SBERT a comparar (ablação)")
    parser.add_argument("--out", default="docs/evaluation/evaluation_results.md")
    parser.add_argument("--fig", default="thesis/figures/eval_retrieval_precision.pdf")
    args = parser.parse_args()

    df = pd.read_csv(args.news).dropna(subset=["date", "ticker", "headline"])
    df["ticker"] = df["ticker"].astype(str).str.upper()
    df = df[df["ticker"].isin(SECTORS)].reset_index(drop=True)
    df["sector"] = df["ticker"].map(SECTORS)
    n = len(df)
    print(f"Notícias com setor conhecido: {n:,} | tickers: {sorted(df['ticker'].unique())}")

    tickers = df["ticker"].to_numpy()
    sectors = df["sector"].to_numpy()
    dates = df["date"].astype(str).to_numpy()
    headlines = df["headline"].astype(str).tolist()

    n_q = min(args.queries, n)
    print("A calcular embeddings…")
    from src.historical_kb.embedder import HashingEmbedder, SbertEmbedder

    # Métodos baseados em embeddings: um ou mais modelos SBERT (ablação) + baseline lexical.
    emb_methods: dict[str, np.ndarray] = {}
    for model in args.sbert_models:
        print(f"  SBERT: {model}")
        emb_methods[f"SBERT ({_short(model)})"] = SbertEmbedder(model).encode(headlines)
    emb_methods["Lexical (baseline)"] = HashingEmbedder(dim=512).encode(headlines)

    ks = sorted(set(args.k))
    methods = list(emb_methods.keys()) + ["Recency", "Random (base rate)"]
    # Para cada método/k, acumula o valor de cada seed → média ± desvio.
    samples: dict[str, dict[int, list[float]]] = {m: {k: [] for k in ks} for m in methods}
    for rep in range(args.repeats):
        rng = np.random.default_rng(args.seed + rep)
        q_idx = rng.choice(n, size=n_q, replace=False)
        forbid = same_ticker_forbid(tickers[q_idx], tickers)  # cross-ticker (exclui a empresa)
        for k in ks:
            for label, emb in emb_methods.items():
                samples[label][k].append(retrieval_precision_at_k(
                    emb[q_idx], emb, sectors[q_idx], sectors, k=k, forbid=forbid))
            samples["Recency"][k].append(recency_precision_at_k(
                sectors[q_idx], sectors, dates, k=k, forbid=forbid))
            samples["Random (base rate)"][k].append(expected_random_precision(
                sectors[q_idx], sectors, forbid))

    results = {m: {k: float(np.mean(samples[m][k])) for k in ks} for m in methods}
    stds = {m: {k: float(np.std(samples[m][k])) for k in ks} for m in methods}
    for k in ks:
        print(f"  k={k}: " + " | ".join(
            f"{m}={results[m][k]:.3f}±{stds[m][k]:.3f}" for m in methods))

    _write_markdown(args.out, df, n_q, ks, results, stds, methods, args.seed, args.repeats)
    _write_figure(args.fig, ks, results, stds, methods)


def _write_markdown(path, df, n_q, ks, results, stds, methods, seed, repeats) -> None:
    n = len(df)
    by_sec = df["sector"].value_counts().to_dict()
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# evaluation_results.md — Resultados da avaliação (reprodutível)",
        "",
        "> Gerado por `scripts/evaluate.py`. **Não editar à mão.** Ver os caveats no fim.",
        "",
        "## Pergunta A — qualidade da recuperação de precedentes (precision@k por setor)",
        "",
        f"- **Dados:** {n:,} notícias reais (Finnhub), {len(by_sec)} setores: {by_sec}.",
        f"- **Consultas amostradas:** {n_q} por repetição; **{repeats} repetições** "
        f"(seeds {seed}..{seed + repeats - 1}); média ± desvio. Recuperação **cross-ticker** "
        "(exclui a própria empresa).",
        "- **Proxy de relevância:** mesmo setor (data_card.md). "
        "Baselines: recência e taxa-base.",
        f"- **Gerado:** {now}.",
        "",
        "| Método | " + " | ".join(f"P@{k}" for k in ks) + " |",
        "|---|" + "|".join("---" for _ in ks) + "|",
    ]
    for method in methods:
        lines.append(
            f"| {method} | "
            + " | ".join(f"{results[method][k]:.3f} ± {stds[method][k]:.3f}" for k in ks) + " |"
        )
    k0 = ks[0]
    primary = methods[0]  # 1.º modelo SBERT (resultado principal)
    lift = results[primary][k0] - results["Random (base rate)"][k0]
    lines += [
        "",
        f"**Leitura:** a P@{k0} do {primary} é {results[primary][k0]:.3f} vs "
        f"{results['Random (base rate)'][k0]:.3f} da taxa-base aleatória "
        f"(lift {lift:+.3f}); baseline lexical {results['Lexical (baseline)'][k0]:.3f}.",
        "",
        "**Caveats (honestos):** o setor é um *proxy* automático de analogia (não um julgamento "
        "humano de relevância); os dados são do último período disponível no Finnhub (não o "
        "histórico multi-ano do FNSPID); títulos curtos limitam a semântica captável. Estes "
        "números são uma avaliação **preliminar** e reprodutível, não a avaliação final da tese.",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Resultados escritos em {path}")


def _write_figure(path, ks, results, stds, methods) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x = np.arange(len(ks))
    width = 0.8 / len(methods)
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, m in enumerate(methods):
        offset = (i - (len(methods) - 1) / 2) * width
        ax.bar(x + offset, [results[m][k] for k in ks], width, label=m,
               yerr=[stds[m][k] for k in ks], capsize=3, error_kw={"elinewidth": 0.8})
    ax.set_xticks(x, [f"P@{k}" for k in ks])
    ax.set_ylabel("Precision (same sector, cross-ticker)")
    ax.set_title("Precedent retrieval: SBERT versus baselines")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out = REPO / path if not Path(path).is_absolute() else Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"Figura escrita em {out}")


if __name__ == "__main__":
    main()
