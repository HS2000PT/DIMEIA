# SESSIONS — Registo de sessões (continuidade)

Registo curto de cada sessão para garantir continuidade entre dispositivos.
A entrada mais recente fica no topo.

---

## Sessão 40 (fecho) — 2026-07-22 — Plano de 9 fases: F4/F7/F8/F9 na máquina do FNSPID + visuais
**Pedido:** "continue with the plan. i'm already on the best pc as well." (o aluno estava AGORA no
PC `C:\Users\henri` — o do corpus FNSPID + torch — o que DESBLOQUEIA a F4.) A meio, pediu mais
visuais: snapshots reais dos objetos de dados por todas as fases da IA + logos das tecnologias/APIs,
moderno/simples/jovem, em tese e apresentação.
- **F4 (7ae5390) — ablação RQ4-ext CORRIDA:** wiring aditivo `context_ext` (produção byte-idêntica);
  novo `train_triage_ext.py` (não toca models/ nem evaluation_triage.md); `build_dataset.py --ext`
  offline → 79.453 linhas. **Resultado honesto:** contexto v1 0,537 (≈ congelado 0,538); +5 features
  0,535 (Δ −0,002, nenhuma ajuda); só `ret_event_z` +0,001. A volatilidade já absorve o sinal — mesma
  lição do texto. → evaluation_triage_ext.md + figura + secção Cap. 5 + roadmap Eixo 1 ✅. +4 testes.
- **F7 (6f199e3):** Fig. 4.5 recapturada (Playwright) com a marca nova (logo/slogan/tema + notas
  abertura/fecho); figura do corpo aponta para a completa do apêndice; apêndice novo "Proof of Work"
  (cada número → comando → ficheiro congelado + evidência ao vivo). Tese 90 pp, 0 erros.
- **Visuais novos:** Fig. 3.2 "jornada dos dados" — 1 headline real (NVDA, embedding SBERT real) por
  RAW→CLEAN→REPRESENT(a fase "AI")→MEASURE; espelhada nos slides (775462a) e no guia (8f0291b, PT).
  + visual "Built with" (badges de nome por categoria — offline-safe) nos slides e guia. Slides 17→19,
  guia 73→76; ablação RQ4-ext adicionada ao Result 4 e ao guia.
- **F9 (106ed97):** `make_public_bundle.py` (git ls-files − internos; scan de segredos; --git = 1 commit;
  nunca faz push) + manifesto `public_bundle.md`. Testado: 210 ficheiros, 21 internos fora, scan limpo.
- **Gates:** 199 testes (+4) + ruff verdes; tese 90 pp/paper/slides 19/guia 76 = 0 erros; congelados
  byte-iguais; 0 fabricação. Commits sem trailer de co-autoria (convenção do projeto). Pendente = humano (licença,
  declaração ISEP, leitura final, publicar o bundle).
- **Adenda (25e1988) — o aluno reforçou "logos + snapshots dos dados":** (1) infraestrutura de LOGOS
  reais nos frames "Built with"/"Feito com" (`\techlogo`/`\glogo` + `\IfFileExists` → logo se o PNG
  existir em `slides/logos/`, senão badge; README com nomes+fontes). (2) **Tabela 3.4** na tese (+frame
  no guia, 77 slides): cada coluna que a triagem lê + valor real (NVDA) + que métrica usa que colunas.

---

## Sessão 39 — 2026-07-13 (noite) — Verificação ao vivo: o mercado ACORDOU
**Pedido:** "continue" (pós-sessão 38; máxima autonomia).
- **Confirmado nos logs reais do Actions** (API GitHub + credencial git local; sem `gh` neste PC):
  **1.º alerta de MERCADO de sempre** (13/07, NVDA −3,53% intradiário, z=−1,67 vs ±1,5,
  "notable") com Sector check (sector-wide), Possible explanation, dedup e envio Telegram —
  tudo da sessão 38 a funcionar em produção. Histórico: 44 alertas (43 news + 1 market).
- **Segredos:** ALPHAVANTAGE_API_KEY adicionada pelo aluno; TIINGO/POLYGON ainda vazios
  (CHECKLIST reescrito: robustez, não bloqueia — o yfinance respondeu nos runners hoje).
- **KB viva maturou cedo (13/07, previsto ~17/07):** 13 casos com impactos reais em
  live_kb.jsonl (JPM/NFLX 04-05/07 → 1.º dia de negociação 06/07), 1.043 pendentes,
  "13 caso(s) em uso" no retrieval.
- **Pós-validação corrida** (venv 3.12 deste PC): 33 decisões maturadas → precisão das
  mantidas 0,667 vs base 0,455, Brier 0,229 → live_monitoring.md regenerado.
- **Fica 1 confirmação pendente:** 1.º resumo diário (corrida ≥21h UTC de dia útil).
  Sem código tocado; CHECKLIST com 2 pendentes fechados.
- **Adenda 1 — chaves fechadas:** o aluno criou TIINGO/POLYGON às 19:10; workflow_dispatch
  via API às 19:27 confirmou os 3 segredos (`***`) e scan saudável; fallback fica de reserva.
- **Adenda 2 — Platt vs isotónica FEITO** (este PC é o do FNSPID): novo
  `scripts/evaluate_calibration_ext.py` reproduz o congelado 5/5 ao milésimo e mostra que a
  **Platt ganha/empata no Brier em todas as famílias** (ECE misto, margens pequenas) mesmo
  com 17.710 pts de calibração → `docs/evaluation/calibration_platt_vs_isotonic.md`;
  escolha da tese validada empiricamente; produção intocada. docs/README.md ressincronizado
  (+4 linhas de avaliação).

---

## Sessão 38 — 2026-07-13 — Tese: IA a fundo; produto: o mercado estava CEGO (não insensível)
**Pedido:** "improve a lot the thesis (AI part weak; workflows/examples/tables/justificações);
0 market events → more sensitive; app cleaner; recent data first; be critical; novas APIs ok."
- **Diagnóstico com provas:** 42 alertas reais, todos news, 0 market E 0 summary ⇒
  `collect_market_results` vazio SEMPRE (yfinance bloqueado no Actions, sem fallback; VM do
  intradiário nunca ligada). O limiar nunca foi o problema.
- **Produto:** cadeia de preços yfinance→Tiingo→Polygon→Stooq→AV (Stooq caiu: anti-bot PoW,
  testado ao vivo); intradiário também no Actions (a norma só precisa de dias completos);
  resumo cai para intradiário; threshold 1.5 COM severidade (notable/strong/extreme);
  linha "Sector check"; recência 120d; require_fresh_bar exposto.
- **App:** faixa "Market now" (lote único, fail-open), About curta, tema navy+esmeralda.
- **Ciência aditiva (congelados intactos):** LOF (F1 0,280, perde) + EWMA (F1 0,664 >
  rolling 0,516 — achado honesto, produção fica rolling, futuro validado); projeção PCA real;
  exemplo trabalhado META que reproduz o 54% enviado; funil real 944→42 (22:1).
- **Tese 78→86 pp, 0 erros:** equações (pooling/cosseno/LR/Platt/Brier), reconciliação
  raw-vs-market-adjusted, Platt-vs-isotonic, tabela do exemplo real (ch3); GARCH/LOF/FinBERT
  endurecidos (ch2); secção "The Life of One Alert" + funil + lição de deploy (ch4); CS1-ext
  + projeção + contribuições (ch5, CS3 intocado); EWMA no futuro (ch6); apêndice com a 1.ª
  figura ROTADA (pipeline completo, todos os gates); screenshot real novo (faixa + eventos).
- **Sync:** guia 73 slides; README/RELATORIO 189 testes/86 pp; free_apis/going_live/vm_watch;
  product_review Pass 8; CHECKLIST (chaves de preços = clique do aluno).
- **Gates:** 189 testes + ruff verdes; demo +6,46%; tese e guia 0 erros; dry-run validado.
- **Nota de ambiente:** este PC agora TEM 3.12+MiKTeX (venv criado); sessão 31 obsoleta.

## Sessão 37 — 2026-07-12 — Passe premium de UX: velocidade 10×, alertas para leigos
**Pedido:** "cleaner, faster, premium; upgrade the output; full critical review."
- **Velocidade (achado nº 1):** st.tabs renderizava as 10 abas a cada interação → seletor
  horizontal renderiza SÓ a empresa escolhida (~10× menos fetch/scoring; teste garante 1
  métrica por render). segmented_control rejeitado (bug de serialização no AppTest 1.41).
  Risco de fundo cacheado 10 min.
- **Alertas para leigos:** "Anomaly detected for TSLA (Tesla)" — nome de empresa em todos os
  headers (aditivo; fidelidade intacta); demo/how_to_run/guia sincronizados; CS3 congelado
  intocado. Resumo diário com hierarquia: movers um por linha, calmos numa linha "Quiet:".
