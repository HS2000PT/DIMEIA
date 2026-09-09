"""Descarrega e subselecciona o FNSPID (notícias financeiras) por ticker e janela temporal.

Dataset: FNSPID — Financial News and Stock Price Integration Dataset (Dong et al., 2024).
- Hugging Face: Zihan1004/FNSPID
- Licença: CC BY-SA 4.0 — ATRIBUIÇÃO OBRIGATÓRIA no README e na tese.

O ficheiro de notícias do FNSPID é enorme (~23 GB), pelo que NÃO o descarregamos inteiro:
fazemos *stream* por *chunks* (via `requests` — `pd.read_csv(url)` BLOQUEIA neste endpoint do
Hugging Face) e filtramos à medida (apenas os tickers e a janela escolhida), lendo só
3 colunas (`usecols`). Como o ficheiro está ORDENADO por ticker, paramos a varredura assim que
passamos o maior ticker pedido (`early_stop`). Só o subconjunto fica em disco.

NOTA DE VIABILIDADE (verificado, S17): o débito observado é ~1.300 linhas/s; o ficheiro tem
~15M linhas → varrer tudo demora ~3,4 h. Validado que o stream funciona (extraiu 379 notícias da
Agilent 2018-2023 e parou cedo). Para a KB multi-ano completa, correr este script numa máquina/
ligação adequada (ex.: durante a noite) e depois `build_kb.py --sbert`. A avaliação atual usa a KB
real do Finnhub; o FNSPID multi-ano é trabalho futuro reprodutível.

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

# Subconjunto default — tem de coincidir com docs/design/data_card.md.
DEFAULT_TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", "TSLA", "META", "JPM",
    "BAC", "XOM", "CVX", "JNJ", "PFE", "WMT", "KO",
]
DEFAULT_START = "2018-01-01"
DEFAULT_END = "2023-12-31"

# ⚠️ REVISÃO FIXADA. Antes de 2026-09-09 esta constante apontava para `resolve/main`, que é um
# ponteiro MÓVEL: o mesmo comando podia devolver conteúdo diferente em datas diferentes, sem
# aviso e sem deixar rasto. Um corpus assim não é reproduzível ainda que o script o seja.
#
# A revisão abaixo foi lida da API do Hugging Face a 2026-09-09; o dataset não é modificado
# desde 2024-04-09, pelo que fixá-la não perde nada e passa a garantir tudo.
FNSPID_REVISION = "bf9189c41527198897d1af3e17b1a0095279fc45"
FNSPID_REPO = "Zihan1004/FNSPID"

DEFAULT_NEWS_URL = (
    f"https://huggingface.co/datasets/{FNSPID_REPO}/resolve/{FNSPID_REVISION}/"
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
    # AUDITORIA DE ORDENAÇÃO. A paragem antecipada só é correta se o ficheiro estiver mesmo
    # ordenado por ticker; o código anterior assumia-o sem o verificar, e uma exceção à
    # ordenação truncaria o corpus em silêncio. Guarda-se o maior ticker já visto e regista-se
    # qualquer chunk que o contrarie, para que a suposição passe a ser um facto declarado.
    audit = {"chunks": 0, "max_ticker_visto": "", "violacoes_ordenacao": 0, "parou_cedo": False}
    reader = pd.read_csv(resp.raw, chunksize=chunksize, usecols=usecols, low_memory=False)
    for chunk in reader:
        norm = normalize_columns(chunk)
        if not norm["ticker"].empty:
            cmin, cmax = str(norm["ticker"].min()), str(norm["ticker"].max())
            if cmin < audit["max_ticker_visto"]:
                audit["violacoes_ordenacao"] += 1
            audit["max_ticker_visto"] = max(audit["max_ticker_visto"], cmax)
        audit["chunks"] += 1
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
                audit["parou_cedo"] = True
                break
    resp.close()
    audit["linhas_varridas"] = scanned
    result = pd.concat(kept, ignore_index=True) if kept else pd.DataFrame(
        columns=["date", "ticker", "headline"]
    )
    result = result.sort_values(["ticker", "date"]).reset_index(drop=True)
    return result, audit


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
    df, audit = stream_filter(args.news_url, args.tickers, args.start, args.end,
                              chunksize=args.chunksize, limit=args.limit,
                              early_stop=not args.no_early_stop)
    print(f"Total de notícias no subconjunto: {len(df):,}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Subconjunto gravado em {out} (gitignored).")

    # ── MANIFESTO ────────────────────────────────────────────────────────────
    # O corpus não é versionado (tem centenas de MB), pelo que sem isto não há forma de
    # saber, meses depois, QUE corpus produziu um número publicado. O manifesto é pequeno,
    # é versionado, e é o que torna verdadeira a afirmação de reprodutibilidade do Apêndice A.
    import hashlib
    import json
    from datetime import UTC, datetime

    h = hashlib.sha256()
    with open(out, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)

    por_ticker = df.groupby("ticker").size().sort_index().to_dict()
    manifesto = {
        "gerado_em": datetime.now(UTC).isoformat(timespec="seconds"),
        "fonte": {"repo": FNSPID_REPO, "revisao": FNSPID_REVISION, "url": args.news_url},
        "parametros": {
            "tickers": sorted(t.upper() for t in args.tickers),
            "inicio": args.start,
            "fim": args.end,
            "chunksize": args.chunksize,
            "limit": args.limit,
            "early_stop": not args.no_early_stop,
        },
        "resultado": {
            "linhas": int(len(df)),
            "tickers_presentes": sorted(df["ticker"].unique().tolist()),
            "data_min": str(df["date"].min()),
            "data_max": str(df["date"].max()),
            "linhas_por_ticker": {k: int(v) for k, v in por_ticker.items()},
            "sha256": h.hexdigest(),
        },
        "auditoria_varredura": audit,
    }
    man_path = Path("docs/design/fnspid_corpus_manifest.json")
    man_path.parent.mkdir(parents=True, exist_ok=True)
    man_path.write_text(json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifesto gravado em {man_path} (versionado).")
    print(f"  sha256={h.hexdigest()[:16]}… · linhas={len(df):,} · "
          f"tickers={len(manifesto['resultado']['tickers_presentes'])} · "
          f"violações de ordenação={audit['violacoes_ordenacao']} · "
          f"parou cedo={audit['parou_cedo']}")

    sample = df.head(args.sample_size)
    sample_path = Path(args.sample)
    sample_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(sample_path, index=False)
    print(f"Amostra ({len(sample)} linhas) gravada em {sample_path} (versionada).")


if __name__ == "__main__":
    main()
