# Backlog do aluno — pedidos por trabalhar

> **Estatuto: por analisar.** Registado a **2026-08-05**, tal como o aluno o ditou, para não se
> perder na mudança de sessão ou de máquina. **Nada aqui foi pensado, estimado ou decidido** — é
> a lista em bruto, e é de propósito que está em bruto: analisá-la agora seria decidir sozinho
> coisas que ele quer decidir depois.
>
> Ordem = a ordem em que foi ditada, não prioridade.

---

## 1. Refazer o painel por completo

Tecnologias novas, estudo de mercado, usabilidade talhada para o utilizador. Interface
**premium**: responsividade, desempenho, moderno, *drill-downs*, estados de *hover*, cliques,
detalhe. **Interactivo.**

*Já existe material para arrancar, e é só isto que registo:*
[`docs/design/PROMPT_dashboard_v4.md`](../docs/design/PROMPT_dashboard_v4.md) (briefing para uma
sessão nova) e o estudo de mercado que **completou** na sessão 49 — 4 agentes, resultado em bruto
no `journal.jsonl` da corrida `wf_c5217b07-1db`. A conclusão que ficou registada no `CLAUDE.md`:
o custo não é CSS nem afinação do Streamlit, é **carga a frio**, e a recomendação era
**pré-computar para um *snapshot* estático** no worker de 60 s.

## 2. Rever a revisão de literatura por completo

Com **o PDF real de cada referência numa pasta do repositório**, e um documento que diga
**exactamente o que foi extraído e de onde**.

⚠️ **Uma restrição que ele vai precisar de saber quando pensar nisto, e por isso fica escrita
aqui em vez de ser descoberta depois:** o repositório é **público** e os PDFs são material com
direitos de autor. Versioná-los transformaria uma auditoria de integridade numa violação de
copyright. A infra-estrutura já está montada com esse cuidado:
[`docs/decisions/citation_pdfs/`](../docs/decisions/citation_pdfs/) existe, tem README com a
lista exacta do que descarregar, e os `*.pdf` estão **gitignored**. Ou seja: os PDFs podem viver
na máquina e ser lidos; o que vai para o repositório é o **relatório** da extracção.
Se ele quiser mesmo os ficheiros versionados, a saída é **tornar o repositório privado** — e isso
tem consequências já medidas (parte a app em silêncio, limita minutos do Actions), registadas em
[`v3_backlog.md`](../docs/design/v3_backlog.md). **É decisão dele, não minha.**

*Estado actual, para ele saber de onde parte:* metadados **84/84** verificados por script;
conteúdo **129/129 instâncias, 59/59 chaves**; paridade EN↔PT **0 assimetrias**. O que falta é o
que ele está a pedir: o **texto integral** de cada fonte lido e a extracção registada.
Das 59, **44 são legíveis sem conta nenhuma**; **14 precisam da conta ISEP** (lista no README
acima, com prioridade indicada).

## 3. Melhorar a latência dos alertas (quase tempo real)

**Sintoma dado por ele:** ontem foi notificado **depois** de o acontecimento já ter ocorrido no
mundo real.

*Sem análise, só o que já está registado e é relevante:* o worker corre a **60 s** desde a sessão
44; antes era o cron do GitHub, medido em **1,5–2 h**. A mediana de latência mostrada
(**208 min, n=44**) ainda **inclui o histórico do cron antigo**, portanto o número no ecrã e a
latência actual não são a mesma coisa.

## 4. Melhorar o guia de estudo

(86 slides hoje.) Sem mais detalhe dado.

## 5. Rever a escrita

**Humana, jovem, natural** — e que **não seja apanhada por detectores de IA**.

⚠️ **Nota de integridade que fica registada porque a regra do projecto obriga:** a declaração
honesta de uso de IA no *front matter* **mantém-se**. O pedido é sobre **voz e naturalidade do
texto**; não é, e não pode virar, encobrir o uso de IA. Já houve uma passagem destas na sessão 41
com exactamente esta fronteira: limparam-se os *tells* de meta-comentário defensivo e a
declaração ficou intacta.

## 6bis. Rever o mecanismo de alertas e de notícias

**Ditado a 2026-08-05, com um caso concreto.** Hoje a NVDA subiu muito porque o Elon Musk disse
que a SpaceX passaria a usar exclusivamente chips NVDA. **Essa notícia nunca apareceu nos
alertas**; apareceram outras menos importantes. Além disso: **a mesma notícia veio repetida**; e
notícias **semanticamente negativas** trouxeram precedentes que subiram, e notícias muito
positivas trouxeram precedentes que desceram.

