# Independência dos precedentes mostrados

> **Gerado por** `scripts/evaluate_precedent_independence.py`. Não editar à mão.
> **Fonte:** os alertas **realmente entregues** ao canal, lidos de `origin/alerts-history:alerts_history.jsonl`.
> Nada é reconstruído nem simulado.

## O que se mede, e porquê

O impacto de uma notícia é medido por `(ticker, dia)`. Logo, **duas manchetes da mesma empresa
no mesmo dia partilham exactamente o mesmo impacto por construção** — não porque o mercado tenha
reagido duas vezes da mesma maneira, mas porque é o mesmo dia.

Um alerta que mostra três precedentes e diz *"3 of 3 shown cases moved down"* está a apresentar
isso como **concordância entre casos**. Se os três forem do mesmo dia, é **um** caso repetido três
vezes, e a frase promete mais evidência do que existe.

## Resultado

- Alertas de notícia com precedentes: **247**
- Período: **2026-07-11** a **2026-08-13**

| Casos mostrados | Dias distintos por trás | Alertas | % |
|---|---|---|---|
| 3 | 1 | 28 | 11.3% |
| 3 | 2 | 63 | 25.5% |
| 3 | 3 | 156 | 63.2% |

- Com **menos dias distintos** do que casos mostrados: **91/247
  (36.8%)**
- Com **todos os casos do mesmo dia**: **28/247 (11.3%)**
- Alertas que afirmam unanimidade (*"N of N shown cases moved"*): **120**
  - destes, apoiados num **único** dia observado: **28**
    (23.3% dos unânimes)

## Leitura honesta

A recuperação **não está errada**: as manchetes recuperadas são genuinamente as mais parecidas, e
o impacto de cada uma é o impacto real daquele dia. O que está errado é a **forma de apresentar**:
contar casos quando o que varia são dias.

Isto **não afecta** nenhuma métrica de recuperação reportada na dissertação. A precisão@5 conta
manchetes relevantes, não dias, e a concordância de direcção é medida par a par sobre o corpus
histórico, não sobre estes alertas.

O que afecta é a **força que o alerta reivindica** quando fala ao utilizador, e é por isso que fica
registado como limitação em vez de ser corrigido em silêncio.
