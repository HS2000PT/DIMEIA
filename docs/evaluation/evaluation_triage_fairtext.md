# evaluation_triage_fairtext.md — Re-teste justo da hipótese de texto (RQ4; fase D)

> Gerado por `scripts/evaluate_triage_fairtext.py` (ADITIVO). Dá ao texto o teste mais justo
> possível — C afinado na validação, bloco de texto reduzido por PCA (não esmaga os
> escalares), e opcionalmente o encoder de domínio FinBERT — para separar 'texto sem sinal'
> de 'sub-ajuste'. Seleção de modelo só na VALIDAÇÃO; teste tocado uma vez.

- **Dataset:** 78933 linhas · seleção por PR-AUC na validação · grelha C = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0].
- **Gerado:** 2026-07-27 07:55 UTC.
- **Congelados (C=1, sem afinação):** vol 0.542 · context 0.538 · full 0.496.

| Configuração | C* | PR-AUC (val) | PR-AUC (teste) |
|---|---|---|---|
| Volatility-only (tuned) | C=0.01 | 0.620 | 0.542 |
| Context-only (tuned) | C=10.0 | 0.613 | 0.538 |
| Context+text MiniLM 384d (tuned) | C=0.01 | 0.596 | 0.499 |
| Context+text MiniLM PCA-16 (tuned) | C=10.0 | 0.617 | 0.533 |
| Context+text MiniLM PCA-32 (tuned) | C=10.0 | 0.616 | 0.533 |
| Context+text MiniLM PCA-64 (tuned) | C=10.0 | 0.610 | 0.523 |
| Context+text FinBERT (tuned) | C=0.01 | 0.580 | 0.483 |
| Context+text FinBERT PCA-32 (tuned) | C=10.0 | 0.611 | 0.527 |

**Veredicto (reportado tal como cai):** com o C afinado, o bloco de texto reduzido por PCA e o encoder de domínio FinBERT, **o texto NÃO supera a volatilidade**.

**Nuance honesta (o arguente tinha razão num ponto):** o texto cru de 384 dims (afinado) dá 0.499, mas reduzi-lo por PCA recupera até **0.533** ('Context+text MiniLM PCA-16 (tuned)') — ou seja, o número congelado (full 0,496) estava EM PARTE deprimido por dimensionalidade (384 dims a diluir 5 escalares de contexto). MAS mesmo o melhor texto justo (0.533) não supera a volatilidade (0.542) nem o contexto (0.538): o texto recupera até ao nível do contexto, nunca acima. Sob um teste JUSTO e afinado, o veredicto da RQ4 — o sinal de materialidade de curto prazo vive no contexto de mercado, não na manchete — passa de 'plausivelmente sub-ajustado' a **robusto**. Reportam-se TODAS as configurações, incluindo as que recuperam.
