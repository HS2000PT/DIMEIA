# SESSIONS — Registo de sessões (continuidade)

Registo curto de cada sessão para garantir continuidade entre dispositivos.
A entrada mais recente fica no topo.

---

## Sessão 20 — 2026-06-26 — MASTER PLAN A–H + Fase A (conteúdo+visuais)
**Contexto:** pós-rework, o aluno definiu a estrada longa até submissão/IEEE/defesa. Criado
`progress/MASTER_PLAN.md` (Fases A–H; porta de submissão = Fase E: validação página-a-página +
re-verificar TODAS as citações). Pedido central da Fase A: ~80 pp por **conteúdo genuíno** (sem encher),
mais visuais, e "visualizar o workflow de dados/passos".

**Feito (Fase A, conteúdo genuíno — 4 commits):**
- **Cap. 3 (Methods):** figura conceptual do espaço de embeddings + **exemplo de recuperação REAL e
  reproduzível** sobre a KB-amostra commitada (query "Nvidia demand surges on AI chip orders" → 3
  precedentes AI; inclui match **cross-ticker** MSFT; impacto médio +5d = **+6.5%**). Encoder transparente
  baseline para reprodutibilidade sem download de modelo; o sistema implantado usa SBERT (avaliado no Cap. 5).
- **Cap. 5 (CS1):** **exemplo numérico de anomalia REAL** — TSLA 24-10-2024 (reação a resultados):
  μ=−0.92%, σ=2.73%, r=+19.82% (log; ≈+22% em preço) → **z=+7.61**, sinalizado a k=3 (yfinance, janela fixada).
- **Cap. 2 §2.7 "Existing Tools for the Retail Investor":** posiciona o CLARION vs alertas de corretora /
  apps de notícias-sentimento / robo-advisors (tabela em 4 dimensões). **2 citações novas verificadas**
  (DOI resolúvel, registadas em `citation_log.md`): `dacunto2019robo` (RFS 2019), `cardillo2024robo` (FRL 2024).
- **Cap. 5 "Threats to Validity"** reescrito pela taxonomia clássica (construct / internal / external /
  statistical-conclusion), com mitigação de cada ameaça (proxy de setor, restrição cross-ticker,
  no-lookahead, confounding, generalização, 5 seeds).
- (Sessões anteriores da Fase A, já commitadas: 3 algoritmos + Lista de Algoritmos; figura de fluxo mestre;
  exemplo z-score hipotético; secção de deployment; análise qualitativa de recuperações; Lista de Código removida.)

**Achado medido (não suposição):** das **70 pp** físicas, **16 são páginas em branco** (versos do
`twoside`/`openright`; sobretudo front matter) → **conteúdo real ≈ 53 pp**. O documento é muito denso em
floats: cada acréscimo é re-empacotado e só "transborda" quando acumula → daí 68→70 apesar de ~5 pp novas.
**Chegar a ~80 exige mais prosa genuína ao longo de várias sessões — sem encher** (Conclusões/Introdução já
completas; aprofundá-las seria encher).

**Estado:** compila **70 pp**, 0 erros, 0 citações indefinidas, 0 overfull >15pt; **42 refs**; 41 testes
verdes + ruff limpo. Tudo commitado e pushed.

**Próxima ação:** continuar Fase A com conteúdo genuíno (diagrama de sequência por gatilho; aprofundar 1–2
áreas do Estado da Arte com fontes verificadas; `docs/design/how_to_run.md`) **ou** seguir para Fase B
(naturalidade) se o aluno aceitar ~70 pp densas. **Humano:** confirmar redação ISEP da declaração de IA + data.

---

## Sessão 19 — 2026-06-24 — REWORK: plano definitivo multi-sessão + reestruturação (S1)
**Contexto:** o aluno leu o PDF e ficou desiludido — demasiado técnico/"software-ish", curto, desorganizado,
revisão de literatura fraca, poucas figuras e confusas, nomes de pastas e **português visível** no documento;
"é um documento de dissertação, não uma especificação de software". Pediu reescrita orientada à dissertação,
limpeza/reorganização do repositório, e um **Caderno de Defesa em PT-PT**, num plano definitivo multi-sessão.

**Decisões (esta sessão):** estrutura canónica MEIA de 6 capítulos; sistema **CLARION**; cleanup = consolidação
moderada; defesa = guia único PT-PT; sequência = declutter já, reorganização estrutural perto do fim.

**Feito (S1):**
- Estudadas as 4 dissertações de referência (104–139 pp): estrutura idêntica (Intro · State of the Art ·
  Methods and Materials · [Sistema nomeado] · Case Studies · Conclusions). Tese antiga = 53 pp, 7 caps finos.
- **Reestruturação para 6 capítulos** (`main.tex` + `ch1..ch6`; removido `ch7`); conteúdo redistribuído.
- **Estado da Arte** reescrito em prosa académica: +12 fontes **verificadas** (Barber&Odean, Tetlock, Welch,
  Fama et al. 1969, Loughran&McDonald, Pang, Guidotti, Rudin, Doshi-Velez, Vaswani, GloVe, BloombergGPT) → 28
  no total; 2 figuras de taxonomia; discussão por secção + conclusões de capítulo. Todas registadas em
  `citation_log.md`.
- **Figuras/artefactos:** diagrama de arquitetura redesenhado (camadas, Y convergente, sem cruzamentos);
  novo fluxo do gatilho de notícias; **mockup do alerta Telegram** (caixas LaTeX robustas).
- **Português no PDF corrigido:** as figuras de avaliação tinham etiquetas/títulos PT → reescritos em EN e
  **regenerados com números idênticos** (anomalia spread 0.017/0.343, F1 0.524; retrieval P@5 0.549/0.569).
