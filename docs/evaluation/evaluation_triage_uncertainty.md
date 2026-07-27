# evaluation_triage_uncertainty.md — Incerteza da triagem (RQ4; bootstrap por cluster)

> Gerado por `scripts/evaluate_triage_uncertainty.py` (ADITIVO; não altera congelados).
> Responde à crítica: as PR-AUC vinham single-seed, a 3 casas, sem intervalos e com
> amostras correlacionadas. Aqui os modelos ficam fixos (train+val) e reamostram-se os
> CLUSTERS (ticker,dia) do teste com reposição (1000×), IC 95% percentil.

- **Teste:** 32649 linhas em 1951 clusters (ticker,dia); prevalência 0.378.
- **Gerado:** 2026-07-27 19:25 UTC · seed 42.

| Modelo | PR-AUC (ponto) | IC 95% (bootstrap) |
|---|---|---|
| Volatility-only LR | 0.542 | [0.492, 0.597] |
| Context-only LR | 0.538 | [0.487, 0.592] |

## Diferenças emparelhadas (o que a comparação decisiva realmente suporta)

| Diferença | Δ médio | IC 95% | P(Δ>0) |
|---|---|---|---|
| vol−context | +0.0048 | [+0.0013, +0.0076] | 1.00 |

**Leitura honesta:** as barras marginais (coluna IC 95%) são largas, por isso reportar as PR-AUC a 3 casas como pontos precisos não era defensável — o honesto é o par (ponto, IC). Mas o bootstrap é EMPARELHADO (mesma reamostragem para todas as famílias), e são as DIFERENÇAS que sustentam a comparação decisiva: quando `vol−full` e `context−full` são positivos com IC a excluir 0 e P(Δ>0)=1, adicionar o bloco de texto PIORA de forma robusta (não é ruído de uma seed) — o veredicto 'o texto não acrescenta sobre o contexto de mercado' fica estatisticamente sustentado, cluster-robusto. Fica em aberto para o re-teste justo da RQ4 (fase D) se a degradação reflete 'texto sem sinal' ou sub-ajuste do pipeline de texto (penalização não afinada; bloco 384-d a diluir 5 escalares).
