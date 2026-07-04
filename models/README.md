# models/ — modelos TREINADOS da triagem de materialidade (RQ4)

Artefactos treinados pelo aluno com `scripts/train_triage.py` (reprodutível: mesma seed ⇒ métricas
idênticas; verificado). Cada `.joblib` contém {modelo, calibrador Platt, nomes das features}; o
`.json` ao lado tem os metadados (janela de treino, seed, embedder, métricas de teste).

| Ficheiro | O quê |
|----------|-------|
| `triage_lr.joblib` | Regressão logística contexto+texto (principal, interpretável) |
| `triage_gbm.joblib` | HistGradientBoosting contexto+texto (comparação) |
| `triage_context_lr.joblib` | LR SÓ-CONTEXTO — a variante de PRODUÇÃO (stack leve, sem SBERT): é a que o runner de alertas e a app na nuvem pontuam (`src/triage/infer.py`) |

Retreinar: `python scripts/train_triage.py` (SBERT; precisa da stack `--ml`).
Resultados/tabela: `docs/evaluation/evaluation_triage.md`. Plano: `progress/ML_PLAN.md`.

> ⚠️ Estes modelos fazem **triagem** ("esta notícia merece alerta?") — nunca previsão de
> direção/preço. Os atuais foram treinados no corpus-fumo de 4 semanas; os finais virão do
> FNSPID 2018–2023 (M6).
