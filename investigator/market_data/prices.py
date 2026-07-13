"""Camada live: preços de mercado (NYSE/NASDAQ) — yfinance com cadeia de fallback multi-fonte.

Lição de produção (2026-07-13): nos runners partilhados do GitHub Actions o Yahoo bloqueia
IPs e o pipeline de mercado ficou CEGO durante dias (0 alertas de mercado E 0 resumos diários
no canal — provado pelo histórico da branch `alerts-history`). Uma fonte única é um ponto
único de falha; o histórico DIÁRIO tem agora uma cadeia de fallback, do mais generoso para o
mais escasso:

    yfinance → Tiingo → Polygon → Stooq → Alpha Vantage (25 req/dia)

Fontes sem chave configurada são saltadas em silêncio. O Stooq (sem chave) foi testado ao
vivo a 2026-07-13 e devolve agora um desafio anti-bot em JavaScript (proof-of-work) — fica
na cadeia como tentativa oportunista (pode voltar a funcionar noutras redes), mas as fontes
com chave é que são o plano a sério. Nota honesta sobre ajustes: o yfinance
devolve preços ajustados (splits+dividendos), Stooq/Polygon ajustam splits, o Alpha Vantage é
raw — para RETORNOS diários numa janela de ~20 dias a diferença é irrelevante (dividendos são
~centésimos de %; splits são raros e ajustados nas fontes usadas em primeiro).

Desenho (igual ao `news_fetcher`): **parsing puro** (testável sem rede) separado do **HTTP
tardio**. A deteção de anomalias trabalha sobre RETORNOS (não preços) — ver learning.md.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

_OHLCV = ["Open", "High", "Low", "Close", "Volume"]
# períodos yfinance → dias de calendário (para pedir o mesmo intervalo às fontes de fallback)
_PERIOD_DAYS = {"1mo": 31, "3mo": 92, "6mo": 183, "1y": 366, "2y": 731}


# ── Parsing (puro, testável) ───────────────────────────────────────────────────
def _finish(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Normaliza um DataFrame de fallback: índice datetime ordenado, colunas OHLCV."""
    if df.empty:
        raise RuntimeError(f"{source}: resposta sem dados.")
    df = df.sort_index()
    df.index.name = "Date"
    return df[[c for c in _OHLCV if c in df.columns]]


def parse_stooq_csv(text: str) -> pd.DataFrame:
    """CSV diário do Stooq (`Date,Open,High,Low,Close,Volume`) → DataFrame OHLCV."""
    import io

    text = (text or "").strip()
    if not text or text.lower().startswith("no data"):
        raise RuntimeError("Stooq: resposta sem dados.")
    df = pd.read_csv(io.StringIO(text))
    if "Date" not in df.columns or "Close" not in df.columns:
        raise RuntimeError("Stooq: CSV sem as colunas esperadas.")
    df["Date"] = pd.to_datetime(df["Date"])
    return _finish(df.set_index("Date"), "Stooq")


def parse_tiingo_json(payload: list[dict]) -> pd.DataFrame:
    """JSON do Tiingo `/tiingo/daily/{t}/prices` → DataFrame OHLCV (usa adjClose)."""
    rows = {
        pd.to_datetime(str(p.get("date", ""))[:10]): {
            "Open": p.get("adjOpen", p.get("open")),
            "High": p.get("adjHigh", p.get("high")),
            "Low": p.get("adjLow", p.get("low")),
            "Close": p.get("adjClose", p.get("close")),
            "Volume": p.get("adjVolume", p.get("volume")),
        }
        for p in payload or []
        if p.get("date") and (p.get("adjClose") or p.get("close"))
    }
    return _finish(pd.DataFrame.from_dict(rows, orient="index"), "Tiingo")


def parse_polygon_json(payload: dict) -> pd.DataFrame:
    """JSON do Polygon `/v2/aggs/.../range/1/day/...` → DataFrame OHLCV."""
    results = (payload or {}).get("results") or []
    rows = {
        pd.to_datetime(int(r["t"]), unit="ms").normalize(): {
            "Open": r.get("o"), "High": r.get("h"), "Low": r.get("l"),
            "Close": r.get("c"), "Volume": r.get("v"),
        }
        for r in results
        if r.get("t") and r.get("c") is not None
    }
    return _finish(pd.DataFrame.from_dict(rows, orient="index"), "Polygon")


