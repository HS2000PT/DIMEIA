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
    ("números contra a fonte", "check_tese_numeros.py"),
    ("escapes de LaTeX comidos", "check_tex_escapes.py"),
    ("apêndice: cada número onde diz estar", "check_apendice_xref.py"),
    ("materiais de estudo alinhados", "check_materiais.py"),
    ("flutuantes referenciados", "check_floats.py"),
]

PDFS = [
    ("tese", TESE / "main.pdf", TESE / "main.tex"),
    ("slides", TESE / "slides" / "main.pdf", TESE / "slides" / "main.tex"),
    ("guia", TESE / "guia" / "main.pdf", TESE / "guia" / "main.tex"),
]


def paginas(pdf: pathlib.Path) -> str:
    try:
        r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, timeout=120)
        m = re.search(r"Pages:\s*(\d+)", r.stdout.decode("utf-8", "replace"))
        return m.group(1) if m else "?"
    except (OSError, subprocess.SubprocessError):
        return "?"


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
        print(f"  ok  {nome}: {paginas(pdf)} páginas, mais recente do que a fonte")

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
    print("com o orientador, os agradecimentos, e rodar as credenciais. Está no CHECKLIST.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
