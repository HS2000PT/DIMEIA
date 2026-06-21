# free_apis.md — APIs gratuitas identificadas, avaliadas e aprovadas

> **Fase C.** Restrição não negociável: **apenas free tier** (§5.2). Cobertura US (NYSE/NASDAQ).
> **Verificação web: 2026-06-21** (limites mudam — reconfirmar antes da implementação). Fontes no fim.
> Princípio confirmado: **histórico vem do FNSPID, não de APIs** (os free tiers de notícias dão ~30 dias,
> são "development-use" e atrasados → não servem para construir histórico).

## Preços / dados de mercado (camada LIVE)
| Fonte | Free tier (limites verificados) | Histórico | Cobertura US | Fiabilidade | Estado |
|---|---|---|---|---|---|
| **yfinance** (Yahoo Finance, não-oficial) | sem chave; limites **não documentados**, sujeito a 429 / `YFRateLimitError` / bloqueio de IP | intradiário + longo histórico | excelente | **frágil** (scraping; Yahoo apertou em 2024–25; pode partir) | **Aprovado como base**, com cache + backoff |
| **Finnhub** | **60 chamadas/min** (cap 30/seg); inclui cotações US em tempo real, **company news**, fundamentais básicos, SEC filings, WebSocket 50 símbolos; sem cartão | limitado no free | boa (US) | boa (API oficial) | **Aprovado como fallback/secundária** |
| **Alpha Vantage** | **25 pedidos/dia** (e ~5/min) — reduzido ao longo do tempo (500→100→25) | EOD/algum histórico | boa | boa | **Terciária/ocasional** (25/dia é pouco para polling) |
| *(alternativas)* Polygon.io (free ~5/min, EOD), Tiingo (free EOD+news) | — | — | — | — | reserva, se necessário |

## Notícias (camada LIVE)
| Fonte | Free tier (limites verificados) | Notas | Estado |
|---|---|---|---|
| **Finnhub – company news** | incluído no free (60/min) | ligado a tickers US; já temos a chave Finnhub | **Aprovado (primária)** |
| **RSS financeiro** (Yahoo Finance RSS, Nasdaq, SEC EDGAR, IR das empresas) | **sem chave, sem rate limit prático** | robusto e simples; ótimo fallback | **Aprovado (primária/fallback)** |
| **GNews** | **100 pedidos/dia**, 1/seg, reset 00:00 UTC; **só não-comercial/dev** | enriquecimento | Opcional |
| **Marketaux** | ~**100 pedidos/dia**, 50 resultados/chamada; inclui **sentimento + tickers** | financeiro, útil | Opcional |
| **NewsAPI.org** | dev-only, 100/dia, **atraso 24h, só último mês** | **não serve histórico** | **Último recurso** |

## Histórico (NÃO é API)
- **FNSPID** (`Zihan1004/FNSPID`, **CC BY-SA 4.0** — atribuição obrigatória). Notícias já alinhadas a preços,
  ~4.775 empresas S&P 500, 1999–2023. É a base do motor de correlação. Detalhe em `data_card.md`.

## Alertas
- **Telegram Bot API** — **gratuito**. Limites: **30 msg/seg** por bot (global), **1 msg/seg para o mesmo chat**;
  429 com `retry_after` e cooldown de 30s. **Muito acima** da nossa necessidade (poucos alertas). **Aprovado.**

## Conjunto aprovado (proposta da Fase C)
- **Preços live:** **yfinance** (base) + **Finnhub** (fallback, 60/min). Alpha Vantage só ocasional (25/dia).
- **Notícias live:** **Finnhub company news** + **RSS financeiro** (primárias); GNews/Marketaux como enriquecimento opcional.
- **Histórico:** **FNSPID** (núcleo; não-API).
- **Alertas:** **Telegram Bot API**.

## Estratégia de robustez (free tier)
- **Cache** agressivo de preços/notícias; **polling de baixa cadência** (respeitar 25/dia AV, 100/dia GNews).
- **Backoff exponencial** e tratamento de 429; nunca exceder os limites (evita bloqueios e respeita ToS).
- **Fallbacks encadeados** (yfinance→Finnhub; Finnhub news→RSS) para não depender de uma só fonte frágil.
- Chaves só no `.env` (nunca versionadas); nomes em `.env.example`. Registar a data de cada reverificação.

## Riscos associados (ver `risk_register.md` R3)
- yfinance pode bloquear/partir → fallback Finnhub/RSS.
- Free tiers podem mudar/reduzir (como o Alpha Vantage) → reconfirmar e documentar a troca.

## Fontes (verificado 2026-06-21)
- Finnhub: <https://finnhub.io/docs/api/rate-limit>, <https://finnhub.io/pricing-stock-api-market-data>
- Alpha Vantage: <https://www.macroption.com/alpha-vantage-api-limits/>, <https://www.alphavantage.co/support/>
- GNews: <https://gnews.io/pricing>, <https://docs.gnews.io/>
- Marketaux: <https://www.marketaux.com/pricing>, <https://www.marketaux.com/documentation>
- yfinance (fiabilidade/429): <https://github.com/ranaroussi/yfinance/issues/2128>, <https://github.com/ranaroussi/yfinance/issues/2422>
- Telegram Bot API: <https://core.telegram.org/bots/faq>
