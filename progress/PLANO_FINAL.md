# PLANO FINAL — as 4 frentes pós-ML (P1–P4)

> **Origem:** pedido do aluno (2026-07-05), após o fecho do workstream ML (M0–M7): fazer TUDO —
> polimento da escrita da tese, rename `src/`→`investigator/`, KB FNSPID multi-ano e S-APP (Fase B) —
> pela ordem que fizer mais sentido. Este ficheiro é o checkpoint multi-dispositivo (como o
> `ML_PLAN.md` foi para o ML): qualquer sessão futura retoma daqui + `CLAUDE.md` + `CHECKLIST.md`.

## Ordem escolhida (racional)

| # | Frente | Porquê nesta posição |
|---|--------|----------------------|
| **P1** | **Polimento da escrita da tese** | É o artefacto avaliado. As secções novas da RQ4 (M7) foram escritas numa maratona e nunca receberam o passe editorial das Sessões 23–24. Zero risco técnico; valor máximo. |
| **P2** | **Rename `src/`→`investigator/`** | Fazê-lo ANTES de escrever código novo (P3/P4) evita criar ainda mais referências a `src/` para migrar. Tese/paper não referem `src/` (verificado na Sessão 27) → não afeta o P1. |
| **P3** | **KB FNSPID multi-ano** | O corpus 2018–2023 já está no disco (`data/fnspid_news_subset.csv`, provado pelo estudo de triagem). A KB nova nasce já no layout novo do P2. Alimenta o P4 (precedentes mais ricos na app/bot). |
| **P4** | **S-APP — Fase B (Telegram/app)** | A maior frente e a única explicitamente pós-submissão. Beneficia de tudo o que vem antes (pacote limpo, KB rica). Desenho já existe em `docs/design/going_live.md` (Fase B). |

## Estado

### P1 — Polimento da escrita da tese
- [x] Diagnóstico: travessões-conectores em prosa = **0** (só 2 comentários TikZ + 1 célula de tabela
      aceite); tiques clássicos de IA = **0**. O trabalho é nas secções novas da RQ4.
- [ ] Passe editorial às secções RQ4: Ch2 §triage, Ch3 §met_triage + §protocolo, Ch4 §learned severity,
      Ch5 CS4, Ch6 (RQ4/contribuições), Ch1/abstract (frases longas partidas, ecos de palavras
      removidos, voz natural). **Regra: nenhum número, citação, equação, tabela ou figura muda.**
- [ ] Passe rápido de coerência ao resto (grep de tiques, EN-GB, consistência de rótulos).
- [ ] Recompilar: 0 erros, 0 citações indefinidas, overfull ≤15pt, abstract ≤200 palavras. Commit.

### P2 — Rename `src/` → `investigator/`
- [ ] Pacote instalável (`pyproject.toml` ou pelo menos layout de pacote); remover os hacks `sys.path`.
- [ ] Migrar imports em `src/`, `scripts/`, `tests/`, `app/`; CI e `.vscode/` e `run/*.bat` atualizados.
- [ ] Sync de docs internos que citam `src/…`: CLAUDE.md (inventário), caderno de defesa, learning.md,
      glossary.md, guia de estudo (frames P5 com caminhos), README (layout), how_to_run.
- [ ] Gates: 93 testes + ruff verdes; AppTest verde; demo reproduz +6,46%; CI verde no push; deploy
      Streamlit continua a funcionar (entrypoint `app/streamlit_app.py` não muda de caminho).

### P3 — KB FNSPID multi-ano (retrieval)
- [ ] `scripts/build_kb.py --sbert` sobre `data/fnspid_news_subset.csv` (stack ML local; KB local
      gitignored — grande demais para versionar; amostra curada pequena para `data/samples/` se útil).
- [ ] Validação honesta: cobertura por ticker/ano, sanidade de impactos, 3 consultas de exemplo.
- [ ] Decidir o que usa a KB nova (demo local/app local) SEM tocar nos números congelados da tese;
      docs atualizados (data card já diz que o rebuild da KB de retrieval é trabalho futuro → passa a
      "feito como artefacto de produto, avaliação de retrieval multi-ano continua futuro" se for o caso).
- [ ] Gate: números da tese intocados; testes verdes.

### P4 — S-APP — Fase B (Telegram interativo + app UX)
- [ ] Desenho fino a partir de `going_live.md` Fase B: `/start`, `/watch`, `/unwatch`, `/list`,
      utilizadores em SQLite, webhook vs polling, host grátis (Student Pack) — decidir o mínimo defensável.
- [ ] Implementação incremental com testes; segredos só em `.env`/Actions.
- [ ] UX da app (Streamlit): melhorias da lista de polimento que fizerem sentido.
- [ ] Runbook atualizado; CHECKLIST com os cliques humanos.

## Guardrails (herdados, sempre em vigor)
Zero fabricação; números validados nunca editados à mão; sem previsão de preço/direção; só compute
grátis; segredos nunca em ficheiros versionados; commits PT-PT com
`Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`; sem force-push; CLAUDE.md atualizado no fim
de cada sessão.
