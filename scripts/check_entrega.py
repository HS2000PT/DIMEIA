"""A porta única: está pronto para entregar?

Corre tudo o que se pode verificar por máquina e diz, numa linha, o que falta. O que
sobrar depois disto é humano: a leitura final, a conversa com o orientador, e os cliques.

    python scripts/check_entrega.py

Sai com 0 quando tudo o que é verificável passa.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
TESE = RAIZ / "tese"

VERIFICADORES = [
    ("dissertação canónica tese-v2", "check_tese_v2.py"),
    ("números contra a fonte", "check_tese_numeros.py"),
    # O de cima verifica uma lista curada contra o ficheiro que a produz: garante que os que estão
    # na lista estão certos, e nada diz sobre os que não estão. Este faz o inverso, e é por isso
    # que os dois coexistem: varre o documento inteiro e exige que TODO o número afirmado tenha
    # origem, ou uma justificação escrita.
    ("todo o número tem origem", "auditar_numeros.py"),
    ("escapes de LaTeX comidos", "check_tex_escapes.py"),
    ("apêndice: cada número onde diz estar", "check_apendice_xref.py"),
    ("materiais de estudo alinhados", "check_materiais.py"),
    ("flutuantes referenciados", "check_floats.py"),
    ("escrita: PT-PT e um termo por conceito", "check_escrita.py"),
    # O guia de construção promete código verbatim. Sem esta porta a promessa vale o que valer
    # a memória de quem o escreveu, e o código muda: um excerto correcto hoje deixa de o ser.
    ("guia de construção: código verbatim", "check_guia_codigo.py"),
]

# ⚠️ A DISSERTAÇÃO A ENTREGAR É `tese-v2/`, e esta lista apontava para `tese/`. Corrigido a
# 2026-09-04. Os materiais de estudo — slides, guia, guia de construção — nunca foram movidos
# e continuam em `tese/`; a dissertação foi. Uma porta que confere o documento errado dá
# garantia falsa sobre o que vai ser entregue E grita por defeitos que não contam, que é a
# combinação que faz alguém deixar de a ler.
TESE_V2 = RAIZ / "tese-v2"

PDFS = [
    ("dissertação (canónica)", TESE_V2 / "main.pdf", TESE_V2 / "main.tex"),
    ("slides", TESE / "slides" / "main.pdf", TESE / "slides" / "main.tex"),
    ("guia", TESE / "guia" / "main.pdf", TESE / "guia" / "main.tex"),
    ("guia de construção", TESE / "guia_construir" / "main.pdf",
     TESE / "guia_construir" / "main.tex"),
]


def paginas(pdf: pathlib.Path) -> str:
    try:
        r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, timeout=120)
        m = re.search(r"Pages:\s*(\d+)", r.stdout.decode("utf-8", "replace"))
        return m.group(1) if m else "?"
    except (OSError, subprocess.SubprocessError):
        return "?"


def registo_sujo(log: pathlib.Path) -> list[str]:
    """Erros e referências por resolver no `.log` do LaTeX.

    Um PDF existir não quer dizer que esteja bem: o LaTeX escreve-o mesmo depois de erros, e o
    que sai para a página é lixo tipográfico que só se vê a olhar. As referências indefinidas
    são piores, porque saem como `??` e ninguém repara numa página cheia de texto.

    As faltas de tipo de letra não contam: são cosméticas e o template do ISEP produz três.
    """
    if not log.exists():
        return [f"registo de compilação em falta: {log.name}"]
    linhas = log.read_text(encoding="utf-8", errors="replace").splitlines()
    erros = [x.strip() for x in linhas if x.startswith("! ")]
    indefinidas = [x.strip() for x in linhas
                   if "undefined" in x.lower() and "Font shape" not in x]
    return erros + indefinidas


def main() -> int:
    falhas = 0

    print("=== os PDF existem e têm páginas ===")
    for nome, pdf, tex in PDFS:
        if not pdf.exists():
            print(f"  !!  {nome}: {pdf.name} NÃO EXISTE — compila antes de entregar")
            falhas += 1
            continue
        if tex.exists() and tex.stat().st_mtime > pdf.stat().st_mtime:
            print(f"  !!  {nome}: o .tex é MAIS RECENTE do que o .pdf — recompila")
            falhas += 1
            continue
        # ⚠️ E O REGISTO DE COMPILAÇÃO, que esta porta não olhava. O LaTeX **recupera** de quase
        # tudo: um `\ref` partido por um escape produz três erros, imprime lixo na página, e
        # **escreve o PDF na mesma**. A porta dizia "ok, 118 páginas" sobre um documento com
        # erros dentro. Apanhado a 2026-08-20, no próprio dia em que causei um.
        problemas = registo_sujo(pdf.with_suffix(".log"))
        if problemas:
            print(f"  !!  {nome}: {len(problemas)} problema(s) no registo de compilação")
            for x in problemas[:3]:
                print(f"        {x[:78]}")
            falhas += 1
            continue
        print(f"  ok  {nome}: {paginas(pdf)} páginas, compila limpo, mais recente do que a fonte")

    print("\n=== os verificadores ===")
    for descricao, script in VERIFICADORES:
        p = RAIZ / "scripts" / script
        if not p.exists():
            print(f"  !!  {descricao}: {script} não existe")
            falhas += 1
            continue
        r = subprocess.run([sys.executable, str(p)], capture_output=True, cwd=RAIZ, timeout=1800)
        if r.returncode == 0:
            print(f"  ok  {descricao}")
        else:
            print(f"  !!  {descricao}  ->  python scripts/{script}")
            falhas += 1

    print("\n=== marcadores de trabalho por acabar no que vai ser entregue ===")
    # ⚠️ SEM re.I, e é o ponto todo: em português "todo" é uma palavra corrente, e um
    # \bTODO\b insensível a maiúsculas acusa dezassete frases perfeitamente normais. É a
    # quinta vez que esta classe de falso positivo aparece neste projecto.
    padrao = re.compile(r"\[A definir\]|\bTODO\b|\bFIXME\b|\bXXX\b")
    achados = []
    for f in sorted(TESE.rglob("*.tex")):
        if "build" in f.parts:
            continue
        for n, linha in enumerate(f.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
            if linha.lstrip().startswith("%"):
                continue
            if padrao.search(linha):
                achados.append(f"{f.relative_to(RAIZ)}:{n}  {linha.strip()[:64]}")
    if achados:
        for x in achados:
            print(f"  !!  {x}")
        falhas += len(achados)
    else:
        print("  ok  nenhum")

    print("\n=== a data não muda sozinha ===")
    # ⚠️ Só fora de comentários: os dois ficheiros EXPLICAM em comentário porque é que o
    # \today saiu, e um verificador que lê comentários acusa a própria explicação.
    def sem_comentarios(p: pathlib.Path) -> str:
        return "\n".join(x for x in p.read_text(encoding="utf-8").split("\n")
                         if not x.lstrip().startswith("%"))

    main_tex = sem_comentarios(TESE / "main.tex")
    fm = sem_comentarios(TESE / "frontmatter" / "frontmatter.tex")
    if "\\today" in main_tex or "\\today" in fm:
        print("  !!  ainda há \\today: a data muda a cada compilação, e numa declaração "
              "assinada isso é pior do que na capa")
        falhas += 1
    else:
        print("  ok  fixada")

    print()
    if falhas:
        print(f"FALTA RESOLVER: {falhas}")
        return 1
    print("Tudo o que se verifica por máquina está feito.")
    print("O que sobra é humano: a leitura final, a redação da declaração de IA e a licença")
    print("com o orientador, os agradecimentos, e rodar as credenciais. "
          "Está no docs/planos/CHECKLIST.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