def parse_alphavantage_json(payload: dict) -> pd.DataFrame:
    """JSON do Alpha Vantage `TIME_SERIES_DAILY` → DataFrame OHLCV.

    Sem a chave "Time Series (Daily)" (ex.: resposta de rate-limit com "Information"),
    levanta — quem chama passa à fonte seguinte.
    """
    series = (payload or {}).get("Time Series (Daily)") or {}
    rows = {
        pd.to_datetime(d): {
            "Open": float(v.get("1. open", "nan")),
            "High": float(v.get("2. high", "nan")),
            "Low": float(v.get("3. low", "nan")),
            "Close": float(v.get("4. close", "nan")),
            "Volume": float(v.get("5. volume", "nan")),
        }
        for d, v in series.items()
        if v.get("4. close")
    }
    return _finish(pd.DataFrame.from_dict(rows, orient="index"), "Alpha Vantage")


# ── HTTP (invólucros finos, tardios; levantam em erro — a cadeia decide) ───────
def fetch_stooq_daily(ticker: str, start: str, end: str, timeout: int = 10) -> pd.DataFrame:
    """Histórico diário do Stooq (CSV público, sem chave). Símbolos US levam sufixo `.us`."""
    import requests

    resp = requests.get(
        "https://stooq.com/q/d/l/",
        params={"s": f"{ticker.lower()}.us", "i": "d",
                "d1": start.replace("-", ""), "d2": end.replace("-", "")},
        timeout=timeout,
    )
    resp.raise_for_status()
    return parse_stooq_csv(resp.text)


def fetch_tiingo_daily(ticker: str, start: str, end: str, timeout: int = 10) -> pd.DataFrame:
    """Histórico diário do Tiingo (precisa de TIINGO_API_KEY)."""
    import requests

    from investigator import config

    if not config.TIINGO_API_KEY:
        raise RuntimeError("TIINGO_API_KEY não configurada (ver .env).")
    resp = requests.get(
        f"https://api.tiingo.com/tiingo/daily/{ticker.lower()}/prices",
        params={"startDate": start, "endDate": end, "token": config.TIINGO_API_KEY},
        timeout=timeout,
    )
    resp.raise_for_status()
    return parse_tiingo_json(resp.json())


def fetch_polygon_daily(ticker: str, start: str, end: str, timeout: int = 10) -> pd.DataFrame:
    """Histórico diário do Polygon (precisa de POLYGON_API_KEY; free tier: 5 req/min)."""
    import requests

    from investigator import config

    if not config.POLYGON_API_KEY:
        raise RuntimeError("POLYGON_API_KEY não configurada (ver .env).")
    resp = requests.get(
        f"https://api.polygon.io/v2/aggs/ticker/{ticker.upper()}/range/1/day/{start}/{end}",
        params={"adjusted": "true", "sort": "asc", "limit": 5000,
                "apiKey": config.POLYGON_API_KEY},
        timeout=timeout,
    )
    resp.raise_for_status()
    return parse_polygon_json(resp.json())


def fetch_alphavantage_daily(ticker: str, start: str, end: str,
                             timeout: int = 10) -> pd.DataFrame:
    """Histórico diário do Alpha Vantage (25 req/dia no free tier — ÚLTIMO recurso)."""
    import requests

    from investigator import config

    if not config.ALPHAVANTAGE_API_KEY:
        raise RuntimeError("ALPHAVANTAGE_API_KEY não configurada (ver .env).")
    resp = requests.get(
        "https://www.alphavantage.co/query",
        params={"function": "TIME_SERIES_DAILY", "symbol": ticker.upper(),
                "outputsize": "compact", "apikey": config.ALPHAVANTAGE_API_KEY},
        timeout=timeout,
    )
    resp.raise_for_status()
    df = parse_alphavantage_json(resp.json())
    return df.loc[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]


