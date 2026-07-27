# evaluation_triage_uncertainty.md — Incerteza da triagem (RQ4; bootstrap por cluster)

> Gerado por `scripts/evaluate_triage_uncertainty.py` (ADITIVO; não altera os congelados).
> Responde à crítica: as PR-AUC da RQ4 vinham single-seed, a 3 casas, sem intervalos e com
> amostras correlacionadas. Aqui os modelos ficam fixos (train+val) e reamostram-se os
> CLUSTERS (ticker,dia) do teste com reposição (1000×), IC 95% percentil.

- **Teste:** 32649 linhas em 1951 clusters (ticker,dia); prevalência 0.378.
- **Gerado:** 2026-07-27 07:06 UTC · seed 42 · SBERT.

| Modelo | PR-AUC (ponto) | IC 95% (bootstrap) |
|---|---|---|
| Volatility-only LR | 0.542 | [0.492, 0.597] |
| Context-only LR | 0.538 | [0.487, 0.592] |
| Text-only LR | 0.439 | [0.406, 0.474] |
| Context+text LR | 0.496 | [0.453, 0.540] |
| Gradient boosting | 0.469 | [0.427, 0.517] |

## Diferenças emparelhadas (o que a comparação decisiva realmente suporta)

| Diferença | Δ médio | IC 95% | P(Δ>0) |
|---|---|---|---|
| vol−context | +0.0048 | [+0.0013, +0.0076] | 1.00 |
| vol−full | +0.0480 | [+0.0320, +0.0660] | 1.00 |
| context−full | +0.0432 | [+0.0269, +0.0610] | 1.00 |

**Leitura honesta:** as barras marginais (coluna IC 95%) são largas, por isso reportar as PR-AUC a 3 casas como pontos precisos não era defensável — o honesto é o par (ponto, IC). Mas o bootstrap é EMPARELHADO (mesma reamostragem para todas as famílias), e são as DIFERENÇAS que sustentam a comparação decisiva: `vol−full` (+0,048) e `context−full` (+0,043) são positivos com IC a excluir 0 e P(Δ>0)=1 — adicionar o bloco de texto PIORA de forma robusta (não é ruído de uma seed), pelo que o veredicto "o texto não acrescenta sobre o contexto de mercado" fica **estatisticamente sustentado, cluster-robusto**. `vol−context` é minúsculo (+0,005) mas consistente. Fica em aberto para o re-teste justo da RQ4 (fase D) se a degradação reflete "texto sem sinal" ou sub-ajuste do pipeline de texto (penalização não afinada; bloco 384-d a diluir 5 escalares).
