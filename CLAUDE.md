# CLAUDE.md — Memória Persistente do Projeto

> Ficheiro mais crítico do projeto. É o mecanismo principal de continuidade entre sessões e dispositivos.
> **REGRA ABSOLUTA: atualizar este ficheiro no fim de TODAS as sessões, sem exceção.**
> Ler na íntegra no início de cada sessão, antes de agir.

---

## Estado Atual
- **Sessão nº:** 20 (REWORK concluído S1–S9 + revisão de examinador do Cap. 1 + análise por setor; agora **MASTER PLAN A–H** definido)
- **Última atualização:** 2026-06-26
- **MASTER PLAN (estrada longa até submissão, publicação e defesa):** ver **`progress/MASTER_PLAN.md`** —
  Fases A (conteúdo+visuais → ~80 pp) · B (naturalidade) · C (revisão crítica do zero) · D (revisão crítica
  da implementação + "como correr") · **E (validação ultra-rigorosa página-a-página + RE-VERIFICAR TODAS as
  citações — porta de submissão)** · F (publicação IEEE) · G (slides de defesa) · H (caderno de defesa visual).
  Continuidade multi-dispositivo: este ficheiro + `MASTER_PLAN.md` + `TRACKER.md`, commit/push por sessão.
- **Fase atual + último passo concluído:** **REWORK COMPLETO — plano S1–S9 concluído.** O aluno leu o PDF e ficou desiludido (demasiado técnico/"software-ish", curto, desorganizado, literatura fraca, poucas figuras e confusas, nomes de pastas e **português visível**). Executado o plano definitivo multi-sessão (`.claude/plans/…squishy-yeti.md`; checklist em `progress/TRACKER.md`):
  **S1** estrutura canónica MEIA de 6 capítulos (Introduction · State of the Art · Methods and Materials · **CLARION** · Case Studies · Conclusions) + declutter (removidos `notebooks/`, `presentation/`, `impact_analyzer/`).
  **S2** Cap. 3 aprofundado (data card FNSPID, IA responsável, metodologia de avaliação).
  **S3** Cap. 4 (CLARION) ao nível de desenho: arquitetura limpa + fluxos dos 2 gatilhos + **mockup Telegram** + tabela de decisões; detalhe técnico no Apêndice A.
  **S4** Case Studies com figuras reais novas (série temporal de anomalias TSLA; ablação à janela).
  **S5** Estado da Arte com **+20 fontes → 36 refs verificadas**, 2 figuras de taxonomia.
  **S6** auditoria de citações (36 citadas = 36 no .bib = 36 renderizadas; 0 indefinidas) + consistência global.
  **S7** reorganização de `docs/` em subpastas (`design/ evaluation/ decisions/ defence/ _archive/`); caminhos atualizados.
  **S8** **Caderno de Defesa (PT-PT)** em `docs/defence/caderno_de_defesa.md`.
  **S9** validação final. **Estado: compila 66 pp, 0 erros, 0 citações indefinidas, 0 overfull >15pt; 41 testes verdes + ruff limpo; 0 identificadores de código e 0 PT no corpo; 5 figuras; figuras de avaliação em EN; números reprodutíveis (janela de anomalia fixa).**
