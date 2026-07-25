"""Testes da cadeia de fallback de preços (parsing puro + ordem da cadeia; sem rede).

Contexto: em produção (GitHub Actions) o yfinance ficou bloqueado e o pipeline de mercado
esteve CEGO — 0 alertas de mercado e 0 resumos diários no canal (2026-07-13). Estes testes
provam que (1) cada parser lê o formato real da fonte, (2) a cadeia tenta pela ordem
definida e salta fontes sem chave, (3) `get_price_history` cai para a cadeia quando o
yfinance falha em pedidos diários.
"""

from __future__ import annotations

import pandas as pd
import pytest

from investigator.market_data import prices
from investigator.market_data.prices import (
    fallback_daily,
    get_price_history,
    parse_alphavantage_json,
    parse_polygon_json,
    parse_stooq_csv,
    parse_tiingo_json,
)

STOOQ_CSV = """Date,Open,High,Low,Close,Volume
2026-07-09,159.00,163.10,158.20,162.50,50123000
2026-07-10,162.80,164.00,160.10,161.20,43210000
2026-07-08,157.00,159.90,156.50,158.90,39990000
"""

TIINGO_JSON = [
    {"date": "2026-07-09T00:00:00.000Z", "close": 162.0, "adjClose": 162.5,
     "open": 159.0, "adjOpen": 159.1, "high": 163.1, "low": 158.2, "volume": 50123000},
    {"date": "2026-07-10T00:00:00.000Z", "close": 161.0, "adjClose": 161.2,
     "open": 162.8, "high": 164.0, "low": 160.1, "volume": 43210000},
]

POLYGON_JSON = {
    "status": "OK",
    "results": [
        {"t": 1783987200000, "o": 159.0, "h": 163.1, "l": 158.2, "c": 162.5, "v": 50123000},
        {"t": 1784073600000, "o": 162.8, "h": 164.0, "l": 160.1, "c": 161.2, "v": 43210000},
    ],
}

AV_JSON = {
    "Time Series (Daily)": {
        "2026-07-10": {"1. open": "162.80", "2. high": "164.00", "3. low": "160.10",
                       "4. close": "161.20", "5. volume": "43210000"},
        "2026-07-09": {"1. open": "159.00", "2. high": "163.10", "3. low": "158.20",
                       "4. close": "162.50", "5. volume": "50123000"},
    }
}


def test_parse_stooq_ordena_e_extrai_close():
    df = parse_stooq_csv(STOOQ_CSV)
    assert list(df.index) == sorted(df.index)          # ordenado por data
    assert df.index[-1] == pd.Timestamp("2026-07-10")
    assert df["Close"].iloc[-1] == pytest.approx(161.20)
    assert "Volume" in df.columns


def test_parse_stooq_sem_dados_levanta():
    with pytest.raises(RuntimeError):
        parse_stooq_csv("No data")
    with pytest.raises(RuntimeError):
        parse_stooq_csv("")


def test_parse_tiingo_usa_adjclose():
    df = parse_tiingo_json(TIINGO_JSON)
    assert len(df) == 2
    assert df["Close"].iloc[0] == pytest.approx(162.5)  # adjClose, não close
    with pytest.raises(RuntimeError):
        parse_tiingo_json([])


def test_parse_polygon_converte_epoch_ms():
    df = parse_polygon_json(POLYGON_JSON)
    assert len(df) == 2
    assert df["Close"].iloc[-1] == pytest.approx(161.2)
    with pytest.raises(RuntimeError):
        parse_polygon_json({"status": "OK", "results": []})


def test_parse_alphavantage_e_rate_limit():
    df = parse_alphavantage_json(AV_JSON)
    assert list(df.index) == sorted(df.index)
    assert df["Close"].iloc[-1] == pytest.approx(161.20)
    # resposta típica de rate-limit: sem a série → levanta (a cadeia passa à frente)
    with pytest.raises(RuntimeError):
        parse_alphavantage_json({"Information": "rate limit"})


