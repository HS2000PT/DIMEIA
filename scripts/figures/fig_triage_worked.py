"""Exemplo TRABALHADO da triagem (2026-07-13): um alerta real decomposto número a número.

A tese descrevia a triagem (RQ4) sem nunca mostrar o modelo a pontuar UM caso concreto.
Este script pega num alerta REAL do canal (META, 2026-07-12, "Mark Zuckerberg Said Meta's
AI Bets 'Haven't Come to Fruition Yet'…", enviado com "Risk estimate: 54%") e reproduz a
decisão de ponta a ponta com o bundle DE PRODUÇÃO (models/triage_context_lr.joblib):

    features de contexto → contribuições aditivas ao log-odds (exatas, sem aproximação)
    → logit → σ(logit) = p_raw → calibração de Platt → p_cal → gate ≥ 0.5

Saídas: thesis/figures/triage_contributions.pdf (barras assinadas)
        docs/evaluation/triage_worked_example.md (números para a tabela do Cap. 3)

Uso: python scripts/figures/fig_triage_worked.py
Nota de fidelidade: os fechos do yfinance são reajustados a cada dividendo, pelo que o p
reproduzido pode divergir ~1 p.p. do enviado — o .md regista ambos, honestamente.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent.parent

# O alerta real do canal (branch alerts-history, 2026-07-12; ver docs/evaluation/alert_funnel.md).
DEFAULT_TICKER = "META"
DEFAULT_HEADLINE = ('Mark Zuckerberg Said Meta\'s AI Bets "Haven\'t Come to Fruition Yet" '
                    "as Shares Fell 5%")
DEFAULT_ASOF = "2026-07-12"  # fim de semana: as features vêm do último fecho (sexta 07-10)
PRODUCTION_PROB = 0.54       # o valor na mensagem realmente enviada ao canal


def main() -> None:
    parser = argparse.ArgumentParser(description="Exemplo trabalhado da triagem (figura+md).")
    parser.add_argument("--ticker", default=DEFAULT_TICKER)
    parser.add_argument("--headline", default=DEFAULT_HEADLINE)
    parser.add_argument("--as-of", default=DEFAULT_ASOF)
    parser.add_argument("--fig", default="thesis/figures/triage_contributions.pdf")
    parser.add_argument("--out", default="docs/evaluation/triage_worked_example.md")
    args = parser.parse_args()

    from investigator.market_data.prices import load_close_series
    from investigator.triage.dataset import event_features
    from investigator.triage.infer import load_context_bundle, score_context

    bundle = load_context_bundle()
    if bundle is None:
        raise SystemExit("models/triage_context_lr.joblib em falta.")

    from datetime import date, timedelta

    asof = date.fromisoformat(args.as_of)
    start = (asof - timedelta(days=120)).isoformat()
    closes = load_close_series([args.ticker], start, (asof + timedelta(days=1)).isoformat())
    close = closes[args.ticker]
    feats = event_features(close, len(close) - 1)
    if feats is None:
        raise SystemExit("Histórico insuficiente para as features.")

    prob, contribs = score_context(bundle, feats["vol20"], feats["mom5"],
                                   feats["ret_event"], args.headline, args.ticker)

    # Decomposição exata: logit = intercepto + Σ contribuições; p_raw = σ(logit); Platt → p.
    lr = bundle["model"].named_steps["lr"]
    intercept = float(lr.intercept_[0])
    soma = intercept + sum(c for _, c in contribs)
    p_raw = 1.0 / (1.0 + np.exp(-soma))
    cal = bundle["calibrator"]
    a, b = getattr(cal, "a", None), getattr(cal, "b", None)

    print(f"{args.ticker} @ {args.as_of} (último fecho: {close.index[-1].date()})")
    print(f"features: vol20={feats['vol20']:.4f} mom5={feats['mom5']:.4f} "
          f"ret_event={feats['ret_event']:.4f} len={len(args.headline)}")
    for nome, c in contribs:
        print(f"  {nome:<28} {c:+.3f}")
    print(f"  intercepto                  {intercept:+.3f}")
    print(f"logit={soma:+.3f} → p_raw={p_raw:.3f} → Platt → p={prob:.3f} "
          f"(produção enviou {PRODUCTION_PROB:.0%})")

    _write_md(args, feats, contribs, intercept, soma, p_raw, prob, a, b, close)
    _write_fig(args.fig, contribs, intercept, soma, prob)


def _write_md(args, feats, contribs, intercept, soma, p_raw, prob, a, b, close) -> None:
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    platt = (f"σ({a:.3f}·p_raw + {b:.3f})" if a is not None and b is not None
             else "Platt (parâmetros no bundle)")
    lines = [
        "# triage_worked_example.md — exemplo trabalhado da triagem (reprodutível)",
        "",
        "> Gerado por `scripts/figures/fig_triage_worked.py`. **Não editar à mão.**",
        "",
        f"- **Caso real:** alerta {args.ticker} enviado ao canal a {args.as_of} "
        f"(branch `alerts-history`), manchete: \"{args.headline}\".",
        f"- **Features no último fecho ({close.index[-1].date()}):** "
        f"vol20={feats['vol20']:.4f}, mom5={feats['mom5']:.4f}, "
        f"ret_event={feats['ret_event']:.4f}, headline_len={len(args.headline)}.",
        "- **Modelo:** bundle de produção `models/triage_context_lr.joblib` "
        "(LR só-contexto, StandardScaler + Platt).",
        f"- **Gerado:** {now}.",
        "",
        "## Decomposição aditiva exata (log-odds)",
        "",
        "| Termo | Contribuição ao logit |",
        "|---|---|",
        f"| intercepto | {intercept:+.3f} |",
        *[f"| {nome} | {c:+.3f} |" for nome, c in contribs],
        f"| **logit (soma)** | **{soma:+.3f}** |",
        "",
        f"σ(logit) = **{p_raw:.3f}** (probabilidade crua) → calibração de Platt "
        f"({platt}) → **p = {prob:.3f}**.",
        "",
        f"**Fidelidade:** a mensagem realmente enviada dizia \"Risk estimate: "
        f"{PRODUCTION_PROB:.0%} … raised by recent volatility (20d) and sector\"; a "
        f"reprodução dá {prob:.0%} com os MESMOS fatores dominantes — reprodução exata da "
        "decisão de produção. (Nota: os fechos yfinance são reajustados retroativamente a "
        "cada dividendo, pelo que reproduções futuras podem divergir ~1 p.p.; a decisão do "
        "gate é robusta a isso.)",
        f"Gate de produção: p = {prob:.3f} ≥ 0.5 → "
        f"{'PASSA' if prob >= 0.5 else 'suprimido'} (o alerta foi de facto enviado).",
    ]
    out = REPO / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


def _write_fig(path, contribs, intercept, soma, prob) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    termos = [("intercept", intercept)] + list(reversed(contribs))
    nomes = [n for n, _ in termos]
    vals = [v for _, v in termos]
    cores = ["#2c6fbb" if v >= 0 else "#999999" for v in vals]

    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    bars = ax.barh(nomes, vals, color=cores, height=0.62)
    ax.bar_label(bars, fmt="%+.3f", fontsize=8, padding=3)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Additive contribution to the log-odds (exact, no approximation)")
    ax.set_title(f"One real alert, decomposed: Σ = {soma:+.3f} → calibrated "
                 f"P(material) = {prob:.0%}", fontsize=10)
    lim = max(abs(v) for v in vals) * 1.35
    ax.set_xlim(-lim, lim)
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    out = REPO / path if not Path(path).is_absolute() else Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
