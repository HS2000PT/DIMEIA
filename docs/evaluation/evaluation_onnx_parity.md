# evaluation_onnx_parity.md — motor de produção (ONNX) vs motor da tese (SBERT)

> Gerado por `scripts/evaluate_onnx_parity.py` a 2026-08-09 19:03 UTC.
> **Não editar à mão.** Semente fixa; re-correr reproduz.

- Base de conhecimento: `C:/Users/henri/Desktop/DIMEIA/data/samples/kb_fnspid_light.jsonl` (2016 casos)
- Consultas: 503 (3 canónicas + 500 manchetes da KB, semente 42)
- Vizinhos comparados: top-3

## 1. Concordância de embeddings

| métrica | valor |
|---|---|
| cosseno médio | **0.9916** |
| cosseno mínimo | **0.9830** |

## 2. Concordância de retrieval (o que o utilizador recebe)

Configuração de **produção**: a base guarda os embeddings SBERT; só a consulta passa
pelo ONNX. É a única diferença que existe em runtime.

| métrica | valor |
|---|---|
| conjuntos top-3 idênticos | **383/503** |
| vizinhos comuns no total | **1435/1509 (95 %)** |

Variante **estrita** (base também re-embebida por cada motor — não é o que a produção
faz, mas limita o erro no pior caso):

| métrica | valor |
|---|---|
| conjuntos top-3 idênticos | 312/503 |
| vizinhos comuns no total | 1370/1509 (91 %) |

## 3. Natureza das divergências

| métrica | valor |
|---|---|
| divergências observadas | 74 |
| diferença de similaridade, mediana | **0.0057** |
| diferença de similaridade, máxima | 0.0311 |

**Leitura.** O cosseno mede se o espaço é o mesmo; a sobreposição de vizinhos mede se
a **ordem** é a mesma, e é essa que o produto entrega. As duas podem divergir: a
quantização int8 desloca os vectores sem necessariamente trocar a ordenação. A
distância entre as duas tabelas é o custo de re-embeber a base, que a produção não paga.
A secção 3 diz se uma divergência importa: uma troca entre vizinhos separados por
milésimos de similaridade é um empate, não um tema diferente.
