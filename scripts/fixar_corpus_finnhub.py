"""Fixa o corpus de notícias do Finnhub como artefacto, com manifesto versionado.

**Porque isto existe.** O corpus da §5.3 não estava fixado por nada: o CSV de origem não estava
em disco e a recolha dependia de uma API cujo comportamento não estava caracterizado. A 2026-09-10
mediu-se que o `/company-news` gratuito devolve no máximo ~250 itens por pedido e, ao bater nesse
tecto, **ignora o `from`** — pedir 5, 13 ou 27 dias da mesma empresa devolve as mesmas manchetes,
dos mesmos poucos dias, sem erro nem aviso. A janela declarada deixava de ser a janela medida, e a
truncagem era proporcional ao volume de notícias de cada empresa, o que entrelaçava a cobertura
temporal com a identidade da empresa numa secção que mede recuperação **por setor**.

O corpus fixado aqui é recolhido com a janela partida em fatias de um dia, pelo que **nenhum
pedido bate no tecto** salvo nos dias em que uma só empresa gera mais de ~250 manchetes — o que é
irredutível, porque a granularidade mínima da API é o dia (`from` e `to` são datas, não
instantes). Essa truncagem residual é medida e declarada no manifesto, não escondida.

O manifesto segue a convenção do `precos_manifest.json`: versionado, com a proveniência, as
dimensões e a soma de controlo, enquanto o CSV fica gitignored por ser grande e regenerável.

Uso:
    python scripts/fixar_corpus_finnhub.py --origem data/_arquivo/_finnhub_news_fatiado.csv
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from investigator.news_fetcher.relevance import SECTOR_OF  # noqa: E402

#: Acima disto um pedido de um único dia veio ao tecto da API e o dia está truncado.
TECTO_API = 240


def soma(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--origem", required=True, help="CSV recolhido com --fatiar")
    ap.add_argument("--destino", default=str(RAIZ / "data" / "finnhub_news.csv"))
    ap.add_argument("--manifesto",
                    default=str(RAIZ / "docs" / "design" / "finnhub_corpus_manifest.json"))
    ap.add_argument("--fatia", type=int, default=1,
                    help="dias por pedido usados na recolha (para o registo)")
    args = ap.parse_args()

    origem = Path(args.origem)
    if not origem.exists():
        print(f"ERRO: {origem} não existe.")
        return 2

    df = pd.read_csv(origem)
    df["setor"] = df["ticker"].map(SECTOR_OF)
    if df["setor"].isna().any():
        faltam = sorted(df.loc[df["setor"].isna(), "ticker"].unique())
        print(f"ERRO: tickers sem setor no mapa canónico: {faltam}")
        return 2

    dias = pd.to_datetime(df["date"]).dt.date
    por_dia = df.assign(d=dias).groupby(["ticker", "d"]).size()
    truncados = por_dia[por_dia >= TECTO_API]

    destino = Path(args.destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(origem, destino)

    manifesto = {
        "gerado": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fonte": "Finnhub /company-news (plano gratuito)",
        "ficheiro": destino.name,
        "sha256": soma(destino),
        "manchetes": int(len(df)),
        "empresas": int(df["ticker"].nunique()),
        "janela": {"primeiro": str(dias.min()), "ultimo": str(dias.max())},
        "recolha": {
            "fatia_dias": args.fatia,
            "nota": (
                "A janela é pedida em fatias de um dia porque a API devolve no máximo ~250 "
                "itens por pedido e, ao atingir esse tecto, ignora o `from`. Sem fatiar, "
                "pedir 27 dias devolvia as ~250 manchetes mais recentes e a cobertura real "
                "variava de 3 a 28 dias segundo o volume de notícias da empresa."
            ),
        },
        "por_empresa": {
            tk: {
                "manchetes": int((df["ticker"] == tk).sum()),
                "primeiro": str(dias[df["ticker"] == tk].min()),
                "ultimo": str(dias[df["ticker"] == tk].max()),
                "dias_com_noticias": int(dias[df["ticker"] == tk].nunique()),
            }
            for tk in sorted(df["ticker"].unique())
        },
        "por_setor": {
            s: {"manchetes": int(n), "fracao": round(float(n) / len(df), 4)}
            for s, n in df["setor"].value_counts().items()
        },
        "truncagem_residual": {
            "pares_ticker_dia": int(len(por_dia)),
            "pares_no_tecto": int(len(truncados)),
            "fracao_pares": round(float(len(truncados)) / len(por_dia), 4),
            "manchetes_em_dias_truncados": int(truncados.sum()),
            "fracao_manchetes": round(float(truncados.sum()) / len(df), 4),
            "empresas": sorted({tk for tk, _ in truncados.index}),
            "nota": (
                "Irredutível com o plano gratuito: `from` e `to` são datas, logo o dia é a "
                "granularidade mínima e um dia em que uma empresa gere mais de ~250 manchetes "
                "não pode ser pedido em pedaços. Declara-se em vez de se esconder."
            ),
        },
    }

    Path(args.manifesto).write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Corpus fixado em {destino} ({len(df):,} manchetes, {df['ticker'].nunique()} empresas)")
    print(f"  janela {dias.min()} … {dias.max()}")
    print(f"  sha256 {manifesto['sha256']}")
    print(f"  truncagem residual: {len(truncados)}/{len(por_dia)} pares "
          f"({manifesto['truncagem_residual']['fracao_pares']:.2%}), "
          f"empresas {manifesto['truncagem_residual']['empresas']}")
    print(f"Manifesto em {args.manifesto}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
