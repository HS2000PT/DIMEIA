"""Smoke test da thin slice.

- `test_pacote_src_importavel`: o pacote importa (corre sempre).
- `test_pipeline_explicacao`: pipeline deteção->explicação sem rede (corre sempre).
- `test_thin_slice_envia_telegram`: envio REAL via Telegram. Marcado @telegram e OFF por defeito
  (pyproject: -m "not telegram"). Correr com: pytest -m telegram
"""

import importlib

import pytest

from src.anomaly_detector.detector import detect_latest
from src.explanation_engine.explainer import explain_anomaly


def _serie_anomala() -> list[float]:
    base = [0.001 if i % 2 == 0 else -0.001 for i in range(30)]
    return base + [0.06]


def test_pacote_src_importavel():
    assert importlib.import_module("src") is not None


def test_pipeline_explicacao():
    """Deteção -> explicação produz texto rastreável (sem rede)."""
    res = detect_latest(_serie_anomala(), window=20, threshold=3.0)
    texto = explain_anomaly("TEST", res)
    assert res.is_anomaly is True
    assert "Anomaly detected for TEST" in texto
    assert "z-score" in texto


@pytest.mark.telegram
def test_thin_slice_envia_telegram():
    """Envia um alerta real ao Telegram (requer .env). Pulado se não configurado."""
    from src import config
    from src.telegram_bot.sender import send_message

    if not config.telegram_ready():
        pytest.skip("Telegram não configurado no .env.")
    res = detect_latest(_serie_anomala(), window=20, threshold=3.0)
    texto = "[smoke test] " + explain_anomaly("TEST", res)
    resp = send_message(texto)
    assert resp.get("ok") is True
