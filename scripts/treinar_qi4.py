"""Treina um braço da QI4 e grava o codificador ajustado com o seu manifesto.

Três braços, o mesmo arnês:

    # principal — materialidade comparável, nunca direção
    python -m scripts.treinar_qi4 --arma magnitude --saida models/qi4/magnitude

    # replicação — retorno com sinal, reproduzindo [Jeong26] aqui dentro
    python -m scripts.treinar_qi4 --arma direcao --saida models/qi4/direcao

    # controlo — codificador de domínio com o objetivo principal
    python -m scripts.treinar_qi4 --arma magnitude --base ProsusAI/finbert \\
        --saida models/qi4/dominio

Os pares saem SEMPRE do bloco de treino, com o mapa de percentis ajustado nesse bloco. O
`investigator/qi4/pares.py` garante-o e `tests/test_qi4_pares.py` prova-o.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from investigator.console import force_utf8_stdout
from investigator.qi4 import ajuste, pares

REPO = Path(__file__).resolve().parents[1]


def main() -> int:
    force_utf8_stdout()
    ap = argparse.ArgumentParser(description="Treino de um braço da QI4")
    ap.add_argument("--dataset", default=str(REPO / "data" / "qi4_dataset.csv"))
    ap.add_argument("--arma", choices=list(pares.ARMAS), required=True)
    ap.add_argument("--horizonte", type=int, default=3,
                    help="horizonte do retorno anormal (o primário da tese é 3)")
    ap.add_argument("--base", default=ajuste.BASE_PADRAO)
    ap.add_argument("--saida", required=True)
    ap.add_argument("--n-pares", type=int, default=40_000)
    ap.add_argument("--epocas", type=int, default=1)
    ap.add_argument("--lote", type=int, default=32)
    ap.add_argument("--taxa", type=float, default=2e-5)
    ap.add_argument("--perda", choices=list(ajuste.PERDAS), default="cosent")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--passos-max", type=int, default=None,
                    help="corta o treino a N passos (sondagem de tempo)")
    args = ap.parse_args()

    df = pd.read_csv(args.dataset)
    coluna = f"abn_h{args.horizonte}"
    antes = len(df)
    df = df.dropna(subset=[coluna])
    print(f"Dataset: {antes:,} linhas · {antes - len(df):,} sem {coluna} · {len(df):,} úteis")
    print(f"Blocos: {df['split'].value_counts().to_dict()}")

    p = pares.construir_pares(df, coluna_retorno=coluna, arma=args.arma,
                              n_pares=args.n_pares, seed=args.seed, blocos=("train",))
    print(f"Pares: {len(p):,} · braço {args.arma} · alvo médio {p['alvo'].mean():.3f} "
          f"(desvio {p['alvo'].std():.3f})")
    print(f"Base: {args.base} · perda {args.perda} · lote {args.lote} · "
          f"{args.epocas} época(s) · taxa {args.taxa:g}")

    man = ajuste.ajustar(p, saida=args.saida, modelo_base=args.base, epocas=args.epocas,
                         lote=args.lote, taxa=args.taxa, seed=args.seed, perda=args.perda,
                         passos_max=args.passos_max)
    man["arma"] = args.arma
    man["horizonte"] = args.horizonte
    man["dataset"] = str(args.dataset)
    man["alvo_medio"] = round(float(p["alvo"].mean()), 6)
    (Path(args.saida) / "manifesto_qi4.json").write_text(
        json.dumps(man, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nModelo em {args.saida}")
    print(f"  {man['passos_por_epoca']} passos/época · {man['segundos']:.0f} s "
          f"({man['segundos'] / max(man['passos_por_epoca'] * args.epocas, 1):.2f} s/passo)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
