# Critérios de aceitação da v4 — escritos ANTES do código

> **Estatuto: rascunho para o aluno aprovar ou emendar.** Nenhuma linha de código da v4 deve ser
> escrita antes disto estar fechado. É o que o
> [briefing](PROMPT_dashboard_v4.md) exige, e a razão é histórica e não cerimonial: **sete versões
> desta camada foram rejeitadas**, todas por critério estético, que não tem condição de paragem.
>
> ⚠️ **Declaração de enviesamento.** Quem escreve isto desenhou a v3 e não a consegue ver com
> olhos limpos — o próprio aluno o disse, e tem razão. A defesa contra esse enviesamento não é
> boa vontade: é **cada critério ser decidido por um teste ou por uma medição, nunca por opinião**.
> Onde um critério não for verificável, é um critério mau e deve cair.

## 1. O diagnóstico, nas palavras dele

> *"too laggy. too zoomed out. not responsive enough. not cool UX/UI design. very old-school and
> static."*

E, mais tarde, sobre o produto e não sobre o ecrã: a notícia que interessava não apareceu, e as
que apareceram vinham repetidas.

## 2. O que a medição já disse, e que muda o problema

Isto não é opinião e poupa a discussão mais provável. Os quatro agentes do
[estudo de mercado](market_study_v4.md) convergiram, independentemente, na mesma causa:

- **A lentidão não é CSS nem afinação do Streamlit.** É **carga a frio**, e é **rede**: medido,
  o *backfill* de 8,8 MB analisa-se em **0,30 s** e o `pandas` importa-se em **0,97 s**, contra
  uma carga a frio de **~5,5 s**. O tempo está nas chamadas de rede por render, não no cálculo.
- **O clique já é rápido** — mediana **0,75 s** morno, medida em browser real na sessão 47. A
  queixa de "laggy" aponta para a **primeira** pintura, não para a navegação.
- Portanto **a correcção é de arquitectura**: o worker de 60 s **pré-computa** e escreve um
  instantâneo; a página **lê um ficheiro** e não faz chamadas de rede. É o padrão do
  *data loader* do Observable Framework e é o que o worldmonitor faz visivelmente.

**Consequência para esta decisão:** *sair do Streamlit não é a variável que decide o desempenho.*
Pode sair-se por outras razões (controlo de interacção, transições), mas trocar de framework sem
pré-computar mantém o defeito.

## 2b. A medição que decide a stack (2026-08-06)

O briefing manda **questionar a tecnologia com números** antes de propor trocá-la, e exige um
**protótipo pequeno a provar o ganho antes de reescrever seja o que for**. Está feito:
[`scripts/build_snapshot.py`](../../scripts/build_snapshot.py) pré-computa a grelha inteira com
**as mesmas funções que a app usa** — se fossem reimplementadas, o ficheiro podia divergir do que
a app calcularia e ninguém dava por isso.

| caminho | tempo |
|---|---|
| Construir o instantâneo a frio, doze tickers, rede real | **4,92 s** |
| Calcular ao vivo com a cache HTTP já quente (o que a grelha faz hoje) | **0,870 s** |
| **Ler o instantâneo do disco** | **0,011 s** |

O ficheiro tem **2,4 KB**.

**A leitura, e é a que fecha a discussão mais cara desta linha:** o custo da carga a frio da
grelha são **doze idas à rede**, e desaparece para **11 ms** de leitura de um ficheiro de 2,4 KB.
Contra a construção a frio, é uma razão de ~450×; contra a versão com cache quente, 77×.

⚠️ **O que isto NÃO prova.** Mede a **camada de dados**, não a página inteira. A sobrecarga do
próprio Streamlit — ida ao servidor por interacção, *rerun* do script — continua lá e não é
medida aqui. O P1 (≤1,5 s) **ainda não está provado**.

Mas muda a pergunta, e essa é a parte útil: depois disto, **todo o orçamento que sobra é
sobrecarga de framework**, e passa a ser mensurável isoladamente. Portanto:

> **Sair do Streamlit não é a variável que decide o desempenho.** Trocar de framework sem
> pré-computar mantém o defeito; pré-computar sem trocar de framework remove-o quase todo. A
> migração tem de se justificar por **controlo de interacção** (transições, estado sem *rerun*),
> nunca por "é lento" — porque a lentidão está medida e a causa não é essa.

## 3. A lei do desenho, uma linha

> **A página responde à pergunta antes de mostrar os dados, e nunca faz o utilizador esperar por
> uma resposta que já estava calculada.**

## 4. Critérios binários

Cada um decidido por teste automático ou por medição registada. `P` = desempenho, `C` = conteúdo,
`H` = honestidade (herdados, não negociáveis).

### ⚠️ Correcção ao método de medição (2026-08-07)

**O `first-contentful-paint` é a métrica errada para este painel, e usei-a durante meio dia.**

Medido lado a lado: FCP da v3 **840 ms**, FCP da v4 **864 ms**. Praticamente iguais — porque o
FCP dispara quando o **Streamlit pinta a casca**, não quando os cartões existem. Uma página
completamente vazia de dados marcaria o mesmo tempo.

O que interessa é o **tempo até o conteúdo existir**. Medido com Playwright a esperar pelo
primeiro cartão (v4) e pela primeira linha da watchlist (v3):

| | 1.º pedido, caches vazias | pedido morno |
|---|---:|---:|
| **v3** | **6014 ms** | 1214 ms |
| **v4** | **1987 ms** | 1165 ms |

