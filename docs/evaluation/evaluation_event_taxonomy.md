# Taxonomia de tipos de evento — agrupamento não supervisionado das manchetes

> Gerado por `scripts/evaluate_event_taxonomy.py` em 2026-07-30 23:55 UTC.
> **Aditivo.** Não altera `models/` (exceto o artefacto novo `event_taxonomy.json`),
> o dataset de triagem, nem qualquer .md de avaliação existente.

## A pergunta

Os embeddings MiniLM nunca viram um rótulo de tipo de evento. Organizam mesmo assim o
fluxo de notícias em grupos que coincidem com uma taxonomia escrita por uma pessoa?

Isto importa para o produto e não só para a curiosidade: sem tipo de evento, a
recuperação só sabe comparar por semelhança geral, que é exatamente o mecanismo que
faz uma manchete positiva recuperar um cacho de precedentes negativos (Caso 3).

## Como a referência foi construída (e porque é credível)

A referência é uma **rubrica de palavras-chave** publicada em
`investigator/historical_kb/taxonomy.py`, escrita a partir da lista de tipos de evento
e **commitada antes de qualquer agrupamento ter corrido** — o histórico do git é o
pré-registo. Sem essa ordem, a rubrica podia ter sido afinada até concordar com os
grupos, e a medição não valeria nada.

A rubrica é de **alta precisão e baixa cobertura** por desenho. Devolve `None` quando
nenhum padrão dispara e também quando **mais do que um** dispara, porque uma manchete
que é ao mesmo tempo resultados e ação de analista é genuinamente ambígua.

Cobertura: **11,889 de 78,933** manchetes (**15.1%**).
Todos os números de pureza abaixo são sobre este subconjunto, e o `n` vai sempre junto.

| Tipo de evento | Manchetes cobertas |
|---|---:|
| `earnings` | 2,604 |
| `guidance` | 23 |
| `analyst` | 1,222 |
| `product` | 1,047 |
| `legal_regulatory` | 1,160 |
| `ma` | 542 |
| `personnel` | 17 |
| `macro_market` | 5,274 |
| **(sem rótulo)** | **67,044** |

## Escolha de k

Silhueta calculada sobre uma subamostra de 10,000 pontos (é O(n²); com
78,933 manchetes a matriz completa não cabe em memória).

| k | Silhueta | Pureza vs rubrica | n avaliado |
|---:|---:|---:|---:|
| 6 | +0.050 | 0.635 | 11,889 |
| 8 | +0.068 | 0.599 | 11,889 |
| 10 | +0.081 | 0.603 | 11,889 |
| 12 | +0.078 | 0.706 | 11,889 |
| 14 | +0.080 | 0.711 | 11,889 |
| 16 | +0.082 | 0.714 | 11,889 |
| 18 ← | +0.084 | 0.712 | 11,889 |
| 20 | +0.083 | 0.723 | 11,889 |

**k\* = 18**, pela silhueta.

## Resultado

- **Pureza contra a rubrica: 0.712** sobre 11,889 manchetes rotuladas.
- **Estabilidade entre sementes:** ARI 0.786 
  (mín 0.749, máx 0.836, 3 sementes contra a semente 0).
- **k-means vs hierárquico** na mesma subamostra de 5,000: silhueta +0.085 vs +0.053; pureza 0.712 vs 0.472.
- **Confiança** (cosseno ao centróide atribuído): mediana 0.610, 1.º decil 0.388.

### Os grupos

