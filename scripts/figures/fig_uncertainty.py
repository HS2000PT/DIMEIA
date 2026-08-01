"""Figuras dos Casos 5-7: taxonomia de eventos, predição conformal e deriva.

Três painéis, um por caso de estudo, todos a partir de números já medidos e registados nos
respetivos `docs/evaluation/*.md`. **Não recalcula nada**: os valores entram como constantes
copiadas dos relatórios, para que a figura e o texto não possam divergir em silêncio.

Saídas (EN, como todas as figuras de dados da tese):
    thesis/figures/eval_taxonomy.pdf
    thesis/figures/eval_conformal.pdf
    thesis/figures/eval_drift.pdf

Uso: python scripts/figures/fig_uncertainty.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent.parent
FIGS = REPO / "thesis" / "figures"

# ── Números medidos (docs/evaluation/evaluation_event_taxonomy.md) ────────────
KS = [6, 8, 10, 12, 14, 16, 18, 20]
SILHOUETTE = [0.050, 0.068, 0.081, 0.078, 0.080, 0.082, 0.084, 0.083]
K_STAR = 18
AMI = {"Event type": 0.358, "Ticker": 0.188, "Sector": 0.130}

# ── Números medidos (docs/evaluation/evaluation_conformal.md) ─────────────────
ALPHAS = [0.05, 0.10, 0.20]
NOMINAL = [0.95, 0.90, 0.80]
COV_RANDOM = [0.951, 0.902, 0.803]
COV_TEMPORAL = [0.937, 0.900, 0.822]
BOTH_RANDOM = [0.784, 0.605, 0.323]  # fração "não sei"

# ── Números medidos (docs/evaluation/evaluation_drift.md) ─────────────────────
DRIFT = [
    ("Pre-event volatility (20 d)", 0.281),
    ("Headline length", 0.111),
    ("Event-day return", 0.020),
    ("5-day momentum", 0.014),
]
PSI_STABLE, PSI_MODERATE = 0.10, 0.25


def fig_taxonomy() -> None:
    """Esquerda: a silhueta é plana. Direita: o evento ganha ao assunto."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.4))

    ax1.plot(KS, SILHOUETTE, "o-", color="#2c6fbb", lw=1.6, ms=5)
    star = SILHOUETTE[KS.index(K_STAR)]
    ax1.plot([K_STAR], [star], "*", color="#d95f02", ms=16, zorder=5)
    ax1.annotate(
        f"$k^*={K_STAR}$",
        xy=(K_STAR, star),
        xytext=(K_STAR - 5.0, star - 0.010),
        fontsize=8,
        color="#d95f02",
    )
    # A mensagem honesta da figura: a curva é PLANA, logo k* é fracamente determinado.
    ax1.axhspan(min(SILHOUETTE[2:]), max(SILHOUETTE), color="#d95f02", alpha=0.08)
    ax1.text(
        11.0,
        0.0595,
        "flat from $k=10$:\nrange 0.003",
        fontsize=7.5,
        color="#666666",
        style="italic",
    )
    ax1.set_xlabel("Number of clusters $k$", fontsize=9)
    ax1.set_ylabel("Silhouette (cosine)", fontsize=9)
    ax1.set_title("Choosing $k$: weakly determined", fontsize=10)
    ax1.grid(alpha=0.3)
    ax1.tick_params(labelsize=8)

    names = list(AMI)
    vals = [AMI[n] for n in names]
    colours = ["#2c6fbb", "#9ecae1", "#c6dbef"]
    bars = ax2.bar(names, vals, color=colours, width=0.6)
    ax2.bar_label(bars, fmt="%.3f", fontsize=8.5, padding=2)
    ax2.set_ylabel("Adjusted mutual information", fontsize=9)
    ax2.set_ylim(0, max(vals) * 1.28)
    ax2.set_title("Event, not just subject", fontsize=10)
    ax2.tick_params(labelsize=8)
    ax2.grid(axis="y", alpha=0.3)
    ax2.text(
        0.5,
        0.93,
        "same 11,889 rows; chance-corrected",
        transform=ax2.transAxes,
        ha="center",
        fontsize=7.5,
        color="#666666",
        style="italic",
    )

    fig.tight_layout()
    out = FIGS / "eval_taxonomy.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")


