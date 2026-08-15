# Fontes de notícias: qual serve, e em que se completam

> **Gerado por** `scripts/evaluate_news_sources.py`. Não editar à mão.
> **Janela:** últimos 3 dias · **watchlist:** 12 empresas ·
> **corrido em:** 2026-08-15 20:47 UTC

## 1. Volume não é qualidade

A coluna que decide não é quantas notícias a fonte devolve: é quantas **sobrevivem ao filtro de
relevância** que já está em produção. Uma fonte generosa e mal etiquetada custa pedidos e não
acrescenta nada.

| Fonte | Devolvidas | Relevantes | Precisão | Frescura (mediana) | Cobertura |
|---|---|---|---|---|---|
| Finnhub | 1228 | 432 | 35% | 15.8h | 12/12 |
| Alpha Vantage | 600 | 141 | 24% | 9.3h | 12/12 |
| Polygon | 1600 | 429 | 27% | 52.6h | 8/12 |

## 2. Somar fontes acrescenta, ou repete?

É a pergunta que decide, e mede-se contando quantas manchetes relevantes cada fonte traz que
**nenhuma outra** traz.

| Fonte | Exclusivas | Do total |
|---|---|---|
| Finnhub | 401 | 41% |
| Alpha Vantage | 119 | 12% |
| Polygon | 418 | 43% |

- Manchetes relevantes distintas com **as três** fontes: **970**
- Só com o Finnhub (o que o sistema faz hoje): **432**
- Ganho: **538** manchetes (125% mais)

## 3. Rejeitada, e porquê

O **Tiingo** foi sondado com a chave existente e devolve **HTTP 403** no endpoint de notícias:
exige plano pago. Fica registado porque parecia servir, tal como o Stooq no caso dos preços.

O **GNews** responde e traz URL, mas **não é por empresa** — é uma pesquisa por palavras. Usá-lo
obrigaria a inferir a empresa a partir do texto, acrescentando um erro que as outras três não
têm. Não entra por essa razão, e não por limite de pedidos.

## 4. Leitura honesta

Acrescentar fontes serve para duas coisas diferentes, e só uma delas é sobre volume:

1. **Cobertura**: mais manchetes distintas, portanto menos dias em que o sistema não tem nada
   para dizer sobre uma empresa que se mexeu.
2. **Redundância**: quando uma fonte falha ou bloqueia, as outras respondem. É a mesma razão
   pela qual os preços já vêm de uma cadeia e não de uma fonte só.

O que **não** melhora é a latência de descoberta de forma garantida: as três publicam com atrasos
próprios, e o ganho depende de qual delas viu a história primeiro. Isso mede-se com o tempo, no
registo de latência, e não se afirma aqui.
