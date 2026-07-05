"""Motor de explicação (XAI) — regra transparente + precedentes históricos.

Produz texto rastreável: o utilizador vê exatamente porque é que o alerta disparou.
- Gatilho 1 (anomalia): `explain_anomaly` / `explain_normal` (z-score, janela, média/desvio).
- Gatilho 2 (notícia): `explain_news_impact` — a notícia + precedentes históricos semelhantes
  (recuperados por similaridade) e o impacto que tiveram. (Opcional futuro: atribuição SHAP.)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from investigator.anomaly_detector.detector import AnomalyResult

if TYPE_CHECKING:
    from investigator.historical_kb.record import NewsRecord


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
        f"std {result.std * 100:.2f}%).\n"
        f"In plain terms: about {abs(result.z_score):.1f}x this stock's typical daily swing, "
        f"well beyond ordinary day-to-day volatility."
    )


def explain_normal(ticker: str, result: AnomalyResult) -> str:
    """Mensagem quando não há anomalia (útil para testes/diagnóstico)."""
    return (
        f"No anomaly for {ticker} today "
        f"(z-score {result.z_score:+.2f}, within ±{result.threshold:g})."
    )


def _mean_precedent_impact(precedents: list[tuple[NewsRecord, float]], horizon: int) -> float:
    """Impacto médio dos precedentes no horizonte (ignora NaN). NaN se não houver dados."""
    key = str(horizon)
    vals = [
        rec.impacts[key]
        for rec, _ in precedents
        if key in rec.impacts and rec.impacts[key] == rec.impacts[key]  # exclui NaN
    ]
    return sum(vals) / len(vals) if vals else float("nan")


def explain_news_impact(
    ticker: str,
    headline: str,
    precedents: list[tuple[NewsRecord, float]],
    horizon: int = 3,
    date: str = "",
    materiality: str | None = None,
) -> str:
    """Explicação XAI para o Gatilho 2: notícia nova + precedentes históricos semelhantes.

    Mostra a notícia, o impacto médio observado em eventos passados análogos e a lista de
    precedentes (data, ticker, similaridade, impacto e título), tudo rastreável. NÃO é uma
    previsão de preço — é o resultado OBSERVADO no passado (restrição §5.2).

    `materiality` (opcional, off por defeito): linha da triagem aprendida (RQ4), já composta
    por `investigator.triage.explain.materiality_line`. None ⇒ saída exatamente igual à de sempre.
    """
    header = f"📰 News alert for {ticker}\n\"{headline}\""
    if date:
        header += f" ({date})"
    if not precedents:
        out = header + "\nNo similar historical precedents found in the knowledge base."
        return f"{out}\n{materiality}" if materiality else out

    avg = _mean_precedent_impact(precedents, horizon)
    avg_line = (
        f"average {horizon}-day move: {avg * 100:+.2f}%"
        if avg == avg  # not NaN
        else f"average {horizon}-day move: n/a"
    )
    lines = [
        header,
        f"Potential impact (from {len(precedents)} similar past events): {avg_line}",
    ]
    if materiality:
        lines.append(materiality)
    lines.append("Historical precedents:")
    key = str(horizon)
    for rec, score in precedents:
        imp = rec.impacts.get(key)
        imp_txt = f"{imp * 100:+.2f}%" if imp is not None and imp == imp else "n/a"
        lines.append(
            f"  • {rec.date} {rec.ticker} (sim {score:.2f}) "
            f"→ {horizon}d {imp_txt}: \"{rec.headline}\""
        )
    lines.append(
        "Note: precedents are retrieved by semantic similarity; the impact is the observed "
        "past outcome, not a price prediction."
    )
    return "\n".join(lines)
