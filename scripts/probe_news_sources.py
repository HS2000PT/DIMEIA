"""Sonda as fontes de notícias candidatas com as chaves REAIS, antes de depender delas.

**Porquê sondar em vez de ler a documentação.** Este projecto já pagou uma vez por confiar no
que estava escrito: os fornecedores de modelos de linguagem foram escolhidos por documentação e
a sondagem mostrou que o principal devolvia 404 a contas novas e o segundo 429 à primeira
chamada. A ordem acabou invertida **por medição**. O mesmo se aplica aqui.

**O que se mede, e é o que decide:**

- a fonte responde com a chave que existe?
- devolve notícias **por empresa**, ou só um fluxo geral? (o sistema precisa por empresa; sem
  isso teria de adivinhar a empresa a partir do texto, e isso acrescenta um erro que não é
  preciso ter)
- traz **URL** e **fonte**? (sem eles o alerta não pode ligar à notícia)
- traz **hora de publicação** e não só o dia? (é o que permite medir latência)
- quantas devolve, e quão recentes são as mais recentes?

USO:  python scripts/probe_news_sources.py [--ticker NVDA]
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta

TIMEOUT = 25


def _get(url: str) -> tuple[int, dict | list | None, float]:
    t0 = time.monotonic()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "investigator-probe/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace")), time.monotonic() - t0
    except urllib.error.HTTPError as e:
        return e.code, None, time.monotonic() - t0
    except Exception:  # noqa: BLE001
        return 0, None, time.monotonic() - t0


def _idade(iso: str) -> str:
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        h = (datetime.now(UTC) - d).total_seconds() / 3600
        return f"{h:.1f}h"
    except Exception:  # noqa: BLE001
        return "?"


def relatar(nome: str, estado: int, n: int, dt: float, *, por_empresa: bool,
            url: bool, fonte: bool, hora: str | None, exemplo: str = "") -> None:
    ok = "ok " if estado == 200 and n else "!! "
    print(f"{ok}{nome:16s} HTTP {estado:3d} · {n:4d} notícias · {dt:.2f}s")
    if estado == 200 and n:
        print(f"     por empresa: {'sim' if por_empresa else 'NÃO'} · "
              f"url: {'sim' if url else 'NÃO'} · fonte: {'sim' if fonte else 'NÃO'} · "
              f"mais recente: {hora or '?'}")
        if exemplo:
            print(f"     ex.: {exemplo[:92]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", default="NVDA")
    args = ap.parse_args()
    t = args.ticker.upper()
    hoje = datetime.now(UTC).date()
    desde = (hoje - timedelta(days=3)).isoformat()

    try:
        from investigator.config import load_env
        load_env()
    except Exception:  # noqa: BLE001
        pass

    print(f"=== sondagem de fontes de notícias · ticker {t} · {hoje} ===\n")

    # ── Finnhub (a que já está em uso) ────────────────────────────────────────
    k = os.environ.get("FINNHUB_API_KEY", "")
    if k:
        st, d, dt = _get(f"https://finnhub.io/api/v1/company-news?symbol={t}"
                         f"&from={desde}&to={hoje}&token={k}")
        arts = d if isinstance(d, list) else []
        a0 = arts[0] if arts else {}
        quando = (datetime.fromtimestamp(a0["datetime"], tz=UTC).isoformat()
                  if a0.get("datetime") else "")
        relatar("Finnhub", st, len(arts), dt, por_empresa=True,
                url=bool(a0.get("url")), fonte=bool(a0.get("source")),
                hora=_idade(quando) if quando else None,
                exemplo=str(a0.get("headline", "")))
    else:
        print("!! Finnhub          sem chave")

    # ── Alpha Vantage NEWS_SENTIMENT ─────────────────────────────────────────
    k = os.environ.get("ALPHAVANTAGE_API_KEY", "")
    if k:
        st, d, dt = _get("https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
                         f"&tickers={t}&limit=50&apikey={k}")
        feed = (d or {}).get("feed", []) if isinstance(d, dict) else []
        a0 = feed[0] if feed else {}
        quando = a0.get("time_published", "")
        if len(quando) == 15:  # 20260815T203300
            quando = f"{quando[:4]}-{quando[4:6]}-{quando[6:8]}T{quando[9:11]}:{quando[11:13]}:00Z"
        dd = d if isinstance(d, dict) else {}
        nota = dd.get("Information") or dd.get("Note")
        if nota:
            print(f"!! Alpha Vantage    HTTP {st} · limite: {str(nota)[:78]}")
        else:
            relatar("Alpha Vantage", st, len(feed), dt, por_empresa=True,
                    url=bool(a0.get("url")), fonte=bool(a0.get("source")),
                    hora=_idade(quando) if quando else None,
                    exemplo=str(a0.get("title", "")))
    else:
        print("!! Alpha Vantage    sem chave")

    # ── Polygon ──────────────────────────────────────────────────────────────
    k = os.environ.get("POLYGON_API_KEY", "")
    if k:
        st, d, dt = _get(f"https://api.polygon.io/v2/reference/news?ticker={t}"
                         f"&limit=50&apiKey={k}")
        res = (d or {}).get("results", []) if isinstance(d, dict) else []
        a0 = res[0] if res else {}
        relatar("Polygon", st, len(res), dt, por_empresa=True,
                url=bool(a0.get("article_url")),
                fonte=bool((a0.get("publisher") or {}).get("name")),
                hora=_idade(a0.get("published_utc", "")) if a0.get("published_utc") else None,
                exemplo=str(a0.get("title", "")))
    else:
        print("!! Polygon          sem chave")

    # ── GNews ────────────────────────────────────────────────────────────────
    k = os.environ.get("GNEWS_API_KEY", "")
    if k:
        from investigator.news_fetcher.relevance import COMPANY_DISPLAY
        nome = COMPANY_DISPLAY.get(t, t)
        q = urllib.parse.quote(f'"{nome}" OR "{t}"')
        st, d, dt = _get(f"https://gnews.io/api/v4/search?q={q}&lang=en&max=25&apikey={k}")
        arts = (d or {}).get("articles", []) if isinstance(d, dict) else []
        a0 = arts[0] if arts else {}
        relatar("GNews", st, len(arts), dt, por_empresa=False,
                url=bool(a0.get("url")),
                fonte=bool((a0.get("source") or {}).get("name")),
                hora=_idade(a0.get("publishedAt", "")) if a0.get("publishedAt") else None,
                exemplo=str(a0.get("title", "")))
    else:
        print("!! GNews            sem chave")

    # ── Tiingo ───────────────────────────────────────────────────────────────
    k = os.environ.get("TIINGO_API_KEY", "")
    if k:
        st, d, dt = _get(f"https://api.tiingo.com/tiingo/news?tickers={t.lower()}"
                         f"&limit=50&token={k}")
        arts = d if isinstance(d, list) else []
        a0 = arts[0] if arts else {}
        if st == 403:
            print("!! Tiingo           HTTP 403 · o endpoint de notícias exige plano pago")
        else:
            relatar("Tiingo", st, len(arts), dt, por_empresa=True,
                    url=bool(a0.get("url")), fonte=bool(a0.get("source")),
                    hora=_idade(a0.get("publishedDate", "")) if a0.get("publishedDate") else None,
                    exemplo=str(a0.get("title", "")))
    else:
        print("!! Tiingo           sem chave")

    print("\nO que decide a adopção: por empresa + url + hora de publicação. Sem os três, a fonte "
          "não serve\npara este sistema, por muito generoso que seja o limite.")


if __name__ == "__main__":
    main()
