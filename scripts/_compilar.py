"""Compila tese-pt e/ou tese-eng com latexmk e resume os erros que interessam.

Uso:
    python scripts\\_compilar.py            # as duas
    python scripts\\_compilar.py tese-pt    # so uma

Substitui `scripts/build_pdf.sh`, que aponta para `thesis/`, arvore que ja nao existe.
O que este script acrescenta e a leitura do .log: latexmk devolve 0 com avisos, e um
`Reference undefined` ou um `Citation undefined` passa despercebido num log de 3000 linhas.
"""
import pathlib
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # noqa: BLE001
    pass

RAIZ = pathlib.Path(__file__).resolve().parents[1]

# Os avisos que nao se toleram: uma referencia por resolver e um erro de conteudo, nao de estilo.
PADROES = [
    (r"Citation '([^']+)' on page .* undefined", "citação por resolver"),
    (r"Reference `([^']+)' on page .* undefined", "referência por resolver"),
    (r"There were undefined references", "há referências por resolver"),
    (r"^! (.+)$", "ERRO de LaTeX"),
    (r"Overfull \\hbox \((\d+\.\d+)pt too wide\)", "linha a transbordar"),
]


def compilar(arvore: str) -> int:
    pasta = RAIZ / arvore
    if not (pasta / "main.tex").exists():
        print(f"[{arvore}] sem main.tex — saltado")
        return 0
    print(f"=== {arvore} ===")
    r = subprocess.run(
        # NAO acrescentar `-halt-on-error=false`: nao e opcao do latexmk. Ele responde
        # «Bad options specified», devolve 10 e NAO COMPILA NADA -- e como o PDF antigo
        # continua no sitio, o relatorio diz «ok» sobre um ficheiro que ninguem gerou.
        ["latexmk", "-pdf", "-outdir=build", "-interaction=nonstopmode", "main.tex"],
        cwd=pasta, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    log = pasta / "build" / "main.log"
    texto = log.read_text(encoding="utf-8", errors="replace") if log.exists() else r.stdout

    achados: dict[str, list[str]] = {}
    for padrao, etiqueta in PADROES:
        for m in re.finditer(padrao, texto, re.M):
            achados.setdefault(etiqueta, []).append(m.group(0).strip())

    pdf = pasta / "build" / "main.pdf"
    # O numero de paginas e a defesa contra o modo de falha mais traicoeiro: latexmk devolve
    # um PDF valido mas truncado (por exemplo quando duas instancias escrevem no mesmo
    # `build/`), e um PDF de 270 KB onde deviam estar 2,5 MB passa despercebido.
    paginas = re.search(r"Output written on .*?\((\d+) pages?", texto)
    print(f"  latexmk devolveu {r.returncode}; "
          f"PDF: {'sim, ' + str(pdf.stat().st_size) + ' bytes' if pdf.exists() else 'NAO'}"
          f"{', ' + paginas.group(1) + ' paginas' if paginas else ''}")
    problemas = 0
    if r.returncode != 0:
        cauda = [x for x in (r.stdout or "").splitlines() if x.strip()][-15:]
        print("  ! latexmk nao devolveu 0; ultimas linhas:")
        for linha in cauda:
            print(f"      {linha[:150]}")
        problemas += 1
    for etiqueta, linhas in achados.items():
        unicas = sorted(set(linhas))
        # Linhas a transbordar sao ruido tipografico; conta-se, nao se lista.
        if etiqueta == "linha a transbordar":
            print(f"  . {etiqueta}: {len(linhas)} (não bloqueia)")
            continue
        problemas += len(unicas)
        print(f"  ! {etiqueta}: {len(unicas)}")
        for linha in unicas[:12]:
            print(f"      {linha[:150]}")
        if len(unicas) > 12:
            print(f"      ... (+{len(unicas) - 12})")
    if not problemas:
        print("  ok — sem citações nem referências por resolver, sem erros de LaTeX")
    return problemas


def main() -> int:
    arvores = sys.argv[1:] or ["tese-pt", "tese-eng"]
    total = sum(compilar(a) for a in arvores)
    print(f"\ntotal de problemas: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
