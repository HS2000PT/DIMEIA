# CLAUDE.md — Memória Persistente do Projeto

> Ficheiro mais crítico do projeto. É o mecanismo principal de continuidade entre sessões e dispositivos.
> **REGRA ABSOLUTA: atualizar este ficheiro no fim de TODAS as sessões, sem exceção.**
> Ler na íntegra no início de cada sessão, antes de agir.

---

## Estado Atual
- **Sessão nº:** 9 (Implementação — KB histórica + motor de correlação; sessão contínua desde a 0)
- **Última atualização:** 2026-06-21
- **Fase atual + último passo concluído:** **KB HISTÓRICA + RECUPERAÇÃO DE PRECEDENTES IMPLEMENTADAS E PROVADAS.** `src/correlation_engine/similarity.py` (cosseno + top-k, puro NumPy) e `src/historical_kb/` (`NewsRecord`; interface `Embedder` com `HashingEmbedder` baseline determinístico **e** `SbertEmbedder` lazy; `HistoricalKB` build/save/load/`find_precedents`). Scripts reais: `scripts/download_data.py` (FNSPID em **streaming**+filtro) e `scripts/build_kb.py` (notícias+preços yfinance → KB JSONL). **Pipeline validado ponta-a-ponta** com amostra sintética + preços reais → `data/samples/kb_sample.jsonl` (10 registos, impactos coerentes). **22 testes verdes** + lint limpo + `verify.sh` ok. **Fonte FNSPID verificada** (HTTP 200, ~23,2 GB, colunas confirmadas) — download completo é job longo (R2), por correr. Stack ML pesada **ainda não instalada** (SbertEmbedder por validar).
- **PRÓXIMA AÇÃO IMEDIATA:** (1) instalar a stack ML faseada (sentence-transformers/torch) e validar `SbertEmbedder` num pequeno conjunto; (2) correr o **download real** do FNSPID (`download_data.py`, job longo) e construir a KB completa (`build_kb.py`); (3) `news_fetcher` (Gatilho 2 — notícias live) e `explanation_engine` com precedentes da KB. Prosseguir autonomamente (D-009).
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
- **Temporário:** `\nocite{*}` em `main.tex` (inclui as 8 refs enquanto os capítulos não citam — remover na escrita).
- **Caps. 1–4 em rascunho** (47 pp. no total); Cap.2 com 1 figura reprodutível (matplotlib); Cap.3 com 4 tabelas comparativas; Cap.4 com diagrama de arquitetura (TikZ); **16 referências** no `.bib` (8 metodológicas + 3 contextualização + 5 revisão de literatura). Caps. 5–7 dependem da implementação/avaliação.
- **Pipeline de figuras reprodutíveis estabelecido:** matplotlib; scripts em `scripts/figures/` geram PDF vetorial para `thesis/figures/` (commitado para o CI).
- **PDF versionado:** `thesis/main.pdf` é gerado por `scripts/build_pdf.sh` e **commitado** (o aluno quer vê-lo no repo); CI continua a compilar também.
- **Front matter:** declaração de integridade limpa (só EN) + **declaração honesta de uso de IA**; símbolos próprios (z-score). Falta confirmar redação ISEP exata da declaração de IA (humano).
- **Em falta:** restantes capítulos (5–7, após implementação/avaliação); abstract <=200 palavras; remover `\nocite{*}` quando o texto citar todas as fontes.
- **Problemas de compilação:** nenhum (só aviso cosmético de fonte `T1/cmtl/b/n`). LaTeX local: MiKTeX + biber 2.21; CI (`compile-thesis.yml`) compila em cada push a `thesis/**`.

## Estado do Código
- **Implementado (thin slice / Gatilho 1):** `src/config.py` (.env), `src/market_data/prices.py` (yfinance + log-returns), `src/anomaly_detector/detector.py` (z-score sem lookahead, `AnomalyResult`), `src/explanation_engine/explainer.py` (explicação por regra), `src/telegram_bot/sender.py` (Telegram API), `src/main.py` (`run_thin_slice`). Dep ativa: `yfinance==1.4.1`.
- **Núcleo (motor de correlação):**
  - `src/correlation_engine/event_study.py` — impacto pós-evento (+1/+3/+5d) e impacto médio (puro; nota anti-lookahead: medir o outcome ≠ prever).
  - `src/correlation_engine/similarity.py` — similaridade do cosseno + `top_k_similar` (puro NumPy, vetorizado).
  - `src/historical_kb/` — `record.py` (`NewsRecord`, JSON), `embedder.py` (interface `Embedder` + `HashingEmbedder` baseline determinístico + `SbertEmbedder` lazy), `knowledge_base.py` (`HistoricalKB.build/save/load/find_precedents`; alinhamento evento = 1.º dia de negociação ≥ data da notícia; persistência JSONL).
- **Scripts de dados:** `scripts/download_data.py` (FNSPID em **streaming** + filtro por ticker/janela → `data/` gitignored + amostra de títulos); `scripts/build_kb.py` (notícias CSV + preços yfinance → KB JSONL; `--sbert` para SBERT real). `data/samples/news_sample.csv` (sintético) + `data/samples/kb_sample.jsonl` (gerado) + `data/samples/README.md`.
- **Testes (22, verde):** `test_anomaly_detector.py` (4) + `test_event_study.py` (4) + `test_similarity.py` (7) + `test_knowledge_base.py` (5) + `test_smoke.py` (pipeline + envio Telegram `@telegram`).
- **Smoke test da thin slice:** **PASSA** (envio real confirmado; `pytest -m telegram`). Excluído do verify por defeito.
- **Pipeline KB validado:** `build_kb.py` corrido com a amostra sintética + preços reais (yfinance) → `kb_sample.jsonl` com impactos coerentes com a realidade (ex.: TSLA −9,75% após margens de Q1; MSFT +7,2% após cloud). **Fonte FNSPID verificada** (HTTP 200, ~23,2 GB; colunas `Date/Article_title/Stock_symbol`).
- **Em falta:** correr download real do FNSPID + KB completa (job longo, R2); instalar stack ML e validar `SbertEmbedder`; `news_fetcher` (Gatilho 2); `explanation_engine` com precedentes; `impact_analyzer` (opcional).

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
