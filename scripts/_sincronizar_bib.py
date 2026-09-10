"""Compara tese-pt/references.bib com tese-eng/references.bib e, opcionalmente, sincroniza.

Sem argumentos: so mostra as diferencas (linha a linha).
Com --escrever: copia a versao portuguesa por cima da inglesa, byte a byte.

A regra da tese e que as duas arvores citam exactamente a mesma bibliografia; havendo
divergencia, a portuguesa e a fonte.
"""
import difflib
import pathlib
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

RAIZ = pathlib.Path(__file__).resolve().parents[1]
PT = RAIZ / "tese-pt" / "references.bib"
EN = RAIZ / "tese-eng" / "references.bib"


def main():
    escrever = "--escrever" in sys.argv
    b_pt = PT.read_bytes()
    b_en = EN.read_bytes()
    if b_pt == b_en:
        print("identicos byte a byte:", len(b_pt), "bytes")
        return
    t_pt = b_pt.decode("utf-8", "replace").splitlines()
    t_en = b_en.decode("utf-8", "replace").splitlines()
    dif = list(difflib.unified_diff(t_en, t_pt, "tese-eng", "tese-pt", lineterm="", n=1))
    print(f"diferem: {len(t_en)} vs {len(t_pt)} linhas, {len(dif)} linhas de diff")
    for linha in dif[:80]:
        print(linha)
    if len(dif) > 80:
        print(f"... (+{len(dif) - 80} linhas)")
    if escrever:
        EN.write_bytes(b_pt)
        print("\nESCRITO: tese-eng/references.bib passou a ser copia da portuguesa.")


if __name__ == "__main__":
    main()