- **FASE A em curso (conteúdo+visuais → ~80 pp).** **Concluído:** A1 3 algoritmos (Lista de Algoritmos preenchida) · A2 figura do fluxo mestre de dados/passos (Cap. 4) · A3 figura conceito de embeddings + linha temporal do event study (Cap. 3) · A4 exemplos trabalhados (z-score hipotético no Cap. 3; **recuperação real reproduzível** sobre a KB-amostra no Cap. 3 — query Nvidia → 3 precedentes AI, match cross-ticker MSFT, impacto médio +5d=+6.5%; **anomalia real** TSLA 24-10-2024 z=+7.61 no Cap. 5) · A5 Lista de Código removida. **+ Cap. 2 §2.7 "Existing Tools for the Retail Investor"** (vs alertas de corretora / apps de sentimento / robo-advisors; tabela; 2 citações novas verificadas: `dacunto2019robo`, `cardillo2024robo`). **+ Cap. 5 "Threats to Validity"** reescrito pela taxonomia (construct/internal/external/statistical-conclusion). **+ Cap. 4 diagrama de sequência (UML) do gatilho de notícias.** **+ Cap. 2 §2.5 "Information Retrieval and Ranking Evaluation"** (fundamenta cosine/embeddings, baseline lexical e a métrica precision@k; 3 citações verificadas: `salton1975vsm`, `robertson2009bm25`, `manning2008ir`). **+ Cap. 2 EMH** (Fama 1970 fundamenta a recusa de previsão). **+ `docs/design/how_to_run.md`** (guia do operador, testado). **Estado: compila 72 pp, 0 erros, 0 citações indefinidas, 0 overfull >15pt; 46 refs (todas citadas, 0 órfãs); 41 testes verdes + ruff limpo.**
- **REALIDADE DA CONTAGEM DE PÁGINAS (medida):** ~16 das 72 pp físicas são versos em branco (`twoside`/`openright`, sobretudo front matter) → **conteúdo real ≈ 56 pp**. **Achado confirmado:** prosa em zonas pouco densas em floats (ex.: Estado da Arte) **transborda** para páginas novas (a secção de IR levou 70→72), enquanto figuras/tabelas em capítulos densos são re-empacotadas (não somam páginas). **Logo, o caminho honesto para ~80 é mais PROSA genuína no Estado da Arte / Métodos — SEM encher** (Conclusões/Introdução já completas). **PRÓXIMO:** continuar Fase A com prosa genuína (mais profundidade no Estado da Arte com fontes verificadas; diagrama de sequência do gatilho de mercado) **ou** seguir para Fase B (naturalidade) se o aluno aceitar ~72 pp densas. **Humano (em paralelo):** confirmar redação ISEP da declaração de IA + data; ler/rever a tese (§6.6).
- **Nota de ambiente:** o venv 3.12 foi **recriado** neste ambiente com a stack leve (numpy/pandas/matplotlib/yfinance/pytest/ruff). Para os testes `@sbert` e re-correr a recuperação completa (SBERT/torch), correr `scripts/setup_env.sh` (stack pesada). CI corre testes a cada push.
- **Verificação de integridade da sessão:** confirmar que este ficheiro, `progress/TRACKER.md` e `progress/SESSIONS.md` foram lidos nesta sessão.

---

## Contexto do Projeto (resumo compacto do ROOT PROMPT)
- **Aluno:** Henrique José da Silva Santos — MEIA (ISEP), 2.º ano, fase de dissertação. Nº 1180934.
- **Orientador:** Prof. Luís Gomes. **Coorientador:** Rafael Silva.
- **Perfil do aluno (§3):** não é especialista em IA, tem lacunas de base; objetivo central = **terminar uma dissertação sólida e defendê-la com calma** (pessoa nervosa). **Regra de ouro: ensinar à medida que se avança** (explicar cada conceito em PT-PT em `docs/decisions/learning.md` + `docs/decisions/glossary.md`, com nota de "como explico ao júri em 3 frases" por componente). **Simplicidade defensável > sofisticação.**
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
- **APIs aprovadas:** proposta (Fase C, `docs/design/free_apis.md`, verificado 2026-06-21) — preços: yfinance (base) + Finnhub (fallback, 60/min); notícias: Finnhub news + RSS (+ GNews/Marketaux opcional); histórico: FNSPID; alertas: Telegram Bot API. Alpha Vantage só ocasional (25/dia).
- **Metodologias de IA por componente:** [APÓS FASE C]
- **Estrutura de capítulos:** 7 capítulos (Introduction · Contextualization · Literature Review · Methodology · Implementation · Evaluation · Conclusion), mapeados em `thesis/ch1..ch7/` do template ISEP. [Sessão 3 / Fase D]
- **Layout LaTeX:** usar a estrutura/classe nativa do template ISEP (`meia-style.cls`, `authoryear-comp`, `chN/`); o esboço `thesis/chapters/0X_*.tex` do §9 é ilustrativo e será reconciliado na Fase D. [Sessão 0]
- **Autonomia máxima (pedido do aluno, 2026-06-21):** **NÃO usar AskUserQuestion para confirmações de rotina** ("Yes, continue"). Prosseguir e decidir sozinho ao longo das fases/sessões, com defaults sensatos. Parar **apenas** para os limites rígidos do §2.2 (operações irreversíveis/destrutivas, gastar dinheiro, segredos) ou decisões académicas mesmo irreversíveis. `.claude/settings.json` alargado em conformidade. [D-009]
- (Racional completo em `progress/DECISIONS.md`.)

