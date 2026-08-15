"""Dá embeddings aos casos do backfill, para eles poderem ser recuperados.

**O problema.** `data/samples/backfill_kb.jsonl` tem 38 mil casos reais reconstruídos do último
ano, cada um com a manchete e com o impacto **já medido** a +1/+3/+5 dias. Falta-lhe a única
coisa que a recuperação precisa: o **vector**. Sem ele, esses casos existem e não podem ser
comparados com nada, e o alerta continua a procurar precedentes numa base de 2016 casos curados.

**O que isto faz.** Lê o ficheiro, embebe cada manchete com o MESMO embedder do produto
(MiniLM em ONNX, 384 dimensões), e escreve um ficheiro NOVO. O original não é tocado.

**Porque é um ficheiro novo.** A separação entre o que foi *observado ao vivo* e o que foi
*reconstruído* é deliberada e existe desde que o backfill foi criado. Reescrever o original
apagaria a distinção; usar o mesmo nome do ficheiro de produção confundiria as duas coisas.

**Retomável.** Escreve à medida que avança e salta o que já está feito, porque são dezenas de
milhares de manchetes e o processo pode ser interrompido.

Correr:  python scripts/embed_backfill_kb.py
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ORIGEM = RAIZ / "data" / "samples" / "backfill_kb.jsonl"
DESTINO = RAIZ / "data" / "samples" / "backfill_kb_sbert.jsonl"
LOTE = 64


def ler(p: pathlib.Path) -> list[dict]:
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def chave(r: dict) -> str:
    return f"{r.get('date')}|{r.get('ticker')}|{r.get('headline')}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--origem", default=str(ORIGEM))
    ap.add_argument("--destino", default=str(DESTINO))
    ap.add_argument("--lote", type=int, default=LOTE)
    args = ap.parse_args()

    origem, destino = pathlib.Path(args.origem), pathlib.Path(args.destino)
    if not origem.exists():
        print(f"ERRO: {origem} não existe.", file=sys.stderr)
        raise SystemExit(2)

    registos = ler(origem)
    print(f"origem : {len(registos)} casos em {origem.name}", flush=True)

    feitos: set[str] = set()
    if destino.exists():
        for r in ler(destino):
            feitos.add(chave(r))
        print(f"destino: {len(feitos)} já embebidos — a retomar", flush=True)

    falta = [r for r in registos if chave(r) not in feitos]
    if not falta:
        print("nada a fazer: já está tudo embebido.", flush=True)
        return
    print(f"por fazer: {len(falta)}", flush=True)

    # O MESMO embedder do produto. Se não estiver disponível, PARA — um backfill embebido com
    # outro modelo seria incomparável com a base de produção, e isso é pior do que não o ter.
    from investigator.historical_kb.embedder import HashingEmbedder
    from investigator.main import product_retrieval

    _, emb = product_retrieval(auto_download=True)
    if isinstance(emb, HashingEmbedder):
        print("ERRO: o embedder semântico não está disponível (caiu no fallback lexical).\n"
              "      Embeber com outro modelo produziria vectores incomparáveis com a base de\n"
              "      produção. Preferível não escrever nada.", file=sys.stderr)
        raise SystemExit(2)
    print(f"embedder: {type(emb).__name__}", flush=True)

    t0 = time.monotonic()
    escritos = 0
    with open(destino, "a", encoding="utf-8") as saida:
        for i in range(0, len(falta), args.lote):
            bloco = falta[i:i + args.lote]
            vecs = emb.encode([r["headline"] for r in bloco])
            for r, v in zip(bloco, vecs, strict=True):
                r = dict(r)
                r["embedding"] = [round(float(x), 5) for x in v]
                saida.write(json.dumps(r, ensure_ascii=False) + "\n")
                escritos += 1
            saida.flush()
            if (i // args.lote) % 20 == 0:
                passado = time.monotonic() - t0
                ritmo = escritos / passado if passado else 0
                resta = (len(falta) - escritos) / ritmo if ritmo else 0
                print(f"  {escritos}/{len(falta)}  ({ritmo:.0f}/s, faltam ~{resta/60:.0f} min)",
                      flush=True)

    print(f"FEITO: {escritos} casos embebidos -> {destino}", flush=True)
    print(f"tempo: {(time.monotonic()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()
