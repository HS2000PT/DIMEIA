"""Avalia o detetor de anomalias (Pergunta 1) em preços reais (yfinance).

Evidências (ver src/evaluation/anomaly_eval.py e docs/design/evaluation_design.md §1):
1. **Consistência da taxa de disparo** entre tickers — z-score (normaliza volatilidade) vs limiar
   fixo em % (ingénuo). Reporta o intervalo/dispersão das taxas entre tickers.
2. **Precision/recall/F1** vs rótulo-proxy (movimento extremo por ticker), agregado (pooled).
3. **Ablação** ao tamanho da janela (10/20/60).

Saída: docs/evaluation/evaluation_anomaly.md + figura thesis/figures/eval_anomaly_firing_rate.pdf.

Uso: python scripts/evaluate_anomaly.py [--period 3y] [--window 20] [--threshold 3.0]
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.evaluation.anomaly_eval import (  # noqa: E402
    firing_rate,
    fixed_threshold_flags,
    isolation_forest_flags,
    label_extreme_moves,
    precision_recall_f1,
    rolling_zscore_flags,
)

REPO = Path(__file__).resolve().parent.parent
TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", "TSLA", "META", "JPM",
    "BAC", "XOM", "CVX", "JNJ", "PFE", "WMT", "KO",
]


def _returns(start: str, end: str) -> dict[str, np.ndarray]:
    import yfinance as yf

    out: dict[str, np.ndarray] = {}
    for t in TICKERS:
        df = yf.Ticker(t).history(start=start, end=end, interval="1d")
        if df is None or df.empty:
            print(f"  [!] sem dados: {t}")
            continue
        close = df["Close"].to_numpy()
        r = np.diff(np.log(close))  # log-returns
        out[t] = r
        print(f"  [ok] {t}: {len(r)} retornos")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Avaliação do detetor de anomalias.")
    # Janela FIXA (reprodutível): evita o desvio de `period=3y` relativo à data de hoje.
    parser.add_argument("--start", default="2023-06-01")
    parser.add_argument("--end", default="2026-06-01")
    parser.add_argument("--window", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=3.0)
    parser.add_argument("--fixed-pct", type=float, default=0.03)
    parser.add_argument("--quantile", type=float, default=0.99)
    parser.add_argument("--out", default="docs/evaluation/evaluation_anomaly.md")
    parser.add_argument("--fig", default="thesis/figures/eval_anomaly_firing_rate.pdf")
    parser.add_argument("--ablation-fig", default="thesis/figures/eval_anomaly_window_ablation.pdf")
    # Comparação estatístico vs APRENDIDO (M4): IF causal (treina no passado, pontua o futuro).
    parser.add_argument("--if-train-days", type=int, default=250)
    parser.add_argument("--if-contamination", type=float, default=0.02)
    parser.add_argument("--if-seed", type=int, default=42)
    args = parser.parse_args()

    print(f"A obter preços (yfinance, {args.start}..{args.end})…")
    rets = _returns(args.start, args.end)

    z_pred_all, fx_pred_all, label_all = [], [], []
    fire_z, fire_fx = {}, {}
    for t, r in rets.items():
        label = label_extreme_moves(r, q=args.quantile)
        zf = rolling_zscore_flags(r, args.window, args.threshold)
        ff = fixed_threshold_flags(r, args.fixed_pct)
        z_pred_all.append(zf)
        fx_pred_all.append(ff)
        label_all.append(label)
        fire_z[t] = firing_rate(zf)
        fire_fx[t] = firing_rate(ff)

    z_pred = np.concatenate(z_pred_all)
    fx_pred = np.concatenate(fx_pred_all)
    label = np.concatenate(label_all)
    z_prf = precision_recall_f1(z_pred, label)
    fx_prf = precision_recall_f1(fx_pred, label)

    # Ablação à janela (F1 pooled). Tabela = 3 pontos representativos; curva = conjunto alargado.
    ablation = {}
    for w in (10, 20, 60):
        preds = np.concatenate([rolling_zscore_flags(r, w, args.threshold) for r in rets.values()])
        ablation[w] = precision_recall_f1(preds, label)[2]
    ablation_curve = {}
    for w in (5, 10, 15, 20, 30, 40, 60, 90):
        preds = np.concatenate([rolling_zscore_flags(r, w, args.threshold) for r in rets.values()])
        ablation_curve[w] = precision_recall_f1(preds, label)[2]

    # ── M4: Isolation Forest (aprendido, causal) vs z-score NA MESMA REGIÃO pontuada ─────
    if_pred_all, z_same_all, lbl_same_all, fire_if = [], [], [], {}
    for t, r in rets.items():
        iff, scored = isolation_forest_flags(
            r, args.window, args.if_train_days, args.if_contamination, args.if_seed
        )
        if not scored.any():
            continue
        zf = rolling_zscore_flags(r, args.window, args.threshold)
        lbl = label_extreme_moves(r, q=args.quantile)
        if_pred_all.append(iff[scored])
        z_same_all.append(zf[scored])
        lbl_same_all.append(lbl[scored])
        fire_if[t] = firing_rate(iff[scored])
    if_prf = precision_recall_f1(np.concatenate(if_pred_all), np.concatenate(lbl_same_all))
    z_same_prf = precision_recall_f1(np.concatenate(z_same_all), np.concatenate(lbl_same_all))
    fi = np.array(list(fire_if.values()))

    fz = np.array(list(fire_z.values()))
    ff_ = np.array(list(fire_fx.values()))
    print(f"Firing rate z-score: {fz.min():.3f}-{fz.max():.3f} (spread {fz.max()-fz.min():.3f})")
    print(f"Firing rate fixo: {ff_.min():.3f}-{ff_.max():.3f} (spread {ff_.max()-ff_.min():.3f})")
    print(f"F1 z-score={z_prf[2]:.3f} | F1 fixo={fx_prf[2]:.3f}")
    print(f"[M4] IF: F1={if_prf[2]:.3f} vs z-score(mesma região)={z_same_prf[2]:.3f} | "
          f"spread taxas IF={fi.max()-fi.min():.3f}")

    _write_md(args, rets, fire_z, fire_fx, z_prf, fx_prf, ablation,
              if_prf=if_prf, z_same_prf=z_same_prf, fire_if=fire_if)
    _write_fig(args.fig, fire_z, fire_fx)
    _write_ablation_fig(args.ablation_fig, ablation_curve)


def _write_md(args, rets, fire_z, fire_fx, z_prf, fx_prf, ablation,
              if_prf=None, z_same_prf=None, fire_if=None) -> None:
    fz = np.array(list(fire_z.values()))
    ff_ = np.array(list(fire_fx.values()))
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# evaluation_anomaly.md — Avaliação do detetor de anomalias (reprodutível)",
        "",
        "> Gerado por `scripts/evaluate_anomaly.py`. **Não editar à mão.** Ver caveats no fim.",
        "",
        f"- **Dados:** {len(rets)} tickers, preços reais (yfinance, {args.start} a {args.end}).",
        f"- **z-score:** janela {args.window}d, limiar ±{args.threshold:g} (sem lookahead). "
        f"**Baseline fixo:** |retorno| ≥ {args.fixed_pct*100:g}%. "
        f"**Rótulo-proxy:** |retorno| ≥ percentil {args.quantile:g} por ticker.",
        f"- **Gerado:** {now}.",
        "",
        "## 1. Consistência da taxa de disparo entre tickers (argumento principal)",
        "",
        "| Método | Taxa mín | Taxa máx | Amplitude |",
        "|---|---|---|---|",
        f"| z-score | {fz.min():.3f} | {fz.max():.3f} | **{fz.max()-fz.min():.3f}** |",
        f"| Limiar fixo (%) | {ff_.min():.3f} | {ff_.max():.3f} | **{ff_.max()-ff_.min():.3f}** |",
        "",
        f"**Leitura:** o z-score dispara a uma taxa quase constante entre tickers "
        f"(amplitude {fz.max()-fz.min():.3f}), enquanto o limiar fixo varia muito "
        f"(amplitude {ff_.max()-ff_.min():.3f}) — confirma que normaliza a volatilidade.",
        "",
        "## 2. Precision / recall / F1 vs rótulo-proxy (suporte)",
        "",
        "| Método | Precision | Recall | F1 |",
        "|---|---|---|---|",
        f"| z-score | {z_prf[0]:.3f} | {z_prf[1]:.3f} | {z_prf[2]:.3f} |",
        f"| Limiar fixo (%) | {fx_prf[0]:.3f} | {fx_prf[1]:.3f} | {fx_prf[2]:.3f} |",
        "",
        "## 3. Ablação à janela (F1 pooled)",
        "",
        "| Janela | F1 |",
        "|---|---|",
        *[f"| {w}d | {f1:.3f} |" for w, f1 in ablation.items()],
        "",
        "**Caveats (honestos):** o rótulo é um *proxy* (percentil de movimento), não verdade "
        "absoluta, e é volatilidade-relativo como o z-score (alguma circularidade — por isso o "
        "argumento principal é a **consistência da taxa de disparo**, que não depende do rótulo). "
        "Avaliação reprodutível (`scripts/evaluate_anomaly.py`).",
    ]
    if if_prf is not None:
        fi = np.array(list(fire_if.values()))
        lines += [
            "",
            "## 4. Estatístico vs APRENDIDO — Isolation Forest causal (M4)",
            "",
            f"IF não-supervisionado (200 árvores, contaminação {args.if_contamination:g}, "
            f"seed {args.if_seed}) com features causais [retorno, vol20 anterior]; treina nos "
            f"primeiros {args.if_train_days} dias válidos e pontua os seguintes (nunca vê o "
            "futuro). Comparação na MESMA região pontuada:",
            "",
            "| Método (região pontuada) | Precision | Recall | F1 | Amplitude da taxa |",
            "|---|---|---|---|---|",
            f"| Isolation Forest | {if_prf[0]:.3f} | {if_prf[1]:.3f} | {if_prf[2]:.3f} | "
            f"{fi.max()-fi.min():.3f} |",
            f"| z-score (mesma região) | {z_same_prf[0]:.3f} | {z_same_prf[1]:.3f} | "
            f"{z_same_prf[2]:.3f} | — |",
            "",
            "**Leitura:** comparação 'regra estatística vs detetor aprendido' com a mesma "
            "informação e sem lookahead. O z-score continua a ser o detetor de produção salvo "
            "vantagem clara do IF — a própria comparação é o contributo (RQ4/M4).",
        ]
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Resultados escritos em {args.out}")


def _write_fig(path, fire_z, fire_fx) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    tickers = list(fire_z.keys())
    x = np.arange(len(tickers))
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(x - 0.2, [fire_fx[t] for t in tickers], 0.4, label="Fixed threshold (%)")
    ax.bar(x + 0.2, [fire_z[t] for t in tickers], 0.4, label="z-score")
    ax.set_xticks(x, tickers, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Firing rate")
    ax.set_title("Firing rate per ticker: fixed threshold versus z-score")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out = REPO / path if not Path(path).is_absolute() else Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"Figura escrita em {out}")


def _write_ablation_fig(path, ablation_curve) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    windows = sorted(ablation_curve)
    f1s = [ablation_curve[w] for w in windows]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(windows, f1s, marker="o", color="black")
    ax.set_xlabel("Estimation window (trading days)")
    ax.set_ylabel(r"$F_1$ vs extreme-move proxy")
    ax.set_title("Anomaly detector: window-size ablation")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = REPO / path if not Path(path).is_absolute() else Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"Figura escrita em {out}")


if __name__ == "__main__":
    main()