def test_alphavantage_janela_fora_do_intervalo_levanta(monkeypatch):
    """Regressão do contrato da cadeia: o 'compact' do AV traz só ~100 dias; se a janela
    pedida cai toda fora, o slice fica vazio → tem de LEVANTAR (senão preços vazios
    propagavam-se como 'sucesso' por ser a última fonte da cadeia)."""
    from investigator import config

    class _Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return AV_JSON  # série de 2026-07-09/10

    monkeypatch.setattr(config, "ALPHAVANTAGE_API_KEY", "chave-de-teste", raising=False)
    monkeypatch.setattr("requests.get", lambda *a, **k: _Resp())
    with pytest.raises(RuntimeError):
        prices.fetch_alphavantage_daily("NVDA", "2020-01-01", "2020-02-01")
    # janela que CONTÉM os dados devolve normalmente
    df = prices.fetch_alphavantage_daily("NVDA", "2026-07-01", "2026-07-31")
    assert df["Close"].iloc[-1] == pytest.approx(161.20)


def _df_ok() -> pd.DataFrame:
    idx = pd.to_datetime(["2026-07-09", "2026-07-10"])
    return pd.DataFrame({"Close": [162.5, 161.2]}, index=idx)


def test_fallback_daily_respeita_a_ordem_e_salta_sem_chave(monkeypatch):
    chamadas: list[str] = []

    def falha(nome):
        def _f(t, s, e):
            chamadas.append(nome)
            raise RuntimeError(f"{nome} indisponível")
        return _f

    def serve(t, s, e):
        chamadas.append("polygon")
        return _df_ok()

    monkeypatch.setattr(prices, "_FALLBACKS", [
        ("tiingo", falha("tiingo")), ("polygon", serve),
        ("stooq", falha("stooq")), ("alphavantage", falha("alphavantage")),
    ])
    df, fonte = fallback_daily("NVDA", "2026-01-01", "2026-07-10")
    assert fonte == "polygon"
    assert chamadas == ["tiingo", "polygon"]  # ordem respeitada; Stooq/AV nem foram chamadas
    assert df["Close"].iloc[-1] == pytest.approx(161.2)


def test_fallback_daily_todas_falham_levanta_com_resumo(monkeypatch):
    monkeypatch.setattr(prices, "_FALLBACKS", [
        ("stooq", lambda t, s, e: (_ for _ in ()).throw(RuntimeError("x"))),
    ])
    with pytest.raises(RuntimeError, match="nenhuma fonte"):
        fallback_daily("NVDA", "2026-01-01", "2026-07-10")


def test_get_price_history_cai_para_a_cadeia_quando_yfinance_falha(monkeypatch):
    def yf_morto(ticker, **kw):
        raise RuntimeError("yfinance bloqueado")

    monkeypatch.setattr(prices, "_yf_history", yf_morto)
    monkeypatch.setattr(prices, "_FALLBACKS", [("stooq", lambda t, s, e: _df_ok())])
    df = get_price_history("NVDA")
    assert df["Close"].iloc[-1] == pytest.approx(161.2)
    # pedidos intradiários NÃO caem para a cadeia (as fontes grátis são diárias)
    with pytest.raises(RuntimeError):
        get_price_history("NVDA", period="5d", interval="15m")


def test_load_close_series_usa_fallback_e_ignora_tickers_mortos(monkeypatch):
    def yf_morto(ticker, **kw):
        raise RuntimeError("yfinance bloqueado")

    monkeypatch.setattr(prices, "_yf_history", yf_morto)
    monkeypatch.setattr(prices, "_FALLBACKS", [
        ("stooq", lambda t, s, e: _df_ok() if t == "NVDA"
         else (_ for _ in ()).throw(RuntimeError("sem dados"))),
    ])
    series = prices.load_close_series(["NVDA", "MORTO"], "2026-07-01", "2026-07-11")
    assert set(series) == {"NVDA"}
    assert series["NVDA"].index.tz is None  # índice tz-naive, pronto para searchsorted
