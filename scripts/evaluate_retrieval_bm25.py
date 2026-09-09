"""B1 — Linha de base BM25 na recuperação de precedentes, no protocolo da tese.

A §5.3.2 declara que a linha lexical avaliada é a forma mais elementar da sua família e que
«a comparação com uma função de ordenação bem parametrizada constitui trabalho por realizar,
e é a que tornaria esta conclusão mais forte». Este procedimento fecha essa lacuna.

Protocolo IDÊNTICO ao de `evaluate_retrieval_fnspid.py` — mesmas consultas, mesmas sementes
(42..46), mesmo k, mesma proibição cross-ticker — de modo que a comparação seja emparelhada:
em cada repetição, o SBERT e o BM25 respondem exatamente ao mesmo conjunto de consultas.

Reporta ainda a fração dos lugares preenchidos com pontuação zero, que é o diagnóstico honesto
de quantas vezes o BM25 não encontrou termo comum nenhum e a posição foi ocupada pelo desempate.

Uso:
    python scripts/evaluate_retrieval_bm25.py --kb data/kb_fnspid_sbert.jsonl
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from investigator.console import force_utf8_stdout
from investigator.evaluation.retrieval_bm25 import Bm25Index, bm25_precision_at_k
from investigator.evaluation.retrieval_eval import (
    expected_random_precision,
    recency_precision_at_k,
    retrieval_precision_at_k,
    same_ticker_forbid,
)

REPO = Path(__file__).resolve().parents[1]

# Mesmo mapa de setores de evaluate_retrieval_fnspid.py. FB = símbolo do Meta no FNSPID.
SECTORS = {
    "AAPL": "tech", "MSFT": "tech", "AMZN": "tech", "GOOGL": "tech",
    "NVDA": "tech", "TSLA": "tech", "META": "tech", "FB": "tech",
    "JPM": "banking", "BAC": "banking",
    "XOM": "energy", "CVX": "energy",
    "JNJ": "health", "PFE": "health",
    "WMT": "consumer", "KO": "consumer",
}


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="BM25 contra SBERT no protocolo da tese")
    ap.add_argument("--kb", default=str(REPO / "data" / "kb_fnspid_sbert.jsonl"))
    ap.add_argument("--queries", type=int, default=500)
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--block", type=int, default=250, help="bloco de consultas (memória)")
    ap.add_argument("--k1", type=float, default=1.5)
    ap.add_argument("--b", type=float, default=0.75)
    args = ap.parse_args()

    print(f"A carregar {args.kb} …")
    dates, tickers, heads, embs = [], [], [], []
    with open(args.kb, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            t = str(r["ticker"]).upper()
            if t not in SECTORS or "embedding" not in r:
                continue
            dates.append(str(r["date"]))
            tickers.append(t)
            heads.append(str(r["headline"]))
            embs.append(r["embedding"])

    emb = np.asarray(embs, dtype="float64")
    emb = emb / np.clip(np.linalg.norm(emb, axis=1, keepdims=True), 1e-12, None)
    tickers = np.asarray(tickers)
    dates = np.asarray(dates)
    sectors = np.asarray([SECTORS[t] for t in tickers])
    n = len(emb)
    print(f"  {n} registos · setores {sorted(set(sectors))}")

    print(f"A construir o índice BM25 (k1={args.k1}, b={args.b}) …")
    index = Bm25Index(heads, k1=args.k1, b=args.b)
    print(f"  vocabulário: {len(index.vocabulary)} termos · avgdl {index.avgdl:.2f}")

    n_q = min(args.queries, n)
    k = args.k
    p_sbert, p_bm25, p_rand, p_rec, z_frac = [], [], [], [], []
    paired = []  # diferença SBERT − BM25 na mesma repetição

    for rep in range(args.repeats):
        rng = np.random.default_rng(args.seed + rep)
        q = rng.choice(n, size=n_q, replace=False)
        forbid = same_ticker_forbid(tickers[q], tickers)
        q_heads = [heads[i] for i in q]

        s = retrieval_precision_at_k(emb[q], emb, sectors[q], sectors, k=k, forbid=forbid)
        b = bm25_precision_at_k(
            index, q_heads, sectors[q], sectors, k=k, forbid=forbid, block=args.block
        )
        p_sbert.append(s)
        p_bm25.append(b)
        paired.append(s - b)
        p_rand.append(expected_random_precision(sectors[q], sectors, forbid))
        p_rec.append(recency_precision_at_k(sectors[q], sectors, dates, k=k, forbid=forbid))
        z_frac.append(
            index.zero_score_fraction(q_heads, k=k, forbid=forbid, block=args.block)
        )
        print(f"  rep {rep}: SBERT {s:.4f} · BM25 {b:.4f} · Δ {s - b:+.4f}")

    def ms(v: list[float]) -> tuple[float, float]:
        a = np.asarray(v, dtype="float64")
        return float(a.mean()), float(a.std())

    sb_m, sb_s = ms(p_sbert)
    bm_m, bm_s = ms(p_bm25)
    rd_m, _ = ms(p_rand)
    rc_m, _ = ms(p_rec)
    d_m, d_s = ms(paired)
    zf_m, _ = ms(z_frac)

    print()
    print(f"  P@{k}: SBERT {sb_m:.4f}±{sb_s:.4f} · BM25 {bm_m:.4f}±{bm_s:.4f}"
          f" · random {rd_m:.4f} · recency {rc_m:.4f}")
    print(f"  diferença emparelhada SBERT − BM25: {d_m:+.4f}±{d_s:.4f}")
    print(f"  margem sobre o acaso: SBERT {sb_m - rd_m:+.4f} · BM25 {bm_m - rd_m:+.4f}")
    print(f"  lugares com pontuação zero no BM25: {zf_m:.2%}")

    out = REPO / "docs" / "evaluation" / "evaluation_retrieval_bm25.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f"""# B1 — BM25 contra SBERT na recuperação de precedentes

