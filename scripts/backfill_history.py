"""Reconstrói um ano de história correndo o sistema sobre o passado.

**O problema que isto resolve.** O sistema entrou ao vivo a 9 de Julho de 2026, portanto o
registo real tem ~4 semanas. Os gates suprimem nove em cada dez varreduras — por desenho —
e o resultado é um painel onde metade das empresas parece nunca ter tido nada. Não é falso,
é só recente.

**O que isto NÃO é.** Não substitui nem apaga o registo real. Os alertas enviados
(`alerts_history.jsonl`) são a única prova de operação verdadeira que existe, e é neles que
assentam a latência medida e a pós-validação citadas na tese. Este ficheiro é **separado**,
tem um nome diferente, e a interface desenha-o com um marcador diferente. Um alerta
reproduzido não é um alerta enviado, e confundir os dois seria fabricar operação.

**A armadilha, e como é evitada.** Ao reconstruir o passado é trivial deixar entrar
informação do futuro. Duas defesas:

1. **Impactos.** A maturação reutiliza `live_kb.mature_entry`, o MESMO código do caminho de
   produção, que alinha o evento ao primeiro dia de negociação ≥ data da notícia e mede
   +1/+3/+5 dias a partir daí. Não se reescreve a regra para o passado; usa-se a que já
   está testada.
2. **Precedentes.** Quem consumir este ficheiro para reproduzir decisões TEM de filtrar a
   base pelos registos anteriores ao dia que está a explicar. O ficheiro sai ordenado por
   data justamente para tornar esse corte trivial — e o campo `date` é a data da notícia,
   nunca a da maturação.

Correr:  python scripts/backfill_history.py --months 12
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

from investigator.config import FINNHUB_API_KEY
from investigator.live_kb import PendingNews, mature_entry
from investigator.market_data.prices import load_close_series
from investigator.news_fetcher.relevance import is_relevant

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "data" / "samples" / "backfill_kb.jsonl"

# O Finnhub devolve no máximo ~250 itens por pedido, por isso a janela tem de ser estreita:
# uma semana mantém-se folgadamente abaixo do tecto mesmo nos tickers mais ruidosos.
JANELA_DIAS = 7
PAUSA = 1.1  # 60 pedidos/min no plano gratuito


def _watchlist() -> list[str]:
    cfg = yaml.safe_load((RAIZ / "config" / "alerts.yaml").read_text(encoding="utf-8")) or {}
    return list(cfg.get("market", {}).get("tickers") or [])


def buscar_janela(ticker: str, inicio: dt.date, fim: dt.date) -> list[dict]:
    """Notícias de uma janela. Devolve `[]` em falha — uma semana em falta não trava um ano."""
    url = (f"https://finnhub.io/api/v1/company-news?symbol={ticker}"
           f"&from={inicio}&to={fim}&token={FINNHUB_API_KEY}")
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            dados = json.load(resp)
        return dados if isinstance(dados, list) else []
    except (urllib.error.URLError, OSError, ValueError):
        return []


def recolher(ticker: str, meses: int, hoje: dt.date) -> list[tuple[str, str]]:
    """`(data, manchete)` únicos e relevantes, do mais antigo para o mais recente."""
    vistos: set[str] = set()
    saida: list[tuple[str, str]] = []
    inicio = hoje - dt.timedelta(days=30 * meses)
    cursor = inicio
    while cursor < hoje:
        fim = min(cursor + dt.timedelta(days=JANELA_DIAS), hoje)
        for item in buscar_janela(ticker, cursor, fim):
            manchete = (item.get("headline") or "").strip()
            epoch = item.get("datetime")
            if not manchete or not epoch:
                continue
            # O mesmo filtro de relevância da produção. Sem ele entrava o lixo que o
            # Finnhub etiqueta mal (escritórios de advogados, listas de "top movers").
            if not is_relevant(manchete, ticker):
                continue
            chave = manchete.lower()
            if chave in vistos:
                continue
            vistos.add(chave)
            data = dt.datetime.fromtimestamp(epoch, tz=dt.UTC).date().isoformat()
            saida.append((data, manchete))
        cursor = fim
        time.sleep(PAUSA)
    saida.sort()
    return saida


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--months", type=int, default=12)
    ap.add_argument("--tickers", nargs="*")
    ap.add_argument("--out", default=str(DESTINO))
    args = ap.parse_args()

    if not FINNHUB_API_KEY:
        print("[backfill] sem FINNHUB_API_KEY.")
        return 1

    tickers = [t.upper() for t in (args.tickers or _watchlist())]
    hoje = dt.date.today()
    print(f"[backfill] {len(tickers)} tickers x {args.months} meses -> {args.out}")

    # Preços de uma só vez: a maturação precisa de fechos ATÉ depois da última notícia.
    inicio_precos = (hoje - dt.timedelta(days=30 * args.months + 40)).isoformat()
    print("[backfill] a carregar fechos…")
    closes = load_close_series(tickers, inicio_precos, hoje.isoformat())

    total_escritos = 0
    destino = Path(args.out)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8") as fh:
        for i, ticker in enumerate(tickers, 1):
            manchetes = recolher(ticker, args.months, hoje)
            serie = closes.get(ticker)
            if serie is None or serie.empty:
                print(f"[backfill] {ticker:<6} {len(manchetes):5} manchetes · SEM PREÇOS, saltado")
                continue

            escritos = 0
            for data, manchete in manchetes:
                # O embedding é um marcador de posição e NÃO é escrito. O que interessa
                # reutilizar de `mature_entry` é o **alinhamento**: primeiro dia de
                # negociação ≥ data da notícia, +1/+3/+5 dias a partir daí, e `None`
                # quando a barra +5d ainda não existe. Reimplementar essa regra aqui era
                # exactamente como se introduz lookahead sem dar por isso.
                try:
                    entrada = PendingNews(date=data, ticker=ticker, headline=manchete,
                                          key=f"{data}|{ticker}|{manchete}",
                                          embedding=[0.0])
                    registo = mature_entry(entrada, serie)
                except Exception:  # noqa: BLE001
                    registo = None
                if registo is None:
                    continue  # ainda não maturou (fim da janela) — correcto, não se inventa
                fh.write(json.dumps({
                    "date": registo.date, "ticker": registo.ticker,
                    "headline": registo.headline, "impacts": registo.impacts,
                }, ensure_ascii=False) + "\n")
                escritos += 1

            total_escritos += escritos
            print(f"[backfill] {ticker:<6} {len(manchetes):5} relevantes -> "
                  f"{escritos:5} maturadas   ({i}/{len(tickers)})")

    print(f"\n[backfill] {total_escritos} registos em {destino}")
    print("[backfill] NOTA: isto e um REPLAY. Nao substitui alerts_history.jsonl,")
    print("[backfill] que continua a ser o unico registo de operacao real.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
