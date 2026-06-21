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

## Sessão 10 — Implementação: Gatilho 2 (notícias) + explicação com precedentes
- [x] `src/news_fetcher/fetcher.py` — `NewsItem`; parsing puro (`parse_finnhub_news`, `parse_rss`, `_rss_date_to_iso`) + HTTP tardio (`fetch_finnhub_company_news`, `fetch_rss_feed`)
- [x] **Finnhub validado ao vivo** (247 notícias AAPL parseadas para `NewsItem`)
- [x] `explanation_engine.explain_news_impact` — alerta XAI: notícia + impacto médio (horizonte) + lista de precedentes (data/ticker/sim/impacto/título) + nota "não é previsão" (§5.2)
- [x] `src/main.py::run_news_trigger` — orquestra notícia→embedding→`KB.find_precedents`→explicação→(opcional)Telegram; default KB-amostra + HashingEmbedder
- [x] Testes: `test_news_fetcher.py` (3, parsing) + `test_explainer.py` (3, incl. média ignora NaN) + smoke Gatilho 2 offline (1)
- [x] Demo end-to-end do alerta (precedentes recuperados + texto rastreável)
- [x] `learning.md` §12 (Gatilho 2) + `glossary.md` (Gatilho 2, RSS, Finnhub)
- [x] **29 testes verdes** + 2 gated; lint limpo; `verify.sh` ok
- [ ] Próximo: download real FNSPID + KB SBERT completa; demo Gatilho 2 ao vivo (Finnhub→KB→Telegram); avaliação (Cap. 6)

## Sessão 11 — Avaliação: recuperação de precedentes (Pergunta A) em dados reais
- [x] `src/evaluation/retrieval_eval.py` — precision@k por setor (cross-ticker) + baselines aleatório/recência (puro, 5 testes)
- [x] `scripts/fetch_finnhub_news.py` — **3.692 notícias reais** (Finnhub, 15 tickers/5 setores) → CSV + amostra
- [x] `scripts/evaluate.py` — ablação SBERT vs lexical vs recência vs aleatório → `docs/evaluation_results.md` + figura reprodutível
- [x] **Resultado real (P@5):** SBERT 0,568 > lexical 0,357 > aleatório 0,245 > recência 0,096 (lift +0,323) — hipótese central validada
- [x] `learning.md` §14 (precision@k/lift/baselines) + `glossary.md` (P@k, taxa-base, lift, cross-ticker) + `data_card.md` (dataset Finnhub)
- [x] **34 testes verdes** + 2 gated; lint limpo; `verify.sh` ok
- [ ] Próximo: escrever Cap. 6 (Evaluation) com estes resultados + detetor de anomalias; Cap. 5 (Implementation); (opcional) FNSPID completo

## Sessão 12 — Avaliação: detetor de anomalias (Pergunta 1) em preços reais
- [x] `src/evaluation/anomaly_eval.py` — z-score flags (sem lookahead), baseline fixo, rótulo-proxy por percentil, P/R/F1, taxa de disparo (puro, 6 testes)
- [x] `scripts/evaluate_anomaly.py` — corre em yfinance (3 anos, 15 tickers) → `docs/evaluation_anomaly.md` + figura reprodutível
- [x] **Resultado real:** amplitude da taxa de disparo z-score **0,017** vs limiar fixo **0,343** (20× mais consistente); F1 z-score 0,524 vs fixo 0,216; ablação janela 10/20/60d → F1 0,385/0,524/0,687
- [x] `learning.md` §15 (consistência da taxa de disparo, com nota de defesa)
- [x] **40 testes verdes** + 2 gated; lint limpo; `verify.sh` ok
- [ ] Próximo: escrever Cap. 6 (Evaluation) com ambos os resultados + estudo de caso; Cap. 5 (Implementation)

