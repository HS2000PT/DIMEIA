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
    """Linha honesta para o alerta: probabilidade + principais fatores. Nunca é previsão."""
    factors = ", ".join(
        f"{name} ({'+' if c >= 0 else '-'})" for name, c in contributions[:top]
    )
    return (
        f"Materiality (learned triage): {prob:.0%} of historically similar cases were followed "
        f"by an abnormal move. Top factors: {factors}. Triage evidence, not a forecast."
    )
