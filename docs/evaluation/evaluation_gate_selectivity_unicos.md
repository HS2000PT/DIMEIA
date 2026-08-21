# O portão de triagem separa notícias ou empresas?

> **Gerado por** `scripts/evaluate_gate_selectivity.py`. Não editar à mão.
> **Fonte:** `origin/alerts-history:predictions_log.jsonl` — as decisões **realmente tomadas em produção**.
> **Decisões pontuadas:** 36925 · **período:** 2026-07-22 a 2026-08-20 ·
> **piso implantado:** 0.5

## 1. A distribuição do score, empresa a empresa

| Ticker | Decisões | Mín | Mediana | Máx | Amplitude | O piso 0.5 |
|---|---|---|---|---|---|---|
| AAPL | 3893 | 0.423 | 0.457 | 0.472 | 0.049 | nunca passa |
| JNJ | 3803 | 0.294 | 0.298 | 0.324 | 0.029 | nunca passa |
| AMD | 3549 | 0.549 | 0.633 | 0.641 | 0.093 | sempre passa |
| XOM | 3218 | 0.390 | 0.399 | 0.407 | 0.017 | nunca passa |
| TSLA | 3139 | 0.545 | 0.586 | 0.630 | 0.086 | sempre passa |
| AMZN | 3105 | 0.411 | 0.568 | 0.571 | 0.159 | o piso decide |
| MSFT | 3063 | 0.417 | 0.557 | 0.561 | 0.144 | o piso decide |
| NVDA | 2939 | 0.457 | 0.475 | 0.501 | 0.044 | o piso decide |
| GOOGL | 2918 | 0.444 | 0.513 | 0.528 | 0.083 | o piso decide |
| NFLX | 2628 | 0.388 | 0.439 | 0.486 | 0.097 | nunca passa |
| META | 2566 | 0.498 | 0.506 | 0.545 | 0.047 | o piso decide |
| JPM | 2104 | 0.237 | 0.241 | 0.258 | 0.020 | nunca passa |

- **Amplitude média DENTRO de cada empresa:** `0.072`
- **Amplitude ENTRE as medianas das empresas:** `0.392`
- **Razão entre/dentro: 5.4×**

## 2. O resultado

- Empresas que passam **sempre**: 2 — AMD, TSLA
- Empresas que **nunca** passam: 5 — AAPL, JNJ, JPM, NFLX, XOM
- Empresas em que o piso **chega a decidir**: 5 — AMZN, GOOGL, META, MSFT, NVDA

> **Em 48% dos títulos distintos o resultado estava determinado pela
> EMPRESA antes de a manchete ser lida.**

⚠️ **Duas contagens, e a diferença entre elas importa.** Contado por **decisão registada**, o
valor é `60%` sobre 36925 decisões; contado por **título distinto**, é
`48%` sobre 982. A diferença não é ruído: o sistema repontua os mesmos
títulos a cada ciclo de 60 segundos, e a duplicação é **maior nas empresas com menos notícias**
(o pior caso é a JNJ, com 181 decisões por título), que são
precisamente as que nunca passam o piso. Contar decisões empurra portanto a fração para cima, ou
seja **na direção que convém à conclusão**. O número a citar é o dos títulos distintos.

Isto explica, de uma só vez, as três queixas do utilizador: recebe demasiados alertas (as
empresas que passam sempre saturam o tecto diário), recebe-os sempre das mesmas, e nunca recebe
nada sobre as restantes, aconteça o que acontecer.

É o mesmo defeito que a dissertação já identifica nos preços — um limiar fixo mede a
volatilidade da empresa e não a raridade do dia — mas um nível acima, sobre o score do modelo.

## 3. E se o piso fosse relativo a cada empresa?

A correcção aparentemente óbvia é tornar o piso relativo, tal como o *z*-score fez para os
preços. Simulada sobre as mesmas decisões:

| Regime | Passariam | Empresas representadas | Concentração |
|---|---|---|---|
| piso fixo em 0.5 (actual) | 17913 (49%) | 7/12 | AMD com 3549 |
| top 5% de cada empresa | 2983 (8%) | 12/12 | JNJ com 541 |
| top 10% de cada empresa | 7250 (20%) | 12/12 | AAPL com 1641 |
| top 20% de cada empresa | 9861 (27%) | 12/12 | AAPL com 1641 |

**Resolve metade e cria outro problema.** Todas as empresas passam a estar representadas, o que
é o efeito pretendido. Mas nas empresas cujo score é quase constante — as de amplitude mais
baixa nesta tabela — o percentil cai **em cima** da constante e quase todas as decisões empatam
acima dele. O regime relativo passa a seleccionar por desempate, que é exactamente o artefacto
que a dissertação documenta noutro sítio.

## 4. Leitura honesta

A conclusão não é que falta afinar o piso. É mais funda, e é coerente com o resultado negativo
já reportado para a questão da triagem:

> **Dentro de uma empresa, o score do modelo quase não varia com a manchete.**
> A amplitude média dentro de cada empresa é `0.072`, contra `0.392` entre empresas.
> Nenhuma regra de decisão aplicada a este score o pode tornar sensível à notícia, porque a
> informação que distinguiria uma manchete da seguinte não está lá.

O que isto implica para o produto é que **o score da triagem não deve ser o critério principal
de alerta**. Serve para ordenar entre empresas, que é para o que tem informação, e para ser
mostrado com a ressalva que já tem. O critério que decide *se* se interrompe alguém precisa de
assentar em quantidades que variem com o acontecimento: o movimento do próprio dia, a força da
evidência recuperada, e a novidade da história.
