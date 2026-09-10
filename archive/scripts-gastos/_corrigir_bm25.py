"""Corrige os metadados de robertson2009bm25 no .bib, preservando as terminacoes de linha.

A citacao "3(4), 333-389" que circula (e que o Google Scholar propaga) nao bate certo com o
deposito do proprio editor no Crossref, que declara volume 4, numero 1-2, paginas 1-174.
"""
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
PT = RAIZ / "tese-pt" / "references.bib"

ANTIGO = """  year      = {2009},
  volume    = {3},
  number    = {4},
  pages     = {333--389},"""

NOVO = """  year      = {2009},
  %% Verificada no Crossref a 2026-09-09 contra o deposito do proprio editor: volume 4,
  %% numero 1-2, paginas 1-174. ATENCAO: circula muito uma citacao "3(4), 333-389" --- e a
  %% que o Google Scholar propaga, e era a que esta entrada tinha. Nao bate certo com o
  %% registo do editor, e e este que prevalece.
  volume    = {4},
  number    = {1-2},
  pages     = {1--174},"""


def main():
    bruto = PT.read_bytes().decode("utf-8")
    crlf = "\r\n" in bruto
    texto = bruto.replace("\r\n", "\n")
    if texto.count(ANTIGO) != 1:
        print(f"ABORTADO: encontrei {texto.count(ANTIGO)} ocorrencias, esperava 1")
        return 1
    texto = texto.replace(ANTIGO, NOVO)
    if crlf:
        texto = texto.replace("\n", "\r\n")
    PT.write_bytes(texto.encode("utf-8"))
    print("corrigido; terminacoes preservadas:", "CRLF" if crlf else "LF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
