"""Constrói a base de conhecimento histórica (KB) a partir de notícias + preços.

Junta o subconjunto de notícias do FNSPID (CSV: date, ticker, headline) aos preços de fecho
históricos (yfinance) e produz a KB (JSONL) com impacto pós-evento e embeddings — ver
investigator/historical_kb/knowledge_base.py.

Embedder: por defeito o `HashingEmbedder` (sem dependências; baseline e reprodutível). Com
`--sbert` usa o `SbertEmbedder` (SBERT real; requer sentence-transformers/torch instalados).

Uso:
    python scripts/build_kb.py --news data/fnspid_news_subset.csv          # KB completa
    python scripts/build_kb.py --news data/samples/fnspid_news_sample.csv  # demo (amostra)
    python scripts/build_kb.py --news <csv> --sbert                        # com SBERT real
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):  # consola Windows (cp1252) → UTF-8 para acentos/glifos
    sys.stdout.reconfigure(encoding="utf-8")

from investigator.historical_kb.embedder import HashingEmbedder
from investigator.historical_kb.knowledge_base import HistoricalKB


def load_prices(tickers: list[str], start: str, end: str, *,
                cache_dir=None, refrescar: bool = False) -> dict[str, pd.Series]:
    """Preços de fecho diários por ticker — delega na camada de mercado do pacote.

    Com `cache_dir`, as séries ficam fixadas em disco e a reconstrução deixa de depender da
    rede. Isto importa aqui e não na camada viva: a KB histórica é um artefacto citado pela
    tese, e um artefacto citado não pode mudar porque um dividendo reajustou o histórico.
    """
    from investigator.market_data.prices import load_close_series

    return load_close_series(tickers, start, end, cache_dir=cache_dir, refrescar=refrescar)


def main() -> None:
    parser = argparse.ArgumentParser(description="Construção da KB histórica (notícias+preços).")
    parser.add_argument("--news", required=True, help="CSV com colunas date, ticker, headline")
    parser.add_argument("--out", default="data/kb.jsonl")
    parser.add_argument("--sample", default="data/samples/kb_sample.jsonl")
    parser.add_argument("--sample-size", type=int, default=50)
    parser.add_argument("--sbert", action="store_true",
                        help="usa SBERT real (senão HashingEmbedder)")
    parser.add_argument("--dim", type=int, default=64, help="dimensão do HashingEmbedder")
    parser.add_argument("--precos-cache", default="data/prices",
                        help="pasta onde as séries de preços ficam fixadas (vazio desliga)")
    parser.add_argument("--refrescar-precos", action="store_true",
                        help="ignora a cache de preços e vai à rede outra vez")
    parser.add_argument("--precos-manifesto", default="docs/design/precos_manifest.json",
                        help="cópia versionada do manifesto da cache de preços")
    args = parser.parse_args()

    news = pd.read_csv(args.news)
    news["date"] = pd.to_datetime(news["date"], errors="coerce")
    news = news.dropna(subset=["date", "ticker", "headline"])
    tickers = sorted(news["ticker"].astype(str).str.upper().unique().tolist())
    start = news["date"].min().strftime("%Y-%m-%d")
    end = (news["date"].max() + pd.Timedelta(days=10)).strftime("%Y-%m-%d")  # margem p/ +5d
    print(f"Notícias: {len(news):,} | tickers: {tickers} | {start}…{end}")

    cache = Path(args.precos_cache) if args.precos_cache else None
    if cache is None:
        print("A obter preços (yfinance, SEM cache — a reconstrução não será determinística)…")
    else:
        print(f"A obter preços (cache em {cache})…")
    prices = load_prices(tickers, start, end, cache_dir=cache,
                         refrescar=args.refrescar_precos)

    if cache is not None and args.precos_manifesto:
        import json

        from investigator.market_data import price_cache as _pc

        man = _pc.manifesto(cache)
        man["janela"] = {"inicio": start, "fim": end}
        destino = Path(args.precos_manifesto)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8")
        fontes = sorted({r["fonte"] for r in man["series"].values()})
        print(f"Manifesto dos preços em {destino} "
              f"({len(man['series'])} séries, fontes: {', '.join(fontes) or 'nenhuma'}).")

    if args.sbert:
        from investigator.historical_kb.embedder import SbertEmbedder

        embedder = SbertEmbedder()
        print(f"Embedder: SBERT ({embedder.model_name}, dim={embedder.dim})")
    else:
        embedder = HashingEmbedder(dim=args.dim)
        print(f"Embedder: HashingEmbedder (baseline, dim={embedder.dim})")

    print("A construir a KB…")
    kb = HistoricalKB.build(news, prices, embedder)
    print(f"KB construída: {len(kb)} registos")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    kb.save(out)
    print(f"KB gravada em {out} (gitignored).")

    HistoricalKB(kb.records[: args.sample_size]).save(args.sample)
    n_sample = min(args.sample_size, len(kb))
    print(f"Amostra da KB ({n_sample} registos) em {args.sample} (versionada).")


if __name__ == "__main__":
    main()
