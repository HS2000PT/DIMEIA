"""Um rótulo desenhado que seja idêntico nas duas árvores não foi traduzido.

Porque é que isto existe. O `check_figuras_lingua.py` pergunta se uma figura mistura as
duas línguas *dentro de si*, e responde comparando o texto contra vocabulário. Isso deixa
sempre uma fresta: uma figura cujo interior está *todo* na língua errada é monolingue, e
uma expressão que não conste de nenhuma lista é invisível. Foi assim que `promotion gate`
e `does not win: log and discard` atravessaram o verificador a 2026-09-05, numa figura
portuguesa, e que `somam` ficou desenhado dentro da tese inglesa.

Esta verificação não sabe vocabulário nenhum e por isso não tem essa fresta. Existem duas
árvores que são traduções uma da outra: se o mesmo texto desenhado aparece nas duas, ou é
um nome próprio, ou é um número, ou é material citado — ou escapou à tradução. Tudo o que
não caiba nas três primeiras hipóteses é reportado, e a lista de exceções está aqui em
baixo, onde se lê, em vez de estar implícita no silêncio do verificador.

⚠️ A direção da lista importa. A do `check_figuras_lingua` é de *acusação* e por isso
fechá-la cega o verificador; esta é de *isenção*, logo um rótulo novo que ninguém previu
faz a verificação falhar em vez de passar. É a diferença entre um guarda que só conhece o
que já viu e um que exige explicação para o que não conhece.

    python scripts/check_figuras_paridade.py
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

RX_COM = re.compile("(?<![" + BS * 2 + "])%.*")
RX_CAP = re.compile(re.escape(BS) + r"caption(\[[^\]]*\])?\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
RX_NODE = re.compile(re.escape(BS) + r"node\s*(?:\[[^\]]*\])?\s*(?:\([^)]*\))?\s*"
                     r"(?:at\s*\([^)]*\))?\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")
RX_EIXO = re.compile(r"(?:xlabel|ylabel|xticklabels|yticklabels|legend|legend entries"
                     r"|title)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")

# As três hipóteses legítimas para um rótulo ser igual nas duas línguas.
ISENTOS = {
    # nomes próprios, siglas e notação que não se traduzem
    "ROC-AUC", "PR-AUC", "$F_1$", "$0" + BS + "%$",
    BS + "gls{PRAUC}", BS + "gls{LIME}, " + BS + "gls{SHAP}",
    # termo latino corrente nas duas línguas da área
    "embargo",
    # argumentos de macro em ciclos \foreach: não são texto desenhado, são substituídos
    BS + "i", BS + "nome", BS + "quota", BS + "valor", BS + "xrot", BS + "xtk",
    BS + "x", BS + "xcus", BS + "xfut", BS + "xlim",
    # ⚠️ Os quatro acima vieram dos decks, que entraram nesta porta a 2026-09-06. O
    # `NVDA` é um ticker e `VALID.` é a abreviatura de validação, que se escreve igual
    # nas duas línguas: traduzi-las seria inventar uma diferença que não existe.
    "NVDA", "VALID.",
}


def rotulos(arvore: str) -> set[str]:
    fora: set[str] = set()
    base = RAIZ / arvore
    fich = [base / f"ch{i}/chapter{i}.tex" for i in range(1, 7)]
    fich += [base / "appendices/appendixA.tex"]
    # ⚠️ OS DECKS TAMBEM. O deck ingles nasceu a 2026-09-06 com os exemplos do
    # trocadilho ainda em portugues, e nenhuma porta os via: as figuras do Beamer sao
    # `tikzpicture` dentro de `frame`, e nao ambientes `figure`.
    fich += [base / "slides/main.tex"]
    if not any(f.exists() for f in fich):
        print(f"ERRO: nenhum capítulo encontrado em '{arvore}'. Um verificador que não vê "
              "o corpus tem de ser indistinguível de um que falha.")
        raise SystemExit(2)
    for f in fich:
        if not f.exists():
            continue
        # a legenda é prosa do documento e está traduzida por outra via: sai daqui
        txt = RX_CAP.sub("", RX_COM.sub("", f.read_text(encoding="utf-8", errors="replace")))
        for rx in (RX_NODE, RX_EIXO):
            for m in rx.finditer(txt):
                v = " ".join(m.group(1).split())
                # números, pontuação pura e imagens não têm língua. Os logótipos das
                # tecnologias são nós cujo conteúdo é só um \includegraphics: são a
                # mesma imagem nas duas árvores por serem a mesma marca.
                if v.startswith(BS + "includegraphics"):
                    continue
                if v and not re.fullmatch(r"[\d.,\s$%+\-{}]*", v):
                    fora.add(v)
    return fora


def main() -> int:
    pt, en = (rotulos(a) for a in ARVORES)
    comuns = sorted((pt & en) - ISENTOS)
    print(f"{len(pt)} rótulos PT · {len(en)} EN · {len(comuns)} iguais sem explicação")
    if not comuns:
        print("ok  todo o texto desenhado difere entre as árvores, salvo as isenções "
              "declaradas.")
        return 0
    print()
    for c in comuns:
        print(f"  ⚠ {c[:96]}")
    print()
    print("FALHA: um rótulo idêntico nas duas árvores não foi traduzido, ou é uma isenção "
          "legítima que falta declarar em ISENTOS — com a razão escrita ao lado.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
