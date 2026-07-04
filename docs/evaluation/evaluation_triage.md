# evaluation_triage.md — Triagem de materialidade (RQ4; reprodutível)

> Gerado por `scripts/train_triage.py`. **Não editar à mão.**
> SMOKE — corpus Finnhub de 4 semanas (embargo 1); números finais virão do FNSPID (M6).

- **Dataset:** `C:\Users\henri\Desktop\DIMEIA\data\triage_dataset.csv` — treino 990 / val 333 / teste 1515 linhas (positivos: 67.8% / 49.2% / 37.2%).
- **Protocolo:** split temporal por dias únicos + embargo; calibração Platt na validação; seed=42, embedder=sbert; orçamento de alertas = 5/dia.
- **Gerado:** 2026-07-04 10:52 UTC.

| Modelo | PR-AUC | ROC-AUC | Brier | Precisão@orçamento |
|---|---|---|---|---|
| Alertar-sempre (chão) | 0.372 | 0.500 | 0.628 | 1.000 |
| LR só-volatilidade (baseline) | 0.445 | 0.425 | 0.244 | 0.000 |
| LR só-contexto | 0.447 | 0.473 | 0.230 | 0.000 |
| LR só-texto | 0.379 | 0.527 | 0.248 | 0.300 |
| LR contexto+texto (principal) | 0.357 | 0.489 | 0.247 | 0.200 |
| Gradient boosting (contexto+texto) | 0.461 | 0.500 | 0.225 | 0.500 |

**Leitura honesta:** a comparação decisiva é `full` (e `gbm`) vs `vol` — se o modelo aprendido não superar a baseline de volatilidade, isso é reportado como está. PR-AUC do alertar-sempre = prevalência do teste (chão).

**Caveats:** rótulo = |retorno anormal vs SPY| ≥ τ no horizonte primário (proxy de materialidade, não julgamento humano); títulos do mesmo (ticker, dia) partilham o rótulo (clustering — split por dias únicos mitiga fuga, não a correlação); corpus recente curto ⇒ possível desvio de regime entre blocos (ver positivos por split).
