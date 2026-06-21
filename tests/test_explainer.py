"""Testes do motor de explicação para o Gatilho 2 (notícia + precedentes)."""

from src.explanation_engine.explainer import explain_news_impact
from src.historical_kb.record import NewsRecord


def _precedents():
    return [
        (NewsRecord(date="2023-05-25", ticker="NVDA", headline="AI chips demand soars",
                    impacts={"1": 0.02, "3": 0.04, "5": 0.05}), 0.91),
        (NewsRecord(date="2023-06-13", ticker="NVDA", headline="New AI accelerator",
                    impacts={"1": 0.05, "3": 0.04, "5": 0.05}), 0.80),
    ]


def test_explica_impacto_com_precedentes():
    text = explain_news_impact("NVDA", "Nvidia raises outlook", _precedents(), horizon=3)
    assert "News alert for NVDA" in text
    assert "+4.00%" in text          # média de 0.04 e 0.04
    assert "sim 0.91" in text
    assert "not a price prediction" in text


def test_sem_precedentes():
    text = explain_news_impact("XYZ", "Algo novo", [], horizon=3)
    assert "No similar historical precedents" in text


def test_explicacao_fiel_aos_precedentes_recuperados():
    """Fidelidade (XAI): a explicação reflete EXATAMENTE os precedentes e scores recuperados."""
    precs = _precedents()
    text = explain_news_impact("NVDA", "Nvidia raises outlook", precs, horizon=3)
    for rec, score in precs:
        assert rec.date in text          # cada data aparece
        assert rec.ticker in text        # cada ticker aparece
        assert rec.headline in text      # cada título aparece
        assert f"sim {score:.2f}" in text  # o score exato recuperado aparece
    # nenhuma data/título inventado: o nº de linhas de precedente == nº de precedentes
    assert text.count("sim ") == len(precs)


def test_media_ignora_nan():
    precs = [
        (NewsRecord(date="2023-01-01", ticker="A", headline="h1",
                    impacts={"3": float("nan")}), 0.9),
        (NewsRecord(date="2023-01-02", ticker="A", headline="h2",
                    impacts={"3": 0.04}), 0.8),
    ]
    text = explain_news_impact("A", "consulta", precs, horizon=3)
    assert "+4.00%" in text   # média ignora o NaN → só 0.04
    assert "n/a" in text       # o precedente com NaN aparece como n/a na lista
