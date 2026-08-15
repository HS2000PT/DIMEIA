"""Qual das fontes gratuitas entrega notícias que servem, e em que se completam?

**A pergunta não é qual devolve mais.** É qual devolve mais que **sobreviva ao filtro de
relevância** do sistema, porque tudo o que é rejeitado à entrada não vale nada — e a sondagem
mostrou que a manchete mais recente que uma fonte devolveu para a NVDA era sobre a Eli Lilly.

Mede-se, para cada fonte e sobre a watchlist inteira:

1. **volume** — quantas devolve;
2. **precisão de etiquetagem** — que fracção passa `is_relevant`, o filtro que já está em
   produção. É o único critério de qualidade que não depende de opinião;
3. **frescura** — quão recente é a mais recente que serve;
4. **complemento** — quantas manchetes cada fonte traz que as outras **não** trazem. É isto que
   decide se vale a pena somar fontes ou se é redundância paga com pedidos.

O ponto 4 é o que responde à pergunta do produto: acrescentar fontes reduz o silêncio, ou só
repete o mesmo com outras palavras?

USO:  python scripts/evaluate_news_sources.py
SAI:  docs/evaluation/evaluation_news_sources.md
"""

from __future__ import annotations

import collections
import json
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime, timedelta

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_news_sources.md"
TIMEOUT = 25
DIAS = 3


def _json(url: str):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "investigator/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001
        return None


def _norm(t: str) -> str:
    """Chave de comparação entre fontes: minúsculas, sem pontuação, sem espaços a mais."""
    return re.sub(r"[^a-z0-9 ]+", " ", (t or "").lower()).strip()


def finnhub(t: str, desde: str, ate: str) -> list[tuple[str, str]]:
    k = os.environ.get("FINNHUB_API_KEY", "")
    d = _json(f"https://finnhub.io/api/v1/company-news?symbol={t}&from={desde}&to={ate}&token={k}")
    return [(a.get("headline", ""),
             datetime.fromtimestamp(a["datetime"], tz=UTC).isoformat())
            for a in (d or []) if a.get("headline") and a.get("datetime")]


def alphavantage(t: str, *_a) -> list[tuple[str, str]]:
    k = os.environ.get("ALPHAVANTAGE_API_KEY", "")
    d = _json("https://www.alphavantage.co/query?function=NEWS_SENTIMENT"
              f"&tickers={t}&limit=200&apikey={k}")
    out = []
    for a in (d or {}).get("feed", []) if isinstance(d, dict) else []:
        q = a.get("time_published", "")
        iso = (f"{q[:4]}-{q[4:6]}-{q[6:8]}T{q[9:11]}:{q[11:13]}:00+00:00"
               if len(q) == 15 else "")
        if a.get("title"):
            out.append((a["title"], iso))
    return out


def polygon(t: str, *_a) -> list[tuple[str, str]]:
    k = os.environ.get("POLYGON_API_KEY", "")
    d = _json(f"https://api.polygon.io/v2/reference/news?ticker={t}&limit=200&apiKey={k}")
    return [(a.get("title", ""), a.get("published_utc", ""))
            for a in (d or {}).get("results", []) if isinstance(d, dict) and a.get("title")]


FONTES = {"Finnhub": finnhub, "Alpha Vantage": alphavantage, "Polygon": polygon}


