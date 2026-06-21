"""Motor de explicação (XAI) — versão mínima da thin slice (baseada em regra transparente).

Produz texto rastreável: o utilizador vê exatamente porque é que o alerta disparou.
Versões futuras juntam precedentes históricos e (opcional) atribuição SHAP.
"""

from __future__ import annotations

from src.anomaly_detector.detector import AnomalyResult


def explain_anomaly(ticker: str, result: AnomalyResult) -> str:
    """Constrói a explicação textual de uma anomalia detetada."""
    direction = "up" if result.last_return >= 0 else "down"
    return (
        f"⚠️ Anomaly detected for {ticker}\n"
        f"Today's move: {result.last_return * 100:+.2f}% ({direction})\n"
        f"z-score: {result.z_score:+.2f} "
        f"(threshold ±{result.threshold:g}, window {result.window}d)\n"
        f"Why: the return is {abs(result.z_score):.1f} standard deviations from the "
        f"{result.window}-day norm (mean {result.mean * 100:+.2f}%, "
        f"std {result.std * 100:.2f}%)."
    )


def explain_normal(ticker: str, result: AnomalyResult) -> str:
    """Mensagem quando não há anomalia (útil para testes/diagnóstico)."""
    return (
        f"No anomaly for {ticker} today "
        f"(z-score {result.z_score:+.2f}, within ±{result.threshold:g})."
    )
