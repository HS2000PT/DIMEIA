# B1 — BM25 contra SBERT na recuperação de precedentes

Gerado por `scripts/evaluate_retrieval_bm25.py` a 2026-09-08 23:58 UTC.

Protocolo idêntico ao de `evaluate_retrieval_fnspid.py`: 5 repetições de
500 consultas, sementes 42..46, k=5, recuperação
cross-ticker, relevância = mesmo setor. Corpus: 78481 registos.
BM25 com k1=1.5 e b=0.75; empates resolvidos por permutação fixa (semente 42).

| Método | Precision@5 | Margem sobre o acaso |
|---|---|---|
| SBERT (implantado) | 0.6042 ± 0.0184 | +0.2674 |
| **BM25** | **0.5244 ± 0.0150** | **+0.1877** |
| Recência | 0.0880 | -0.2487 |
| Acaso (taxa-base) | 0.3367 | — |

Diferença emparelhada SBERT − BM25, sobre as mesmas consultas: **+0.0798 ± 0.0147**.

Lugares preenchidos com pontuação BM25 exatamente zero: **0.00%**. Um valor elevado
significaria que o BM25 não encontrou termos comuns e que a posição foi ocupada pelo
desempate aleatório, e não por correspondência lexical.

Valores por repetição:

| Repetição | SBERT | BM25 | Δ |
|---|---|---|---|
| 0 | 0.6284 | 0.5480 | +0.0804 |
| 1 | 0.6244 | 0.5264 | +0.0980 |
| 2 | 0.5948 | 0.5008 | +0.0940 |
| 3 | 0.5864 | 0.5228 | +0.0636 |
| 4 | 0.5868 | 0.5240 | +0.0628 |
