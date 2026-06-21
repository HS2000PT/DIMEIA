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

## Sessão 2 — Fase C (Planeamento) — EM CURSO
- [x] Arquitetura técnica detalhada → `docs/arquitectura_sistema.md` (diagrama de componentes, 2 camadas de dados, fluxos dos 2 gatilhos, thin slice, garantias XAI/anti-lookahead)
- [x] 4 títulos candidatos (T0–T3) → `DECISIONS.md` D-007 (recomendado T1); **a aguardar escolha do aluno**
- [x] `learning.md` + `glossary.md` com conceitos da arquitetura (PT-PT, com notas de defesa)
- [x] Título escolhido pelo aluno (**T1**, D-008) + arquitetura confirmada
- [x] APIs gratuitas verificadas → `docs/free_apis.md` (verificado 2026-06-21; conjunto aprovado proposto)
- [x] Metodologias por componente + **8 citações verificadas** (`arquitectura_sistema.md` §9 + `citation_log.md`)
- [x] `docs/evaluation_design.md` detalhado (métricas, baselines, ablções, rubrica XAI, anti-lookahead)
- [x] `progress/PLANO_SESSOES.md` detalhado (~30 sessões + buffer, marcos M1–M5)
- [x] Escolha de título do aluno registada (T1, D-008)
- [ ] **Gate da Fase C:** confirmação do aluno antes da Fase D (LaTeX)

> **Fase C concluída.**

## Sessão 3 — Fase D (Setup LaTeX)
- [x] Template ISEP integrado em `thesis/` (classe, frontmatter, ch1..ch7, appendices, assets)
- [x] `thesis/main.tex` adaptado (título T1, autor, nº 1180934, orientador/coorientador, keywords)
- [x] 7 capítulos esqueleto com estrutura de secções (EN-GB; comentários PT-PT)
- [x] `thesis/references.bib` com as **8 referências verificadas** (`\nocite{*}` temporário)
- [x] `thesis/latexmk.rc` criado (resolve o achado da Fase A) + acrónimos em `glossary.tex`
- [x] Front matter: abstract (EN) + resumo (PT) em rascunho; exemplos do template removidos
- [x] **Compila localmente: 41 páginas, 0 erros, biber OK, 8 refs no `.bib`**
- [ ] Confirmar compilação no **CI** (após push)
- [ ] **Gate da Fase D:** confirmação do aluno; depois → escrita (Sessão 4+)

> **Arco de setup (Fases 0→D) concluído.**

## Sessão 4 — Escrita: Capítulo 2 (Contextualization)
- [x] Investigação de dados US 2025–2026 (mercado, retalho, IA em finanças) — fontes credíveis
- [x] Fontes verificadas em fonte primária e registadas (`citation_log.md` + `references.bib`): SIFMA 2025, Gallup 2025, CCAF 2026
- [x] 1.ª **figura reprodutível** (`scripts/figures/fig_us_market_cap.py` → `thesis/figures/us_equity_market_cap.pdf`); matplotlib fixado
- [x] **Cap. 2 redigido** (rascunho EN-GB, 4 secções, cada afirmação citada) — compila (43 pp., 0 erros, 11 refs)
- [ ] Revisão do aluno ao Cap. 2; fixar fonte primária para a quota de retalho no volume (TODO)

## Sessão 5 — Escrita: Capítulo 1 (Introduction)
- [x] **Cap. 1 redigido** (rascunho EN-GB): motivação, problema, **RQ1–RQ3**, contribuições (Engenharia de IA), estrutura
- [x] Referências cruzadas aos capítulos + citações verificadas; compila (43 pp., 0 erros)
- [ ] Revisão do aluno

## Sessão 6 — Escrita: Capítulo 3 (Literature Review)
- [x] +5 referências verificadas (Liu 2008, Ribeiro 2016, Devlin 2019, Mikolov 2013, Yang 2020) → 16 no total
- [x] **Cap. 3 redigido** (rascunho EN-GB): anomalias, XAI, NLP financeiro, event study; cada obra com o quê/como/limitações
- [x] **4 tabelas comparativas** (anomalias; XAI; representações de texto; posicionamento das escolhas)
- [x] Compila (45 pp., 0 erros; 6 overfull triviais 2–6pt)
- [ ] Revisão do aluno

