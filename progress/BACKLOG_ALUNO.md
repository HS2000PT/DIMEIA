# Backlog do aluno — pedidos por trabalhar

> Registado a **2026-08-05** tal como o aluno o ditou. **Actualizado a 2026-08-06** com o que
> entretanto foi feito — a versão anterior dizia "nada aqui foi analisado" e isso deixou de ser
> verdade, e um ficheiro de estado que mente sobre o seu próprio estado é pior do que não existir.
>
> Ordem = a ordem em que foi ditada, não prioridade.

## Ponto de situação (2026-08-06)

| # | pedido | estado |
|---|---|---|
| 1 | Refazer o painel | **por começar.** Briefing e estudo de mercado prontos |
| 2 | Literatura com os PDF reais | **à espera dele.** Infra pronta; 44/59 já legíveis, 14 precisam da conta ISEP |
| 3 | Latência quase-real | **por começar** |
| 4 | Melhorar o guia | **em curso.** 85 → 88 slides, 3 frames novos |
| 5 | Rever a escrita | **por começar** |
| 6 | Varrer TODO que restam | **por começar** |
| 6bis | Mecanismo de alertas | **⭐ (a), (b) e (c) FEITOS.** Cobertura medida: **88,5%** |
| 6ter | Comparação de mercado na tese | **material salvo; tese por actualizar** |
| 7 | Refazer o logótipo (olhos/mascote) | **por decidir.** Já caiu 2× por medição — ler §7 |

## ⚠️ Estado do que está NO AR (verificado a 2026-08-06, a renderizar)

| camada | estado |
|---|---|
| **Painel web** | ✅ **v3 no ar**, verificado por captura: 12 cartões, logótipos reais, contagens empíricas, 293 alertas no histórico |
| **Worker de alertas** | ❌ **desactualizado.** Corre o código da sessão 48. A correcção do tecto por materialidade está no GitHub, **não no Heroku** |

O `web` e o `worker` saem do **mesmo *slug***, portanto o ecrã está actual e a lógica que decide
**que notícia chega ao telemóvel** não está. Um `git push` para o GitHub **não implanta**: o
Heroku foi implantado pela API de Sources/Builds na sessão 48 e não está ligado a auto-deploy.

**Feito nesta sessão, com prova:** o tecto diário passou a ser servido por **materialidade** e não
por ordem de chegada (era isto que fazia a notícia da NVDA desaparecer); a repetição da mesma
história noutras palavras passa a ser apanhada pela **manchete**; e as duas coisas estão escritas
na tese EN+PT, nos dois decks, no guia e no autoteste, como **caso de falha diagnosticado**.

**O que falta do 6bis, e é o mais valioso que resta:** ninguém mediu **quanto** é que a fonte de
notícias perde. É a alínea (c), e é o que está a ser feito a seguir.

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

## 7. Refazer o logótipo — mais apelativo, com olhos ou mascote

**Ditado a 2026-08-06:** algo que **dê mais nas vistas**. *"Acho que temos de ter olhos, ou o
jacaré/crocodilo, ou uma mascote — tipo uma marca registada."*

### ⚠️ Isto já foi tentado duas vezes, e as duas vezes caiu por medição

Fica escrito porque é a informação de que ele vai precisar quando decidir, não para o travar.
**A decisão é dele.**

- **Sessão 40 — "The Stare".** Era exactamente isto: olho de crocodilo, íris dourada, pupila em
  fenda, sobrolho, sobre uma linha de mercado. Ele escolheu-a de entre três propostas.
- **Sessão 42 — substituída.** Três razões, e só a primeira é estética:
  1. **Falhava a 16 px** — o sobrolho fundia-se com o olho e a linha de mercado desaparecia. E
     16 px é onde vive um *favicon*, ou seja o sítio onde a marca é mais vista.
  2. Metia **três metáforas** num só ícone.
  3. Um **olho de predador com pupila em fenda** é contra-mensagem num produto cuja posição
     fundadora é *não prever* e não caçar ninguém.
- **Sessão 45 — reconfirmada com alternativas construídas a sério.** Foram feitas duas ("Jaws",
  as maxilas do indicador Williams Alligator, que seria a melhor *história*; e o monograma
  "Gator G") e comparadas às escalas reais contra o critério escrito. **A "Tail" ganhou.** A
  "Jaws" desfaz-se num `<` aos 16 px. Os ficheiros ficaram no repositório como registo:
  [`logo-jaws.svg`](../app/assets/logo-jaws.svg),
  [`logo-gator-g.svg`](../app/assets/logo-gator-g.svg).

O teste de aceitação está escrito em [`brand.md`](../docs/design/brand.md) §"Teste de aceitação
da marca" e é este: legível a **16 px**; funciona a **preto e branco**; funciona em fundo claro
**e** escuro; **uma só ideia**, não três; **não contradiz a postura do produto**.

### O caminho que provavelmente resolve isto sem repetir o erro

**Logótipo e mascote não são a mesma peça, e o projecto tem-nos confundido.** Uma marca tem de
sobreviver a 16 px; uma mascote não — vive grande, na capa, no canal, nos slides, no guia.

- **Já existe uma mascote** e está esquecida:
  [`app/assets/investigator.svg`](../app/assets/investigator.svg), um jacaré-detective com
  *deerstalker*, monóculo e lupa, desenhado na sessão 28. Foi retirada da app na sessão 41 por
  parecer órfã. **Recuperá-la e usá-la em grande é provavelmente o que ele quer**, e não custa
  o critério dos 16 px.
- Se ainda assim quiser **olhos na marca pequena**, o desenho tem de passar o mesmo teste — e o
  registo diz que a versão anterior não passava. Vale a pena tentar de novo com uma forma mais
  simples (um olho **sem** sobrolho e **sem** linha de mercado é uma ideia só), mas **testar aos
  16 px antes de decidir**, com a marca actual como controlo, que foi assim que a decisão anterior
  se tomou.

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
