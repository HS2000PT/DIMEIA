# evaluation_retrieval_fnspid.md — Recuperação em ESCALA (RQ2; corpus multi-ano FNSPID)

> Gerado por `scripts/evaluate_retrieval_fnspid.py` (ADITIVO; não altera a avaliação
> preliminar em `evaluation_results.md`). Reutiliza os embeddings SBERT da KB
> (sem re-embeder). É o passo 'trabalho futuro' da RQ2: validar o componente mais forte à
> escala (2018-2023) em vez do corpus recente de poucos meses.

- **Corpus:** 79753 manchetes · tickers ['AAPL', 'AMZN', 'BAC', 'CVX', 'GOOGL', 'JNJ', 'JPM', 'KO', 'MSFT', 'NVDA', 'PFE', 'TSLA', 'WMT', 'XOM'].
- **Protocolo:** cross-ticker precision@5, 500 consultas × 5 sementes (média ± desvio); mesmo proxy de setor da tese.
- **Gerado:** 2026-07-27 23:45 UTC · seed 42.

| Método | P@5 |
|---|---|
| SBERT (MiniLM) | 0.595 ± 0.024 |
| Recency | 0.090 ± 0.014 |
| Random (base rate) | 0.333 |

**Leitura:** a P@5 do SBERT à escala é **0.595** vs 0.333 do acaso (lift **+0.262**). Confirma, sobre ~79k manchetes de 6 anos, o que a avaliação preliminar (corpus recente) já indicava: a recuperação semântica supera as baselines triviais — agora à escala, não em poucos meses.

## Tema ≠ direção, quantificado (o ponto honesto do CS3)

- **Dispersão do impacto (+3d) nos top-5 precedentes:** 0.030 (desvio-padrão médio dos retornos dos precedentes recuperados).
- **Consistência de direção média:** **0.708** (1,0 = todos os precedentes na mesma direção; 0,5 = metade sobe, metade desce).
- **Chão do acaso** (direções aleatórias, k=5): **0.688** — o valor esperado se a direção dos precedentes fosse uma moeda ao ar.

**Leitura honesta:** a consistência de direção observada (0.708) fica **quase no chão do acaso (0.688)** — ou seja, saber que os precedentes são do mesmo tema quase não diz nada sobre a **direção** do movimento. Isto **confirma quantitativamente** a limitação assumida no CS3/Cap. 6: a recuperação capta o **tema** (P@k bem acima do acaso), mas o impacto médio é evidência sobre esse tema, **nunca** uma previsão direcional — e é por isso que o alerta mostra sempre os precedentes individuais, não só a média.
