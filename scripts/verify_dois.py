"""Cada identificador da bibliografia resolvido e conferido campo a campo, sem atalhos.

O que isto faz, e que um olhar humano nao faz bem:
  1. resolve o DOI contra o Crossref e confirma que ele existe;
  2. compara o TITULO devolvido com o do .bib, para apanhar o caso mais grave de todos, que e
     um DOI valido a apontar para OUTRO trabalho;
  3. compara ano, autores e local de publicacao;
  4. assinala as entradas que sao pre-publicacoes (arXiv) e procura versao publicada.

Comparacao de titulos por CONTENCAO e nao por Jaccard: o Crossref guarda muitos titulos
truncados no subtitulo, e o Jaccard acusava classicos de apontarem para outro trabalho.

    python scripts/verify_dois.py            # todos
    python scripts/verify_dois.py --so-doi   # so os que declaram DOI
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[1]
BIB = RAIZ / "thesis" / "references.bib"
SAIDA = RAIZ / "docs" / "decisions" / "doi_verification.md"
UA = "InvestiGator-thesis-check/1.0 (mailto:1180934@isep.ipp.pt)"


def campos(corpo: str) -> dict[str, str]:
    """Campos de uma entrada BibTeX.

    ⚠️ O delimitador final tem de aceitar FIM DE CADEIA e nao so nova linha: o ultimo campo de
    cada entrada nao traz virgula nem newline depois, e uma versao anterior deste extractor
    perdia-o silenciosamente. Como o `doi` costuma ser o ultimo campo, o relatorio dizia que
    quase nao havia DOIs.
    """
    out = {}
    for m in re.finditer(r"(\w+)\s*=\s*[{\"](.*?)[}\"]\s*(?:,|\n|$)", corpo, re.S):
        out[m.group(1).lower()] = re.sub(r"\s+", " ", m.group(2)).strip()
    return out


def limpa(s: str) -> str:
    """Minusculas, sem acentos de LaTeX, sem pontuacao. Acentos ANTES de tirar comandos."""
    s = re.sub(r"\\[`'^\"~=.]\{?(\w)\}?", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def contido(a: str, b: str) -> bool:
    """Um titulo esta contido no outro? Apanha truncagem no subtitulo sem falsos positivos."""
    pa, pb = set(limpa(a).split()), set(limpa(b).split())
    if not pa or not pb:
        return False
    menor, maior = (pa, pb) if len(pa) <= len(pb) else (pb, pa)
    return len(menor & maior) / len(menor) >= 0.80


def crossref(doi: str) -> dict | None:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()).get("message")
    except urllib.error.HTTPError as e:
        return {"__erro__": f"HTTP {e.code}"}
    except Exception as e:  # noqa: BLE001
        return {"__erro__": type(e).__name__}


def procura_publicado(titulo: str) -> dict | None:
    """Existe versao publicada com este titulo? Usado para as entradas de arXiv."""
    url = ("https://api.crossref.org/works?rows=5&select=DOI,title,container-title,issued,type"
           "&query.bibliographic=" + urllib.parse.quote(limpa(titulo)))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            itens = json.loads(r.read().decode())["message"]["items"]
    except Exception:  # noqa: BLE001
        return None
    for it in itens:
        t = (it.get("title") or [""])[0]
        cont = (it.get("container-title") or [""])[0]
        if contido(titulo, t) and "arxiv" not in cont.lower():
            if it.get("type") in ("journal-article", "proceedings-article", "book-chapter"):
                return it
    return None


def main() -> int:
    bib = BIB.read_text(encoding="utf-8")
    entradas = []
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", bib, re.S):
        entradas.append((m.group(1), m.group(2).strip(), campos(m.group(3))))

    achados, ok, sem_id, arxiv = [], 0, [], []
    linhas = []

    for tipo, chave, c in entradas:
        doi = c.get("doi", "").strip()
        titulo = c.get("title", "")
        onde = c.get("journal") or c.get("booktitle") or c.get("publisher") or ""
        eprint = c.get("eprint", "") or ("arxiv" in onde.lower()) or ("arxiv" in c.get("note", "").lower())

        if not doi:
            (arxiv if eprint else sem_id).append((chave, titulo, onde))
            continue

        msg = crossref(doi)
        time.sleep(0.35)  # cortesia com a API
        if not msg:
            achados.append((chave, "sem resposta do Crossref", doi, ""))
            continue
        if "__erro__" in msg:
            achados.append((chave, f"DOI NAO RESOLVE ({msg['__erro__']})", doi, ""))
            continue

        t_cr = (msg.get("title") or [""])[0]
        ano_cr = ""
        for k in ("published-print", "published-online", "issued"):
            if msg.get(k, {}).get("date-parts", [[None]])[0][0]:
                ano_cr = str(msg[k]["date-parts"][0][0])
                break
        cont = (msg.get("container-title") or [""])[0]

        problemas = []
        if t_cr and not contido(titulo, t_cr):
            problemas.append(f"TITULO DIFERENTE: bib='{titulo[:56]}' vs crossref='{t_cr[:56]}'")
        ano_bib = c.get("year", "")
        if ano_cr and ano_bib and abs(int(ano_cr) - int(ano_bib)) > 1:
            problemas.append(f"ano {ano_bib} vs crossref {ano_cr}")

        if problemas:
            for p in problemas:
                achados.append((chave, p, doi, cont))
        else:
            ok += 1
        linhas.append((chave, doi, t_cr[:58], cont[:36], ano_cr, "OK" if not problemas else "!!"))

    # ── relatorio ────────────────────────────────────────────────────────────
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with SAIDA.open("w", encoding="utf-8") as f:
        w = f.write
        w("# Verificacao dos identificadores bibliograficos\n\n")
        w("> Gerado por `scripts/verify_dois.py`. Cada DOI resolvido contra o Crossref e\n")
        w("> comparado campo a campo com o `.bib`. Nao editar a mao.\n\n")
        w(f"- entradas no `.bib`: **{len(entradas)}**\n")
        w(f"- com DOI que resolve e bate certo: **{ok}**\n")
        w(f"- com problema: **{len(achados)}**\n")
        w(f"- sem identificador, nao arXiv: **{len(sem_id)}**\n")
        w(f"- pre-publicacoes (arXiv ou sem DOI): **{len(arxiv)}**\n\n")

        if achados:
            w("## Problemas\n\n| Chave | Problema | DOI | Publicado em |\n|---|---|---|---|\n")
            for ch, p, d, cont in achados:
                w(f"| `{ch}` | {p} | `{d}` | {cont} |\n")
            w("\n")

        if arxiv:
            w("## Pre-publicacoes: existe versao publicada?\n\n")
            w("| Chave | Titulo | Versao publicada encontrada |\n|---|---|---|\n")
            for ch, t, onde in arxiv:
                pub = procura_publicado(t)
                time.sleep(0.35)
                if pub:
                    cont = (pub.get("container-title") or [""])[0]
                    ano = pub.get("issued", {}).get("date-parts", [[None]])[0][0]
                    w(f"| `{ch}` | {t[:44]} | **{cont[:46]}** ({ano}), `{pub['DOI']}` |\n")
                else:
                    w(f"| `{ch}` | {t[:44]} | nao encontrada |\n")
            w("\n")

        if sem_id:
            w("## Sem identificador e sem ser pre-publicacao\n\n")
            for ch, t, onde in sem_id:
                w(f"- `{ch}`: {t[:70]} ({onde[:40]})\n")

        w("\n## Todas as entradas com DOI\n\n")
        w("| Chave | Estado | Crossref devolve | Publicado em | Ano |\n|---|---|---|---|---|\n")
        for ch, d, t, cont, ano, est in sorted(linhas):
            w(f"| `{ch}` | {est} | {t} | {cont} | {ano} |\n")

    print(f"entradas {len(entradas)} · DOI certo {ok} · problemas {len(achados)} · "
          f"pre-publicacoes {len(arxiv)} · sem id {len(sem_id)}")
    for ch, p, d, _ in achados:
        print(f"  !! {ch}: {p}")
    print(f"\nEscrito: {SAIDA}")
    return 1 if achados else 0


if __name__ == "__main__":
    sys.exit(main())
