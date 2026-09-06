"""Os quatro exemplares do resumo dizem todos a mesma coisa?

Cada uma das duas árvores imprime **dois** resumos: o da sua língua e a tradução. São, ao
todo, quatro textos e apenas dois conteúdos — o resumo português tem de ser idêntico nas duas
árvores, e o abstract inglês também.

⚠️ PORQUE É QUE ISTO EXISTE, e é um defeito medido e não hipotético. A sessão 56 encontrou o
**resumo português a divergir entre as duas teses**: a cópia dentro da tese inglesa omitia o
resultado negativo da triagem em produção que a cópia portuguesa trazia. Um leitor português
lia um resumo diferente consoante o ficheiro que abrisse, **e nenhuma das duas falhava a
compilar** — é texto válido nos dois sítios.

Verifica ainda o limite de palavras do abstract, que o próprio template declara e que a
sessão 56 encontrou ultrapassado em 218 palavras contra 200.

⚠️ A contagem ignora comandos LaTeX. A sessão 64 pagou o inverso: uma primeira contagem deu
201 contra o limite de 200 e ia corrigir-se um resumo que estava certo, porque contava as
chavetas de um comando como palavras.

    python scripts/check_resumos.py
"""

from __future__ import annotations

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BS = chr(92)
RAIZ = pathlib.Path(__file__).resolve().parents[1]
ARVORES = ("tese-pt", "tese-eng")
LIMITE = 200

RX = {
    "própria": (re.escape(BS) + r"begin\{abstract\}(.*?)" + re.escape(BS) + r"end\{abstract\}"),
    "traduzida": (re.escape(BS) + r"begin\{abstractotherlanguage\}(.*?)"
                  + re.escape(BS) + r"end\{abstractotherlanguage\}"),
}


def texto(bruto: str) -> str:
    """Só as palavras: sem comentários e sem comandos."""
    s = re.sub("(?<![" + BS * 2 + "])%.*", " ", bruto)
    s = re.sub(re.escape(BS) + r"[a-zA-Z]+\*?(\[[^\]]*\])?", " ", s)
    return " ".join(s.replace("{", " ").replace("}", " ").split())


def main() -> int:
    lidos: dict[str, dict[str, str]] = {}
    for arv in ARVORES:
        f = RAIZ / arv / "frontmatter" / "frontmatter.tex"
        if not f.exists():
            print(f"ERRO: {arv}/frontmatter/frontmatter.tex não existe. Um verificador que "
                  "não vê o corpus tem de ser indistinguível de um que falha.")
            return 2
        s = f.read_text(encoding="utf-8", errors="replace")
        lidos[arv] = {}
        for papel, rx in RX.items():
            m = re.search(rx, s, re.S)
            if not m:
                print(f"ERRO: {arv} não tem o resumo «{papel}».")
                return 2
            lidos[arv][papel] = texto(m.group(1))

    falhas = 0
    # o resumo de cada língua aparece como «própria» numa árvore e «traduzida» na outra
    pares = [("resumo português", ("tese-pt", "própria"), ("tese-eng", "traduzida")),
             ("abstract inglês", ("tese-eng", "própria"), ("tese-pt", "traduzida"))]
    for nome, (a1, p1), (a2, p2) in pares:
        t1, t2 = lidos[a1][p1], lidos[a2][p2]
        if t1 == t2:
            print(f"  ok  {nome}: idêntico nas duas árvores ({len(t1.split())} palavras)")
        else:
            falhas += 1
            print(f"  !!  {nome}: DIVERGE entre {a1} e {a2}")
            # strict=False de propósito: os dois podem ter comprimentos diferentes, e é
            # justamente esse o caso que o `else` do ciclo reporta.
            for i, (x, y) in enumerate(zip(t1.split(), t2.split(), strict=False)):
                if x != y:
                    print(f"      1.ª diferença na palavra {i + 1}: "
                          f"{a1} diz «{x}», {a2} diz «{y}»")
                    break
            else:
                print(f"      um é mais longo: {len(t1.split())} contra {len(t2.split())} "
                      "palavras")

    # ⚠️ O LIMITE APLICA-SE AOS DOIS, e durante um tempo só o inglês era verificado. O modelo
    # oficial declara-o para «the abstract», e o brief da reescrita fixa-o para ambos; a
    # verificação de um só deixava o resumo português crescer sem nada disparar, e foi o que
    # aconteceu — passou a 201 palavras e o gate imprimia «ok» na mesma.
    for nome, (arv, papel) in (("abstract inglês", ("tese-eng", "própria")),
                               ("resumo português", ("tese-pt", "própria"))):
        n = len(lidos[arv][papel].split())
        if n <= LIMITE:
            print(f"  ok  {nome} dentro do limite: {n}/{LIMITE} palavras")
        else:
            falhas += 1
            print(f"  !!  {nome} acima do limite: {n}/{LIMITE} palavras")

    print()
    if falhas:
        print("FALHA: um leitor que abra a outra árvore lê um resumo diferente, e nenhuma "
              "das duas falha a compilar.")
        return 1
    print("Os quatro exemplares dizem o mesmo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