## Sessão 7 — Escrita: Capítulo 4 (Methodology)
- [x] **Cap. 4 redigido** (rascunho EN-GB): arquitetura, 2 camadas, métodos por componente, avaliação, rigor
- [x] **Diagrama de arquitetura em TikZ** (`fig:architecture`) — reprodutível, versionado no `.tex`
- [x] Equação do z-score; citações verificadas; compila (47 pp., 0 erros, 16 refs)
- [x] **Concluídos os 4 capítulos pré-implementação (1–4)**
- [ ] Revisão do aluno
- [ ] **Boundary:** Caps. 5–7 exigem sistema construído/avaliado → próximo bloco = implementação (precisa Python 3.12, Telegram, APIs)

## Sessão 8 — Implementação: Thin slice (M1) + setup do aluno
- [x] **Setup humano confirmado:** Python 3.12.10; `.env` completo (Telegram + APIs); venv canónico + lockfile (42 pkgs)
- [x] **Autonomia máxima** (D-009): `.claude/settings.json` alargado; sem AskUserQuestion de rotina; memória `max-autonomy`
- [x] **Declaração honesta de uso de IA** no front matter (recusada a versão enganosa; memória `honest-ai-declaration`)
- [x] **`thesis/main.pdf` versionado** via `scripts/build_pdf.sh` (visível no repo)
- [x] **Thin slice (M1)** implementada: market_data(yfinance) → anomaly(z-score, sem lookahead) → explanation → telegram
- [x] Testes: `test_anomaly_detector.py` (4) + `test_smoke.py`; **envio Telegram real confirmado** (`pytest -m telegram`)
- [x] `yfinance==1.4.1` ativo; verify verde (6 testes, lint limpo)
- [ ] Próximo: componentes — `historical_kb`/FNSPID (`data_card.md`), depois `correlation_engine` (stack ML faseada) e Gatilho 2

## Sessão 9 — Implementação: KB histórica + motor de correlação (recuperação)
- [x] `src/correlation_engine/similarity.py` — cosseno + `top_k_similar` (puro NumPy, vetorizado) + 7 testes
- [x] `src/historical_kb/`: `record.py` (`NewsRecord`/JSON), `embedder.py` (interface `Embedder` + `HashingEmbedder` baseline + `SbertEmbedder` lazy), `knowledge_base.py` (`HistoricalKB.build/save/load/find_precedents`)
- [x] Alinhamento evento = 1.º dia de negociação ≥ data da notícia (`searchsorted`); impacto medido do fecho (anti-lookahead) → `learning.md` §11
- [x] `scripts/download_data.py` real (FNSPID **streaming** + filtro ticker/janela → gitignored + amostra de títulos)
- [x] `scripts/build_kb.py` (notícias CSV + preços yfinance → KB JSONL; `--sbert` opcional) + bootstrap sys.path + stdout UTF-8
- [x] `data/samples/news_sample.csv` (sintético) + `data/samples/kb_sample.jsonl` (gerado) + `data/samples/README.md`
- [x] **Pipeline validado ponta-a-ponta** (amostra sintética + preços reais → KB com impactos coerentes com a realidade)
- [x] 5 testes da KB (build, ignora sem-preços, find_precedents, save/load, guarda da amostra versionada)
- [x] **Fonte FNSPID verificada** (HTTP 200, ~23,2 GB; colunas `Date/Article_title/Stock_symbol`) → `data_card.md`
- [x] `learning.md` (§11–12) + `glossary.md` (KB, embedder, baseline, ablação, streaming, top-k) atualizados
- [x] **22 testes verdes**, lint limpo (src+tests+scripts), `verify.sh` ok
- [x] **Stack ML instalada** (torch 2.12.1+cpu via índice CPU, sentence-transformers 5.6.0, transformers 5.12.1, scikit-learn 1.9.0); `requirements.txt` + `requirements.lock.txt` (72 pkgs); numpy/pandas inalterados
- [x] **`SbertEmbedder` validado** (`pytest -m sbert`): recuperação semântica — consulta sem palavras em comum recupera a notícia certa (vantagem sobre baseline lexical); `FutureWarning` de dimensão corrigido (suporta ST 4.x e 5.x)
- [ ] Próximo: download real FNSPID + KB completa (`build_kb.py --sbert`); `news_fetcher` (Gatilho 2); explicação com precedentes
