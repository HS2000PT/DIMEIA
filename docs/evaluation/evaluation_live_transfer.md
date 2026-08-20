# evaluation_live_transfer.md — o modelo transfere para a população implantada?

> Gerado por `scripts/evaluate_live_transfer.py` a 2026-08-20 15:45 UTC.
> **Não editar à mão.** Semente fixa; re-correr sobre o mesmo log reproduz.

- Decisões maturadas: **825** linhas em **239** pares (ticker, dia) · rótulo |retorno anormal vs SPY em (d, d+3]| ≥ 0.02
- Prevalência ao vivo: **0.602** (treino: 0.378)

⚠️ O rótulo é por (ticker, dia), pelo que as linhas vêm em grupos e a amostra efectiva
é de 239 unidades e não de 825. O IC abaixo vem de bootstrap **de cluster**;
um bootstrap sobre linhas daria um intervalo mais estreito e enganador.

## 1. Discriminação — o score ordena?

| métrica | valor | chão |
|---|---|---|
| ROC-AUC | **0.486** (IC 95% de cluster [0.403, 0.571]) | 0.500 |
| PR-AUC | 0.588 | 0.602 (prevalência) |

## 2. Calibração — os números estão na escala certa?

| métrica | valor |
|---|---|
| Brier, probabilidades tal como enviadas | **0.2551** |
| Brier, recalibrado ao vivo (Platt, CV 5 folds) | **0.2388** |
| ganho da recalibração | +0.0164 |

Fiabilidade por quintis (previsto vs observado):

| p previsto (média) | fração observada | n |
|---|---|---|
| 0.349 | 0.533 | 165 |
| 0.451 | 0.691 | 165 |
| 0.495 | 0.661 | 165 |
| 0.548 | 0.600 | 165 |
| 0.594 | 0.527 | 165 |

## 3. O que o gate fez

| conjunto | materiais | n | IC 95% |
|---|---|---|---|
| mantidos (p ≥ 0.5) | 0.589 | 436 | [0.543, 0.635] |
| suprimidos (p < 0.5) | 0.617 | 389 | [0.568, 0.664] |

