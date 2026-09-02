# TRACKER — Progresso por sessão (checklist)

Checklist sintética do que foi feito em cada sessão. Detalhe narrativo em `SESSIONS.md`.

## Sessão 0 — Setup & Authorization (Fase 0)
- [x] Verificação de ambiente (Git, Python, Node, LaTeX, remote GitHub)
- [x] `.claude/settings.json` (allow/deny de permissões)
- [x] `.gitignore`, `.gitattributes`, `.env.example`
- [x] Esqueleto do repositório (§9): `investigator/`, `tests/`, `thesis/`, `docs/`, `progress/`, `scripts/`, `data/`, `archive/streamlit-app/notebooks/`, `presentation/`, `.github/`
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
- [x] ~~fixar fonte primária para a quota de retalho no **volume**~~ — **caixa fechada a
  2026-08-07 por já não haver afirmação a sustentar.** A frase que preocupava esta linha era de
  um rascunho da sessão 4 e desapareceu na reescrita S1–S9. Hoje o Cap. 1 afirma **propriedade**
  (87% acima de US\$100k, 28% abaixo de US\$50k, Gallup) e o Cap. 2 afirma **comportamento**
  (Robinhood em Março de 2020, Welch), com escala em SIFMA — nenhuma delas é quota de volume, e
  as três estão verificadas em fonte primária. Uma caixa aberta sobre um texto que já não existe
  manda procurar um problema inexistente.
- [ ] Revisão do aluno ao Cap. 2

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
- [x] `investigator/correlation_engine/similarity.py` — cosseno + `top_k_similar` (puro NumPy, vetorizado) + 7 testes
- [x] `investigator/historical_kb/`: `record.py` (`NewsRecord`/JSON), `embedder.py` (interface `Embedder` + `HashingEmbedder` baseline + `SbertEmbedder` lazy), `knowledge_base.py` (`HistoricalKB.build/save/load/find_precedents`)
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
- [x] `investigator/news_fetcher/fetcher.py` — `NewsItem`; parsing puro (`parse_finnhub_news`, `parse_rss`, `_rss_date_to_iso`) + HTTP tardio (`fetch_finnhub_company_news`, `fetch_rss_feed`)
- [x] **Finnhub validado ao vivo** (247 notícias AAPL parseadas para `NewsItem`)
- [x] `explanation_engine.explain_news_impact` — alerta XAI: notícia + impacto médio (horizonte) + lista de precedentes (data/ticker/sim/impacto/título) + nota "não é previsão" (§5.2)
- [x] `investigator/main.py::run_news_trigger` — orquestra notícia→embedding→`KB.find_precedents`→explicação→(opcional)Telegram; default KB-amostra + HashingEmbedder
- [x] Testes: `test_news_fetcher.py` (3, parsing) + `test_explainer.py` (3, incl. média ignora NaN) + smoke Gatilho 2 offline (1)
- [x] Demo end-to-end do alerta (precedentes recuperados + texto rastreável)
- [x] `learning.md` §12 (Gatilho 2) + `glossary.md` (Gatilho 2, RSS, Finnhub)
- [x] **29 testes verdes** + 2 gated; lint limpo; `verify.sh` ok
- [ ] Próximo: download real FNSPID + KB SBERT completa; demo Gatilho 2 ao vivo (Finnhub→KB→Telegram); avaliação (Cap. 6)

## Sessão 11 — Avaliação: recuperação de precedentes (Pergunta A) em dados reais
- [x] `investigator/evaluation/retrieval_eval.py` — precision@k por setor (cross-ticker) + baselines aleatório/recência (puro, 5 testes)
- [x] `scripts/fetch_finnhub_news.py` — **3.692 notícias reais** (Finnhub, 15 tickers/5 setores) → CSV + amostra
- [x] `scripts/evaluate.py` — ablação SBERT vs lexical vs recência vs aleatório → `docs/evaluation_results.md` + figura reprodutível
- [x] **Resultado real (P@5):** SBERT 0,568 > lexical 0,357 > aleatório 0,245 > recência 0,096 (lift +0,323) — hipótese central validada
- [x] `learning.md` §14 (precision@k/lift/baselines) + `glossary.md` (P@k, taxa-base, lift, cross-ticker) + `data_card.md` (dataset Finnhub)
- [x] **34 testes verdes** + 2 gated; lint limpo; `verify.sh` ok
- [ ] Próximo: escrever Cap. 6 (Evaluation) com estes resultados + detetor de anomalias; Cap. 5 (Implementation); (opcional) FNSPID completo

