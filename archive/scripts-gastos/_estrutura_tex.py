"""Imprime a arvore de seccoes de um .tex, com numero de linha e contagem de linhas.

Uso: python scripts\\_estrutura_tex.py <ficheiro.tex> [<ficheiro.tex> ...]
Evita passar regex pela linha de comandos (o cmd come '^' e '|').
"""
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

RX = re.compile(r"^\s*\\(chapter|section|subsection|subsubsection)\*?\{(.*)")
NIVEL = {"chapter": 0, "section": 1, "subsection": 2, "subsubsection": 3}


def main():
    for caminho in sys.argv[1:]:
        with open(caminho, encoding="utf-8", errors="replace") as fh:
            linhas = fh.read().splitlines()
        print(f"### {caminho} ({len(linhas)} linhas)")
        marcas = []
        for n, linha in enumerate(linhas, start=1):
            m = RX.match(linha)
            if m:
                marcas.append((n, m.group(1), m.group(2).rstrip("}")))
        for i, (n, tipo, titulo) in enumerate(marcas):
            fim = marcas[i + 1][0] - 1 if i + 1 < len(marcas) else len(linhas)
            recuo = "  " * NIVEL[tipo]
            print(f"{n:6d}  {recuo}{titulo}   [{fim - n + 1} linhas]")
        print()


if __name__ == "__main__":
    main()
