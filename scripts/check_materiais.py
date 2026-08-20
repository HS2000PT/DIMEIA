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
T = RAIZ / "tese"

MATERIAIS = [T / "slides" / "main.tex", T / "guia" / "main.tex",
             T / "quiz" / "index.html", T / "GRAVACAO.md"]

PROSA = sorted(T.rglob("cap*/capitulo*.tex")) + [T / "apendices" / "apendiceA.tex",
                                                 T / "frontmatter" / "frontmatter.tex"]

RX_RESULTADO = re.compile(r"\d+\.\d{2}(?!\d)")


def limpa(t: str) -> str:
    """Fora o que nao e afirmacao: desenhos, estilos e blocos de codigo."""
    t = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", t, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S | re.I)
    t = re.sub(r"\\begin\{lstlisting\}.*?\\end\{lstlisting\}", " ", t, flags=re.S)
    t = re.sub(r"```.*?```", " ", t, flags=re.S)
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
