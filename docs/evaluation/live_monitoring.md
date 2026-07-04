# live_monitoring.md — Pós-validação das decisões ao vivo (M5.5; reprodutível)

> Gerado por `scripts/post_validate.py` a partir de `data/predictions_log.jsonl`.
> **Não editar à mão.** O loop: o runner regista decisões → dias depois este script
> rotula-as com o resultado REAL (mesmo rótulo do treino) → métricas ao vivo → retreino.

- **Gerado:** 2026-07-04 15:00 UTC · rótulo |retorno anormal vs SPY em (d, d+3]| ≥ 0.02 (o primário do treino).
- **Decisões:** 3 registadas · 3 únicas · 0 maturadas · 3 ainda pendentes · 0 sem preços.

| Métrica ao vivo | Valor |
|---|---|
| Precisão das decisões mantidas | n/a (0 mantidas) |
| Base rate (todas as decisões maturadas) | n/a (0) |
| Brier das probabilidades | n/a |

**Retreino com os dados acumulados** (quando houver decisões maturadas suficientes):
`python scripts/build_dataset.py` → `python scripts/train_triage.py` (stack `--ml`;
os joblib novos substituem os de `models/` — reprodutível, mesma seed).

**Caveats honestos:** o log vive na máquina onde o runner corre — no cron do GitHub
Actions o runner é efémero, por isso o loop completo corre na máquina do aluno
(persistir o log na nuvem = Fase B, ver `docs/design/going_live.md`); decisões de
`--dry-run` também contam (são decisões, não envios); amostras pequenas ⇒ ler as
métricas como monitorização, não como avaliação (essa é `evaluation_triage.md`).
