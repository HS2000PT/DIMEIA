# TRACKER — Progresso por sessão (checklist)

Checklist sintética do que foi feito em cada sessão. Detalhe narrativo em `SESSIONS.md`.

## Sessão 0 — Setup & Authorization (Fase 0)
- [x] Verificação de ambiente (Git, Python, Node, LaTeX, remote GitHub)
- [x] `.claude/settings.json` (allow/deny de permissões)
- [x] `.gitignore`, `.gitattributes`, `.env.example`
- [x] Esqueleto do repositório (§9): `src/`, `tests/`, `thesis/`, `docs/`, `progress/`, `scripts/`, `data/`, `notebooks/`, `presentation/`, `.github/`
- [x] `CLAUDE.md` (memória persistente) + `README.md`
- [x] Ficheiros `progress/` (TRACKER, SESSIONS, DECISIONS, PLANO_SESSOES, QUESTIONS)
- [x] Stubs `docs/` (PT-PT)
- [x] Scripts de automação (setup_env, start_session, end_session, verify, download_data)
- [x] `requirements.txt`, `.python-version`, CI (`compile-thesis.yml`), `tests/test_smoke.py`
- [x] `verify.sh` verde (testes passam, lint limpo) + primeiro commit + push (`origin/main`)
- [ ] **Gate de fase:** confirmação do aluno para iniciar a Fase A

## Sessão 1 — Fase A (Análise de ficheiros de referência)
- [x] Análise de `dissertação_Rafael Silva.pdf` → `docs/analise_referencia.md` (índice completo, 109 pp., ~170 refs, 34 figuras + 6 tabelas, estilo de escrita, benchmark)
- [x] Análise do template ISEP → `docs/analise_template_latex.md` (estrutura, classe/opções, pacotes, citações, figuras/tabelas/algoritmos/código, glossário, build; achado: `latexmk.rc` em falta)
- [x] Benchmark alargado às outras 3 dissertações (Bruno Ribeiro, Helder Pereira, Joana Figueiredo) → secção comparativa em `docs/analise_referencia.md`
- [ ] **Gate de fase:** confirmação do aluno para avançar (Fase B já coberta pela Fase 0 → segue Fase C)

## Próximas sessões
- Fase C (planeamento): 3 títulos; arquitetura; APIs gratuitas (`free_apis.md`); metodologias por componente; `evaluation_design.md`; `PLANO_SESSOES.md` detalhado.
