# evaluation_live_transfer.md — o modelo transfere para a população implantada?

> Gerado por `scripts/evaluate_live_transfer.py` a 2026-08-09 19:47 UTC.
> **Não editar à mão.** Semente fixa; re-correr sobre o mesmo log reproduz.

- Decisões maturadas: **530** linhas em **145** pares (ticker, dia) · rótulo |retorno anormal vs SPY em (d, d+3]| ≥ 0.02
- Prevalência ao vivo: **0.626** (treino: 0.378)

⚠️ O rótulo é por (ticker, dia), pelo que as linhas vêm em grupos e a amostra efectiva
é de 145 unidades e não de 530. O IC abaixo vem de bootstrap **de cluster**;
um bootstrap sobre linhas daria um intervalo mais estreito e enganador.

## 1. Discriminação — o score ordena?

| métrica | valor | chão |
|---|---|---|
| ROC-AUC | **0.494** (IC 95% de cluster [0.391, 0.601]) | 0.500 |
| PR-AUC | 0.585 | 0.626 (prevalência) |

## 2. Calibração — os números estão na escala certa?

| métrica | valor |
|---|---|
| Brier, probabilidades tal como enviadas | **0.2598** |
| Brier, recalibrado ao vivo (Platt, CV 5 folds) | **0.2340** |
| ganho da recalibração | +0.0258 |

Fiabilidade por quintis (previsto vs observado):

| p previsto (média) | fração observada | n |
|---|---|---|
| 0.350 | 0.500 | 106 |
| 0.437 | 0.774 | 106 |
| 0.476 | 0.632 | 106 |
| 0.535 | 0.717 | 106 |
| 0.590 | 0.509 | 106 |

## 3. O que o gate fez

| conjunto | materiais | n | IC 95% |
|---|---|---|---|
| mantidos (p ≥ 0.5) | 0.592 | 201 | [0.523, 0.658] |
| suprimidos (p < 0.5) | 0.647 | 329 | [0.594, 0.697] |

