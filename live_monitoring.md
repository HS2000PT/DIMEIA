# live_monitoring.md — Pós-validação das decisões ao vivo (M5.5; reprodutível)

> Gerado por `scripts/post_validate.py` a partir de `predictions_log.jsonl`.
> **Não editar à mão.** O loop: o runner regista decisões → dias depois este script
> rotula-as com o resultado REAL (mesmo rótulo do treino) → métricas ao vivo → retreino.

- **Gerado:** 2026-07-30 21:15 UTC · rótulo |retorno anormal vs SPY em (d, d+3]| ≥ 0.02 (o primário do treino).
- **Decisões:** 518 registadas · 352 únicas · 195 maturadas · 157 ainda pendentes · 0 sem preços.

| Métrica ao vivo | Valor |
|---|---|
| Precisão das decisões mantidas | 0.812 (64 mantidas) |
| Base rate (todas as decisões maturadas) | 0.667 (195) |
| Brier das probabilidades | 0.246 |

Calibração (previsto vs observado):

| P prevista (média) | Fração observada | n |
|---|---|---|
| 0.25 | 0.18 | 17 |
| 0.49 | 0.71 | 178 |

**Retreino com os dados acumulados** (quando houver decisões maturadas suficientes):
`python scripts/build_dataset.py` → `python scripts/train_triage.py` (stack `--ml`;
os joblib novos substituem os de `models/` — reprodutível, mesma seed).

**Notas honestas:** o log de decisões é PERSISTIDO na branch partilhada `alerts-history`
(`predictions_log.jsonl`), por isso o loop acumula na nuvem e este relatório é regenerado
ao fecho pelo workflow do Actions (preços via cadeia de fallback). Decisões de `--dry-run` também contam (são decisões, não envios); amostras pequenas ⇒ ler como
monitorização, não como avaliação (essa é `evaluation_triage.md`).
