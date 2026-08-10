"""Proveniência do corpus de avaliação e efeito medido do filtro de relevância.

PORQUE É QUE ISTO EXISTE
------------------------
Duas grandezas que a tese usava sem as ter medido, e uma terceira que corrigia uma afirmação
falsa:

1. **A amplitude do corpus.** A tese dizia "os meses mais recentes disponíveis". São
   **27 dias**. Um corpus de menos de um mês não sustenta afirmações sobre generalização
   temporal, e chamar-lhe meses é um erro factual que qualquer leitor confirma numa linha.

2. **O que o filtro de relevância deita fora.** O funil reportado contava o que SOBREVIVEU
   (manchetes relevantes, alertas enviados) e nunca o que foi removido. Um passo que descarta
   dois terços da entrada não pode ficar por medir.

3. **A ordem temporal dos vizinhos recuperados.** A avaliação de recuperação não restringe os
   candidatos a serem anteriores à consulta — só a linha de base de recência usa datas. Num
   corpus de 27 dias isso significa que a maior parte dos "precedentes" não é anterior. A
   métrica (concordância de setor) não é afectada, porque o setor não muda com o tempo, mas a
   PALAVRA precedente é. Em produção o problema não existe: a base é de 2018--2023 e as
   consultas são de 2026, logo tudo é anterior por construção.

⚠️ **O filtro foi escrito DEPOIS de olhar para os dados** (2026-07-11, a partir de 27 alertas
reais), e os padrões de boilerplate são transcrições de falhas observadas. É engenharia
normal, não é um critério a priori, e a tese passa a dizê-lo.

USO
---
    python scripts/evaluate_corpus_and_filter.py              # tudo (precisa da stack --ml)
    python scripts/evaluate_corpus_and_filter.py --sem-modelo # salta a parte temporal
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from datetime import UTC, datetime

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

CORPUS = RAIZ / "data" / "finnhub_news.csv"
DESTINO = RAIZ / "docs" / "evaluation" / "evaluation_relevance_filter.md"
MODELO = "sentence-transformers/all-MiniLM-L6-v2"
SEMENTE = 42
N_CONSULTAS = 300


def main() -> int:
    ap = argparse.ArgumentParser(description="Corpus + filtro de relevância")
    ap.add_argument("--news", default=str(CORPUS))
    ap.add_argument("--out", default=str(DESTINO))
    ap.add_argument("--sem-modelo", action="store_true")
    args = ap.parse_args()

    from investigator.console import force_utf8_stdout
    from investigator.news_fetcher.relevance import (
        _BOILERPLATE_RE,
        COMPANY_NAMES,
        is_relevant,
    )
    from investigator.triage.dataset import SECTORS

    force_utf8_stdout()

    df = pd.read_csv(args.news).dropna(subset=["date", "ticker", "headline"])
    df["ticker"] = df["ticker"].astype(str).str.upper()
    df = df[df["ticker"].isin(SECTORS)].reset_index(drop=True)
    datas = pd.to_datetime(df["date"])
    dias = int((datas.max() - datas.min()).days)

    # (2) efeito do filtro, restrito aos tickers que o produto varre (os que têm aliases).
    # Fora deles o filtro cai no fallback "só o símbolo conta", e quase nenhuma manchete
    # escreve "BAC" — a taxa de retenção desabaria por uma razão que é da LISTA e não do texto.
    com_alias = df[df["ticker"].isin(COMPANY_NAMES)].reset_index(drop=True)
    n = len(com_alias)
    boiler = com_alias["headline"].str.lower().str.contains(_BOILERPLATE_RE, regex=True)
    mantidas = com_alias.apply(lambda r: is_relevant(r["headline"], r["ticker"]), axis=1)
    n_keep, n_boiler = int(mantidas.sum()), int(boiler.sum())
    n_sem = n - n_keep - n_boiler

    linhas = [
        "# evaluation_relevance_filter.md — proveniência do corpus e efeito do filtro",
        "",
        "> Gerado por `scripts/evaluate_corpus_and_filter.py` a "
        f"{datetime.now(UTC):%Y-%m-%d %H:%M} UTC. **Não editar à mão.**",
        "",
        "## 1. O corpus de avaliação",
        "",
        "| item | valor |",
        "|---|---|",
        f"| manchetes (com setor conhecido) | **{len(df)}** |",
        f"| tickers | {df['ticker'].nunique()} |",
        f"| primeira data | {datas.min():%Y-%m-%d} |",
        f"| última data | {datas.max():%Y-%m-%d} |",
        f"| amplitude | **{dias} dias** |",
        "",
        f"⚠️ **{dias} dias**, não meses. Um corpus desta amplitude não sustenta afirmações sobre",
        "generalização temporal, e é por isso que o resultado de recuperação é reportado como",
        "preliminar e repetido à escala sobre o FNSPID multi-ano.",
        "",
        "## 2. O que o filtro de relevância deita fora",
        "",
        f"Restrito aos {com_alias['ticker'].nunique()} tickers com lista de aliases, que são os",
        "que o produto varre.",
        "",
        "| decisão | manchetes | quota |",
        "|---|---|---|",
        f"| **mantidas** | {n_keep} | **{100 * n_keep / n:.1f}%** |",
        f"| descartadas | {n - n_keep} | {100 * (n - n_keep) / n:.1f}% |",
        f"| &nbsp;&nbsp;— boilerplate de mercado | {n_boiler} | {100 * n_boiler / n:.1f}% |",
        f"| &nbsp;&nbsp;— não menciona a empresa | {n_sem} | {100 * n_sem / n:.1f}% |",
        f"| total | {n} | 100% |",
        "",
        "**Leitura.** O trabalho é feito pela regra da menção, não pela lista de boilerplate: os",
        f"padrões de resumo de mercado explicam apenas {100 * n_boiler / n:.1f}% dos descartes. E",
        "a taxa de retenção depende da lista de aliases: tickers sem entrada caem no fallback",
        "\"só o símbolo conta\", e quase nenhuma manchete escreve o símbolo.",
        "",
    ]

    if not args.sem_modelo:
        from investigator.evaluation.retrieval_eval import (
            _normalize_rows,
            same_ticker_forbid,
        )
        from investigator.historical_kb.embedder import SbertEmbedder

        emb = _normalize_rows(np.asarray(
            SbertEmbedder(MODELO).encode(df["headline"].astype(str).tolist()), dtype="float64"))
        tick = df["ticker"].to_numpy()
        dts = datas.to_numpy()
        rng = np.random.default_rng(SEMENTE)
        q = rng.choice(len(df), size=min(N_CONSULTAS, len(df)), replace=False)
        sims = np.where(same_ticker_forbid(tick[q], tick), -np.inf, emb[q] @ emb.T)
        top = np.argsort(-sims, axis=1)[:, :5]
        depois = int((dts[top] > dts[q][:, None]).sum())
        igual = int((dts[top] == dts[q][:, None]).sum())
        tot = int(top.size)
        antes = tot - depois - igual
        linhas += [
            "## 3. Os vizinhos recuperados são anteriores à consulta?",
            "",
            f"{N_CONSULTAS} consultas, top-5, cross-ticker — o mesmo protocolo da avaliação.",
            "",
            "| posição temporal do vizinho | n | quota |",
            "|---|---|---|",
            f"| **posterior** à consulta | {depois} | **{100 * depois / tot:.1f}%** |",
            f"| mesma data | {igual} | {100 * igual / tot:.1f}% |",
            f"| anterior | {antes} | {100 * antes / tot:.1f}% |",
            "",
            "**Leitura, e é a que corrige a palavra.** A avaliação não restringe os candidatos a",
            "serem anteriores; só a linha de base de recência usa datas. Num corpus de "
            f"{dias} dias, o resultado é que apenas {100 * antes / tot:.1f}% dos vizinhos são",
            "anteriores. **A métrica não é afectada** — mede concordância de setor, e o setor de",
            "uma manchete não muda com o tempo — mas o que se mede é *recuperação semântica de",
            "itens do mesmo setor*, e não *recuperação de precedentes*.",
            "",
            "**Em produção o problema não existe:** a base curada é de 2018--2023 e as consultas",
            "são de 2026, portanto todos os casos recuperados são anteriores por construção.",
            "",
        ]

    saida = pathlib.Path(args.out)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text("\n".join(linhas), encoding="utf-8")
    print(f"corpus {len(df)} manchetes · {dias} dias "
          f"({datas.min():%Y-%m-%d} a {datas.max():%Y-%m-%d})")
    print(f"filtro: {n_keep}/{n} mantidas ({100 * n_keep / n:.1f}%) · "
          f"boilerplate {100 * n_boiler / n:.1f}% · sem menção {100 * n_sem / n:.1f}%")
    print(f"Escrito: {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
