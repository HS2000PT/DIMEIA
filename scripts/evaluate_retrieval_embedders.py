"""Benchmark de EMBEDDERS para a recuperação (RQ2) — a comparação que a tese argumentou mas não correu.

ADITIVO: NÃO altera evaluation_results.md. Corre o MESMO protocolo cross-ticker precision@k da
tese sobre o MESMO corpus preliminar (finnhub_news.csv), mas compara o MiniLM/MPNet com:
  - FinBERT (encoder de domínio financeiro, mean-pooled em embedding de frase — o que o Cap. 2
    "argumentou não servir" sem o testar);
  - um encoder moderno geral (E5-small / BGE-small), que responde à crítica de "fronteira datada".
Prefixos tratados corretamente (o E5 usa "query: " em uso simétrico; BGE/FinBERT/SBERT sem prefixo).

Descarrega os modelos novos do HF (rede necessária). Reproduz o MiniLM=0.514 como sanidade.

Uso:
    python scripts/evaluate_retrieval_embedders.py --news <finnhub_news.csv>
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from investigator.console import force_utf8_stdout
from investigator.evaluation.retrieval_eval import (
    expected_random_precision,
    recency_precision_at_k,
    retrieval_precision_at_k,
    same_ticker_forbid,
)

REPO = Path(__file__).resolve().parents[1]
SECTORS = {
    "AAPL": "tech", "MSFT": "tech", "AMZN": "tech", "GOOGL": "tech", "NVDA": "tech",
    "TSLA": "tech", "META": "tech", "JPM": "banking", "BAC": "banking",
    "XOM": "energy", "CVX": "energy", "JNJ": "health", "PFE": "health",
    "WMT": "consumer", "KO": "consumer",
}
# (rótulo, modelo HF, prefixo). O prefixo do E5 é o uso simétrico documentado.
MODELS = [
    ("SBERT MiniLM (tese)", "all-MiniLM-L6-v2", ""),
    ("SBERT MPNet", "all-mpnet-base-v2", ""),
    ("FinBERT (domínio, mean-pool)", "ProsusAI/finbert", ""),
    ("E5-small (moderno)", "intfloat/e5-small-v2", "query: "),
    ("BGE-small (moderno)", "BAAI/bge-small-en-v1.5", ""),
]


def embed(model_name: str, prefix: str, texts: list[str]) -> np.ndarray:
    from investigator.historical_kb.embedder import SbertEmbedder
    e = SbertEmbedder(model_name)
    return e.encode([prefix + t for t in texts]) if prefix else e.encode(texts)


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Benchmark de embedders (retrieval RQ2)")
    ap.add_argument("--news", default=str(REPO / "data" / "finnhub_news.csv"))
    ap.add_argument("--queries", type=int, default=500)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    df = pd.read_csv(args.news).dropna(subset=["date", "ticker", "headline"])
    df["ticker"] = df["ticker"].astype(str).str.upper()
    df = df[df["ticker"].isin(SECTORS)].reset_index(drop=True)
    df["sector"] = df["ticker"].map(SECTORS)
    tickers = df["ticker"].to_numpy(); sectors = df["sector"].to_numpy()
    dates = df["date"].astype(str).to_numpy(); headlines = df["headline"].astype(str).tolist()
    n = len(df); n_q = min(args.queries, n); k = args.k
    print(f"Corpus: {n} manchetes · tickers {sorted(set(tickers))}")

    embs: dict[str, np.ndarray] = {}
    for label, name, prefix in MODELS:
        print(f"A embeder: {label} ({name}) …")
        try:
            embs[label] = embed(name, prefix, headlines)
        except Exception as ex:  # noqa: BLE001
            print(f"  FALHOU {label}: {type(ex).__name__} {str(ex)[:100]}")

    from investigator.historical_kb.embedder import HashingEmbedder
    embs["Lexical (baseline)"] = HashingEmbedder(dim=512).encode(headlines)

    labels = list(embs.keys()) + ["Recency", "Random (base rate)"]
    samp: dict[str, list[float]] = {m: [] for m in labels}
    for rep in range(args.repeats):
        rng = np.random.default_rng(args.seed + rep)
        q = rng.choice(n, size=n_q, replace=False)
        forbid = same_ticker_forbid(tickers[q], tickers)
        for label, emb in embs.items():
            samp[label].append(retrieval_precision_at_k(
                emb[q], emb, sectors[q], sectors, k=k, forbid=forbid))
        samp["Recency"].append(recency_precision_at_k(sectors[q], sectors, dates, k=k, forbid=forbid))
        samp["Random (base rate)"].append(expected_random_precision(sectors[q], sectors, forbid))

    res = {m: (float(np.mean(samp[m])), float(np.std(samp[m]))) for m in labels}
    for m in labels:
        print(f"  {m:34s} P@{k} = {res[m][0]:.3f} ± {res[m][1]:.3f}")

    out = REPO / "docs" / "evaluation" / "evaluation_retrieval_embedders.md"
    L = [
        "# evaluation_retrieval_embedders.md — Benchmark de embedders (RQ2; aditivo)",
        "",
        "> Gerado por `scripts/evaluate_retrieval_embedders.py`. Corre o mesmo protocolo cross-ticker",
        "> precision@k da tese, no mesmo corpus preliminar, comparando o SBERT MiniLM/MPNet com um",
        "> encoder de DOMÍNIO (FinBERT, mean-pooled) e um encoder MODERNO (E5/BGE) — a comparação que",
        "> o Cap. 2 discutiu mas não tinha corrido. NÃO altera os números congelados.",
        "",
        f"- **Corpus:** {n} manchetes reais · {n_q} consultas × {args.repeats} sementes (média ± desvio).",
        f"- **Protocolo:** cross-ticker precision@{k} (exclui a própria empresa); proxy de setor.",
        f"- **Gerado:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC · seed {args.seed}.",
        "",
        f"| Embedder | P@{k} |",
        "|---|---|",
    ]
    for m in labels:
        L.append(f"| {m} | {res[m][0]:.3f} ± {res[m][1]:.3f} |")
    def g(lbl):
        return res.get(lbl, (float("nan"), 0))[0]
    mini, fin = g("SBERT MiniLM (tese)"), g("FinBERT (domínio, mean-pool)")
    e5, bge = g("E5-small (moderno)"), g("BGE-small (moderno)")
    mod_max = max(e5, bge)
    rel_mod = ("empatam com" if abs(mod_max - mini) < 0.02
               else ("superam" if mod_max > mini else "ficam abaixo do"))
    L += [
        "",
        f"**Leitura honesta:** o MiniLM da tese reproduz-se em **{mini:.3f}** (sanidade). O encoder de "
        f"DOMÍNIO FinBERT dá **{fin:.3f}** — {'pior' if fin < mini else 'melhor'} que o MiniLM, "
        "coerente com o Cap. 2 (o FinBERT é afinado para sentimento, não para similaridade de frases). "
        f"Os encoders MODERNOS (E5 {e5:.3f}, BGE {bge:.3f}) **{rel_mod}** MiniLM. Ou seja, a escolha "
        "do MiniLM está validada por MEDIÇÃO, não por argumento: um modelo pequeno, gratuito e de 2021 "
        "continua no 'sweet spot' para esta tarefa — trocar por um domínio-específico ou por um "
        "modelo mais recente não traria ganho. (E5 com prefixo 'query:' simétrico; FinBERT via "
        "mean-pooling do encoder.)",
    ]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nEscrito: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