- **Premium:** crosshair + hover "$Y · X"; default 1M; métrica "Tesla (TSLA)"; tabela de
  eventos só com o facto forte + expander "Full alert texts"; CTA Telegram na sidebar;
  About com "Get the alerts" no topo.
- **Lição:** AppTest engole SyntaxErrors (árvore vazia sem exceção) — diagnosticar com
  py_compile. Screenshot v4 → Fig. 4.5; tese/slides/guia recompilam 0 erros.
- **167 testes + ruff verdes.**

## Sessão 36 — 2026-07-12 — Dashboard final (a visão realizada) + identidade profissional
**Pedido:** "one tab per company; main = one very big chart with real-time movements and the
events signalized there (hover = details) + the same in a table below; the rest on another
page; read-only; better logo/slogan; guarantee always-online or an alternative."
- **App reescrita — 2 vistas:** 📊 Live (aba por empresa → gráfico grande 1D/5D/1M/6M com
  eventos do canal marcados na curva + tabela + risco RQ4 compacto; read-only) e ℹ️ About
  (tudo o resto + a única ação, a demo de retrieval, num expander). 8 AppTests novos.
- **Identidade:** logo.svg profissional (linha de mercado → "olho" vigilante) + slogan
  "Market intelligence, explained." (app + README).
- **Sempre-online honesto:** keep-alive no workflow (ping por corrida) + alternativa 24/7
  real na VM (archive/deploy/investigator-app.service, porta 8501; vm_watch.md §Bónus).
- **Screenshot real novo** (TSLA, marcadores visíveis) → Fig. 4.5 atualizada (frase+caption);
  tese 78 pp/slides 17/guia 71 recompilam 0 erros. Docs deployment/RELATORIO/README em sync.
- **167 testes + ruff verdes.**

## Sessão 35 — 2026-07-12 — Evolução "sensor-first": KB viva + investigação cruzada + intradiário
**Pedido:** o aluno partilhou uma visão ChatGPT (sistema por eventos, sensores, tempo quase-real)
e delegou a decisão. **Análise devolvida:** ~80% da visão JÁ é o sistema (2 gatilhos→motor único;
"priorização inteligente"=RQ4; "aprendizagem contínua"=M5.5); construído o delta genuíno,
rejeitados com razões a reescrita da tese, redes sociais e scores preditivos de "confiança".
- **V1 KB viva (e62cf56):** `investigator/live_kb.py` — manchetes relevantes capturadas (embedding
  na captura; summary só em memória, §5.4), maturadas ≥8d com preços reais → `live_kb.jsonl` na
  branch alerts-history; retrieval fundido com decaimento por idade (a sim mostrada é o cosseno
  real; idade visível "3y ago"); botões `recency_half_life_days`/`max_precedent_age_days`.
  846 pendentes capturados na 1.ª varredura real.
- **V2 investigação cruzada (a5fbf4a):** anomalia→notícia ("Possible explanation (Xh ago)" ou
  "no public explanation yet"); direção dos precedentes descritiva ("3 of 3 moved down — an
  observed pattern, not a forecast").
- **V3 intradiário (6ebb9f9):** cotação Finnhub em tempo real vs norma diária (mesmo z-score,
  sem lookahead) no --watch; wording "so far today"; bug real apanhado antes de produção
  (cotação estagnada ao fim de semana) → guarda `is_us_market_session`.
- **V4:** tese Cap. 6 +1 parágrafo (iteração pós-avaliação, avaliação formal=futuro; 78 pp,
  0 erros); guia 71 slides (+pergunta júri "KB desatualizada?"); product_review Pass 7
  (P-13/14/15); vm_watch/going_live/README/RELATORIO em sync. **167 testes + ruff verdes.**

## Sessão 34 — 2026-07-11 — Grande limpeza + qualidade dos alertas + quase-tempo-real + guia único
**Pedido:** "full repository cleanup… the product sucks… similarity not working… only news, no
market triggers… alerts on weekends… near real time… single study source". Diagnóstico com provas
(27 alertas reais do canal + logs do Actions) ANTES de mexer; plano aprovado em modo de planeamento.
- **Diagnóstico:** o Finnhub etiqueta lixo (escritório de advogados como "AMD"; "S&P500 movers"
  para vários tickers) e não havia filtro de relevância — a similaridade parecia má porque a
  ENTRADA era má; zero |z|≥2 nesses 2 dias + canal mudo em dias calmos; cron do GitHub na prática
  de 1,5-2h em 1,5-2h (medido); só TSLA/META/AMD passavam o gate (volatilidade domina o modelo).
- **F1 qualidade:** `investigator/news_fetcher/relevance.py` (menção obrigatória da empresa +
  rejeição de boilerplate — testado com os casos reais do canal); chão `news.min_similarity: 0.45`;
  aviso "⚠ BOTH directions" (a lição do CS3 no produto — P-3 implementado); teto 2 notícias/
  ticker/dia; P da triagem de cada ticker no log.
- **F2 presença de mercado:** resumo diário ao fecho (`build_daily_summary`, kind=summary no
  histórico e na app); crons alargados (manhãs úteis + fins de semana, só notícias — o mercado
  auto-salta via bar_is_fresh); dedup ENTRE produtores via histórico partilhado (campo `key`).
- **F3 quase-tempo-real:** `run_alerts.py --watch` (loop ~5 min, SIGTERM limpo) + push git
  opcional do histórico (INVESTIGATOR_HISTORY_GIT=1) + runbook `docs/design/vm_watch.md` +
  systemd + `archive/deploy/setup_vm.sh` — decisão do aluno: VM Oracle Free; cron fica de rede de segurança.
- **F4 limpeza:** APAGADOS (git preserva) ML_PLAN/PLANO_FINAL/PLANO_SESSOES (planos concluídos),
  editorial_review/review_log/implementation_review (auditorias one-off), start/end_session.sh,
  fnspid-overnight.bat/kb-fnspid.cmd; ARQUIVADOS caderno_de_defesa/guia_rapido/QUESTIONS/proposta_ml
  (absorvidos no guia). Referências ativas corrigidas; README com mapa "6 sítios"; CHECKLIST
  reescrito para SÓ o que falta; docs/README refeito.
- **F5 guia ÚNICO:** guia_estudo 64→**71 slides** (+guião oral 3 min e por-RQ, +2 frames de
  perguntas do júri, +mapa dos números congelados, +plano B; "Onde estudar" atualizado) — fonte
  única de estudo, 0 erros.
- **Validado:** 145 testes + ruff verdes; dry-run ao vivo com os filtros (lixo rejeitado no log,
  AAPL suprimida por precedente fraco, aviso de direção mista a aparecer, P de todos visível).
- **Achado para o aluno:** o deploy do Streamlit está PRESO num pull antigo (4 falhas "Updating
  the app files has failed" no log dele) — precisa de **Reboot app** manual (plotly ausente do
  ambiente é sintoma, não causa).

## Sessão 33 — 2026-07-09 — Redesenho de produto: painel único ao vivo
**Pedido:** feedback real após dias de uso — alertas de mercado raros, materialidade em jargão,
Streamlit "com muito lixo" e sem mostrar o modelo treinado; "we need hard changes and renew" +
pedido de um plano de vários dias + pergunta direta "fomos por um caminho errado?".
- **Resposta verificada:** não — a tese não prende nenhuma UI específica; pivô de produto, não de
  ciência. Entrei em modo de planeamento (2 Explore + 3 AskUserQuestion) antes de codificar.
- **Fixes imediatos:** threshold de mercado 3,0→2,0 (produção, divulgado); materiality_line em
  linguagem simples.
- **Fase 1:** `investigator/alerts_history.py` + branch de dados `alerts-history` — Telegram e
  Streamlit passam a ler o MESMO registo, nunca recalculam.
- **Fase 2:** app reescrita — painel único, aba por ticker, "Background risk" do modelo TREINADO
  (RQ4, novo `score_background`) todos os dias, gráfico Plotly anotado, histórico, "Method &
  evaluation" num expander. 2 bugs reais (IDs de gráfico duplicados; expander aninhado) apanhados
  pelos testes antes de produção; confirmado também com arranque real do servidor.
- **Fase 3:** `archive/streamlit-app/notebooks/investigator_walkthrough.ipynb` (anomalia+retrieval+modelo treinado),
  executado de ponta a ponta, 0 erros.
- **Fase 4:** screenshots reais (Playwright, servidor local) inseridos na tese (Fig. 4.5, 78 pp),
  slides (17 pp) e guia (64 pp) — 0 erros em todos; documentação toda sincronizada.
- **132 testes + ruff verdes** em todas as fases. Pendente não-bloqueante: confirmar a branch
  `alerts-history` a receber o 1.º registo real (clique do aluno ou corrida agendada de amanhã).

## Sessão 32 — 2026-07-07 — Retrieval SEMÂNTICO na nuvem (MiniLM em ONNX) — produto fechado
**Pedido:** "continue with the pendings and plan" → o último pendente de código do CHECKLIST.
- **Novo `investigator/historical_kb/onnx_embedder.py`:** o MESMO `all-MiniLM-L6-v2` da tese em
  ONNX quantizado (~23 MB; `onnxruntime==1.27.0` + `tokenizers`, sem torch), download sob demanda
  com **SHA256 pinado**, cache `models/onnx/` gitignored; pipeline igual ao sentence-transformers
  (truncation 256, mean pooling com máscara, L2).
- **KB do produto recurada a 384-d:** `curate_kb_light.py --sbert-kb` reutiliza os embeddings da
  KB grande (79.753) → 2.016 registos versionados (7,7 MB; arredondados a 5 casas).
- **Validação (docs/evaluation/onnx_minilm_validation.md):** cosseno ONNX↔SBERT médio 0,992
  (mín 0,987; 63 manchetes reais); top-3 idênticos 20/23, 96 % vizinhos comuns; recall TSLA →
  precedente NTSB exato (sim 0,73).
- **Fail-open:** `product_retrieval()` (main.py) — sem modelo degrada para a amostra word-overlap
  e a UI di-lo; uma KB 384-d NUNCA é consultada por hashing (levanta). App: `st.cache_resource`;
  testes com `INVESTIGATOR_OFFLINE=1` (conftest novo) — nunca descarregam. Workflow Alerts com
  cache do modelo (chave `onnx-minilm-quint8-v1`).
- **Gates:** 117 testes (+7/+atualizado e2e) + ruff verdes; demo +6,46% intacta; dry-run ao vivo
  com precedentes genuinamente on-topic (AMD→TSMC/semis 0,51–0,55). Tese intocada (verificado:
  só refere o baseline lexical na avaliação).
- **⚠️ Achados operacionais:** a app do Streamlit **voltou a privada** após o redeploy (anónimo →
  login) — item reaberto no CHECKLIST (clique humano); Alerts correu 2× hoje com sucesso (o GitHub
  salta crons de 30 min sob carga — best-effort, documentado).

### Sessão 32 — adenda FECHO ("organize everything and put an end to this")
- **Sync Telegram↔Streamlit:** "Markets now" ganhou "Today's alerts (as sent to the Telegram
  channel)" — mesmo detetor, config e texto (`plain_text(explain_anomaly)`); AppTest exige a secção.
