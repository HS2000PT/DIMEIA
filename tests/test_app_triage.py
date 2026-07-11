"""AppTest do painel único (redesenho de produto): abas por ticker, risco de fundo (RQ4),
gráfico anotado, e o histórico partilhado (o MESMO que o Telegram recebeu).

Corre só onde o streamlit está instalado (local, stack app); no CI leve é saltado.
Os preços são simulados (monkeypatch) e o histórico partilhado NUNCA toca a rede real —
tudo isolado via `investigator.alerts_history.fetch_remote`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("streamlit")

import streamlit as st  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402

from investigator.alerts_history import HistoryEntry  # noqa: E402

APP = "app/streamlit_app.py"


def _fake_history(ticker: str, period: str = "6mo") -> pd.DataFrame:
    rng = np.random.default_rng(1)
    close = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, 60)))
    idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=60, freq="D")
    return pd.DataFrame({"Close": close}, index=idx)


@pytest.fixture(autouse=True)
def _limpa_caches_streamlit():
    # st.cache_data/cache_resource persistem entre instâncias de AppTest no mesmo processo —
    # sem isto, o monkeypatch de um teste podia "vazar" para o histórico/preços de outro.
    st.cache_data.clear()
    st.cache_resource.clear()
    yield


def _run(monkeypatch, history: list[HistoryEntry] | None = None) -> AppTest:
    import investigator.alerts_history as alerts_history
    import investigator.market_data.prices as prices

    monkeypatch.setattr(prices, "get_price_history", _fake_history)
    monkeypatch.setattr(alerts_history, "fetch_remote",
                        lambda url, timeout=5.0: history or [])
    at = AppTest.from_file(APP)
    at.run(timeout=120)
    return at


def _todos_dataframes_texto(at: AppTest) -> str:
    """Concatena o conteúdo de todos os dataframes renderizados (procura ampla, ignora onde)."""
    partes = []
    for el in at.dataframe:
        try:
            partes.append(el.value.to_csv())
        except Exception:  # noqa: BLE001
            partes.append(str(el.value))
    return "\n".join(partes)


def test_board_sem_excecoes_com_uma_aba_por_ticker(monkeypatch):
    at = _run(monkeypatch)
    assert not at.exception
    # 10 tickers no watchlist (config/alerts.yaml) — uma aba principal por cada.
    assert len(at.tabs) >= 10


def test_titulo_e_disclaimer_presentes_sem_navegacao_lateral(monkeypatch):
    at = _run(monkeypatch)
    assert not at.exception
    titles = [t.value for t in at.title]
    assert any("Markets now" in t for t in titles)
    # já não há radio de navegação (painel único, não multi-página)
    assert len(at.sidebar.radio) == 0


def test_risco_de_fundo_aparece_quando_ha_modelo(monkeypatch):
    at = _run(monkeypatch)
    assert not at.exception
    metric_labels = [m.label for m in at.metric]
    assert any("Background risk" in lbl for lbl in metric_labels)


def test_risco_de_fundo_ausente_sem_modelo(monkeypatch):
    import investigator.triage.infer as infer

    monkeypatch.setattr(infer, "load_context_bundle", lambda path=None: None)
    at = _run(monkeypatch)
    assert not at.exception
    metric_labels = [m.label for m in at.metric]
    assert not any("Background risk" in lbl for lbl in metric_labels)


def test_historico_partilhado_aparece_na_tabela_do_ticker(monkeypatch):
    hist = [HistoryEntry(date="2026-07-08", ticker="AAPL", kind="market",
                         text="Anomaly detected for AAPL: a very specific unique marker text")]
    at = _run(monkeypatch, history=hist)
    assert not at.exception
    assert "a very specific unique marker text" in _todos_dataframes_texto(at)


def test_sem_historico_mostra_aviso_gracioso_e_nao_rebenta(monkeypatch):
    at = _run(monkeypatch, history=[])
    assert not at.exception
    captions = [c.value for c in at.caption]
    assert any("No shared alert history available" in c for c in captions)


def test_expander_method_e_evaluation_presente(monkeypatch):
    at = _run(monkeypatch)
    assert not at.exception
    assert len(at.expander) >= 1
    headers_and_labels = [e.label for e in at.expander]
    assert any("Method" in lbl for lbl in headers_and_labels)


def test_app_boota_sem_plotly(monkeypatch):
    """A app NUNCA cai por causa do gráfico interativo: sem plotly, degrada para line_chart.
    (Caso real: deploy em Python 3.14 sem wheels para a stack pinada → plotly ausente.)"""
    import investigator.alerts_history as alerts_history
    import investigator.market_data.prices as prices

    monkeypatch.setenv("INVESTIGATOR_NO_PLOTLY", "1")
    monkeypatch.setattr(prices, "get_price_history", _fake_history)
    monkeypatch.setattr(alerts_history, "fetch_remote", lambda url, timeout=5.0: [])
    at = AppTest.from_file(APP)
    at.run(timeout=120)
    assert not at.exception
    captions = [c.value for c in at.caption]
    assert any("Interactive chart unavailable" in c for c in captions)
