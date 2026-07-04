# evaluation_triage.md — Triagem de materialidade (RQ4; reprodutível)

> Gerado por `scripts/train_triage.py`. **Não editar à mão.**
> FNSPID 2018-2023 (M6)

- **Dataset:** `C:\Users\henri\Desktop\DIMEIA\data\triage_dataset.csv` — treino 28574 / val 17710 / teste 32649 linhas (positivos: 38.5% / 47.0% / 37.8%).
- **Protocolo:** split temporal por dias únicos + embargo; calibração Platt na validação; seed=42, embedder=sbert; orçamento de alertas = 5/dia.
- **Gerado:** 2026-07-04 23:36 UTC.

| Modelo | PR-AUC | ROC-AUC | Brier | Precisão@orçamento |
|---|---|---|---|---|
| Alertar-sempre (chão) | 0.378 | 0.500 | 0.622 | 0.163 |
| LR só-volatilidade (baseline) | 0.542 | 0.665 | 0.218 | 0.632 |
| LR só-contexto | 0.538 | 0.658 | 0.224 | 0.632 |
| LR só-texto | 0.439 | 0.564 | 0.240 | 0.572 |
| LR contexto+texto (principal) | 0.496 | 0.622 | 0.229 | 0.585 |
| Gradient boosting (contexto+texto) | 0.469 | 0.624 | 0.228 | 0.551 |

**Leitura honesta:** a comparação decisiva é `full` (e `gbm`) vs `vol` — se o modelo aprendido não superar a baseline de volatilidade, isso é reportado como está. PR-AUC do alertar-sempre = prevalência do teste (chão).

**Caveats:** rótulo = |retorno anormal vs SPY| ≥ τ no horizonte primário (proxy de materialidade, não julgamento humano); títulos do mesmo (ticker, dia) partilham o rótulo (clustering — split por dias únicos mitiga fuga, não a correlação); corpus recente curto ⇒ possível desvio de regime entre blocos (ver positivos por split).
