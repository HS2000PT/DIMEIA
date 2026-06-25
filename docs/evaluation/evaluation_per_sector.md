# evaluation_per_sector.md — Recuperação por setor (reprodutível)

> Gerado por `scripts/evaluate_per_sector.py`. **Não editar à mão.**

- **Gerado:** 2026-06-25 21:44 UTC. Modelo: SBERT all-MiniLM-L6-v2. População completa por setor (cross-ticker, sem amostragem).

| Setor | N | P@5 | P@10 | Aleatório (base) | Lift P@5 |
|---|---|---|---|---|---|
| Technology | 1736 | 0.712 | 0.675 | 0.429 | +0.283 |
| Banking | 496 | 0.272 | 0.228 | 0.072 | +0.200 |
| Energy | 497 | 0.448 | 0.408 | 0.072 | +0.377 |
| Health | 494 | 0.419 | 0.379 | 0.071 | +0.348 |
| Consumer | 491 | 0.171 | 0.150 | 0.071 | +0.100 |

**Leitura:** a recuperação semântica supera a taxa-base aleatória em todos os setores; o *lift* é maior na energia e na saúde (vocabulário distintivo) e menor no consumo. A tecnologia tem a P@5 bruta mais alta apenas por dominar o corpus (taxa-base elevada). Avaliação preliminar (corpus recente do Finnhub).
