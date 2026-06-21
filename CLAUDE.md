# CLAUDE.md — Memória Persistente do Projeto

> Ficheiro mais crítico do projeto. É o mecanismo principal de continuidade entre sessões e dispositivos.
> **REGRA ABSOLUTA: atualizar este ficheiro no fim de TODAS as sessões, sem exceção.**
> Ler na íntegra no início de cada sessão, antes de agir.

---

## Estado Atual
- **Sessão nº:** 17 (FNSPID: correção do downloader + achado de viabilidade; sessão contínua desde a 0)
- **Última atualização:** 2026-06-21
- **Fase atual + último passo concluído:** **DOWNLOADER FNSPID CORRIGIDO E VERIFICADO; SCAN COMPLETO INVIÁVEL NESTE AMBIENTE (~3,4 h).** Achei e corrigi um bug real: `pd.read_csv(url)` **bloqueia** no endpoint HF → reescrito para *stream* via `requests` + `usecols` (3 colunas) + `early_stop` (paragem por ordenação de ticker). **Verificado**: extraiu 379 notícias da Agilent 2018-2023 e parou cedo. Mas o débito (~1.300 linhas/s, ~15M linhas) torna o scan dos 15 tickers (A→X) impraticável aqui (job de noite, máquina do aluno). **Decisão honesta:** a avaliação (Cap. 6) fica com a KB real do **Finnhub** (3.692 notícias, multi-seed); FNSPID multi-ano = trabalho futuro reprodutível (script pronto). Tese inalterada (já dizia isto). **41 testes verdes**; lint limpo.
- **PRÓXIMA AÇÃO IMEDIATA (sobretudo humano/opcional):** (1) **o aluno revê e edita todos os capítulos** (o texto é dele; §6.6); (2) confirmar com o Prof. Luís Gomes a redação ISEP da declaração de IA + data de entrega; (3) **correr o `download_data.py` numa máquina/ligação adequada (job de noite)** → KB FNSPID multi-ano → análise de impacto (Pergunta B) — script pronto e verificado, mas inviável neste ambiente; (4) estudo humano de utilidade (RQ3); polish (agradecimentos). Prosseguir autonomamente nos itens técnicos viáveis (D-009).
- **Verificação de integridade da sessão:** confirmar que este ficheiro e `progress/SESSIONS.md` foram lidos nesta sessão.

---

## Contexto do Projeto (resumo compacto do ROOT PROMPT)
- **Aluno:** Henrique José da Silva Santos — MEIA (ISEP), 2.º ano, fase de dissertação. Nº 1180934.
- **Orientador:** Prof. Luís Gomes. **Coorientador:** Rafael Silva.
- **Perfil do aluno (§3):** não é especialista em IA, tem lacunas de base; objetivo central = **terminar uma dissertação sólida e defendê-la com calma** (pessoa nervosa). **Regra de ouro: ensinar à medida que se avança** (explicar cada conceito em PT-PT em `docs/learning.md` + `docs/glossary.md`, com nota de "como explico ao júri em 3 frases" por componente). **Simplicidade defensável > sofisticação.**
- **Contribuição (enquadramento permanente):** tese de **Engenharia de IA**. A contribuição NÃO é inventar algoritmos — é **integrar, aplicar e avaliar criticamente** componentes existentes num sistema funcional, explicável e reproduzível, com uma metodologia documentada de correlação notícia–impacto. Usar modelos/ferramentas existentes **é** o trabalho de engenharia.
- **Tema:** sistema inteligente de alertas financeiros para investidores de retalho, **XAI-first** (toda a lógica transparente e rastreável). Dois gatilhos: (1) movimento abrupto de mercado (NYSE/NASDAQ) → anomalia estatística → alerta + explicação; (2) nova notícia financeira → alerta + impacto potencial + precedentes históricos. **Núcleo:** motor de correlação notícia–mercado baseado em histórico (FNSPID). **Saída:** alertas via Telegram com evento + explicação + fontes + precedentes.
- **Restrições não negociáveis (§5.2):** apenas APIs gratuitas; foco mercado US (NYSE/NASDAQ); XAI-first; útil a um investidor real; rigor académico. ❌ Sem previsão de preços, sem trading algorítmico, sem APIs pagas, sem conteúdo de enchimento.
- **Disciplina de âmbito (§5.3):** primeiro uma **fatia fina end-to-end**; cada componente começa na versão mais simples e defensável; perguntar antes de adicionar complexidade; cortar opcionais se o prazo apertar.
- **Arquitetura de dados (§5.4):** camada **HISTÓRICA** = FNSPID (`Zihan1004/FNSPID`, CC BY-SA 4.0 — atribuição obrigatória); camada **LIVE** = yfinance + (a confirmar) Finnhub/Alpha Vantage/GNews/RSS.
- **Horizonte:** ~30 sessões (guia flexível, orientado pela qualidade). **Continuidade entre sessões é o requisito nº 1.**

