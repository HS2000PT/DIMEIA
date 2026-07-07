"""Cura uma KB LEVE multi-ano para o produto (app pública + runner na nuvem).

Problema real: a app pública só tinha a KB-amostra (10 registos). A KB SBERT completa
(~691 MB, 384-d) não é versionável nem corre na stack leve. Solução: uma seleção
ESTRATIFICADA e determinística do FNSPID 2018–2023 (N por ticker×ano, espaçada no tempo,
sem aleatoriedade) — pequena o suficiente para o git.

Modo SEMÂNTICO (o do produto desde 2026-07-07): `--sbert-kb` reutiliza os embeddings
SBERT 384-d JÁ calculados na KB grande (nenhum re-embedding; impactos preservados) e
arredonda-os a 5 casas (erro de cosseno < 1e-4, verificado; reduz o ficheiro para caber
no git). A app/runner consultam-na com o MESMO modelo em ONNX (onnx_embedder.py).
O modo antigo (HashingEmbedder) continua disponível sem a flag.

Não toca em `kb_sample.jsonl` (demo/tese) nem nos números da tese.

Uso:
    python scripts/curate_kb_light.py --sbert-kb data/kb_fnspid_sbert.jsonl   # produto
    python scripts/curate_kb_light.py            # legado: word-overlap 256-d
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from investigator.historical_kb.embedder import HashingEmbedder
from investigator.historical_kb.knowledge_base import HistoricalKB
from investigator.market_data.prices import load_close_series

_REPO = Path(__file__).resolve().parents[1]
_IN = _REPO / "data" / "fnspid_news_subset.csv"
_OUT = _REPO / "data" / "samples" / "kb_fnspid_light.jsonl"


def stratify(news: pd.DataFrame, per_group: int) -> pd.DataFrame:
    """Seleção determinística: até `per_group` manchetes por (ticker, ano), espaçadas no tempo."""
    news = news.sort_values(["ticker", "date"]).reset_index(drop=True)
    grupos = []
    for _, g in news.groupby([news["ticker"], news["date"].dt.year], sort=True):
        if len(g) <= per_group:
            grupos.append(g)
        else:
            passo = len(g) / per_group
            idx = [int(math.floor(i * passo)) for i in range(per_group)]
            grupos.append(g.iloc[idx])
    return pd.concat(grupos).sort_values(["date", "ticker"]).reset_index(drop=True)


def curate_from_sbert_kb(kb_path: Path, per_group: int, out: Path) -> None:
    """Seleciona da KB SBERT completa reutilizando os embeddings 384-d (sem re-embedding)."""
    import json

    from investigator.historical_kb.knowledge_base import HistoricalKB

    rows, records = [], []
    with kb_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    for i, r in enumerate(records):
        rows.append({"idx": i, "ticker": r["ticker"], "date": r["date"],
                     "headline": r["headline"]})
    news = pd.DataFrame(rows)
    news["date"] = pd.to_datetime(news["date"], errors="coerce")
    news = news.dropna(subset=["date"])
    # Produto limpo: só registos com impacto completo (+1/+3/+5d finito) ANTES de estratificar,
    # para que cada grupo (ticker, ano) fique cheio com registos utilizáveis.
    completos = [i for i in news["idx"]
                 if all(pd.notna(records[i]["impacts"].get(h)) for h in ("1", "3", "5"))]
    news = news[news["idx"].isin(set(completos))]
    sel = stratify(news, per_group)
    print(f"KB SBERT: {len(records):,} → curadas {len(sel):,} "
          f"({sel['ticker'].nunique()} tickers, {sel['date'].dt.year.nunique()} anos)")

    kb = HistoricalKB.load(kb_path)  # reutiliza os NewsRecord já construídos
    escolhidos = []
    for i in sel["idx"]:
        rec = kb.records[i]
        rec.embedding = [round(float(x), 5) for x in rec.embedding]  # cabe no git
        escolhidos.append(rec)
    HistoricalKB(escolhidos).save(out)
    tam = out.stat().st_size / 1e6
    print(f"KB leve SEMÂNTICA: {len(escolhidos):,} registos 384-d → {out} "
          f"({tam:.1f} MB, versionável)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="KB leve multi-ano (estratificada; --sbert-kb = modo semântico do produto)")
    parser.add_argument("--sbert-kb", default=None,
                        help="caminho da KB SBERT completa (ex.: data/kb_fnspid_sbert.jsonl); "
                             "reutiliza os embeddings 384-d — é o modo do produto")
    parser.add_argument("--dim", type=int, default=256,
                        help="dimensão do HashingEmbedder no modo legado (sem --sbert-kb)")
    parser.add_argument("--per-group", type=int, default=36,
                        help="manchetes por (ticker, ano); 14 tickers × 6 anos × 36 ≈ 3000")
    parser.add_argument("--out", default=str(_OUT))
    args = parser.parse_args()

    if args.sbert_kb:
        curate_from_sbert_kb(Path(args.sbert_kb), args.per_group, Path(args.out))
        return

    news = pd.read_csv(_IN)
    news["date"] = pd.to_datetime(news["date"], errors="coerce")
    news = news.dropna(subset=["date", "ticker", "headline"])
    sel = stratify(news, args.per_group)
    print(f"Corpus: {len(news):,} → curadas {len(sel):,} "
          f"({sel['ticker'].nunique()} tickers, {sel['date'].dt.year.nunique()} anos)")

    tickers = sorted(sel["ticker"].astype(str).str.upper().unique().tolist())
    start = sel["date"].min().strftime("%Y-%m-%d")
    end = (sel["date"].max() + pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    print("A obter preços (yfinance)…")
    prices = load_close_series(tickers, start, end)

    kb = HistoricalKB.build(sel, prices, HashingEmbedder(dim=args.dim))
    # Produto limpo: só registos com impacto completo (+1/+3/+5d finito) — os ~0,25% do fim
    # da janela (sem +5d observável) ficam de fora; ver docs/evaluation/kb_fnspid_build.md.
    completos = [r for r in kb.records
                 if all(pd.notna(r.impacts.get(h)) for h in ("1", "3", "5"))]
    kb = HistoricalKB(completos)
    out = Path(args.out)
    kb.save(out)
    tam = out.stat().st_size / 1e6
    print(f"KB leve: {len(kb):,} registos → {out} ({tam:.1f} MB, versionável)")


if __name__ == "__main__":
    main()
