# Backlog do aluno — pedidos por trabalhar

> Registado a **2026-08-05** tal como o aluno o ditou. **Actualizado a 2026-08-06** com o que
> entretanto foi feito — a versão anterior dizia "nada aqui foi analisado" e isso deixou de ser
> verdade, e um ficheiro de estado que mente sobre o seu próprio estado é pior do que não existir.
>
> Ordem = a ordem em que foi ditada, não prioridade.

## Ponto de situação (2026-08-06)

| # | pedido | estado |
|---|---|---|
| 1 | Refazer o painel (**v4**) | **investigação feita, código não começado** — ver quadro abaixo |
| 2 | Literatura com os PDF reais | **à espera dele.** Infra pronta; 44/59 já legíveis, 14 precisam da conta ISEP |
| 3 | Latência quase-real | **⭐ MEDIDA, e a explicação que aqui estava era falsa** — ver §3 |
| 4 | Melhorar o guia | **em curso.** 85 → 89 slides, 4 frames novos |
| 5 | Rever a escrita | **por começar** |
| 6 | Varrer TODO que restam | **✅ feito 2026-08-07: zero TODO reais no código** — ver §6 |
| 6bis | Mecanismo de alertas | **⭐ (a), (b) e (c) FEITOS.** Cobertura medida: **88,5%** |
| 6ter | Comparação de mercado na tese | **⭐ pontos 1 e 2 FEITOS 2026-08-07** (produtos nomeados, fonte primária, EN+PT); ponto 3 impossível sem observar no dia — ver §6ter |
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

## 1. Refazer o painel por completo (v4)

### Onde é que isto está, exactamente (verificado a 2026-08-06)

O briefing manda uma ordem — estudo de mercado → questionar a tecnologia com números → critérios
de aceitação → **só então** código. Estado passo a passo:

| passo do briefing | estado |
|---|---|
| 1. Estudo de mercado | ✅ [`market_study_v4.md`](../docs/design/market_study_v4.md), 786 linhas, 69 achados, 12 produtos |
| 2. Questionar a stack com números | ✅ **medido 2026-08-06**: 4,92 s → **0,011 s** (ficheiro de 2,4 KB) |
| 3. `dashboard_v4_acceptance.md` **antes** do código | ⚠️ **rascunho escrito 2026-08-06 — falta ele aprovar/emendar** |
| 4. Código | ❌ não começado (`app/` tem só a v1 e a v3) |

**O passo 3 tem agora um rascunho:**
[`dashboard_v4_acceptance.md`](../docs/design/dashboard_v4_acceptance.md) — P1–P5 (desempenho,
todos com número e forma de medir), C1–C6 (conteúdo) e H1–H4 (honestidade, herdados). **Falta o
aluno lê-lo e emendá-lo**, e é ele que decide, não quem o escreveu: quem escreveu desenhou a v3 e
está enviesado, e isso está declarado no topo do documento.

A defesa contra esse enviesamento não é boa vontade — é cada critério ser decidido por **um teste
ou uma medição**. Onde um critério não for verificável, é mau e deve cair.

**Nota que o estudo de mercado já traz, e poupa uma discussão:** a queixa de "lento" não é CSS
nem afinação do Streamlit. É **carga a frio** — 8,7 MB de *backfill* analisados em tempo de
pedido. A recomendação é **pré-computar para um instantâneo estático** no worker de 60 s, que é
o padrão que o worldmonitor usa e que o Observable Framework formaliza. Isso é uma decisão de
**arquitectura**, e é ela que decide se se fica no Streamlit ou não.

⚠️ Os quatro cépticos que deviam contestar esse estudo morreram no limite de gasto — está
escrito no topo do documento. Nada dali entra na tese sem reconfirmação.

---

### O pedido original, como foi ditado

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

### ⚠️ MEDIDO a 2026-08-07 — e o parágrafo que estava aqui era uma hipótese, e é falsa

O que estava escrito: *"a mediana mostrada (208 min, n=44) inclui o histórico do cron antigo,
portanto o número no ecrã e a latência actual não são a mesma coisa"*. Verdade a meias, e a metade
que faltava é a que interessa: **separar as eras não resolve nada.** Desce de **196 min** (cron)
para **143 min** (worker a 60 s) e fica lá.

Relatório completo: [`evaluation_latency.md`](../docs/evaluation/evaluation_latency.md), gerado por
`python scripts/evaluate_latency.py --escrever` sobre os **101 alertas entregues** que têm carimbos.