| # | Rótulo | n | Termos de topo (TF-IDF) | Manchete mais próxima do centróide |
|---:|---|---:|---|---|
| 0 | `legal_regulatory` | 8,314 | google, microsoft, says, musk, deal | 'States' massive Google antitrust probe will expand into search and An |
| 1 | `analyst` | 2,196 | option activity, activity, option, active, aapl | After Hours Most Active for Aug 25, 2023 : AAPL, VHNA, QQQ, JNJ, MSFT, |
| 2 | `ma` | 5,314 | oil, exxon, chevron, mobil, exxon mobil | A Tale of 2 Oils: Why ExxonMobil and Chevron Headed in Different Direc |
| 3 | `macro_market` | 3,596 | wall, stocks wall, wall st, st, wall street | US STOCKS-Wall St rises on hopes of less-aggressive Fed as business ac |
| 4 | `analyst` | 6,248 | cola, coca, coca cola, jpmorgan, buys | JPMorgan, Goldman Sachs Are Making Their Biggest Buyouts In Years |
| 5 | `earnings` | 3,657 | earnings, q3, estimates, q2, q1 | Q2 Earnings: An Early Preview |
| 6 | `macro_market` | 8,432 | stock, movers, dow, buy, dow movers | Amazon Is Soaring, and the Stock Is Probably Still a Great Buy |
| 7 | `analyst` | 4,407 | tesla, tesla stock, ev, stock, musk | The Future Remains Bright for Tesla Stock as Near-Term Issues Clear Up |
| 8 | `legal_regulatory` | 3,952 | walmart, amazon, target, retail, walmart wmt | Walmart Makes a Brilliant Move to Better Compete With Amazon |
| 9 | `product` | 2,455 | apple, apple stock, stock, apple aapl, aapl | What's New With Apple Stock? |
| 10 | `analyst` | 3,262 | nvidia, nvidia stock, stock, nvda, nvidia nvda | Nvidia Stock: Looking At The Big Picture |
| 11 | `analyst` | 2,774 | sector update, sector, update, fundamental, guru fundamental | Energy Sector Update for 01/06/2020: XOM, CVX, COP, SLB, OXY, YUMA, CE |
| 12 | `macro_market` | 2,398 | dividend, dividend stocks, stocks, buy, stocks buy | The 3 Most Promising Dividend Stocks to Own Now |
| 13 | `macro_market` | 5,142 | stocks, futures, stocks futures, 500, markets | A Peek Into The Markets: US Stock Futures Surge Ahead Of Earnings |
| 14 | `macro_market` | 1,772 | buffett, warren, warren buffett, buffett stocks, stocks | The Ultimate Warren Buffett Stock to Buy Right Now |
| 15 | `macro_market` | 8,051 | stocks, buy, stocks buy, best, growth | The 3 Best Stocks to Buy Right Now |
| 16 | `product` | 2,427 | ai, intelligence, artificial, artificial intelligence, ai stocks | A Bull Market in Artificial Intelligence Is Coming: 2 AI Stocks to Buy |
| 17 | `macro_market` | 4,536 | etf, etfs, investing radar, investing, radar | Should iShares Russell Top 200 Growth ETF (IWY) Be on Your Investing R |

## Os dois controlos, sem os quais a pureza não significa nada

### 1. A pureza bruta está inflacionada

A pureza com rotulagem por maioria **inflaciona** quando a referência é desequilibrada
e k é grande. Aqui um único tipo (`macro_market`) vale 44.4% dos rótulos, e há
18 grupos: muitos ficam com esse rótulo quase por omissão. O controlo é a mesma
métrica sobre uma atribuição **aleatória com exatamente os mesmos tamanhos de grupo**.

| Pureza medida | Aleatório (mesmos tamanhos) | Tudo-no-maioritário |
|---:|---:|---:|
| **0.712** | 0.444 | 0.444 |

O ganho real sobre o acaso é **+0.269**, não 0.712.

### 2. Por evento, ou apenas por assunto?

Este é o controlo decisivo. Se os grupos se alinharem mais com a **empresa** ou o
**setor** do que com o **tipo de evento**, então o agrupamento está a redescobrir o
assunto, e uma taxonomia de eventos não sai daqui.

Duas exigências de método, ambas necessárias para a comparação ser válida:

- **A pureza não serve aqui.** O seu valor depende de quantas classes a referência tem
  (8 tipos vs 14 tickers vs
  5 setores) e de quão desequilibradas são;
  comparar purezas entre referências diferentes é comparar coisas incomparáveis. A
  **informação mútua ajustada (AMI)** é corrigida para o acaso e para a cardinalidade.
- **As mesmas linhas.** Todas as três medidas correm sobre as 11,889
  manchetes que a rubrica cobre. Medir eventos numa amostra e tickers noutra não
  compara nada.

| Referência | AMI com os grupos |
|---|---:|
| **Tipo de evento** (rubrica) | **0.358** |
| Ticker | 0.188 |
| Setor | 0.130 |

## Leitura honesta

