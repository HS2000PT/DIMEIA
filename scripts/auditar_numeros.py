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
    # (a) instantaneos de dados reais mostrados verbatim: o valor E o dado, nao um resultado
    "0.0112": "vetor de um registo real da base de casos (Cap. 3)",
    "0.0243": "idem", "0.1301": "idem", "0.0662": "idem",
    "0.0674": "impacto a +3d do mesmo registo real",
    "0.01266203305026954": "linha real do conjunto de treino, mostrada com todas as casas (Cap. 3)",
    "0.024854333506149767": "idem", "0.036392215960942983": "idem",
    # (b) valores derivados cuja aritmetica a propria tese mostra a fazer
    "0.0128": "logit por 80 caracteres; a tese mostra peso x escala no mesmo paragrafo",
    "0.252": "parcela da volatilidade no exemplo trabalhado; a tabela mostra a soma",
    "0.437": "3.700 x 0.507 - 2.313, escrito na propria celula",
    "2.72": "sigma dos 20 dias da Tesla; a tabela ao lado mostra as parcelas",
    "0.217": "reconstrucao do leitor a duas casas, contra o 0.218 reportado; a tese di-lo",
    "7.63": "reconstrucao do leitor a duas casas, contra o 7.61 reportado; a tese di-lo",
    "0.336": "0.968 - 0.632, escrito na mesma frase",
    "0.143": "0.632 - 0.489, escrito na mesma frase",
    "0.037": "limite superior de [-0.0321, +0.0366] em evaluation_triage_within.md, a 3 casas",
    "0.462": "limite inferior de um IC do mesmo ficheiro, a 3 casas",
    # (c) exemplo ilustrativo, marcado como tal ("do genero...")
    "2.11": "linha de alerta dada como exemplo de FORMATO no Cap. 4", "1.71": "idem",
    # (d) nao sao afirmacoes: composicao e versoes de bibliotecas
    "1.15": "\\arraystretch, medida de composicao",
    "3.11": "versao do matplotlib", "3.12": "versao do Python", "5.12": "versao do transformers",
    # (e) o funil de um dia, agora com ficheiro proprio
    "1194": "funil por porta, docs/evaluation/funil_por_porta.md",
    "2994": "idem",
    "1785": "candidatas por maturar no incidente do Cap. 4; lido do registo, dito no sitio",
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
