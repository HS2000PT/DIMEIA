# evaluation_results.md — Resultados da avaliação (reprodutível)

> Gerado por `scripts/evaluate.py`. **Não editar à mão.** Ver os caveats no fim.

## Pergunta A — qualidade da recuperação de precedentes (precision@k por setor)

- **Dados:** 3,692 notícias reais (Finnhub), 5 setores: {'tech': 1726, 'banking': 496, 'energy': 493, 'health': 493, 'consumer': 484}.
- **Consultas amostradas:** 500 por repetição; **5 repetições** (seeds 42..46); média ± desvio. Recuperação **cross-ticker** (exclui a própria empresa).
- **Proxy de relevância:** mesmo setor (data_card.md). Baselines: recência e taxa-base.
- **Gerado:** 2026-06-21 20:56 UTC.

| Método | P@5 | P@10 |
|---|---|---|
| SBERT | 0.549 ± 0.014 | 0.516 ± 0.013 |
| Lexical (baseline) | 0.359 ± 0.010 | 0.327 ± 0.011 |
| Recency | 0.105 ± 0.013 | 0.081 ± 0.006 |
| Random (base rate) | 0.241 ± 0.004 | 0.241 ± 0.004 |

**Leitura:** a P@5 do SBERT é 0.549 vs 0.241 da taxa-base aleatória (lift +0.308); baseline lexical 0.359.

**Caveats (honestos):** o setor é um *proxy* automático de analogia (não um julgamento humano de relevância); os dados são do último período disponível no Finnhub (não o histórico multi-ano do FNSPID); títulos curtos limitam a semântica captável. Estes números são uma avaliação **preliminar** e reprodutível, não a avaliação final da tese.
