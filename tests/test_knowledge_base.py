"""Testes da base de conhecimento histórica (puros: usam o HashingEmbedder, sem torch)."""

from pathlib import Path

import pandas as pd
import pytest

from investigator.historical_kb.embedder import HashingEmbedder
from investigator.historical_kb.knowledge_base import HistoricalKB

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


def test_find_precedents_rejeita_embedder_de_dimensao_diferente():
    """Guarda (R1): consultar com um embedder de dimensão diferente da KB falha com erro claro."""
    news, prices = _sample_inputs()
    kb = HistoricalKB.build(news, prices, HashingEmbedder(dim=64))
    with pytest.raises(ValueError, match="dim mismatch"):
        kb.find_precedents("Apple unveils new iPhone", HashingEmbedder(dim=32), top_k=1)


def test_formato_compacto_da_o_MESMO_resultado_que_o_jsonl(tmp_path):
    """⚠️ O formato compacto existe por uma medição: a base de 38 214 casos custava 655 MB de
    RAM em JSONL e o contentor de produção tem 512 MB. Em float32 são 25 MB.

    Mas só serve se devolver exactamente os mesmos precedentes. É isso que este teste fixa.
    """
    import numpy as np

    news, prices = _sample_inputs()
    emb = HashingEmbedder(dim=16)
    kb = HistoricalKB.build(news, prices, emb)
    consulta = "chip demand"
    esperado = [(r.headline, round(s, 4)) for r, s in kb.find_precedents(consulta, emb, top_k=3)]

    meta, vec = tmp_path / "meta.jsonl", tmp_path / "vec.npy"
    kb.save_compact(meta, vec)
    compacta = HistoricalKB.load_compact(meta, vec)

    assert np.load(vec).dtype == np.float32, "os vectores têm de ficar em float32"
    obtido = [(r.headline, round(s, 4))
              for r, s in compacta.find_precedents(consulta, emb, top_k=3)]
    assert obtido == esperado, "o formato compacto tem de devolver os mesmos precedentes"


def test_compacto_recusa_metadados_e_matriz_desalinhados(tmp_path):
    """Se os dois ficheiros forem regenerados em alturas diferentes, os precedentes passariam
    a ser atribuídos às manchetes erradas, em silêncio. Tem de rebentar."""
    import numpy as np

    news, prices = _sample_inputs()
    kb = HistoricalKB.build(news, prices, HashingEmbedder(dim=16))
    meta, vec = tmp_path / "meta.jsonl", tmp_path / "vec.npy"
    kb.save_compact(meta, vec)
    np.save(vec, np.load(vec)[:1])  # a matriz encolhe, os metadados não

    with pytest.raises(ValueError, match="não batem certo"):
        HistoricalKB.load_compact(meta, vec)


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


def test_load_lean_da_os_mesmos_precedentes_e_larga_as_listas():
    """`lean=True` muda a forma em memoria, nunca o resultado.

    Medido a 2026-09-04 sobre a base viva real: 10 968 registos custavam 136,7 MB em listas
    de `float` de Python e 22,3 MB com a matriz float32 -- 6,1x -- com top-5 identico em 6/6
    consultas. O contentor tem 512 MB e o worker corria entre 518 e 970 MB, com R14 a cada
    poucos minutos. A base viva e a que CRESCE, logo era a que mais precisava disto.
    """
    import json
    import pathlib
    import tempfile

    import numpy as np

    rng = np.random.default_rng(20260904)
    linhas = []
    for i in range(40):
        v = rng.normal(size=16)
        v = v / np.linalg.norm(v)
        linhas.append({"date": f"2026-01-{i % 28 + 1:02d}", "ticker": "NVDA",
                       "headline": f"manchete {i}",
                       "impacts": {"1": 0.01, "3": 0.02, "5": 0.03},
                       "embedding": [round(float(x), 5) for x in v]})
    d = pathlib.Path(tempfile.mkdtemp()) / "kb.jsonl"
    d.write_text("\n".join(json.dumps(x) for x in linhas), encoding="utf-8")

    gordo = HistoricalKB.load(d)
    magro = HistoricalKB.load(d, lean=True)
    assert len(gordo) == len(magro) == 40

    qv = list(np.ones(16) / 4.0)

    class _Fixo:
        """Consulta fixa: o que se compara e a KB, nao o embedder."""

        def encode(self, textos):
            return [qv]

    a = [(r.ticker, r.headline) for r, _ in gordo.find_precedents("x", _Fixo(), top_k=5)]
    b = [(r.ticker, r.headline) for r, _ in magro.find_precedents("x", _Fixo(), top_k=5)]
    assert a == b, "lean mudou a ordem dos precedentes"

    # as listas foram mesmo largadas: a matriz passa a ser a unica copia dos vectores
    assert all(r.embedding is None for r in magro.records)
    assert all(r.embedding is not None for r in gordo.records)


def test_load_lean_com_registos_sem_embedding_nao_muda_nada():
    """Controlo: se algum registo nao tem vector, `lean` desiste e devolve o caminho antigo."""
    import json
    import pathlib
    import tempfile

    d = pathlib.Path(tempfile.mkdtemp()) / "kb.jsonl"
    d.write_text(json.dumps({"date": "2026-01-01", "ticker": "NVDA", "headline": "h",
                             "impacts": {"1": 0.0}, "embedding": None}), encoding="utf-8")
    kb = HistoricalKB.load(d, lean=True)
    assert len(kb) == 1
    assert kb._matrix is None
