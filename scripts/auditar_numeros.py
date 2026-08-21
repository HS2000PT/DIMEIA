"""Todo o número da PROSA e das TABELAS da tese, e onde ele aparece nas fontes.

⚠️ POR QUE E QUE ISTO EXISTE, e em que difere do `check_tese_numeros.py`. Aquele verifica uma
lista curada de 53 números contra o ficheiro que os produz: garante que os que estão na lista
estão certos, e nada diz sobre os que não estão. Este faz o inverso — varre o documento inteiro
e pergunta, de cada número, se ele existe em ALGUMA fonte. O que interessa é o resto: os números
que a tese afirma e que nenhum ficheiro sustenta.

O QUE E EXCLUIDO, e porquê. As coordenadas de TikZ não são afirmações: são posições de desenho,
e uma varredura ingénua enche-se delas (a primeira versão devolveu 94 falsos positivos). Também
saem os ambientes de código e os índices de equação.

    python scripts/auditar_numeros.py
"""

from __future__ import annotations

import glob
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
B = chr(92)

# ambientes que NAO sao prosa nem tabela: o que la esta dentro sao coordenadas ou codigo
NAO_PROSA = ("tikzpicture", "lstlisting", "verbatim", "equation", "equation*", "align", "align*",
             "aligned", "array")


def prosa_e_tabelas(texto: str) -> str:
    for amb in NAO_PROSA:
        texto = re.sub(B + B + r"begin\{" + amb + r"\*?\}.*?" + B + B + r"end\{" + amb + r"\*?\}",
                       " ", texto, flags=re.S)
    texto = re.sub(r"(?m)^\s*%.*$", " ", texto)          # comentarios de linha inteira
    texto = re.sub(r"(?<!" + B + B + r")%.*", " ", texto)  # comentarios em fim de linha
    return texto


def numeros(texto: str) -> set[str]:
    """Decimais com 2+ casas e inteiros com separador de milhar: os que sao afirmacoes."""
    fora = set(re.findall(r"\b\d+\.\d{2,}\b", texto))
    fora |= {m.replace(B + ",", "").replace(",", "")
             for m in re.findall(r"\b\d{1,3}" + B + B + r",\d{3}\b", texto)}
    return fora


def main() -> int:
    corpo = ""
    for f in sorted(glob.glob(str(RAIZ / "tese" / "cap*" / "*.tex"))) + \
             sorted(glob.glob(str(RAIZ / "tese" / "apendices" / "*.tex"))) + \
             [str(RAIZ / "tese" / "frontmatter" / "frontmatter.tex")]:
        corpo += prosa_e_tabelas(open(f, encoding="utf-8", errors="replace").read())

    fontes = ""
    for padrao in ("docs/evaluation/*.md", "docs/evaluation/*.csv", "docs/decisions/*.md",
                   "config/*.yaml"):
        for f in glob.glob(str(RAIZ / padrao)):
            fontes += open(f, encoding="utf-8", errors="replace").read()
    for f in glob.glob(str(RAIZ / "investigator" / "**" / "*.py"), recursive=True):
        fontes += open(f, encoding="utf-8", errors="replace").read()

    alvos = sorted(numeros(corpo))
    sem_fonte = []
    for n in alvos:
        variantes = {n, n.rstrip("0").rstrip("."), n.replace(".", ","),
                     f"{n[:-3]},{n[-3:]}" if n.isdigit() and len(n) > 3 else n}
        if not any(v and v in fontes for v in variantes):
            sem_fonte.append(n)

    print(f"números de prosa e tabelas: {len(alvos)}")
    print(f"sem ocorrência em nenhuma fonte: {len(sem_fonte)}\n")
    if sem_fonte:
        print("  " + "  ".join(sem_fonte))
        print("\n⚠️  Nem todos são defeitos: há valores derivados que a própria tese mostra a")
        print("    calcular, e medições sobre os dados brutos. Mas cada um destes tem de ter")
        print("    a sua origem escrita no sítio onde aparece.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
