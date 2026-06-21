# evaluation_results.md — Resultados da avaliação (reprodutível)

> Gerado por `scripts/evaluate.py`. **Não editar à mão.** Ver os caveats no fim.

## Pergunta A — qualidade da recuperação de precedentes (precision@k por setor)

- **Dados:** 3,692 notícias reais (Finnhub), 5 setores: {'tech': 1726, 'banking': 496, 'energy': 493, 'health': 493, 'consumer': 484}.
- **Consultas amostradas:** 500 (seed 42); recuperação **cross-ticker** (exclui a própria empresa).
- **Proxy de relevância:** mesmo setor (data_card.md). Baselines: recência e taxa-base.
- **Gerado:** 2026-06-21 18:08 UTC.

| Método | P@5 | P@10 |
|---|---|---|
| SBERT | 0.568 | 0.533 |
| Lexical (baseline) | 0.357 | 0.328 |
| Recency | 0.096 | 0.077 |
| Random (base rate) | 0.245 | 0.245 |

**Leitura:** a P@5 do SBERT é 0.568 vs 0.245 da taxa-base aleatória (lift +0.323); baseline lexical 0.357.

**Caveats (honestos):** o setor é um *proxy* automático de analogia (não um julgamento humano de relevância); os dados são do último período disponível no Finnhub (não o histórico multi-ano do FNSPID); títulos curtos limitam a semântica captável. Estes números são uma avaliação **preliminar** e reprodutível, não a avaliação final da tese.
