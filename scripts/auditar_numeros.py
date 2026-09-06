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

# ⚠️ NUMEROS QUE SAO AFIRMACOES DA TESE MAS NAO TEM (NEM PODEM TER) FICHEIRO DE AVALIACAO POR TRAS.
# Cada um foi rastreado a mao a 2026-08-22 e a razao esta escrita. A lista existe para que a saida
# do varrimento seja ACCIONAVEL: sem ela sao vinte e seis nomes de que ninguem se lembra porque
# estao la, e um numero novo e verdadeiramente sem fonte passaria despercebido no meio deles.
# Acrescentar aqui exige escrever a razao. Se a razao nao se escrever, o numero e um defeito.
JUSTIFICADOS: dict[str, str] = {
    # Cada entrada e um numero que a tese afirma e que nenhum ficheiro de avaliacao
    # sustenta, com a razao pela qual isso esta certo. A lista e podada sempre que o
    # verificador diz que uma entrada deixou de corresponder a alguma coisa: uma
    # justificacao que ja nao justifica nada e folclore, e a lista perde autoridade.

    # (a) nao sao afirmacoes: composicao e versoes de bibliotecas
    "1.08": "\\arraystretch da matriz de evidencia, medida de composicao",
    "3.11": "versao do matplotlib", "3.12": "versao do Python",

    # (b) contagens de producao, datadas, que crescem com o sistema
    "11445": "casos da base viva na branch de dados; instantaneo datado (Cap. 4)",
    "10968": "registos da base viva no momento da medicao de memoria (apendice A.5)",

    # (c) o funil de um dia, com ficheiro proprio
    "1194": "funil por porta, docs/evaluation/funil_por_porta.md",
    # (d) aritmetica que a propria figura mostra
    "4727": ("soma das eliminacoes da Figura do funil (2994+1194+269+249+21); "
             "a legenda enuncia-a para que o leitor a possa refazer, e 5060-4727=333"),
}




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
    # A ARVORE E A CANONICA. Este verificador apontava para `tese/`, que foi superseda:
    # reportava ok sobre um documento que nao e entregue, ou seja garantia falsa na
    # porta. E os NOMES dos ficheiros mudam com a arvore -- apontar a arvore certa sem
    # corrigir a lista deixa-o a ler o frontmatter e mais nada, que e o defeito que a
    # sessao 63 pagou e quase mandou corrigir uma tese que estava certa.
    for f in sorted(glob.glob(str(RAIZ / "tese-pt" / "ch*" / "chapter*.tex"))) + \
             sorted(glob.glob(str(RAIZ / "tese-pt" / "appendices" / "*.tex"))) + \
             [str(RAIZ / "tese-pt" / "frontmatter" / "frontmatter.tex")]:
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

    novos = [n for n in sem_fonte if n not in JUSTIFICADOS]
    mortos = [n for n in JUSTIFICADOS if n not in sem_fonte]

    print(f"números de prosa e tabelas: {len(alvos)}")
    print(f"sem ocorrência em nenhuma fonte: {len(sem_fonte)}")
    print(f"  dos quais rastreados à mão e justificados: {len(sem_fonte) - len(novos)}")
    print(f"  SEM ORIGEM CONHECIDA: {len(novos)}\n")

    if mortos:
        print("⚠️  Justificações que já não correspondem a nada (o número saiu da tese ou")
        print("    ganhou fonte). Apagar da lista, para ela não virar folclore:")
        print("      " + "  ".join(sorted(mortos)) + "\n")

    if novos:
        print("  " + "  ".join(novos))
        print("\n⚠️  Cada um destes é um número que a tese afirma e que nenhum ficheiro sustenta.")
        print("    Ou ganha fonte, ou ganha uma linha em JUSTIFICADOS com a razão escrita.")
        return 1

    print("Todos os números da prosa e das tabelas têm origem conhecida.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
