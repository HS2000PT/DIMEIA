"""Testes da base de conhecimento histórica (puros: usam o HashingEmbedder, sem torch)."""

from pathlib import Path

import pandas as pd
import pytest

from src.historical_kb.embedder import HashingEmbedder
from src.historical_kb.knowledge_base import HistoricalKB

KB_SAMPLE = Path(__file__).resolve().parent.parent / "data" / "samples" / "kb_sample.jsonl"


def _sample_inputs():
    # 10 dias úteis a partir de 2020-01-02; preços crescentes para impactos previsíveis.
    dates = pd.bdate_range("2020-01-02", periods=10)
    prices = {
        "AAPL": pd.Series(
            [100, 101, 102, 103, 104, 105, 106, 107, 108, 109], index=dates, dtype="float64"
        ),
        "TSLA": pd.Series(
            [200, 198, 202, 205, 203, 207, 210, 209, 212, 215], index=dates, dtype="float64"
        ),
    }
    news = pd.DataFrame(
        [
            {"date": "2020-01-06", "ticker": "AAPL", "headline": "Apple unveils new iPhone"},
            {"date": "2020-01-06", "ticker": "TSLA", "headline": "Tesla deliveries beat estimates"},
            {"date": "2020-01-07", "ticker": "AAPL", "headline": "Apple faces supply disruption"},
        ]
    )
    return news, prices


def test_build_calcula_impactos_e_embeddings():
    news, prices = _sample_inputs()
    kb = HistoricalKB.build(news, prices, HashingEmbedder(dim=32))
    assert len(kb) == 3
    aapl = next(r for r in kb.records if r.ticker == "AAPL" and r.date == "2020-01-06")
    # evento em 2020-01-06 (índice 2, preço 102); +1d → 103/102 - 1
    assert aapl.impacts["1"] == pytest.approx(103 / 102 - 1)
    assert aapl.impacts["3"] == pytest.approx(105 / 102 - 1)
    assert aapl.embedding is not None and len(aapl.embedding) == 32


def test_noticia_sem_precos_e_ignorada():
    news, prices = _sample_inputs()
    news = pd.concat(
        [news, pd.DataFrame([{"date": "2020-01-06", "ticker": "XYZ", "headline": "Sem preços"}])],
        ignore_index=True,
    )
    kb = HistoricalKB.build(news, prices, HashingEmbedder(dim=32))
    assert len(kb) == 3  # a notícia de XYZ (sem série de preços) é descartada


def test_find_precedents_recupera_o_mais_semelhante():
    news, prices = _sample_inputs()
    kb = HistoricalKB.build(news, prices, HashingEmbedder(dim=64))
    embedder = HashingEmbedder(dim=64)
    hits = kb.find_precedents("Apple unveils new iPhone", embedder, top_k=2)
    assert len(hits) == 2
    top_record, top_score = hits[0]
    assert top_record.headline == "Apple unveils new iPhone"
    assert top_score == pytest.approx(1.0)  # consulta idêntica ao título → cosseno 1


def test_save_load_roundtrip(tmp_path):
    news, prices = _sample_inputs()
    kb = HistoricalKB.build(news, prices, HashingEmbedder(dim=16))
    path = tmp_path / "kb.jsonl"
    kb.save(path)
    loaded = HistoricalKB.load(path)
    assert len(loaded) == len(kb)
    a, b = kb.records[0], loaded.records[0]
    assert (a.date, a.ticker, a.headline) == (b.date, b.ticker, b.headline)
    assert a.impacts == b.impacts
    assert a.embedding == pytest.approx(b.embedding)


@pytest.mark.skipif(not KB_SAMPLE.exists(), reason="amostra da KB ainda não gerada")
def test_amostra_kb_versionada_carrega_e_recupera():
    """Guarda de regressão: a amostra versionada carrega e a recuperação funciona."""
    kb = HistoricalKB.load(KB_SAMPLE)
    assert len(kb) > 0
    target = kb.records[0]
    hits = kb.find_precedents(target.headline, HashingEmbedder(dim=64), top_k=1)
    assert hits and hits[0][0].headline == target.headline
