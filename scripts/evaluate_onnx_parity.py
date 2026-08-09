"""Paridade entre o embedder de PRODUÇÃO (MiniLM-ONNX int8) e o da TESE (SbertEmbedder).

PORQUE É QUE ISTO EXISTE
------------------------
A tese afirma dois números sobre esta substituição — concordância de embeddings (cosseno) e
concordância de *retrieval* (top-3) — e o Capítulo 3 garante que **cada figura reportada é
produzida por um script versionado**. Até 2026-08-09 estes dois números eram a excepção: foram
medidos à mão numa máquina e escritos no `.md`. Um número que ninguém consegue regenerar não é
reprodutível, por muito verdadeiro que seja; e com o repositório privado, o arguente não tem
sequer como o inspeccionar. Este script fecha essa lacuna.

O QUE MEDE, E PORQUE SÃO DUAS COISAS
------------------------------------
1. **Embeddings**: cosseno entre o vector ONNX e o vector sentence-transformers para as mesmas
   manchetes. Mede se o espaço semântico é o mesmo.
2. **Retrieval**: sobreposição dos top-k vizinhos devolvidos pelos dois motores sobre a MESMA
   base de conhecimento. É esta que interessa ao produto — o utilizador recebe *vizinhos*, não
   vectores, e dois motores podem discordar no 4.º decimal de um cosseno e devolver a mesma
   lista. A distinção não é académica: a quantização int8 move os vectores, e a pergunta certa
   é se move a ORDEM.

Requer a stack pesada (`setup_env.sh --ml`): o lado B é o sentence-transformers da tese.

USO
---
    python scripts/evaluate_onnx_parity.py
    python scripts/evaluate_onnx_parity.py --kb data/samples/kb_fnspid_light.jsonl --k 3
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import UTC, datetime

import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

DESTINO = RAIZ / "docs" / "evaluation" / "evaluation_onnx_parity.md"
KB_PADRAO = RAIZ / "data" / "samples" / "kb_fnspid_light.jsonl"

# Queries canónicas: as três que o produto usa como demonstração, mais manchetes reais da
# própria KB. Fixas no código (e não amostradas) para o número ser reprodutível.
QUERIES_CANONICAS = (
    "Nvidia unveils new AI chips for data centers",
    "Federal Reserve raises interest rates to fight inflation",
    "Tesla recalls thousands of vehicles over safety concerns",
)
# ⚠️ 2026-08-09: a medição original usava 20 manchetes e reportava 20/23 conjuntos idênticos.
# Esse número **não reproduz**: com outra amostra do mesmo tamanho obtêm-se 12/23. A causa não
# é o motor, é o tamanho da amostra — a 23 consultas a estatística é instável e o valor
# depende de quais manchetes calharam. A resposta certa não é escolher a amostra que dá o
# número simpático, é usar uma amostra grande o suficiente para o número parar de se mexer.
N_QUERIES_DA_KB = 500
SEMENTE = 42


def _carregar_kb(caminho: pathlib.Path) -> list[dict]:
    linhas = caminho.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(x) for x in linhas]


def _cos(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Cosseno linha-a-linha entre duas matrizes já alinhadas."""
    an = a / np.linalg.norm(a, axis=1, keepdims=True)
    bn = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.sum(an * bn, axis=1)


def _topk(consulta: np.ndarray, base: np.ndarray, k: int) -> list[list[int]]:
    """Índices dos k vizinhos mais próximos por cosseno, para cada linha de `consulta`."""
    cn = consulta / np.linalg.norm(consulta, axis=1, keepdims=True)
    bn = base / np.linalg.norm(base, axis=1, keepdims=True)
    sims = cn @ bn.T
    return [list(np.argsort(-linha)[:k]) for linha in sims]


