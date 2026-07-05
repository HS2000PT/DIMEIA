"""Constrói a base de conhecimento histórica (KB) a partir de notícias + preços.

Junta o subconjunto de notícias do FNSPID (CSV: date, ticker, headline) aos preços de fecho
históricos (yfinance) e produz a KB (JSONL) com impacto pós-evento e embeddings — ver
investigator/historical_kb/knowledge_base.py.

Embedder: por defeito o `HashingEmbedder` (sem dependências; baseline e reprodutível). Com
`--sbert` usa o `SbertEmbedder` (SBERT real; requer sentence-transformers/torch instalados).

Uso:
    python scripts/build_kb.py --news data/fnspid_news_subset.csv          # KB completa
    python scripts/build_kb.py --news data/samples/fnspid_news_sample.csv  # demo (amostra)
    python scripts/build_kb.py --news <csv> --sbert                        # com SBERT real
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):  # consola Windows (cp1252) → UTF-8 para acentos/glifos
    sys.stdout.reconfigure(encoding="utf-8")

from investigator.historical_kb.embedder import HashingEmbedder
from investigator.historical_kb.knowledge_base import HistoricalKB


def load_prices(tickers: list[str], start: str, end: str) -> dict[str, pd.Series]:
    """Preços de fecho diários por ticker (yfinance), índice tz-naive e ordenado."""
    import yfinance as yf

    prices: dict[str, pd.Series] = {}
    for ticker in tickers:
        df = yf.Ticker(ticker).history(start=start, end=end, interval="1d")
        if df is None or df.empty:
            print(f"  [!] sem precos para {ticker} - ignorado")
            continue
        close = df["Close"].copy()
        # yfinance devolve índice tz-aware (America/New_York); normalizamos para naive
        # para o `searchsorted` comparar com a data da notícia.
        close.index = pd.to_datetime(close.index).tz_localize(None)
        prices[ticker] = close.sort_index()
        print(f"  [ok] {ticker}: {len(close)} dias")
    return prices


def main() -> None:
    parser = argparse.ArgumentParser(description="Construção da KB histórica (notícias+preços).")
    parser.add_argument("--news", required=True, help="CSV com colunas date, ticker, headline")
    parser.add_argument("--out", default="data/kb.jsonl")
    parser.add_argument("--sample", default="data/samples/kb_sample.jsonl")
    parser.add_argument("--sample-size", type=int, default=50)
    parser.add_argument("--sbert", action="store_true",
                        help="usa SBERT real (senão HashingEmbedder)")
    parser.add_argument("--dim", type=int, default=64, help="dimensão do HashingEmbedder")
    args = parser.parse_args()

    news = pd.read_csv(args.news)
    news["date"] = pd.to_datetime(news["date"], errors="coerce")
    news = news.dropna(subset=["date", "ticker", "headline"])
    tickers = sorted(news["ticker"].astype(str).str.upper().unique().tolist())
    start = news["date"].min().strftime("%Y-%m-%d")
    end = (news["date"].max() + pd.Timedelta(days=10)).strftime("%Y-%m-%d")  # margem p/ +5d
    print(f"Notícias: {len(news):,} | tickers: {tickers} | {start}…{end}")

    print("A obter preços (yfinance)…")
    prices = load_prices(tickers, start, end)

    if args.sbert:
        from investigator.historical_kb.embedder import SbertEmbedder

        embedder = SbertEmbedder()
        print(f"Embedder: SBERT ({embedder.model_name}, dim={embedder.dim})")
    else:
        embedder = HashingEmbedder(dim=args.dim)
        print(f"Embedder: HashingEmbedder (baseline, dim={embedder.dim})")

    print("A construir a KB…")
    kb = HistoricalKB.build(news, prices, embedder)
    print(f"KB construída: {len(kb)} registos")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    kb.save(out)
    print(f"KB gravada em {out} (gitignored).")

    HistoricalKB(kb.records[: args.sample_size]).save(args.sample)
    n_sample = min(args.sample_size, len(kb))
    print(f"Amostra da KB ({n_sample} registos) em {args.sample} (versionada).")


if __name__ == "__main__":
    main()
