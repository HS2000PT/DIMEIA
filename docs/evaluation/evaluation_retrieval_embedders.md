# evaluation_retrieval_embedders.md — Benchmark de embedders (RQ2; aditivo)

> Gerado por `scripts/evaluate_retrieval_embedders.py`. Corre o protocolo cross-ticker
> precision@k da tese, no mesmo corpus preliminar, comparando o SBERT MiniLM/MPNet com um
> encoder de DOMÍNIO (FinBERT, mean-pooled) e um MODERNO (E5/BGE) — a comparação que
> o Cap. 2 discutiu mas não tinha corrido. NÃO altera os números congelados.

- **Corpus:** 3714 manchetes · 500 consultas × 5 sementes.
- **Protocolo:** cross-ticker precision@5 (exclui a própria empresa); proxy de setor.
- **Gerado:** 2026-07-27 23:51 UTC · seed 42.

| Embedder | P@5 |
|---|---|
| SBERT MiniLM (tese) | 0.514 ± 0.015 |
| SBERT MPNet | 0.538 ± 0.011 |
| FinBERT (domínio, mean-pool) | 0.420 ± 0.010 |
| E5-small (moderno) | 0.504 ± 0.016 |
| BGE-small (moderno) | 0.513 ± 0.014 |
| Lexical (baseline) | 0.346 ± 0.011 |
| Recency | 0.126 ± 0.006 |
| Random (base rate) | 0.240 ± 0.004 |

**Leitura honesta:** o MiniLM da tese reproduz-se em **0.514** (sanidade). O encoder de DOMÍNIO FinBERT dá **0.420** — pior que o MiniLM, coerente com o Cap. 2 (o FinBERT é afinado para sentimento, não para similaridade de frases). Os encoders MODERNOS (E5 0.504, BGE 0.513) **empatam com** MiniLM. Ou seja, a escolha do MiniLM está validada por MEDIÇÃO, não por argumento: um modelo pequeno, gratuito e de 2021 continua no 'sweet spot' para esta tarefa — trocar por um domínio-específico ou por um modelo mais recente não traria ganho. (E5 com prefixo 'query:' simétrico; FinBERT via mean-pooling do encoder.)