- **`archive/reports/RELATORIO_FINAL.md` (raiz):** relatório de 10 min para o orientador (tudo o que existe + mapa
  do repo + números verificados + o que falta).
- **Guia de estudo em 2 camadas:** 64 slides atualizados (ONNX/paridade/intradiário; 0 erros) +
  NOVO `docs/defence/guia_rapido.md` (versão de bolso; números todos verificados contra os
  ficheiros congelados).
- **`docs/design/migrar_repo.md`:** repo novo sem história — procedimento + trade-offs honestos
  (minutos do Actions em privado; religação Streamlit/badges; tese verificada sem URLs). Nada
  migrado — decisão/cliques do aluno.
- Veredicto de submissão dado: tecnicamente pronto; falta só o lado humano (leitura final,
  licença+declaração IA, app pública, pin do canal, post_validate 08-09/07).

## Sessão 31 — 2026-07-07 — HOTFIX Cloud: Live board (registo retroativo; detalhe no CLAUDE.md)
`TypeError` no Streamlit Cloud quando o yfinance falhava para TODOS os tickers (coluna z-score
toda `None` → `sort_values(key=s.abs())` rebentava). Fix `pd.to_numeric(...).abs()` + teste de
regressão provado contra o código antigo; verificado também com pandas 3.0.2 (stack do Cloud).
Commits `ab14cda`/`6cd8c2e`; canal público no alerts.yaml (`df7a714`).

## Sessão 30 — 2026-07-06 — PRODUTO REAL + SINCRONIA TOTAL para a defesa

### Sessão 30 — adenda REVISÃO DURA (mensagens + usabilidade; "pasta de palavras; amador")
Crítica aceite e verificada contra os artefactos reais (imprimi as mensagens como o utilizador
as recebe). **Mensagens Telegram reescritas em camadas** com HTML (negrito na manchete, método
em itálico curto; sender parse_mode + fallback; escapes em todo o conteúdo dinâmico): mercado
5→3 linhas sem repetição; notícia com INTERVALO antes da média (média sozinha esconde direções
mistas — a lição do CS3 aplicada ao produto), manchetes truncadas, `plain_text()` para
consola/app. Fidelidade XAI intacta (testes exigem cada número). **App deslastrada**: disclaimer
só na sidebar, knobs em "Advanced", métricas dev fora, Live board enxuto, /help agrupado.
**Sincronia**: demo/how_to_run/guia com o output novo (valores congelados intactos; 64 slides
0 erros); tese Cap. 4 +1 frase honesta (formato compactado depois; campos idênticos; CS3 =
registo congelado, intocado); caderno com a pergunta de júri sobre a evolução do formato.
109 testes + ruff verdes; 76 pp 0 erros.

### Sessão 30 — adenda UX ("a app continua confusa; estuda o mercado; refaz para utilizadores reais")
Rebranding da navegação para TAREFAS (padrão Yahoo/Google Finance): **📊 Markets now** (landing,
o Live board) · **🔎 Ticker check** (o antigo "Market trigger", cabeçalho em linguagem de
utilizador) · **📰 Check a headline** · **📡 Get alerts** (página NOVA: botão do canal via
`public.channel_url` no alerts.yaml — não-secreto, o canal é público —, tabela de comandos do
bot, exemplo REAL de alerta do demo determinístico) · **🎓 About & method** (Home/How-it-works/
Evaluation/About agrupados em tabs — o académico sai do caminho do utilizador). Testes
atualizados; as 5 páginas renderizam sem exceções (verificado com AppTest, dados reais).
Log real do Streamlit Cloud registado em deployment.md: Python 3.14 no cloud (leve OK; recriar
com 3.12 se quiseres coerência), aviso uv/pyproject benigno. 109 testes + ruff verdes.

### Sessão 30 — adenda ZERO-OPS (o aluno: "não quero fazer nada; tempo real; painel vivo; sê crítico")
Auditoria crítica honesta: o canal era um digest 1×/dia (não tempo real), notícias nunca ligadas,
bot exigia a máquina do aluno, canais não têm boas-vindas automáticas, app era demo clicável.
**Construído:**
- **Intradiário zero-ops:** cron de 30 em 30 min em horário de mercado (`0,30 13-21 * * 1-5`) +
  `concurrency`; estado do dia (`load_state/filter_new_alerts`, reset diário preserva offset) na
  cache do Actions → a mesma anomalia/manchete nunca repete no dia.
- **Notícias no canal LIGADAS** (10 tickers) com o gate de triagem treinado a 0.5 como controlo de
  fadiga — validado ao vivo em dry-run: suprimiu 7 manchetes (26–49%), passou TSLA. A RQ4 em produção.
- **Bot sem máquina:** comandos processados em lote em cada corrida (`process_bot_commands`,
  fail-open; resposta ≤30 min documentada); **bot_users.db persistida na cache** (falha crítica do
  runner efémero apanhada em revisão própria antes do deploy); aviso de consumidor único getUpdates;
  nota honesta de durabilidade (cache é best-effort → host/BD continua como evolução).
- **Live board na app (landing):** watchlist com preço/movimento/z-score/badge (ícone+texto)/
  sparkline 30 sessões/tiles, auto-refresh 120s, ordenado por |z|; testável offline pela seam
  `get_price_history`; AppTest dedicado; render real verificado (10 tickers, 0 exceções).
- Onboarding do canal: mensagem afixada + descrição prontas a colar (going_live §1b).
- **109 testes + ruff verdes.** CHECKLIST: app pública ✅ (clique do aluno); novos cliques: afixar
  a mensagem no canal + verificação de 1 min do Live board/Actions.

**Pedido do aluno (verbatim no espírito):** "turn this into a real product, public, for everyone…
no bullshit… thesis/slides/guide/caderno completely in sync… the most important thing is I dominate
everything… so I can be confident in my oral defence."

**Produto (defeitos reais corrigidos + melhorias, commit a941674):**
- **Anti-spam:** `news_is_fresh` (≤2 dias, `news.max_age_days`) — o scan olhava 7 dias para trás e a
  mesma manchete podia alertar dias a fio. **Anti-duplicado:** `bar_is_fresh`
  (`market.require_fresh_bar`, true por defeito) — num feriado o cron repetia o alerta da sessão
  anterior. Ambos puros e testados.
- **App pública com precedentes reais:** `scripts/curate_kb_light.py` (estratificação determinística
  do FNSPID 2018–2023, ≤36 por ticker×ano, só impactos completos) → `data/samples/kb_fnspid_light.jsonl`
  (**2.016 registos, 3,4 MB, versionada**). Decisão 256-d tomada COM evidência (64-d: consulta de
  recall da TSLA devolvia KO/XOM; 256-d devolve o precedente certo). `kb_query_embedder()` lê a
  dimensão do próprio ficheiro → coerência consulta↔KB por construção. Caption honesta na app
  ("word overlap, mais fraco que o SBERT da tese"). Demo/Cap. 3 (+6,46%) intocados.