## Sessão 12 — Avaliação: detetor de anomalias (Pergunta 1) em preços reais
- [x] `investigator/evaluation/anomaly_eval.py` — z-score flags (sem lookahead), baseline fixo, rótulo-proxy por percentil, P/R/F1, taxa de disparo (puro, 6 testes)
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

## Sessão 17 — FNSPID: correção do downloader + achado de viabilidade
- [x] **Bug encontrado e corrigido:** `pd.read_csv(url)` bloqueia no endpoint HF → `download_data.py` reescrito para *stream* via `requests` + `usecols` (3 colunas) + `early_stop` (paragem por ordenação de ticker)
- [x] **Verificado:** extraiu 379 notícias reais da Agilent (ticker A) 2018-2023 e parou cedo, corretamente
- [x] **Achado de viabilidade:** ~1.300 linhas/s, ~15M linhas → ~3,4 h para varrer tudo; 15 tickers vão de A a X (sem atalho) → **scan completo inviável neste ambiente**; é job para a máquina/ligação do aluno (de noite)
- [x] Documentado em `download_data.py` (docstring) e `docs/data_card.md`; artefactos de teste limpos
- [x] **Decisão honesta:** avaliação fica com a KB real do Finnhub (3.692, multi-seed); FNSPID multi-ano = futuro reprodutível (script pronto). 41 testes verdes; lint limpo
- [ ] Próximo (humano): correr `download_data.py` numa ligação adequada → KB FNSPID → impacto (Pergunta B)

## Sessão 18 — Avaliação: ablação de modelo de embeddings
- [x] `evaluate.py` generalizado para comparar N modelos SBERT (`--sbert-models`) + tabela/figura dinâmicas
- [x] **Ablação corrida** (5 seeds): P@5 SBERT-MiniLM 0,549±0,014, SBERT-MPNet 0,569±0,009, lexical 0,359, aleatório 0,241, recência 0,105 → vantagem robusta ao modelo
- [x] Cap. 6 atualizado (tabela com MiniLM+MPNet + nota de ablação); figura regenerada (5 métodos); `learning.md` §14 atualizado
- [x] **41 testes verdes**; lint limpo; tese compila 53 pp., 0 citações indefinidas
- [x] **README atualizado**: estado real (rascunho completo) + secção "Reproducing the results" (comandos exatos); LaTeX verificado sem overfull boxes nem avisos
- [ ] Próximo (humano/opcional): revisão do aluno; FNSPID completo (job de noite); estudo humano de utilidade

---

# REWORK (a partir da revisão do aluno) — Plano definitivo multi-sessão

> O aluno leu o PDF e ficou desiludido: demasiado técnico/"software-ish", curto, desorganizado,
> revisão de literatura fraca, poucas figuras e confusas, nomes de pastas e português no documento.
> Objetivo: dissertação académica limpa e clara (estilo das 4 de referência, ~90–120 pp), repositório
> arrumado, e um **Caderno de Defesa em PT-PT**. Trabalho deliberado, multi-sessão, validado passo a passo.
> **Checklist mestre completo:** ver plano aprovado (`.claude/plans/…squishy-yeti.md`).

## Roadmap S1–S9 (estado)
- [x] **S1 — Plano + declutter + consolidar ganhos**
  - [x] Reestruturação para 6 capítulos canónicos MEIA (remoção do Cap. 7); compila
  - [x] Estado da Arte expandido (+12 fontes verificadas → 28; 2 figuras de taxonomia; discussão por secção)
  - [x] Diagrama de arquitetura redesenhado (sem cruzamentos) + fluxo do gatilho de notícias + **mockup do alerta Telegram**
  - [x] Figuras de avaliação PT→EN (números idênticos): era o "português" visível no PDF
  - [x] Identificadores de código removidos do corpo (0 `\texttt{}` de código); InvestiGator no abstract/resumo
  - [x] **Declutter:** removidos `archive/streamlit-app/notebooks/`, `presentation/`, `investigator/impact_analyzer/` (stub); .py compilam; sem importações pendentes
  - [x] TRACKER semeado; CLAUDE.md + SESSIONS.md atualizados
