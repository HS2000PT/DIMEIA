# evaluation_results.md — Resultados da avaliação (reprodutível)

> Gerado por `scripts/evaluate.py`. **Não editar à mão.** Ver os caveats no fim.

## Pergunta A — qualidade da recuperação de precedentes (precision@k por setor)

- **Dados:** 3,714 notícias reais (Finnhub), 5 setores: {'tech': 1736, 'energy': 497, 'banking': 496, 'health': 494, 'consumer': 491}.
- **Consultas amostradas:** 500 por repetição; **5 repetições** (seeds 42..46); média ± desvio. Recuperação **cross-ticker** (exclui a própria empresa).
- **Proxy de relevância:** mesmo setor (data_card.md). Baselines: recência e taxa-base.
- **Gerado:** 2026-06-25 21:57 UTC.

| Método | P@5 | P@10 |
|---|---|---|
| SBERT (MiniLM) | 0.514 ± 0.015 | 0.478 ± 0.011 |
| SBERT (MPNet) | 0.538 ± 0.011 | 0.506 ± 0.010 |
| Lexical (baseline) | 0.346 ± 0.011 | 0.314 ± 0.008 |
| Recency | 0.126 ± 0.006 | 0.106 ± 0.005 |
| Random (base rate) | 0.240 ± 0.004 | 0.240 ± 0.004 |

**Leitura:** a P@5 do SBERT (MiniLM) é 0.514 vs 0.240 da taxa-base aleatória (lift +0.273); baseline lexical 0.346.

**Caveats (honestos):** o setor é um *proxy* automático de analogia (não um julgamento humano de relevância); os dados são do último período disponível no Finnhub (não o histórico multi-ano do FNSPID); títulos curtos limitam a semântica captável. Estes números são uma avaliação **preliminar** e reprodutível, não a avaliação final da tese.