- Badge "Alerts (scheduled scan)" no README; `load_prices` promovido a
  `investigator.market_data.load_close_series`.

**Sincronia + defesa:**
- **Tese (1 bullet, Cap. 6):** "rebuild da KB = futuro" ficou desatualizado após o P3 → agora diz,
  com precisão, que a KB JÁ foi reconstruída (depois de congelados os case studies) e que o trabalho
  futuro é a AVALIAÇÃO sobre ela. Recompila: 76 pp, 0 erros, 0 refs indefinidas, 0 overfull >15pt.
- **Caderno:** novo **§0 — guião oral** (abertura de 3 minutos + resposta de 15 segundos por RQ,
  só números congelados, com a frase-fecho "modesto e verdadeiro > impressionante e frágil") e novo
  **§6.5 — O produto HOJE** (tabela "como mostrar em 30s", honestidades prontas, plano B sem wifi).
- **Guia:** frame "O produto, HOJE — o que está ao vivo" → **64 slides, 0 erros**. Slides de defesa
  verificados (sem staleness). README: bot já construído, 16 frames/63 slides, KB como artefacto.
- **106 testes** (+3: frescura, barra fresca, KB leve end-to-end) + ruff verdes.
- Registado no CHECKLIST o próximo passo de produto desenhado: retrieval semântico na nuvem com
  MiniLM-ONNX (~23 MB, sem torch) para fechar o fosso word-overlap↔SBERT na app pública.

---

## Sessão 29 (continuação) — 2026-07-05 — PLANO FINAL: P1 escrita + P2 rename src/→investigator/
**Pedido do aluno:** "fazer TUDO" — polimento da escrita da tese, rename, KB multi-ano e S-APP, pela
ordem que fizesse mais sentido. Ordem fixada em **`progress/PLANO_FINAL.md`**: P1 escrita → P2 rename →
P3 KB FNSPID → P4 S-APP.

**P1 — passe editorial (commit 5c4c099):** as secções novas da RQ4 (M7) nunca tinham recebido o passe
das Sessões 23–24. Diagnóstico: 0 travessões-conectores, 0 tiques de IA → o trabalho foi partir
frases-comboio (Ch2 §triage, Ch3 §met_triage, Ch5 CS4 corpus/caveats, Ch6 4.ª contribuição) e limar
ecos ("deliberately", "precisely", "transparent(ly)"). **Nenhum número/citação/equação alterado.**
Reflow legítimo 74→76 pp (densidade verificada página a página — sem páginas vazias); 0 erros,
0 cit. indefinidas, 0 overfull >15pt; 93 testes + ruff verdes.

**P2 — rename `src/`→`investigator/` (o item deferido da Sessão 27, agora executado):**
- `git mv` (história preservada); pyproject ganha empacotamento (`[project] name=investigator`) e o
  requirements.txt ganha **`-e .`** → CI, workflow de alertas e Streamlit Cloud herdam o pacote sem
  hacks. Hacks `sys.path` removidos dos 12 scripts; o guard do `app/streamlit_app.py` fica de
  propósito (robustez no deploy). Imports reescritos em todos os .py; ci.yml/verify.sh/tasks.json/
  tests.bat passam a `ruff check .`.
- **Gotcha real encontrado e resolvido SEM retreino:** os bundles joblib guardavam
  `src.triage.model.PlattCalibrator` no pickle (load partiria após o rename). Solução: shim
  temporário em `sys.modules` + re-dump; **probe numérico byte-a-byte idêntico** (a/b do calibrador,
  p_raw/p_cal em vetor-zero, n.º de features) e load limpo sem shim; sidecars JSON intocados.
- Docs sincronizados (README, how_to_run, arquitectura, data_card, models/README, learning, caderno,
  guia, ML_PLAN, TRACKER, SESSIONS, CLAUDE) com as linhas que descrevem o próprio rename preservadas
  como `src/`→`investigator/`. Caderno: mapa do repo ganhou `models/`+`app/` e "14 frames"→16.
- **Validação:** 93 testes + ruff verdes; demo reproduz +6,46%; guia recompila (63 slides, 0 erros).

**P3 — KB de retrieval FNSPID multi-ano (commit f6553a2):** build destacado (`archive/streamlit-app/run/kb-fnspid.cmd`,
log `data/kb_build.log`, HF offline) → **79.753 registos** SBERT 384-d (~691 MB, gitignored);
amostra de 50 num caminho NOVO (o `--sample` por defeito esmagaria a `kb_sample.jsonl` da
demo/tese com dim 384≠64 — armadilha apanhada antes de disparar). Validação honesta em
`docs/evaluation/kb_fnspid_build.md`: 14/15 tickers (META="FB"), impactos ±1/3d completos,
**200 registos (0,25%) com +5d=NaN** (fim da janela — documentado), consultas AI/Fed/recalls
devolvem os clusters certos (sim 0,62–0,85). Consumo: produção fica na stack leve; números da
tese e deploy intocados; avaliação multi-ano continua futuro (Cap. 6), agora com a base pronta.

**P4 — S-APP Fase B (bot interativo, sem servidor):** decisão-chave = **long-polling** (getUpdates)
em vez de webhook → corre em qualquer máquina, grátis, sem host; utilizadores em SQLite stdlib
(`data/bot_users.db`). Novo: `investigator/telegram_bot/{store,commands,interactive}.py` (lógica
pura separada do transporte), `scripts/run_bot.py`, `archive/streamlit-app/run/bot.bat`, tarefa VS Code; runner ganha
fan-out por subscritor (`bot.enabled` no alerts.yaml, **off por defeito, fail-open provado** —
sem base: "fan-out saltado", nunca vermelho). Produto responsável: limite 20 tickers, /stop
reversível, validação sintática, moldura "evidência, nunca previsão". **10 testes novos → 103
no total**; app Home com "Get the alerts on your phone" e métrica 103; going_live.md Fase B
marcada CONSTRUÍDA; how_to_run §2.5. Dry-run do runner com config por defeito = comportamento
de sempre (verificado).

**PLANO FINAL P1–P4: COMPLETO.** Restam os cliques humanos do CHECKLIST (app pública no
Streamlit, licença/declaração com o orientador, leitura final, post_validate a 08-09/07).

