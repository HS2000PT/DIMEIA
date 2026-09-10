# evaluation_results.md — Resultados da avaliação (reprodutível)

> Gerado por `scripts/evaluate.py`. **Não editar à mão.** Ver os caveats no fim.

## Pergunta A — qualidade da recuperação de precedentes (precision@k por setor)

- **Dados:** 18,599 notícias reais (Finnhub), 5 setores: {'tech': 15624, 'banking': 957, 'consumer': 728, 'energy': 721, 'health': 569}.
- **Consultas amostradas:** 500 por repetição; **5 repetições** (seeds 42..46); média ± desvio. Recuperação **cross-ticker** (exclui a própria empresa).
- **Proxy de relevância:** mesmo setor (data_card.md). Baselines: recência e taxa-base.
- **Gerado:** 2026-09-10 08:32 UTC.

| Método | P@5 | P@10 |
|---|---|---|
| SBERT (MiniLM) | 0.779 ± 0.016 | 0.771 ± 0.014 |
| SBERT (MPNet) | 0.778 ± 0.015 | 0.776 ± 0.010 |
| Lexical (baseline) | 0.746 ± 0.021 | 0.737 ± 0.017 |
| Recency | 0.560 ± 0.009 | 0.302 ± 0.005 |
| Random (base rate) | 0.685 ± 0.013 | 0.685 ± 0.013 |

**Leitura:** a P@5 do SBERT (MiniLM) é 0.779 vs 0.685 da taxa-base aleatória (lift +0.094); baseline lexical 0.746.

**Caveats (honestos):** o setor é um *proxy* automático de analogia (não um julgamento humano de relevância); os dados são do último período disponível no Finnhub (não o histórico multi-ano do FNSPID); títulos curtos limitam a semântica captável. Estes números são uma avaliação **preliminar** e reprodutível, não a avaliação final da tese.
