"""Cada número do artigo conferido contra a dissertação canónica e contra a evidência.

Porque é que isto existe, e é um defeito medido e não hipotético. A 2026-09-04 o
`paper/main.tex` estava tocado pela última vez a 13 de agosto, ou seja **antes** da
reescrita para `tese-v2`. Continha os valores antigos da recuperação e **não continha**
a estratégia trivial de `0,467` que leva a dissertação a abandonar o valor agregado em
favor da afirmação setor a setor. Submetido nesse estado, o artigo afirmaria o que a
dissertação declara não sustentar, e nada falhava: o LaTeX compilava, os testes passavam.

O verificador faz duas perguntas distintas:

1. **todo o número do artigo existe na dissertação?** Um número que só exista no artigo
   ou é novo (e então precisa de fonte própria) ou é resto de uma versão anterior;
2. **os resultados que a dissertação estreitou aparecem no artigo?** Uma afirmação
   retirada da tese que sobreviva no artigo é a pior das duas divergências, porque os
   dois documentos são lidos pelas mesmas pessoas.

    python scripts/check_artigo_numeros.py
"""

from __future__ import annotations

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
ARTIGO = RAIZ / "paper" / "main.tex"
TESE = RAIZ / "tese-pt"
FICHEIROS_TESE = [f"ch{i}/chapter{i}.tex" for i in range(1, 7)] + [
    "appendices/appendixA.tex", "frontmatter/frontmatter.tex"]

AVAL = RAIZ / "docs" / "evaluation"

# Números de COMPOSIÇÃO, que não são afirmações: larguras de figura e derivações que o
# próprio texto mostra. A lista é curta de propósito; tudo o resto tem de ter fonte.
COMPOSICAO = {
    0.95,   # largura de coluna em \includegraphics
    2.1,    # "about 2.1x the random base rate", derivado de 0.514/0.240 no proprio texto
}

# Resultados que a dissertação ESTREITOU. Se o artigo os afirmar sem a ressalva, é a
# divergência que mais custa. A ressalva é procurada como cadeia, não como número.
ESTREITADOS: list[tuple[str, str, str]] = [
    ("0.514", "0.467",
     "o agregado da recuperação: a tese abandona-o porque existe uma estratégia trivial "
     "que vale 0.467. O artigo tem de nomear essa estratégia."),
    ("0.632", "1.67",
     "a precisão dentro do orçamento: a tese diz 1.67x e não 'quase quatro vezes', "
     "porque o chão de acaso real é 0.379 e não 0.163."),
]


def valores(texto: str, *, ingles: bool) -> set[float]:
    """Todos os decimais do texto, por VALOR e não por cadeia.

    ⚠️ A CHAVETA {,} NÃO SIGNIFICA O MESMO NAS DUAS LÍNGUAS, e tratá-la de forma
    igual inventa divergências. No artigo, que é inglês, separa MILHARES e tem de
    desaparecer: 3{,}714 é 3714. Na tese, que é portuguesa, é a vírgula DECIMAL e
    passa a ponto: 0{,}514 é 0.514. A sessão 56 pagou este defeito no sentido
    inverso, com o 88,5 do português lido como 885.
    """
    texto = texto.replace("{,}", "" if ingles else ".")
    out: set[float] = set()
    for m in re.findall(r"\d+(?:\.\d+)?", texto):
        try:
            out.add(float(m))
        except ValueError:
            pass
    return out


def main() -> int:
    if not ARTIGO.exists():
        print("ERRO: paper/main.tex não existe. Um verificador que não vê o corpus "
              "tem de ser indistinguível de um que falha.")
        return 2

    art_txt = ARTIGO.read_text(encoding="utf-8", errors="replace")
    art_txt = re.sub(r"(?<!\\)%.*", " ", art_txt)
    tese_txt = "\n".join((TESE / f).read_text(encoding="utf-8", errors="replace")
                         for f in FICHEIROS_TESE if (TESE / f).exists())

    # só os decimais interessam: os inteiros são anos, contagens e coordenadas
    art_dec = {v for v in valores(art_txt, ingles=True) if v != int(v)}
    tese_dec = {v for v in valores(tese_txt, ingles=False) if v != int(v)}

    # Um número que o artigo tenha e a tese não NÃO é, por si só, um defeito: o artigo
    # pode reportar mais. O que é defeito é não ter fonte nenhuma. Por isso a segunda
    # pergunta é feita contra os artefactos de avaliação, e não contra a tese.
    so_no_artigo = sorted(v for v in art_dec - tese_dec if v not in COMPOSICAO)
    falhas: list[str] = []

    print(f"artigo: {len(art_dec)} decimais · tese canónica: {len(tese_dec)}")
    print()

    aval_txt = "\n".join(f.read_text(encoding="utf-8", errors="replace")
                         for f in sorted(AVAL.glob("*.md")))
    aval_dec = valores(aval_txt, ingles=True)

    sem_fonte = [v for v in so_no_artigo if v not in aval_dec]
    if sem_fonte:
        print(f"decimais do artigo SEM fonte em lado nenhum: {len(sem_fonte)}")
        for v in sem_fonte:
            print(f"   {v:g}")
        print("   Não estão na dissertação nem em docs/evaluation/. Ou são novos e "
              "precisam de gerador, ou são resto de uma versão anterior.")
        falhas.append(f"{len(sem_fonte)} decimais sem fonte")
    elif so_no_artigo:
        print(f"ok  {len(so_no_artigo)} decimais só no artigo, todos com fonte em "
              "docs/evaluation/")
        print("    " + ", ".join(f"{v:g}" for v in so_no_artigo))
    else:
        print("ok  todo o decimal do artigo existe também na dissertação canónica")

    print()
    for numero, ressalva, porque in ESTREITADOS:
        if numero not in art_txt.replace("{,}", ""):
            print(f"ok  o artigo não afirma {numero}")
            continue
        if ressalva in art_txt.replace("{,}", ""):
            print(f"ok  {numero} aparece com a ressalva de {ressalva}")
        else:
            print(f"!!  o artigo afirma {numero} SEM a ressalva de {ressalva}")
            print(f"    {porque}")
            falhas.append(f"{numero} sem ressalva")

    print()
    if falhas:
        print("FALHA: " + "; ".join(falhas))
        return 1
    print("O artigo está alinhado com a dissertação canónica.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
