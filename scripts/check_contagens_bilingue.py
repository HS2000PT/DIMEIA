"""Diagnóstico: os numerais escritos por extenso batem entre a árvore inglesa e a portuguesa?

PORQUE É QUE ESTE FICHEIRO EXISTE. A 2026-09-10 encontraram-se **dois** defeitos da mesma família,
os dois no Capítulo 6 e os dois **só na árvore inglesa**, que é a que vai ser entregue:

  * a legenda da figura-resumo dizia «The three research questions» e «The three answers» sobre uma
    figura que desenha **quatro**, com «the negative answer» no singular quando dois dos quatro
    veredictos são negativos;
  * a prosa dizia «On three distinct occasions... on three others» e a frase seguinte prometia «the
    seven», o que dá 3+3 e não 7.

Nos dois casos **o português estava correcto**. A causa é a mesma: a QI4 foi acrescentada depois de
o Capítulo 6 estar escrito, o lado português foi actualizado e o inglês não.

⚠️ **O QUE AS PORTAS EXISTENTES NÃO APANHAVAM.** O `check_bilingual_parity` compara as frases que
carregam **citação**, e nenhuma destas carrega. O `check_tese_numeros` compara **decimais** contra a
fonte, e «quatro» não é um decimal. Uma contagem prometida em prosa vivia entre as duas.

⚠️ **E ESTE SCRIPT NÃO É UMA PORTA. SAI SEMPRE A 0, E A RAZÃO É MEDIDA.** Três versões deram 25, 11
e 9 achados, e em todas a esmagadora maioria era gramática e não defeito: o português usa «um/uma»
como artigo indefinido, o inglês diz «both» onde o português diz «os dois», e os compostos
(«seven hundred» contra «setecentos») partem-se em palavras que são numerais isolados. A terceira
versão, ao excluir compostos, passou a **comer enumerações legítimas** — em «a um, três e cinco
dias» o `três` é seguido de «e cinco» e desaparecia. Trocar o gritar por cegueira é o par que este
projeto documenta desde a sessão 63.

**Os dois defeitos reais foram encontrados A LER**, e é isso que fica escrito. O que este script
faz é levantar candidatos para triagem humana, e diz de si próprio que a maioria será gramática.

USO:  python scripts/check_contagens_bilingue.py
"""

from __future__ import annotations

import pathlib
import re
import sys

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = pathlib.Path(__file__).resolve().parents[1]
B = chr(92)

#: O numeral 1 fica de fora por desenho: em português é também o artigo indefinido.
#: `both` entra como 2, porque é o que o inglês escreve onde o português diz «os dois».
EN = {"both": 2, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
      "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
      "fourteen": 14, "fifteen": 15, "seventeen": 17, "nineteen": 19, "twenty": 20}
PT = {"dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
      "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "treze": 13, "catorze": 14,
      "quinze": 15, "dezassete": 17, "dezanove": 19, "vinte": 20}

RX_EN = re.compile(r"\b(" + "|".join(EN) + r")\b", re.I)
RX_PT = re.compile(r"\b(" + "|".join(PT) + r")\b", re.I)

#: Um numeral seguido destas palavras faz parte de um COMPOSTO e não é uma contagem.
#: ⚠️ A LISTA PARA AQUI DE PROPÓSITO. Excluir também «e cinco», para apanhar «duas mil e
#: quinhentas», passava a comer enumerações: «a um, três e cinco dias» perdia o `três`.
COMPOSTO = re.compile(r"^\s*(?:hundred|thousand|million|mil|milh|cent|quinhent|setecent)", re.I)

FLUT = re.compile(
    B + B + r"begin\{(figure|table|tikzpicture|lstlisting|sidewaysfigure)\*?\}"
    r".*?" + B + B + r"end\{\1\*?\}", re.S)
CMD = re.compile(B + B + r"[a-zA-Z@]+\*?(\[[^\]]*\])?")
MAT = re.compile(r"\$[^$]*\$")
LIXO = {ord(c): " " for c in "{}~&" + B}


def paragrafos(caminho: pathlib.Path) -> list[str]:
    """Os parágrafos de prosa, sem flutuantes, sem comentários e sem comandos."""
    t = caminho.read_text(encoding="utf-8", errors="replace").replace(chr(13), "")
    t = FLUT.sub(" ", t)
    t = re.sub(r"(?m)^%.*$", " ", t)
    fora = []
    for par in re.split(r"\n\s*\n", t):
        limpo = CMD.sub(" ", MAT.sub(" 0 ", par)).translate(LIXO)
        limpo = " ".join(limpo.split())
        if len(limpo) > 120:
            fora.append(limpo)
    return fora


def contagens(texto: str, rx: re.Pattern, mapa: dict[str, int]) -> list[int]:
    fora = set()
    for m in rx.finditer(texto):
        if COMPOSTO.match(texto[m.end():m.end() + 24]):
            continue
        fora.add(mapa[m.group(1).lower()])
    return sorted(fora)


def main() -> int:
    candidatos: list[str] = []
    comparados = 0
    idiomaticos = 0
    for n in range(1, 7):
        en = paragrafos(RAIZ / f"tese-eng/ch{n}/chapter{n}.tex")
        pt = paragrafos(RAIZ / f"tese-pt/ch{n}/chapter{n}.tex")
        if len(en) != len(pt):
            candidatos.append(
                f"ch{n}: {len(en)} parágrafos em inglês contra {len(pt)} em português; "
                "a comparação por posição não é fiável neste capítulo")
            continue
        for i, (a, b) in enumerate(zip(en, pt, strict=True), 1):
            ca, cb = contagens(a, RX_EN, EN), contagens(b, RX_PT, PT)
            comparados += 1
            # Só se compara onde os DOIS lados afirmam uma contagem e ela difere. Um lado ter
            # numeral e o outro não é idioma, e a forma dos dois defeitos reais foi os dois
            # lados afirmarem números diferentes.
            if not ca or not cb:
                idiomaticos += 1
                continue
            if ca != cb:
                candidatos.append(
                    f"ch{n}, parágrafo {i}: EN={ca} PT={cb}\n"
                    f"      EN: {a[:150]}\n"
                    f"      PT: {b[:150]}")

    print(f"{comparados} parágrafos comparados nos seis capítulos")
    print(f"{idiomaticos} com numeral só num dos lados: idioma, e por isso não verificados")
    print("(o numeral 1 e os ordinais ficam de fora por desenho)\n")
    if candidatos:
        print(f"CANDIDATOS A LEITURA HUMANA - {len(candidatos)}\n")
        for x in candidatos:
            print(f"  {x}\n")
        print("  Nao e' uma porta e sai a 0. A maioria destes sera gramatica e nao defeito;")
        print("  os dois defeitos reais de 2026-09-10 foram encontrados a ler.")
        return 0
    print("ok  as contagens batem em todos os parágrafos comparáveis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