| componente | mediana | de quem é |
|---|---|---|
| publicação → detecção | **158 min** | da fonte (e é um **limite inferior**) |
| detecção → entrega | **1 s** | nosso |

**O nosso lado do sistema não é o problema.** O tempo está todo na descoberta, por duas razões que
nenhuma infra-estrutura compra: o Finnhub *company news* não é um canal em tempo real, e **a
manchete mais recente do feed não é a mais recente relevante** — num teste ao vivo (2026-08-07,
14 h UTC) o feed da NVDA trazia 250 manchetes com a mais recente às 11:39, mas das 30 que
mencionavam a empresa a mais recente era de **08:14**.

**O que já foi feito com isto:** o painel passou a mostrar as **duas** componentes (um número
agregado não distingue "somos lentos" de "a fonte é lenta", e as duas afirmações pedem coisas
opostas); a tese EN+PT corrigiu o Cap. 6, que afirmava que a latência está **limitada pelo ciclo
de sondagem**; o `gravar_demo.md` deixou de o pôr a dizer que "o número vai descer à medida que o
histórico se renova"; e o guia ganhou um frame que ensina o achado.

**O que ele tem de decidir, porque não é decisão minha:** a única forma de comprar latência a
sério é um **serviço de notícias pago** — e a restrição §5.2 do projecto é *só APIs gratuitas*.
Portanto, ou a limitação fica como está (medida, honesta, e escrita como Trabalho Futuro), ou a
restrição fundadora muda. Recomendação: **fica como está.** Uma limitação medida vale mais numa
tese do que uma capacidade comprada, e mudar a restrição a cinco semanas da entrega abre trabalho
sem fechar nenhuma RQ.

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

### ✅ Feito a 2026-08-07: pontos 1 e 2. ⚠️ Ponto 3: não, e a razão importa

**Ponto 1 (nomes) e ponto 2 (a vaga de 2025-26): feitos**, no §2.7 das duas teses. Nomeados os dois
produtos que reclamam **exactamente** a pergunta central deste trabalho:

- **Robinhood Cortex** (março 2025) — propósito declarado pela própria empresa: *"answer the age-old
  question of, 'Why is this stock going up or down today?'"*
- **Google Finance "key moments"** (junho 2026) — *"explain why a stock moved"*, anotados no gráfico.

**A regra que apliquei é mais estreita do que o habitual, e é por causa do aviso que está neste
ficheiro:** são afirmações sobre produtos de terceiros, e um arguente pode abrir a app e verificar.
Portanto **só entrou na tese o que está na página do próprio fornecedor**, citado com data de
observação (2026-08-07). Li cobertura de imprensa para encontrar as fontes e **descartei-a** como
base de afirmação — é por isso que a tabela diz *"não declarado"* e não *"não faz"*: a fonte
primária não diz, e eu não sei.

O parágrafo novo **admite a sobreposição** em vez de a minimizar (estes produtos respondem à mesma
pergunta para muito mais gente, e em linguagem simples, que era um objetivo aqui) e põe a diferença
onde ela existe: um resumo gerado é uma **afirmação**; isto entrega a afirmação **com a evidência
anexada**. A divulgação da própria Robinhood — *"there is no guarantee that AI will improve
investing performance"* — é sobre desfechos, não sobre se uma explicação individual está certa.

**⚠️ Ponto 3 (o mesmo acontecimento lado a lado): NÃO FEITO, e não podia ser.** Exigiria ter
observado esses produtos **no dia** da NVDA. Reconstruí-lo agora seria fabricar evidência, e é a
única regra deste projecto que não tem excepção. **Se quiseres esse quadro — e é o que daria mais
força ao capítulo — tens de escolher um dia em que uma das doze empresas se mexa muito, e capturar
os ecrãs nesse dia.** Chega uma captura por produto.

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

## 7. Identidade visual NOVA — logótipo e mascote

**Ditado a 2026-08-06:** algo que **dê nas vistas**, com **olhos**, ou o jacaré/crocodilo, ou uma
mascote — *"tipo uma marca registada"*.

**Clarificado por ele no mesmo dia, e é o que manda:** *"a 'Stare' era má. Estou a falar de coisa
**nova**."* Portanto **não é para ressuscitar** nenhuma das marcas anteriores. É conceito novo.

### O que serve de material, e não de travão

Só duas coisas do passado interessam aqui, e nenhuma delas é um veto:

1. **O teste de aceitação, que é o que evita o oitavo redesenho rejeitado.** Está em
   [`brand.md`](../docs/design/brand.md): legível a **16 px** com silhueta reconhecível; funciona
   a **preto e branco**; funciona em fundo **claro e escuro**; **uma ideia só**, não três; não
   contradiz a postura do produto. É o mesmo padrão dos critérios de aceitação do painel — sem
   condição de paragem escrita, o ciclo repete-se.
2. **Porque é que a marca-olho anterior caiu**, útil só como armadilha a evitar, não como
   proibição: o sobrolho fundia-se com o olho aos 16 px e a linha de mercado desaparecia; metia
   três metáforas num ícone. Um olho **pode** funcionar — o que não funciona é um olho **mais**
   sobrolho **mais** linha de mercado no mesmo glifo.

### A separação que provavelmente destrava isto

**Logótipo e mascote são duas peças com requisitos diferentes, e o projecto tratou-as como uma.**

- O **logótipo** tem de sobreviver a 16 px. É aí que morrem os desenhos com detalhe.
- A **mascote** não tem esse constrangimento nenhum: vive grande — avatar do canal, capa dos
  slides, guia de estudo, ecrã inicial. É aí que cabem olhos, expressão, personalidade, "marca
  registada".

⚠️ **Já existiu uma mascote, e está recuperável — mas NÃO está no repositório.**
Correcção a uma afirmação minha de 2026-08-06, que estava errada: eu disse que
`app/assets/investigator.svg` estava lá esquecido. **Não está.** Foi **apagado** no commit
`609a30b` ("Auditoria de consistência: 3 restos da marca antiga corrigidos"), e a pasta
`app/assets/` só tem hoje os ficheiros da marca "The Tail".

O ficheiro continua na história do git (3 252 bytes, jacaré-detective com *deerstalker*, monóculo
e lupa, desenhado na sessão 28) e recupera-se com:

```bash
git show 2ce21e4:app/assets/investigator.svg > app/assets/investigator.svg
```

Vale a pena **ver antes de desenhar do zero** — pode ser o ponto de partida ou um descarte
informado. Mas quem o for buscar deve saber que foi retirado **de propósito**, por não estar
ligado a nada depois da mudança de marca.

### Como fazer isto sem repetir o ciclo

1. Escrever primeiro o que a marca tem de **dizer** (uma frase), e só depois desenhar.
2. Produzir **três** direcções genuinamente diferentes, não três variações da mesma.
3. **Renderizar cada uma a 16, 32, 88 e 512 px** e comparar lado a lado **com a marca actual como
   controlo** — foi assim que a decisão da sessão 45 se tomou, e é a única parte do método
   anterior que vale a pena manter.
4. Decidir com as imagens à frente, não com descrições.

## 6. Quaisquer pendências que restem nos TODOs do repositório

Varrer [`docs/planos/CHECKLIST.md`](../CHECKLIST.md), os `TODO` no código e nos `.tex`, e o que sobrar do
[`v3_backlog.md`](../docs/design/v3_backlog.md).

### ✅ Varredura feita a 2026-08-07 — e o resultado é "não há nada", com prova

`TODO|FIXME|XXX|HACK` em todo o repositório fora do `.venv`: **zero marcadores reais no código.**
A maioria dos acertos era a palavra portuguesa **TODOS** ("todos os tickers"), que o padrão apanha
por acidente — a mesma classe de falso positivo que já apareceu três vezes neste projecto (a
máscara do narrador, o "price target" dentro de "No price targets", o "not a forecast" que contém
"forecast").

Os únicos `% TODO` verdadeiros são **dois, nas duas teses**: dedicatória e agradecimentos. **Ficam
por escrever de propósito** — são a voz do aluno, e escrever a gratidão dele por ele seria a única
coisa neste repositório que não se pode verificar.

**Uma caixa fechada por não ter assunto:** o `TRACKER.md` tinha, desde a sessão 4, *"fixar fonte
primária para a quota de retalho no volume"*. A frase que a motivava era de um rascunho e
desapareceu na reescrita S1–S9. Hoje o Cap. 1 afirma **propriedade** (Gallup) e o Cap. 2
**comportamento** (Welch), com escala em SIFMA — nenhuma é quota de volume, e as três estão
verificadas em fonte primária. Uma caixa aberta sobre um texto que já não existe manda procurar um
problema inexistente, e por isso foi fechada com a razão escrita ao lado em vez de apagada.

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