## Sessão 29 — 2026-07-03/04 — WORKSTREAM ML: o aluno passa a ter modelos TREINADOS (M0–M5)
**Objetivo:** responder à preocupação do aluno ("não posso só aplicar; tenho de mostrar engenharia de
ML minha") com um componente treinado **honesto**: triagem/materialidade de notícias (RQ4), sem nunca
prever direção/preço. Ideia "RL" do aluno traduzida para o **loop de pós-validação** (M5.5).

**Plano-mestre (fonte de verdade multi-dispositivo): `progress/ML_PLAN.md`** (desenho fixado, fases
M0–M7 com caixas de estado, dados, avaliação honesta das áreas de IA). Tese/guia/slides SÓ mudam após
o OK do orientador (proposta pronta em `docs/internal/proposta_ml_orientador.md` — **o aluno tem de a
enviar**).

**Feito (M0–M3, tudo committado e pushed):**
- **M1 rótulos+dataset:** `abnormal_returns` (ticker−SPY) puro; `investigator/triage/dataset.py` (features com
  convenção anti-lookahead TESTADA por mutação do futuro; split temporal por dias únicos + embargo);
  `scripts/build_dataset.py` (cache de preços; grelha τ×h). Corpus real: 3.714 notícias → 0 descartes.
  **Achado honesto:** corpus-fumo de 4 semanas tem regime shift (treino 67,8% vs teste 37,2% positivos).
- **M2 treino:** `investigator/triage/{features,model,explain}.py` + `scripts/train_triage.py` — 6 famílias
  (always/vol/context/text/full/gbm), calibração Platt própria na validação, PR-AUC/ROC/Brier +
  precisão@orçamento/dia, XAI por decomposição aditiva exata da LR, persistência joblib+JSON.
- **M3 smoke com SBERT real:** reproduzível (2 corridas = métricas idênticas). Resultado honesto no
  corpus-fumo: **GBM 0,461 > vol 0,445 ≈ context 0,447 > always 0,372; texto ainda não ajuda (full LR
  0,357)** — coerente com o regime shift; motiva o FNSPID (M6). `docs/evaluation/evaluation_triage.md`
  + 2 figuras + **modelos versionados** (`models/triage_lr.joblib` 18 KB, `triage_gbm.joblib` 1,1 MB).
- Testes: 47 → **64** (17 novos), ruff verde; números congelados intactos.
- **M4 IF vs z-score (fbf01c1):** Isolation Forest causal (mesma informação, mesma região pontuada)
  **perde** para o z-score — F1 0,271 vs 0,530; amplitude de taxa de disparo 0,135 vs 0,015. A escolha
  estatística da tese fica validada por comparação com um detetor aprendido; secções congeladas do
  relatório de anomalia byte-idênticas.
- **M5 integração off-by-default:** a stack leve (runner/app na nuvem) não tem SBERT ⇒ o treino grava
  também a variante **só-contexto** (`models/triage_context_lr.joblib`, 1,8 KB) e é essa que a produção
  pontua (`investigator/triage/infer.py`, com guarda de compatibilidade de features). `news.min_materiality` no
  `config/alerts.yaml` (null = tudo como antes; **fail-open**: sem modelo/histórico o alerta segue);
  linha de materialidade opcional no `explain_news_impact`; página News da app ganha severidade +
  contribuições (graciosa sem `models/`; AppTest verde com e sem). Retreino de verificação: joblib
  principais **bit-idênticos**. Validado ao vivo (dry-run): NVDA real P=36% com linha; gate 0,99
  suprime com aviso; modelo ausente ⇒ "gate ignorado". Testes 64 → **81**; ruff verde.

- **M5.5 loop de pós-validação (a ideia "RL" do aluno, forma defensável):** `investigator/triage/postval.py`
  (log JSONL fail-safe, dedup, rotulagem ao maturar com a MESMA `abnormal_label` do treino, métricas
  ao vivo) + `scripts/post_validate.py` (preços frescos → `docs/evaluation/live_monitoring.md`:
  precisão das mantidas vs base rate, Brier, calibração, receita de retreino, caveat do runner
  efémero no Actions). Runner regista cada decisão de notícia. **Validado ao vivo:** 3 decisões reais
  registadas hoje (pendentes — correto, a janela não fechou) e uma sonda com data antiga maturou
  contra preços reais (label 1; Brier 0,25 = (0,5−1)² exato). Testes 81 → **93**; ruff verde.

- **GATE M7 ABERTO (2026-07-04):** o Prof. Luís Gomes deu o OK a tudo (confia no aluno; férias).
- **M6 lançado em background** na máquina do aluno (cadeia download FNSPID 2018–2023 → limpar cache
  de preços → dataset embargo 5 → retreino SBERT; log `data/fnspid_overnight.log`).
- **M7 parte 1 (8dcb1b1):** RQ4 integrada nos Caps. 1–5 sem números por chegar — Ch1 (RQ4 + 5.º
  objetivo + 4.ª contribuição), Ch2 (secção "Learned Alert Triage"; +2 citações VERIFICADAS
  Crossref: friedman2001gbm, niculescu2005calibration → 52/52), Ch3 (modelo + "Triage protocol" +
  desafio IF no protocolo), Ch4 (componente, "Learned severity", correções de honestidade: ranking
  já implementado; deploy agendado real), Ch5 (IF vs z-score, números M4 finais). 3 overfulls
  >15pt PRÉ-EXISTENTES eliminados (Apêndice A ×2 + tabela worked example, herança do rebrand;
  verificado por rebuild com o ch3 de HEAD). Compila 72 pp, 0 erros, 0 cit. indefinidas;
  compile-thesis CI verde. learning.md: §15 corrigido para números congelados; +§16–18 (triagem,
  IF, pós-validação) com notas de júri. Smoke preservada: `evaluation_triage_smoke.md`.

- **M6 FEITO (madrugada de 05/07):** a 1.ª cadeia (background Bash) morreu com a sessão → relançada
  como processo DESTACADO (Start-Process; lição em memória). Download afinal ~1h. Dataset FNSPID:
  **79.753 exemplos**, 1.501 dias, 0 descartes, 14/15 tickers (META="FB" no corpus), positivos
  38,5/47,0/37,8%. Retreino falhou 1.ª vez num erro httpx do HF hub (modelo JÁ em cache) → retry com
  HF_HUB_OFFLINE=1 ⇒ OK. **Resultado final (teste):** PR-AUC vol 0,542 > contexto 0,538 > full 0,496
  > GBM 0,469 > texto 0,439 > sempre 0,378; precisão@5/dia 0,632 vs 0,163; Brier 0,218 vs 0,622.
  93 testes verdes com os modelos novos.
- **M7-TESE COMPLETA (madrugada de 05/07):** Ch5 Case Study 4 (corpus+setup, tabela 6 famílias,
  figuras PR/calibração, leitura em 3 observações, caveats) + setup "four studies" + conclusões do
  capítulo; Ch3 data card atualizado (subset FNSPID CONSTRUÍDO e usado na triagem; KB de recuperação
  multi-ano continua futuro); Ch6 "four questions" + veredicto RQ4 ("No on the text hypothesis; yes
  on the mechanism") + 4 contribuições + limitações + futuro (gap de texto, FB→META, bandits);
  abstract EN 197 palavras + resumo PT com a frase da triagem. **74 pp, 0 erros, 0 cit. indefinidas,
  overfull máx 12pt.** learning.md §16 ganhou os números finais + nota de júri do resultado.

- **M7-MATERIAIS FEITOS (manhã de 05/07):** paper IEEE 4 pp (subsecção de triagem + IF; +2 refs
  espelhadas; discussão corrigida — "triage labels ARE market-adjusted"); slides 16 frames (+RQ4,
  +"Result 4" com tabela e veredicto, +3 perguntas de júri); guia 63 slides (+3 frames a ensinar
  triagem do zero; slide "o que usa/NÃO usa" corrigido — JÁ treina um modelo); caderno (§5 RQ4 com a
  resposta de júri em 3 frases, mapa de números +5 linhas, +4 perguntas difíceis); app 93✓/52-52 +
  "one model trained by the author"; README atualizado; page-audit "Extensão M7". Tudo 0 erros;
  93 testes + ruff verdes. **Workstream ML fechado: M0–M7 a 100%.**

**Restam (humano):** Streamlit Sharing→público; licença de código com o orientador; declaração ISEP de
IA + data; leitura final da tese. Loop M5.5: as 3 decisões reais maturam ~08-09/07 →
`python scripts/post_validate.py`.

---

## Sessão 28 — 2026-07-03 — Rebranding total do nome antigo → InvestiGator + go-live
**Objetivo:** o aluno escolheu o nome público **InvestiGator** (investigate+alligator, mascote
jacaré-detetive) e, depois de avisado do peso académico (Cap. 4, abstracts, o júri vê o trocadilho),
decidiu **renomear tudo, incluindo a tese**.

**Feito:**
- **Rename completo** em tese/paper/slides/guia/caderno/app/README/docs/scripts/CITATION/config.
  Técnica: só texto visível (CAPS + `\textsc`); labels LaTeX internos intactos (0 refs partidas);
  artigo EN corrigido ("A …"→"An InvestiGator"). História: depois renomeada também pelo próprio aluno
  (replace global no editor); o nome antigo fica preservado na história do git.
- **Rebuilds validados:** tese 72 pp / paper 3 pp / slides 15 pp / guia 60 pp — todos 0 erros; 0 citações
  indefinidas; 47 testes + ruff verdes; AppTest sem exceções.
- **Mascote:** `app/assets/investigator.svg` (deerstalker + monóculo + lupa) em `st.logo` + Home + README;
  favicon 🐊; tagline "Investigate. Don't speculate."
- **Go-live:** repo tornado **público** pelo aluno (antes: API 404 = privado — era a causa do dashboard
  inacessível); **história auditada antes de publicar** (128 commits, 0 segredos). Canal + segredos +
  workflow feitos pelo aluno. **URL vivo:** <https://investigator.streamlit.app> (no README/CHECKLIST).
  Falta 1 clique: tornar a app pública no Streamlit (Sharing) — foi implantada com o repo privado.
- **Revisão pós-rebrand (mesma sessão):** (1) **história reparada** — um replace global tinha mangled as
  entradas de continuidade (o par "nome antigo→nome novo" tinha virado "nome novo→nome novo");
  redação restaurada e tornada à prova de replaces futuros. (2) **Coerência de números:** 43→47 testes (README ×2,
  run_in_vscode, archive/streamlit-app/run/README, slide do guia) e 14→15 frames (slides/README); guia recompilado (60 pp,
  0 erros). (3) **Limpeza:** removidos `.gitkeep` obsoletos (tests/, thesis/figures/, data/samples/;
  data/.gitkeep fica — pasta gitignored). (4) **Reciclagem:** novo `investigator/console.py::force_utf8_stdout`
  usado por demo.py e run_alerts.py (scripts de avaliação congelados ficam como estão — reproduzem os
  números da tese; churn cosmético lá é só risco). 0 lixo versionado (sem .bak/.tmp); 0 TODOs no código.
  Validação: 47 testes + ruff; demo reproduz +6,46%; dry-run ok; AppTest sem exceções.

---

## Sessão 27 — 2026-07-02 — Auditoria ao repositório + polimento seguro + flagship Streamlit
**Objetivo:** auditoria profunda ao **repositório** (pedido do aluno, prompt tipo "team de arquiteto/
staff eng/reviewer"). Runway: meses até submeter → autorizado **relatório + polimento seguro + 1 feature**.

**Relatório de auditoria** (no plano `.claude/plans/…squishy-yeti.md`): scorecard honesto, Top-25,
críticos/altos/médios, e desenhos de Streamlit/cloud/Telegram-onboarding/multi-mercado como trabalho
futuro. Desafiado o prompt genérico (assume training/prediction/DB/scheduler que a tese **não tem por
desenho** — manter: sem treino, sem previsão de preços).

**Feito (43 testes + ruff verdes; números da tese inalterados; sem fabricação):**
- **C1 (reprodutibilidade):** `requirements.txt` → **leve**; nova `requirements-ml.txt` (torch CPU +
  SBERT, com `--extra-index-url` da PyTorch dentro do ficheiro); `setup_env.sh` leve por defeito +
  `--ml`. Corrige o "correr num comando" que **falhava numa máquina limpa** (torch `+cpu` não está no
  PyPI e o script não passava o índice).
- **C2/C3 (CI):** novo `.github/workflows/ci.yml` (pytest+ruff, runner limpo, cada push de código). O CI
  antes só compilava a tese; a afirmação "CI corre testes" era falsa → corrigida.
- **Organização:** `CITATION.cff`; `docs/README.md` (índice); `ROOT_PROMPT_CLAUDE_CODE.md` →
  `docs/internal/`; badges no README; **licença de código deixada por decidir com o orientador**.
- **Flagship:** `app/streamlit_app.py` (dashboard: Home, News, Market, Evaluation, How it works, About) +
  `requirements-app.txt` + `docs/design/deployment.md`. Validado por boot headless (`ok`) e **AppTest**
  ponta-a-ponta (sem exceções; clique devolve 3 precedentes). ruff cobre `app/`.

**Correr por cliques (P3 UX):** para quem evita a consola — `.vscode/` (Run & Debug ▶ + tarefas: demo,
dashboard, testes, compilar tese/slides/guia/paper, setup), `archive/streamlit-app/run/*.bat` (duplo-clique), guia
`docs/design/run_in_vscode.md`, e **`docs/planos/CHECKLIST.md`** (lista viva do que está feito/por fazer). Aditivo.

**Going-live 24/7 (P4, grátis, sem servidor):** pedido "app sempre up + notificações no telemóvel +
webpage a qualquer hora, tudo grátis". Faseado (confirmado): **Fase A** construída — `config/alerts.yaml`
(watchlist/limiares, sem segredos), `scripts/run_alerts.py` (varredura → z-score → alerta explicável →
canal Telegram; `--dry-run`; no-op seguro sem segredos), `.github/workflows/alerts.yml` (cron pós-fecho US
+ botão manual; segredos só em Actions Secrets), `tests/test_run_alerts.py` (4 testes), runbook
`docs/design/going_live.md` (canal + 3 segredos + caveats; **Fase B** — bot interativo por utilizador com
host do Student Pack + BD — desenhada, não construída). Clarificado ao aluno: **não há modelo treinado**
(por desenho), não havia timer/servidor, e push agendado não precisa de servidor always-on. **Validado:**
dry-run ao vivo apanhou anomalia real (META +8,44%, z=+3,31) sem enviar; **47 testes** (43+4) + ruff verdes.

**Deferido (com razão):** `src/`→`investigator/` (pacote instalável) — grande churn de docs; sessão dedicada.
Verificado que **nem a tese nem o paper** referenciam `investigator/` (rework tirou identificadores) → o rename não
afetará a tese.

**Próximo humano:** declaração ISEP + data; leitura final; **escolher a licença** com o orientador;
(opcional) publicar o dashboard e colar o URL.

---

## Sessão 26 — 2026-07-01 — Organização & sincronização (README + slides + guia)
**Objetivo:** fechar o pedido "correr a app / organização e qualidade" — pôr o repo apresentável e alinhar
os artefactos de defesa com a tese reescrita, com mais exemplos.

**Feito (com build/verify verdes):**
- **README como porta de entrada:** bloco "▶ Run it in one command" (`setup_env.sh` → `scripts/demo.py`),
  secção "Learn it / prepare the defence" (guia 60 slides + slides 15 frames + caderno), números corrigidos
  (43 testes, ~72 pp), layout do repo e comandos de build de todos os artefactos.
- **Slides de defesa (`slides/main.tex`) sincronizados:** `\tikzset` anti-hifenização global (sem cortes de
  palavra, igual à tese) + **novo frame "The data model — the objects"** a seguir à arquitetura. Render
  confirmado limpo → **15 páginas, 0 erros**.
- **Guia de estudo (`slides/guia_estudo/`): +3 frames** → **60 slides, 0 erros**: (a) exemplo honesto de
  quando o **baseline falha** (consulta de banca JPM → scores baixos porque o HashingEmbedder só vê palavras
  → motiva o SBERT / problema de vocabulário); (b) "**Constrói a tua própria KB**" (`build_kb.py` baseline vs
  `--sbert`); (c) "**Onde continuar a estudar**" (cross-links demo↔how_to_run↔tese↔slides↔caderno).

**Estado:** 43 testes + ruff verdes; demo reproduz +6,46%; números da tese inalterados; citações 50/50.
Nada de conteúdo/números/citações alterado. Falta só o humano (declaração ISEP + leitura final).

---

## Sessão 21 — 2026-06-27 — MASTER PLAN A–H COMPLETO (B→H, e fecho da A)
**Objetivo:** executar o resto da estrada longa após a Fase A, até deixar tudo pronto para submissão,
publicação e defesa.

**Feito (todas as fases, commit a commit, com build/verify verdes e push por incremento):**
- **A (fecho):** Estado da Arte elevado a **50 refs verificadas** (IR + precision@k; EMH/Fama 1970;
  trust/reliance Lee&See 2004 + Bansal 2021; volatilidade Engle 1982/Bollerslev 1986; ferramentas
  existentes dacunto/cardillo); protocolo de avaliação formalizado; diagrama de sequência do gatilho de
  mercado; `docs/design/how_to_run.md`. **76 pp** (alvo "80-ish" atingido com conteúdo genuíno).
- **B (naturalidade):** voz académica/natural no conteúdo novo (menos travessões/tics de IA).
- **C (revisão crítica do zero):** `docs/decisions/review_log.md`; achados C-1..C-5 corrigidos (lista do
  SoTA no Cap. 1; nota do *lift*; clareza cross-ticker no consumo; mockup ilustrativo; cross-ticker é de
  avaliação).
- **D (implementação + estatística):** `implementation_review.md`. **Re-corri os 3 scripts de avaliação
  (SBERT 5.6.0 + corpus presentes) e reproduzem EXATAMENTE os números da tese** (única diferença = carimbo
  temporal); 42 testes verdes (inclui `@sbert`) + ruff; guarda R1 (dimensão embedder–KB).
- **E (porta de submissão):** `page_audit.md`. **50/50 citações re-verificadas** (script → Crossref/arXiv;
  ISBN; fontes primárias confirmadas nas páginas oficiais com os números exatos — Gallup 62/87/28%, SIFMA
  US$62,2T, CCAF 81/71%). +DOI aamodt/lipton, +URL ding. PDF: 0 erros, 0 indefinidas, 0 `??`, 50 na
  bibliografia, 0 overfull. **Ataque do júri sobre fontes = ZERO.**
- **F (IEEE):** `paper/` (IEEEtran) destilado da tese validada; 23 refs (subconjunto verificado); compila.
- **G (slides):** `slides/` (Beamer, 14 frames); compila; último frame = perguntas do júri.
- **H (caderno visual):** `docs/defence/caderno_de_defesa.md` com workflow em diagramas, exemplos reais
  passo-a-passo e mapa dos números validados; números desatualizados corrigidos.

**Estado:** tese 76 pp (0 erros/indefinidas/órfãs/overfull; 50 refs re-verificadas); estatística
reprodutível; paper/ e slides/ compilam; tudo commitado e **pushed**.

**Próxima ação (só HUMANO):** confirmar redação ISEP da declaração de IA + data de entrega; leitura final
do aluno (§6.6). Opcional futuro: FNSPID multi-ano; estudo humano de utilidade; expandir o paper.

---

## Sessão 20 — 2026-06-26 — MASTER PLAN A–H + Fase A (conteúdo+visuais)
**Contexto:** pós-rework, o aluno definiu a estrada longa até submissão/IEEE/defesa. Criado
`progress/_historico/MASTER_PLAN.md` (Fases A–H; porta de submissão = Fase E: validação página-a-página +
re-verificar TODAS as citações). Pedido central da Fase A: ~80 pp por **conteúdo genuíno** (sem encher),
mais visuais, e "visualizar o workflow de dados/passos".

**Feito (Fase A, conteúdo genuíno — 4 commits):**
- **Cap. 3 (Methods):** figura conceptual do espaço de embeddings + **exemplo de recuperação REAL e
  reproduzível** sobre a KB-amostra commitada (query "Nvidia demand surges on AI chip orders" → 3
  precedentes AI; inclui match **cross-ticker** MSFT; impacto médio +5d = **+6.5%**). Encoder transparente
  baseline para reprodutibilidade sem download de modelo; o sistema implantado usa SBERT (avaliado no Cap. 5).
- **Cap. 5 (CS1):** **exemplo numérico de anomalia REAL** — TSLA 24-10-2024 (reação a resultados):
  μ=−0.92%, σ=2.73%, r=+19.82% (log; ≈+22% em preço) → **z=+7.61**, sinalizado a k=3 (yfinance, janela fixada).
- **Cap. 2 §2.7 "Existing Tools for the Retail Investor":** posiciona o InvestiGator vs alertas de corretora /
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

**Decisões (esta sessão):** estrutura canónica MEIA de 6 capítulos; sistema **InvestiGator**; cleanup = consolidação
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
  detalhe técnico movido para o Apêndice A (Reproducibility). InvestiGator no abstract/resumo.
- **Declutter:** removidos `archive/streamlit-app/notebooks/`, `presentation/`, `investigator/impact_analyzer/` (stub nunca usado).
- **Plano mestre** aprovado e registado (`.claude/plans/…`; checklist em `TRACKER.md`).
- Compila: **60 pp, 0 erros, 0 citações/refs indefinidas**.

**Validação:** LaTeX compila limpo; .py compilam (py_compile); sem importações dos módulos removidos.
Nota: **venv 3.12 ausente** neste ambiente (recriar para pytest/figuras; CI é o backstop dos testes).

**Feito (S2–S9, mesma sessão contínua):**
- S2: Cap. 3 (Methods and Materials) aprofundado — data card FNSPID, IA responsável, metodologia de avaliação.
- S3: Cap. 4 (InvestiGator) ao nível de desenho — arquitetura limpa + fluxos dos 2 gatilhos + mockup Telegram +
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
- **Métrica** (`investigator/evaluation/anomaly_eval.py`, puro, 6 testes): `rolling_zscore_flags` (sem
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
- **Métrica** (`investigator/evaluation/retrieval_eval.py`): **precision@k por setor** em recuperação
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
- **`news_fetcher`** (`investigator/news_fetcher/fetcher.py`): `NewsItem` (mesmo esquema da KB); parsing
  **puro e testado** (`parse_finnhub_news`, `parse_rss`, `_rss_date_to_iso`) separado do HTTP fino
  e tardio (`fetch_finnhub_company_news`, `fetch_rss_feed`). **Finnhub validado ao vivo** — 247
  notícias da AAPL na última semana, parseadas corretamente.
- **Explicação com precedentes** (`explain_news_impact`): alerta rastreável com a notícia, o
  impacto médio observado em eventos análogos (horizonte configurável), a lista de precedentes
  (data, ticker, similaridade, impacto, título) e a nota de que **é resultado passado, não
  previsão** (restrição §5.2). Média ignora NaN.
- **Orquestração** (`run_news_trigger` em `investigator/main.py`): notícia → embedding → `KB.find_precedents`
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
- **Similaridade** (`investigator/correlation_engine/similarity.py`): cosseno (1D e vetorizado) + `top_k_similar`,
  puro NumPy, determinístico (7 testes).
- **Base de conhecimento** (`investigator/historical_kb/`): `NewsRecord` (data, ticker, título, impacto, embedding;
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
`investigator/config.py` (.env), `investigator/main.py` (`run_thin_slice`). Testes unitários (4) + smoke (pipeline + envio Telegram
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

## Sessão 22 — 2026-06-27 — Revisão tipo-júri da tese inteira + correções genuínas
**Objetivo:** atuar como orientador/revisor/editor/examinador, ler a tese do início ao fim, questionar tudo,
encontrar fraquezas (com severidade) e **implementar melhorias genuínas** — sem encher, sem soar a IA/PhD,
**0 fabricação** (nenhuma citação/número alterado).

**Feito (correções, por severidade):**
- **M1 (Major).** Cap. 5 (CS3): novo parágrafo honesto — a recuperação semântica capta *tema*, não *direção*,
  por isso um título positivo recupera um *cluster* de ameaça competitiva com impacto médio negativo (−1,97%);
  a média é evidência sobre um tema, não previsão (precedentes mostrados um a um + disclaimer). Artefactos do
  corpus recente nomeados (mesma data de recolha; ticker duplicado partilha impacto). Liga a `lee2004trust`/`bansal2021whole`.
- **M2 (Major, transparência).** *Data card* (Cap. 3) anotado como camada FNSPID **desenhada**, com nota a
  apontar para o corpus real avaliado (3 714 títulos recentes) usado no Cap. 5; cláusula correspondente no Cap. 5.
- **M3 (Major, leitura).** Travessões `---` reduzidos de **117 → 39** (Cap. 2 48→23, Cap. 3 14→6, Cap. 4 18→2,
  Cap. 5 26→2, Cap. 6 9→4), preservando sentido (vírgulas/parênteses/dois-pontos; cabeçalhos `\paragraph` com `:`).
- **Mo2.** Mockup do Telegram (Cap. 4) internamente consistente (3 precedentes mostrados → média −2,2%; datas-artefacto removidas).
- **Mo4.** Cap. 4: parágrafo de produto responsável (fadiga de alertas; over-reliance; ranking por severidade,
  de-dup de precedentes, sinalizar discordância de direção) + linha de trabalho futuro no Cap. 6.
- **Mo3.** Apêndice A: tabela de versões fixadas (do `requirements.lock.txt`) + 3 comandos exatos de reprodução; LOF expandido no Cap. 2.
- **Mi1.** Fraseado da RQ2 (Cap. 1): baselines aplicam-se à recuperação, não à medição de impacto.
- Comentário desatualizado em `main.tex` corrigido (42→50 refs).

**Validação:** compila **78 pp**, 0 erros, 0 citações indefinidas, 0 overfull >15pt, 0 `??`; **42 testes + ruff verdes**;
integridade de citações **50/50** (0 órfãs, 0 indefinidas, 0 novas chaves). Código intocado.

**Entregável:** relatório de revisão completo (severidades + scorecard por capítulo + avaliação global) em
`.claude/plans/root-prompt-claude-code-md-squishy-yeti.md`.

**A precisar do aluno (humano):** confirmar redação ISEP da declaração de IA + data; leitura final do aluno (§6.6).

**Próxima ação:** nenhuma autónoma pendente — à espera de input humano (declaração ISEP) ou de nova direção.

### Sessão 22 — 2.ª passagem de revisão (verificação numérica + honestidade do abstract)
- **Honestidade do abstract/resumo:** a recuperação era quantificada só face ao acaso (0,24, a comparação
  mais lisonjeira); agora cita também a baseline lexical (0,35), a comparação significativa. EN 192 palavras (≤200).
- **Rigor (Cap. 3):** verificado contra o `kb_sample.jsonl` que a média +5d do exemplo trabalhado é
  6,456% → **+6,5%** (correta a partir de valores não-arredondados; os componentes arredondados somam 6,43%);
  adicionada nota de "média a partir de valores não-arredondados" (consistente com a tabela por-setor).
- **Consistência cruzada:** confirmado que todos os números-chave (0,514 / 0,346 / 0,240 / 0,126 / 0,516 /
  0,015 / 0,344) são idênticos no Cap. 5 e Cap. 6; +6,5% coerente entre Cap. 3 e Cap. 5. Sem deriva.
- Compila 78 pp, 0 erros/indefinidas/overfull/`??`.

### Sessão 22 — 3.ª passagem (consistência dos artefactos derivados com a tese)
Propagadas as correções da revisão (sobretudo M1: recuperação capta tema, não direção) para os artefactos
destilados da tese, para não sobre-afirmarem onde a tese passou a ressalvar:
- **`paper/main.tex`** (IEEE): +frase de limitação conceptual (tema≠direção) na Discussion. Compila 3 pp, 0 erros.
- **`slides/main.tex`** (Beamer): +bullet de limitação (thematic, not directional); +pergunta antecipada do
  júri ("título positivo recuperou precedentes negativos −1,97% — engana?") com resposta; rótulo do alerta
  "(5 precedents)" → "(over 5; 3 shown)". Compila 14 pp, 0 erros.
- **`docs/defence/caderno_de_defesa.md`** (PT-PT): +linha de limitação (tema≠direção) e +**P&R do júri**
  preparada sobre o exemplo −1,97% (tema vs direção; evidência verificável vs over-reliance; de-dup + sinalizar
  discordância de direção; nota +6,5% vs −1,97% = KBs/horizontes/encoders diferentes).
Abstract da tese já citava o lexical no `paper` — alinhado. Todos os artefactos coerentes com a tese.

### Sessão 22 — 4.ª passagem (Pass 5: revisão de produto / UX) + melhoria implementada
- **Deliverable:** `docs/decisions/product_review.md` (PT-PT) — crítica de produto/UX com severidades
  (PM/UX/arquiteto/utilizador), honesta e sem funcionalidades irreais; companheiro de review_log/implementation_review/page_audit.
- **Achado-chave (P-1, Maior):** estatística em bruto (z-score, σ, similaridade) é *transparente* mas não
  *compreensível* para o não-especialista. **Implementado:** `explain_anomaly` passa a render­izar o z-score
  em linguagem simples ("cerca de 7,6× a oscilação diária típica … muito além da volatilidade normal");
  +teste `test_explica_anomalia_em_linguagem_simples`; cláusula no Cap. 4. Recomendada banda qualitativa
  para a similaridade (futuro).
- Restantes achados (fadiga de alertas, sobre-confiança/clusters de direção mista, casos-limite, escala,
  acessibilidade/privacidade) já refletidos na tese como desenho/trabalho futuro ou são limites de desenho.
- **Validação:** ruff limpo; **43 testes verdes** (+1); tese compila 78 pp, 0 erros/indefinidas/overfull/`??`.
  Código intocado nos números (gloss só acrescenta prosa; estatística inalterada).

## Sessão 23 — 2026-06-28 — Revisão editorial TOTAL da tese (copy-edit humano)
**Objetivo:** atuar como editor académico/revisor de texto: tornar a tese natural, simples, fluida e
credível em EN-GB, sem tiques de IA, **sem mexer em conteúdo/números** e sem inventar nada. Capítulo a
capítulo, com pausa no fim de cada um (plano aprovado; registo em `docs/decisions/editorial_review.md`).

**Decisões (confirmadas com o aluno):** manter EN-GB (resumo PT também revisto); pausar após cada capítulo;
só a tese agora (artefactos sincronizados no fim).

**Feito:** Ch1–Ch6 + front matter (abstract/resumo) + Apêndice A. Por capítulo: identificar problemas →
explicar → aplicar → compilar/verificar → resumir → commit/push → pausa.
- **Travessões conectores em prosa: 117 → 1** em todo o corpo (resta 1 célula de tabela "não-aplicável").
- Frases/parágrafos longos partidos; jargão simplificado (desiderata→goals; impounded→absorbed; loss
  aversion explicada); tiques removidos (Crucially/moreover/in effect/precisely why/head on); construções
  invertidas reescritas; rótulos de tabela harmonizados; pequenas asperezas limadas.
- **Não tocado:** números, citações, equações, algoritmos, tabelas, figuras, declarações (integridade+IA),
  Apêndice A (já limpo).
- **Gate final:** coerência global verificada (terminologia, 0 espaços duplos, 0 artefactos, cross-refs OK,
  abstract 192 palavras); paper (3pp) e slides (14pp) compilam e ficam alinhados.

**Validação:** compila 78 pp, 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`; 43 testes + ruff verdes.

**Commits:** Cap.1 06ad896 · Cap.2 771dc29 · Cap.3 2356f2a · Cap.4 cd5458b · Cap.5 0314c21 · Cap.6 862e3c3 ·
front matter c2bc093 · gate final (este).

**A precisar do aluno (humano):** declaração ISEP de IA + data; leitura final do aluno (§6.6).
**Próxima ação:** nenhuma autónoma pendente; opcional (a pedido) estender a naturalidade ao caderno/slides.

## Sessão 24 — 2026-06-28 — Reescrita PROFUNDA da tese para clareza (Cap. 1–6)
**Objetivo:** o aluno achou a tese ainda densa/cansativa e o núcleo (modelo de dados, arquitetura, fluxo,
objetos/relações, componentes/responsabilidades, decisão) pouco claro. Reescrita de raiz para **clareza
progressiva**, dentro dos 6 capítulos canónicos. Decisões confirmadas: (1) reescrever a própria tese
(EN-GB); (2) manter 6 capítulos, reconstruir por dentro; (3) **foreground do system design no corpo**.

**Princípios:** cada secção responde a UMA pergunta; conceito antes de implementação; parágrafos curtos;
relações explícitas; clareza > completude; **sem inventar nada** (números/citações/equações preservados).

**Feito (commit por capítulo, com pausa):**
- **Ch1** (`78c9819`): secções guiadas por pergunta; objetivos em lista; "Document Structure" → **mapa do leitor**.
- **Ch2** (`17448dd`): cada secção abre com pergunta + fecha com "For InvestiGator:"; densidade **−4 pp**; citações/tabelas/figuras intactas.
- **Ch3** (`d11212e`): **concept-first** (cada técnica abre por "What it is for:"); "três escolhas" → lista; equações/algoritmos/data card/números intocados.
- **Ch4 = System Design** (`e60604b`): reconstruído — NOVO diagrama do **modelo de dados**, NOVA tabela **componente|responsabilidade|entrada→saída**, secção **Decision Logic**; reutiliza arquitetura/fluxo/mockup.
- **Ch5** (`f4021ff`): cada estudo abre com **pergunta+resposta**; números/tabelas/figuras/bloco do alerta CS3 intactos.
- **Ch6** (`99001f4`): vereditos RQ a negrito; limitações e trabalho futuro em listas.

**Validação:** compila **72 pp** (era 78), 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`;
**travessões conectores em prosa = 0**; **citações 50/50** (0 órfãs/indefinidas); 43 testes + ruff verdes.
Diagramas verificados por render (incl. novo modelo de dados).

**A precisar do aluno (humano):** leitura da tese reescrita (validar voz/estrutura); declaração ISEP de IA + data.
**Próxima ação:** (opcional) sincronizar paper/slides/caderno com a tese reescrita, se o aluno quiser.

## Sessão 25 — 2026-06-28 — Polimento visual + Guia de Estudo do zero (PT-PT)
**Pedido:** (1) pôr todas as figuras com qualidade de apresentação (sem cortes de palavras a meio, sem
colisões); (2) o aluno não sabe nada de IA — criar um guia visual que o ensine do zero a defender a tese.

**Feito:**
- **Polimento (commit f4b0ac3):** regra global em `main.tex` (nós de diagrama não hifenizam) corrige
  "Abrupt mar-ket move" e qualquer corte a meio; auditadas por render as 15 figuras (9 TikZ + 6 gráficos),
  todas limpas; tabelas 0 overfull. Nenhum número alterado; tese 72 pp, 0 erros.
- **Guia de estudo `slides/guia_estudo/` (Beamer PT-PT, 51 slides):** ensina do zero, scoped ao que a tese
  usa, com slide honesto sobre o que NÃO usa (sem treino/CNN/visão computacional). P0 pitch · P1 IA do zero
  + glossário · P2 problema/contribuição · P3 sistema (modelo de dados, componentes) · P4 dados reais (CSV +
  JSON de `data/samples/`) · P5 código módulo-a-módulo (fiel ao `investigator/`, linha a linha) · P6 workflow real
  (TSLA z=+7,61; Nvidia + tema≠direção) · P7 avaliação (gráficos validados) · P8 decisões · P9 sensibilidade
  · P10 perguntas do júri + checklist. Commits: P0/1 5175c47 · P2-4 1645644 · P5-6 9033843 · P7-10 6e90ccd.
  Só conceitos/código/números reais; 0 fabricação; compila 51 pp, 0 erros.

**A precisar do aluno (humano):** ler a tese reescrita e o guia; declaração ISEP de IA + data.
**Próxima ação:** (opcional) sincronizar paper/slides/caderno; estender o guia se o aluno quiser.

### Sessão 25 — adenda: "como corro a app?" + demo executável + mais exemplos
Pedido do aluno: continuava sem saber correr a app (sentia caixa preta) e queria mais exemplos.
- **`scripts/demo.py` (novo):** um comando único — `python scripts/demo.py` — corre os dois gatilhos
  **offline, sem chaves**, Windows-safe (força UTF-8). Corrido de verdade: reproduz o exemplo do Cap. 3
  (média +6,46% ≈ +6,5%) e o gatilho de mercado ao vivo (AAPL, z=+0,89). ruff limpo; 43 testes verdes.
- **Guia (`slides/guia_estudo/`): nova parte "Correr a app"** (6 slides) com o **output real** da demo,
  explicação linha a linha, um **exemplo de mudar parâmetros** (top_k=5/horizon=1 → +3,40%, com precedentes
  menos parecidos JPM/AAPL), correr os testes, e a nota Windows/UTF-8. Guia agora **57 slides, 0 erros**.
- **`docs/design/how_to_run.md`:** novo §0.0 "ver a app a funcionar (1 comando)" com a demo + nota UTF-8.
Descobertos e documentados 2 gotchas reais: emoji vs consola cp1252 (Windows); `-m investigator.main` precisa de
Telegram (por isso a demo usa `send=False`). Nada de números/conteúdo da tese alterado.