Gerado por `scripts/evaluate_retrieval_bm25.py` a {datetime.now(UTC):%Y-%m-%d %H:%M} UTC.

Protocolo idêntico ao de `evaluate_retrieval_fnspid.py`: {args.repeats} repetições de
{n_q} consultas, sementes {args.seed}..{args.seed + args.repeats - 1}, k={k}, recuperação
cross-ticker, relevância = mesmo setor. Corpus: {n} registos.
BM25 com k1={args.k1} e b={args.b}; empates resolvidos por permutação fixa (semente 42).

| Método | Precision@{k} | Margem sobre o acaso |
|---|---|---|
| SBERT (implantado) | {sb_m:.4f} ± {sb_s:.4f} | {sb_m - rd_m:+.4f} |
| **BM25** | **{bm_m:.4f} ± {bm_s:.4f}** | **{bm_m - rd_m:+.4f}** |
| Recência | {rc_m:.4f} | {rc_m - rd_m:+.4f} |
| Acaso (taxa-base) | {rd_m:.4f} | — |

Diferença emparelhada SBERT − BM25, sobre as mesmas consultas: **{d_m:+.4f} ± {d_s:.4f}**.

Lugares preenchidos com pontuação BM25 exatamente zero: **{zf_m:.2%}**. Um valor elevado
significaria que o BM25 não encontrou termos comuns e que a posição foi ocupada pelo
desempate aleatório, e não por correspondência lexical.

Valores por repetição:

| Repetição | SBERT | BM25 | Δ |
|---|---|---|---|
"""
        + "\n".join(
            f"| {i} | {s:.4f} | {b:.4f} | {s - b:+.4f} |"
            for i, (s, b) in enumerate(zip(p_sbert, p_bm25, strict=True))
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nEscrito: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