def main() -> None:
    try:
        from investigator.config import load_env
        load_env()
    except Exception:  # noqa: BLE001
        pass
    import yaml

    from investigator.news_fetcher.relevance import is_relevant

    cfg = yaml.safe_load((RAIZ / "config" / "alerts.yaml").read_text(encoding="utf-8"))
    tickers = (cfg.get("news") or {}).get("tickers") or []
    hoje = datetime.now(UTC).date()
    desde = (hoje - timedelta(days=DIAS)).isoformat()

    bruto: dict[str, dict[str, list]] = {f: {} for f in FONTES}
    relev: dict[str, dict[str, set]] = {f: {} for f in FONTES}
    frescura: dict[str, list[float]] = collections.defaultdict(list)

    for t in tickers:
        for nome, fn in FONTES.items():
            try:
                itens = fn(t, desde, hoje.isoformat())
            except Exception:  # noqa: BLE001
                itens = []
            bruto[nome][t] = itens
            bons = {_norm(h) for h, _ in itens if is_relevant(h, t)}
            relev[nome][t] = bons
            recentes = [q for h, q in itens if q and is_relevant(h, t)]
            if recentes:
                try:
                    d = max(datetime.fromisoformat(q.replace("Z", "+00:00")) for q in recentes)
                    frescura[nome].append((datetime.now(UTC) - d).total_seconds() / 3600)
                except Exception:  # noqa: BLE001
                    pass
            time.sleep(0.4)  # cortesia com os limites gratuitos
        print(f"  {t} feito", flush=True)

    linhas = []
    for nome in FONTES:
        nb = sum(len(v) for v in bruto[nome].values())
        nr = sum(len(v) for v in relev[nome].values())
        pc = 100.0 * nr / nb if nb else 0.0
        fr = frescura[nome]
        med = sorted(fr)[len(fr) // 2] if fr else float("nan")
        linhas.append(f"| {nome} | {nb} | {nr} | {pc:.0f}% | {med:.1f}h | "
                      f"{len([v for v in relev[nome].values() if v])}/{len(tickers)} |")

    # complemento: quantas relevantes cada fonte traz que NENHUMA outra traz
    exclusivas = {}
    for nome in FONTES:
        n = 0
        for t in tickers:
            outras = set().union(*[relev[o][t] for o in FONTES if o != nome]) if len(FONTES) > 1 \
                else set()
            n += len(relev[nome][t] - outras)
        exclusivas[nome] = n
    uniao = sum(len(set().union(*[relev[o][t] for o in FONTES])) for t in tickers)
    so_finnhub = sum(len(relev["Finnhub"][t]) for t in tickers)

    excl = "\n".join(f"| {n} | {v} | {100*v/uniao:.0f}% |" for n, v in exclusivas.items())

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(f"""# Fontes de notícias: qual serve, e em que se completam

> **Gerado por** `scripts/evaluate_news_sources.py`. Não editar à mão.
> **Janela:** últimos {DIAS} dias · **watchlist:** {len(tickers)} empresas ·
> **corrido em:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC

## 1. Volume não é qualidade

A coluna que decide não é quantas notícias a fonte devolve: é quantas **sobrevivem ao filtro de
relevância** que já está em produção. Uma fonte generosa e mal etiquetada custa pedidos e não
acrescenta nada.

| Fonte | Devolvidas | Relevantes | Precisão | Frescura (mediana) | Cobertura |
|---|---|---|---|---|---|
{chr(10).join(linhas)}

## 2. Somar fontes acrescenta, ou repete?

É a pergunta que decide, e mede-se contando quantas manchetes relevantes cada fonte traz que
**nenhuma outra** traz.

| Fonte | Exclusivas | Do total |
|---|---|---|
{excl}

- Manchetes relevantes distintas com **as três** fontes: **{uniao}**
- Só com o Finnhub (o que o sistema faz hoje): **{so_finnhub}**
- Ganho: **{uniao - so_finnhub}** manchetes ({100*(uniao-so_finnhub)/so_finnhub:.0f}% mais)

## 3. Rejeitada, e porquê

O **Tiingo** foi sondado com a chave existente e devolve **HTTP 403** no endpoint de notícias:
exige plano pago. Fica registado porque parecia servir, tal como o Stooq no caso dos preços.

O **GNews** responde e traz URL, mas **não é por empresa** — é uma pesquisa por palavras. Usá-lo
obrigaria a inferir a empresa a partir do texto, acrescentando um erro que as outras três não
têm. Não entra por essa razão, e não por limite de pedidos.

## 4. Leitura honesta

Acrescentar fontes serve para duas coisas diferentes, e só uma delas é sobre volume:

1. **Cobertura**: mais manchetes distintas, portanto menos dias em que o sistema não tem nada
   para dizer sobre uma empresa que se mexeu.
2. **Redundância**: quando uma fonte falha ou bloqueia, as outras respondem. É a mesma razão
   pela qual os preços já vêm de uma cadeia e não de uma fonte só.

O que **não** melhora é a latência de descoberta de forma garantida: as três publicam com atrasos
próprios, e o ganho depende de qual delas viu a história primeiro. Isso mede-se com o tempo, no
registo de latência, e não se afirma aqui.
""", encoding="utf-8")

    print(f"\nunião {uniao} · só Finnhub {so_finnhub} · exclusivas {exclusivas}")
    print(f"-> {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    if not os.environ.get("FINNHUB_API_KEY"):
        try:
            from investigator.config import load_env
            load_env()
        except Exception:  # noqa: BLE001
            print("sem .env", file=sys.stderr)
    main()
