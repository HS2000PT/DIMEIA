# Ordenação sobre a população real de candidatas

> **Gerado por** `scripts/evaluate_ranking_producao.py`. Não editar à mão.
> **Gerado a:** 2026-09-06 08:27 UTC

## Bloco insuficiente

O protocolo exige **80 pares empresa-dia com rótulo maturado** antes de reportar qualquer métrica de comparação, e existem **0**. Nenhum valor é publicado.

O mínimo foi fixado antes de haver dados. Reportar abaixo dele produziria um número que alguém citaria, e o intervalo que o acompanha seria largo ao ponto de não distinguir o modelo do acaso.

| | |
|---|---:|
| Linhas no registo | 40414 |
| Utilizáveis (classe A, `as_of` não posterior à notícia, sem repetição) | 243 |
| Pares empresa-dia com rótulo maturado | 0 |
| Mínimo exigido | 80 |

## A recolha chega ao mínimo a tempo?

Ao ritmo observado de **12 pares por dia de bolsa**, e com **9 dias de bolsa** até 2026-09-17, a projeção é de **120 pares**, contra um mínimo de 80. A recolha está no caminho certo.

⚠️ **2026-09-17 é a última data de NOTÍCIA rotulável, não a data de correr esta avaliação.** O rótulo mede a janela `(d, d+3]` em dias de bolsa, pelo que os pares dos últimos três dias de recolha ainda não maturaram nesse dia. O protocolo fixa o congelamento dos resultados em **~2026-09-22**, que é quando a projeção acima existe de facto. Correr isto a 2026-09-17 devolve uma recusa que **não** significa que a recolha falhou.

Hoje há **12** pares recolhidos, dos quais **0** já maturaram. A projeção supõe que o ritmo se mantém e que o sistema continua no ar, e não é uma garantia.
