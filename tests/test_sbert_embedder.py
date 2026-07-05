"""Validação do SBERT real (gated: marca `sbert`, excluída por defeito).

Demonstra a VANTAGEM semântica do SBERT sobre o baseline lexical: uma consulta com
significado parecido mas SEM palavras em comum deve recuperar o precedente certo — algo
que o `HashingEmbedder` (sobreposição de palavras) não consegue.

Correr explicitamente:  pytest -m sbert
Requer `sentence-transformers` instalado; descarrega o modelo na 1.ª execução.
"""

import importlib.util

import pandas as pd
import pytest

pytestmark = pytest.mark.sbert

_HAS_ST = importlib.util.find_spec("sentence_transformers") is not None


def _prices() -> dict[str, pd.Series]:
    dates = pd.bdate_range("2023-05-22", periods=12)
    return {
        t: pd.Series(range(100, 112), index=dates, dtype="float64")
        for t in ("NVDA", "JPM", "AAPL")
    }


def _news() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"date": "2023-05-25", "ticker": "NVDA",
             "headline": "Nvidia guidance surges on demand for AI data-centre chips"},
            {"date": "2023-05-25", "ticker": "JPM",
             "headline": "JPMorgan steps in amid regional banking turmoil"},
            {"date": "2023-05-25", "ticker": "AAPL",
             "headline": "Apple unveils new iPhone with strong demand"},
        ]
    )


@pytest.mark.skipif(not _HAS_ST, reason="sentence-transformers não instalado")
def test_sbert_recupera_por_semantica_nao_por_palavras():
    from investigator.historical_kb.embedder import SbertEmbedder
    from investigator.historical_kb.knowledge_base import HistoricalKB

    embedder = SbertEmbedder()
    assert embedder.dim >= 256  # all-MiniLM-L6-v2 → 384

    kb = HistoricalKB.build(_news(), _prices(), embedder)
    assert len(kb) == 3

    # Consulta semanticamente próxima da notícia da Nvidia, mas sem palavras em comum.
    query = "Graphics processor maker lifts outlook on artificial-intelligence accelerator sales"
    hits = kb.find_precedents(query, embedder, top_k=3)
    assert hits[0][0].ticker == "NVDA"
    assert hits[0][1] > 0.3  # similaridade clara apesar de zero sobreposição lexical
