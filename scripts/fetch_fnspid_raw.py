"""Descarga RESUMÍVEL do CSV em bruto do FNSPID, fixada por revisão.

Porquê à mão e não pelo cliente do Hugging Face
-----------------------------------------------
A 2026-09-09 o `hf_hub_download` ficou 39 minutos sem escrever um único byte para este
ficheiro, sem erro e sem progresso observável. Um passo que não se consegue ver progredir não
se consegue depurar nem confiar. Isto faz o mínimo, com pedidos `Range`:

- retoma exatamente onde ficou, olhando para o tamanho do ficheiro em disco;
- volta a tentar com espera crescente quando a ligação parte, que foi o modo de falha do
  `IncompleteRead` da tentativa anterior;
- escreve o progresso no registo, para que uma paragem seja visível de imediato.

O ficheiro tem ~23,2 GB. Fica em disco de propósito: uma vez descarregado, filtrar por outros
tickers ou outras datas passa a ser uma operação local de minutos, e nunca mais depende da rede.

Uso:
    python scripts/fetch_fnspid_raw.py
    python scripts/fetch_fnspid_raw.py --verificar   # só confirma tamanho e sha256
"""

from __future__ import annotations

import argparse
import hashlib
import time
from pathlib import Path

import requests

from scripts.download_data import FNSPID_REPO, FNSPID_REVISION

FICHEIRO = "Stock_news/nasdaq_exteral_data.csv"
URL = f"https://huggingface.co/datasets/{FNSPID_REPO}/resolve/{FNSPID_REVISION}/{FICHEIRO}"
REPO = Path(__file__).resolve().parents[1]
DESTINO = REPO / "data" / "raw" / "nasdaq_exteral_data.csv"


def tamanho_remoto() -> int:
    r = requests.head(URL, allow_redirects=True, timeout=60)
    r.raise_for_status()
    return int(r.headers["Content-Length"])


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 22), b""):
            h.update(bloco)
    return h.hexdigest()


def descarregar(destino: Path, total: int, tentativas: int = 200) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    espera = 2
    while True:
        feito = destino.stat().st_size if destino.exists() else 0
        if feito >= total:
            print(f"Completo: {feito:,} bytes", flush=True)
            return
        print(f"Retomar em {feito:,}/{total:,} ({100 * feito / total:.1f}%)", flush=True)
        try:
            r = requests.get(
                URL, headers={"Range": f"bytes={feito}-"}, stream=True, timeout=(30, 120)
            )
            if r.status_code not in (200, 206):
                raise RuntimeError(f"HTTP {r.status_code}")
            marco = feito
            with open(destino, "ab") as fh:
                for pedaco in r.iter_content(chunk_size=1 << 20):
                    if not pedaco:
                        continue
                    fh.write(pedaco)
                    feito += len(pedaco)
                    if feito - marco >= (256 << 20):  # a cada 256 MB
                        marco = feito
                        print(f"  {feito / 1e9:.2f} GB / {total / 1e9:.2f} GB "
                              f"({100 * feito / total:.1f}%)", flush=True)
            r.close()
            espera = 2
        except Exception as e:  # noqa: BLE001 — qualquer falha de rede é para retomar
            tentativas -= 1
            if tentativas <= 0:
                raise
            print(f"  ligação partiu ({type(e).__name__}: {e}); nova tentativa em {espera}s",
                  flush=True)
            time.sleep(espera)
            espera = min(espera * 2, 60)


def main() -> int:
    ap = argparse.ArgumentParser(description="Descarga resumível do FNSPID em bruto")
    ap.add_argument("--verificar", action="store_true")
    ap.add_argument("--destino", default=str(DESTINO))
    args = ap.parse_args()

    destino = Path(args.destino)
    total = tamanho_remoto()
    print(f"Fonte:   {URL}")
    print(f"Destino: {destino}")
    print(f"Tamanho: {total:,} bytes ({total / 1e9:.2f} GB)", flush=True)

    if not args.verificar:
        descarregar(destino, total)

    obtido = destino.stat().st_size if destino.exists() else 0
    print(f"\nEm disco: {obtido:,} bytes · completo={obtido == total}")
    if obtido == total:
        print("A somar sha256 (alguns minutos)…", flush=True)
        print(f"sha256={sha256(destino)}")
    return 0 if obtido == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
