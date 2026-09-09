"""Um codificador ajustado pode parecer treinado e não ter capacidade de distinguir nada.

A primeira tentativa da QI4 produziu uma tabela de métricas plausível — comparabilidade
2,156 pontos contra 2,173 da base — que não valia nada: os dois modelos mapeavam **todas** as
manchetes para praticamente o mesmo vetor. O cosseno entre manchetes diferentes tinha subido de
`0,22` para `0,99`. Só se soube porque se foi verificar.

Daqui em diante nenhuma tabela da QI4 se lê sem estes números ao lado. É barato e evita
publicar o resultado de um modelo degenerado.
"""

from __future__ import annotations

import numpy as np

#: Acima disto considera-se que a representação colapsou. O `all-MiniLM-L6-v2` sem ajuste dá
#: `0,22` sobre manchetes financeiras; um modelo colapsado dá `> 0,99`. O limiar é folgado de
#: propósito: serve para apanhar o desastre, não para afinar nada.
LIMIAR_COLAPSO = 0.90


def perfil(vetores: np.ndarray) -> dict:
    """Mede a dispersão de um conjunto de vetores já normalizados.

    Returns:
        `cosseno_medio` entre pares distintos (baixo = saudável), `norma_do_vetor_medio`
        (0 = isotrópico, 1 = tudo no mesmo sítio), `desvio_por_dimensao` e `colapsou`.
    """
    v = np.asarray(vetores, dtype="float64")
    if len(v) < 2:
        raise ValueError("perfil: precisa de pelo menos dois vetores")
    s = v @ v.T
    fora = s[np.triu_indices(len(v), k=1)]
    cos = float(fora.mean())
    return {
        "n": int(len(v)),
        "cosseno_medio": cos,
        "cosseno_dp": float(fora.std()),
        "norma_do_vetor_medio": float(np.linalg.norm(v.mean(axis=0))),
        "desvio_por_dimensao": float(v.std(axis=0).mean()),
        "colapsou": bool(cos > LIMIAR_COLAPSO),
    }


def comparar(base: np.ndarray, ajustado: np.ndarray) -> dict:
    """Quanto é que o ajuste mexeu — em vetores e em geometria.

    O cosseno par-a-par diz se os vetores se moveram; a correlação entre as duas matrizes de
    similaridade diz se as **relações** entre manchetes mudaram, que é o que interessa a um
    sistema de recuperação. Um modelo pode mover todos os vetores e preservar a geometria, ou
    o contrário.
    """
    b = np.asarray(base, dtype="float64")
    a = np.asarray(ajustado, dtype="float64")
    if b.shape != a.shape:
        raise ValueError(f"formas diferentes: {b.shape} contra {a.shape}")
    cos = np.sum(b * a, axis=1)
    n = min(500, len(b))
    tri = np.triu_indices(n, k=1)
    sb, sa = (b[:n] @ b[:n].T)[tri], (a[:n] @ a[:n].T)[tri]
    return {
        "cosseno_medio_base_ajustado": float(cos.mean()),
        "cosseno_min_base_ajustado": float(cos.min()),
        "correlacao_das_geometrias": float(np.corrcoef(sb, sa)[0, 1]),
    }
