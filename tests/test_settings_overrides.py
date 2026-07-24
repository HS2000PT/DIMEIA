"""Testes do núcleo de overrides de definições (puro, fail-open)."""

from __future__ import annotations

from investigator.settings_overrides import (
    current_values,
    merge_overrides,
    validate_overrides,
)


def _base():
    return {"market": {"enabled": True, "threshold": 1.5, "tickers": ["AAPL"]},
            "news": {"enabled": True, "min_similarity": 0.45, "max_per_ticker_per_day": 2}}


def test_validate_filtra_desconhecidos_e_limita():
    raw = {"market_threshold": 2.2, "news_min_similarity": 0.5,
           "desconhecido": 99, "news_max_per_ticker": 3}
    clean = validate_overrides(raw)
    assert clean == {"market_threshold": 2.2, "news_min_similarity": 0.5,
                     "news_max_per_ticker": 3}


def test_validate_clampa_aos_limites():
    # threshold além do máximo (5.0) e similaridade abaixo do mínimo (0.20) são limitados.
    clean = validate_overrides({"market_threshold": 99, "news_min_similarity": -1})
    assert clean["market_threshold"] == 5.0
    assert clean["news_min_similarity"] == 0.20


def test_validate_failopen_valor_mau_e_tipo_errado():
    assert validate_overrides({"market_threshold": "abc"}) == {}
    assert validate_overrides(None) == {}
    assert validate_overrides("não é dict") == {}
    # bool aceita várias formas
    assert validate_overrides({"market_enabled": "false"})["market_enabled"] is False


def test_merge_nao_muta_a_base_e_aplica_no_caminho_certo():
    base = _base()
    cfg = merge_overrides(base, {"market_threshold": 2.0, "news_max_per_ticker": 5})
    assert cfg["market"]["threshold"] == 2.0
    assert cfg["news"]["max_per_ticker_per_day"] == 5
    assert cfg["market"]["tickers"] == ["AAPL"]           # resto intacto
    assert base["market"]["threshold"] == 1.5             # base NÃO mutada


def test_merge_override_invalido_nao_altera_nada():
    base = _base()
    cfg = merge_overrides(base, {"market_threshold": "lixo", "xpto": 1})
    assert cfg["market"]["threshold"] == 1.5  # inválido descartado → valor base mantém-se


def test_current_values_le_os_efetivos():
    vals = current_values(_base())
    assert vals["market_threshold"] == 1.5
    assert vals["news_min_similarity"] == 0.45
    assert vals["news_max_per_ticker"] == 2