## Sessão 13 — Escrita: Capítulo 6 (Evaluation)
- [x] **Cap. 6 redigido** (EN-GB): setup, detetor de anomalias (consistência da taxa de disparo + P/R/F1 + ablação), recuperação (precision@k + baselines), qualidade da explicação (fidelidade por construção), estudo de caso ponta-a-ponta, discussão/limitações
- [x] 2 tabelas de resultados + 2 figuras reprodutíveis (`eval_anomaly_firing_rate.pdf`, `eval_retrieval_precision.pdf`); citações `chandola2009anomaly`/`brown1985daily`/`reimers2019sbert`/`arrieta2020xai`
- [x] **KB SBERT real** construída de 3.692 notícias Finnhub (2.964 registos) → estudo de caso real NVDA/AI-chips (precedentes temáticos cross-empresa)
- [x] Honestidade: corrigido que Finnhub free só dá ~1 mês de notícias; impactos `n/a` em notícias recentes; FNSPID multi-ano = futuro
- [x] **Tese compila: 51 páginas, 0 erros**, sem refs indefinidas, figuras presentes; `main.pdf` atualizado
- [ ] Próximo: Cap. 5 (Implementation); Cap. 7 (Conclusion); abstract; remover `\nocite{*}`

## Sessão 14 — Escrita: Capítulo 5 (Implementation)
- [x] **Cap. 5 redigido** (EN-GB): ambiente/tooling; estrutura do repo + 3 princípios de engenharia (thin slice; lógica pura vs I/O com imports tardios; interfaces `Embedder`); pipeline da KB (alinhamento anti-lookahead, streaming FNSPID, KB Finnhub p/ avaliação); camada live; detetor; motor de correlação; explicação; orquestração; testes
- [x] Tabela de módulos (componente→módulo→elementos); citações `dong2024fnspid`/`reimers2019sbert`/`araci2019finbert`; referência ao diagrama `fig:architecture` e ao Cap. 6
- [x] **Tese compila: 53 páginas, 0 erros**, sem refs indefinidas; `main.pdf` atualizado
- [ ] Próximo: Cap. 7 (Conclusion); abstract <=200 palavras; remover `\nocite{*}`

## Sessão 15 — Escrita: Capítulo 7 (Conclusion) + abstract + limpeza de citações
- [x] **Cap. 7 redigido** (EN-GB): conclusões por RQ (RQ1 deteção transparente; RQ2 recuperação sem lookahead; RQ3 fidelidade por construção/utilidade por validar), contribuições revisitadas, limitações honestas, trabalho futuro
- [x] **Abstract (EN ~185 palavras, <=200)** e **resumo (PT)** refinados com os resultados reais e alinhados com as conclusões
- [x] **`\nocite{*}` removido** — confirmado que o texto cita as 16 referências (conjunto citado = `.bib`); bibliografia renderiza 16 entradas, 0 citações indefinidas
- [x] **Tese compila: 53 páginas, 0 erros**; `main.pdf` atualizado. **Rascunho completo dos 7 capítulos.**
- [ ] Próximo (humano/opcional): revisão do aluno; redação ISEP da declaração de IA; (opcional) FNSPID completo + estudo humano de utilidade

## Sessão 16 — Rigor da avaliação: multi-seed + teste de fidelidade
- [x] `scripts/evaluate.py` agora corre **5 seeds** e reporta **média ± desvio** (P@5 SBERT 0,549±0,014 vs lexical 0,359 vs aleatório 0,241 vs recência 0,105; desvios ~0,01)
- [x] **Teste automático de fidelidade** (`test_explainer.py`): a explicação reproduz exatamente data/ticker/score de cada precedente recuperado, sem inventar — verificação programática de XAI (RQ3)
- [x] Cap. 6 (tabela mean±std, secção de fidelidade), Cap. 7 (RQ2) e abstract EN/PT atualizados; removida a limitação "single seed"
- [x] **41 testes verdes** + 2 gated; lint limpo; tese compila 53 pp., 0 citações indefinidas
- [ ] Próximo (humano/opcional): revisão do aluno; (opcional) FNSPID completo; estudo humano de utilidade
