"""Testes da avaliação de recuperação (puros, determinísticos)."""

import numpy as np
import pytest

from src.evaluation.retrieval_eval import (
    expected_random_precision,
    recency_precision_at_k,
    retrieval_precision_at_k,
    same_ticker_forbid,
)


def _toy():
    # 6 notícias: 3 do setor "tech" (T1,T2,T3) e 3 do setor "bank" (B1,B2,B3).
    # Embeddings: por setor, vetores quase idênticos → vizinhos do mesmo setor.
    emb = np.array(
        [
            [1.0, 0.0], [0.99, 0.10], [0.98, 0.05],   # tech
            [0.0, 1.0], [0.10, 0.99], [0.05, 0.98],   # bank
        ]
    )
    sectors = np.array(["tech", "tech", "tech", "bank", "bank", "bank"])
    tickers = np.array(["AAPL", "MSFT", "NVDA", "JPM", "BAC", "C"])
    dates = np.array(["2023-01-01", "2023-02-01", "2023-03-01",
                      "2023-01-15", "2023-02-15", "2023-03-15"])
    return emb, sectors, tickers, dates


def test_precision_perfeita_quando_setores_separados():
    emb, sectors, tickers, _ = _toy()
    forbid = same_ticker_forbid(tickers, tickers)  # cross-ticker
    p = retrieval_precision_at_k(emb, emb, sectors, sectors, k=2, forbid=forbid)
    assert p == pytest.approx(1.0)  # vizinhos cross-ticker são todos do mesmo setor


def test_forbid_exclui_mesma_empresa():
    _, _, tickers, _ = _toy()
    forbid = same_ticker_forbid(tickers, tickers)
    # diagonal (mesma empresa consigo) tem de estar proibida
    assert forbid.diagonal().all()


def test_taxa_base_aleatoria():
    emb, sectors, tickers, _ = _toy()
    forbid = same_ticker_forbid(tickers, tickers)
    # excluindo a própria empresa: 2 do mesmo setor entre 5 permitidos → 0.4
    assert expected_random_precision(sectors, sectors, forbid) == pytest.approx(0.4)


def test_recencia_precision():
    emb, sectors, tickers, dates = _toy()
    forbid = same_ticker_forbid(tickers, tickers)
    p = recency_precision_at_k(sectors, sectors, dates, k=2, forbid=forbid)
    assert 0.0 <= p <= 1.0  # valor válido; recência não conhece semântica


def test_embeddings_batem_a_taxa_base():
    """Os embeddings (1.0) devem superar claramente a taxa-base aleatória (0.4)."""
    emb, sectors, tickers, _ = _toy()
    forbid = same_ticker_forbid(tickers, tickers)
    p_emb = retrieval_precision_at_k(emb, emb, sectors, sectors, k=2, forbid=forbid)
    p_rand = expected_random_precision(sectors, sectors, forbid)
    assert p_emb > p_rand