- [x] **S2 — Introdução (Cap. 1) + Métodos e Materiais (Cap. 3)**
  - [x] Cap. 3 aprofundado: **data card FNSPID** (tabela: fonte, licença CC BY-SA 4.0, 15 tickers, janela 2018–2023, governança), pré-processamento + alinhamento anti-lookahead, camada live + dataset de avaliação, **IA responsável/ética** alargada, metodologia de avaliação + rigor
  - [x] Cap. 1 confirmado bem-escopado (contexto de alto nível; literatura profunda fica no Estado da Arte)
  - [x] Compila 62 pp, 0 erros, 0 citações indefinidas, sem overfull; corpo sem identificadores de código/PT
- [x] **S3 — InvestiGator (Cap. 4)** ao nível de desenho + Apêndice de reprodutibilidade
  - [x] Novo **diagrama de fluxo do gatilho de mercado** (preço→janela→z-score→limiar→alerta; nó de decisão losango)
  - [x] **Tabela de decisões de desenho** (decisão/escolha/racional) — torna explícito o juízo de engenharia
  - [x] Apêndice A (Reproducibility) confirmado ao nível certo; corpo sem identificadores de código
  - [x] Compila 64 pp, 0 erros, 0 citações indefinidas, sem overfull
- [x] **S4 — Estudos de Caso (Cap. 5)** + novas figuras de resultados
  - [x] Nova figura: **série temporal de anomalias** (TSLA real, 16 de 750 dias sinalizados; `scripts/figures/fig_anomaly_timeseries.py`)
  - [x] Nova figura: **ablação à janela** (curva F1 vs janela; gerada por `evaluate_anomaly.py`)
  - [x] CS1 enriquecido com exemplo trabalhado + ambas as figuras referenciadas
  - [x] Compila 64 pp, 0 erros, 0 indefinidas; ruff limpo
- [x] **S5 — Estado da Arte (2.ª expansão) + Conclusões (Cap. 6)** (parcial: SoTA expandido)
  - [x] +8 fontes verificadas → **36 refs** (Breunig LOF, Ahmed survey financeiro, Miller, Lipton, Da/Engelberg/Gao, Kearney&Liu, Ding 2015, Johnson FAISS); integradas em §2.1–2.5
  - [x] Compila 66 pp, 0 erros, 0 indefinidas; todas registadas em citation_log
  - [ ] (restante) afinar Conclusões (Cap. 6) — números já atualizados na S4; prosa OK
- [x] **S6 — Front matter + consistência global + auditoria de citações**
  - [x] Auditoria de citações: **36 citadas = 36 no .bib = 36 renderizadas**, 0 órfãs, 0 indefinidas; todas em citation_log
  - [x] Consistência: sem números de anomalia antigos; sem PT no corpo; 0 overfull >15pt; acrónimos todos definidos (0 avisos de glossário)
  - [x] Front matter: abstract/resumo com InvestiGator e números finais (P@5 0.55 vs 0.24); declarações honestas; comentário da data em EN
- [x] **S7 — Reorganização do repositório** (consolidação moderada), validada
  - [x] `docs/` agrupado: `design/` (arquitetura, data card, APIs, eval design, setup, riscos), `evaluation/` (resultados auto-gerados), `decisions/` (citation_log, glossary, learning), `_archive/` (analises de fase inicial), `defence/` (para o Caderno S8)
  - [x] Atualizadas TODAS as referências de caminho (defaults dos scripts evaluate*, docstrings investigator/scripts, README, CLAUDE, links inter-docs); progress/ histórico preservado
  - [x] Corrigidos 6 E501 resultantes; **41 testes verdes, ruff limpo**; .pyc ignorados; README com novo mapa do repositório
