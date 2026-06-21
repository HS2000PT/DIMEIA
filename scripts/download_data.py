"""Descarrega e subselecciona o FNSPID (notícias financeiras) por ticker e janela temporal.

Dataset: FNSPID — Financial News and Stock Price Integration Dataset (Dong et al., 2024).
- Hugging Face: Zihan1004/FNSPID
- Licença: CC BY-SA 4.0 — ATRIBUIÇÃO OBRIGATÓRIA no README e na tese.

O ficheiro de notícias do FNSPID é enorme (~23 GB), pelo que NÃO o descarregamos inteiro:
fazemos *stream* por *chunks* (via `requests` — `pd.read_csv(url)` BLOQUEIA neste endpoint do
Hugging Face) e filtramos à medida (apenas os tickers e a janela de docs/data_card.md), lendo só
3 colunas (`usecols`). Como o ficheiro está ORDENADO por ticker, paramos a varredura assim que
passamos o maior ticker pedido (`early_stop`). Só o subconjunto fica em disco.

NOTA DE VIABILIDADE (verificado, S17): o débito observado é ~1.300 linhas/s; o ficheiro tem
~15M linhas → varrer tudo demora ~3,4 h. Validado que o stream funciona (extraiu 379 notícias da
Agilent 2018-2023 e parou cedo). Para a KB multi-ano completa, correr este script numa máquina/
ligação adequada (ex.: durante a noite) e depois `build_kb.py --sbert`. A avaliação atual usa a KB
real do Finnhub (ver docs/evaluation_results.md); o FNSPID multi-ano é trabalho futuro reprodutível.

Governança (§5.4): o subconjunto vai para `data/` (gitignored) e uma AMOSTRA pequena para
`data/samples/` (versionada, só títulos — não republicar o texto integral de terceiros).

Uso:
    python scripts/download_data.py                 # subconjunto default (data_card.md)
    python scripts/download_data.py --limit 200000  # varre só as primeiras N linhas (probe)
    python scripts/download_data.py --tickers AAPL MSFT --start 2020-01-01 --end 2021-01-01
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

# Subconjunto default — tem de coincidir com docs/data_card.md.
DEFAULT_TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", "TSLA", "META", "JPM",
    "BAC", "XOM", "CVX", "JNJ", "PFE", "WMT", "KO",
]
DEFAULT_START = "2018-01-01"
DEFAULT_END = "2023-12-31"

# URL de resolução do ficheiro de notícias no Hugging Face (público; CC BY-SA 4.0).
# Configurável por --news-url caso o caminho do dataset mude.
DEFAULT_NEWS_URL = (
    "https://huggingface.co/datasets/Zihan1004/FNSPID/resolve/main/"
    "Stock_news/nasdaq_exteral_data.csv"
)

# Candidatos a nomes de coluna (o FNSPID usa estes; normalizamos para date/ticker/headline).
_DATE_COLS = ("Date", "date", "datetime", "Datetime")
_TICKER_COLS = ("Stock_symbol", "stock_symbol", "Symbol", "symbol", "Ticker", "ticker")
_TITLE_COLS = ("Article_title", "article_title", "Title", "title", "headline", "Headline")


def _pick(colnames, candidates) -> str | None:
    lower = {c.lower(): c for c in colnames}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renomeia as colunas do FNSPID para o esquema interno: date, ticker, headline."""
    date_c = _pick(df.columns, _DATE_COLS)
    ticker_c = _pick(df.columns, _TICKER_COLS)
    title_c = _pick(df.columns, _TITLE_COLS)
    found = (("date", date_c), ("ticker", ticker_c), ("headline", title_c))
    missing = [name for name, col in found if col is None]
    if missing:
        raise ValueError(
            f"Colunas em falta {missing}; colunas disponíveis: {list(df.columns)}"
        )
    out = df[[date_c, ticker_c, title_c]].rename(
        columns={date_c: "date", ticker_c: "ticker", title_c: "headline"}
    )
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.date
    out["ticker"] = out["ticker"].astype("string").str.upper().str.strip()
    out["headline"] = out["headline"].astype("string").str.strip()
    return out.dropna(subset=["date", "ticker", "headline"])


