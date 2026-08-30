# evaluation_results.md — Resultados da avaliação (reprodutível)

> Gerado por `scripts/evaluate.py`. **Não editar à mão.** Ver os caveats no fim.

## Pergunta A — qualidade da recuperação de precedentes (precision@k por setor)

- **Dados:** 3,637 notícias reais (Finnhub), 5 setores: {'tech': 1708, 'consumer': 486, 'banking': 485, 'energy': 481, 'health': 477}.
- **Consultas amostradas:** 500 por repetição; **5 repetições** (seeds 42..46); média ± desvio. Recuperação **cross-ticker** (exclui a própria empresa).
- **Proxy de relevância:** mesmo setor (data_card.md). Baselines: recência e taxa-base.
- **Gerado:** 2026-08-30 17:01 UTC.

| Método | P@5 | P@10 |
|---|---|---|
| SBERT (MiniLM) | 0.544 ± 0.013 | 0.518 ± 0.013 |
| Lexical (baseline) | 0.387 ± 0.012 | 0.351 ± 0.008 |
| Recency | 0.309 ± 0.006 | 0.390 ± 0.007 |
| Random (base rate) | 0.241 ± 0.003 | 0.241 ± 0.003 |

**Leitura:** a P@5 do SBERT (MiniLM) é 0.544 vs 0.241 da taxa-base aleatória (lift +0.303); baseline lexical 0.387.

**Caveats (honestos):** o setor é um *proxy* automático de analogia (não um julgamento humano de relevância); os dados são do último período disponível no Finnhub (não o histórico multi-ano do FNSPID); títulos curtos limitam a semântica captável. Estes números são uma avaliação **preliminar** e reprodutível, não a avaliação final da tese.