- **De-tech:** removidos todos os identificadores de código do corpo (0 `\texttt{}` de código; era 72 no Cap. 5);
  detalhe técnico movido para o Apêndice A (Reproducibility). CLARION no abstract/resumo.
- **Declutter:** removidos `notebooks/`, `presentation/`, `src/impact_analyzer/` (stub nunca usado).
- **Plano mestre** aprovado e registado (`.claude/plans/…`; checklist em `TRACKER.md`).
- Compila: **60 pp, 0 erros, 0 citações/refs indefinidas**.

**Validação:** LaTeX compila limpo; .py compilam (py_compile); sem importações dos módulos removidos.
Nota: **venv 3.12 ausente** neste ambiente (recriar para pytest/figuras; CI é o backstop dos testes).

**Feito (S2–S9, mesma sessão contínua):**
- S2: Cap. 3 (Methods and Materials) aprofundado — data card FNSPID, IA responsável, metodologia de avaliação.
- S3: Cap. 4 (CLARION) ao nível de desenho — arquitetura limpa + fluxos dos 2 gatilhos + mockup Telegram +
  tabela de decisões; detalhe técnico no Apêndice A.
- S4: Case Studies com 2 figuras reais novas (série temporal de anomalias TSLA; ablação à janela).
- S5: Estado da Arte com +8 fontes (→ **36 refs verificadas**), todas em citation_log.
- **Achado importante:** um reset de ambiente reverteu um lote não-commitado (as figuras de avaliação tinham
  voltado a PT no PDF!). Reaplicado e re-protegido; figuras regeneradas em EN; janela de anomalia **fixada**
  (2023-06..2026-06) para reprodutibilidade; números da tese atualizados (z-score 0.015 vs 0.344; F1 0.516).
- S6: auditoria de citações (36=36=36, 0 indefinidas) + consistência global.
- S7: `docs/` reorganizado em `design/ evaluation/ decisions/ defence/ _archive/`; todos os caminhos atualizados.
- S8: **Caderno de Defesa (PT-PT)** — `docs/defence/caderno_de_defesa.md`.
- S9: validação final — **66 pp, 0 erros, 0 indefinidas, 0 overfull; 41 testes + ruff verdes**; 0 código/PT no corpo.

**Estado:** REWORK S1–S9 concluído; venv 3.12 recriado (stack leve). **Próxima ação (humano):** o aluno lê/edita
a tese e estuda pelo Caderno de Defesa; decidir extensão (66 pp vs ~90–120, sem encher); confirmar declaração ISEP.

---

