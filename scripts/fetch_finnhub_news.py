"""Recolhe notícias reais (Finnhub /company-news) para os tickers do data_card → CSV.

Fonte de notícias REAL e gratuita para uma primeira avaliação, sem o download de ~23 GB do
FNSPID. O FNSPID continua a ser a fonte histórica mais rica (multi-ano)
— ver docs/design/data_card.md.

Saída: CSV com colunas `date, ticker, headline` (compatível com `build_kb.py` e `evaluate.py`).
Dados grandes ficam gitignored; só uma amostra pequena vai para data/samples/.

Uso:
    python scripts/fetch_finnhub_news.py                      # 15 tickers, últimos 180 dias
    python scripts/fetch_finnhub_news.py --days 90 --max-per-ticker 500
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from investigator.news_fetcher.fetcher import fetch_finnhub_company_news

DEFAULT_TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", "TSLA", "META", "JPM",
    "BAC", "XOM", "CVX", "JNJ", "PFE", "WMT", "KO",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Notícias reais via Finnhub → CSV.")
    parser.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    parser.add_argument("--days", type=int, default=180, help="janela para trás, em dias")
    parser.add_argument("--fim", default=None,
                        help="último dia da janela, YYYY-MM-DD. Por omissão, hoje. Existe para "
                             "poder voltar a recolher uma janela passada — o plano gratuito do "
                             "Finnhub serve cerca de um ano de company-news, e sem isto uma "
                             "janela antiga é irrecuperável mesmo estando ao alcance da API.")
    parser.add_argument("--max-per-ticker", type=int, default=1000)
    parser.add_argument("--pausa", type=float, default=1.1,
                        help="segundos entre pedidos quando se fatia (limite gratuito: "
                             "60/min, logo 1,1 s deixa margem)")
    parser.add_argument("--fatiar", type=int, default=None,
                        help="parte a janela em fatias de N dias, uma chamada por fatia. "
                             "Sem isto, um pedido que bata no tecto da API (~250 itens) "
                             "devolve só os dias mais recentes e ignora o `from` em silêncio.")
    parser.add_argument("--out", default="data/finnhub_news.csv")
    parser.add_argument("--sample", default="data/samples/finnhub_news_sample.csv")
    parser.add_argument("--sample-size", type=int, default=30)
    args = parser.parse_args()

    end = date.fromisoformat(args.fim) if args.fim else date.today()
    start = end - timedelta(days=args.days)
    print(f"Finnhub /company-news: {len(args.tickers)} tickers, {start}…{end}")

    # ⚠️ O TECTO DA API, medido a 2026-09-10 e não suposto. O `/company-news` devolve no máximo
    # ~250 itens por pedido e, ao atingir esse tecto, **ignora o `from`**: pedir 5, 13 ou 27 dias
    # de AAPL devolve exactamente as mesmas 248 manchetes, todas dos 5 dias anteriores ao `to`.
    # A janela pedida deixa de ser a janela obtida, e o pior é que isso não aparece em erro
    # nenhum — o corpus vem com a forma certa e o período errado. Para empresas de muito volume
    # (NVDA, MSFT, GOOGL) a cobertura real cai a 3-4 dias; para as de pouco (KO, PFE) vem a
    # janela inteira. É viés estrutural, porque entrelaça a cobertura temporal com o volume de
    # notícias da empresa — e a §5.3 mede recuperação POR SETOR.
    #
    # Duas defesas: `--fatiar`, que parte a janela em pedaços pequenos o bastante para nenhum
    # pedido bater no tecto, e a deteção abaixo, que grita quando um pedido vem ao tecto.
    TECTO_API = 240  # abaixo dos ~250 observados, para apanhar o tecto antes de ele apertar

    def janelas() -> list[tuple[date, date]]:
        if not args.fatiar:
            return [(start, end)]
        fatias, a = [], start
        while a <= end:
            b = min(a + timedelta(days=args.fatiar - 1), end)
            fatias.append((a, b))
            a = b + timedelta(days=1)
        return fatias

    fatias = janelas()
    if args.fatiar:
        print(f"  (janela partida em {len(fatias)} fatias de {args.fatiar} dia(s) — "
              "para nenhum pedido bater no tecto da API)")

    rows: list[dict] = []
    truncados: list[str] = []
    for ticker in args.tickers:
        items = []
        no_tecto = False
        for a, b in fatias:
            lote = fetch_finnhub_company_news(ticker, a.isoformat(), b.isoformat())
            if len(lote) >= TECTO_API:
                no_tecto = True
            items.extend(lote)
            # O plano gratuito serve 60 pedidos por minuto. Fatiar multiplica os pedidos por
            # ticker, logo sem pausa uma recolha fatiada bate em 429 a meio e devolve um corpus
            # incompleto -- que e o defeito que este script existe para nao ter.
            if len(fatias) > 1:
                time.sleep(args.pausa)
        bruto = len(items)  # antes do teto — para tornar a truncagem visível no log
        if args.max_per_ticker:
            items = items[: args.max_per_ticker]
        datas = sorted(it.date for it in items if it.date)
        for it in items:
            if it.date:  # precisa de data para o event study
                rows.append({"date": it.date, "ticker": it.ticker, "headline": it.headline})
        descartadas = bruto - len(items)
        aviso = f"  ⚠ teto: {descartadas} manchetes mais antigas descartadas" if descartadas else ""
        cobertura = f" [{datas[0]}…{datas[-1]}]" if datas else " [sem datas]"
        if no_tecto:
            truncados.append(ticker)
            aviso += "  ⚠ PEDIDO NO TECTO DA API: a janela pedida NÃO foi coberta"
        print(f"  {ticker}: {len(items)}/{bruto} notícias{cobertura}{aviso}")

    if truncados:
        print()
        print(f"⚠ AVISO: {len(truncados)} de {len(args.tickers)} tickers bateram no tecto "
              f"da API ({', '.join(truncados)}).")
        print("  A janela declarada NÃO é a janela recolhida para esses tickers. Voltar a "
              f"correr com `--fatiar N` menor (agora: {args.fatiar or 'sem fatiar'}) antes de "
              "usar este corpus para qualquer afirmação sobre um período.")

    df = pd.DataFrame(rows).drop_duplicates(subset=["ticker", "headline"]).reset_index(drop=True)
    print(f"Total (após dedupe): {len(df):,} notícias")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Gravado em {out} (gitignored).")

    sample = df.head(args.sample_size)
    Path(args.sample).parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(args.sample, index=False)
    print(f"Amostra ({len(sample)}) em {args.sample} (versionada).")


if __name__ == "__main__":
    main()
