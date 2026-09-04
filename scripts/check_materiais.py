"""Os materiais que o aluno estuda dizem o mesmo que a tese?

O juri ve mais do que a dissertacao: ve os slides, e o aluno estuda pelo guia e pelo quizz.
Se um deles ensinar um numero que a tese corrigiu, ele decora o errado e a contradicao
aparece em directo. Ja aconteceu neste projecto: um documento de defesa mandava decorar um
valor que tinha sido retirado.

Verifica tres coisas de uma vez, sobre tese/:
  1. cada decimal de resultado dos materiais existe tambem na tese
  2. zero travessoes em prosa (a regra de escrita deste trabalho)
  3. zero decimais escritos com virgula (a tese usa ponto, incluindo em modo matematico)

So se comparam decimais com DUAS casas: sao os resultados. Coordenadas de desenho, anos,
versoes e valores de CSS nao sao afirmacoes.

    python scripts/check_materiais.py
"""

from __future__ import annotations

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]

# ⚠️ A ÁRVORE A VERIFICAR VEM POR ARGUMENTO, E O PADRÃO É A CANÓNICA. Corrigido a 2026-09-04.
#
# Este verificador apontava para `tese/`, que foi SUPERSEDA por `tese-v2/`. Continuava a passar
# ou a falhar sobre um documento que já não é entregue — ou seja, gritava por defeitos que não
# contam e ficava cego aos que contam. É a mesma classe que a sessão 58 encontrou no
# `check_references`, que só conhecia os nomes ingleses e imprimia «0 referências» como se
# fosse um estado saudável.
BASE = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "tese-v2"
T = RAIZ / BASE

# ⚠️ DUAS ÁRVORES, E É DE PROPÓSITO. A prosa a verificar é a da dissertação CANÓNICA
# (`tese-v2/`), mas os materiais de estudo — slides, guia, quizz, guião de gravação — nunca
# foram movidos e continuam em `tese/`. Apontar as duas ao mesmo sítio faria uma delas ser
# lida a partir de um caminho que não existe, e o relatório dizia «(ausente)» para tudo, que
# se lê como «não há nada a verificar» e é «não olhei para nada».
MATERIAIS_RAIZ = RAIZ / "tese"
MATERIAIS = [MATERIAIS_RAIZ / "slides" / "main.tex", MATERIAIS_RAIZ / "guia" / "main.tex",
             MATERIAIS_RAIZ / "quiz" / "index.html", MATERIAIS_RAIZ / "GRAVACAO.md"]

if (T / "ch1").is_dir():          # árvore nova: ch1/chapter1.tex
    PROSA = ([T / "frontmatter" / "frontmatter.tex"]
             + [T / f"ch{i}" / f"chapter{i}.tex" for i in range(1, 7)]
             + [T / "appendices" / "appendixA.tex", T / "appendices" / "appendixB.tex"])
else:                            # árvore antiga: cap5/capitulo5.tex
    PROSA = sorted(T.rglob("cap*/capitulo*.tex")) + [T / "apendices" / "apendiceA.tex",
                                                     T / "frontmatter" / "frontmatter.tex"]
PROSA = [p for p in PROSA if p.exists()]

RX_RESULTADO = re.compile(r"\d+\.\d{2}(?!\d)")


def limpa(t: str) -> str:
    """Fora o que nao e afirmacao: desenhos, estilos e blocos de codigo."""
    t = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", t, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", " ", t, flags=re.S)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
    # ⚠️ MEDIDAS DE COMPOSICAO NAO SAO RESULTADOS. Um "0.62" em `egin{column}{0.62	extwidth}`
    # ou em `height=0.78	extheight` e uma fraccao da pagina, nao um numero que a tese afirme.
    # Sem isto o verificador acusava cinco larguras de coluna como afirmacoes sem fonte, e um
    # verificador que grita de mais deixa de ser lido -- este projecto ja pagou isso cinco vezes.
    t = re.sub(r"\d+\.\d+\s*\\(?:text|line|column|page)(?:width|height)", " ", t)
    # ⚠️ UM COMENTARIO NAO E UMA AFIRMACAO, e este verificador acusava-os. Corrigido a
    # 2026-09-04: uma nota de composicao («2mm punha a caixa 0.52pt acima do slide») era
    # reportada como um numero que os materiais dizem e a tese nao. E a MESMA classe das
    # larguras de coluna acima, uma linha antes, na mesma funcao.
    #
    # O `%` tem de NAO estar escapado: `\\%` e o sinal de percentagem e aparece
    # dentro dos proprios numeros que interessa verificar, como `$0.41\\%$`.
    # Apagar por ai cegava o verificador exactamente onde ele serve.
    t = re.sub(r"(?<!\\)%.*", " ", t)
    return t