O alinhamento com **tipo de evento** (AMI 0.358) é superior ao
alinhamento com **assunto** (ticker 0.188, setor 0.130),
medido nas mesmas linhas e com uma métrica corrigida para o acaso e para a
cardinalidade. Os embeddings estão de facto a recuperar estrutura de tipo de
evento que ninguém lhes ensinou — não apenas a agrupar por empresa.

Este resultado merece uma ressalva que o torna mais útil e não menos. A leitura
*qualitativa* da tabela dos grupos sugere o contrário: vários grupos têm por
termos de topo nomes de empresas (`tesla, ev, musk`; `nvidia, nvda`; `apple,
aapl`) e de setores (`oil, exxon, chevron`). As duas observações conciliam-se
assim: o espaço de representação codifica assunto **e** tipo de evento ao mesmo
tempo, e num corpus de 15 tickers o assunto é o eixo mais visível a olho, porque
os nomes das empresas dominam os termos de topo. Medido com uma métrica
corrigida, é o eixo do acontecimento que explica mais da partição.

**Consequência de desenho.** Há sinal de tipo de evento nos embeddings, mas a
separação é fraca em termos absolutos (silhueta +0.084, ver
abaixo) e a atribuição de rótulos depende inteiramente de uma rubrica que só
cobre 15.1% do corpus. Isso chega para caracterizar o corpus e
não chega para filtrar precedentes em produção: um filtro por tipo de evento
errado remove precedentes válidos em silêncio, que é pior do que não filtrar. A
taxonomia fica como artefacto descritivo, e o caminho sustentado pela evidência é
a rubrica — transparente e correta onde responde.

### O confundimento que um arguente levanta primeiro

A rubrica atribui rótulos a partir de **palavras que estão na manchete**, e os
embeddings codificam essas mesmas palavras. Uma manchete rotulada `earnings` contém
quase de certeza a palavra *earnings*, pelo que agrupar por semelhança de texto vai
aproximá-la de outras que também a contêm. Parte do AMI de tipo de evento está,
portanto, garantida por construção, e o número não deve ser lido como prova de que os
embeddings "percebem" tipos de acontecimento.

O que o confundimento **não** destrói é a comparação, e é isso que aqui se usa: a
referência de ticker sofre exatamente do mesmo problema — os nomes das empresas também
estão nas manchetes, muitas vezes mais do que uma vez e no início. As três referências
estão em pé de igualdade quanto a este viés, pelo que a ordenação entre elas continua
informativa mesmo que os valores absolutos estejam inflacionados.

### A silhueta é baixa, e isso também conta

A melhor silhueta é +0.084. Em termos absolutos é fraca: os grupos
não estão bem separados, sobrepõem-se. E a curva é **plana** — de k=10 a k=20 varia
entre +0.081 e +0.084, uma amplitude de 0.003. O k\* escolhido é, portanto,
fracamente determinado: k=16 ou k=12 serviriam quase igualmente bem. Reportado assim
em vez de se apresentar k=18 como se fosse um ótimo nítido.

### Limitações que se mantêm

1. **A referência é uma rubrica, não um humano.** Mede-se concordância entre dois
   métodos, não com a verdade. A rubrica erra onde a linguagem é indireta, e essas
   manchetes contam contra os grupos mesmo quando os grupos estão certos.
2. **A cobertura é parcial** (15.1%): a pureza nada diz sobre as
   manchetes que a rubrica não apanha, que são a maioria.
3. **Dois tipos são residuais** neste corpus — `guidance` (23) e `personnel` (17). Na
   prática a pureza mede-se sobre seis tipos, não oito.
4. **k foi escolhido pela silhueta, não pela pureza.** De propósito: escolher k por
   pureza seria afinar o método não supervisionado contra a sua própria avaliação.

## O que fica

O artefacto (`models/event_taxonomy.json`) é NumPy puro — produto interno e argmax,
sem scikit-learn em produção — e fica no repositório como camada **descritiva**: serve
para caracterizar o corpus e para sustentar a conclusão acima. **Não** está ligado à
recuperação nem aos alertas, e a razão é a medição desta página, não uma falta de
tempo.

O caminho que a evidência sustenta, se houver tempo, é a rubrica: transparente,
verificável, sem treino, e correta onde responde — ao custo de só responder em
15.1% dos casos.
