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
- [x] Passe editorial às secções RQ4: Ch2 §triage, Ch3 §met_triage + §protocolo, Ch4 §learned severity,
      Ch5 CS4, Ch6 (RQ4/contribuições), Ch1/abstract (frases longas partidas, ecos de palavras
      removidos, voz natural). **Regra: nenhum número, citação, equação, tabela ou figura muda.**
- [x] Passe rápido de coerência ao resto (grep de tiques, EN-GB, consistência de rótulos).
- [x] Recompilar: 0 erros, 0 citações indefinidas, overfull ≤15pt, abstract ≤200 palavras.
      Commit `5c4c099` (reflow legítimo 74→76 pp, sem páginas vazias).

### P2 — Rename `src/` → `investigator/`
- [x] Pacote instalável (pyproject `[project] investigator` + `-e .` no requirements.txt); hacks
      `sys.path` removidos dos scripts (guard do app fica — robustez no Streamlit Cloud). Bundles
      joblib re-serializados (pickle referia `src.triage.model`) com probe numérico idêntico.
- [x] Imports migrados em todos os .py; ci.yml/verify.sh/tasks.json/tests.bat → `ruff check .`.
- [x] Sync de docs internos que citavam `src/…`: CLAUDE.md (inventário), caderno de defesa, learning.md,
      glossary.md, guia de estudo (frames P5 com caminhos), README (layout), how_to_run.
- [x] Gates: 93 testes + ruff verdes; AppTest verde; demo reproduz +6,46%; guia recompila (63
      slides, 0 erros). CI a verificar no push.

### P3 — KB FNSPID multi-ano (retrieval)
- [x] Build FEITO (destacado, `run/kb-fnspid.cmd` + tarefa VS Code; log `data/kb_build.log`):
      79.753 registos, SBERT 384-d, ~691 MB gitignored; amostra de 50 em
      `data/samples/kb_fnspid_sample.jsonl`. ⚠️ `--sample` apontada a um caminho NOVO — o defeito
      esmagaria a `kb_sample.jsonl` da demo/tese (e com dim 384≠64).
- [x] Validação honesta em `docs/evaluation/kb_fnspid_build.md`: 14/15 tickers (META="FB"),
      2023=44%, impactos ±1/3d completos e plausíveis; **200 registos (0,25%) com +5d=NaN**
      (fim da janela de preços — documentado); consultas AI/Fed/recalls devolvem os clusters certos
      (sim 0,62–0,85, cross-ticker a funcionar).
- [x] Decisão de consumo: produção na nuvem fica na stack leve com a KB-amostra (números da tese e
      deploy intocados); a KB multi-ano é artefacto local para SBERT + base do trabalho futuro do
      Cap. 6. Data card atualizado ("construída como artefacto; avaliação multi-ano continua futuro").
- [x] Gate: números da tese intocados (demo continua a reproduzir +6,46%); testes verdes.

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
