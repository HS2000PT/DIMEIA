# evaluation_anomaly.md — Avaliação do detetor de anomalias (reprodutível)

> Gerado por `scripts/evaluate_anomaly.py`. **Não editar à mão.** Ver caveats no fim.

- **Dados:** 15 tickers, preços reais (yfinance, 3y).
- **z-score:** janela 20d, limiar ±3 (sem lookahead). **Baseline fixo:** |retorno| ≥ 3%. **Rótulo-proxy:** |retorno| ≥ percentil 0.99 por ticker.
- **Gerado:** 2026-06-21 18:36 UTC.

## 1. Consistência da taxa de disparo entre tickers (argumento principal)

| Método | Taxa mín | Taxa máx | Amplitude |
|---|---|---|---|
| z-score | 0.015 | 0.032 | **0.017** |
| Limiar fixo (%) | 0.011 | 0.354 | **0.343** |

**Leitura:** o z-score dispara a uma taxa quase constante entre tickers (amplitude 0.017), enquanto o limiar fixo varia muito (amplitude 0.343) — confirma que normaliza a volatilidade.

## 2. Precision / recall / F1 vs rótulo-proxy (suporte)

| Método | Precision | Recall | F1 |
|---|---|---|---|
| z-score | 0.388 | 0.808 | 0.524 |
| Limiar fixo (%) | 0.121 | 1.000 | 0.216 |

## 3. Ablação à janela (F1 pooled)

| Janela | F1 |
|---|---|
| 10d | 0.385 |
| 20d | 0.524 |
| 60d | 0.687 |

**Caveats (honestos):** o rótulo é um *proxy* (percentil de movimento), não verdade absoluta, e é volatilidade-relativo como o z-score (alguma circularidade — por isso o argumento principal é a **consistência da taxa de disparo**, que não depende do rótulo). Avaliação reprodutível (`scripts/evaluate_anomaly.py`).