def main() -> int:
    corpo = [p for p in PROSA if p.exists()]
    if not corpo:
        print("ERRO: nao encontrei o corpo da tese. Um verificador que nao ve corpus tem de "
              "ser indistinguivel de um que falha.")
        return 2

    tese = "\n".join(p.read_text(encoding="utf-8") for p in corpo).replace("{,}", ".")
    tese_n = set(RX_RESULTADO.findall(tese))

    falhas = 0

    print(f"tese: {len(corpo)} ficheiros, {len(tese_n)} decimais de resultado")
    for p in MATERIAIS:
        if not p.exists():
            print(f"  (ausente) {p.parent.name}/{p.name}")
            continue
        t = limpa(p.read_text(encoding="utf-8", errors="replace"))
        n = set(RX_RESULTADO.findall(t))
        fora = sorted(n - tese_n)
        marca = "ok  " if not fora else "!!  "
        print(f"  {marca}{p.parent.name}/{p.name}: {len(n)} decimais, {len(fora)} sem par na tese")
        for x in fora:
            m = re.search(r".{0,58}" + re.escape(x) + r".{0,38}", t)
            ctx = re.sub(r"\s+", " ", m.group(0)) if m else ""
            print(f"        {x}  ...{ctx}")
        falhas += len(fora)

    # travessoes em prosa e decimais com virgula, na tese e nos materiais
    # ⚠️ As duas regras correm sobre o texto LIMPO, e nao sobre as linhas em bruto. Sem isso
    # o verificador acusava as coordenadas de TikZ `(3.9,0)` de serem decimais com virgula, e
    # as barras `---` do Markdown de serem travessoes. Um verificador que grita de mais deixa
    # de ser lido, e este projecto ja pagou isso mais do que uma vez.
    travessoes, virgulas = [], []
    for p in corpo + [x for x in MATERIAIS if x.exists()]:
        md = p.suffix.lower() == ".md"
        texto = limpa(p.read_text(encoding="utf-8", errors="replace"))
        for n, linha in enumerate(texto.split("\n"), 1):
            if linha.lstrip().startswith("%"):
                continue
            # travessao a serio: entre palavras. Em Markdown, `---` sozinho e uma barra
            # horizontal e `|---|` e uma tabela: nenhum dos dois e travessao.
            barra = md and linha.lstrip().startswith(("|", "-"))
            if re.search(r"\w\s*---\s*\w", linha) and not barra:
                travessoes.append(f"{p.name}:{n}  {linha.strip()[:60]}")
            if re.search(r"\$[^$]*\d,\d[^$]*\$", linha):
                virgulas.append(f"{p.name}:{n}  {linha.strip()[:60]}")

    print(f"  {'ok  ' if not travessoes else '!!  '}travessoes em prosa: {len(travessoes)}")
    for x in travessoes[:8]:
        print(f"        {x}")
    print(f"  {'ok  ' if not virgulas else '!!  '}decimais com virgula: {len(virgulas)}")
    for x in virgulas[:8]:
        print(f"        {x}")

    falhas += len(travessoes) + len(virgulas)
    if falhas:
        print("\nUm numero que o aluno estuda e a tese nao diz e um numero que ele vai citar "
              "sem o poder mostrar.")
        return 1
    print("\nTudo bate certo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
