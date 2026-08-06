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

## 3. A lei do desenho, uma linha

> **A página responde à pergunta antes de mostrar os dados, e nunca faz o utilizador esperar por
> uma resposta que já estava calculada.**

## 4. Critérios binários

Cada um decidido por teste automático ou por medição registada. `P` = desempenho, `C` = conteúdo,
`H` = honestidade (herdados, não negociáveis).

### Desempenho — medido, com número

| # | Critério | Como se decide |
|---|---|---|
| **P1** | **Primeira pintura com conteúdo real em ≤ 1,5 s** a frio, sem rede no caminho crítico | Playwright, `first-contentful-paint`, 5 corridas, mediana |
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
