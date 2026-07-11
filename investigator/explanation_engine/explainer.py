"""Motor de explicação (XAI) — regra transparente + precedentes históricos.

Produz texto rastreável: o utilizador vê exatamente porque é que o alerta disparou.
- Gatilho 1 (anomalia): `explain_anomaly` / `explain_normal` (z-score, janela, média/desvio).
- Gatilho 2 (notícia): `explain_news_impact` — a notícia + precedentes históricos semelhantes
  (recuperados por similaridade) e o impacto que tiveram.

Formato (revisão UX 2026-07-06): mensagens em CAMADAS — o facto que interessa primeiro, a
lista a seguir, o método numa nota final curta. O Telegram renderiza em HTML (parse_mode no
sender), por isso o conteúdo dinâmico é escapado e os títulos levam <b>…</b>. TODOS os números
calculados continuam presentes (fidelidade XAI testada em tests/test_explainer.py).
"""

from __future__ import annotations

import html
from typing import TYPE_CHECKING

from investigator.anomaly_detector.detector import AnomalyResult

if TYPE_CHECKING:
    from investigator.historical_kb.record import NewsRecord

_MAX_HEADLINE = 100  # truncagem SÓ de apresentação (os objetos calculados ficam intactos)


def plain_text(alert: str) -> str:
    """Versão sem tags para consola/app (o Telegram recebe o HTML canónico)."""
    out = alert.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
    return html.unescape(out)


def _clip(text: str, limit: int = _MAX_HEADLINE) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def explain_anomaly(ticker: str, result: AnomalyResult) -> str:
    """Explicação de uma anomalia: o facto primeiro, o método numa nota curta no fim."""
    arrow = "🔺" if result.last_return >= 0 else "🔻"
    return (
        f"{arrow} <b>Anomaly detected for {html.escape(ticker, quote=False)}: "
        f"{result.last_return * 100:+.2f}% today</b>\n"
        f"About {abs(result.z_score):.1f}x this stock's typical daily swing "
        f"({result.window}-day norm).\n"
        f"<i>Method: z-score: {result.z_score:+.2f} vs threshold ±{result.threshold:g} — "
        f"{abs(result.z_score):.1f} standard deviations from the {result.window}d mean "
        f"({result.mean * 100:+.2f}%, std {result.std * 100:.2f}%). "
        f"An observed move, not advice.</i>"
    )


def explain_normal(ticker: str, result: AnomalyResult) -> str:
    """Mensagem quando não há anomalia (útil para testes/diagnóstico)."""
    return (
        f"No anomaly for {html.escape(ticker, quote=False)} today "
        f"(z-score {result.z_score:+.2f}, within ±{result.threshold:g})."
    )


def _impacts(precedents: list[tuple[NewsRecord, float]], horizon: int) -> list[float]:
    """Impactos não-NaN dos precedentes no horizonte, pela ordem recebida."""
    key = str(horizon)
    return [
        rec.impacts[key]
        for rec, _ in precedents
        if key in rec.impacts and rec.impacts[key] == rec.impacts[key]  # exclui NaN
    ]


def _mean_precedent_impact(precedents: list[tuple[NewsRecord, float]], horizon: int) -> float:
    """Impacto médio dos precedentes no horizonte (ignora NaN). NaN se não houver dados."""
    vals = _impacts(precedents, horizon)
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

    Camadas: a notícia; o resumo honesto dos precedentes (INTERVALO primeiro — a média sozinha
    esconde direções mistas — com a média entre parênteses); a lista, um por linha, com o
    resultado à cabeça; nota final curta. NÃO é uma previsão (restrição §5.2).

    `materiality` (opcional, off por defeito): linha da triagem aprendida (RQ4), já composta
    por `investigator.triage.explain.materiality_line`. None ⇒ sem essa linha.
    """
    header = f"📰 <b>News alert for {html.escape(ticker, quote=False)}</b>"
    if date:
        header += f" ({html.escape(date, quote=False)})"
    header += f'\n"{html.escape(_clip(headline), quote=False)}"'
    if not precedents:
        out = header + "\nNo similar historical precedents found in the knowledge base."
        return f"{out}\n{materiality}" if materiality else out

    vals = _impacts(precedents, horizon)
    avg = _mean_precedent_impact(precedents, horizon)
    if vals:
        resumo = (
            f"<b>{len(precedents)} similar past headlines</b> — their {horizon}-day moves "
            f"ranged {min(vals) * 100:+.2f}%…{max(vals) * 100:+.2f}% "
            f"(average {avg * 100:+.2f}%):"
        )
    else:
        resumo = (f"<b>{len(precedents)} similar past headlines</b> — "
                  f"average {horizon}-day move: n/a:")
    lines = [header, "", resumo]
    key = str(horizon)
    for rec, score in precedents:
        imp = rec.impacts.get(key)
        imp_txt = f"{imp * 100:+.2f}%" if imp is not None and imp == imp else "n/a"
        quem = f"{html.escape(rec.ticker, quote=False)} {html.escape(rec.date, quote=False)}"
        lines.append(
            f"▸ {imp_txt} in {horizon}d · {quem} · "
            f'"{html.escape(_clip(rec.headline), quote=False)}" (sim {score:.2f})'
        )
    # Aviso de direção mista (a lição do CS3 da tese, agora no produto): a semelhança capta
    # o TEMA, não a direção — quando os precedentes divergem em sinal, a média esconde
    # desacordo real e induz sobre-confiança. Dizemo-lo explicitamente.
    if vals and min(vals) < 0 < max(vals):
        lines.append(
            "⚠ Similar past cases moved in BOTH directions — treat the average with caution."
        )
    if materiality:
        lines.append(materiality)
    lines.append(
        "<i>Observed past outcomes after similar news — not a price prediction, "
        "not advice.</i>"
    )
    return "\n".join(lines)
