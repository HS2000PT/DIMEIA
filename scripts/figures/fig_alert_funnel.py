"""Funil de produção REAL (2026-07-13): da manchete relevante ao alerta enviado.

A história da seletividade com números verdadeiros, lidos da branch de dados
`alerts-history` (a MESMA fonte da app): quantas manchetes RELEVANTES o runner capturou
para a KB viva (todas as que passaram o filtro de relevância) vs quantos alertas o canal
recebeu de facto — e por ticker, que mostra o ponto-chave: as notícias fluem para os 10
tickers, mas os gates de qualidade (frescura ≤2d, precedente com cosseno ≥0.45, triagem
P≥0.5, teto 2/ticker/dia, dedup) só deixam passar evidência forte.

Saídas: thesis/figures/alert_funnel.pdf
        docs/evaluation/alert_funnel.md (o snapshot com data — os números da tese citam-no)

Uso: python scripts/figures/fig_alert_funnel.py            (lê da branch remota)
     python scripts/figures/fig_alert_funnel.py --local DIR  (lê ficheiros já descarregados)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent.parent
RAW = "https://raw.githubusercontent.com/HS2000PT/DIMEIA/alerts-history"

GATES = ("relevance filter → capture", "freshness ≤ 2d", "precedent cosine ≥ 0.45",
         "learned triage P ≥ 0.5", "cap 2/ticker/day + dedup")


def _load_jsonl(text: str) -> list[dict]:
    return [json.loads(ln) for ln in text.splitlines() if ln.strip()]


def _fetch(name: str, local: str | None) -> list[dict]:
    if local:
        return _load_jsonl(Path(local, name).read_text(encoding="utf-8"))
    import requests

    resp = requests.get(f"{RAW}/{name}", timeout=15)
    resp.raise_for_status()
    return _load_jsonl(resp.text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Funil de produção (figura+md).")
    parser.add_argument("--local", default=None,
                        help="diretório com alerts_history.jsonl e live_pending.jsonl")
    parser.add_argument("--fig", default="thesis/figures/alert_funnel.pdf")
    parser.add_argument("--out", default="docs/evaluation/alert_funnel.md")
    args = parser.parse_args()

    pend = _fetch("live_pending.jsonl", args.local)
    hist = _fetch("alerts_history.jsonl", args.local)
    news = [h for h in hist if h.get("kind") == "news"]

    cap_por_ticker = Counter(p["ticker"] for p in pend)
    env_por_ticker = Counter(h["ticker"] for h in news)
    datas = sorted({p["date"] for p in pend} | {h["date"] for h in news})
    total_cap, total_env = len(pend), len(news)
    print(f"capturadas: {total_cap} ({len(cap_por_ticker)} tickers) | "
          f"enviadas: {total_env} ({len(env_por_ticker)} tickers) | "
          f"seletividade {total_cap / max(total_env, 1):.0f}:1")

    _write_md(args, cap_por_ticker, env_por_ticker, total_cap, total_env, datas)
    _write_fig(args.fig, cap_por_ticker, env_por_ticker, total_cap, total_env)


def _write_md(args, cap, env, total_cap, total_env, datas) -> None:
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    # Cedo na janela viva (sem pendentes maturados e sem histórico de notícias) `datas`
    # vem vazio — degradar com graça em vez de rebentar com IndexError.
    janela = f"{datas[0]} a {datas[-1]}" if datas else "n/a (sem dados ainda)"
    lines = [
        "# alert_funnel.md — funil de produção real (snapshot)",
        "",
        "> Gerado por `scripts/figures/fig_alert_funnel.py` a partir da branch de dados",
        "> `alerts-history` (a mesma fonte da app). **Não editar à mão.** Snapshot com data:",
        "> os números crescem com o canal vivo; a tese cita ESTE snapshot.",
        "",
        f"- **Janela coberta:** notícias datadas de {janela}.",
        f"- **Capturadas (relevantes, únicas):** {total_cap} manchetes "
        f"(passaram o filtro de relevância; TODAS entram na KB viva como pendentes).",
        f"- **Alertas de notícia enviados ao canal:** {total_env} "
        f"(seletividade {total_cap / max(total_env, 1):.0f}:1).",
        f"- **Gates entre um número e o outro:** {'; '.join(GATES)}.",
        f"- **Gerado:** {now}.",
        "",
        "| Ticker | Relevantes capturadas | Alertas enviados |",
        "|---|---|---|",
        *[f"| {t} | {cap[t]} | {env.get(t, 0)} |"
          for t in sorted(cap, key=lambda t: -cap[t])],
        f"| **Total** | **{total_cap}** | **{total_env}** |",
        "",
        "**Leitura:** as notícias relevantes fluem para os 10 tickers da watchlist, mas os "
        "gates de evidência (precedente forte + triagem aprendida) concentram os alertas "
        "onde a evidência é forte — anti-fadiga por desenho, não por acaso. Nota honesta: "
        "nos 2 primeiros dias o teto de 2/ticker/dia ainda não estava em produção "
        "(entrou a 2026-07-11), por isso há dias antigos com mais alertas.",
    ]
    out = REPO / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


def _write_fig(path, cap, env, total_cap, total_env) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import numpy as np

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    tickers = sorted(cap, key=lambda t: -cap[t])
    y = np.arange(len(tickers))
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    b1 = ax.barh(y + 0.21, [cap[t] for t in tickers], 0.42,
                 color="#9ecae1", label="Relevant headlines captured")
    b2 = ax.barh(y - 0.21, [env.get(t, 0) for t in tickers], 0.42,
                 color="#2c6fbb", label="Alerts actually sent")
    ax.bar_label(b1, fontsize=7, padding=2)
    ax.bar_label(b2, fontsize=7, padding=2)
    ax.set_yticks(y, tickers, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("Count over the live window")
    ax.set_title(f"Production selectivity: {total_cap} relevant headlines → "
                 f"{total_env} alerts ({total_cap / max(total_env, 1):.0f}:1)", fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    out = REPO / path if not Path(path).is_absolute() else Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
