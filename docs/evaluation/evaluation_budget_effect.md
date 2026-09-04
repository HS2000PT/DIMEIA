# A alteração de política produziu o efeito pretendido?

> **Gerado por** `scripts/evaluate_budget_effect.py`. Não editar à mão.
> **Fonte:** histórico de alertas entregues · **Gerado a:** 2026-09-04 09:59 UTC

O modelo deixou de vetar e passou a ordenar, com um orçamento diário de cinco alertas de notícia. A quantidade medida é a **concentração**: a fração dos alertas que pertence às três empresas mais alertadas. Os alertas de **mercado** são o controlo, porque atravessam o mesmo período e as mesmas empresas e o orçamento não os governa.

| Série | Antes | Depois | Diferença | IC 95% | Empresas |
|---|---:|---:|---:|---|---|
| notícia | 0.713 | 0.480 | -0.233 | [-0.320, -0.103] **exclui zero** | 7 para 9 de 12 |
| mercado | 0.449 | 0.485 | +0.036 | [-0.138, +0.236] contém zero | 11 para 12 de 12 |

- **notícia**: 244 alertas em 33 dias antes, 75 em 15 dias depois.
- **mercado**: 49 alertas em 20 dias antes, 33 em 10 dias depois.

## Cinco dias excluídos, e porquê

Entre 25 e 29 de agosto de 2026 o contador do dia vivia em disco efémero e voltava ao princípio a cada arranque do processo. O registo mostra rajadas de exatamente cinco alertas aos segundos dos arranques, e um dia com vinte, num orçamento de cinco. Nesses dias o orçamento não estava em vigor.

- notícia: com esses dias incluídos a concentração seria `0.514` em vez de `0.480`.
- mercado: com esses dias incluídos a concentração seria `0.429` em vez de `0.485`.

## O que isto não estabelece

O controlo partilha o período mas não foi atribuído ao acaso, e as duas janelas diferem em duração e em condições de mercado. O que a comparação sustenta é que a quantidade governada se deslocou e a não governada não, e não que nenhuma outra causa exista.
