"""Verificação da bibliografia contra os registos canónicos, campo a campo.

O QUE ESTE SCRIPT PROVA, E O QUE NÃO PROVA
------------------------------------------
Prova que cada entrada do `.bib` **existe** e que os metadados que a tese lhe atribui batem
certo com o registo canónico: título, ano, autores, revista/conferência, volume, número,
páginas. Prova ainda uma coisa mais subtil e mais perigosa — que o identificador resolve para
**este** trabalho e não para outro com título parecido.

NÃO prova que a citação sustenta a frase a que está agarrada. Isso é outra auditoria
(`docs/decisions/citation_content_audit.md`), feita a ler, não a resolver identificadores.

PORQUÊ UM SCRIPT E NÃO UM REVISOR
---------------------------------
Metadados bibliográficos são exactamente o tipo de coisa que um modelo de linguagem "confirma"
de memória com toda a confiança e erra. Um `GET` ao Crossref não tem opinião. O resultado é
determinístico e volta a correr antes da defesa.

A VERIFICAÇÃO QUE QUASE NINGUÉM FAZ
-----------------------------------
Para cada entrada que só existe como pré-publicação arXiv, o script **procura no Crossref uma
versão publicada e revista por pares**. Citar a pré-publicação quando já existe versão em actas
ou revista é um reparo legítimo de um arguente — e foi assim que se encontrou o caso do
`dong2024fnspid`, que é o conjunto de dados sobre o qual assenta a tese inteira.

USO
---
    python scripts/verify_bibliography.py
    python scripts/verify_bibliography.py --escrever   # regenera o .md do registo
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[1]
BIBS = [RAIZ / "thesis" / "references.bib", RAIZ / "paper" / "references.bib"]
RELATORIO = RAIZ / "docs" / "decisions" / "bibliography_verification.md"

# O Crossref pede um contacto no User-Agent e, em troca, dá o "polite pool" (mais fiável).
UA = "InvestiGator-thesis-verifier/1.0 (mailto:1180934@isep.ipp.pt)"


# --------------------------------------------------------------------- leitura do .bib
def ler_entradas(caminho: pathlib.Path) -> list[dict]:
    """Analisador de BibTeX suficiente para este ficheiro (chavetas equilibradas)."""
    texto = caminho.read_text(encoding="utf-8")
    entradas = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,]+),", texto):
        tipo, chave = m.group(1).lower(), m.group(2).strip()
        i = texto.index("{", m.start())
        nivel, j = 0, i
        while j < len(texto):
            if texto[j] == "{":
                nivel += 1
            elif texto[j] == "}":
                nivel -= 1
                if nivel == 0:
                    break
            j += 1
        corpo = texto[i + 1 : j]
        campos: dict[str, str] = {}
        for cm in re.finditer(r"(\w+)\s*=\s*", corpo):
            k = cm.group(1).lower()
            resto = corpo[cm.end() :].lstrip()
            if not resto:
                continue
            if resto[0] == "{":
                n, p = 0, 0
                while p < len(resto):
                    if resto[p] == "{":
                        n += 1
                    elif resto[p] == "}":
                        n -= 1
                        if n == 0:
                            break
                    p += 1
                campos[k] = resto[1:p]
            elif resto[0] == '"':
                p = resto.index('"', 1)
                campos[k] = resto[1:p]
            else:
                campos[k] = re.split(r"[,\n]", resto)[0].strip()
        entradas.append({"chave": chave, "tipo": tipo, "campos": campos, "ficheiro": caminho.name})
    return entradas


# ------------------------------------------------------------------------ normalização
def normalizar(s: str) -> str:
    """Título/nome comparável: sem LaTeX, sem acentos, sem pontuação, minúsculas.

    A ordem importa. A primeira versão deste código apagava `\\[a-zA-Z]+` antes de tratar os
    acentos, e `J\\'{e}gou` virava "j gou": o apelido partia-se em dois e o autor aparecia como
    "não encontrado no registo". Quatro entradas foram acusadas por isto — Jégou, Žliobaitė,
    Díaz-Rodríguez e García. Ou seja, o verificador estava a inventar defeitos com acentos.
    Primeiro desfazem-se os acentos de LaTeX, só depois se limpam os comandos restantes.
    """
    s = re.sub(r"\\[`'^\"~=.]\s*\{?([a-zA-Z])\}?", r"\1", s)  # \'e  \"o  \^a  \`u  \~n
    s = re.sub(r"\\[a-zA-Z]+\s*\{([^}]*)\}", r"\1", s)  # \v{Z} \c{c} \u{a}
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s)  # comandos sem argumento
    s = s.replace("{", "").replace("}", "").replace("\\", "")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return " ".join(s.split())


def apelidos(autores_bib: str) -> list[str]:
    nomes = []
    for parte in re.split(r"\s+and\s+", autores_bib):
        parte = parte.strip()
        if not parte:
            continue
        apelido = parte.split(",")[0].strip() if "," in parte else parte.split()[-1]
        nomes.append(normalizar(apelido))
    return nomes


def semelhanca(a: str, b: str) -> float:
    """Semelhança por CONTENÇÃO, não por Jaccard.

    O Crossref guarda muitos títulos truncados no subtítulo: "Anomaly detection" para
    "Anomaly Detection: A Survey", "Using daily stock returns" para "Using Daily Stock Returns:
    The Case of Event Studies". Com Jaccard esses pares dão ~0,45 e o verificador anunciava
    "o DOI resolve para OUTRO trabalho" — a acusação mais grave que sabe fazer — sobre três
    entradas perfeitamente correctas. Contenção pergunta o que interessa: o título mais curto
    está inteiro dentro do mais longo?
    """
    pa, pb = set(normalizar(a).split()), set(normalizar(b).split())
    if not pa or not pb:
        return 0.0
    return len(pa & pb) / min(len(pa), len(pb))


# --------------------------------------------------------------------------- resolução
def obter(url: str, tentativas: int = 3) -> bytes:
    ultimo: Exception | None = None
    for n in range(tentativas):
        try:
            pedido = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(pedido, timeout=40) as r:
                return r.read()
        except Exception as erro:  # noqa: BLE001
            ultimo = erro
            time.sleep(1.5 * (n + 1))
    raise ultimo  # type: ignore[misc]


def crossref_por_doi(doi: str) -> dict | None:
    try:
        d = json.loads(obter(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}"))
        return d.get("message")
    except Exception:  # noqa: BLE001
        return None


def crossref_por_titulo(titulo: str) -> dict | None:
    try:
        q = urllib.parse.urlencode({"query.bibliographic": titulo, "rows": 3})
        d = json.loads(obter(f"https://api.crossref.org/works?{q}"))
        itens = d.get("message", {}).get("items", [])
        return itens[0] if itens else None
    except Exception:  # noqa: BLE001
        return None


def arxiv(eid: str) -> dict | None:
    try:
        bruto = obter(f"http://export.arxiv.org/api/query?id_list={eid}").decode("utf-8")
        t = re.search(r"<entry>.*?<title>(.*?)</title>", bruto, re.S)
        pub = re.search(r"<published>(\d{4})", bruto)
        aut = re.findall(r"<author>\s*<name>(.*?)</name>", bruto, re.S)
        if not t:
            return None
        return {
            "title": [" ".join(t.group(1).split())],
            "ano": pub.group(1) if pub else None,
            "autores": [a.strip() for a in aut],
        }
    except Exception:  # noqa: BLE001
        return None


def ano_de(reg: dict) -> str | None:
    for campo in ("published-print", "published-online", "issued", "created"):
        partes = reg.get(campo, {}).get("date-parts") or []
        if partes and partes[0] and partes[0][0]:
            return str(partes[0][0])
    return None


# ------------------------------------------------------------------------- verificação
def verificar(e: dict) -> dict:
    c = e["campos"]
    achados: list[str] = []
    notas: list[str] = []
    titulo_bib = c.get("title", "")
    resolvido = "—"

    doi = c.get("doi", "").strip()
    eprint = c.get("eprint", "").strip()

    if doi:
        reg = crossref_por_doi(doi)
        if reg is None:
            achados.append(f"DOI **não resolve**: `{doi}`")
        else:
            resolvido = f"Crossref `{doi}`"
            titulo_reg = (reg.get("title") or [""])[0]
            # Alguns registos do Crossref vêm SEM título (o do BERT, por exemplo, é uma ficha
            # vazia do lado deles). Título vazio não é prova de que o DOI aponta para outro
            # trabalho — é ausência de prova, e acusar com base nisso é o oposto de verificar.
            if not titulo_reg.strip():
                notas.append("o registo do Crossref não traz título; comparação feita pelo local")
            else:
                sim = semelhanca(titulo_bib, titulo_reg)
                if sim < 0.6:
                    achados.append(
                        f"o DOI resolve para **outro trabalho** — .bib: “{titulo_bib[:70]}” / "
                        f"registo: “{titulo_reg[:70]}” (semelhança {sim:.2f})"
                    )
            # Um artigo tem legitimamente MAIS DO QUE UM ano. A ACM publica online-first e só
            # depois fecha o número impresso: o survey do Pang saiu online em 2021-03 e em papel
            # em 2022-03; o do Guidotti, 2018-08 e 2019-09. A literatura cita o ano em que
            # apareceu, e é esse que o .bib usa. Aceita-se qualquer um dos anos declarados pelo
            # registo; só um ano que não conste de nenhum é que é um achado.
            ano_bib = c.get("year", "").strip()
            anos_reg = set()
            for campo in ("published-print", "published-online", "issued", "created"):
                partes = reg.get(campo, {}).get("date-parts") or []
                if partes and partes[0] and partes[0][0]:
                    anos_reg.add(str(partes[0][0]))
            if ano_bib and anos_reg and ano_bib not in anos_reg:
                achados.append(f"ano difere — .bib {ano_bib}, registo {'/'.join(sorted(anos_reg))}")
            elif ano_bib and len(anos_reg) > 1:
                notas.append(
                    f"o registo declara {'/'.join(sorted(anos_reg))}; o .bib usa {ano_bib}"
                )

            cont = (reg.get("container-title") or [""])[0]
            declarado = c.get("journal") or c.get("booktitle") or ""
            if cont and declarado and semelhanca(cont, declarado) < 0.35:
                achados.append(
                    f"local difere — .bib “{declarado[:60]}” / registo “{cont[:60]}” "
                    f"(tipo Crossref: {reg.get('type')})"
                )
            for campo, chave_cr in (("volume", "volume"), ("number", "issue")):
                # O traço duplo do LaTeX (1--2) é o mesmo intervalo que o traço simples (1-2).
                v_bib = c.get(campo, "").strip().replace("--", "-").replace(" ", "")
                v_reg = str(reg.get(chave_cr, "")).strip().replace("--", "-").replace(" ", "")
                if v_bib and v_reg and v_bib != v_reg:
                    achados.append(f"{campo} difere — .bib {v_bib}, registo {v_reg}")

            pag_bib = c.get("pages", "").replace("--", "-").replace(" ", "")
            pag_reg = str(reg.get("page", "")).replace(" ", "")
            # Muitos registos antigos do Crossref guardam SÓ a primeira página ("263" para
            # 263-291). Isso não é uma divergência, é um registo incompleto do lado deles —
            # e acusava quatro clássicos (Kahneman, Fama x2, Engle) de estarem errados.
            reg_so_primeira = pag_reg and "-" not in pag_reg
            bate_primeira = reg_so_primeira and pag_bib.split("-")[0] == pag_reg
            # Para artigos da ACL, a ACL Anthology é a fonte canónica e o Crossref discorda dela.
            # Verificado à mão em 2026-08-04: aclanthology.org/D19-1410 dá 3982--3992 (que é o que
            # o .bib tem) e o Crossref dá 3980-3990. Quem manda é a Anthology.
            acl = doi.startswith("10.18653")
            if pag_bib and pag_reg and pag_bib != pag_reg and ":" not in pag_bib:
                if bate_primeira:
                    notas.append(f"o registo só guarda a 1.ª página ({pag_reg}); .bib {pag_bib}")
                elif acl:
                    notas.append(
                        f"páginas do Crossref ({pag_reg}) diferem das da ACL Anthology "
                        f"({pag_bib}); prevalece a Anthology"
                    )
                else:
                    achados.append(f"páginas diferem — .bib {pag_bib}, registo {pag_reg}")

            nomes_reg = [normalizar(a.get("family", "")) for a in reg.get("author", []) or []]
            nomes_bib = apelidos(c.get("author", ""))
            if nomes_reg and nomes_bib:
                if len(nomes_reg) != len(nomes_bib):
                    achados.append(
                        f"nº de autores difere — .bib {len(nomes_bib)}, registo {len(nomes_reg)}"
                    )

                # Partículas ("van den", "de", "von") caem de um lado ou do outro consoante o
                # sistema: o .bib escreve "van den Hengel, Anton" (a forma correcta) e o
                # Crossref guarda family="Hengel", given="Anton Van Den". Comparar a cadeia
                # inteira acusava o apelido de não existir. Basta o último elemento bater.
                def bate(n: str) -> bool:
                    return n in nomes_reg or n.split()[-1] in {
                        r.split()[-1] for r in nomes_reg if r
                    }

                faltam = [n for n in nomes_bib if n and not bate(n)]
                if faltam:
                    achados.append(f"autores não encontrados no registo: {', '.join(faltam)}")

    elif eprint:
        reg = arxiv(eprint)
        if reg is None:
            achados.append(f"arXiv **não resolve**: `{eprint}`")
        else:
            resolvido = f"arXiv `{eprint}`"
            sim = semelhanca(titulo_bib, reg["title"][0])
            if sim < 0.6:
                achados.append(
                    f"o arXiv id resolve para outro trabalho — “{reg['title'][0][:70]}” ({sim:.2f})"
                )
        # A verificação que interessa: já existe versão revista por pares?
        #
        # Só faz sentido perguntar isto a entradas que se DECLARAM pré-publicação. Uma entrada
        # @inproceedings com actas próprias (o "Attention Is All You Need" cita o NeurIPS 2017,
        # que simplesmente não emite DOI) já está a citar a versão publicada, e perguntar de
        # novo só produz ruído — na primeira corrida trouxe um capítulo de livro de 2025 com
        # título parecido. Além disso exige-se sobreposição de AUTORES: uma busca por título
        # devolveu, para o word2vec, um artigo de outra revista que apenas reusa o título.
        declara_preprint = "arxiv" in (c.get("journal", "") + c.get("archiveprefix", "")).lower()
        if declara_preprint:
            publicado = crossref_por_titulo(re.sub(r"[{}\\]", "", titulo_bib))
            if publicado:
                sim = semelhanca(titulo_bib, (publicado.get("title") or [""])[0])
                tipo = publicado.get("type", "")
                fam = {normalizar(a.get("family", "")) for a in publicado.get("author", []) or []}
                meus = set(apelidos(c.get("author", "")))
                sobrepoe = len(fam & meus) / max(1, len(meus))
                if (
                    sim >= 0.9
                    and sobrepoe >= 0.5
                    and tipo in {"proceedings-article", "journal-article", "book-chapter"}
                ):
                    cont = (publicado.get("container-title") or [""])[0]
                    achados.append(
                        f"**existe versão publicada** ({tipo}) em “{cont[:60]}”, "
                        f"DOI `{publicado.get('DOI')}`, pp. {publicado.get('page', '?')} — "
                        f"a entrada cita a pré-publicação"
                    )
    elif c.get("url") or c.get("isbn"):
        alvo = c.get("url") or f"ISBN {c.get('isbn')}"
        if c.get("url"):
            try:
                obter(c["url"])
                resolvido = "URL vivo"
            except Exception as erro:  # noqa: BLE001
                achados.append(f"URL não responde: {alvo} ({type(erro).__name__})")
        else:
            resolvido = f"ISBN `{c.get('isbn')}`"
            notas.append("ISBN não verificado por API (sem serviço gratuito fiável)")
    else:
        achados.append("**sem identificador** (nem DOI, nem arXiv, nem URL, nem ISBN)")

    return {**e, "achados": achados, "notas": notas, "resolvido": resolvido}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--escrever", action="store_true", help="regenerar o .md do registo")
    args = p.parse_args()

    todas: list[dict] = []
    for caminho in BIBS:
        if caminho.exists():
            todas.extend(ler_entradas(caminho))

    print(f"{len(todas)} entradas em {len([b for b in BIBS if b.exists()])} ficheiros\n")
    resultados = []
    for i, e in enumerate(todas, 1):
        r = verificar(e)
        resultados.append(r)
        estado = "ACHADO" if r["achados"] else ("nota  " if r["notas"] else "ok    ")
        print(f"[{i:2d}/{len(todas)}] {estado} {r['ficheiro']:16s} {r['chave']}")
        for a in r["achados"]:
            print(f"          ! {a}")
        for n in r["notas"]:
            print(f"          . {n}")
        time.sleep(0.15)  # cortesia com o Crossref

    com_achados = [r for r in resultados if r["achados"]]
    limpas = len(resultados) - len(com_achados)
    print(f"\n{limpas}/{len(resultados)} sem achados; {len(com_achados)} com achados")

    if args.escrever:
        linhas = [
            "# Verificação da bibliografia — gerado por script",
            "",
            "> `python scripts/verify_bibliography.py --escrever`. **Não editar à mão.**",
            "",
            "Prova que cada entrada **existe** e que os metadados batem certo com o registo",
            "canónico, incluindo que o identificador resolve para *este* trabalho e não para",
            "outro de título parecido. **Não** prova que a citação sustenta a frase onde está —",
            "isso é [`citation_content_audit.md`](citation_content_audit.md).",
            "",
            f"| entradas | {len(resultados)} |",
            "|---|---|",
            f"| sem achados | {len(resultados) - len(com_achados)} |",
            f"| com achados | {len(com_achados)} |",
            "",
            "## Achados",
            "",
        ]
        if com_achados:
            for r in com_achados:
                linhas.append(f"### `{r['chave']}` ({r['ficheiro']})")
                linhas += [f"- {a}" for a in r["achados"]] + [""]
        else:
            linhas += ["Nenhum.", ""]
        linhas += [
            "## Todas as entradas",
            "",
            "| chave | ficheiro | resolvido por | estado |",
            "|---|---|---|---|",
        ]
        for r in sorted(resultados, key=lambda x: (x["ficheiro"], x["chave"])):
            estado = "⚠ achado" if r["achados"] else ("· nota" if r["notas"] else "✅")
            linhas.append(f"| `{r['chave']}` | {r['ficheiro']} | {r['resolvido']} | {estado} |")
        RELATORIO.parent.mkdir(parents=True, exist_ok=True)
        RELATORIO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        print(f"-> {RELATORIO}")

    return 1 if com_achados else 0


if __name__ == "__main__":
    sys.exit(main())
