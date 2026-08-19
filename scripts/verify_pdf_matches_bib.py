"""Cada PDF arquivado e mesmo o artigo que a chave declara?

Um DOI valido no .bib nao garante que o PDF que esta na pasta seja esse artigo. Este
verificador le a primeira pagina de cada PDF e compara o titulo com o do .bib.

    python scripts/verify_pdf_matches_bib.py
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

# A consola do Windows e cp1252: imprimir um simbolo mata o verificador a MEIO do
# relatorio, e um relatorio truncado le-se como um relatorio limpo.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
BIB = RAIZ / "thesis" / "references.bib"
PDFS = RAIZ / "docs" / "decisions" / "citation_pdfs"


def limpa(s: str) -> str:
    s = re.sub(r"\\[`'^\"~=.]\{?(\w)\}?", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def titulo_do_bib() -> dict[str, str]:
    bib = BIB.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", bib, re.S):
        chave, corpo = m.group(2).strip(), m.group(3)
        t = re.search(r"title\s*=\s*[{\"](.*?)[}\"]\s*(?:,|\n|$)", corpo, re.S)
        if t:
            out[chave] = re.sub(r"\s+", " ", t.group(1)).strip()
    return out


def apelidos_do_bib() -> dict[str, list[str]]:
    """Primeiros apelidos de cada entrada.

    ⚠️ Sem isto o verificador aceita QUALQUER documento cujo titulo contenha as palavras certas.
    Apanhou-se assim uma tese de mestrado de 2003 posta no lugar do artigo do Bollerslev de 1986:
    o titulo dela contem "Generalized Autoregressive Conditional Heteroscedastic" e passava a
    100%. O nome do autor e o que distingue o artigo de um trabalho SOBRE o artigo.
    """
    bib = BIB.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", bib, re.S):
        chave, corpo = m.group(2).strip(), m.group(3)
        a = re.search(r"author\s*=\s*[{\"](.*?)[}\"]\s*(?:,\s*\n|\n\s*\w+\s*=)", corpo, re.S)
        if not a:
            continue
        apelidos = []
        for autor in a.group(1).split(" and "):
            autor = limpa(autor)
            if not autor:
                continue
            # "Apelido, Nome" ou "Nome Apelido"
            apelidos.append(autor.split()[0] if "," in a.group(1) else autor.split()[-1])
        out[chave] = [x for x in apelidos if len(x) > 3][:4]
    return out


def texto_inicio(pdf: pathlib.Path, paginas: int = 2) -> str:
    r = subprocess.run(["pdftotext", "-enc", "UTF-8", "-f", "1", "-l", str(paginas),
                        str(pdf), "-"], capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def main() -> int:
    titulos = titulo_do_bib()
    apelidos = apelidos_do_bib()
    pdfs = sorted(PDFS.glob("*.pdf"))
    if not pdfs:
        print("Nenhum PDF em", PDFS)
        return 2

    bons, suspeitos, sem_bib = [], [], []
    for p in pdfs:
        chave = p.stem
        if chave not in titulos:
            sem_bib.append(chave)
            continue
        alvo = limpa(titulos[chave])
        corpo = limpa(texto_inicio(p))
        if not corpo:
            suspeitos.append((chave, "PDF sem texto extraivel (digitalizacao?)", ""))
            continue
        # quantas palavras do titulo do .bib aparecem no inicio do PDF
        palavras = [w for w in alvo.split() if len(w) > 3]
        if not palavras:
            palavras = alvo.split()
        achadas = sum(1 for w in palavras if w in corpo)
        frac = achadas / len(palavras) if palavras else 0.0
        # o titulo bate, mas nenhum dos autores aparece? entao nao e este artigo: e provavelmente
        # um trabalho SOBRE ele. So se exige quando ha apelidos legiveis no .bib.
        aps = apelidos.get(chave, [])
        # ⚠️ Num LIVRO os autores nao estao na pagina de rosto: estao na folha de rosto interior,
        # duas ou tres paginas a frente. Sem esta segunda leitura o verificador acusava o manual
        # de recuperacao de informacao e o livro da predicao conforme, que estao ambos certos.
        sem_autor = bool(aps) and not any(a in corpo for a in aps)
        if sem_autor:
            adiante = limpa(texto_inicio(p, 6))
            sem_autor = not any(a in adiante for a in aps)
        if frac >= 0.70 and sem_autor:
            linhas = [x.strip() for x in texto_inicio(p, 1).splitlines() if len(x.strip()) > 22]
            suspeitos.append((chave, f"titulo bate ({frac:.0%}) mas nenhum autor do .bib aparece "
                                     f"na 1.a pagina: {', '.join(aps)}",
                              linhas[0][:78] if linhas else "?"))
        elif frac >= 0.70:
            bons.append(chave)
        else:
            # o que o PDF parece ser, para ajudar a identificar o engano
            linhas = [x.strip() for x in texto_inicio(p, 1).splitlines() if len(x.strip()) > 22]
            parece = linhas[0][:78] if linhas else "?"
            suspeitos.append((chave, f"so {frac:.0%} do titulo aparece no PDF", parece))

    print(f"PDFs: {len(pdfs)} · correspondem: {len(bons)} · suspeitos: {len(suspeitos)} · "
          f"sem entrada no .bib: {len(sem_bib)}\n")
    for ch, porque, parece in suspeitos:
        print(f"  !! {ch}")
        print(f"     {porque}")
        print(f"     .bib diz : {titulos.get(ch, '')[:78]}")
        if parece:
            print(f"     PDF parece: {parece}")
    for ch in sem_bib:
        print(f"  ?? {ch}: PDF na pasta sem entrada correspondente no .bib")
    return 1 if suspeitos else 0


if __name__ == "__main__":
    sys.exit(main())