---

## Decisões Confirmadas
- **Variante de Inglês (tese):** **EN-GB** (bloqueada; nunca misturar). [Sessão 0]
- **Idioma docs de aprendizagem/internos:** **PT-PT** (o único toggle do §0). Tese em Inglês. [Sessão 0]
- **Versão de Python fixada:** **3.12** (estabilidade para torch/transformers/sentence-transformers; 3.14 corre risco de faltar wheels). [Sessão 0]
- **Título escolhido:** **T1** — *Explainable Financial Alerts for Retail Investors: Integrating Statistical Anomaly Detection and News–Market Impact Correlation* (EN-GB). [Sessão 2 / D-008]
- **APIs aprovadas:** proposta (Fase C, `docs/free_apis.md`, verificado 2026-06-21) — preços: yfinance (base) + Finnhub (fallback, 60/min); notícias: Finnhub news + RSS (+ GNews/Marketaux opcional); histórico: FNSPID; alertas: Telegram Bot API. Alpha Vantage só ocasional (25/dia).
- **Metodologias de IA por componente:** [APÓS FASE C]
- **Estrutura de capítulos:** 7 capítulos (Introduction · Contextualization · Literature Review · Methodology · Implementation · Evaluation · Conclusion), mapeados em `thesis/ch1..ch7/` do template ISEP. [Sessão 3 / Fase D]
- **Layout LaTeX:** usar a estrutura/classe nativa do template ISEP (`meia-style.cls`, `authoryear-comp`, `chN/`); o esboço `thesis/chapters/0X_*.tex` do §9 é ilustrativo e será reconciliado na Fase D. [Sessão 0]
- **Autonomia máxima (pedido do aluno, 2026-06-21):** **NÃO usar AskUserQuestion para confirmações de rotina** ("Yes, continue"). Prosseguir e decidir sozinho ao longo das fases/sessões, com defaults sensatos. Parar **apenas** para os limites rígidos do §2.2 (operações irreversíveis/destrutivas, gastar dinheiro, segredos) ou decisões académicas mesmo irreversíveis. `.claude/settings.json` alargado em conformidade. [D-009]
- (Racional completo em `progress/DECISIONS.md`.)

---

## Estado LaTeX
- **Escrito (Fase D):** `thesis/` integrado a partir do template ISEP (classe `meia-style.cls`, `frontmatter/`, `ch1..ch7/`, `appendices/`). `main.tex` adaptado (título T1, autor, nº 1180934, orientador/coorientador, keywords). **Compila localmente: 41 páginas, 0 erros**, biber OK, **8 referências no `references.bib`**. Front matter: abstract (EN) + resumo (PT) em rascunho; acrónimos atualizados (`glossary.tex`).
- **7 capítulos** (esqueleto com secções): Introduction · Contextualization · Literature Review · Methodology · Implementation · Evaluation · Conclusion.
- **`latexmk.rc` criado** (resolve o achado da Fase A: o `Makefile` invocava-o sem existir).
- **`\nocite{*}` REMOVIDO:** confirmado que o texto cita as **16 referências** (conjunto citado = conjunto do `.bib`); bibliografia renderiza 16 entradas, 0 citações indefinidas.
- **TODOS os 7 capítulos em rascunho**; Cap.2 com 1 figura (matplotlib); Cap.3 com 4 tabelas; Cap.4 com diagrama TikZ; **Cap.5 (Implementation)** (engenharia + tabela de módulos); **Cap.6 (Evaluation)** com resultados reais (2 tabelas + 2 figuras + estudo de caso NVDA/AI-chips); **Cap.7 (Conclusion)** responde a RQ1–RQ3 com os resultados reais + contribuições + limitações + trabalho futuro. **Abstract (EN ~185 palavras, <=200) + resumo (PT)** refinados com resultados.
- **Pipeline de figuras reprodutíveis estabelecido:** matplotlib; scripts em `scripts/figures/` geram PDF vetorial para `thesis/figures/` (commitado para o CI).
- **PDF versionado:** `thesis/main.pdf` é gerado por `scripts/build_pdf.sh` e **commitado** (o aluno quer vê-lo no repo); CI continua a compilar também.
- **Front matter:** declaração de integridade limpa (só EN) + **declaração honesta de uso de IA**; símbolos próprios (z-score). Falta confirmar redação ISEP exata da declaração de IA (humano).
- **Em falta:** revisão humana do aluno a todos os capítulos (o texto é dele); confirmar redação ISEP da declaração de IA + data de entrega; (opcional) FNSPID multi-ano; acrónimos/agradecimentos opcionais.
- **Compila localmente: 53 páginas, 0 erros**, 16 refs na bibliografia, 0 citações indefinidas, figuras presentes; só aviso cosmético de fonte. LaTeX local: MiKTeX + biber 2.21; CI (`compile-thesis.yml`) compila em cada push a `thesis/**`.

