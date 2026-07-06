"""Smoke test da thin slice.

- `test_pacote_src_importavel`: o pacote importa (corre sempre).
- `test_pipeline_explicacao`: pipeline deteção->explicação sem rede (corre sempre).
- `test_thin_slice_envia_telegram`: envio REAL via Telegram. Marcado @telegram e OFF por defeito
  (pyproject: -m "not telegram"). Correr com: pytest -m telegram
"""

import importlib

import pytest

from investigator.anomaly_detector.detector import detect_latest
from investigator.explanation_engine.explainer import explain_anomaly


def _serie_anomala() -> list[float]:
    base = [0.001 if i % 2 == 0 else -0.001 for i in range(30)]
    return base + [0.06]


def test_pacote_src_importavel():
    assert importlib.import_module("investigator") is not None


def test_pipeline_explicacao():
    """Deteção -> explicação produz texto rastreável (sem rede)."""
    res = detect_latest(_serie_anomala(), window=20, threshold=3.0)
    texto = explain_anomaly("TEST", res)
    assert res.is_anomaly is True
    assert "Anomaly detected for TEST" in texto
    assert "z-score" in texto


def test_gatilho2_precedentes_offline():
    """Gatilho 2 end-to-end sem rede: notícia -> KB (amostra) -> precedentes -> explicação."""
    from investigator.main import run_news_trigger

    precedents, texto = run_news_trigger(
        "AAPL", "Apple iPhone demand stays strong", send=False
    )
    assert precedents  # a amostra da KB tem registos AAPL semelhantes
    assert "News alert for AAPL" in texto
    assert "similar past headlines" in texto  # linha-resumo da revisão UX (intervalo + média)


@pytest.mark.telegram
def test_thin_slice_envia_telegram():
    """Envia um alerta real ao Telegram (requer .env). Pulado se não configurado."""
    from investigator import config
    from investigator.telegram_bot.sender import send_message

    if not config.telegram_ready():
        pytest.skip("Telegram não configurado no .env.")
    res = detect_latest(_serie_anomala(), window=20, threshold=3.0)
    texto = "[smoke test] " + explain_anomaly("TEST", res)
    resp = send_message(texto)
    assert resp.get("ok") is True


def test_preferred_light_kb_existe_e_responde():
    """O produto (app/runner) usa a KB leve multi-ano quando presente; a demo fica na amostra."""
    from pathlib import Path

    import pytest

    from investigator.main import kb_query_embedder, preferred_light_kb, run_news_trigger

    kb = Path(preferred_light_kb())
    assert kb.exists()
    if kb.name != "kb_fnspid_light.jsonl":
        pytest.skip("KB leve não construída neste checkout (fallback para a amostra é válido)")
    embedder = kb_query_embedder(kb)
    assert embedder.dim == 256  # auto-coerência: a dimensão vem do próprio ficheiro
    precedents, text = run_news_trigger(
        ticker="NVDA", headline="Nvidia earnings beat expectations on AI demand",
        kb_path=kb, embedder=embedder, top_k=3, send=False,
    )
    assert len(precedents) == 3
    assert "not a price prediction" in text