---

## Estado LaTeX
> ⚠️ **EM REWORK (S1–S9).** As notas abaixo são pré-rework (7 capítulos, 53 pp, 16 refs). **Estado atual real:**
> 6 capítulos canónicos MEIA (Introduction · State of the Art · Methods and Materials · CLARION · Case Studies ·
> Conclusions), **46 referências verificadas**, **compila 72 pp, 0 erros, 0 citações indefinidas, 0 overfull >15pt**;
> figuras de avaliação em EN; arquitetura redesenhada + fluxo + mockup Telegram; 3 algoritmos; figura de embeddings;
> exemplos trabalhados reais (recuperação + anomalia). **Achado medido:** 16/70 pp são versos em branco
> (`twoside`/`openright`) → conteúdo real ≈ 53 pp; ver "REALIDADE DA CONTAGEM DE PÁGINAS" no Estado Atual.
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
  - `scripts/fetch_finnhub_news.py` (notícias reais → CSV) + `scripts/evaluate.py` (multi-seed + ablação de modelo via `--sbert-models` → `docs/evaluation/evaluation_results.md` + figura). P@5 (média 5 seeds): SBERT-MiniLM 0,549±0,014, SBERT-MPNet 0,569±0,009, lexical 0,359, aleatório 0,241, recência 0,105.
  - `src/evaluation/anomaly_eval.py` (Pergunta 1: `rolling_zscore_flags`, `fixed_threshold_flags`, `label_extreme_moves`, `precision_recall_f1`, `firing_rate`; puro, testado) + `scripts/evaluate_anomaly.py` (yfinance → `docs/evaluation/evaluation_anomaly.md` + figura). Taxa de disparo: z-score amplitude 0,017 vs fixo 0,343.
- **Scripts de dados:** `scripts/download_data.py` (FNSPID em **streaming** + filtro por ticker/janela → `data/` gitignored + amostra de títulos); `scripts/build_kb.py` (notícias CSV + preços yfinance → KB JSONL; `--sbert` para SBERT real). `data/samples/news_sample.csv` (sintético) + `data/samples/kb_sample.jsonl` (gerado) + `data/samples/README.md`.
- **Testes (22 + 2 gated, verde):** `test_anomaly_detector.py` (4) + `test_event_study.py` (4) + `test_similarity.py` (7) + `test_knowledge_base.py` (5) + `test_smoke.py` (pipeline + Telegram `@telegram` gated) + `test_sbert_embedder.py` (SBERT real, `@sbert` gated).
- **Smoke/gated:** Telegram (`pytest -m telegram`, envio real confirmado) e SBERT (`pytest -m sbert`, validação semântica) — ambos excluídos do verify por defeito (`-m "not telegram and not sbert"`).
- **Stack ML instalada e fixada:** torch 2.12.1+cpu (índice CPU), sentence-transformers 5.6.0, transformers 5.12.1, huggingface-hub 1.20.1, scikit-learn 1.9.0; `requirements.txt` atualizado + `requirements.lock.txt` (72 pkgs). numpy/pandas inalterados (2.1.3/2.2.3).
- **Pipeline KB validado:** `build_kb.py` (HashingEmbedder) → `kb_sample.jsonl` com impactos coerentes (ex.: TSLA −9,75%, MSFT +7,2%); `SbertEmbedder` validado por teste semântico. **Fonte FNSPID verificada** (HTTP 200, ~23,2 GB).
- **Testes (41 + 2 gated, verde):** anomaly(4) + event_study(4) + similarity(7) + knowledge_base(5) + news_fetcher(3) + explainer(4, inclui fidelidade XAI) + retrieval_eval(5) + anomaly_eval(6) + smoke(3) + gated telegram/sbert.
- **Em falta:** escrever Caps. 5–6 com o que está construído/avaliado; (opcional) download completo do FNSPID + KB SBERT multi-ano (job longo, R2); demo Gatilho 2 ao vivo (Finnhub→KB SBERT→Telegram); `impact_analyzer` (opcional, FinBERT).

## Referências Verificadas
- **16 referências verificadas** em `docs/decisions/citation_log.md` e no `thesis/references.bib`:
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