## Estado do Código
- **Implementado (thin slice / Gatilho 1):** `src/config.py` (.env), `src/market_data/prices.py` (yfinance + log-returns), `src/anomaly_detector/detector.py` (z-score sem lookahead, `AnomalyResult`), `src/explanation_engine/explainer.py` (explicação por regra), `src/telegram_bot/sender.py` (Telegram API), `src/main.py` (`run_thin_slice`). Dep ativa: `yfinance==1.4.1`.
- **Núcleo (motor de correlação):**
  - `src/correlation_engine/event_study.py` — impacto pós-evento (+1/+3/+5d) e impacto médio (puro; nota anti-lookahead: medir o outcome ≠ prever).
  - `src/correlation_engine/similarity.py` — similaridade do cosseno + `top_k_similar` (puro NumPy, vetorizado).
  - `src/historical_kb/` — `record.py` (`NewsRecord`, JSON), `embedder.py` (interface `Embedder` + `HashingEmbedder` baseline determinístico + `SbertEmbedder` lazy), `knowledge_base.py` (`HistoricalKB.build/save/load/find_precedents`; alinhamento evento = 1.º dia de negociação ≥ data da notícia; persistência JSONL).
- **Gatilho 2 (notícias):**
  - `src/news_fetcher/fetcher.py` — `NewsItem`; parsing puro (`parse_finnhub_news`, `parse_rss`, `_rss_date_to_iso`) + HTTP tardio (`fetch_finnhub_company_news`, `fetch_rss_feed`). Finnhub validado ao vivo (247 notícias AAPL).
  - `src/explanation_engine/explainer.py::explain_news_impact` — alerta XAI com precedentes + impacto médio + nota anti-previsão.
  - `src/main.py::run_news_trigger` — orquestra notícia → embedding → `KB.find_precedents` → explicação → (opcional) Telegram. Default: KB-amostra + `HashingEmbedder`.
- **Avaliação (Pergunta A):**
  - `src/evaluation/retrieval_eval.py` — `retrieval_precision_at_k`, `expected_random_precision`, `recency_precision_at_k`, `same_ticker_forbid` (puro NumPy, testado: precision@k por setor cross-ticker + baselines).
  - `scripts/fetch_finnhub_news.py` (notícias reais → CSV) + `scripts/evaluate.py` (ablação multi-seed → `docs/evaluation_results.md` + figura). Resultado real P@5 (média de 5 seeds): SBERT 0,549±0,014 vs lexical 0,359 vs aleatório 0,241 vs recência 0,105.
  - `src/evaluation/anomaly_eval.py` (Pergunta 1: `rolling_zscore_flags`, `fixed_threshold_flags`, `label_extreme_moves`, `precision_recall_f1`, `firing_rate`; puro, testado) + `scripts/evaluate_anomaly.py` (yfinance → `docs/evaluation_anomaly.md` + figura). Taxa de disparo: z-score amplitude 0,017 vs fixo 0,343.
- **Scripts de dados:** `scripts/download_data.py` (FNSPID em **streaming** + filtro por ticker/janela → `data/` gitignored + amostra de títulos); `scripts/build_kb.py` (notícias CSV + preços yfinance → KB JSONL; `--sbert` para SBERT real). `data/samples/news_sample.csv` (sintético) + `data/samples/kb_sample.jsonl` (gerado) + `data/samples/README.md`.
- **Testes (22 + 2 gated, verde):** `test_anomaly_detector.py` (4) + `test_event_study.py` (4) + `test_similarity.py` (7) + `test_knowledge_base.py` (5) + `test_smoke.py` (pipeline + Telegram `@telegram` gated) + `test_sbert_embedder.py` (SBERT real, `@sbert` gated).
- **Smoke/gated:** Telegram (`pytest -m telegram`, envio real confirmado) e SBERT (`pytest -m sbert`, validação semântica) — ambos excluídos do verify por defeito (`-m "not telegram and not sbert"`).
- **Stack ML instalada e fixada:** torch 2.12.1+cpu (índice CPU), sentence-transformers 5.6.0, transformers 5.12.1, huggingface-hub 1.20.1, scikit-learn 1.9.0; `requirements.txt` atualizado + `requirements.lock.txt` (72 pkgs). numpy/pandas inalterados (2.1.3/2.2.3).
- **Pipeline KB validado:** `build_kb.py` (HashingEmbedder) → `kb_sample.jsonl` com impactos coerentes (ex.: TSLA −9,75%, MSFT +7,2%); `SbertEmbedder` validado por teste semântico. **Fonte FNSPID verificada** (HTTP 200, ~23,2 GB).
- **Testes (41 + 2 gated, verde):** anomaly(4) + event_study(4) + similarity(7) + knowledge_base(5) + news_fetcher(3) + explainer(4, inclui fidelidade XAI) + retrieval_eval(5) + anomaly_eval(6) + smoke(3) + gated telegram/sbert.
- **Em falta:** escrever Caps. 5–6 com o que está construído/avaliado; (opcional) download completo do FNSPID + KB SBERT multi-ano (job longo, R2); demo Gatilho 2 ao vivo (Finnhub→KB SBERT→Telegram); `impact_analyzer` (opcional, FinBERT).

