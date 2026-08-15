# O portão de triagem separa notícias ou empresas?

> **Gerado por** `scripts/evaluate_gate_selectivity.py`. Não editar à mão.
> **Fonte:** `origin/alerts-history:predictions_log.jsonl` — as decisões **realmente tomadas em produção**.
> **Decisões pontuadas:** 4366 · **período:** 2026-07-22 a 2026-08-15 ·
> **piso implantado:** 0.5

## 1. A distribuição do score, empresa a empresa

| Ticker | Decisões | Mín | Mediana | Máx | Amplitude | O piso 0.5 |
|---|---|---|---|---|---|---|
| AAPL | 963 | 0.423 | 0.457 | 0.472 | 0.049 | nunca passa |
| AMD | 963 | 0.549 | 0.632 | 0.633 | 0.085 | sempre passa |
| JNJ | 876 | 0.298 | 0.298 | 0.324 | 0.025 | nunca passa |
| XOM | 347 | 0.390 | 0.399 | 0.407 | 0.017 | nunca passa |
| MSFT | 251 | 0.417 | 0.555 | 0.557 | 0.140 | o piso decide |
| AMZN | 217 | 0.411 | 0.568 | 0.571 | 0.159 | o piso decide |
| TSLA | 211 | 0.545 | 0.586 | 0.630 | 0.086 | sempre passa |
| NVDA | 114 | 0.457 | 0.481 | 0.501 | 0.044 | o piso decide |
| JPM | 114 | 0.242 | 0.248 | 0.258 | 0.016 | nunca passa |
| NFLX | 106 | 0.388 | 0.413 | 0.426 | 0.038 | nunca passa |
| GOOGL | 102 | 0.444 | 0.489 | 0.528 | 0.083 | o piso decide |
| META | 102 | 0.525 | 0.537 | 0.545 | 0.020 | sempre passa |

- **Amplitude média DENTRO de cada empresa:** `0.064`
- **Amplitude ENTRE as medianas das empresas:** `0.385`
- **Razão entre/dentro: 6.1×**

## 2. O resultado

- Empresas que passam **sempre**: 3 — AMD, META, TSLA
- Empresas que **nunca** passam: 5 — AAPL, JNJ, JPM, NFLX, XOM
- Empresas em que o piso **chega a decidir**: 4 — AMZN, GOOGL, MSFT, NVDA

> **Em 84% das decisões o resultado estava determinado pela EMPRESA antes de
> se ler a manchete.**

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
| piso fixo em 0.5 (actual) | 1670 (38%) | 7/12 | AMD com 963 |
| top 5% de cada empresa | 1549 (35%) | 12/12 | JNJ com 874 |
| top 10% de cada empresa | 1734 (40%) | 12/12 | JNJ com 874 |
| top 20% de cada empresa | 3321 (76%) | 12/12 | JNJ com 874 |

**Resolve metade e cria outro problema.** Todas as empresas passam a estar representadas, o que
é o efeito pretendido. Mas nas empresas cujo score é quase constante — as de amplitude mais
baixa nesta tabela — o percentil cai **em cima** da constante e quase todas as decisões empatam
acima dele. O regime relativo passa a seleccionar por desempate, que é exactamente o artefacto
que a dissertação documenta noutro sítio.

## 4. Leitura honesta

A conclusão não é que falta afinar o piso. É mais funda, e é coerente com o resultado negativo
já reportado para a questão da triagem:

> **Dentro de uma empresa, o score do modelo quase não varia com a manchete.**
> A amplitude média dentro de cada empresa é `0.064`, contra `0.385` entre empresas.
> Nenhuma regra de decisão aplicada a este score o pode tornar sensível à notícia, porque a
> informação que distinguiria uma manchete da seguinte não está lá.

O que isto implica para o produto é que **o score da triagem não deve ser o critério principal
de alerta**. Serve para ordenar entre empresas, que é para o que tem informação, e para ser
mostrado com a ressalva que já tem. O critério que decide *se* se interrompe alguém precisa de
assentar em quantidades que variem com o acontecimento: o movimento do próprio dia, a força da
evidência recuperada, e a novidade da história.
