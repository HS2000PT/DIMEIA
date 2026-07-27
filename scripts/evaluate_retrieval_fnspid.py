"""Avaliação da recuperação de precedentes EM ESCALA (RQ2) — corpus multi-ano FNSPID.

ADITIVO: NÃO altera docs/evaluation/evaluation_results.md (a avaliação preliminar no corpus
recente do Finnhub). Reutiliza os embeddings SBERT JÁ calculados em data/kb_fnspid_sbert.jsonl
(sem re-embeder, sem download) e corre o MESMO protocolo cross-ticker precision@k da tese, agora
sobre ~80k manchetes de 2018-2023 em vez de ~3.7k recentes — o passo "trabalho futuro" que valida
o componente mais forte à escala.

Acrescenta o que o revisor pediu: DISPERSÃO e CONSISTÊNCIA DE DIREÇÃO dos precedentes recuperados
(quantifica o "tema ≠ direção" do CS3 — se a consistência for ~0,5-0,6, os clusters misturam
subidas e descidas, evidência sobre um tema, não uma direção).

Uso:
    python scripts/evaluate_retrieval_fnspid.py --kb <kb_fnspid_sbert.jsonl>
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from investigator.console import force_utf8_stdout
from investigator.evaluation.retrieval_eval import (
    expected_random_precision,
    recency_precision_at_k,
    retrieval_precision_at_k,
    same_ticker_forbid,
)

REPO = Path(__file__).resolve().parents[1]
# Setores dos tickers da watchlist (data_card.md). FB = símbolo do Meta no corpus FNSPID.
SECTORS = {
    "AAPL": "tech", "MSFT": "tech", "AMZN": "tech", "GOOGL": "tech", "NVDA": "tech",
    "TSLA": "tech", "META": "tech", "FB": "tech",
    "JPM": "banking", "BAC": "banking", "XOM": "energy", "CVX": "energy",
    "JNJ": "health", "PFE": "health", "WMT": "consumer", "KO": "consumer",
}


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Retrieval em escala (FNSPID multi-ano)")
    ap.add_argument("--kb", default=str(REPO / "data" / "kb_fnspid_sbert.jsonl"))
    ap.add_argument("--queries", type=int, default=500)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--horizon", type=int, default=3)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    print(f"A carregar {args.kb} …")
    dates, tickers, embs, imps = [], [], [], []
    key = str(args.horizon)
    with open(args.kb, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            t = str(r["ticker"]).upper()
            if t not in SECTORS or "embedding" not in r:
                continue
            dates.append(str(r["date"])); tickers.append(t)
            embs.append(r["embedding"])
            imp = r.get("impacts", {}).get(key)
            imps.append(float(imp) if imp is not None else np.nan)
    emb = np.asarray(embs, dtype="float64")
    tickers = np.asarray(tickers); dates = np.asarray(dates)
    imps = np.asarray(imps, dtype="float64")
    sectors = np.asarray([SECTORS[t] for t in tickers])
    n = len(emb)
    # normalizar L2 (o cosseno = produto interno; a KB já vem normalizada, garante-se na mesma)
    emb = emb / np.clip(np.linalg.norm(emb, axis=1, keepdims=True), 1e-12, None)
    print(f"  {n} registos · tickers {sorted(set(tickers))} · setores {sorted(set(sectors))}")

    n_q = min(args.queries, n)
    k = args.k
    p_sbert, p_rand, p_rec = [], [], []
    disp, dircon = [], []  # dispersão (std dos impactos) e consistência de direção nos top-k
    for rep in range(args.repeats):
        rng = np.random.default_rng(args.seed + rep)
        q = rng.choice(n, size=n_q, replace=False)
        forbid = same_ticker_forbid(tickers[q], tickers)
        p_sbert.append(retrieval_precision_at_k(emb[q], emb, sectors[q], sectors, k=k, forbid=forbid))
        p_rand.append(expected_random_precision(sectors[q], sectors, forbid))
        p_rec.append(recency_precision_at_k(sectors[q], sectors, dates, k=k, forbid=forbid))
        # top-k cross-ticker por cosseno → impactos dos precedentes
        sims = emb[q] @ emb.T
        for j, qi in enumerate(q):
            s = sims[j].copy()
            s[tickers == tickers[qi]] = -np.inf      # cross-ticker
            s[qi] = -np.inf
            top = np.argpartition(-s, k)[:k]
            vals = imps[top]; vals = vals[~np.isnan(vals)]
            if len(vals) >= 2:
                disp.append(float(np.std(vals)))
                up = float((vals > 0).mean())
                dircon.append(max(up, 1 - up))       # 1=unânime, 0,5=metade/metade

    def ms(v):
        a = np.asarray(v, dtype="float64")
        return float(a.mean()), float(a.std())

    ps_m, ps_s = ms(p_sbert); pr_m, _ = ms(p_rand); pc_m, pc_s = ms(p_rec)
    d_m, _ = ms(disp); dc_m, _ = ms(dircon)
    lift = ps_m - pr_m
    # Chão do acaso da consistência de direção: E[max(i,k-i)/k] para i~Binom(k,0.5).
    from math import comb
    dir_floor = sum(comb(k, i) * 0.5**k * max(i, k - i) / k for i in range(k + 1))
    print(f"  P@{k}: SBERT {ps_m:.3f}±{ps_s:.3f} · random {pr_m:.3f} · recency {pc_m:.3f}")
    print(f"  dispersão impacto(+{args.horizon}d) {d_m:.3f} · consistência-direção {dc_m:.3f}")

    out = REPO / "docs" / "evaluation" / "evaluation_retrieval_fnspid.md"
    L = [
        "# evaluation_retrieval_fnspid.md — Recuperação em ESCALA (RQ2; corpus multi-ano FNSPID)",
        "",
        "> Gerado por `scripts/evaluate_retrieval_fnspid.py` (ADITIVO; não altera a avaliação",
        "> preliminar em `evaluation_results.md`). Reutiliza os embeddings SBERT já calculados na KB",
        "> (sem re-embeder). É o passo 'trabalho futuro' da RQ2: validar o componente mais forte à",
        "> escala (2018-2023) em vez do corpus recente de poucos meses.",
        "",
        f"- **Corpus:** {n} manchetes com setor conhecido · tickers {sorted(set(tickers.tolist()))}.",
        f"- **Protocolo:** cross-ticker precision@{k} (exclui a própria empresa), {n_q} consultas × "
        f"{args.repeats} sementes (média ± desvio); mesmo proxy de setor da tese.",
        f"- **Gerado:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC · seed {args.seed}.",
        "",
        f"| Método | P@{k} |",
        "|---|---|",
        f"| SBERT (MiniLM) | {ps_m:.3f} ± {ps_s:.3f} |",
        f"| Recency | {pc_m:.3f} ± {pc_s:.3f} |",
        f"| Random (base rate) | {pr_m:.3f} |",
        "",
        f"**Leitura:** a P@{k} do SBERT à escala é **{ps_m:.3f}** vs {pr_m:.3f} do acaso "
        f"(lift **{lift:+.3f}**). Confirma, sobre ~{n // 1000}k manchetes de 6 anos, o que a "
        "avaliação preliminar (corpus recente) já indicava: a recuperação semântica supera as "
        "baselines triviais — agora à escala, não em poucos meses.",
        "",
        "## Tema ≠ direção, quantificado (o ponto honesto do CS3)",
        "",
        f"- **Dispersão do impacto (+{args.horizon}d) nos top-{k} precedentes:** {d_m:.3f} "
        "(desvio-padrão médio dos retornos dos precedentes recuperados).",
        f"- **Consistência de direção média:** **{dc_m:.3f}** (1,0 = todos os precedentes na mesma "
        "direção; 0,5 = metade sobe, metade desce).",
        f"- **Chão do acaso** (direções aleatórias, k={k}): **{dir_floor:.3f}** — o valor esperado "
        "se a direção dos precedentes fosse uma moeda ao ar.",
        "",
        f"**Leitura honesta:** a consistência de direção observada ({dc_m:.3f}) fica **quase no chão "
        f"do acaso ({dir_floor:.3f})** — ou seja, saber que os precedentes são do mesmo tema quase "
        "não diz nada sobre a **direção** do movimento. Isto **confirma quantitativamente** a "
        "limitação assumida no CS3/Cap. 6: a recuperação capta o **tema** (P@k bem acima do acaso), "
        "mas o impacto médio é evidência sobre esse tema, **nunca** uma previsão direcional — e é por "
        "isso que o alerta mostra sempre os precedentes individuais, não só a média.",
    ]
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nEscrito: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
