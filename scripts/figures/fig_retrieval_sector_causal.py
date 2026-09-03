"""Figura de síntese da QI2 a partir dos dois artefactos de avaliação existentes."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).resolve().parents[2]
SECTOR_LABELS = {
    "Technology": "Tecnologia",
    "Banking": "Banca",
    "Energy": "Energia",
    "Health": "Saúde",
    "Consumer": "Consumo",
}


def _cells(line: str) -> list[str]:
    return [cell.strip().replace("**", "") for cell in line.strip().strip("|").split("|")]


def _tables(path: Path) -> list[list[dict[str, str]]]:
    """Lê as tabelas Markdown sem depender da prosa que as rodeia."""
    lines = path.read_text(encoding="utf-8").splitlines()
    out: list[list[dict[str, str]]] = []
    i = 0
    while i + 1 < len(lines):
        if not lines[i].lstrip().startswith("|") or not lines[i + 1].lstrip().startswith("|"):
            i += 1
            continue
        headers = _cells(lines[i])
        separator = _cells(lines[i + 1])
        if len(headers) != len(separator) or not all(set(cell) <= {"-", ":"} for cell in separator):
            i += 1
            continue
        rows: list[dict[str, str]] = []
        i += 2
        while i < len(lines) and lines[i].lstrip().startswith("|"):
            values = _cells(lines[i])
            if len(values) == len(headers):
                rows.append(dict(zip(headers, values, strict=True)))
            i += 1
        out.append(rows)
    return out


def _sector_rows(path: Path) -> list[dict[str, str]]:
    for rows in _tables(path):
        if rows and {"Setor", "P@5", "Aleatório (base)"} <= set(rows[0]):
            return rows
    raise ValueError(f"Tabela setorial não encontrada em {path}")


def _causal_rows(path: Path) -> list[dict[str, str]]:
    for rows in _tables(path):
        if rows and {"protocolo", "precisão@5", "chão", "margem"} <= set(rows[0]):
            return rows
    raise ValueError(f"Tabela causal não encontrada em {path}")


def _annotate(ax, bars, values) -> None:
    for bar, value in zip(bars, values, strict=True):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.018, f"{value:.3f}".replace(".", ","),
                ha="center", va="bottom", fontsize=8, color="#222222")


def build(sectors_path: Path, causal_path: Path, output: Path) -> None:
    sectors = _sector_rows(sectors_path)
    causal = _causal_rows(causal_path)

    labels = [SECTOR_LABELS[row["Setor"]] for row in sectors]
    method = [float(row["P@5"]) for row in sectors]
    sector_floor = [float(row["Aleatório (base)"]) for row in sectors]

    protocol_labels = ["Simétrico\n(escala)", "Causal\n(produção)"]
    precision = [float(row["precisão@5"]) for row in causal]
    causal_floor = [float(row["chão"]) for row in causal]
    margins = [row["margem"] for row in causal]

    method_color = "#0B7A53"
    floor_color = "#FFFFFF"
    fig, (left, right) = plt.subplots(
        1, 2, figsize=(10.2, 4.25), gridspec_kw={"width_ratios": [1.55, 1.0]}
    )

    x = np.arange(len(labels))
    width = 0.36
    b1 = left.bar(x - width / 2, method, width, color=method_color, label="MiniLM, P@5")
    b2 = left.bar(x + width / 2, sector_floor, width, color=floor_color,
                  edgecolor="#66736F", hatch="///", linewidth=0.7,
                  label="Taxa-base aleatória")
    _annotate(left, b1, method)
    _annotate(left, b2, sector_floor)
    left.set_xticks(x, labels)
    left.set_ylabel("Precisão@5")
    left.set_title("A. Comparação dentro de cada setor", loc="left", fontweight="bold")
    left.legend(frameon=False, fontsize=8, loc="upper right")

    x2 = np.arange(len(protocol_labels))
    b3 = right.bar(x2 - width / 2, precision, width, color=method_color, label="Precisão@5")
    b4 = right.bar(x2 + width / 2, causal_floor, width, color=floor_color,
                   edgecolor="#66736F", hatch="///", linewidth=0.7, label="Taxa-base aleatória")
    _annotate(right, b3, precision)
    _annotate(right, b4, causal_floor)
    right.set_xticks(x2, protocol_labels)
    right.set_title("B. Restrição ao passado", loc="left", fontweight="bold")
    right.legend(frameon=False, fontsize=8, loc="upper right")
    for pos, margin in zip(x2, margins, strict=True):
        right.text(pos, 0.08, f"margem {margin}".replace(".", ","),
                   ha="center", va="center", fontsize=8,
                   fontweight="bold", color="#222222",
                   bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9, "pad": 1.5})

    for ax in (left, right):
        ax.set_ylim(0, 0.82)
        ax.grid(axis="y", color="#D8D8D8", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="both", labelsize=8)

    fig.tight_layout(w_pad=2.0)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, bbox_inches="tight",
                metadata={"Title": "Recuperação por setor e restrição temporal"})
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sectors", type=Path,
                        default=REPO / "docs/evaluation/evaluation_per_sector.md")
    parser.add_argument("--causal", type=Path,
                        default=REPO / "docs/evaluation/evaluation_retrieval_causal.md")
    parser.add_argument("--output", type=Path,
                        default=REPO / "tese-v2/figures/eval_retrieval_sector_causal.pdf")
    args = parser.parse_args()
    build(args.sectors, args.causal, args.output)
    print(f"Figura escrita em {args.output}")


if __name__ == "__main__":
    main()
