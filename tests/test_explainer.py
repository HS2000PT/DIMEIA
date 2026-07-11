"""Testes do motor de explicação para o Gatilho 2 (notícia + precedentes)."""

from investigator.anomaly_detector.detector import AnomalyResult
from investigator.explanation_engine.explainer import explain_anomaly, explain_news_impact
from investigator.historical_kb.record import NewsRecord


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


def test_explica_anomalia_em_linguagem_simples():
    """Gatilho 1: z-score + leitura em linguagem simples para o não-especialista."""
    res = AnomalyResult(
        is_anomaly=True, z_score=7.61, last_return=0.1982,
        mean=-0.0092, std=0.0273, window=20, threshold=3.0,
    )
    text = explain_anomaly("TSLA", res)
    assert "Anomaly detected for TSLA" in text
    assert "z-score: +7.61" in text
    assert "7.6 standard deviations" in text                 # rigor (mantém a estatística)
    assert "7.6x this stock's typical daily swing" in text   # leitura em linguagem simples


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


def test_aviso_de_direcao_mista_quando_precedentes_divergem():
    """A lição do CS3 no produto: sinais mistos nos precedentes → aviso explícito."""
    mistos = [
        (NewsRecord(date="2023-01-01", ticker="A", headline="h1", impacts={"3": 0.05}), 0.9),
        (NewsRecord(date="2023-01-02", ticker="A", headline="h2", impacts={"3": -0.03}), 0.8),
    ]
    texto = explain_news_impact("A", "consulta", mistos, horizon=3)
    assert "BOTH directions" in texto

    concordantes = [
        (NewsRecord(date="2023-01-01", ticker="A", headline="h1", impacts={"3": 0.05}), 0.9),
        (NewsRecord(date="2023-01-02", ticker="A", headline="h2", impacts={"3": 0.02}), 0.8),
    ]
    texto2 = explain_news_impact("A", "consulta", concordantes, horizon=3)
    assert "BOTH directions" not in texto2


def test_direcao_unanime_e_descritiva_nunca_previsao():
    todos_sobem = [
        (NewsRecord(date="2023-01-01", ticker="A", headline="h1", impacts={"3": 0.05}), 0.9),
        (NewsRecord(date="2023-01-02", ticker="A", headline="h2", impacts={"3": 0.02}), 0.8),
    ]
    texto = explain_news_impact("A", "consulta", todos_sobem, horizon=3)
    assert "2 of 2 shown cases moved up" in texto
    assert "not a forecast" in texto
    todos_descem = [
        (NewsRecord(date="2023-01-01", ticker="A", headline="h1", impacts={"3": -0.05}), 0.9),
    ]
    texto2 = explain_news_impact("A", "consulta", todos_descem, horizon=3)
    assert "1 of 1 shown cases moved down" in texto2


def test_idade_dos_precedentes_so_com_today():
    precs = [
        (NewsRecord(date="2023-01-01", ticker="A", headline="h1", impacts={"3": 0.05}), 0.9),
    ]
    sem_idade = explain_news_impact("A", "consulta", precs, horizon=3)
    assert "ago)" not in sem_idade  # demo/tese: byte-igual ao histórico
    com_idade = explain_news_impact("A", "consulta", precs, horizon=3, today="2026-07-11")
    assert "(4y ago)" in com_idade  # 2023-01-01 → ~3,5 anos → arredonda a 4


def test_attach_news_context_com_e_sem_noticia():
    from investigator.explanation_engine.explainer import attach_news_context

    base = "🔺 Anomaly detected for TSLA: +5.00% today"
    com = attach_news_context(base, "Tesla recalls vehicles", news_date="2026-07-10",
                              today="2026-07-11")
    assert base in com
    assert 'Possible explanation (1d ago): "Tesla recalls vehicles"' in com
    sem = attach_news_context(base, None)
    assert "No relevant news found in the last 48h" in sem
    assert base in sem