- [x] **S8 — Caderno de Defesa (PT-PT)** (`docs/defence/caderno_de_defesa.md`)
  - [x] Documento de estudo PT-PT: problema/âmbito/contribuição; decisões+porquês; cada componente + "defesa em 3 frases"; resultados+limitações honestas; mapa do repo; **perguntas difíceis do júri + respostas**
- [x] **S9 — Validação final & sign-off**
  - [x] Build limpo: **66 pp, 0 erros, 0 citações indefinidas, 0 overfull >15pt, 36 entradas na bibliografia**
  - [x] **41 testes verdes + ruff limpo**; 0 identificadores de código e 0 PT no corpo dos capítulos; 5 figuras presentes
  - [x] Continuidade atualizada (CLAUDE/TRACKER/SESSIONS); tudo commitado e enviado
  - [ ] (HUMANO) decisão de extensão (66 pp vs ~90–120): 3.ª expansão SoTA / estudos de caso mais profundos / aceitar tese mais curta — sem encher

> **REWORK S1–S9 CONCLUÍDO.** Tese transformada (53→66 pp): estrutura canónica, literatura forte (36 refs
> verificadas), figuras limpas em EN, sem identificadores de código nem PT no corpo, repo arrumado, Caderno
> de Defesa PT-PT. Resta sobretudo trabalho **humano** (revisão do aluno; decisão de extensão; declaração ISEP).

> **Nota de ambiente:** o venv 3.12 não está presente neste ambiente (foi recriado/limpo entre turnos).
> A compilação LaTeX corre sem venv; para regenerar figuras/correr pytest é preciso recriar o venv
> (`scripts/setup_env.sh`). Backstop: o CI corre os testes a cada push.

---

# MASTER PLAN A–H (estrada longa) — ver `progress/_historico/MASTER_PLAN.md`

> Pós-rework: definido o plano-mestre da estrada longa até submissão, publicação IEEE e defesa.
> Marcar progresso aqui e em `MASTER_PLAN.md`. Porta crítica: **Fase E** (validação ultra-rigorosa
> página-a-página + re-verificação de TODAS as citações).

> **MASTER PLAN A–H COMPLETO (sessão 21, 2026-06-27).** Tese 76 pp; 50 refs re-verificadas; estatística
> re-corrida idêntica; paper/ + slides/ compilam; documentos de rigor commitados. Só faltam tarefas humanas.

- [x] **Fase A** — conteúdo + visuais (**76 pp**, alvo "80-ish"): 3 algoritmos; figuras de fluxo/sequência/embeddings; exemplos reais (TSLA z=7.61; recuperação Nvidia cross-ticker); SoTA 40→**50 refs verificadas** (IR, EMH, trust, volatilidade, ferramentas existentes); protocolo de avaliação formalizado; `how_to_run.md`.
- [x] **Fase B** — passagem de naturalidade/voz académica (conteúdo novo + corpo); menos travessões/tics de IA.
- [x] **Fase C** — revisão crítica independente (`docs/decisions/review_log.md`); achados C-1..C-5 corrigidos.
- [x] **Fase D** — revisão de implementação (`implementation_review.md`); **estatística RE-CORRIDA hoje = idêntica**; 42 testes; guarda R1.
- [x] **Fase E** — porta de submissão (`page_audit.md`): **50/50 citações re-verificadas** (DOI/arXiv/ISBN/fontes primárias); PDF sem `??`/indefinidas/overfull. Ataque sobre fontes = 0.
- [x] **Fase F** — artigo IEEE (`paper/`, IEEEtran) destilado da tese validada; compila.
- [x] **Fase G** — slides de defesa (`slides/`, Beamer 14 frames); compila.
- [x] **Fase H** — caderno de defesa **visual** (`docs/defence/caderno_de_defesa.md`): workflow em diagramas, exemplos passo-a-passo, mapa dos números validados.
- [ ] **HUMANO** — confirmar redação ISEP da declaração de IA + data de entrega; leitura final do aluno (§6.6).

---

# Revisão tipo-júri (Sessão 22, 2026-06-27)

> Passagem de revisão orientador/revisor/examinador sobre a tese inteira. **0 fabricação** (nenhuma
> citação/número alterado). Relatório completo (severidades + scorecard por capítulo) em
> `.claude/plans/root-prompt-claude-code-md-squishy-yeti.md`.

