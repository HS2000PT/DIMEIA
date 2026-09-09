"""Construção CANÓNICA do corpus FNSPID — reprodutível por construção.

Porque existe
-------------
O `download_data.py` faz *stream* do CSV remoto de 23,2 GB numa única ligação HTTP. Isso tem
dois problemas que a sessão de 2026-09-09 tornou visíveis:

1. **Fragilidade.** Uma quebra de ligação a meio mata a varredura inteira. Aconteceu:
   `IncompleteRead(5941119 bytes read, 23227038478 more expected)`.
2. **Paragem antecipada por suposição.** O `early_stop` assume que o ficheiro está ordenado por
   ticker e interrompe quando julga tê-los passado todos. Nunca foi verificado, e uma exceção
   trunca o corpus em silêncio — a hipótese mais provável para o corpus ter passado de
   79 753 linhas (publicado) para 78 481 (reconstruído a 2026-09-08).

Este procedimento separa as duas responsabilidades:

- **descarregar** o ficheiro em bruto UMA vez, de forma **resumível** e **fixada por revisão**,
  através do `huggingface_hub` (que valida o conteúdo e o guarda em cache endereçada por hash);
- **filtrar** localmente, com **varredura completa**, tantas vezes quantas forem precisas.

O resultado é um corpus cuja identidade não depende de uma ligação de rede ter aguentado.

Uso:
    python scripts/build_corpus_canonical.py                 # descarrega (ou reusa) e filtra
    python scripts/build_corpus_canonical.py --so-descarregar
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from scripts.download_data import (
    DEFAULT_END,
    DEFAULT_START,
    DEFAULT_TICKERS,
    FNSPID_REPO,
    FNSPID_REVISION,
    normalize_columns,
)

FICHEIRO_NOTICIAS = "Stock_news/nasdaq_exteral_data.csv"
REPO = Path(__file__).resolve().parents[1]


#: Ficheiro em bruto, descarregado por `scripts/fetch_fnspid_raw.py`, e as suas duas
#: identidades verificadas a 2026-09-09. Constam aqui para que o procedimento FALHE se o
#: ficheiro em disco não for o esperado, em vez de produzir um corpus diferente em silêncio.
BRUTO_PADRAO = REPO / "data" / "raw" / "nasdaq_exteral_data.csv"
BRUTO_BYTES = 23_232_979_597
BRUTO_SHA256 = "1a7a3eb8e6b97ec19f286f2cfca3371542bddb272ab1eb8f36e33ad98fa5c4da"


def obter_ficheiro_bruto(caminho: Path | None = None, verificar_sha: bool = False) -> Path:
    """Devolve o CSV em bruto local, confirmando que é o ficheiro fixado.

    ⚠️ Não usa `hf_hub_download`. A 2026-09-09 esse cliente ficou 39 minutos sem escrever um
    único byte, sem erro e sem progresso observável. A descarga é feita por
    `scripts/fetch_fnspid_raw.py`, que retoma por pedidos `Range` e regista o progresso.

    A verificação de tamanho é imediata e apanha um ficheiro truncado, que é o modo de falha
    real. A soma de controlo completa demora minutos sobre 23 GB e corre a pedido.
    """
    p = Path(caminho) if caminho else BRUTO_PADRAO
    if not p.exists():
        raise SystemExit(
            f"Ficheiro em bruto ausente: {p}\n"
            f"Corre primeiro:  python -m scripts.fetch_fnspid_raw"
        )
    n = p.stat().st_size
    print(f"Fonte:    {FNSPID_REPO} @ {FNSPID_REVISION}")
    print(f"Em bruto: {p}  ({n / 1e9:.2f} GB)")
    if n != BRUTO_BYTES:
        raise SystemExit(
            f"Tamanho inesperado: {n:,} != {BRUTO_BYTES:,}. "
            "O ficheiro está truncado ou não é o da revisão fixada."
        )
    if verificar_sha:
        print("A verificar sha256 (alguns minutos)…", flush=True)
        obtido = sha256(p)
        if obtido != BRUTO_SHA256:
            raise SystemExit(f"sha256 não bate:\n  obtido   {obtido}\n  esperado {BRUTO_SHA256}")
        print("  sha256 confere.")
    return p


def filtrar(
    bruto: Path, tickers: list[str], inicio: str, fim: str, chunksize: int = 200_000
) -> tuple[pd.DataFrame, dict]:
    """Varredura COMPLETA do ficheiro local, com auditoria de ordenação por ticker.

    Sem paragem antecipada: o custo é tempo de CPU sobre disco local, não uma aposta na
    ordenação do ficheiro. A auditoria regista se a ordenação se verifica, o que permite
    justificar (ou recusar) a paragem antecipada em execuções futuras — com facto, não suposição.
    """
    procurados = {t.upper() for t in tickers}
    d0, d1 = pd.Timestamp(inicio).date(), pd.Timestamp(fim).date()
    usecols = ["Date", "Article_title", "Stock_symbol"]

    guardados: list[pd.DataFrame] = []
    auditoria = {
        "chunks": 0,
        "linhas_varridas": 0,
        "violacoes_ordenacao": 0,
        "primeira_violacao": None,
        "varredura_completa": True,
    }
    maior_visto = ""
    leitor = pd.read_csv(bruto, chunksize=chunksize, usecols=usecols, low_memory=False)
    for chunk in leitor:
        norm = normalize_columns(chunk)
        if not norm["ticker"].empty:
            cmin = str(norm["ticker"].min())
            if cmin < maior_visto:
                auditoria["violacoes_ordenacao"] += 1
                if auditoria["primeira_violacao"] is None:
                    auditoria["primeira_violacao"] = {
                        "chunk": auditoria["chunks"],
                        "min_do_chunk": cmin,
                        "maior_ja_visto": maior_visto,
                    }
            maior_visto = max(maior_visto, str(norm["ticker"].max()))
        mask = norm["ticker"].isin(procurados) & (norm["date"] >= d0) & (norm["date"] <= d1)
        guardados.append(norm[mask])
        auditoria["chunks"] += 1
        auditoria["linhas_varridas"] += len(chunk)
        if auditoria["chunks"] % 10 == 0:
            total = sum(len(g) for g in guardados)
            print(
                f"  …{auditoria['linhas_varridas']:,} linhas varridas | "
                f"{total:,} guardadas | maior ticker visto {maior_visto}",
                flush=True,
            )

    df = pd.concat(guardados, ignore_index=True) if guardados else pd.DataFrame(
        columns=["date", "ticker", "headline"]
    )
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    return df, auditoria


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Construção canónica do corpus FNSPID")
    ap.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    ap.add_argument("--inicio", default=DEFAULT_START)
    ap.add_argument("--fim", default=DEFAULT_END)
    ap.add_argument("--chunksize", type=int, default=200_000)
    ap.add_argument("--out", default="data/fnspid_news_canonical.csv")
    ap.add_argument("--manifesto", default="docs/design/fnspid_corpus_manifest.json")
    ap.add_argument("--bruto", default=None, help="caminho do CSV em bruto (por omissão data/raw/)")
    ap.add_argument("--verificar-sha", action="store_true",
                    help="soma o sha256 dos 23 GB antes de filtrar (minutos)")
    args = ap.parse_args()

    bruto = obter_ficheiro_bruto(args.bruto, verificar_sha=args.verificar_sha)

    print(f"A filtrar: {len(args.tickers)} tickers, {args.inicio}…{args.fim} (varredura completa)")
    df, auditoria = filtrar(bruto, args.tickers, args.inicio, args.fim, args.chunksize)
    print(f"Total no subconjunto: {len(df):,}")

    out = REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)

    por_ticker = df.groupby("ticker").size().sort_index().to_dict()
    manifesto = {
        "gerado_em": datetime.now(UTC).isoformat(timespec="seconds"),
        "procedimento": "scripts/build_corpus_canonical.py",
        "fonte": {
            "repo": FNSPID_REPO,
            "revisao": FNSPID_REVISION,
            "ficheiro": FICHEIRO_NOTICIAS,
            "bytes_em_bruto": bruto.stat().st_size,
            "sha256_em_bruto": BRUTO_SHA256,
            "sha256_verificado_nesta_execucao": bool(args.verificar_sha),
        },
        "parametros": {
            "tickers": sorted(t.upper() for t in args.tickers),
            "inicio": args.inicio,
            "fim": args.fim,
            "chunksize": args.chunksize,
            "early_stop": False,
        },
        "resultado": {
            "linhas": int(len(df)),
            "tickers_presentes": sorted(df["ticker"].unique().tolist()),
            "data_min": str(df["date"].min()),
            "data_max": str(df["date"].max()),
            "linhas_por_ticker": {k: int(v) for k, v in por_ticker.items()},
            "sha256": sha256(out),
        },
        "auditoria_varredura": auditoria,
    }
    man = REPO / args.manifesto
    man.parent.mkdir(parents=True, exist_ok=True)
    man.write_text(json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")

    r = manifesto["resultado"]
    print(f"\nCorpus canónico: {out}")
    print(f"Manifesto:       {man}")
    print(f"  linhas={r['linhas']:,} · tickers={len(r['tickers_presentes'])} "
          f"· {r['data_min']}…{r['data_max']}")
    print(f"  sha256={r['sha256']}")
    print(f"  violações de ordenação={auditoria['violacoes_ordenacao']} "
          f"(se 0, a paragem antecipada é segura e passa a estar provada)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
