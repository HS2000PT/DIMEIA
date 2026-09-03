"""Porta de qualidade da dissertação canónica em ``tese-v2/``.

Ao contrário das portas históricas, esta lê a árvore que vai ser entregue e considera todas as
fontes e figuras, não apenas ``main.tex``, ao decidir se o PDF precisa de ser recompilado.

    python scripts/check_tese_v2.py

Sai com zero apenas quando o PDF existe, está atualizado, o registo final está limpo, todo o
corpus esperado foi realmente inspecionado e não restam marcadores de preenchimento.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(__file__).resolve().parents[1]
TESE = REPO / "tese-v2"
PDF = TESE / "main.pdf"
LOG = TESE / "main.log"
AUX = TESE / "main.aux"
FLS = TESE / "main.fls"
EXTENSOES_FONTE = {".tex", ".bib", ".cls", ".sty", ".cfg", ".png", ".jpg", ".jpeg", ".pdf"}
LIMITE_OVERFULL_PT = 15.0

CORPUS = [
    TESE / "main.tex",
    TESE / "frontmatter" / "frontmatter.tex",
    TESE / "frontmatter" / "glossary.tex",
    *[TESE / f"ch{i}" / f"chapter{i}.tex" for i in range(1, 7)],
    TESE / "ch5" / "feedback_auto.tex",
    TESE / "appendices" / "appendixA.tex",
    TESE / "appendices" / "appendixB.tex",
]


def _sem_comentario(linha: str) -> str:
    """Retira o comentário LaTeX iniciado por um ``%`` não escapado."""
    for i, char in enumerate(linha):
        if char != "%":
            continue
        barras = 0
        j = i - 1
        while j >= 0 and linha[j] == "\\":
            barras += 1
            j -= 1
        if barras % 2 == 0:
            return linha[:i]
    return linha


def _fontes() -> list[pathlib.Path]:
    fontes = {
        p for p in TESE.rglob("*")
        if p.is_file() and p != PDF and p.suffix.lower() in EXTENSOES_FONTE
        and "build" not in p.parts
    }
    # ``latexmkrc`` não tem extensão, mas altera a forma como o PDF canónico é produzido.
    # Tem, por isso, de invalidar um PDF mais antigo tal como qualquer fonte LaTeX.
    configuracao = TESE / "latexmkrc"
    if configuracao.exists():
        fontes.add(configuracao)
    return sorted(fontes)


def _paginas() -> int | None:
    try:
        resultado = subprocess.run(
            ["pdfinfo", str(PDF)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    achado = re.search(r"^Pages:\s*(\d+)", resultado.stdout, re.MULTILINE)
    return int(achado.group(1)) if resultado.returncode == 0 and achado else None


def _problemas_log() -> list[str]:
    if not LOG.exists():
        return ["main.log não existe"]
    texto = LOG.read_text(encoding="utf-8", errors="replace")
    linhas = texto.splitlines()
    problemas = [linha.strip() for linha in linhas if linha.startswith("! ")]
    sinais = (
        "There were undefined references",
        "There were undefined citations",
        "multiply defined",
        "Citation '",
        "Reference '",
        "Float too large",
        "Overfull \\vbox",
        "Please (re)run Biber",
    )
    problemas.extend(linha.strip() for linha in linhas if any(sinal in linha for sinal in sinais))
    for achado in re.finditer(r"Overfull \\hbox \(([0-9.]+)pt too wide\)", texto):
        largura = float(achado.group(1))
        if largura > LIMITE_OVERFULL_PT:
            problemas.append(f"Overfull \\hbox de {largura:.2f} pt")
    return list(dict.fromkeys(problemas))


def _entradas_fls() -> set[str] | None:
    if not FLS.exists():
        return None
    entradas: set[str] = set()
    for linha in FLS.read_text(encoding="utf-8", errors="replace").splitlines():
        if not linha.startswith("INPUT "):
            continue
        caminho = linha[6:].strip().replace("\\", "/")
        while caminho.startswith("./"):
            caminho = caminho[2:]
        entradas.add(caminho.casefold())
    return entradas


def _paginas_antes_dos_apendices() -> int | None:
    if not AUX.exists():
        return None
    texto = AUX.read_text(encoding="utf-8", errors="replace")
    achado = re.search(r"\\newlabel\{ap:reprodutibilidade\}\{\{A\}\{(\d+)\}", texto)
    return int(achado.group(1)) - 1 if achado else None


def _executar_verificador(script: str, *args: str) -> tuple[bool, str]:
    resultado = subprocess.run(
        [sys.executable, str(REPO / "scripts" / script), *args],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300,
    )
    ultima = next((x for x in reversed(resultado.stdout.splitlines()) if x.strip()), "sem saída")
    return resultado.returncode == 0, ultima.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--permitir-pendencias-humanas",
        action="store_true",
        help="não falhar por nomes do júri ainda por preencher (útil na compilação contínua)",
    )
    args = parser.parse_args()
    falhas: list[str] = []

    ausentes = [p for p in CORPUS if not p.exists()]
    if ausentes:
        falhas.extend(f"corpus ausente: {p.relative_to(REPO)}" for p in ausentes)
    else:
        print(f"ok  corpus completo: {len(CORPUS)} ficheiros estruturais")

    if not PDF.exists():
        falhas.append("tese-v2/main.pdf não existe")
    else:
        fontes = _fontes()
        recentes = [p for p in fontes if p.stat().st_mtime > PDF.stat().st_mtime]
        if recentes:
            falhas.append(
                "PDF anterior a: " + ", ".join(str(p.relative_to(TESE)) for p in recentes[:5])
            )
        else:
            print(f"ok  PDF posterior às {len(fontes)} fontes e figuras")
        paginas = _paginas()
        if paginas is None:
            falhas.append("pdfinfo não conseguiu ler tese-v2/main.pdf")
        elif paginas == 0:
            falhas.append("o PDF tem zero páginas")
        else:
            print(f"ok  PDF legível: {paginas} páginas físicas")

    problemas_log = _problemas_log()
    if problemas_log:
        falhas.extend(f"log: {problema}" for problema in problemas_log)
    else:
        print("ok  registo final sem erros, referências indefinidas ou avisos graves")

    entradas = _entradas_fls()
    if entradas is None:
        falhas.append("main.fls não existe; compilar com -recorder")
    else:
        em_falta = []
        for ficheiro in CORPUS:
            relativo = ficheiro.relative_to(TESE).as_posix().casefold()
            if relativo not in entradas:
                em_falta.append(relativo)
        if em_falta:
            falhas.append("fontes não lidas pela compilação: " + ", ".join(em_falta))
        else:
            print(f"ok  main.fls confirma as {len(CORPUS)} fontes estruturais")

    paginas_contadas = _paginas_antes_dos_apendices()
    if paginas_contadas is None:
        falhas.append("não consegui obter o início do Apêndice A em main.aux")
    elif paginas_contadas > 120:
        falhas.append(f"limite oficial excedido: {paginas_contadas} páginas antes dos apêndices")
    else:
        print(f"ok  limite oficial: {paginas_contadas} de 120 páginas antes dos apêndices")

    marcadores: list[str] = []
    padrao = re.compile(
        r"\[A definir\]|\[Nome do (?:Presidente|Vogal)[^]]*\]|\bTODO\b|\bFIXME\b|\bXXX\b"
    )
    for ficheiro in sorted(TESE.rglob("*.tex")):
        linhas = ficheiro.read_text(encoding="utf-8", errors="replace").splitlines()
        for numero, linha in enumerate(linhas, 1):
            ativa = _sem_comentario(linha)
            if padrao.search(ativa) or "\\today" in ativa:
                marcadores.append(f"{ficheiro.relative_to(REPO)}:{numero}")
    if marcadores:
        mensagem = "preenchimento por fechar: " + ", ".join(marcadores)
        if args.permitir_pendencias_humanas:
            print(f"aviso  {mensagem}")
        else:
            falhas.append(mensagem)
    else:
        print("ok  sem marcadores de preenchimento e sem \\today")

    capitulo5 = (TESE / "ch5" / "chapter5.tex").read_text(encoding="utf-8", errors="replace")
    feedback = TESE / "ch5" / "feedback_auto.tex"
    if capitulo5.count(r"\input{ch5/feedback_auto}") != 1:
        falhas.append("ch5 não inclui feedback_auto.tex exatamente uma vez")
    elif not feedback.exists() or not feedback.read_text(encoding="utf-8").startswith("% GERADO"):
        falhas.append("feedback_auto.tex ausente ou não reconhecido como gerado")
    else:
        print("ok  fragmento de feedback gerado e incluído uma vez")

    for descricao, script, args in (
        ("referências e flutuantes", "check_references.py", ("tese-v2",)),
        ("escrita PT-PT", "check_escrita.py", ("tese-v2",)),
        ("flutuantes", "check_floats.py", ("tese-v2",)),
        ("escapes LaTeX", "check_tex_escapes.py", ()),
    ):
        passou, detalhe = _executar_verificador(script, *args)
        if passou:
            print(f"ok  {descricao}: {detalhe}")
        else:
            falhas.append(f"{descricao}: executar python scripts/{script} {' '.join(args)}")

    if falhas:
        print("\nFALTA RESOLVER:")
        for falha in falhas:
            print(f"  !! {falha}")
        return 1
    print("\nA dissertação canónica passou todas as verificações automáticas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
