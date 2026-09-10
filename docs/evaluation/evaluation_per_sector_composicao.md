# evaluation_per_sector.md — Recuperação por setor (reprodutível)

> Gerado por `scripts/evaluate_per_sector.py`. **Não editar à mão.**

- **Gerado:** 2026-09-10 08:35 UTC. Modelo: SBERT all-MiniLM-L6-v2. População completa por setor (cross-ticker, sem amostragem).

| Setor | N | P@5 | P@10 | Aleatório (base) | Lift P@5 |
|---|---|---|---|---|---|
| Technology | 15624 | 0.887 | 0.884 | 0.808 | +0.079 |
| Banking | 957 | 0.192 | 0.152 | 0.025 | +0.168 |
| Energy | 721 | 0.347 | 0.312 | 0.020 | +0.328 |
| Health | 569 | 0.243 | 0.227 | 0.015 | +0.228 |
| Consumer | 728 | 0.071 | 0.068 | 0.018 | +0.053 |

**Leitura:** a recuperação semântica supera a taxa-base aleatória em todos os setores; o *lift* é maior na energia e na saúde (vocabulário distintivo) e menor no consumo. A tecnologia tem a P@5 bruta mais alta apenas por dominar o corpus (taxa-base elevada). Avaliação preliminar (corpus recente do Finnhub).
