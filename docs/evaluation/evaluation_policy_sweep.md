# evaluation_policy_sweep.md — Varrimento de política do gate de materialidade (RQ4)

> Gerado por `scripts/evaluate_policy_sweep.py` (ADITIVO — não altera congelados).
> Dataset: `triage_dataset.csv` · teste 32649 linhas · prevalência 37.8%
> Gerado: 2026-07-29 00:19 UTC

## Porquê

`config/alerts.yaml` traz `min_materiality: 0.5` — uma constante posta à
mão por cima de um modelo **calibrado por Platt**. A calibração existe precisamente
para permitir escolher um limiar segundo um custo declarado, e o projeto nunca a usou
para isso. Este documento substitui a constante por um ponto de operação derivado.

## Reprodução dos pontos congelados (sanidade)

| Família | PR-AUC aqui | Congelado | Δ |
|---|---|---|---|
| vol | 0.542 | 0.542 | +0.000 |
| context | 0.538 | 0.538 | +0.000 |

## 1. Ponto de operação por rácio de custo

R = custo(perder um movimento real) ÷ custo(um falso alarme). Nenhum valor é *o*
certo; o ponto é declarar qual se assume, em vez de o esconder num número.

| R | τ* | Precisão | Recall | Alertas/dia |
|---|---|---|---|---|
| 0.5 | 0.64 | 0.835 | 0.036 | 2.4 |
| 1.0 | 0.49 | 0.606 | 0.301 | 27.8 |
| 2.0 | 0.41 | 0.467 | 0.723 | 86.6 |
| 3.0 | 0.38 | 0.414 | 0.889 | 120.0 |
| 5.0 | 0.25 | 0.382 | 0.993 | 145.1 |
| 10.0 | 0.05 | 0.378 | 1.000 | 147.7 |

## 2. O que o τ=0.5 implantado assume, sem o dizer

- Precisão 0.605 · recall 0.273 · 25.2 alertas/dia.
- **Rácio de custo implícito ≈ 0.9**: ao fixar 0,5, o sistema estava a
  assumir que perder um movimento real custa ~0.9× incomodar o
  utilizador com um falso alarme. Passa a ser uma suposição declarada e discutível.

## 3. Aprendido vs volatilidade com o MESMO orçamento de alertas

A tese reporta honestamente que nenhum modelo com texto bate a baseline de
volatilidade em PR-AUC. Mas PR-AUC integra sobre limiares que o produto nunca usa: o
utilizador tem um orçamento diário de atenção. À conta certa — mesmo número de
alertas por dia — a pergunta é qual política acerta mais.

| Orçamento (top-k/dia) | Contexto | Volatilidade | Δ | Base rate |
|---|---|---|---|---|
| top-1 | 0.633 | 0.633 | +0.000 | 0.378 |
| top-2 | 0.577 | 0.572 | +0.005 | 0.378 |
| top-3 | 0.504 | 0.504 | +0.000 | 0.378 |
| top-5 | 0.434 | 0.450 | -0.015 | 0.378 |

**Veredicto, tal como caiu.** O score aprendido não ganha de forma consistente: vence em 0 orçamento(s), perde em 1, e empata nos restantes, sempre por margens ≤0,02. O reenquadramento por política **não** salva a hipótese do texto — apenas mostra que a conclusão negativa da RQ4 se mantém quando se troca o PR-AUC por uma métrica operacional. Reportado como caiu.

> **Nota metodológica (um erro apanhado a meio).** A primeira versão ordenava
> MANCHETES e dava Δ=+0,000 em todos os orçamentos. O rótulo é por (ticker, dia), por
> isso todas as manchetes do mesmo ticker no mesmo dia partilham rótulo e o top-k
> enchia-se de cópias do mesmo nome: a métrica media a contagem de manchetes do ticker
> mais volátil, não a decisão do produto. Agregar a (ticker, dia) antes de ordenar
> corrige a unidade de análise — e os empates perfeitos desapareceram, confirmando que
> eram artefacto.

> **Nota de âmbito.** Os alertas/dia desta tabela referem-se APENAS ao gate de
> materialidade sobre o corpus de avaliação. Em produção passam ainda pelo chão de
> similaridade, pelo teto por ticker/dia e pelo dedup, por isso o canal real envia
> muito menos (ver `docs/evaluation/alert_funnel.md`).

## Varrimento completo

| τ | Alertas/dia | Precisão | Recall | F1 |
|---|---|---|---|---|
| 0.05 | 147.7 | 0.378 | 1.000 | 0.549 |
| 0.10 | 147.7 | 0.378 | 1.000 | 0.549 |
| 0.15 | 147.7 | 0.378 | 1.000 | 0.549 |
| 0.20 | 147.7 | 0.378 | 1.000 | 0.549 |
| 0.25 | 145.1 | 0.382 | 0.993 | 0.552 |
| 0.30 | 135.4 | 0.392 | 0.950 | 0.555 |
| 0.35 | 134.4 | 0.393 | 0.945 | 0.555 |
| 0.40 | 97.6 | 0.444 | 0.775 | 0.564 |
| 0.45 | 49.2 | 0.547 | 0.482 | 0.513 |
| 0.50 | 25.2 | 0.605 | 0.273 | 0.377 |
| 0.55 | 9.1 | 0.665 | 0.108 | 0.186 |
| 0.60 | 4.2 | 0.703 | 0.053 | 0.099 |
| 0.65 | 1.0 | 0.777 | 0.014 | 0.028 |
| 0.70 | 0.0 | nan | 0.000 | nan |
| 0.75 | 0.0 | nan | 0.000 | nan |
| 0.80 | 0.0 | nan | 0.000 | nan |
| 0.85 | 0.0 | nan | 0.000 | nan |
| 0.90 | 0.0 | nan | 0.000 | nan |
| 0.95 | 0.0 | nan | 0.000 | nan |