### O que já foi verificado no código (2026-08-05), para poupar tempo à análise

**(a) O tecto diário é servido por ordem de CHEGADA, não por importância.** Em
`scripts/run_alerts.py::filter_new_alerts`, o `max_per_ticker_per_day` (hoje **2**) corta assim:

```python
if state["news_count"].get(ticker, 0) >= max_per_ticker:
    continue    # ja alertou 2 vezes este ticker hoje -> descarta o resto
```

As notícias são percorridas pela ordem em que chegam. **Duas notícias irrelevantes de manhã
consomem a quota e a notícia que interessa é descartada à tarde**, em silêncio. E o mais irónico:
o projecto **tem um modelo de triagem treinado** cuja função é exactamente ordenar por
materialidade (RQ4, precisão 0,632 contra 0,163 num orçamento de 5/dia) — mas o tecto **não o
usa**. Isto explica o caso da NVDA sem ser preciso mais nenhuma hipótese, e é testável.

**(b) A deduplicação é por texto exacto.** `news_key(ticker, text)` é um hash do texto. A mesma
história escrita por outro meio, ou com o título ligeiramente diferente, dá **chave diferente** e
passa como notícia nova. O projecto já tem *embeddings* — a dedup semântica é possível sem
dependências novas.

**(c) A cobertura da fonte nunca foi medida.** As notícias vêm do Finnhub *company news*. Se o
Finnhub não etiquetar a história da SpaceX como NVDA, ela **nunca entra no funil** e nenhum gate
tem culpa. **Não está medido quantas das histórias que realmente movem o mercado o sistema
chega sequer a ver.** Isto é uma limitação assumida e não quantificada — o mesmo estado em que
estava a deriva antes da sessão 43, e que passou de *afirmada* a *medida*.

### ⚠️ (d) O terceiro ponto NÃO é um defeito. É o resultado central do CS3.

*"Notícia negativa mas os precedentes subiram, e vice-versa"* é **exactamente** o que a tese
mede e reporta: a recuperação capta o **tema**, e o tema quase não diz nada sobre a **direcção**.
Está quantificado: **consistência de direcção 0,708 contra um chão de acaso de 0,688**
(`docs/evaluation/evaluation_retrieval_fnspid.md`), e é por isso que o alerta mostra sempre os
precedentes **individuais** e nunca só a média, com a moldura *tema ≠ direcção*.

**Não "corrigir" isto.** O que pode melhorar é a **comunicação** no produto: hoje a moldura
existe mas é uma frase; o aluno leu os alertas e mesmo assim leu-o como incoerência, o que é o
sinal mais claro de que a frase não está a chegar. É trabalho de interface, não de motor.

## 6ter. Estudo de mercado e tabela comparativa na tese

**Pedido:** analisar e descrever o que existe no mercado parecido com isto (apps, sites,
corretoras de topo), sobretudo a funcionalidade nova do género *"porque é que a NVDA subiu
hoje?"* — o utilizador carrega e recebe uma explicação. Depois, uma **tabela comparativa** do que
cada um tem e não tem, e o que este trabalho tem por cima.

**Sim, é prática comum numa tese — e a tese JÁ TEM isso.** §2.7 (`sec:sota_tools`) tem duas
tabelas: *"Existing retail tools versus the system proposed in this work"* (explica porquê?
mostra precedentes? age pelo utilizador?) e *"Existing tools scored against the three questions"*
(Q1/Q2/Q3), mais um parágrafo sobre assistentes LLM genéricos e a crítica de **ancoragem**.

**O que falta, e o aluno tem razão no que notou:**

1. **Nomes.** As tabelas comparam **categorias** ("brokerage price alert", "news/sentiment app"),
   não **produtos nomeados**. Um arguente pergunta *"quais é que foram mesmo vistos?"*. Nomear
   Google Finance, Robinhood Cortex, Perplexity Finance, Simply Wall St, TradingView, Finviz,
   Koyfin, Yahoo Finance, com **data de observação**, torna a comparação verificável.
2. **A vaga do "porque é que subiu hoje?" é de 2025-26 e não está examinada.** O parágrafo sobre
   LLM genéricos antecipa a crítica, mas foi escrito antes destes produtos existirem. Hoje são o
   concorrente directo da afirmação central deste trabalho e merecem tratamento próprio.