def stream_filter(
    url: str, tickers: list[str], start: str, end: str,
    chunksize: int = 200_000, limit: int | None = None, early_stop: bool = True,
) -> pd.DataFrame:
    """Faz stream do CSV remoto em chunks (via requests) e filtra por ticker e janela [start, end].

    - Usa `requests` (stream=True) em vez de `pd.read_csv(url)`, que NÃO faz stream deste endpoint
      do Hugging Face (bloqueia). Lê apenas as 3 colunas necessárias (`usecols`), ignorando o corpo
      do artigo.
    - `early_stop`: como o ficheiro está ORDENADO por ticker ascendente, paramos a varredura assim
      que ultrapassamos (alfabeticamente) o maior ticker pedido — evita ler o ficheiro todo.
    """
    import requests

    wanted = {t.upper() for t in tickers}
    max_wanted = max(wanted)
    start_d = pd.Timestamp(start).date()
    end_d = pd.Timestamp(end).date()
    usecols = [_DATE_COLS[0], _TITLE_COLS[0], _TICKER_COLS[0]]  # Date, Article_title, Stock_symbol

    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    resp.raw.decode_content = True
    kept: list[pd.DataFrame] = []
    scanned = 0
    seen_any = False
    reader = pd.read_csv(resp.raw, chunksize=chunksize, usecols=usecols, low_memory=False)
    for chunk in reader:
        norm = normalize_columns(chunk)
        mask = norm["ticker"].isin(wanted) & (norm["date"] >= start_d) & (norm["date"] <= end_d)
        matched = norm[mask]
        kept.append(matched)
        seen_any = seen_any or len(matched) > 0
        scanned += len(chunk)
        total_kept = sum(len(k) for k in kept)
        print(f"  …varridas {scanned:,} linhas | guardadas {total_kept:,}", flush=True)
        if limit is not None and scanned >= limit:
            print(f"  (limite de {limit:,} linhas atingido — paragem antecipada)")
            break
        # Paragem antecipada: já passámos (alfabeticamente) todos os tickers pedidos.
        if early_stop and seen_any and not norm["ticker"].empty:
            if str(norm["ticker"].min()) > max_wanted:
                print(f"  (passámos '{max_wanted}' — paragem antecipada por ordenação)")
                break
    resp.close()
    result = pd.concat(kept, ignore_index=True) if kept else pd.DataFrame(
        columns=["date", "ticker", "headline"]
    )
    return result.sort_values(["ticker", "date"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Subconjunto do FNSPID (notícias).")
    parser.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument("--news-url", default=DEFAULT_NEWS_URL)
    parser.add_argument("--chunksize", type=int, default=200_000)
    parser.add_argument("--limit", type=int, default=None,
                        help="máximo de linhas a varrer (para um probe rápido)")
    parser.add_argument("--no-early-stop", action="store_true",
                        help="varre o ficheiro todo (sem parar ao passar o maior ticker)")
    parser.add_argument("--out", default="data/fnspid_news_subset.csv")
    parser.add_argument("--sample", default="data/samples/fnspid_news_sample.csv")
    parser.add_argument("--sample-size", type=int, default=50)
    args = parser.parse_args()

    print(f"A descarregar/filtrar FNSPID: {len(args.tickers)} tickers, {args.start}…{args.end}")
    print("Fonte: Zihan1004/FNSPID (CC BY-SA 4.0). Atribuição obrigatória.")
    df = stream_filter(args.news_url, args.tickers, args.start, args.end,
                       chunksize=args.chunksize, limit=args.limit,
                       early_stop=not args.no_early_stop)
    print(f"Total de notícias no subconjunto: {len(df):,}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Subconjunto gravado em {out} (gitignored).")

    sample = df.head(args.sample_size)
    sample_path = Path(args.sample)
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(sample_path, index=False)
    print(f"Amostra ({len(sample)} linhas) gravada em {sample_path} (versionada).")


if __name__ == "__main__":
    main()