def main() -> int:
    ap = argparse.ArgumentParser(description="Paridade ONNX vs SBERT")
    ap.add_argument("--kb", default=str(KB_PADRAO))
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--out", default=str(DESTINO))
    args = ap.parse_args()

    from investigator.historical_kb.embedder import SbertEmbedder
    from investigator.historical_kb.onnx_embedder import OnnxMiniLMEmbedder

    kb = _carregar_kb(pathlib.Path(args.kb))
    manchetes_kb = [c["headline"] for c in kb]
    rng = np.random.default_rng(SEMENTE)
    idx = rng.choice(len(manchetes_kb), size=min(N_QUERIES_DA_KB, len(manchetes_kb)),
                     replace=False)
    queries = list(QUERIES_CANONICAS) + [manchetes_kb[i] for i in idx]

    onnx, sbert = OnnxMiniLMEmbedder(), SbertEmbedder()

    # (1) concordância de embeddings sobre as queries
    ea = np.asarray(onnx.encode(queries), dtype="float64")
    eb = np.asarray(sbert.encode(queries), dtype="float64")
    cos = _cos(ea, eb)

    # (2) concordância de retrieval na configuração de PRODUÇÃO.
    #
    # ⚠️ É aqui que a primeira versão deste script mediu a coisa errada, e vale a pena deixar
    # escrito. Em produção a base de conhecimento guarda embeddings **já calculados pelo
    # SBERT** (e arredondados a 5 casas para caber no git); o único vector que o motor ONNX
    # produz em tempo de execução é o da **consulta**. Re-embeber a base inteira com cada
    # motor — que foi o que fiz primeiro — introduz erro dos dois lados e responde a uma
    # pergunta que a produção nunca faz. O resultado passou de 20/23 para 10/23, e a
    # diferença não era um defeito do produto: era do instrumento.
    base_guardada = np.asarray([c["embedding"] for c in kb], dtype="float64")
    ta = _topk(ea, base_guardada, args.k)   # consulta ONNX  → base guardada  (= produção)
    tb = _topk(eb, base_guardada, args.k)   # consulta SBERT → base guardada  (= tese)

    iguais = sum(1 for x, y in zip(ta, tb, strict=True) if list(x) == list(y))
    comuns = sum(len(set(x) & set(y)) for x, y in zip(ta, tb, strict=True))
    total = args.k * len(queries)

    # (2b) variante ESTRITA: base re-embebida por cada motor. Não é a produção, mas limita o
    # erro no pior caso, por isso reporta-se ao lado em vez de se escolher o número simpático.
    ba = np.asarray(onnx.encode(manchetes_kb), dtype="float64")
    bb = np.asarray(sbert.encode(manchetes_kb), dtype="float64")
    ta2, tb2 = _topk(ea, ba, args.k), _topk(eb, bb, args.k)
    iguais2 = sum(1 for x, y in zip(ta2, tb2, strict=True) if list(x) == list(y))
    comuns2 = sum(len(set(x) & set(y)) for x, y in zip(ta2, tb2, strict=True))

    # Natureza das divergências: a afirmação a testar é que discordar no k-ésimo vizinho é um
    # empate, não uma troca de tema. Mede-se a diferença de similaridade entre o vizinho que
    # um motor escolheu e o que o outro escolheu no mesmo lugar.
    qn = ea / np.linalg.norm(ea, axis=1, keepdims=True)
    bn = base_guardada / np.linalg.norm(base_guardada, axis=1, keepdims=True)
    sims_prod = qn @ bn.T
    folgas: list[float] = []
    for i, (x, y) in enumerate(zip(ta, tb, strict=True)):
        for so_a in set(x) - set(y):
            for so_b in set(y) - set(x):
                folgas.append(abs(float(sims_prod[i, so_a] - sims_prod[i, so_b])))
    folga_mediana = float(np.median(folgas)) if folgas else 0.0
    folga_max = float(np.max(folgas)) if folgas else 0.0

    linhas = [
        "# evaluation_onnx_parity.md — motor de produção (ONNX) vs motor da tese (SBERT)",
        "",
        f"> Gerado por `scripts/evaluate_onnx_parity.py` a {datetime.now(UTC):%Y-%m-%d %H:%M} UTC.",
        "> **Não editar à mão.** Semente fixa; re-correr reproduz.",
        "",
        f"- Base de conhecimento: `{pathlib.Path(args.kb).as_posix()}` ({len(kb)} casos)",
        f"- Consultas: {len(queries)} ({len(QUERIES_CANONICAS)} canónicas "
        f"+ {len(idx)} manchetes da KB, semente {SEMENTE})",
        f"- Vizinhos comparados: top-{args.k}",
        "",
        "## 1. Concordância de embeddings",
        "",
        "| métrica | valor |",
        "|---|---|",
        f"| cosseno médio | **{cos.mean():.4f}** |",
        f"| cosseno mínimo | **{cos.min():.4f}** |",
        "",
        "## 2. Concordância de retrieval (o que o utilizador recebe)",
        "",
        "Configuração de **produção**: a base guarda os embeddings SBERT; só a consulta passa",
        "pelo ONNX. É a única diferença que existe em runtime.",
        "",
        "| métrica | valor |",
        "|---|---|",
        f"| conjuntos top-{args.k} idênticos | **{iguais}/{len(queries)}** |",
        f"| vizinhos comuns no total | **{comuns}/{total} "
        f"({100 * comuns / total:.0f} %)** |",
        "",
        "Variante **estrita** (base também re-embebida por cada motor — não é o que a produção",
        "faz, mas limita o erro no pior caso):",
        "",
        "| métrica | valor |",
        "|---|---|",
        f"| conjuntos top-{args.k} idênticos | {iguais2}/{len(queries)} |",
        f"| vizinhos comuns no total | {comuns2}/{total} ({100 * comuns2 / total:.0f} %) |",
        "",
        "## 3. Natureza das divergências",
        "",
        "| métrica | valor |",
        "|---|---|",
        f"| divergências observadas | {len(folgas)} |",
        f"| diferença de similaridade, mediana | **{folga_mediana:.4f}** |",
        f"| diferença de similaridade, máxima | {folga_max:.4f} |",
        "",
        "**Leitura.** O cosseno mede se o espaço é o mesmo; a sobreposição de vizinhos mede se",
        "a **ordem** é a mesma, e é essa que o produto entrega. As duas podem divergir: a",
        "quantização int8 desloca os vectores sem necessariamente trocar a ordenação. A",
        "distância entre as duas tabelas é o custo de re-embeber a base, que a produção não paga.",
        "A secção 3 diz se uma divergência importa: uma troca entre vizinhos separados por",
        "milésimos de similaridade é um empate, não um tema diferente.",
        "",
    ]
    saida = pathlib.Path(args.out)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text("\n".join(linhas), encoding="utf-8")

    print(f"cosseno medio {cos.mean():.4f} / minimo {cos.min():.4f}")
    print(f"top-{args.k} identicos {iguais}/{len(queries)} · vizinhos comuns {comuns}/{total}")
    print(f"Escrito: {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
