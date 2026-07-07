# Validação: MiniLM em ONNX (produto) vs SBERT (tese)

> **Data:** 2026-07-07 · **Objetivo:** provar que o retrieval semântico da app pública/runner
> (MiniLM `all-MiniLM-L6-v2` exportado em ONNX **quantizado**, `model_quint8_avx2.onnx`,
> ~23 MB, `onnxruntime` CPU, sem torch) vive no MESMO espaço de embeddings do
> `SbertEmbedder` avaliado na tese — antes de o pôr em produção.
> Reproduzir: os testes de `tests/test_onnx_embedder.py` cobrem o contrato; os números
> abaixo foram medidos nesta máquina com a stack ML (`setup_env.sh --ml`) instalada.

## O que se comparou

- **A:** `OnnxMiniLMEmbedder` (tokenizers + onnxruntime; mean pooling com máscara + L2 —
  pipeline idêntico ao do sentence-transformers; SHA256 do modelo e do tokenizer pinados
  em `investigator/historical_kb/onnx_embedder.py`).
- **B:** `SbertEmbedder` (sentence-transformers 5.6.0, o da tese).

## Resultados

**1. Concordância de embeddings** (63 manchetes reais do FNSPID, espaçadas + 3 queries):

| métrica | valor |
|---|---|
| cosseno(A, B) mínimo | **0,9868** |
| cosseno(A, B) médio | **0,9919** |
| normas L2 = 1 | ✓ (ambos) |

A diferença é o ruído da quantização int8 — o espaço semântico é o mesmo.

**2. Concordância de retrieval** (KB curada 384-d, 2.016 registos; top-3 por query;
23 queries = 3 canónicas + 20 manchetes reais da própria KB):

| métrica | valor |
|---|---|
| conjuntos top-3 idênticos | **20/23** |
| vizinhos comuns no total | **66/69 (96 %)** |
| natureza das 3 divergências | empate no 3.º vizinho (ex.: sim 0,475 vs 0,474) |

**3. Queries canónicas via ONNX** (o que o utilizador vê):

- *"Nvidia unveils new AI chips for data centers"* → **NVIDIA Launches AI Data Center
  Platform** (NVDA 2018-09-13, sim 0,80) + procura de data centers na pandemia + AWS/AI.
- *"Federal Reserve raises interest rates to fight inflation"* → cluster de inflação/subida
  de taxas (sim 0,53) — tema certo, cross-ticker.
- *"Tesla recalls thousands of vehicles over safety concerns"* → **Safety Group Calls For
  Tesla Recall After NTSB Report** (TSLA 2019-09-06, sim 0,73) — o precedente exato que o
  word-overlap 256-d não devolvia em 1.º.

**4. Arredondamento dos embeddings na KB versionada** (5 casas decimais, para o ficheiro
caber no git: 7,7 MB): erro de cosseno < 1e-4 — incluído na medição acima (a KB consultada
já era a arredondada).

## Decisão e âmbito

- **Em produção** (app pública + runner do Actions): retrieval semântico MiniLM-ONNX sobre a
  KB curada 384-d; **fail-open** para a KB-amostra word-overlap se o modelo não estiver
  disponível (sem rede/sem cache) — o produto nunca cai.
- **Fora do âmbito:** os números da tese (P@5 0,549/0,569 etc.) foram medidos com o
  `SbertEmbedder` e **não mudam**; este documento valida a *paridade do motor de produção*,
  não re-avalia retrieval (avaliação multi-ano continua trabalho futuro, Cap. 6).
