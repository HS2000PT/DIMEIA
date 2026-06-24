# evaluation_anomaly.md — Avaliação do detetor de anomalias (reprodutível)

> Gerado por `scripts/evaluate_anomaly.py`. **Não editar à mão.** Ver caveats no fim.

- **Dados:** 15 tickers, preços reais (yfinance, 2023-06-01 a 2026-06-01).
- **z-score:** janela 20d, limiar ±3 (sem lookahead). **Baseline fixo:** |retorno| ≥ 3%. **Rótulo-proxy:** |retorno| ≥ percentil 0.99 por ticker.
- **Gerado:** 2026-06-24 20:23 UTC.

## 1. Consistência da taxa de disparo entre tickers (argumento principal)

| Método | Taxa mín | Taxa máx | Amplitude |
|---|---|---|---|
| z-score | 0.016 | 0.031 | **0.015** |
| Limiar fixo (%) | 0.009 | 0.353 | **0.344** |

**Leitura:** o z-score dispara a uma taxa quase constante entre tickers (amplitude 0.015), enquanto o limiar fixo varia muito (amplitude 0.344) — confirma que normaliza a volatilidade.

## 2. Precision / recall / F1 vs rótulo-proxy (suporte)

| Método | Precision | Recall | F1 |
|---|---|---|---|
| z-score | 0.381 | 0.800 | 0.516 |
| Limiar fixo (%) | 0.122 | 0.992 | 0.218 |

## 3. Ablação à janela (F1 pooled)

| Janela | F1 |
|---|---|
| 10d | 0.385 |
| 20d | 0.516 |
| 60d | 0.678 |

**Caveats (honestos):** o rótulo é um *proxy* (percentil de movimento), não verdade absoluta, e é volatilidade-relativo como o z-score (alguma circularidade — por isso o argumento principal é a **consistência da taxa de disparo**, que não depende do rótulo). Avaliação reprodutível (`scripts/evaluate_anomaly.py`).