**As duas leituras honestas, e a segunda importa tanto como a primeira:**

1. **A frio, a v4 é ~3× mais rápida** (6,0 s → 2,0 s), e bate certo com os ~5,5 s que o estudo
   de mercado tinha identificado. É o caso que o utilizador encontra **depois de cada
   implantação e de cada reciclagem do dyno**, que num Basic acontece todos os dias.
2. **A morno não há diferença que se veja** (1,2 s nas duas). As funções de dados da v3 são
   `@st.cache_data`, portanto com a cache quente ela já era rápida. **Dizer que a v4 "é muito
   mais rápida" sem qualificar seria falso.**

O ganho real da v4 não é só velocidade: é **não depender da rede no momento em que alguém
olha**. A v3 morna é rápida enquanto as TTL das caches (300–900 s) não expirarem e enquanto o
Yahoo responder; a v4 lê um ficheiro que o worker escreveu, e a idade desse ficheiro está no
ecrã.

Fica registado porque é a terceira vez nesta sessão que medir a coisa errada quase produziu uma
afirmação falsa — e desta vez a afirmação era **minha, e favorável ao meu próprio trabalho**.

### Desempenho — medido, com número

| # | Critério | Como se decide |
|---|---|---|
| **P1** | **Conteúdo real presente em ≤ 2,5 s no 1.º pedido** (caches vazias), sem rede no caminho crítico. ~~FCP ≤ 1,5 s~~ — ver a correcção acima | Playwright a esperar pelo **primeiro cartão**, servidor reiniciado, mediana de 4 corridas |
| **P2** | **Zero chamadas de rede** no render da grelha; todos os números vêm do instantâneo pré-computado | Contar pedidos de rede na captura; tem de ser 0 para APIs de dados |
| **P3** | O instantâneo tem **idade visível** no ecrã (`as of HH:MM`) e nunca mais de **90 s** em operação normal | Teste sobre o carimbo do ficheiro |
| **P4** | Trocar de intervalo, paginar ou auto-refrescar **não repinta a página** | Captura antes/depois; o cabeçalho não pode piscar |
| **P5** | Nenhuma regressão face à v3 no clique morno (**≤ 0,75 s**, o valor medido) | Playwright, mediana de 10 cliques |

### Conteúdo — o que a página tem de responder

| # | Critério | Como se decide |
|---|---|---|
| **C1** | **Uma linha acima da grelha responde à pergunta do dia** antes de qualquer cartão ("O mercado caiu 1,1%. Dez das doze estão normais.") | Teste de presença + varrimento de vocabulário |
| **C2** | **Estrutura fixa de resposta**: as três perguntas aparecem como **secções nomeadas, na mesma ordem, sempre** — incluindo quando a resposta é "nada aconteceu" | Teste: as três etiquetas existem em todos os estados, incluindo o vazio |
| **C3** | A raridade é **vista, não lida**: tira de ~250 marcas com o dia de hoje assinalado, além da frase | Captura; a tira existe em todos os cartões |
| **C4** | **Porque é que este ticker ficou calado hoje** é consultável, com a margem que faltou ("melhor semelhança 0,42 < chão 0,45") | Página/painel alimentado por `gate_log.py` |
| **C5** | O alerta do Telegram liga **directamente** ao detalhe (`?t=NVDA`) e esse ecrã abre com o dia de hoje | Teste de rota |
| **C6** | Sem regressão: tudo o que a v3 já garante (V1–V8 de [`dashboard_acceptance.md`](dashboard_acceptance.md) §6) continua verdadeiro | A suite `tests/test_dashboard_v3.py` adaptada, a passar |

### Honestidade — herdados, e a violação invalida o trabalho

| # | Critério |
|---|---|
| **H1** | A promessa do produto aparece **uma** vez, não repetida em cada painel |
| **H2** | **Zero números previstos.** Sem alvos de preço, sem "movimento esperado". Inclui a probabilidade da triagem, que é um número sobre o futuro |
| **H3** | Precedentes sempre com a moldura *tema ≠ direcção* |
| **H4** | **Nenhum score que a medição não sustente** |

⚠️ **O H3 tem uma dívida conhecida, e é o próprio aluno a prova.** Ele leu os seus alertas e
interpretou *"notícia negativa, precedentes a subir"* como incoerência — quando é o resultado
central do CS3, medido (consistência de direcção **0,708** contra um chão de acaso de **0,688**).
Se a moldura não chega a quem escreveu a tese, não chega a ninguém. **A v4 tem de a mostrar de
outra forma que não uma frase**, e isso é um critério de conteúdo, não um remendo de texto.

## 5. O que fica de fora, e porquê

- **Trocar de framework como objectivo em si.** Só se justifica depois de P1–P5 estarem medidos
  com o instantâneo pré-computado. Se passarem em Streamlit, a migração não tem argumento.
- **Qualquer coisa que exija carregar o modelo semântico na página de entrada.** Já foi medido:
  custa **6,2 s → 13,7 s** a frio (emenda V6′). Continua proibido pelo P1.
- **Um score agregado de "saúde" ou "convergência".** Proibido pelo H4 — a fusão ganhou em 1 de 3
  orçamentos, e um ganho que depende do orçamento citado não é um resultado.

## 6. A condição de paragem

A v4 está pronta quando **P1–P5 e C1–C6 passam**, medidos e registados, e as capturas a
1920×1080 **e** 1366×768 estão lado a lado com a v3.

**Não está pronta quando parece melhor.** Foi assim que se rejeitaram sete.
