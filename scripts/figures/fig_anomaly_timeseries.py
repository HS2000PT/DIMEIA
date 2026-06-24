"""Figura reprodutível: série temporal de retornos de um ticker volátil (TSLA) com os
dias sinalizados como anomalia pelo detetor z-score (janela 20, limiar 3, sem lookahead).

Mostra o detetor a funcionar em dados reais: assinala os movimentos abruptos relativos
à volatilidade recente, e não os movimentos grandes em termos absolutos.

Saída: thesis/figures/anomaly_timeseries.pdf
Uso: python scripts/figures/fig_anomaly_timeseries.py [--ticker TSLA]
     [--start 2023-06-01] [--end 2026-06-01] [--window 20] [--threshold 3.0]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.evaluation.anomaly_eval import rolling_zscore_flags  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Série temporal de anomalias (figura).")
    parser.add_argument("--ticker", default="TSLA")
    parser.add_argument("--start", default="2023-06-01")
    parser.add_argument("--end", default="2026-06-01")
    parser.add_argument("--window", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=3.0)
    parser.add_argument("--out", default="thesis/figures/anomaly_timeseries.pdf")
    args = parser.parse_args()

    import yfinance as yf

    df = yf.Ticker(args.ticker).history(start=args.start, end=args.end, interval="1d")
    close = df["Close"].to_numpy()
    dates = df.index.to_numpy()[1:]  # returns align to day t (drop first)
    r = np.diff(np.log(close))  # daily log-returns
    flags = rolling_zscore_flags(r, args.window, args.threshold)

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(dates, r * 100, color="black", linewidth=0.7, alpha=0.7, label="Daily log-return")
    ax.scatter(
        dates[flags], r[flags] * 100, color="crimson", s=22, zorder=3,
        label=f"Flagged anomaly (|z| > {args.threshold:g})",
    )
    ax.axhline(0, color="grey", linewidth=0.5)
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily log-return (%)")
    ax.set_title(
        f"{args.ticker}: daily returns with z-score-flagged anomalies "
        f"(window {args.window}, k = {args.threshold:g})"
    )
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    out = REPO / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"wrote {out} ({int(flags.sum())} flagged of {len(r)} days)")


if __name__ == "__main__":
    main()