def fig_conformal() -> None:
    """Esquerda: cobertura vs nominal nas duas divisões. Direita: o preço, em conjuntos."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.4))

    x = np.arange(len(ALPHAS))
    w = 0.36
    b1 = ax1.bar(x - w / 2, COV_RANDOM, w, color="#2c6fbb", label="Random split")
    b2 = ax1.bar(x + w / 2, COV_TEMPORAL, w, color="#f0a860", label="Temporal split")
    ax1.bar_label(b1, fmt="%.3f", fontsize=7.5, padding=2)
    ax1.bar_label(b2, fmt="%.3f", fontsize=7.5, padding=2)
    for i, nom in enumerate(NOMINAL):
        ax1.hlines(nom, i - 0.48, i + 0.48, colors="#333333", linestyles="--", lw=1.3,
                   zorder=6)
    # A única quebra: alfa=0,05 sob divisão temporal.
    # Colocada na faixa vazia acima das barras: dentro da área dos dados cruzava a linha
    # nominal de 0,90 e o rótulo vizinho.
    ax1.annotate(
        "coverage lost",
        xy=(w, 0.912),  # flanco direito da barra, não o topo (aí tapava o rótulo 0.937)
        xytext=(0.80, 0.978),
        fontsize=7.5,
        color="#c0392b",
        ha="center",
        va="center",
        arrowprops={"arrowstyle": "->", "color": "#c0392b", "lw": 1.0,
                    "shrinkA": 2, "shrinkB": 2},
    )
    ax1.set_xticks(
        x,
        [
            f"$\\alpha$={a:.2f}\n(nominal {n:.0%})"
            for a, n in zip(ALPHAS, NOMINAL, strict=True)
        ],
        fontsize=8,
    )
    ax1.set_ylabel("Empirical coverage", fontsize=9)
    ax1.set_ylim(0.75, 1.0)
    ax1.set_title("The guarantee, and where it breaks", fontsize=10)
    ax1.legend(fontsize=7.5, loc="lower left")
    ax1.grid(axis="y", alpha=0.3)
    ax1.tick_params(labelsize=8)

    decided = [1.0 - b for b in BOTH_RANDOM]
    b3 = ax2.barh(x, decided, 0.5, color="#2c6fbb", label="Definite call")
    b4 = ax2.barh(x, BOTH_RANDOM, 0.5, left=decided, color="#d9d9d9",
                  label='Both labels ("don\'t know")')
    ax2.bar_label(b3, fmt="%.0f%%", labels=[f"{d:.0%}" for d in decided], fontsize=8,
                  label_type="center")
    ax2.bar_label(b4, labels=[f"{b:.0%}" for b in BOTH_RANDOM], fontsize=8,
                  label_type="center", color="#444444")
    ax2.set_yticks(x, [f"{n:.0%} coverage" for n in NOMINAL], fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 1)
    ax2.set_xlabel("Share of test headlines", fontsize=9)
    ax2.set_title("The price of the guarantee", fontsize=10)
    # Legenda ACIMA dos eixos: dentro do painel tapava o rótulo da barra de baixo.
    ax2.legend(
        fontsize=7.5,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.06),
        ncol=2,
        frameon=False,
    )
    ax2.tick_params(labelsize=8)

    fig.tight_layout()
    out = FIGS / "eval_conformal.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")


def fig_drift() -> None:
    """PSI por feature contra as bandas convencionadas do risco de crédito."""
    fig, ax = plt.subplots(figsize=(7.4, 3.0))
    names = [n for n, _ in DRIFT][::-1]
    vals = [v for _, v in DRIFT][::-1]
    colours = [
        "#c0392b" if v >= PSI_MODERATE else ("#f0a860" if v >= PSI_STABLE else "#7bb47b")
        for v in vals
    ]
    y = np.arange(len(names))
    bars = ax.barh(y, vals, 0.55, color=colours)
    ax.bar_label(bars, fmt="%.3f", fontsize=8.5, padding=3)

    xmax = max(vals) * 1.35
    ax.axvline(PSI_STABLE, color="#666666", ls="--", lw=1.0)
    ax.axvline(PSI_MODERATE, color="#666666", ls="--", lw=1.0)

    # Rotular as REGIÕES (e não as fronteiras): "stable | moderate" colado à linha lia-se
    # mal e, no topo do eixo, colidia com o título. Cada rótulo vai ao centro da sua banda,
    # numa faixa de folga aberta acima das barras.
    topo = len(names) - 1 + 0.62
    for centro, etiqueta in (
        (PSI_STABLE / 2, "stable"),
        ((PSI_STABLE + PSI_MODERATE) / 2, "moderate"),
        ((PSI_MODERATE + xmax) / 2, "significant"),
    ):
        ax.text(centro, topo, etiqueta, fontsize=7.5, color="#666666", ha="center",
                style="italic")

    ax.set_yticks(y, names, fontsize=8.5)
    ax.set_xlabel("Population Stability Index (train 2018--2022 $\\rightarrow$ test 2023)",
                  fontsize=9)
    ax.set_xlim(0, xmax)
    ax.set_ylim(-0.62, len(names) - 1 + 0.95)
    ax.set_title("Which inputs moved, and by how much", fontsize=10)
    ax.grid(axis="x", alpha=0.3)
    ax.tick_params(labelsize=8)

    fig.tight_layout()
    out = FIGS / "eval_drift.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    fig_taxonomy()
    fig_conformal()
    fig_drift()


if __name__ == "__main__":
    main()