## Referências Verificadas
- **16 referências verificadas** em `docs/citation_log.md` e no `thesis/references.bib`:
  - **8 metodológicas** (DOI/arXiv): Chandola 2009, Brown & Warner 1985, Reimers & Gurevych 2019, Araci 2019, Lundberg & Lee 2017, Arrieta 2020, Adadi & Berrada 2018, Dong 2024.
  - **3 de contextualização** (fonte primária, 2026-06-21): SIFMA 2025 Fact Book, Gallup 2025, CCAF 2026.
  - **5 da revisão de literatura** (Crossref/arXiv, 2026-06-21): Liu 2008 (Isolation Forest), Ribeiro 2016 (LIME), Devlin 2019 (BERT), Mikolov 2013 (word2vec), Yang 2020 (FinBERT).
- **Rejeitada:** MacKinlay 1997 (sem DOI resolúvel) → substituída por Brown & Warner 1985.
- Protocolo §6.4 em vigor: nenhuma entrada no `.bib` sem identificador verificado e registado.

---

## Questões em Aberto / À Espera do Aluno (humano-only)
1. ~~Instalar Python 3.12~~ ✅ FEITO (3.12.10; venv canónico criado).
2. ~~Auth GitHub~~ ✅ FEITO (push a funcionar).
3. ~~Bot Telegram~~ ✅ FEITO (.env preenchido; envio real confirmado).
4. ~~Chaves de APIs~~ ✅ FEITO (.env: Finnhub/AlphaVantage/GNews preenchidas).
5. **Política ISEP de uso de IA** — escrita uma declaração **honesta** no front matter; **falta o aluno confirmar a redação/forma exata exigida pela MEIA** com o Prof. Luís Gomes (não fabricar/encobrir — ver memória `honest-ai-declaration`).
6. **Confirmar conjunto de tickers e janela temporal** do FNSPID (próximo, S12 / `data_card.md`).
7. ~~Escolher o título~~ ✅ RESOLVIDO (T1 — D-008). Arquitetura confirmada.

---

## Regras Permanentes (cópia compacta)
**Limites rígidos (§2.2):** nunca expor segredos (só em `.env` gitignored; scan antes de cada commit); nunca fabricar (dados, resultados, **citações** — toda a citação verificada §6.4); nunca operações git destrutivas/irreversíveis sem aviso (sem `--force`, sem reescrita de história publicada, sem `reset --hard` que perca trabalho); nada destrutivo fora do repo; nunca gastar dinheiro (só free tier); nunca automatizar logins em portais de editoras; **pausar em cada gate de fase**.

**Aluno & aprendizagem (§3):** explicar cada conceito em PT-PT antes de usar; o aluno tem de conseguir defender tudo; simplicidade defensável > sofisticação; nada que o aluno não entenda entra na tese.

**Académico (§6):** contextualização com dados 2025–2026; literatura seminal + recente, peer-reviewed primeiro; tabelas comparativas; cada afirmação com fonte, cada decisão técnica com justificação; **cada citação verificada (citation_log.md) — zero fabricação**; uso de IA declarado; datasets/modelos atribuídos.

**DoD (§8) — gate para avançar de fase:** deliverables existem e commitados; `verify.sh` passa (testes + LaTeX compila); cada conceito novo explicado em `learning.md` com nota de defesa; cada citação nova verificada e registada; nenhum segredo em ficheiros versionados; `CLAUDE.md` atualizado com estado e próxima ação.

**Git & continuidade (§12):** branch único `main`, história linear (rebase); começar sessão com pull-rebase; terminar com verify→commit→pull-rebase→push (sem force-push, sem auto-resolver conflitos que possam perder trabalho); dados grandes/modelos nunca versionados; commits descritivos em PT-PT.