# A ordem É a política: do mais generoso/estável para o mais escasso (Alpha Vantage tem só
# 25 req/dia — último recurso). Os testes substituem esta lista para provar a ordem e o
# salto de fontes sem chave.
_FALLBACKS: list[tuple[str, object]] = [
    ("tiingo", fetch_tiingo_daily),
    ("polygon", fetch_polygon_daily),
    ("stooq", fetch_stooq_daily),
    ("alphavantage", fetch_alphavantage_daily),
]


def _yf_history(ticker: str, *, period: str | None = None, start: str | None = None,
                end: str | None = None, interval: str = "1d") -> pd.DataFrame:
    """Chamada yfinance isolada (testes fazem monkeypatch aqui). Levanta se vazio."""
    import yfinance as yf

    if period is not None:
        df = yf.Ticker(ticker).history(period=period, interval=interval)
    else:
        df = yf.Ticker(ticker).history(start=start, end=end, interval=interval)
    if df is None or df.empty:
        raise RuntimeError(f"yfinance sem dados para '{ticker}'.")
    return df


def fallback_daily(ticker: str, start: str, end: str) -> tuple[pd.DataFrame, str]:
    """Percorre a cadeia de fallback; devolve (DataFrame, nome da fonte que serviu).

    Fontes sem chave/erradas são saltadas; se TODAS falharem, levanta com o resumo
    dos erros (diagnóstico visível no log do runner).
    """
    errors: list[str] = []
    for name, fetch in _FALLBACKS:
        try:
            return fetch(ticker, start, end), name
        except Exception as exc:  # noqa: BLE001  (uma fonte a falhar não pára a cadeia)
            errors.append(f"{name}: {type(exc).__name__}: {exc}")
    raise RuntimeError(
        f"Sem dados de preços para '{ticker}' em nenhuma fonte — " + " | ".join(errors)
    )


def get_price_history(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    """Histórico recente de preços de um ticker (camada live), com fallback multi-fonte.

    yfinance primeiro (comportamento de sempre); se falhar e o pedido for DIÁRIO, a cadeia
    de fallback serve o mesmo intervalo (as alternativas gratuitas não dão barras intradiárias,
    por isso pedidos com `interval` fino continuam yfinance-only — a app degrada com graça).
    """
    try:
        return _yf_history(ticker, period=period, interval=interval)
    except Exception as exc:  # noqa: BLE001
        if interval != "1d":
            raise RuntimeError(f"Sem dados de preços para o ticker '{ticker}'.") from exc
        dias = _PERIOD_DAYS.get(period, 183)
        start = (date.today() - timedelta(days=dias)).isoformat()
        end = date.today().isoformat()
        df, fonte = fallback_daily(ticker, start, end)
        print(f"[precos {ticker}] yfinance indisponível → servido por {fonte} ({len(df)} dias)")
        return df


def log_returns(close: pd.Series) -> pd.Series:
    """Retornos logarítmicos a partir da série de preços de fecho."""
    return np.log(close / close.shift(1)).dropna()


def load_close_series(tickers: list[str], start: str, end: str) -> dict[str, pd.Series]:
    """Fechos diários por ticker numa janela (para construir KBs/datasets), com fallback.

    Índice tz-naive e ordenado — pronto para `searchsorted` contra datas de notícias.
    Tickers sem dados em NENHUMA fonte são avisados e ignorados (best-effort). A maturação
    da KB viva corre em cima disto no Actions — sem o fallback ficava cega como o resto.
    """
    prices: dict[str, pd.Series] = {}
    for ticker in tickers:
        fonte = "yfinance"
        try:
            df = _yf_history(ticker, start=start, end=end)
        except Exception:  # noqa: BLE001
            try:
                df, fonte = fallback_daily(ticker, start, end)
            except Exception as exc:  # noqa: BLE001
                print(f"  [!] sem precos para {ticker} ({exc}) - ignorado")
                continue
        close = df["Close"].copy()
        idx = pd.to_datetime(close.index)
        close.index = idx.tz_localize(None) if idx.tz is not None else idx
        prices[ticker] = close.sort_index()
        print(f"  [ok] {ticker}: {len(close)} dias ({fonte})")
    return prices
