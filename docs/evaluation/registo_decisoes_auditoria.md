# O registo de decisões dá para retreinar?

> **Gerado por** `scripts/auditar_registo_decisoes.py`. Não editar à mão.
> **Fonte:** `origin/alerts-history:predictions_log.jsonl` · **Gerado a:** 2026-09-06 08:23 UTC.

## 1. Dimensão

| | |
|---|---|
| Linhas | 41747 |
| Títulos distintos (`news_date`, `ticker`, `headline`) | 1318 |
| Datas de notícia | 2026-05-18 a 2026-09-05 |
| Carimbos de decisão | 2026-08-29T03:58:04+00:00 a 2026-09-05T14:14:02+00:00 |
| Empresas | 12 |
| Dias com pelo menos um título | 47 |
| Mediana de títulos distintos por dia | 1 |

**O número de linhas não é o número de observações.** Mediana de
2 decisões por título distinto; máximo de 1407.

| Ticker | Decisões | Títulos distintos | Decisões por título |
|---|---|---|---|
| TSLA | 4448 | 227 | 20 |
| AAPL | 4443 | 198 | 22 |
| NVDA | 4343 | 180 | 24 |
| AMZN | 4283 | 110 | 39 |
| MSFT | 4278 | 114 | 38 |
| META | 4131 | 79 | 52 |
| GOOGL | 3838 | 118 | 33 |
| AMD | 3829 | 69 | 55 |
| JPM | 2397 | 60 | 40 |
| XOM | 2197 | 44 | 50 |
| NFLX | 1939 | 79 | 25 |
| JNJ | 1621 | 40 | 41 |

## 2. Esquema

| Campo | Linhas | Fração |
|---|---:|---:|
| `prob` presente | 34860 | 83.5% |
| `feature_snapshot` presente | 1272 | 3.0% |
| `model_info` presente | 1995 | 4.8% |
| `kept` verdadeiro | 39856 | 95.5% |

Primeira linha com `feature_snapshot`: 2026-09-04T00:25:25+00:00.
Esquemas de features observados: {'triage-context-v1': 1272}.

## 3. Momento das entradas

Comparação entre `feature_snapshot.as_of` — a última barra de preço usada — e a data da notícia:

| Relação | Linhas |
|---|---:|
| `as_of` anterior à notícia | 440 |
| `as_of` igual à notícia | 383 |
| `as_of` posterior à notícia | 449 |
| snapshot sem `as_of` | 0 |

**As linhas com `as_of` POSTERIOR à data da notícia não servem para treino nem para avaliação.**
O rótulo mede o retorno anormal em `(data, data+3]`; se a barra usada é posterior, as entradas
descrevem um mercado que **já viu esse desfecho**. Medido a 2026-09-04: as candidatas velhas
tinham `as_of` de +1 a +107 dias, e eram 430 de 977. A pontuação de candidatas velhas foi
desligada nessa data, portanto estas linhas são histórico e não crescem — mas continuam no
ficheiro e **não podem entrar em nenhum conjunto**.

Uma barra anterior à notícia significa que `ret_event` descreve a véspera e não o dia do
acontecimento. É a assimetria que a dissertação declara entre treino e produção; aqui fica
contada em vez de suposta.

## 4. O que isto permite e o que não permite

- Linhas **sem** `feature_snapshot` não são reproduzíveis a partir do registo. Recalcular hoje
  as entradas daquele dia usaria uma série de preços que já contém o que veio a seguir. Essas
  linhas servem para caracterizar a operação; **não servem como conjunto de treino**.
- Se `kept` for constante, a comparação entre decisões mantidas e suprimidas não é recalculável
  sobre esta janela. Com orçamento diário ligado, a triagem ordena e não veta.
- A contagem de títulos distintos por dia é o tamanho real do bloco de comparação. Fixar os
  mínimos de dias e de classes **a partir deste número**, e antes de observar qualquer
  candidato.
