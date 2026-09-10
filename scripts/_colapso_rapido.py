"""Porta de colapso, isolada e barata: corre sem esperar pelo resto da avaliacao.

A avaliacao completa da QI4 leva minutos e concorre com o treino que ainda esteja a decorrer.
Esta porta responde a unica pergunta que interessa primeiro -- **o codificador ainda distingue
manchetes?** -- embebendo algumas centenas de titulos e mais nada.

Uso:
    python scripts\\_colapso_rapido.py data\\qi4_modelos\\magnitude_v2 [mais modelos...]

Imprime, por modelo: o perfil de dispersao e a comparacao contra o `all-MiniLM-L6-v2` sem ajuste.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

from investigator.qi4 import colapso as C  # noqa: E402

BASE = "all-MiniLM-L6-v2"
QUANTAS = 1500


def manchetes(n: int) -> list[str]:
    caminho = REPO / "data" / "qi4_dataset.csv"
    if not caminho.exists():
        caminho = REPO / "data" / "fnspid_news_subset.csv"
    df = pd.read_csv(caminho)
    coluna = next(c for c in ("headline", "title", "manchete") if c in df.columns)
    # Titulos distintos: repetidos inflacionam artificialmente o cosseno medio e fariam a
    # porta disparar sobre um modelo saudavel.
    unicos = df[coluna].dropna().astype(str).drop_duplicates()
    return unicos.head(n).tolist()


def embeber(caminho: str, textos: list[str]) -> np.ndarray:
    from sentence_transformers import SentenceTransformer

    m = SentenceTransformer(caminho)
    return m.encode(textos, normalize_embeddings=True, show_progress_bar=False,
                    batch_size=64, convert_to_numpy=True)


def main() -> int:
    argumentos = sys.argv[1:]
    base = BASE
    if "--base" in argumentos:
        i = argumentos.index("--base")
        base = argumentos[i + 1]
        argumentos = argumentos[:i] + argumentos[i + 2:]
    alvos = argumentos
    if not alvos:
        print("uso: _colapso_rapido.py [--base <modelo>] <caminho_do_modelo> [...]")
        return 2
    textos = manchetes(QUANTAS)
    print(f"{len(textos)} manchetes distintas\n")

    print(f"--- base ({base}) ---")
    vb = embeber(base, textos)
    pb = C.perfil(vb)
    print(f"  cosseno entre manchetes diferentes: {pb['cosseno_medio']:.4f} "
          f"(desvio {pb['cosseno_dp']:.4f})")
    print(f"  norma do vetor medio: {pb['norma_do_vetor_medio']:.4f}")
    print(f"  colapsou: {pb['colapsou']}\n")

    houve = False
    for alvo in alvos:
        nome = pathlib.Path(alvo).name
        print(f"--- {nome} ---")
        if not pathlib.Path(alvo).exists():
            print("  (ainda nao existe)\n")
            continue
        va = embeber(alvo, textos)
        pa = C.perfil(va)
        cmp_ = C.comparar(vb, va)
        marca = "COLAPSADO" if pa["colapsou"] else "ok"
        houve = houve or pa["colapsou"]
        print(f"  [{marca}] cosseno entre manchetes diferentes: {pa['cosseno_medio']:.4f} "
              f"(desvio {pa['cosseno_dp']:.4f})   <- base {pb['cosseno_medio']:.4f}")
        print(f"  norma do vetor medio: {pa['norma_do_vetor_medio']:.4f} "
              f"  <- base {pb['norma_do_vetor_medio']:.4f}")
        print(f"  desvio por dimensao: {pa['desvio_por_dimensao']:.4f} "
              f"  <- base {pb['desvio_por_dimensao']:.4f}")
        print(f"  moveu-se? cosseno base<->ajustado: medio "
              f"{cmp_['cosseno_medio_base_ajustado']:.4f}, "
              f"minimo {cmp_['cosseno_min_base_ajustado']:.4f}")
        print(f"  preservou a geometria? correlacao das similaridades: "
              f"{cmp_['correlacao_das_geometrias']:.4f}\n")

    if houve:
        print("PELO MENOS UM BRACO COLAPSOU. Nao ler metricas destes bracos.")
        return 1
    print("Nenhum braco colapsou.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