3. **A comparação é uma lista de funcionalidades, não uma medição.** O que ninguém faz e teria
   muito mais força: **pegar no MESMO acontecimento** (o dia da NVDA serve) e pôr lado a lado o
   que cada produto disse e o que o InvestiGator disse. Deixa de ser uma tabela de Sim/Não e passa
   a ser evidência.

**Já existe material para arrancar, e já está salvo:**
[`docs/design/market_study_v4.md`](../docs/design/market_study_v4.md) — 69 achados sobre
TradingView, Koyfin, Finviz, Yahoo, **Robinhood Cortex**, Public.com, Bloomberg web,
**Perplexity Finance**, worldmonitor, Stock Events, Delta e **Simply Wall St**, com o teste
*"o que é que um leigo extrai em dez segundos?"*. Extraído do `journal.jsonl` da corrida
`wf_c5217b07-1db` na sessão 51, porque só existia numa pasta temporária de uma máquina.

⚠️ **Os quatro cépticos que deviam contestar esse estudo morreram no limite de gasto**, e isso
está escrito no topo do próprio documento: **as conclusões não passaram por contraditório**. Tudo
o que dali for para a tese tem de ser **reconfirmado** — são afirmações sobre produtos de
terceiros, observadas numa data, e um arguente pode abrir a app e verificar.

## 6quater. Sugestões minhas, para o aluno decidir

Pedidas por ele. Ordenadas pelo que **acrescenta mais à tese por unidade de esforço**, não pelo
que é mais divertido.

1. **Medir a cobertura do funil de notícias.** Hoje a tese diz que a fonte é gratuita e limitada;
   não diz **quanto** perde. Pegar em N dias, listar as histórias que realmente moveram cada
   acção, e contar quantas o sistema chegou a **ver**, quantas passaram a relevância, e quantas
   saíram. Converte uma limitação **afirmada** numa limitação **medida** — exactamente o padrão
   que já valorizou a deriva e a incerteza. É provavelmente o acrescento mais forte que resta.
2. **Ordenar por materialidade em vez de por chegada** (o defeito (a) acima). Além de corrigir o
   produto, dá à RQ4 uma **utilidade operacional a sério**: o modelo deixa de ser só avaliado e
   passa a decidir o que cabe no orçamento diário. É a ponte que falta entre "a triagem vale como
   mecanismo" e "a triagem está a fazer alguma coisa".
3. **Estudo de utilidade com pessoas** — continua a ser a **única linha em aberto** do Cap. 6, e
   nenhum trabalho meu a fecha. 6 a 10 pessoas, ~15 min cada. O material está pronto e por correr
   desde a sessão 42 (`scripts/build_usefulness_pack.py`).
4. **Um caso de estudo de FALHA, escrito por extenso.** O dia da NVDA é perfeito: notícia real que
   moveu o mercado, sistema não a mostrou, causa identificada no código, correcção aplicada e
   medida. Uma tese que mostra um falhanço diagnosticado é mais credível do que uma que só mostra
   vitórias — e este projecto já ganha crédito precisamente por isso.
5. **Dedup semântica** (defeito (b)): reutiliza os *embeddings* que já existem; sem dependências
   novas.

## 6. Quaisquer pendências que restem nos TODOs do repositório

Varrer [`CHECKLIST.md`](../CHECKLIST.md), os `TODO` no código e nos `.tex`, e o que sobrar do
[`v3_backlog.md`](../docs/design/v3_backlog.md).

---

## O que já estava em fila antes disto (não apagar)

Da sessão 49/50, por ordem:

1. **Arrumação do repo** — feita em parte a 2026-08-05: `progress/_historico/` criado com os três
   planos superados, `progress/README.md` novo, `dashboard_v2_design.md` marcado como superado,
   0 links relativos partidos. **Falta** varrer o resto de `docs/design/` (27 ficheiros).
2. **Demo e notificações** — [`docs/defence/gravar_demo.md`](../docs/defence/gravar_demo.md) já
   tem o guião de 3 min. Falta gravar, e falta a captura das **notificações push no telemóvel**,
   que ele pediu explicitamente e ainda não tem procedimento escrito.
3. **Humano, e nenhum destes sou eu que faço:** enviar a tese ao orientador; rodar as 3
   credenciais expostas (PAT do GitHub primeiro, tem `admin: true`); mudar o *Main file path* no
   Streamlit Cloud para `app/dashboard.py`; estudo de utilidade (6–10 pessoas); agradecimentos;
   licença e redacção da declaração de IA com o orientador.
