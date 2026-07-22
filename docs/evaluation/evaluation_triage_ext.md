# evaluation_triage_ext.md — RQ4-ext: ablação de features de contexto (reprodutível)

> Gerado por `scripts/train_triage_ext.py`. **Não editar à mão.** Aditivo: os modelos
> e `evaluation_triage.md` congelados ficam intactos (ver `docs/evaluation/roadmap_rq4.md`).

- **Dataset:** `C:\Users\henri\Desktop\DIMEIA\data\triage_dataset_ext.csv` — treino 28562 / val 17988 / teste 32266 linhas (positivos: 39.0% / 47.0% / 37.6%).
- **Protocolo:** idêntico ao congelado — split temporal por dias únicos + embargo, calibração Platt na validação, seed=42, orçamento = 5/dia. Só features de contexto (sem texto/SBERT).
- **Gerado:** 2026-07-22 19:53 UTC.

## 1. Âncora e ablação principal

| Modelo | PR-AUC | ROC-AUC | Brier | Precisão@orçamento |
|---|---|---|---|---|
| Alertar-sempre (chão) | 0.376 | 0.500 | 0.624 | 0.161 |
| LR só-volatilidade (baseline) | 0.538 | 0.663 | 0.219 | 0.629 |
| LR contexto v1 (âncora) | 0.537 | 0.659 | 0.223 | 0.629 |
| LR contexto v1 + 5 features (RQ4-ext) | 0.535 | 0.661 | 0.223 | 0.630 |

O contexto v1 aqui (PR-AUC 0.537) reproduz a âncora congelada (`evaluation_triage.md`: 0.538) até ao ruído do split ligeiramente mais curto do build `--ext` (exige 60 dias de histórico, ~300 eventos iniciais a menos). Acrescentar os 5 sinais move a PR-AUC para 0.535 (Δ -0.002).

## 2. Contribuição marginal de cada sinal

- **leave-one-in (LOI):** contexto v1 + *só* esta feature — valor isolado sobre a v1.
- **leave-one-out (LOO):** contexto+5 *menos* esta feature — custo de a remover, dado o resto.

| Feature nova | LOI PR-AUC | Δ vs v1 | LOO Δ (custo de remover) |
|---|---|---|---|
| ret_event_z (reação padronizada) | 0.538 | +0.001 | +0.001 |
| market_vol20 (regime do mercado) | 0.537 | -0.000 | +0.000 |
| mom20 (momento 20d da ação) | 0.532 | -0.005 | -0.000 |
| vol_ratio (vol20/vol60) | 0.538 | +0.000 | -0.001 |
| downside_vol20 (risco de queda) | 0.534 | -0.003 | -0.001 |

![Contribuição marginal](../../thesis/figures/eval_triage_ext.pdf)

**Leitura honesta:** a ablação diz quais sinais valem e quais não — reportado tal como cai, com o mesmo rigor do resultado congelado ("o texto não bate a volatilidade"). Δ pequenos (~0.00) significam que o sinal é redundante face aos que já lá estão; Δ negativos que atrapalha (ruído). Nada aqui muda a produção — a stack leve continua na variante só-contexto congelada; isto é ciência de features para a tese e futuro.
