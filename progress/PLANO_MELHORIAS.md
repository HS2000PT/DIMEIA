# PLANO DE MELHORIAS — roadmap acordado com o aluno (Sessão 41+)

> Fonte única deste esforço. Multi-sessão, multi-dispositivo. Cada fase fecha com gates
> verdes (202 testes + ruff; tese(s) compilam 0 erros) e **congelados byte-iguais**
> (models/, docs/evaluation/*.md, data/, números da tese). **Nunca fabricar** números,
> dados, citações ou resultados. Commits SEM trailer de IA (instrução do aluno).

## Princípios que o aluno reforçou (2026-07-24)
- **Visual sempre.** Moderno, simples, jovem, claro, agradável de ler. Os professores gostam
  de figuras/diagramas fáceis. "Simplicidade sobre complexidade."
- **Transparência dos dados.** Mostrar SNAPSHOTS reais dos objetos de dados (API/CSV) e o que
  lhes acontece em cada fase ("todas as fases da IA": bruto → limpo/alinhado → representado →
  aprendido/medido), que métrica se constrói e com que colunas.
- **Nada que revele processo tipo-software.** Sem nomes de ficheiros/scripts (`scripts/x.py`),
  sem frases "reads as a dissertation rather than a software specification". O júri NÃO tem
  acesso ao git. Frases dessas parecem tentativa de esconder uso de ferramentas de IA.
- **Honestidade.** Os resultados são o que são; melhorar o PRODUTO e a APRESENTAÇÃO, não os
  números congelados. Onde a ciência é fraca, dizê-lo (já é a postura da tese).

---

## WORKSTREAM 1 — Integridade da tese (URGENTE) 🔴
**Problema (confirmado):** o Apêndice A (`thesis/appendices/appendixA.tex`) lista comandos
`python scripts/evaluate.py`, `scripts/train_triage.py`, etc. (linhas 168–182); ch3/ch5 têm
notas `\texttt{scripts/…py}`. Contagem "199 tests" desatualizada (agora 202).
**Fazer:**
1. Reescrever a secção "Tests and Reproducible Results" do apêndice: descrever o MECANISMO de
   reprodução (procedimentos determinísticos, semente fixa, escrevem para ficheiros de
   resultado congelados que a tese cita) **sem nomear scripts nem ficheiros**.
2. Neutralizar as notas `\texttt{scripts/…py}` em ch3/ch5 (frase neutra: "regenerado por um
   procedimento determinístico documentado").
3. Atualizar "199"→"202"; rever "more than two hundred commits" (manter, é verdade).
4. Espelhar no thesis-pt quando o apêndice PT for traduzido (WS2).
**Risco:** toca prosa da tese (autorizado pelo aluno). Recompilar EN → 0 erros. Bilingue: o
apêndice PT é scaffold, sincroniza-se na tradução.
**Estado:** ⬜ a fazer nesta fase.

## WORKSTREAM 2 — Bilingue EN ↔ PT-PT (tese + SLIDES) (REGRA + tradução) 🔴
**REGRA estendida (2026-07-25, pedido do aluno):** a sincronia bilingue inclui os SLIDES DE
DEFESA. `slides/main.tex` (EN) ↔ `slides/main-pt.tex` (PT-PT, feito nesta sessão: mesmo
diretório → figuras/logos resolvem; 19 frames == EN; compila 0 erros; verificado ao render). O
guia de estudo (`slides/guia_estudo/`) já é PT-PT. Qualquer alteração a um deck espelha-se no
outro. **Build:** `cd slides && latexmk -pdf main-pt.tex`.

**REGRA (agora explícita, ver CLAUDE.md "Decisões Confirmadas"):** existem DUAS teses com o
MESMO conteúdo — `thesis/` (EN-GB) e `thesis-pt/` (PT-PT), tradução PURA, MESMO estilo de
escrita, tudo em sincronia (prosa, legendas, texto de figuras TikZ, tabelas, front matter).
Números/citações/labels/estrutura idênticos; só a língua muda. Gráficos de dados matplotlib
(`eval_*.pdf`) ficam EN nas duas (autorizado; legenda/caption traduzidas). Qualquer alteração
a uma língua É espelhada na outra no mesmo commit. Verificar sempre: as duas compilam 0 erros e
têm a MESMA contagem de secções/figuras/tabelas.
**✅ ESTADO (2026-07-25): TESE BILINGUE COMPLETA.** ch1+ch2+ch3+ch4+ch5+ch6 + APÊNDICE +
frontmatter TRADUZIDOS + **slides de defesa PT** (`slides/main-pt.tex`) + guia (já era PT).
ch2/ch3/ch4/ch5/ch6/apêndice feitos nesta sessão (labels/refs/citações/math BYTE-IDÊNTICOS —
diffs vazios; figuras/tabelas/diagramas/equações/algoritmos traduzidos, incl. as figuras novas,
a master_pipeline e a Fig 5.8; gráficos matplotlib ficam EN c/ legendas PT; alertas reais do
produto ficam EN). **thesis-pt compila 92 pp, 0 erros, ZERO refs indefinidas** (EN: 90 pp). FIX:
`meia-style.cls` PT com `shorthands=off`. **REGRA DE SINCRONIA em vigor:** qualquer alteração de
conteúdo a EN espelha-se em PT no mesmo commit. **Passo humano:** o aluno reler/aprovar o PT (voz
e terminologia) antes da defesa — é o texto dele. **Padrão de tradução PROVADO** (ver ch6): traduzir
prosa + captions + texto de figuras TikZ + células de tabela; manter labels/refs/citações/math/
números idênticos; ajustar só o espaçamento de figuras ao texto PT mais longo; compilar +
verificar render + `diff` dos labels vazio.
Também: **há PT-PT à mistura no EN** — pelo menos o resumo PT no `thesis/frontmatter` (isso é
esperado: o resumo PT faz parte do front matter EN) — VERIFICAR se há prosa PT no corpo EN.
**Fazer (por capítulo, com pausa de verificação):**
1. Traduzir ch2 → ch6 para PT-PT (pura tradução, mesmo estilo), incluindo legendas/tabelas/
   texto de figuras TikZ.
2. Traduzir o Apêndice A (já com a WS1 aplicada).
3. Varredura anti-mistura: nenhuma prosa EN esquecida no PT nem PT esquecido no EN.
4. Gate por capítulo: contagem de secções/figuras/tabelas EN==PT; ambas compilam.
**Risco:** trabalho ACADÉMICO grande; o texto é do aluno para defender → traduzir fiel, sem
inventar. O aluno deve reler.
**Estado:** ⬜ ch1+front feitos; ch2–ch6 + apêndice por fazer.

## WORKSTREAM 3 — Visuais: snapshots de dados + fases "IA" + logos 🟠
O aluno adora visuais e os professores também. Já existe (Sessão 40): Fig. 3.2 "jornada dos
dados" (RAW→CLEAN→REPRESENT→LEARN) e Tabela 3.4 (dicionário de colunas). **Reforçar/estender:**
1. **Snapshots reais dos objetos de dados** (o pedido central): para CADA fonte (Finnhub news
   JSON, yfinance/fallback preços, FNSPID CSV, NewsRecord da KB, embedding SBERT, features da
   triagem) uma figura/cartão com um EXEMPLO REAL (valores genuínos) do objeto **bruto** e do
   objeto **depois de limpo/normalizado/representado** — lado a lado. Modernos, coloridos,
   simples. Na tese (Cap. 3) E nos slides/guia.
2. **"O que acontece aos dados" por fase da IA:** um diagrama por fase (limpeza/alinhamento
   anti-lookahead; embedding; rótulo; calibração) com um antes→depois concreto.
3. **Que métrica com que colunas:** estender a Tabela 3.4 / novo diagrama que liga colunas →
   métrica (contexto→PR-AUC; embedding→precision@k).
4. **Logos** das fontes/APIs/tecnologias: já há badges + logos reais nos slides/guia (Sessão
   40, `slides/logos/`). Garantir que estão visíveis e completos na apresentação; na tese ficam
   badges/figura (logos de marca são incomuns numa tese — decisão da Sessão 40, mantida).
5. **Mais figuras "tipo slides" na tese:** o aluno acha que a tese tem menos clareza visual que
   os slides/guia. Identificar 3–5 pontos densos (ex.: retrieval, calibração Platt, funil) e
   acrescentar um diagrama simples em cada, à imagem dos slides.
**Risco:** figuras novas na tese NÃO podem alterar números; snapshots usam valores reais já no
repo (ex.: o exemplo NVDA 10 Mai 2018 da Sessão 40). Bilingue: espelhar legendas.
**Estado:** ⬜.

## WORKSTREAM 4 — App: correções + marketing + funcionalidades 🟠
Lista concreta do aluno (2026-07-24):
1. **Setas/ícones (BUG):** `direction_icon` devolve 🔺 (VERMELHO) para SUBIR. Subir deve ser
   VERDE, descer VERMELHO. Corrigir o glifo/estilo em TODOS os sítios (texto do alerta, resumo
   diário, nota de abertura, dashboard) — fonte única já existe (`direction_icon`). Atualizar os
   testes de fidelidade que fixam 🔺/🔻. **[opções de glifo a decidir com o aluno: 📈/📉;
   🟢/🔴; ▲/▼ coloridos no dashboard.]**
2. **Estado do mercado em tempo real:** a app mostra aberto/fechado AO VIVO (já existe
   `is_us_market_session`; expor no topo com contagem para abertura/fecho).
3. **Mais bolsas / horários europeus** (Xetra, Euronext, LSE…): mapa de sessões por bolsa +
   fusos; watchlist multi-bolsa. (Fases: primeiro o indicador de estado por bolsa; depois
   alertas multi-bolsa.)
4. **Visão intradiária por defeito no gráfico** + **gráfico mais "tempo real"** (ping
   constante; já há `@st.fragment(run_every=120)` — reduzir/afinar; cuidado com limites free).
5. **Tema claro/escuro** mantém-se e pode seguir a HORA (dia=claro, noite=escuro) — mesma
   função que troca também: **mascote crocodilo dia/noite**, fundo sol/lua/por-hora. "Fun."
6. **Mascote** da app (crocodilo investigador, silly/alegre) — asset visual; base para o futuro
   chatbot-mascote.
7. **Logo/interface mais customizado/polémico** — iterar o logo e o look (o aluno quer
   personalidade).
8. **Autenticação no painel (admin/guest):** por defeito GUEST; forma de autenticar como ADMIN;
   admin altera as definições por cliques (rato) e essas mudanças refletem-se nos alertas do
   Telegram (os thresholds/critérios passam a ser editáveis no painel, persistidos).
9. **Marketing/apelo:** tornar a app mais apelativa e "likeable" (hero, copy, cores, mascote,
   storytelling do alerta).
**Risco:** auth + config editável que afeta o Telegram = mudança de produto com estado; desenhar
com cuidado (persistência segura, sem segredos no cliente). Não fabricar. Manter fail-open.
**Estado:** ⬜ (1 e 2 são os primeiros; rápidos).

## WORKSTREAM 5 — Resultados: análise crítica + melhorias honestas 🔴
**A frustração do aluno (legítima):** "tantas notícias positivas, mas os casos passados são
quedas"; "os ícones ainda confundem"; "o critério de alerta é duro demais, devia ser mais
sensível e customizável"; "a história real aparece tarde"; "não traz valor real, é ignorado".
**Diagnóstico honesto (a fazer, com provas dos alertas reais):**
- O "positivo → precedentes negativos" é o achado tema≠direção (já no Cap. 5, CS3): o retrieval
  capta TEMA, não direção. Isto CONFUNDE o utilizador. **Melhorias de produto (não de número):**
  (a) separar claramente "tema semelhante" de "direção"; (b) quando os precedentes divergem em
  direção, dizê-lo em destaque (já existe o aviso BOTH — reforçar visualmente); (c) mostrar a
  DISTRIBUIÇÃO de direções dos precedentes, não só a média; (d) rótulos human-first.
- **Critério de alerta "duro demais":** o threshold de mercado e o chão de similaridade são
  configuráveis. Estudar tornar ligeiramente mais sensível E **customizável no painel** (WS4-8),
  mantendo a avaliação da tese (3.0) congelada e distinta da produção.
- **"História tarde":** rever a latência (cron 1–2 h vs intradiário; a VM/pings ajudam).
- **Ser crítico:** escrever `docs/evaluation/product_critique.md` — o que não funciona, porquê,
  e o que muda (produto), separando claramente do que a ciência já provou/refutou.
**Regra dura:** NÃO inventar melhores resultados. Melhorar clareza, sensibilidade configurável,
e a NARRATIVA; ser honesto sobre limites.
**Estado:** ⬜.

## WORKSTREAM 6 — Produto/futuro (desenho agora, construir depois) 🟢
- **Chatbot-mascote** ("investigator" crocodilo): pergunta→pesquisa nos dados do aluno→em último
  caso na net, em tempo real. Desenho: começar por RAG sobre a KB/alertas locais; net é fase 2.
- **Multi-bolsa completo** (WS4-3 estendido).
- **Auth robusta** (WS4-8 estendido).
Estes ficam DESENHADOS no plano; construção faseada e só com decisão do aluno onde há custo/risco.

---

## As minhas sugestões proativas (o aluno pediu) 💡
1. **"Uma página, um alerta explicado"** na tese/slides: um alerta REAL do canal (NVDA 13/07)
   dissecado visualmente gate a gate — já existe texto no Cap. 4 ("Life of One Alert"); torná-lo
   uma FIGURA-cartaz limpa (o júri adora um exemplo concreto ponta a ponta).
2. **Cartão "o que é / o que NÃO é"** logo no início (app + slides): "evidência do passado,
   nunca previsão" — gere confiança e alinha expectativas (resolve parte do "não traz valor").
3. **Painel de saúde ao vivo** na app: nº de alertas, precisão pós-validação (0,667 vs 0,455),
   KB a maturar — prova de que "está vivo" e funciona (combate o "é ignorado").
4. **Glossário visual** de 6 ícones (anomalia, precedente, tema≠direção, severidade, triagem,
   frescura) reutilizado em app+slides+tese — linguagem visual consistente.
5. **Guia de estudo:** um "mapa dos números congelados" já existe; acrescentar um "guião de 3
   min por RQ" com as figuras novas (WS3) — para a defesa calma que o aluno quer.
6. **App marketing:** hero com a mascote + slogan + 3 provas ("explicável", "grátis", "ao
   vivo"), e um mini-tour de 20s.

## Decisões do aluno (2026-07-25) ✅
- **Próximo foco:** **App value + clarity** (corrigir a confusão dos precedentes, alertas mais
  sensíveis/customizáveis, estado do mercado ao vivo, painel de saúde, marketing).
- **Setas:** **manter 📈 / 📉** (já aplicado).
- **Auth do painel:** **guest + password de admin** (guest read-only; admin desbloqueia edição
  das definições, que persistem e alimentam os alertas Telegram).
- (Ainda em aberto: que bolsa europeia primeiro — Xetra/Euronext/LSE.)

## Registo de progresso
- **Sessão 41 (feito, PR #1):** robustez (10 correções + 5 testes); contagens de teste;
  WS1 integridade do apêndice ✅; WS4-1 setas 📈/📉 ✅; **clareza dos precedentes** (split de
  direção + "not a prediction for this news") ✅.
- **App value + clarity — FEITO nesta corrida (PR #1):**
  - ✅ **Clareza dos precedentes:** split de direção + "not a prediction for this news".
  - ✅ **Estado do mercado US ao vivo** (🟢/🔴 + contagem, DST via zoneinfo).
  - ✅ **Badge de prova de vida** ao topo (alertas entregues + precisão vs base rate).
  - ✅ **Painel guest/admin + overrides ajustáveis** que chegam aos alertas: núcleo puro
    `investigator/settings_overrides.py` (valida/limita, fail-open) + runner `effective_config()`
    (base + local + branch) + painel na app (password de admin → sliders → publica na branch).
  - ⏳ Marketing/hero e nudge de defaults: o painel já torna os critérios customizáveis pelo
    admin; a identidade (mascote/logo/tema por hora) é o foco "App fun + identity", ainda não
    escolhido.
- **🧑 PASSO HUMANO p/ ativar o painel de admin:** no Streamlit (Manage app → Settings →
  Secrets) definir `admin_password = "..."` (desbloqueia a edição) e, para aplicar ao vivo sem
  copiar à mão, `github_token = "<PAT com repo:contents write>"` (o repo é derivado do
  history_url). Sem estes segredos, a app fica em guest (read-only) — comportamento seguro.
- **✅ App fun + identity (FEITO, PR #1):** mascote crocodilo dia/noite on-brand
  (`app/assets/mascot_day.svg` sol + olho acordado; `mascot_night.svg` lua crescente + estrelas
  + olho sonolento), sincronizada com a hora local (Lisboa) via `day_phase()`; logo do canto +
  herói do About + saudação do "investigador" sensíveis à hora. Verificado ao vivo (Playwright):
  renderiza, mantém o toggle de tema. **Crítica honesta** em `docs/design/product_critique.md`.
  **Também:** About sem nomes de scripts/ficheiros (integridade, coerente com o apêndice).
- **✅ WS3 figuras de tese (4 novas, PR #1, todas verificadas ao render + grounded):**
  (1) **Fig 3.3 "objetos de dados reais"** — bruto→registo→embedding (AAPL 2020-03-09 "Crude
  Awakening"; impactos +7,2%/−6,7%/−9,0%). (2) **Fig 3.4 "duas curvas" do z-score** — calma vs
  volátil, mesmo −3,2% na cauda vs no corpo (z=−8,1 vs −2,2), da Tabela 3.2. (3) **Fig 5.8
  "tema≠direção"** — barras dos 5 precedentes reais do alerta NVDA positivo, todas vermelhas
  (média −1,97%). (4) **Fig 6.1 "scorecard das RQ"** — 4 veredictos honestos (verde/amarelo) +
  um número cada. (5) **Fig 2.3 "3 gerações de texto → SBERT"** — escada Lexicons/word2vec/BERT/
  Sentence-BERT (a escolha, ★). (6) **Fig 6.2 "limitações → trabalho futuro"** — mapa de 2
  colunas. Tese 90 pp, 0 erros; todas grounded + verificadas ao render (pp. 10/18/20/48/55/58).
  **⚠️ falta espelhar as 6 no thesis-pt (WS2, quando ch2/ch3/ch5/ch6 forem traduzidos).**
  **Auditoria multi-agente** deu um
  BACKLOG de figuras grounded (verificação bateu no limite da conta, reset 05:30 Lisboa) —
  candidatas fortes por implementar (verificar grounding eu próprio antes):
  ch5 "tema≠direção (notícia positiva → precedentes negativos)"; ch6 "scorecard dos veredictos
  das RQ"; ch4 "a vida de um alerta pelos gates"; ch5 "4 estudos de caso num relance";
  ch2 "3 gerações de representação de texto → SBERT"; ch3 "split cronológico com embargo".
  **Espelhar no thesis-pt quando o ch3 for traduzido (WS2).**
- **✅ Bolsas europeias (FEITO, PR #1):** `market_hours` generalizado (Exchange + EXCHANGES:
  US/Xetra/Euronext/LSE; `exchange_status` DST via zoneinfo com abreviatura de fuso dinâmica;
  `all_exchange_status`; `us_market_status` = wrapper compat). App mostra a pílula US + "Other
  exchanges: 🟢/🔴 Xetra · Euronext · London". As europeias são informativas (watchlist = US).
  **+ robustez:** preços NaN degradam com graça (sem "$nan"; `closes.dropna()`). Verificado ao
  vivo (Playwright): pílula multi-bolsa + mascote DIA (sincronia dia/noite confirmada a mudar
  entre corridas). 224 testes + ruff verdes.
  **⏳ Ainda em aberto (para escolher):** resto do backlog de figuras (ch5 4-casos, ch3 split,
  ch6 limitações→futuro, ch4 vida-de-alerta); tradução PT ch2–ch6 (WS2) + espelhar as 5 figuras
  novas; alertas multi-bolsa (dados de preços europeus); chatbot-mascote (WS6).

## Ordem de execução proposta
**Fase 1 (já):** WS1 (integridade do apêndice) + WS4-1 (setas verdes) + WS4-2 (estado do
mercado ao vivo) — concretas, seguras, alto impacto visível.
**Fase 2:** WS3 (snapshots de dados + fases IA) na tese/slides + WS5 (crítica honesta +
sensibilidade configurável).
**Fase 3:** WS2 (tradução ch2–ch6) — grande, faseada por capítulo.
**Fase 4:** WS4 restante (tema/mascote/auth/multi-bolsa) + WS6 (desenho do chatbot).
```
```
