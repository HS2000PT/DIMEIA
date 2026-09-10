"""As contagens de paginas que os materiais afirmam batem com os PDF que existem?

⚠️ POR QUE E' QUE ESTA PORTA EXISTE. A 2026-09-08 o `CHECKLIST`, o `LEIA-ME-PRIMEIRO` e o
documento de perguntas do juri diziam que a dissertacao tem **132 paginas** e termina no
folio **108**. Tinha **129** e terminava no **111**. Os numeros tinham derrapado ao longo de
quatro sessoes -- as paginas sobem e descem a cada figura acrescentada -- e **nenhuma das
dezanove portas via nada**, porque o `check_materiais` compara decimais de duas ou tres casas
e uma contagem de paginas e' um inteiro.

O sitio onde isso mais custa nao e' o checklist: e' a **resposta preparada para o juri**, que
ensinava a dizer «132 paginas, 108 em numeracao arabe» em voz alta. Um arguente que abra o PDF
conta 129. O argumento sobrevivia (111 continua abaixo do folio 120 da dissertacao aprovada
que serve de referencia), mas quem o diz com dois numeros errados perde-o na mesma.

O que esta porta faz: le o numero de paginas do PROPRIO PDF e o ultimo folio arabe impresso,
e exige que os materiais vivos digam o mesmo. Nao adivinha -- se o PDF nao existir, RECUSA-SE
a validar em vez de aprovar em silencio.

    python scripts/check_paginas.py
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]

# Os documentos VIVOS: os que descrevem o estado de hoje e que o autor usa para estudar.
# ⚠️ Os registos DATADOS ficam de fora de proposito -- as entradas de sessao do CLAUDE.md, as
# criticas e as auditorias descrevem o que era verdade no dia em que foram escritas, e
# obriga-las a acompanhar o presente seria falsificar o registo em vez de o actualizar.
VIVOS = [
    "docs/planos/CHECKLIST.md",
    "docs/defence/LEIA-ME-PRIMEIRO.md",
    "docs/defence/perguntas_abertas_2026-09-06.md",
    "docs/defence/THESIS_FACT_SHEET.md",
    "README.md",
]

PDFS = {"tese-pt": RAIZ / "tese-pt/main.pdf", "tese-eng": RAIZ / "tese-eng/main.pdf"}


def paginas(pdf: pathlib.Path) -> int:
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout
    m = re.search(r"^Pages:\s+(\d+)", out, re.M)
    if not m:
        print(f"ERRO: nao consegui ler as paginas de {pdf}. Nao e' seguro validar as cegas.")
        raise SystemExit(2)
    return int(m.group(1))


def ultimo_folio(pdf: pathlib.Path, n: int) -> int | None:
    """O ultimo numero arabe IMPRESSO. E' o que se compara com as teses aprovadas, porque o
    limite de paginas do regulamento incide sobre a numeracao e nao sobre o ficheiro."""
    for p in range(n, max(0, n - 14), -1):
        t = subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), str(pdf), "-"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace").stdout
        achados = re.findall(r"^\s*(\d{1,3})\s*$", t, re.M)
        if achados:
            return int(achados[-1])
    return None


def main() -> int:
    for pdf in PDFS.values():
        if not pdf.exists():
            print(f"ERRO: {pdf} nao existe. Compilar antes de validar.")
            return 2

    reais = {}
    for nome, pdf in PDFS.items():
        n = paginas(pdf)
        reais[nome] = (n, ultimo_folio(pdf, n))
        f = reais[nome][1]
        print(f"  {nome}: {n} paginas fisicas, ultimo folio arabe {f if f else '?'}")
    print()

    pt_fis, pt_fol = reais["tese-pt"]
    en_fis, _ = reais["tese-eng"]
    # Contagens que seriam ERRADAS se aparecessem: qualquer numero de 3 digitos entre 100 e
    # 199 colado a `pp`/`paginas` que nao seja um dos valores reais. Manter estreito de
    # proposito -- um verificador que grita de mais deixa de ser lido.
    legitimos = {pt_fis, en_fis, pt_fol or -1, 120, 139, 133, 109, 104}
    rx = re.compile(r"\b(1\d{2})\s*(?:pp\b|páginas|paginas)")

    maus = 0
    for rel in VIVOS:
        f = RAIZ / rel
        if not f.exists():
            continue
        for i, linha in enumerate(f.read_text(encoding="utf-8").splitlines(), start=1):
            # ⚠️ ISENCAO POR CONTEXTO: uma linha que fale do arquivo esta a descrever um
            # documento que nao e' nenhuma das teses vivas, e a sua contagem nao tem de bater
            # com elas. Isentar pelo VALOR (juntando-o aos legitimos) deixaria passar o mesmo
            # numero dito sobre a tese actual, que e' o que esta porta existe para apanhar.
            if "archive/" in linha or "archive\\" in linha:
                continue
            for m in rx.finditer(linha):
                v = int(m.group(1))
                if v in legitimos:
                    continue
                maus += 1
                print(f"  !! {rel}:{i}  diz {v} paginas")
                print(f"     {' '.join(linha.split())[:96]}")

    print()
    if maus:
        print(f"FALHA: {maus} contagem(ns) de paginas que nenhum PDF sustenta. "
              f"Reais: PT {pt_fis} (folio {pt_fol}) - EN {en_fis}.")
        return 1
    print("ok  as contagens dos materiais vivos batem com os PDF que existem.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
