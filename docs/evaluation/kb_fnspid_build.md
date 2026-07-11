# KB de retrieval FNSPID multi-ano — build + validação do artefacto

> **O que isto É:** a validação do ARTEFACTO (a base de conhecimento multi-ano construída).
> **O que isto NÃO é:** uma avaliação de retrieval — não há aqui precision@k novo; os números
> da tese (Cap. 5, corpus Finnhub multi-seed) ficam exatamente como estão. Uma avaliação de
> retrieval multi-ano (com dispersão e consistência de direção) continua como trabalho futuro,
> tal como o Cap. 6 a descreve.

**Data do build:** 2026-07-05 · **Comando:** `scripts/build_kb.py --sbert` destacado (ver
how_to_run §4); log em `data/kb_build.log`. Fonte: `data/fnspid_news_subset.csv` (FNSPID 2018–2023,
15 tickers configurados) + preços yfinance; embedder **SBERT all-MiniLM-L6-v2 (dim 384)** com
`HF_HUB_OFFLINE=1` (modelo em cache).

## Resultado

| Propriedade | Valor |
|---|---|
| Registos | **79.753** (= linhas do subset; 0 descartes) |
| Ficheiro | `data/kb_fnspid_sbert.jsonl` (**~691 MB, local, gitignored**) |
| Amostra versionada | `data/samples/kb_fnspid_sample.jsonl` (50 registos) |
| Tickers | **14/15** — META ausente (o corpus indexa-a como "FB"; mesma nota do estudo de triagem) |
| Janela | 2018-01 → 2023-12; densidade cresce (2023 = 34.922 registos ≈ 44%) |

Por ticker: TSLA 10.587 · NVDA 10.059 · AAPL 9.338 · MSFT 8.737 · WMT 8.686 · CVX 7.416 ·
XOM 7.346 · KO 5.236 · AMZN 5.060 · JPM 2.883 · GOOGL 1.754 · JNJ 977 · PFE 932 · BAC 742.

## Sanidade dos impactos (medidos, não previstos)

| Horizonte | n | média | desvio | min | max |
|---|---|---|---|---|---|
| +1d | 79.753 | +0,09% | 2,65% | −22,12% | +24,37% |
| +3d | 79.753 | +0,32% | 4,44% | −34,01% | +40,87% |
| +5d | 79.553 válidos | — | — | −43,05% | +56,48% |

**Achado honesto:** exatamente **200 registos (0,25%)** têm impacto **+5d = NaN**, todos com
data ≥ 2023-12-16 — o fim da janela de preços (max da data de notícia + 10 dias de calendário)
não deixa 5 dias de negociação à frente. +1d/+3d estão completos. Consumidores da KB devem
ignorar impactos NaN (o `explain_news_impact` já lida com dicionários de impacto parciais).

## Consultas de exemplo (SBERT real, offline)

- *"Nvidia unveils new AI chip for data centers"* → cluster AI da NVDA (sim 0,74–0,82; ex.:
  "NVIDIA Launches AI Data Center Platform", 2018-09-13, +5d −1,86%).
- *"Federal Reserve raises interest rates to fight inflation"* → cluster macro **cross-ticker**
  (NVDA/WMT/AMZN, sim 0,62–0,65) — tema, não direção, como a tese discute (CS3).
- *"Tesla recalls thousands of vehicles over safety concerns"* → recalls reais da TSLA
  (sim 0,80–0,85; impactos +5d de −15,04% a +8,53% — o mesmo aviso: cluster mistura direções).

## Consumo (decisão honesta)

A produção na nuvem (runner do Actions e app Streamlit) **continua de propósito na stack
leve** com a KB-amostra + HashingEmbedder — nada muda nos números da tese nem no deploy.
A KB multi-ano serve para uso local com SBERT (ex.: `run_news_trigger(kb_path=...)`) e como
base do trabalho futuro registado no Cap. 6 (avaliação multi-ano com dispersão e consistência
de direção). A demo (`scripts/demo.py`) continua a usar `data/samples/kb_sample.jsonl` —
o exemplo do Cap. 3 (+6,46%) reproduz-se como sempre.
