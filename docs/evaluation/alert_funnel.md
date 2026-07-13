# alert_funnel.md — funil de produção real (snapshot)

> Gerado por `scripts/figures/fig_alert_funnel.py` a partir da branch de dados
> `alerts-history` (a mesma fonte da app). **Não editar à mão.** Snapshot com data:
> os números crescem com o canal vivo; a tese cita ESTE snapshot.

- **Janela coberta:** notícias datadas de 2026-07-04 a 2026-07-13.
- **Capturadas (relevantes, únicas):** 944 manchetes (passaram o filtro de relevância; TODAS entram na KB viva como pendentes).
- **Alertas de notícia enviados ao canal:** 42 (seletividade 22:1).
- **Gates entre um número e o outro:** relevance filter → capture; freshness ≤ 2d; precedent cosine ≥ 0.45; learned triage P ≥ 0.5; cap 2/ticker/day + dedup.
- **Gerado:** 2026-07-13 14:03 UTC.

| Ticker | Relevantes capturadas | Alertas enviados |
|---|---|---|
| TSLA | 148 | 14 |
| META | 137 | 14 |
| AAPL | 135 | 0 |
| AMZN | 91 | 0 |
| AMD | 88 | 14 |
| NFLX | 83 | 0 |
| MSFT | 75 | 0 |
| GOOGL | 71 | 0 |
| JPM | 60 | 0 |
| NVDA | 56 | 0 |
| **Total** | **944** | **42** |

**Leitura:** as notícias relevantes fluem para os 10 tickers da watchlist, mas os gates de evidência (precedente forte + triagem aprendida) concentram os alertas onde a evidência é forte — anti-fadiga por desenho, não por acaso. Nota honesta: nos 2 primeiros dias o teto de 2/ticker/dia ainda não estava em produção (entrou a 2026-07-11), por isso há dias antigos com mais alertas.
