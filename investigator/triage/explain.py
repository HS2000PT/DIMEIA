"""Explicação dos scores de triagem (XAI): decomposição aditiva da regressão logística.

Para a LR com StandardScaler, o logit é  b0 + Σ coef_i · x_scaled_i  — uma soma exata, sem
aproximações. Agrupamos as centenas de dimensões do embedding numa só contribuição "headline
content" para a explicação ficar legível; as features de contexto aparecem individualmente.
"""

from __future__ import annotations

import numpy as np

# Nomes legíveis das features de contexto (a ordem vem de features.CONTEXT_COLS + setores).
_FRIENDLY = {
    "vol20": "recent volatility (20d)",
    "mom5": "recent momentum (5d)",
    "ret_event": "today's own move",
    "headline_len": "headline length",
}


def lr_group_contributions(pipeline, x_row: np.ndarray,
                           feature_names: list[str]) -> list[tuple[str, float]]:
    """Contribuições aditivas ao logit, por grupo, ordenadas por |contribuição| decrescente.

    Grupos: cada feature de contexto individualmente; todas as `emb_*` somadas em
    "headline content"; todos os `sector_*` somados em "sector".
    """
    scaler = pipeline.named_steps["scale"]
    lr = pipeline.named_steps["lr"]
    x_scaled = scaler.transform(np.asarray(x_row, dtype="float64").reshape(1, -1))[0]
    contribs = lr.coef_[0] * x_scaled

    grouped: dict[str, float] = {}
    for name, c in zip(feature_names, contribs, strict=True):
        if name.startswith("emb_"):
            key = "headline content"
        elif name.startswith("sector_"):
            key = "sector"
        else:
            key = _FRIENDLY.get(name, name)
        grouped[key] = grouped.get(key, 0.0) + float(c)
    return sorted(grouped.items(), key=lambda kv: -abs(kv[1]))


def materiality_line(prob: float, contributions: list[tuple[str, float]], top: int = 2) -> str:
    """Linha honesta para o alerta: risco em linguagem simples + porquê.

    Revisão UX (2026-07-08): a versão anterior ("Top factors: sector (+)") era jargão
    ilegível para um leigo. Agora separa-se em "sobe o risco" / "desce o risco" com os
    nomes das features já amigáveis (ver `_FRIENDLY`); sem fatores fortes, di-lo.

    ⚠️ Revisão de honestidade (2026-08-09): a versão anterior terminava em *"not a
    forecast"*, e isso era **falso**. Uma probabilidade sobre os próximos dias é, por
    definição, uma afirmação sobre o futuro — o próprio `dashboard_acceptance.md`
    classifica este número como violação do critério H2 ("é um número para a frente") e
    por isso ele está banido de todas as vistas do painel. Dizer "não é previsão" no
    canal e bani-lo do ecrã por ser previsão é incoerente, e um arguente encontra-o.

    A distinção que **é** verdadeira, e é a que o rótulo de treino sustenta, é entre
    **materialidade** e **direção**: o modelo estima se o mercado reage de forma
    anormalmente grande, nunca para que lado. A linha passa a dizer exactamente isso.
    """
    ups = [name for name, c in contributions if c > 0][:top]
    downs = [name for name, c in contributions if c < 0][:top]
    bits = []
    if ups:
        bits.append("raised by " + " and ".join(ups))
    if downs:
        bits.append("lowered by " + " and ".join(downs))
    why = "; ".join(bits) if bits else "no single factor dominates"
    return (
        f"Materiality estimate (learned triage): {prob:.0%} chance of an unusually large move "
        f"over the next few days, in EITHER direction — {why}. This estimates whether the market "
        f"reacts, never which way: it is not a price forecast and not advice."
    )
