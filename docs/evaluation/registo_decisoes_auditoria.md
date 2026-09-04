# O registo de decisões dá para retreinar?

> **Gerado por** `scripts/auditar_registo_decisoes.py`. Não editar à mão.
> **Fonte:** `origin/alerts-history:predictions_log.jsonl` · **Gerado a:** 2026-09-04 01:44 UTC.

## 1. Dimensão

| | |
|---|---|
| Linhas | 41450 |
| Títulos distintos (`news_date`, `ticker`, `headline`) | 1021 |
| Datas de notícia | 2026-05-18 a 2026-09-04 |
| Carimbos de decisão | 2026-08-29T03:58:04+00:00 a 2026-09-04T01:06:01+00:00 |
| Empresas | 12 |
| Dias com pelo menos um título | 45 |
| Mediana de títulos distintos por dia | 1 |

**O número de linhas não é o número de observações.** Mediana de
2 decisões por título distinto; máximo de 1407.

| Ticker | Decisões | Títulos distintos | Decisões por título |
|---|---|---|---|
| AAPL | 4409 | 164 | 27 |
| TSLA | 4364 | 143 | 31 |
| NVDA | 4288 | 125 | 34 |
| AMZN | 4263 | 90 | 47 |
| MSFT | 4250 | 86 | 49 |
| META | 4114 | 62 | 66 |
| GOOGL | 3821 | 101 | 38 |
| AMD | 3821 | 61 | 63 |
| JPM | 2384 | 47 | 51 |
| XOM | 2189 | 36 | 61 |
| NFLX | 1930 | 70 | 28 |
| JNJ | 1617 | 36 | 45 |

## 2. Esquema

| Campo | Linhas | Fração |
|---|---:|---:|
| `prob` presente | 34565 | 83.4% |
| `feature_snapshot` presente | 977 | 2.4% |
| `model_info` presente | 1700 | 4.1% |
| `kept` verdadeiro | 39770 | 95.9% |

Primeira linha com `feature_snapshot`: 2026-09-04T00:25:25+00:00.
Esquemas de features observados: {'triage-context-v1': 977}.

## 3. Momento das entradas

Comparação entre `feature_snapshot.as_of` — a última barra de preço usada — e a data da notícia:

| Relação | Linhas |
|---|---:|
| `as_of` anterior à notícia | 336 |
| `as_of` igual à notícia | 211 |
| `as_of` posterior à notícia | 430 |
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
