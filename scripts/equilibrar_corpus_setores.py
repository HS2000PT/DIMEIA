"""Deriva do corpus fixado um subconjunto equilibrado por setor, de forma determinística.

**Porque isto existe.** O corpus honestamente recolhido é **84% tecnologia**, porque sete das
quinze empresas da lista são tecnológicas e são também as de maior volume de notícias. Num corpus
assim, a precisão@k agregada deixa de medir a capacidade de recuperar por tema e passa a medir a
composição: devolver tecnologia já é quase sempre a resposta certa, pelo que o acaso sobe a
`0,685` e a linha lexical fica a três pontos do modelo semântico. O agregado não fica errado —
fica **incapaz de distinguir** o que a §5.3 existe para distinguir.

O corpus anterior escondia isto por um acidente: a API truncava cada empresa em ~250 manchetes,
o que dava a cada empresa o mesmo peso e fazia a composição setorial coincidir com a proporção de
**empresas** por setor (tecnologia a `7/15 = 0,467`). Era um equilíbrio involuntário, produzido
por um defeito, e por isso não se pode continuar a usar.

Este subconjunto produz o mesmo efeito **de propósito e declaradamente**: a mesma quantidade de
manchetes por setor, escolhidas com semente fixa. O agregado volta a ser legível e a janela
continua a ser a janela recolhida. As três vistas respondem a perguntas diferentes e a §5.3
reporta-as como três:

1. **corpus truncado** — a janela declarada não era a recolhida; não se usa;
2. **corpus honesto completo** — a janela é verdade, o agregado é dominado pela composição;
3. **corpus honesto equilibrado** — a janela é verdade e o agregado é interpretável.

A medição **por setor** atravessa as três e é a que sustenta a conclusão da QI2, precisamente
porque não depende da composição.

Uso:
    python scripts/equilibrar_corpus_setores.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from investigator.news_fetcher.relevance import SECTOR_OF  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--origem", default=str(RAIZ / "data" / "finnhub_news.csv"))
    ap.add_argument("--destino", default=str(RAIZ / "data" / "finnhub_news_equilibrado.csv"))
    ap.add_argument("--manifesto",
                    default=str(RAIZ / "docs" / "design" / "finnhub_equilibrado_manifest.json"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    origem = Path(args.origem)
    if not origem.exists():
        print(f"ERRO: {origem} não existe. Correr scripts/fixar_corpus_finnhub.py primeiro.")
        return 2

    df = pd.read_csv(origem)
    df["setor"] = df["ticker"].map(SECTOR_OF)
    if df["setor"].isna().any():
        print("ERRO: tickers sem setor no mapa canónico.")
        return 2

    # O setor mais pequeno fixa a quota: qualquer valor acima obrigaria a reamostrar com
    # repetição, e uma manchete contada duas vezes não é uma segunda observação.
    quota = int(df["setor"].value_counts().min())
    partes = [
        g.sample(n=quota, random_state=args.seed).sort_values(["ticker", "date"])
        for _, g in df.groupby("setor", sort=True)
    ]
    eq = pd.concat(partes).reset_index(drop=True)

    destino = Path(args.destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    eq.drop(columns=["setor"]).to_csv(destino, index=False)

    h = hashlib.sha256()
    with destino.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)

    dias = pd.to_datetime(eq["date"]).dt.date
    manifesto = {
        "gerado": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "derivado_de": origem.name,
        "ficheiro": destino.name,
        "sha256": h.hexdigest(),
        "seed": args.seed,
        "quota_por_setor": quota,
        "manchetes": int(len(eq)),
        "empresas": int(eq["ticker"].nunique()),
        "janela": {"primeiro": str(dias.min()), "ultimo": str(dias.max())},
        "por_setor": {
            s: {"manchetes": int(n), "fracao": round(float(n) / len(eq), 4)}
            for s, n in eq["setor"].value_counts().items()
        },
        "nota": (
            "A quota é o tamanho do setor mais pequeno do corpus completo, para que nenhuma "
            "manchete seja contada duas vezes. Existe para tornar o agregado interpretável: no "
            "corpus completo, 84% de tecnologia fazem o acaso subir a 0,685 e o agregado passa a "
            "medir composição em vez de capacidade de recuperação."
        ),
    }
    Path(args.manifesto).write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Equilibrado: {len(eq):,} manchetes, {quota} por setor, "
          f"{eq['ticker'].nunique()} empresas")
    print(f"  janela {dias.min()} … {dias.max()}")
    print(f"  sha256 {h.hexdigest()}")
    print(f"Manifesto em {args.manifesto}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
