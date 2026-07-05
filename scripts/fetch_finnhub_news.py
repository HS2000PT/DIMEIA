"""Recolhe notícias reais (Finnhub /company-news) para os tickers do data_card → CSV.

Fonte de notícias REAL e gratuita para uma primeira avaliação, sem o download de ~23 GB do
FNSPID. O FNSPID continua a ser a fonte histórica mais rica (multi-ano)
— ver docs/design/data_card.md.

Saída: CSV com colunas `date, ticker, headline` (compatível com `build_kb.py` e `evaluate.py`).
Dados grandes ficam gitignored; só uma amostra pequena vai para data/samples/.

Uso:
    python scripts/fetch_finnhub_news.py                      # 15 tickers, últimos 180 dias
    python scripts/fetch_finnhub_news.py --days 90 --max-per-ticker 500
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from investigator.news_fetcher.fetcher import fetch_finnhub_company_news

DEFAULT_TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", "TSLA", "META", "JPM",
    "BAC", "XOM", "CVX", "JNJ", "PFE", "WMT", "KO",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Notícias reais via Finnhub → CSV.")
    parser.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    parser.add_argument("--days", type=int, default=180, help="janela para trás, em dias")
    parser.add_argument("--max-per-ticker", type=int, default=1000)
    parser.add_argument("--out", default="data/finnhub_news.csv")
    parser.add_argument("--sample", default="data/samples/finnhub_news_sample.csv")
    parser.add_argument("--sample-size", type=int, default=30)
    args = parser.parse_args()

    end = date.today()
    start = end - timedelta(days=args.days)
    print(f"Finnhub /company-news: {len(args.tickers)} tickers, {start}…{end}")

    rows: list[dict] = []
    for ticker in args.tickers:
        items = fetch_finnhub_company_news(ticker, start.isoformat(), end.isoformat())
        if args.max_per_ticker:
            items = items[: args.max_per_ticker]
        for it in items:
            if it.date:  # precisa de data para o event study
                rows.append({"date": it.date, "ticker": it.ticker, "headline": it.headline})
        print(f"  {ticker}: {len(items)} notícias")

    df = pd.DataFrame(rows).drop_duplicates(subset=["ticker", "headline"]).reset_index(drop=True)
    print(f"Total (após dedupe): {len(df):,} notícias")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Gravado em {out} (gitignored).")

    sample = df.head(args.sample_size)
    Path(args.sample).parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(args.sample, index=False)
    print(f"Amostra ({len(sample)}) em {args.sample} (versionada).")


if __name__ == "__main__":
    main()
