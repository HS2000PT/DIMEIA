# O registo de decisões dá para retreinar?

> **Gerado por** `scripts/auditar_registo_decisoes.py`. Não editar à mão.
> **Fonte:** `origin/alerts-history:predictions_log.jsonl` · **Gerado a:** 2026-09-03 23:31 UTC.

## 1. Dimensão

| | |
|---|---|
| Linhas | 39595 |
| Títulos distintos (`news_date`, `ticker`, `headline`) | 257 |
| Datas de notícia | 2026-08-27 a 2026-09-03 |
| Carimbos de decisão | 2026-08-29T03:58:04+00:00 a 2026-09-03T23:28:49+00:00 |
| Empresas | 12 |
| Dias com pelo menos um título | 8 |
| Mediana de títulos distintos por dia | 28 |

**O número de linhas não é o número de observações.** Mediana de
78 decisões por título distinto; máximo de 1406.

| Ticker | Decisões | Títulos distintos | Decisões por título |
|---|---|---|---|
| AAPL | 4094 | 27 | 152 |
| NVDA | 4094 | 42 | 97 |
| TSLA | 4094 | 31 | 132 |
| AMZN | 4094 | 24 | 171 |
| MSFT | 4090 | 25 | 164 |
| META | 3997 | 19 | 210 |
| AMD | 3713 | 22 | 169 |
| GOOGL | 3635 | 24 | 151 |
| JPM | 2297 | 13 | 177 |
| XOM | 2122 | 7 | 303 |
| NFLX | 1818 | 15 | 121 |
| JNJ | 1547 | 8 | 193 |

## 2. Esquema

| Campo | Linhas | Fração |
|---|---:|---:|
| `prob` presente | 33445 | 84.5% |
| `feature_snapshot` presente | 0 | 0.0% |
| `model_info` presente | 0 | 0.0% |
| `kept` verdadeiro | 39595 | 100.0% |

Primeira linha com `feature_snapshot`: **nenhuma**.
Esquemas de features observados: nenhum.

## 3. Momento das entradas

Comparação entre `feature_snapshot.as_of` — a última barra de preço usada — e a data da notícia:

| Relação | Linhas |
|---|---:|
| `as_of` anterior à notícia | 0 |
| `as_of` igual à notícia | 0 |
| `as_of` posterior à notícia | 0 |
| snapshot sem `as_of` | 0 |

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
