"""Comandos de LaTeX que foram comidos por um escape de shell.

⚠️ POR QUE E QUE ISTO EXISTE. Escrever LaTeX a partir de um heredoc ou de `python -c`
converte silenciosamente a barra invertida seguida de certas letras:

    \\textbf  ->  TAB + "extbf"       (\\t)
    \\ref     ->  CR  + "ef"          (\\r)
    \\newline ->  LF  + "ewline"      (\\n)
    \\emph    ->  BEL + "mph"?  nao, mas \\a e \\b e \\f e \\v tambem existem

O ficheiro continua a compilar A ZERO ERROS, porque `extbf{...}` e texto valido, e o PDF
entregue mostra ao leitor a cadeia "extbfesta amostra". Nenhum exit code o denuncia.
Aconteceu neste projecto pelo menos tres vezes, e uma delas chegou ao PDF final.

Este verificador procura os restos: um caracter de controlo seguido do que sobra de um
comando conhecido, e caracteres de controlo soltos em geral.

    python scripts/check_tex_escapes.py
"""

from __future__ import annotations

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]

# (caracter que o escape produz, o que resta do comando)
RESTOS = [
    ("\t", ["extbf", "extit", "extsc", "exttt", "extcite", "extwidth", "extsuperscript",
            "abhead", "abular", "able", "oprule", "op", "imes", "extcolor"]),
    ("\r", ["ef", "aggedright", "ule", "ightarrow", "owcolor"]),
    ("\n", ["ode", "ewline", "ewcommand", "umberline", "oindent", "ewpage"]),
    ("\x08", ["egin", "ottomrule", "f", "aselineskip"]),   # \b
    ("\x0c", ["rac", "ootnote", "igure", "ill"]),          # \f
    ("\x0b", ["space", "fill", "ec"]),                     # \v
    ("\x07", ["lign", "utocite", "ddlinespace", "rraybackslash"]),  # \a
]

ALVOS = ["tese-v2", "tese", "thesis", "thesis-pt", "paper"]


def main() -> int:
    achados: list[tuple[str, int, str]] = []
    controlo: list[tuple[str, int, str]] = []
    vistos = 0

    for base in ALVOS:
        d = RAIZ / base
        if not d.exists():
            continue
        for f in sorted(d.rglob("*.tex")):
            if "build" in f.parts:
                continue
            vistos += 1
            # Ler BYTES e descodificar a mao, em vez de read_text. Em modo de
            # texto o Python traduz mudancas de linha, e um CR solto (que e
            # exactamente o que o escape de \ref deixa para tras) chega ca
            # dentro ja convertido: o verificador ficava cego a metade dos
            # defeitos que existe para apanhar. Ver o teste de sabotagem.
            bruto = f.read_bytes().decode("utf-8", errors="replace")
            texto = bruto.replace("\r\n", "\n")
            rel = str(f.relative_to(RAIZ))
            for n, linha in enumerate(texto.split("\n"), 1):
                for ch, palavras in RESTOS:
                    for p in palavras:
                        if ch + p in linha:
                            achados.append((rel, n, f"{ch!r} + {p!r}  ->  era \\{p}"))
                # caracteres de controlo soltos que nao deviam existir num .tex
                for m in re.finditer(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", linha):
                    controlo.append((rel, n, f"caracter de controlo {hex(ord(m.group(0)))}"))

    print(f"{vistos} ficheiros .tex lidos")
    print(f"comandos comidos por um escape: {len(achados)}")
    for rel, n, o in achados:
        print(f"  !! {rel}:{n}  {o}")
    if controlo:
        print(f"caracteres de controlo soltos: {len(controlo)}")
        for rel, n, o in controlo[:20]:
            print(f"  !! {rel}:{n}  {o}")

    if achados or controlo:
        print("\nUm destes compila a zero erros e sai impresso no PDF. Corrigir com a "
              "ferramenta de edicao, nunca com heredoc.")
        return 1
    print("Nenhum. (Os TABs em linhas de comentario sao ignorados por desenho.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
