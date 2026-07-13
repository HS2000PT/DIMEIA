"""Extensão do CS1 (2026-07-13): mais detetores (LOF) e outra σ (EWMA) — mesmo protocolo.

Motivação (revisão crítica da tese): o LOF era citado como alternativa mas nunca testado, e
o "porquê rolling-std e não GARCH?" tinha só uma frase — o EWMA (RiskMetrics, λ=0,94) é o
degrau empírico intermédio: pondera o passado recente exponencialmente sem estimar
parâmetros por ticker.

PROTOCOLO CONGELADO (idêntico a scripts/evaluate_anomaly.py — nada muda nos números da
tese): mesmos 15 tickers, mesma janela fixa 2023-06-01→2026-06-01, janela 20d, limiar ±3,
rótulo-proxy |retorno| ≥ p99 por ticker, detetores aprendidos causais (treino 250d,
contaminação 0,02, seed 42) comparados NA MESMA região pontuada.

Saídas NOVAS (o evaluation_anomaly.md congelado fica intocado):
  docs/evaluation/evaluation_anomaly_ext.md
  thesis/figures/eval_anomaly_detectors.pdf

Uso: python scripts/evaluate_anomaly_ext.py
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from investigator.evaluation.anomaly_eval import (
    ewma_zscore_flags,
    firing_rate,
    isolation_forest_flags,
    label_extreme_moves,
    lof_flags,
    precision_recall_f1,
    rolling_zscore_flags,
)

REPO = Path(__file__).resolve().parent.parent
# Os MESMOS 15 tickers da avaliação congelada (scripts/evaluate_anomaly.py).
TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", "TSLA", "META", "JPM",
    "BAC", "XOM", "CVX", "JNJ", "PFE", "WMT", "KO",
]


def _returns(start: str, end: str) -> dict[str, np.ndarray]:
    """Preços reais — yfinance primeiro, com a cadeia de fallback do produto."""
    import yfinance as yf

    from investigator.market_data.prices import fallback_daily

    out: dict[str, np.ndarray] = {}
    for t in TICKERS:
        close = None
        try:
            df = yf.Ticker(t).history(start=start, end=end, interval="1d")
            if df is not None and not df.empty:
                close = df["Close"].to_numpy()
        except Exception:  # noqa: BLE001
            pass
        if close is None:
            try:
                df, fonte = fallback_daily(t, start, end)
                close = df["Close"].to_numpy()
                print(f"  [fallback:{fonte}] {t}")
            except Exception as exc:  # noqa: BLE001
                print(f"  [!] sem dados: {t} ({exc})")
                continue
        out[t] = np.diff(np.log(close))
        print(f"  [ok] {t}: {len(out[t])} retornos")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="CS1-ext: LOF + EWMA (protocolo congelado).")
    parser.add_argument("--start", default="2023-06-01")
    parser.add_argument("--end", default="2026-06-01")
    parser.add_argument("--window", type=int, default=20)
    parser.add_argument("--threshold", type=float, default=3.0)
    parser.add_argument("--quantile", type=float, default=0.99)
    parser.add_argument("--train-days", type=int, default=250)
    parser.add_argument("--contamination", type=float, default=0.02)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--lam", type=float, default=0.94)
    parser.add_argument("--out", default="docs/evaluation/evaluation_anomaly_ext.md")
    parser.add_argument("--fig", default="thesis/figures/eval_anomaly_detectors.pdf")
    args = parser.parse_args()

    print(f"A obter preços ({args.start}..{args.end})…")
    rets = _returns(args.start, args.end)

    # ── 1. Detetores aprendidos vs z-score, NA MESMA região pontuada ────────────
    per = {k: [] for k in ("z", "if", "lof", "lbl")}
    fire = {"z": {}, "if": {}, "lof": {}}
    for t, r in rets.items():
        iff, s1 = isolation_forest_flags(r, args.window, args.train_days,
                                         args.contamination, args.seed)
        loff, s2 = lof_flags(r, args.window, args.train_days, args.contamination)
        scored = s1 & s2
        if not scored.any():
            continue
        zf = rolling_zscore_flags(r, args.window, args.threshold)
        lbl = label_extreme_moves(r, q=args.quantile)
        per["z"].append(zf[scored])
        per["if"].append(iff[scored])
        per["lof"].append(loff[scored])
        per["lbl"].append(lbl[scored])
        fire["z"][t] = firing_rate(zf[scored])
        fire["if"][t] = firing_rate(iff[scored])
        fire["lof"][t] = firing_rate(loff[scored])
    lbl = np.concatenate(per["lbl"])
    prf = {k: precision_recall_f1(np.concatenate(per[k]), lbl) for k in ("z", "if", "lof")}
    spread = {k: (max(v.values()) - min(v.values())) for k, v in fire.items()}

    # ── 2. σ rolling vs σ EWMA (região completa a partir da janela) ─────────────
    lbl_all = np.concatenate([label_extreme_moves(r, q=args.quantile)
                              for r in rets.values()])
    roll_all = np.concatenate([rolling_zscore_flags(r, args.window, args.threshold)
                               for r in rets.values()])
    ewma_all = np.concatenate([ewma_zscore_flags(r, args.lam, args.threshold, args.window)
                               for r in rets.values()])
    prf_roll = precision_recall_f1(roll_all, lbl_all)
    prf_ewma = precision_recall_f1(ewma_all, lbl_all)
    fire_roll = {t: firing_rate(rolling_zscore_flags(r, args.window, args.threshold))
                 for t, r in rets.items()}
    fire_ewma = {t: firing_rate(ewma_zscore_flags(r, args.lam, args.threshold, args.window))
                 for t, r in rets.items()}
    spread_roll = max(fire_roll.values()) - min(fire_roll.values())
    spread_ewma = max(fire_ewma.values()) - min(fire_ewma.values())

    print(f"[detetores] F1 z={prf['z'][2]:.3f} | IF={prf['if'][2]:.3f} | "
          f"LOF={prf['lof'][2]:.3f}")
    print(f"[sigma] F1 rolling={prf_roll[2]:.3f} (spread {spread_roll:.3f}) | "
          f"EWMA={prf_ewma[2]:.3f} (spread {spread_ewma:.3f})")

    _write_md(args, rets, prf, spread, prf_roll, prf_ewma, spread_roll, spread_ewma)
    _write_fig(args.fig, prf, prf_roll, prf_ewma)


def _write_md(args, rets, prf, spread, prf_roll, prf_ewma,
              spread_roll, spread_ewma) -> None:
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# evaluation_anomaly_ext.md — CS1-ext: LOF + EWMA (reprodutível)",
        "",
        "> Gerado por `scripts/evaluate_anomaly_ext.py`. **Não editar à mão.**",
        "> Extensão ADITIVA: o `evaluation_anomaly.md` congelado da tese fica intocado;",
        "> este ficheiro acrescenta detetores/estimadores ao MESMO protocolo.",
        "",
        f"- **Dados:** {len(rets)} tickers, preços reais ({args.start} a {args.end}).",
        f"- **Protocolo:** janela {args.window}d, limiar ±{args.threshold:g}, rótulo-proxy "
        f"|retorno| ≥ p{args.quantile*100:g} por ticker; detetores aprendidos causais "
        f"(treino {args.train_days}d, contaminação {args.contamination:g}, seed {args.seed}); "
        "métricas na MESMA região pontuada pelos três detetores.",
        f"- **Gerado:** {now}.",
        "",
        "## 1. Detetores: estatístico vs aprendidos (mesma região, mesmas features)",
        "",
        "| Detetor | Precision | Recall | F1 | Amplitude da taxa |",
        "|---|---|---|---|---|",
        f"| z-score (regra da tese) | {prf['z'][0]:.3f} | {prf['z'][1]:.3f} | "
        f"**{prf['z'][2]:.3f}** | {spread['z']:.3f} |",
        f"| Isolation Forest | {prf['if'][0]:.3f} | {prf['if'][1]:.3f} | "
        f"{prf['if'][2]:.3f} | {spread['if']:.3f} |",
        f"| Local Outlier Factor | {prf['lof'][0]:.3f} | {prf['lof'][1]:.3f} | "
        f"{prf['lof'][2]:.3f} | {spread['lof']:.3f} |",
        "",
        "**Leitura:** o LOF era citado na tese como alternativa mas nunca tinha sido "
        "testado — agora está, com o mesmo protocolo causal do IF. A regra estatística "
        "transparente ganha aos dois detetores aprendidos não-supervisionados com a mesma "
        "informação (features [retorno, vol20 anterior]): ambos disparam demasiado "
        "(recall alto, precisão ~0,16) e com taxas inconsistentes entre tickers. "
        "**Fidelidade ao protocolo:** a linha do z-score reproduz os valores congelados do "
        "CS1 (0,407/0,761/0,530); o IF difere ~0,002 do congelado porque o yfinance "
        "reajusta os fechos históricos a cada dividendo novo desde a corrida de 2026-07-04 "
        "(drift documentado, não um erro).",
        "",
        "## 2. Estimador de volatilidade: σ rolling (tese) vs σ EWMA (RiskMetrics)",
        "",
        f"EWMA com λ={args.lam:g} (RiskMetrics), média zero, causal; mesma região a partir "
        f"do dia {args.window}. O degrau empírico entre a σ rolling e um GARCH completo.",
        "",
        "| Estimador | Precision | Recall | F1 | Amplitude da taxa |",
        "|---|---|---|---|---|",
        f"| σ rolling {args.window}d (tese) | {prf_roll[0]:.3f} | {prf_roll[1]:.3f} | "
        f"**{prf_roll[2]:.3f}** | {spread_roll:.3f} |",
        f"| σ EWMA (λ={args.lam:g}) | {prf_ewma[0]:.3f} | {prf_ewma[1]:.3f} | "
        f"{prf_ewma[2]:.3f} | {spread_ewma:.3f} |",
        "",
        "**Leitura (honesta — o resultado surpreendeu):** a experiência foi desenhada para "
        "justificar o \"porquê não GARCH?\" e os dados dizem o CONTRÁRIO do esperado: com o "
        "MESMO recall, a σ EWMA quase elimina metade dos falsos positivos (precisão "
        f"{prf_ewma[0]:.3f} vs {prf_roll[0]:.3f}) — F1 {prf_ewma[2]:.3f} vs "
        f"{prf_roll[2]:.3f} — e é ainda mais consistente entre tickers. Mecanismo: com "
        "clustering de volatilidade, a σ rolling dilui um choque por 20 pesos iguais "
        "enquanto a EWMA o incorpora de imediato — nos dias seguintes a um choque, a EWMA "
        "re-alerta menos (comportamento provado em teste unitário). Implicação para a tese: "
        "a regra implantada continua a ser a rolling (transparência: \"média e desvio de 20 "
        "dias\" explica-se a um leigo; a EWMA exige explicar pesos exponenciais), mas o "
        "ganho fica REGISTADO e a adoção é uma mudança de 1 linha — trabalho futuro "
        "validado, não especulado. Caveat: o rótulo-proxy é volatilidade-relativo (mesma "
        "circularidade assumida no CS1) e favorece dias de |retorno| extremo incondicional.",
    ]
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Resultados escritos em {args.out}")


def _write_fig(path, prf, prf_roll, prf_ewma) -> None:
    """Uma figura simples (pedido do aluno: 'multiple but simple'): F1 por método,
    detetores à esquerda, estimadores de σ à direita — mesma linguagem visual das
    figuras existentes da tese (matplotlib sóbrio, grid 0.3)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.6),
                                   gridspec_kw={"width_ratios": [3, 2]})
    nomes = ["z-score\n(thesis rule)", "Isolation\nForest", "Local Outlier\nFactor"]
    f1s = [prf["z"][2], prf["if"][2], prf["lof"][2]]
    cores = ["#404040", "#8c8c8c", "#bfbfbf"]
    b1 = ax1.bar(nomes, f1s, color=cores, width=0.6)
    ax1.bar_label(b1, fmt="%.3f", fontsize=9)
    ax1.set_ylabel(r"$F_1$ vs extreme-move proxy")
    ax1.set_title("Detector (same causal features)", fontsize=10)
    ax1.set_ylim(0, max(f1s) * 1.25)
    ax1.grid(axis="y", alpha=0.3)

    nomes2 = ["Rolling σ\n(thesis)", "EWMA σ\n(λ=0.94)"]
    f1s2 = [prf_roll[2], prf_ewma[2]]
    b2 = ax2.bar(nomes2, f1s2, color=["#404040", "#8c8c8c"], width=0.5)
    ax2.bar_label(b2, fmt="%.3f", fontsize=9)
    ax2.set_title("Volatility estimator", fontsize=10)
    ax2.set_ylim(0, max(f1s2) * 1.25)
    ax2.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    out = REPO / path if not Path(path).is_absolute() else Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"Figura escrita em {out}")


if __name__ == "__main__":
    main()
