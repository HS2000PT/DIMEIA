"""Mede o desvio entre a KB reconstruida e a amostra congelada do build original.

Porque existe
-------------
O corpus esta fixado por sha256. Os PRECOS nao estao fixados por nada: o `build_kb.py` vai
ao yfinance no momento do build, e os fechos ajustados sao reescritos retroativamente a cada
dividendo ou desdobramento. O mesmo vale para os embeddings, que dependem da versao do
`sentence-transformers` instalada.

`data/samples/kb_fnspid_sample.jsonl` traz 50 registos do build de 2026-07-05, versionados
em git. Sao a unica referencia congelada que existe. Este script compara-os com a KB
reconstruida, registo a registo, em vez de supor que nada mudou.

Uso:
    .venv\\Scripts\\python.exe -m scripts.verificar_desvio_kb
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
AMOSTRA = REPO / "data" / "samples" / "kb_fnspid_sample.jsonl"
KB = REPO / "data" / "kb_fnspid_sbert.jsonl"


def carregar(caminho: Path, limite: int | None = None) -> list[dict]:
    registos = []
    with open(caminho, encoding="utf-8") as fh:
        for linha in fh:
            linha = linha.strip()
            if not linha:
                continue
            registos.append(json.loads(linha))
            if limite and len(registos) >= limite:
                break
    return registos


def chave(r: dict) -> tuple:
    return (str(r.get("ticker")), str(r.get("date"))[:10], str(r.get("headline")).strip())


def main() -> int:
    if not AMOSTRA.exists():
        raise SystemExit(f"Ausente: {AMOSTRA}")
    if not KB.exists():
        raise SystemExit(f"Ausente: {KB}")

    ref = carregar(AMOSTRA)
    print(f"Amostra congelada (2026-07-05): {len(ref)} registos")
    print(f"Campos: {sorted(ref[0].keys())}")

    procurados = {chave(r) for r in ref}
    novos: dict[tuple, dict] = {}
    with open(KB, encoding="utf-8") as fh:
        for linha in fh:
            linha = linha.strip()
            if not linha:
                continue
            r = json.loads(linha)
            k = chave(r)
            if k in procurados and k not in novos:
                novos[k] = r
            if len(novos) == len(procurados):
                break
    print(f"Encontrados na KB reconstruida: {len(novos)}/{len(procurados)}")

    em_falta = procurados - set(novos)
    if em_falta:
        print("\nAUSENTES (o corpus mudou de conteudo):")
        for k in sorted(em_falta)[:10]:
            print(f"  {k[0]} {k[1]} | {k[2][:70]}")

    return comparar(ref, novos)


def comparar(ref: list[dict], novos: dict[tuple, dict]) -> int:
    horizontes: dict[str, list[tuple[float, float]]] = {}
    cossenos: list[float] = []
    dims: set[int] = set()

    for r in ref:
        k = chave(r)
        n = novos.get(k)
        if n is None:
            continue
        a, b = r.get("impacts") or {}, n.get("impacts") or {}
        for h in sorted(set(a) | set(b)):
            va, vb = a.get(h), b.get(h)
            if va is None or vb is None:
                continue
            horizontes.setdefault(h, []).append((float(va), float(vb)))
        ea, eb = r.get("embedding"), n.get("embedding")
        if ea and eb:
            va_, vb_ = np.asarray(ea, float), np.asarray(eb, float)
            dims.add(len(va_))
            dims.add(len(vb_))
            if len(va_) == len(vb_):
                den = np.linalg.norm(va_) * np.linalg.norm(vb_)
                if den > 0:
                    cossenos.append(float(va_ @ vb_ / den))

    print("\n=== IMPACTOS (preco) ===")
    if not horizontes:
        print("  sem impactos comparaveis")
    problema = False
    for h, pares in sorted(horizontes.items()):
        arr = np.asarray(pares, float)
        d = np.abs(arr[:, 0] - arr[:, 1])
        iguais = int((d < 1e-12).sum())
        print(f"  {h:>4s}  n={len(arr):3d}  identicos={iguais:3d}  "
              f"|delta| max={d.max():.3e}  medio={d.mean():.3e}")
        if d.max() > 1e-6:
            problema = True

    print("\n=== EMBEDDINGS (SBERT) ===")
    print(f"  dimensoes observadas: {sorted(dims) or 'n/d'}")
    if cossenos:
        c = np.asarray(cossenos)
        print(f"  n={len(c)}  cosseno min={c.min():.9f}  medio={c.mean():.9f}")
        if c.min() < 0.999999:
            problema = True
    else:
        print("  a amostra congelada nao guarda embeddings comparaveis")

    print("\nVEREDICTO:", "DESVIO DETECTADO" if problema else
          "sem desvio mensuravel — a KB reconstruida iguala o build congelado")
    return 1 if problema else 0


if __name__ == "__main__":
    raise SystemExit(main())