## Sessão 18 — 2026-06-21 — Avaliação: ablação de modelo de embeddings
**Objetivo:** reforçar a avaliação da recuperação com a ablação prevista no design (§2: "modelo de
embeddings, 1 alternativo"), mostrando que a vantagem do SBERT não depende de um modelo específico.

**Feito:**
- **`evaluate.py` generalizado** para comparar uma lista de modelos SBERT (`--sbert-models`), com
  tabela e figura dinâmicas (N métodos). Mantém multi-seed (média ± desvio).
- **Ablação corrida** (MiniLM vs MPNet, 5 seeds): P@5 — **SBERT-MiniLM 0,549±0,014**,
  **SBERT-MPNet 0,569±0,009**, lexical 0,359, aleatório 0,241, recência 0,105. Ambos os modelos
  batem largamente os baselines; o MPNet (maior) dá um ganho modesto. **Conclusão: a vantagem é uma
  propriedade dos embeddings semânticos, não de um modelo específico.**
- **Cap. 6 atualizado**: tabela com as duas linhas SBERT + nota da ablação; figura regenerada
  (5 métodos). `learning.md` §14 atualizado. Tese compila 53 pp., 0 citações indefinidas.

**Estado dos testes:** **41 verdes** + 2 *gated*; lint limpo.

**Próxima ação:** (humano/opcional) revisão do aluno; FNSPID completo (job de noite na máquina do
aluno) → impacto (Pergunta B); estudo humano de utilidade (RQ3).

---

## Sessão 17 — 2026-06-21 — FNSPID: correção do downloader + achado de viabilidade
**Objetivo:** o aluno aprovou o download completo do FNSPID → tentar construir a KB multi-ano e a
análise de impacto (Pergunta B).

**Feito (e descoberto):**
- **Bug real corrigido:** o `download_data.py` usava `pd.read_csv(url)`, que **bloqueia** neste
  endpoint do Hugging Face (confirmado: pendurou várias vezes). Reescrito para fazer *stream* via
  `requests` (stream=True) + `pd.read_csv(resp.raw, ...)`, lendo só 3 colunas (`usecols`) e com
  **paragem antecipada** por ordenação de ticker (`early_stop`). **Verificado**: extraiu 379 notícias
  reais da Agilent (ticker `A`) 2018-2023 e parou cedo, corretamente.
- **Achado de viabilidade (honesto):** débito medido ~1.300 linhas/s; o ficheiro tem ~15M linhas →
  **~3,4 h para o varrer todo**. Os 15 tickers vão de `A` a `X`, logo não há atalho por ordenação;
  uma tentativa com 4 tickers (AAPL/AMZN/BAC/CVX) não completou um único chunk de 100k em 3,5 min.
  Conclusão: o scan completo do FNSPID **não é praticável neste ambiente** — é um job para a máquina/
  ligação do aluno (ex.: durante a noite).
- **Decisão honesta:** mantém-se a avaliação do Cap. 6 com a KB **real do Finnhub** (3.692 notícias,
  multi-seed); o FNSPID multi-ano fica como **trabalho futuro reprodutível** (script agora pronto e
  verificado). A tese já descrevia isto, por isso não precisou de alteração.
- Documentado em `download_data.py` e `docs/data_card.md`; artefactos de teste limpos.

**Estado dos testes:** **41 verdes** + 2 *gated*; lint limpo.

**Próxima ação:** (humano) correr `download_data.py` numa ligação adequada → `build_kb.py --sbert` →
análise de impacto (Pergunta B). Restante: revisão do aluno; declaração ISEP; estudo de utilidade.

---

## Sessão 16 — 2026-06-21 — Rigor da avaliação: multi-seed + teste de fidelidade
**Objetivo:** remover duas limitações declaradas no Cap. 6 — o resultado de recuperação com uma só
seed e a afirmação de fidelidade não automatizada — sem o download pesado do FNSPID.

**Feito:**
- **Robustez multi-seed:** `scripts/evaluate.py` corre agora 5 amostragens (seeds 42–46) e reporta
  **média ± desvio**. P@5: SBERT **0,549±0,014** | lexical 0,359±0,010 | recência 0,105±0,013 |
  aleatório 0,241±0,004. Os desvios ~0,01 confirmam que a vantagem do SBERT é robusta (separação de
  >20 desvios face ao acaso), não um artefacto da amostra. (A seed única anterior dava 0,568, ~1,3
  desvios acima da média — honesto reportar agora a média.)
- **Fidelidade automatizada (XAI/RQ3):** novo teste em `test_explainer.py` assegura que o texto do
  alerta reproduz exatamente a data, o ticker e o score de cada precedente recuperado e não introduz
  nenhum que não tenha sido recuperado — a fidelidade deixa de ser só "por construção" e passa a ser
  verificada por teste.
- **Tese atualizada:** Cap. 6 (tabela mean±std + secção de fidelidade com a nota do teste), Cap. 7
  (números da RQ2) e abstract EN/PT (0,55 vs 0,24); removida a limitação de "single seed". Compila
  53 pp., 0 citações indefinidas.

**Estado dos testes:** **41 verdes** + 2 *gated*; lint limpo.

**Próxima ação:** sobretudo humano/opcional — revisão do aluno; (opcional técnico) FNSPID completo →
KB multi-ano → análise de impacto (Pergunta B); estudo humano de utilidade (RQ3). Autónomo (D-009).

---

## Sessão 15 — 2026-06-21 — Escrita: Cap. 7 (Conclusion) + abstract + remoção de \nocite{*}
**Objetivo:** fechar o rascunho da tese — escrever a conclusão, refinar o abstract com os resultados
e remover a inclusão temporária de todas as referências.

**Feito:**
- **Cap. 7 (Conclusion)** redigido (EN-GB): respostas explícitas às três research questions com os
  resultados reais --- RQ1 (deteção transparente: afirmativo, com a consistência da taxa de disparo),
  RQ2 (precedentes análogos sem lookahead: afirmativo para a recuperação; impacto multi-ano = futuro),
  RQ3 (explicações fiéis por construção; utilidade por validar com estudo humano); contribuições
  revisitadas (engenharia de IA); limitações honestas; trabalho futuro mapeado nas limitações.
- **Abstract (EN, ~185 palavras, <=200)** e **resumo (PT)** refinados: acrescentam os resultados reais
  (recuperação SBERT supera baselines; detetor com taxa de disparo consistente) e a nota anti-lookahead.
- **`\nocite{*}` removido:** verifiquei que o conjunto de chaves citadas no texto é exatamente igual ao
  do `references.bib` (16 refs), pelo que a bibliografia renderiza as 16 sem nenhuma citação indefinida.
- **Tese compila: 53 páginas, 0 erros, 16 refs, 0 citações indefinidas**; `main.pdf` atualizado.
  **Rascunho completo dos 7 capítulos.**

**Estado dos testes:** **40 verdes** + 2 *gated*; `verify.sh` ok.

**Próxima ação:** sobretudo humano/opcional --- revisão e edição do aluno a todos os capítulos (o texto
é dele, §6.6); confirmar a redação ISEP da declaração de IA e a data de entrega; tecnicamente (opcional):
FNSPID completo → KB multi-ano → reavaliar impacto, e um pequeno estudo humano de utilidade (RQ3).

---

## Sessão 14 — 2026-06-21 — Escrita: Capítulo 5 (Implementation)
**Objetivo:** documentar a engenharia construída (a contribuição de engenharia de IA), sem repetir a
justificação metodológica do Cap. 4.

**Feito:**
- **Cap. 5 redigido** (EN-GB): ambiente e tooling (Python 3.12, lockfile de 72 pacotes, torch CPU,
  testes gated telegram/sbert, `verify.sh`, CI, scan de segredos); estrutura do repositório com uma
  **tabela de módulos** (componente→módulo→elementos) e **3 princípios** — (i) fatia fina end-to-end
  primeiro, (ii) lógica pura separada de I/O com imports tardios (parsing vs HTTP), (iii) programar
  contra interfaces (`Embedder` com `HashingEmbedder`/`SbertEmbedder`); pipeline da KB (alinhamento
  anti-lookahead no código, streaming do FNSPID ~23 GB, KB Finnhub usada na avaliação); camada live;
  detetor; motor de correlação; explicação fiel por construção; orquestração (`run_thin_slice`,
  `run_news_trigger`) e entrega; testes e reprodutibilidade.
- Citações `dong2024fnspid`, `reimers2019sbert`, `araci2019finbert`; referência ao diagrama
  `fig:architecture` e ao Cap. 6.
- **Tese compila: 53 páginas, 0 erros**, sem referências indefinidas; `main.pdf` atualizado.

**Honestidade:** não inventei capacidades — agendamento/deploy explicitamente fora de âmbito; a KB
completa do FNSPID continua como trabalho futuro (a avaliação usou a KB Finnhub real).

**Estado dos testes:** **40 verdes** + 2 *gated*; lint limpo.

**Próxima ação:** Cap. 7 (Conclusion); abstract <=200 palavras; remover `\nocite{*}` após confirmar
que o texto cita as 16 referências. Autónomo (D-009).

---

## Sessão 13 — 2026-06-21 — Escrita: Capítulo 6 (Evaluation)
**Objetivo:** escrever o Cap. 6 assente nos resultados reais já produzidos (zero fabricação), com
tabelas, as figuras reprodutíveis e um estudo de caso ponta-a-ponta real.

**Feito:**
- **Cap. 6 redigido** (EN-GB) com seis secções: setup experimental; detetor de anomalias
  (consistência da taxa de disparo como argumento principal + P/R/F1 + ablação à janela);
  motor de correlação (precision@k cross-ticker + baselines + medição de impacto); qualidade da
  explicação (fidelidade por construção; rubrica humana assumida como limitação/futuro); estudo de
  caso; discussão e limitações honestas.
- **2 tabelas** (taxa de disparo; precision@k) + **2 figuras** reprodutíveis já geradas; citações
  metodológicas (`chandola2009anomaly`, `brown1985daily`, `reimers2019sbert`, `arrieta2020xai`).
- **KB SBERT real** construída de 3.692 notícias Finnhub + preços yfinance (2.964 registos);
  estudo de caso real: consulta "Nvidia raises guidance on AI data-centre accelerators" recupera 5
  precedentes todos temáticos de Nvidia/AI-chips, vindos de feeds de empresas diferentes (META, BAC,
  AMZN) → prova de recuperação por significado, não por nome/keyword.
- **Honestidade:** descobri que o Finnhub free só devolve ~1 mês de notícias (não o ano pedido);
  corrigi o texto do setup; impactos `n/a` em notícias muito recentes (janela além dos preços
  disponíveis) — assumido e motiva o FNSPID multi-ano como trabalho futuro.
- **Tese compila: 51 páginas, 0 erros**, sem referências indefinidas nem figuras em falta;
  `thesis/main.pdf` atualizado e versionado.

**Estado dos testes:** **40 verdes** + 2 *gated*; lint limpo.

**Próxima ação:** escrever o Cap. 5 (Implementation) com a arquitetura construída; depois Cap. 7
(Conclusion), abstract <=200 palavras e remoção do `\nocite{*}`. Autónomo (D-009).

---

## Sessão 12 — 2026-06-21 — Avaliação: detetor de anomalias (Pergunta 1) em preços reais
**Objetivo:** dar ao detetor de anomalias uma avaliação real e honesta (a par da recuperação),
para o Cap. 6 assentar em DUAS experiências quantitativas.

**Feito:**
- **Métrica** (`src/evaluation/anomaly_eval.py`, puro, 6 testes): `rolling_zscore_flags` (sem
  lookahead), `fixed_threshold_flags` (baseline), `label_extreme_moves` (rótulo-proxy por percentil),
  `precision_recall_f1`, `firing_rate`.
- **Argumento principal (não circular): consistência da taxa de disparo entre tickers.** Em preços
  reais (yfinance, 3 anos, 15 tickers): amplitude da taxa **z-score 0,017 vs limiar fixo 0,343** —
  o limiar fixo dispara ~1% na KO e ~35% na TSLA/NVDA; o z-score ~2% em todos (normaliza
  volatilidade). Suporte: **F1 z-score 0,524 vs fixo 0,216** (rótulo-proxy); ablação à janela
  10/20/60d → F1 0,385/0,524/0,687. Resultados em `docs/evaluation_anomaly.md`; figura
  `thesis/figures/eval_anomaly_firing_rate.pdf`.
- Docs: `learning.md` §15 (com nota de defesa e caveat de circularidade do rótulo).

**Honestidade:** o rótulo-proxy é volatilidade-relativo como o z-score (alguma circularidade),
por isso o argumento central é a consistência da taxa de disparo, que não depende do rótulo.

**Estado dos testes:** **40 verdes** + 2 *gated*; lint limpo; `verify.sh` ok.

**Próxima ação:** escrever o Cap. 6 (Evaluation) integrando recuperação + anomalias (tabelas, as 2
figuras, caveats) e um estudo de caso ponta-a-ponta; depois Cap. 5 (Implementation). Autónomo (D-009).

---

## Sessão 11 — 2026-06-21 — Avaliação: recuperação de precedentes (Pergunta A) em dados reais
**Objetivo:** produzir resultados de avaliação **reais e honestos** para a peça central da tese
(o motor de correlação), sem o download de 23 GB do FNSPID, usando a fonte real e gratuita já
validada (Finnhub).

**Feito:**
- **Métrica** (`src/evaluation/retrieval_eval.py`): **precision@k por setor** em recuperação
  **cross-ticker** (exclui a própria empresa → testa analogia temática, não o nome). Baselines
  **aleatório** (taxa-base exata) e **recência**. Puro NumPy, determinístico, 5 testes.
- **Dados reais** (`scripts/fetch_finnhub_news.py`): **3.692 notícias** dos 15 tickers (Finnhub,
  ~250 recentes/ticker; 5 setores). Gitignored; amostra versionada.
- **Ablação** (`scripts/evaluate.py`): embeddings SBERT vs HashingEmbedder (lexical), 500 consultas
  (seed 42). **P@5 — SBERT 0,568 | lexical 0,357 | aleatório 0,245 | recência 0,096**
  (P@10 — 0,533 / 0,328 / 0,245 / 0,077). O SBERT está ~2,3× acima do acaso e claramente acima do
  baseline lexical → **a hipótese central (recuperação semântica encontra precedentes mais
  análogos) verifica-se em dados reais.** Resultados em `docs/evaluation_results.md`; figura
  reprodutível em `thesis/figures/eval_retrieval_precision.pdf`.
- Docs: `learning.md` §14, `glossary.md` (P@k, taxa-base, lift, cross-ticker), `data_card.md`.

**Honestidade:** o setor é um *proxy* automático (não julgamento humano); dados recentes do
Finnhub (não o histórico multi-ano do FNSPID); títulos curtos limitam a semântica. Resultados
**preliminares**, reprodutíveis com seed fixa — explicitamente assumido nos caveats.

**Estado dos testes:** **34 verdes** + 2 *gated*; lint limpo; `verify.sh` ok.

**Próxima ação:** escrever o Cap. 6 (Evaluation) com estes resultados (tabela + figura + caveats)
e o detetor de anomalias; depois Cap. 5 (Implementation). Opcional: FNSPID completo (R2) para uma
avaliação multi-ano mais rica. Prosseguir autonomamente (D-009).

---

## Sessão 10 — 2026-06-21 — Implementação: Gatilho 2 (notícias) + explicação com precedentes
**Objetivo:** fechar o ciclo XAI do segundo gatilho — de uma notícia nova até um alerta com
precedentes históricos — escolhendo isto (em vez do download pesado do FNSPID) por dar mais valor
visível por minuto.

**Feito:**
- **`news_fetcher`** (`src/news_fetcher/fetcher.py`): `NewsItem` (mesmo esquema da KB); parsing
  **puro e testado** (`parse_finnhub_news`, `parse_rss`, `_rss_date_to_iso`) separado do HTTP fino
  e tardio (`fetch_finnhub_company_news`, `fetch_rss_feed`). **Finnhub validado ao vivo** — 247
  notícias da AAPL na última semana, parseadas corretamente.
- **Explicação com precedentes** (`explain_news_impact`): alerta rastreável com a notícia, o
  impacto médio observado em eventos análogos (horizonte configurável), a lista de precedentes
  (data, ticker, similaridade, impacto, título) e a nota de que **é resultado passado, não
  previsão** (restrição §5.2). Média ignora NaN.
- **Orquestração** (`run_news_trigger` em `src/main.py`): notícia → embedding → `KB.find_precedents`
  → explicação → (opcional) Telegram. Por defeito usa a KB-amostra + `HashingEmbedder` (offline,
  testável); aceita `SbertEmbedder` + KB SBERT.
- **Testes:** `test_news_fetcher.py` (3), `test_explainer.py` (3, incluindo média que ignora NaN),
  e um smoke offline do Gatilho 2 ponta-a-ponta. Total **29 verdes** + 2 *gated* (telegram, sbert).
- Docs: `learning.md` §12 (Gatilho 2) e `glossary.md` (Gatilho 2, RSS, Finnhub).

**Notas:** os componentes do Gatilho 2 estão todos validados (Finnhub ao vivo; parsing e explicação
por testes; orquestração por smoke). Falta a demo **ao vivo** ponta-a-ponta com a KB SBERT completa
(depende do download real do FNSPID — job longo, R2) e a avaliação (Cap. 6).

**Próxima ação:** correr o download real do FNSPID + KB SBERT completa; depois demo Gatilho 2 ao
vivo (Finnhub → KB → Telegram) e iniciar a avaliação. Prosseguir autonomamente (D-009).

---

## Sessão 9 — 2026-06-21 — Implementação: KB histórica + motor de correlação (recuperação)
**Objetivo:** construir o núcleo da correlação notícia–mercado — a base de conhecimento histórica e a
recuperação de precedentes por similaridade — seguindo "a versão mais simples e defensável primeiro".

**Feito:**
- **Similaridade** (`src/correlation_engine/similarity.py`): cosseno (1D e vetorizado) + `top_k_similar`,
  puro NumPy, determinístico (7 testes).
- **Base de conhecimento** (`src/historical_kb/`): `NewsRecord` (data, ticker, título, impacto, embedding;
  JSON); interface `Embedder` com duas implementações intermutáveis — `HashingEmbedder` (baseline lexical
  determinístico, **sem dependências** → permite testar tudo sem torch e serve de baseline para ablação) e
  `SbertEmbedder` (SBERT real, import **tardio**); `HistoricalKB` com `build/save/load/find_precedents`
  (persistência JSONL).
- **Decisão de engenharia (anti-lookahead na prática):** dia do evento = 1.º dia de negociação ≥ data da
  notícia; impacto medido a partir do **fecho** desse dia → não capta o salto já refletido na abertura
  (ex.: NVDA 2023-05-25). Documentado em `learning.md` §11.
- **Scripts reais:** `download_data.py` (FNSPID em **streaming** por chunks + filtro ticker/janela — não
  descarrega os ~23 GB; só o subconjunto fica em disco, gitignored, + amostra de títulos) e `build_kb.py`
  (notícias CSV + preços yfinance, índice tz-naive → KB JSONL; `--sbert` para SBERT real).
- **Validação ponta-a-ponta:** criada amostra **sintética** `data/samples/news_sample.csv` (não são notícias
  reais); corrido `build_kb.py` com preços reais (yfinance) → `data/samples/kb_sample.jsonl` (10 registos).
  Impactos coerentes com a realidade (TSLA −9,75% após margens Q1; MSFT +7,2% após cloud).
- **Fonte FNSPID verificada** (honesto, não fabricado): probe controlado confirmou HTTP 200, `text/csv`,
  **~23,2 GB**, colunas `Date/Article_title/Stock_symbol` → mapeamento do `download_data.py` correto.
- Docs: `learning.md` (§11–12), `glossary.md` (KB, embedder, baseline, ablação, JSONL, streaming, top-k),
  `data_card.md` (pipeline implementado + schema verificado), `data/samples/README.md`.

**Estado dos testes:** **22 verdes**; lint limpo (src+tests+scripts); `verify.sh` ok.

**Notas técnicas:** `build_kb.py` precisou de bootstrap do `sys.path` (correr como script) e de reconfigurar
o stdout para UTF-8 (consola Windows cp1252 não imprimia acentos/glifos). A stack ML pesada **continua por
instalar** — o `SbertEmbedder` está pronto mas por validar (próximo passo).

**Próxima ação:** instalar a stack ML faseada e validar o `SbertEmbedder`; correr o download real do FNSPID
(job longo, R2) e construir a KB completa; depois `news_fetcher` (Gatilho 2) e a explicação com precedentes.
Prosseguir autonomamente (D-009).

**(cont.) Stack ML + validação do SBERT:** instalada a stack pesada — torch 2.12.1+cpu (índice CPU dedicado),
sentence-transformers 5.6.0, transformers 5.12.1, huggingface-hub 1.20.1, scikit-learn 1.9.0; `requirements.txt`
atualizado e `requirements.lock.txt` regenerado (72 pacotes; numpy/pandas inalterados). **`SbertEmbedder`
validado** com teste *gated* `-m sbert`: uma consulta semanticamente próxima mas **sem palavras em comum**
("Graphics processor maker lifts outlook on AI accelerator sales") recupera corretamente a notícia da NVIDIA
sobre chips de IA como top-1 (similaridade > 0,3) — a vantagem do SBERT sobre o baseline lexical, demonstrada.
Corrigido um `FutureWarning` (método de dimensão renomeado no ST 5.x; agora suporta 4.x e 5.x). Testes:
22 verdes por defeito + 2 *gated* (telegram, sbert).

---

## Sessão 8 — 2026-06-21 — Implementação: Thin slice (M1) + pedidos do aluno
**Objetivo:** desbloquear com o setup do aluno e construir a fatia fina end-to-end.

**Setup confirmado:** Python 3.12.10 instalado; `.env` completo (Telegram token+chat id, Finnhub/AlphaVantage/GNews).
Criado o venv canónico 3.12 + `requirements.lock.txt` (42 pacotes). `yfinance==1.4.1` adicionado.

**Pedidos do aluno tratados:**
- **Autonomia máxima (D-009):** alargado `.claude/settings.json` (allowlist amplo + denylist dos perigosos);
  deixo de usar AskUserQuestion para confirmações de rotina; registado em CLAUDE/DECISIONS + memória `max-autonomy`.
- **Declaração de uso de IA:** **recusei** a versão pedida para "não parecer que usei muito" (seria enganosa e contra
  §2.2/§6.8, e é o que mais o prejudicaria numa defesa). Escrevi uma versão **honesta e digna** no front matter
  (IA auxiliou escrita/edição do texto e desenvolvimento de software; o aluno dirigiu, reviu e é responsável).
  Memória `honest-ai-declaration`. Falta o aluno confirmar a redação exata exigida pela ISEP.
- **`main.pdf` no repo:** `scripts/build_pdf.sh` compila e versiona `thesis/main.pdf` (visível no repositório).

**Thin slice (M1):** pipeline Gatilho 1 — `market_data` (yfinance, log-returns) → `anomaly_detector`
(z-score sem lookahead, `AnomalyResult`) → `explanation_engine` (regra transparente) → `telegram_bot` (Telegram API).
`src/config.py` (.env), `src/main.py` (`run_thin_slice`). Testes unitários (4) + smoke (pipeline + envio Telegram
marcado `@telegram`, excluído do verify por defeito). **Envio real confirmado**; caminho live yfinance validado (AAPL,
hoje sem anomalia z=+0.47). Verify verde (6 testes, lint limpo).

**Próxima ação:** componentes — `historical_kb`/FNSPID (`data_card.md`), depois `correlation_engine` (instalar stack
ML faseada) e Gatilho 2 (notícias). Prosseguir autonomamente (D-009).

---

## Sessão 7 — 2026-06-21 — Escrita: Capítulo 4 (Methodology)
**Objetivo:** redigir a metodologia com diagrama de arquitetura.

**Feito:**
- **Cap. 4 redigido** (rascunho EN-GB): (4.1) arquitetura + **diagrama TikZ** (`fig:architecture`, reprodutível);
  (4.2) 2 camadas de dados; (4.3) deteção de anomalias com a **equação do z-score** [Chandola; contraste Isolation
  Forest]; (4.4) motor de correlação [SBERT + cosseno + event-study; Brown & Warner; FNSPID]; (4.5) explicação XAI
  [SHAP; Arrieta/Adadi; FinBERT opcional]; (4.6) design de avaliação; (4.7) rigor (anti-lookahead, reprodutibilidade).
- Habilitadas bibliotecas TikZ (`positioning`, `arrows.meta`) no `main.tex`. Compila: **47 páginas, 0 erros, 16 refs**.
- **Marco:** concluídos os 4 capítulos que se podem escrever honestamente antes de o sistema existir.

**Boundary importante:** Caps. 5 (Implementation), 6 (Evaluation) e 7 (Conclusion) só depois de construir/avaliar
o sistema (sem fabricação). Próximo bloco real = implementação (thin slice), que precisa de Python 3.12, token
Telegram e chaves de APIs (ações humanas).

**Próxima ação:** decisão do aluno — começar implementação (após setup humano) ou rever/polir Caps. 1–4.

---

## Sessão 6 — 2026-06-21 — Escrita: Capítulo 3 (Literature Review)
**Objetivo:** redigir a revisão de literatura com tabelas comparativas (§6.2).

**Feito:**
- **+5 referências verificadas** (Crossref/arXiv): Liu et al. 2008 (Isolation Forest), Ribeiro et al. 2016 (LIME),
  Devlin et al. 2019 (BERT), Mikolov et al. 2013 (word2vec), Yang et al. 2020 (FinBERT). Total: **16 refs**.
- **Cap. 3 redigido** (rascunho EN-GB): (3.1) deteção de anomalias [Chandola, Isolation Forest]; (3.2) XAI
  [LIME, SHAP, surveys]; (3.3) NLP financeiro [word2vec, BERT, SBERT, FinBERT]; (3.4) event study [Brown & Warner]
  + FNSPID; (3.5) análise comparativa/posicionamento; (3.6) lacunas. Cada obra com o quê/como/limitações.
- **4 tabelas comparativas** (anomalias; XAI; representações de texto; escolhas vs. alternativas).
- Compila: **45 páginas, 0 erros, 16 referências** (6 overfull triviais 2–6pt, para polir na revisão).

**Próxima ação:** Cap. 4 (Methodology), com diagrama de arquitetura (figura reprodutível).

---

## Sessão 5 — 2026-06-21 — Escrita: Capítulo 1 (Introduction)
**Objetivo:** redigir a Introduction, fundacional e apoiada no Cap. 2.

**Feito:**
- **Cap. 1 redigido** (rascunho EN-GB): motivação (com stats do Cap.2 citadas), enunciado do problema (explicação,
  não previsão), **3 research questions (RQ1 deteção transparente; RQ2 correlação/precedentes sem lookahead vs.
  baselines; RQ3 explicações fiéis e úteis)**, contribuições (enquadramento de Engenharia de IA: integrar/aplicar/
  avaliar; metodologia documentada de correlação notícia–impacto; pipeline XAI-first), e estrutura do documento.
- Referências cruzadas (`\ref` aos capítulos) e citações verificadas (Gallup, SIFMA, CCAF, Arrieta, Adadi).
- Compila: **43 páginas, 0 erros, 11 referências**.

**Próxima ação:** Cap. 3 (Literature Review) — tabelas comparativas + ampliar citações verificadas.

---

## Sessão 4 — 2026-06-21 — Escrita: Capítulo 2 (Contextualization)
**Objetivo:** redigir o capítulo de contextualização com dados US 2025–2026 reais e verificados.

**Feito:**
- Investigação web + **verificação em fonte primária** de 3 fontes: SIFMA 2025 Fact Book (cap. ações US =
  $62,2T, 49,1% do global, 5,3× a China; valor extraído do PDF), Gallup 2025 (62% dos americanos detêm ações),
  CCAF 2026 (81% adoção de IA, 40% avançada, 71% GenAI). Registadas em `citation_log.md` + `references.bib`.
- **Cap. 2 redigido** (rascunho EN-GB): mercado US (NYSE/NASDAQ), panorama do retalho, IA em finanças +
  necessidade de XAI, e o problema de sobrecarga de informação. Cada afirmação citada.
- **1.ª figura reprodutível** (§6.7): `scripts/figures/fig_us_market_cap.py` (matplotlib) gera
  `thesis/figures/us_equity_market_cap.pdf` (capitalização US 2015–2024). Pipeline de figuras estabelecido.
- Adicionado acrónimo SIFMA; termos no `glossary.md`. Compila: **43 páginas, 0 erros, 11 referências**.

**Próxima ação:** Cap. 1 (Introduction) e Cap. 3 (Literature Review). Rever Cap. 2 (fonte da quota de retalho).

---

## Sessão 3 — 2026-06-21 — Fase D (Setup LaTeX)
**Objetivo:** integrar o template ISEP em `thesis/` e garantir compilação.

**Feito:**
- Template ISEP copiado para `thesis/` (classe `meia-style.cls`, `frontmatter/`, `appendices/`, assets) e criados
  `ch1..ch7/`. `main.tex` adaptado: título **T1**, autor, nº 1180934, orientador Luís Gomes, coorientador Rafael
  Silva, keywords; `\addbibresource{references.bib}`; `authoryear-comp` + biber; `makenoidxglossaries`.
- **7 capítulos** com estrutura de secções (Introduction · Contextualization · Literature Review · Methodology ·
  Implementation · Evaluation · Conclusion).
- `references.bib` com as **8 referências verificadas**; `latexmk.rc` criado (resolve o achado da Fase A);
  acrónimos próprios em `glossary.tex`; abstract (EN) + resumo (PT) em rascunho (exemplos do template removidos).
- **Compila localmente: 41 páginas, 0 erros**, biber OK, 8 refs no `.bbl` (só aviso cosmético de fonte).
- Correção: removido `\thesissubtitle{}` vazio (causava "There's no line here to end"). `\nocite{*}` temporário.

**Próxima ação:** gate da Fase D; confirmar compilação no CI após push; depois escrita (Sessão 4+).

---

## Sessão 2 — 2026-06-21 — Fase C (Planeamento e decisões técnicas)
**Objetivo:** planear o sistema e fechar decisões técnicas antes da Fase D.

**Feito:**
- **Título:** escolhido **T1** pelo aluno — *Explainable Financial Alerts for Retail Investors: Integrating
  Statistical Anomaly Detection and News–Market Impact Correlation* (D-008).
- **Arquitetura:** `docs/arquitectura_sistema.md` — diagrama de componentes, 2 camadas (histórica FNSPID vs.
  live), fluxos dos 2 gatilhos, thin slice, garantias XAI/anti-lookahead; **confirmada pelo aluno**.
- **Metodologias por componente** com **8 citações verificadas** (Crossref/arXiv, 2026-06-21) em
  `citation_log.md` + secção 9 da arquitetura: Chandola 2009, Brown & Warner 1985, Reimers & Gurevych 2019,
  Araci 2019, Lundberg & Lee 2017, Arrieta 2020, Adadi & Berrada 2018, Dong 2024. (MacKinlay 1997 rejeitada —
  sem DOI resolúvel.)
- **APIs gratuitas:** `docs/free_apis.md` (verificado 2026-06-21): yfinance+Finnhub (preços), Finnhub news+RSS
  (notícias), FNSPID (histórico), Telegram (alertas); Alpha Vantage só ocasional (25/dia).
- **Avaliação:** `docs/evaluation_design.md` detalhado (métricas, baselines, ablções, rubrica XAI).
- **Plano:** `progress/PLANO_SESSOES.md` detalhado (~30 sessões + buffer, marcos M1–M5).
- **Aprendizagem:** `learning.md` + `glossary.md` com os conceitos (z-score, embeddings, cosseno, event-study,
  XAI, lookahead, FinBERT, SHAP), cada um com nota de defesa.

**Próxima ação:** pausar no gate da Fase C; depois Fase D (integrar template ISEP em `thesis/`).

---

## Sessão 1 — 2026-06-20 — Fase A (Análise de ficheiros de referência)
**Objetivo:** analisar a dissertação de referência e o template ISEP (benchmark + regras LaTeX).

**Feito:**
- `docs/analise_referencia.md` — *Distributed Intelligent Management of Citizen Communities* (Rafael Silva, EN,
  feito em Word): **109 páginas**, 6 capítulos (Intro / State of the art / Methods & Materials / Implementation /
  Case Studies / Conclusion), front matter i–xv, **~170 referências** (autor-ano), **34 figuras + 6 tabelas**
  (concentradas em implementação e casos de estudo). Estilo claro/direto, estatísticas concretas, citações inline.
  Definidos alvos de benchmark para a nossa tese (dimensão, nº refs, ≥30 figuras, tabelas comparativas).
- `docs/analise_template_latex.md` — classe `meia-style.cls` (book, 11pt, EN, frente-e-verso), pacotes,
  `biblatex authoryear-comp` + `biber`, convenções de figuras/tabelas/algoritmos/código, glossário
  `makenoidxglossaries`, build via Makefile/latexmk. **Achado:** `Makefile` refere `latexmk.rc` inexistente
  (tratar na Fase D; CI não depende dele).

- **Benchmark alargado** (secção comparativa em `docs/analise_referencia.md`): analisadas as outras 3
  dissertações — Bruno Ribeiro (139pp, 40 fig, 13 tab, ~210 refs), Helder Pereira (133pp, 41 fig, 14 tab,
  ~200 refs, citação numérica), Joana Figueiredo (104pp, 20 fig, 5 tab, ~60 refs). Todas EN. Estrutura comum
  (Intro→Estado da arte/Literatura→…→Conclusão) valida o plano de 7 capítulos. Alvos refinados: ~110–120 pp.,
  ~30–40 figuras, ~8–14 tabelas, ~150–200 refs, `authoryear-comp`.

**Notas técnicas:** instalado `pypdf` no venv (gitignored) para extrair estrutura dos PDFs.

**Próxima ação:** pausar no gate da Fase A; depois Fase C (planeamento). Fase B já coberta pela Fase 0.

---

## Sessão 0 — 2026-06-20 — Setup & Authorization (Fase 0)
**Objetivo:** preparar o repositório 100% scaffolded e seguro antes de qualquer trabalho real.

**Feito:**
- Verificado o ambiente: Git 2.54, Node 24, Python 3.14.6 (sistema), MiKTeX (pdflatex, latexmk 4.88, biber 2.21);
  remote HTTPS `github.com/HS2000PT/DIMEIA.git`; Git Credential Manager configurado; repo sem commits.
- Decisões bloqueadas com o aluno: **EN-GB**, **Python 3.12**, **docs de aprendizagem em PT-PT**.
- Criados: permissões (`.claude/settings.json`), ignore/segredos (`.gitignore`, `.gitattributes`, `.env.example`),
  esqueleto §9, `CLAUDE.md`, `README.md`, ficheiros `progress/` e `docs/`, scripts de automação, `requirements.txt`,
  `.python-version`, workflow de CI, e teste placeholder.

**Decisões:** ver `DECISIONS.md` (EN-GB; Python 3.12; docs PT-PT; layout LaTeX nativo do template ISEP;
dependências ML faseadas; PDFs de referência gitignored).

**A precisar do aluno:** instalar Python 3.12; aprovar auth do GitHub no primeiro push; (mais tarde) bot Telegram,
chaves de APIs, política ISEP de uso de IA.

**Próxima ação:** pausar no gate da Fase 0 e confirmar com o aluno antes de iniciar a Fase A (análise de
referência + template).