- [x] **M1** — Cap. 5/CS3: recuperação capta tema, não direção; artefactos nomeados; liga a trust/over-reliance.
- [x] **M2** — *data card* (Cap. 3) marcado como FNSPID **desenhada** + ponteiro para o corpus real avaliado (Cap. 5).
- [x] **M3** — travessões `---` 117 → 39 (sentido preservado).
- [x] **Mo2** — mockup do Telegram consistente (3 precedentes → −2,2%).
- [x] **Mo4** — Cap. 4 produto responsável (fadiga/over-reliance) + Cap. 6 trabalho futuro.
- [x] **Mo3** — Apêndice A: versões fixadas + comandos de reprodução; LOF expandido.
- [x] **Mi1** — fraseado da RQ2.
- [x] **Validação** — 78 pp, 0 erros/indefinidas/overfull/`??`; 42 testes + ruff; citações 50/50.
- [ ] **HUMANO** — declaração ISEP de IA + data; leitura final do aluno (§6.6).

---

# Reescrita profunda para clareza (Sessão 24, 2026-06-28)
- [x] Ch1 — secções por pergunta + mapa do leitor (`78c9819`)
- [x] Ch2 — pergunta + takeaway "For InvestiGator"; −4 pp (`17448dd`)
- [x] Ch3 — concept-first; "três escolhas" → lista (`d11212e`)
- [x] Ch4 — **System Design**: modelo de dados + componentes + Decision Logic (`e60604b`)
- [x] Ch5 — cada estudo abre com pergunta + resposta (`f4021ff`)
- [x] Ch6 — vereditos RQ + listas (`99001f4`)
- [x] Validação global: 72 pp, 0 erros/indefinidas/overfull/`??`; 0 travessões em prosa; citações 50/50
- [ ] (opcional) sincronizar paper/slides/caderno; leitura do aluno; declaração ISEP (humano)

---

# Polimento visual + Guia de estudo (Sessão 25, 2026-06-28)
- [x] Figuras: regra global anti-hifenização; 15 figuras auditadas por render; tese 72 pp, 0 erros (f4b0ac3)
- [x] Guia de estudo PT-PT (Beamer) `slides/guia_estudo/` — 51 slides, do zero, só o que a tese usa
  - [x] P0/P1 capa + IA do zero + glossário (5175c47)
  - [x] P2-P4 problema + sistema + dados reais (1645644)
  - [x] P5-P6 código módulo-a-módulo + workflow real (9033843)
  - [x] P7-P10 avaliação + decisões + sensibilidade + júri (6e90ccd)
- [ ] (opcional) sincronizar paper/slides/caderno; leitura do aluno; declaração ISEP (humano)

---

# Plano de 9 fases + visuais (Sessão 40, 2026-07-22) — na máquina do FNSPID
- [x] **F4** ablação RQ4-ext CORRIDA (7ae5390): `context_ext` aditivo + `train_triage_ext.py`; contexto
  v1 0,537 ≈ congelado, +5 features 0,535 (Δ −0,002, nenhuma ajuda); evaluation_triage_ext.md + figura
  + secção Cap. 5; congelados intactos; +4 testes (199)
- [x] **F7** screenshot com marca nova (Playwright) + figura corpo→apêndice + apêndice "Proof of Work"
  (6f199e3); tese 90 pp, 0 erros
- [x] **Visuais** Fig. 3.2 "jornada dos dados" (1 headline real por RAW→CLEAN→REPRESENT/AI→MEASURE) na
  tese + slides (775462a) + guia (8f0291b); "Built with" (badges) nos slides+guia
- [x] **F8** guia 73→76 slides (jornada dos dados + ablação RQ4-ext + "feito com"); README 73→76
- [x] **F9** `make_public_bundle.py` + `public_bundle.md` (106ed97): git ls-files − internos, scan de
  segredos, --git=1 commit, nunca faz push; testado (210 ficheiros, 21 fora, limpo)
- [x] Gates: 199 testes + ruff; tese 90 pp/paper/slides 19/guia 76 = 0 erros
- [ ] (HUMANO) licença + declaração ISEP; leitura final; publicar o bundle (cliques)
