# B1 — BM25 contra SBERT na recuperação de precedentes

Gerado por `scripts/evaluate_retrieval_bm25.py` a 2026-09-09 09:41 UTC.

Protocolo idêntico ao de `evaluate_retrieval_fnspid.py`: 5 repetições de
500 consultas, sementes 42..46, k=5, recuperação
cross-ticker, relevância = mesmo setor. Corpus: 79753 registos.
BM25 com k1=1.5 e b=0.75; empates resolvidos por permutação fixa (semente 42).

| Método | Precision@5 | Margem sobre o acaso |
|---|---|---|
| SBERT (implantado) | 0.5946 ± 0.0240 | +0.2613 |
| **BM25** | **0.5214 ± 0.0159** | **+0.1881** |
| Recência | 0.0900 | -0.2433 |
| Acaso (taxa-base) | 0.3333 | — |

Diferença emparelhada SBERT − BM25, sobre as mesmas consultas: **+0.0733 ± 0.0112**.

Lugares preenchidos com pontuação BM25 exatamente zero: **0.00%**. Um valor elevado
significaria que o BM25 não encontrou termos comuns e que a posição foi ocupada pelo
desempate aleatório, e não por correspondência lexical.

Valores por repetição:

| Repetição | SBERT | BM25 | Δ |
|---|---|---|---|
| 0 | 0.6092 | 0.5356 | +0.0736 |
| 1 | 0.5560 | 0.4976 | +0.0584 |
| 2 | 0.5772 | 0.5108 | +0.0664 |
| 3 | 0.6140 | 0.5220 | +0.0920 |
| 4 | 0.6168 | 0.5408 | +0.0760 |
