# evaluation_triage_uncertainty.md — Incerteza da triagem (RQ4; bootstrap por cluster)

> Gerado por `scripts/evaluate_triage_uncertainty.py` (ADITIVO; não altera os congelados).
> Responde à crítica: as PR-AUC da RQ4 vinham single-seed, a 3 casas, sem intervalos e com
> amostras correlacionadas. Aqui os modelos ficam fixos (train+val) e reamostram-se os
> CLUSTERS (ticker,dia) do teste com reposição (1000×), IC 95% percentil.

- **Teste:** 32649 linhas em 1951 clusters (ticker,dia); prevalência 0.378.
- **Gerado:** 2026-07-27 06:58 UTC · seed 42.

| Modelo | PR-AUC (ponto) | IC 95% (bootstrap) |
|---|---|---|
| Volatility-only LR | 0.542 | [0.492, 0.597] |
| Context-only LR | 0.538 | [0.487, 0.592] |

## Diferenças emparelhadas (o que a comparação decisiva realmente suporta)

| Diferença | Δ médio | IC 95% | P(Δ>0) |
|---|---|---|---|
| vol−context | +0.0048 | [+0.0013, +0.0076] | 1.00 |

**Leitura honesta:** se o IC de `vol−context` contém 0, então volatilidade e contexto são **estatisticamente indistinguíveis** — a ordenação a 3 casas não era defensável, mas o veredicto qualitativo (o texto não acrescenta) mantém-se se `vol−full` e `context−full` ficarem ≥0 com P(Δ>0) alto. Reportado tal como cai.
