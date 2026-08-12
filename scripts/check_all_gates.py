"""Corre TODAS as portas de entrega e imprime um veredicto por linha.

Existe porque as portas estavam espalhadas por comandos soltos, e uma porta que só corre quando
alguém se lembra dela não é uma porta. Reúne o que já havia (`verify.sh` cobria testes e lint) com
as verificações que foram nascendo à medida que cada defeito apareceu.

⚠️ **O QUE ISTO NÃO COBRE**, e vale mais dizê-lo do que deixar a lista parecer exaustiva:
  - se uma referência RESOLVE mas aponta à secção errada (é leitura; ver `check_references.py`
    com `--all`, que agrupa por alvo para essa leitura ser rápida);
  - se uma frase caracteriza bem o facto que cita;
  - se os números são os *certos* — só verifica que são consistentes entre si e entre línguas.

USO
---
    python scripts/check_all_gates.py            # tudo
    python scripts/check_all_gates.py --rapido   # salta as compilações LaTeX (lentas)
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
PY = str(RAIZ / ".venv" / "Scripts" / "python.exe")
if not pathlib.Path(PY).exists():
    PY = sys.executable

RESULTADOS: list[tuple[str, bool, str]] = []


def porta(nome: str, ok: bool, detalhe: str = "") -> None:
    RESULTADOS.append((nome, ok, detalhe))
    print(f"  {'PASSA' if ok else 'FALHA':5s}  {nome:44s} {detalhe}")


def corre(cmd: list[str], cwd: pathlib.Path | None = None, timeout: int = 900):
    return subprocess.run(cmd, cwd=cwd or RAIZ, capture_output=True, text=True,
                          timeout=timeout, encoding="utf-8", errors="replace")


# ── 1. código ─────────────────────────────────────────────────────────────────
def gate_testes() -> None:
    r = corre([PY, "-m", "pytest", "-m", "not telegram and not sbert",
               "-p", "no:cacheprovider", "-q"])
    m = re.search(r"(\d+) passed", r.stdout + r.stderr)
    falhou = "failed" in r.stdout or "error" in r.stdout.lower()
    porta("testes", r.returncode == 0 and not falhou,
          f"{m.group(1) if m else '?'} passaram")


def gate_ruff() -> None:
    r = corre([PY, "-m", "ruff", "check", "."])
    porta("ruff", r.returncode == 0, "limpo" if r.returncode == 0 else r.stdout[-90:])


# ── 2. documentos ─────────────────────────────────────────────────────────────
DOCS = [("thesis", "main"), ("thesis-pt", "main"), ("paper", "main"),
        ("slides", "main"), ("slides", "main-pt"), ("slides/guia_estudo", "main")]


def gate_latex() -> None:
    for pasta, ficheiro in DOCS:
        d = RAIZ / pasta
        if not d.exists():
            continue
        r = corre(["latexmk", "-pdf", "-interaction=nonstopmode", f"{ficheiro}.tex"], cwd=d)
        log = (d / f"{ficheiro}.log")
        txt = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
        erros = len(re.findall(r"^! ", txt, re.M))
        indef = len(re.findall(r"(?:Reference|Citation) `[^']+' .*undefined", txt))
        ovf = [int(x) for x in re.findall(r"Overfull \\hbox \((\d+)\.", txt)]
        pior = max(ovf) if ovf else 0
        pdf = d / f"{ficheiro}.pdf"
        pp = "?"
        if pdf.exists():
            rp = corre(["pdfinfo", str(pdf)])
            mp = re.search(r"Pages:\s+(\d+)", rp.stdout)
            pp = mp.group(1) if mp else "?"
        ok = r.returncode == 0 and erros == 0 and indef == 0 and pior <= 15
        porta(f"{pasta}/{ficheiro}", ok,
              f"{pp} pp · {erros} erros · {indef} indefinidas · overfull máx {pior}pt")


# ── 3. paridade bilingue ──────────────────────────────────────────────────────
CAPS = [f"ch{i}/chapter{i}" for i in range(1, 7)] + ["appendices/appendixA"]


def _texto(base: str, cap: str) -> str:
    p = RAIZ / base / f"{cap}.tex"
    return re.sub(r"(?<!\\)%.*", "", p.read_text(encoding="utf-8")) if p.exists() else ""


def gate_estrutura() -> None:
    difs = 0
    for cap in CAPS:
        en, pt = _texto("thesis", cap), _texto("thesis-pt", cap)
        if not en or not pt:
            continue
        for _etiqueta, padrao in (("secções", r"\\section\{"), ("subsecções", r"\\subsection\{"),
                                 ("figuras", r"\\begin\{figure"), ("tabelas", r"\\begin\{table"),
                                 ("labels", r"\\label\{"), ("refs", r"\\(?:eq)?ref\{")):
            if len(re.findall(padrao, en)) != len(re.findall(padrao, pt)):
                difs += 1
    porta("paridade estrutural EN↔PT", difs == 0, f"{difs} assimetrias em {len(CAPS)} capítulos")


def gate_citacoes() -> None:
    r = corre([PY, "-X", "utf8", "scripts/check_bilingual_parity.py"])
    m = re.search(r"(\d+) candidato", r.stdout)
    porta("paridade de citações EN↔PT", r.returncode == 0 and m and m.group(1) == "0",
          f"{m.group(1) if m else '?'} candidatos a leitura")


def gate_referencias() -> None:
    for base in ("thesis", "thesis-pt"):
        r = corre([PY, "-X", "utf8", "scripts/check_references.py", base])
        mt = re.search(r"TIPO \(palavra vs alvo\): (\d+)", r.stdout)
        mr = re.search(r"(\d+) referências, (\d+) labels", r.stdout)
        ok = bool(mt) and mt.group(1) == "0"
        porta(f"referências {base}", ok,
              f"{mr.group(1) if mr else '?'} refs · {mr.group(2) if mr else '?'} labels · "
              f"{mt.group(1) if mt else '?'} tipos errados")


ABS = {"abstract": r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
       "outra": r"\\begin\{abstractotherlanguage\}(.*?)\\end\{abstractotherlanguage\}"}


def gate_resumos() -> None:
    def limpa(t: str) -> str:
        t = re.sub(r"%.*", "", t)
        t = re.sub(r"(\d)\{,\}(\d)", r"\1\2", t)
        t = re.sub(r"\\[a-zA-Z]+", " ", t)
        return " ".join(re.sub(r"[${}~\\]", "", t).split())

    def blocos(f: str) -> dict[str, str]:
        s = (RAIZ / f).read_text(encoding="utf-8")
        return {k: limpa(m.group(1)) for k, rx in ABS.items()
                if (m := re.search(rx, s, re.S))}

    en = blocos("thesis/frontmatter/frontmatter.tex")
    pt = blocos("thesis-pt/frontmatter/frontmatter.tex")
    igual_en = en.get("abstract") == pt.get("outra")
    igual_pt = en.get("outra") == pt.get("abstract")
    n = len(en.get("abstract", "").split())
    porta("resumos idênticos nas 4 cópias", igual_en and igual_pt,
          f"abstract EN {n} palavras (limite 200)")
    porta("abstract EN dentro do limite", n <= 200, f"{n}/200")


# ── 4. higiene ────────────────────────────────────────────────────────────────
def gate_cr() -> None:
    """A corrupção que já partiu a tese PT duas vezes: um `\\ref` escrito como byte CR."""
    mau = []
    for p in RAIZ.rglob("*.tex"):
        if "build" in p.parts or ".git" in p.parts:
            continue
        b = p.read_bytes()
        if b.count(b"\r") - b.count(b"\r\n"):
            mau.append(p.relative_to(RAIZ).as_posix())
    extra = f" {mau[:2]}" if mau else ""
    porta("sem bytes CR soltos em .tex", not mau, f"{len(mau)} ficheiros{extra}")


def gate_congelados() -> None:
    r = corre(["git", "status", "--porcelain", "models/", "data/"])
    porta("congelados intactos (models/, data/)", not r.stdout.strip(),
          "sem alterações" if not r.stdout.strip() else r.stdout.strip()[:60])


def gate_quizz() -> None:
    p = RAIZ / "quiz" / "index.html"
    if not p.exists():
        return
    s = p.read_text(encoding="utf-8")
    i, j = s.index("const BANCO = ["), s.index("\n];", s.index("const BANCO = ["))
    bruto = s[i + len("const BANCO ="):j + 2]
    # valida a forma sem executar JS: conta objectos e campos obrigatórios
    n = bruto.count("\n{b:")
    escolha = len(re.findall(r"t:\s*\"escolha\"", bruto))
    sem_ok = escolha - len(re.findall(r"\bok:\s*\d", bruto))
    porta("quizz bem formado", sem_ok == 0 and n > 0,
          f"{n} perguntas · {escolha} de escolha · {sem_ok} sem campo ok")


def gate_git() -> None:
    r = corre(["git", "status", "--porcelain"])
    n = len([x for x in r.stdout.splitlines() if x.strip()])
    porta("árvore de trabalho limpa", n == 0, f"{n} ficheiros por commitar")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rapido", action="store_true", help="salta as compilações LaTeX")
    args = ap.parse_args()

    print("\n═══ CÓDIGO ═══")
    gate_testes()
    gate_ruff()

    if not args.rapido:
        print("\n═══ DOCUMENTOS ═══")
        gate_latex()

    print("\n═══ PARIDADE E INTEGRIDADE ═══")
    gate_estrutura()
    gate_citacoes()
    gate_referencias()
    gate_resumos()

    print("\n═══ HIGIENE ═══")
    gate_cr()
    gate_congelados()
    gate_quizz()
    gate_git()

    maus = [n for n, ok, _ in RESULTADOS if not ok]
    print("\n" + "═" * 74)
    if maus:
        print(f"❌ {len(maus)} PORTA(S) EM FALHA: {', '.join(maus)}")
    else:
        print(f"✅ {len(RESULTADOS)} portas, todas verdes.")
    print("═" * 74)
    print("Não coberto: uma referência que resolve mas aponta ao sítio errado; se uma frase")
    print("caracteriza bem o facto que cita; se os números são os certos (só a consistência).")
    return 1 if maus else 0


if __name__ == "__main__":
    sys.exit(main())
