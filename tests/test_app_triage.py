"""AppTest do M5: página News com e sem models/ (ausência graciosa; gate do ML_PLAN §6).

Corre só onde o streamlit está instalado (local, stack app); no CI leve é saltado.
Os preços são simulados (monkeypatch) — nenhum teste toca a rede.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("streamlit")

from streamlit.testing.v1 import AppTest  # noqa: E402

APP = "app/streamlit_app.py"


def _fake_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    rng = np.random.default_rng(1)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 60)))
    return pd.DataFrame({"Close": close})


def _abrir_news_e_clicar(monkeypatch) -> AppTest:
    import investigator.market_data.prices as prices

    monkeypatch.setattr(prices, "get_price_history", _fake_history)
    at = AppTest.from_file(APP)
    at.run(timeout=120)
    at.sidebar.radio[0].set_value("News trigger").run(timeout=120)
    at.button[0].click().run(timeout=120)
    return at


def test_news_com_models_mostra_severidade(monkeypatch):
    at = _abrir_news_e_clicar(monkeypatch)
    assert not at.exception
    subheaders = [s.value for s in at.subheader]
    assert any("Learned severity" in s for s in subheaders)


def test_news_sem_models_e_gracioso(monkeypatch):
    import investigator.triage.infer as infer

    monkeypatch.setattr(infer, "load_context_bundle", lambda path=None: None)
    at = _abrir_news_e_clicar(monkeypatch)
    assert not at.exception
    subheaders = [s.value for s in at.subheader]
    assert not any("Learned severity" in s for s in subheaders)
