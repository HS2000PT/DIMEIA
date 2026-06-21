"""Gera a figura da capitalização do mercado acionista dos EUA (2015–2024).

Figura reprodutível (§6.7): produzida por script, saída vetorial (PDF) para LaTeX.
Dados (US equity market cap, em biliões de USD = $ trillion) do SIFMA 2025 Capital
Markets Fact Book (fonte primária: World Federation of Exchanges). Verificado 2026-06-21.
Valores extraídos do gráfico "US Equity Market Capitalization" do Fact Book.

Uso:  python scripts/figures/fig_us_market_cap.py
Saída: thesis/figures/us_equity_market_cap.pdf
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")  # backend sem ecrã (reprodutível em CI/local)
import matplotlib.pyplot as plt

# Anos e capitalização do mercado acionista US, em $ trilião (SIFMA 2025 Fact Book).
ANOS = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
CAP_USD_T = [25.1, 27.4, 32.1, 30.4, 34.1, 41.6, 48.5, 40.3, 49.0, 62.2]

SAIDA = (
    pathlib.Path(__file__).resolve().parents[2] / "thesis" / "figures" / "us_equity_market_cap.pdf"
)


def gerar() -> None:
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    barras = ax.bar(ANOS, CAP_USD_T, color="#2c6fbb", width=0.65)
    ax.set_xlabel("Year")
    ax.set_ylabel("Market capitalisation (US$ trillion)")
    ax.set_xticks(ANOS)
    ax.set_ylim(0, max(CAP_USD_T) * 1.15)
    ax.bar_label(barras, fmt="%.1f", padding=2, fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(SAIDA, bbox_inches="tight")
    plt.close(fig)
    print(f"Figura gerada: {SAIDA}")


if __name__ == "__main__":
    gerar()
