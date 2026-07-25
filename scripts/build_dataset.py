"""Constrói o dataset de treino da triagem de materialidade (M1 do ML_PLAN).

Entrada:  CSV de notícias (date,ticker,headline) — ex.: data/finnhub_news.csv (ou o FNSPID em M6).
Saída:    data/triage_dataset.csv (gitignored) + amostra pequena em data/samples/triage_sample.csv.

Para cada notícia: alinha ao 1.º dia de negociação ≥ data (regra da KB), calcula as features de
contexto (vol20/mom5/ret_event — convenção anti-lookahead em investigator/triage/dataset.py) e o
rótulo de materialidade |retorno anormal vs SPY em (d,d+h]| ≥ τ para a grelha τ×h. Divisão
temporal por dias únicos com embargo. Preços via yfinance com cache em data/prices/ (apagar
para refrescar).

Uso:
    python scripts/build_dataset.py                       # defaults (corpus Finnhub; embargo 5)
    python scripts/build_dataset.py --embargo 1           # corpus-fumo de 4 semanas (ML_PLAN §4)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from investigator.console import force_utf8_stdout
from investigator.triage.dataset import (
    MIN_HISTORY,
    SECTORS,
    abnormal_label,
    assign_splits,
    event_features,
    event_features_ext,
)

REPO = Path(__file__).resolve().parents[1]
PRICES_DIR = REPO / "data" / "prices"
MARKET = "SPY"  # proxy de mercado para o retorno anormal


def fetch_closes(ticker: str, start: str, end: str) -> pd.Series:
    """Fechos diários [start, end], com cache CSV em data/prices/ (apagar o ficheiro refresca).

    A cache é indexada por (ticker, start, end): re-correr sobre uma janela DIFERENTE não
    reutiliza em silêncio uma série mais estreita — o que faria cair eventos fora do intervalo
    antes cacheado. Cada janela tem o seu ficheiro.
    """
    PRICES_DIR.mkdir(parents=True, exist_ok=True)
    cache = PRICES_DIR / f"{ticker}_{start}_{end}.csv"
    if cache.exists():
        s = pd.read_csv(cache, index_col=0, parse_dates=True)["Close"]
        return s
    import yfinance as yf

    hist = yf.Ticker(ticker).history(start=start, end=end, interval="1d")
    if hist is None or hist.empty:
        raise RuntimeError(f"Sem preços para {ticker}.")
    s = hist["Close"]
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    s.to_csv(cache)
    return s


def build(news: pd.DataFrame, taus: list[float], horizons: list[int],
          primary_tau: float, primary_h: int, embargo: int,
          ext: bool = False) -> tuple[pd.DataFrame, dict]:
    """Constrói o dataset; devolve (df, contadores de descartes).

    `ext=True` (RQ4-ext) inclui as features estendidas (`event_features_ext`); default False
    reproduz o dataset congelado da tese byte-a-byte (as colunas novas nem aparecem).
    """
    news = news[news["ticker"].isin(SECTORS)].copy()
    news["date"] = pd.to_datetime(news["date"])
    start = (news["date"].min() - pd.DateOffset(days=60)).strftime("%Y-%m-%d")
    end = (news["date"].max() + pd.DateOffset(days=30)).strftime("%Y-%m-%d")

    spy = fetch_closes(MARKET, start, end)
    drops = {"sem_precos": 0, "sem_historico": 0, "sem_futuro": 0, "fora_da_serie": 0}
    rows: list[dict] = []
    for ticker, group in news.groupby("ticker"):
        try:
            closes = fetch_closes(ticker, start, end)
        except Exception as exc:  # noqa: BLE001  (um ticker sem preços não pára o build)
            print(f"[saltar {ticker}] {type(exc).__name__}: {exc}")
            drops["sem_precos"] += len(group)
            continue
        # Alinhar ticker e SPY pelas datas comuns (retorno anormal exige séries alinhadas).
        aligned = pd.DataFrame({"t": closes, "m": spy}).dropna()
        dates = aligned.index
        for _, r in group.iterrows():
            idx = int(dates.searchsorted(r["date"]))
            if idx >= len(dates):
                drops["fora_da_serie"] += 1
                continue
            feats = (event_features_ext(aligned["t"], aligned["m"], idx) if ext
                     else event_features(aligned["t"], idx))
            if feats is None:
                drops["sem_historico"] += 1
                continue
            primary = abnormal_label(aligned["t"], aligned["m"], idx, primary_tau, primary_h)
            if primary is None:
                drops["sem_futuro"] += 1
                continue
            row = {
                "date": dates[idx].strftime("%Y-%m-%d"),   # dia do EVENTO (negociação)
                "news_date": r["date"].strftime("%Y-%m-%d"),
                "ticker": ticker,
                "sector": SECTORS[ticker],
                "headline": str(r["headline"]),
                "headline_len": len(str(r["headline"])),
                **feats,
                "label": primary,
            }
            for tau in taus:
                for h in horizons:
                    lab = abnormal_label(aligned["t"], aligned["m"], idx, tau, h)
                    row[f"label_t{tau:g}_h{h}"] = lab if lab is not None else ""
            rows.append(row)

    df = pd.DataFrame(rows).sort_values(["date", "ticker"]).reset_index(drop=True)
    df["split"] = assign_splits(df["date"], embargo_days=embargo).to_numpy()
    return df, drops


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Dataset de triagem de materialidade (M1)")
    ap.add_argument("--news", default=str(REPO / "data" / "finnhub_news.csv"))
    ap.add_argument("--out", default=str(REPO / "data" / "triage_dataset.csv"))
    ap.add_argument("--taus", nargs="+", type=float, default=[0.015, 0.02, 0.03])
    ap.add_argument("--horizons", nargs="+", type=int, default=[1, 3, 5])
    ap.add_argument("--primary-tau", type=float, default=0.02)
    ap.add_argument("--primary-horizon", type=int, default=3)
    ap.add_argument("--embargo", type=int, default=5,
                    help="dias únicos de embargo entre blocos (corpus-fumo de 4 semanas: usar 1)")
    ap.add_argument("--ext", action="store_true",
                    help="inclui features estendidas (RQ4-ext; ver docs/evaluation/roadmap_rq4.md)")
    args = ap.parse_args()

    news = pd.read_csv(args.news)
    print(f"Notícias lidas: {len(news)}  (tickers no mapa de setores: {len(SECTORS)})")
    df, drops = build(news, args.taus, args.horizons, args.primary_tau,
                      args.primary_horizon, args.embargo, ext=args.ext)

    # Com --ext, escrever num ficheiro SEPARADO por defeito (nunca esmagar o dataset congelado).
    if args.ext and args.out == str(REPO / "data" / "triage_dataset.csv"):
        args.out = str(REPO / "data" / "triage_dataset_ext.csv")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    sample = df.head(25)
    sample.to_csv(REPO / "data" / "samples" / "triage_sample.csv", index=False, encoding="utf-8")

    print(f"Dataset: {len(df)} linhas -> {out}")
    print(f"Descartes: {drops}")
    print(f"Histórico mínimo exigido: {MIN_HISTORY} fechos antes do evento")
    print("\nBalanço de classes (rótulo primário "
          f"τ={args.primary_tau:g}, h={args.primary_horizon}):")
    print(df.groupby("split")["label"].agg(["count", "mean"]).rename(columns={"mean": "positivos"}))
    print("\nBalanço por τ×h (fração positiva, todas as linhas):")
    for tau in args.taus:
        for h in args.horizons:
            col = f"label_t{tau:g}_h{h}"
            vals = pd.to_numeric(df[col], errors="coerce").dropna()
            print(f"  τ={tau:g} h={h}: {vals.mean():.3f}  (n={len(vals)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
