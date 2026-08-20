"""Cada DOI e cada URL da bibliografia resolvem MESMO, hoje?

⚠️ O `verify_dois.py` pergunta ao Crossref se o registo existe e compara os metadados. Isso
verifica que o identificador está CERTO. Não verifica que a ligação FUNCIONA: um DOI pode estar
correcto no registo e o `doi.org` devolver erro, e um URL pode ter mudado de sítio.

Este script segue cada ligação até ao fim, com redireccionamentos, e diz o código que voltou.
É uma verificação diferente e complementar, e é a que responde à pergunta "clicaste em cada um?".

    python scripts/check_links_vivos.py

Sai a 0 se todos responderem. As falhas de rede são reportadas como tal e não como erro da
bibliografia, porque não são a mesma coisa.
"""

from __future__ import annotations

import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
BIB = RAIZ / "thesis" / "references.bib"

UA = {"User-Agent": "Mozilla/5.0 (compatible; tese-meia/1.0; +mailto:1180934@isep.ipp.pt)"}
TEMPO = 45


def entradas() -> list[tuple[str, str, str]]:
    """(chave, tipo, valor) para cada doi/url/eprint do .bib."""
    t = BIB.read_text(encoding="utf-8")
    fora = []
    for m in re.finditer(r"@(\w+)\{([^,]+),(.*?)\n\}", t, re.S):
        chave, corpo = m.group(2).strip(), m.group(3)
        corpo = re.sub(r"^\s*%%.*$", "", corpo, flags=re.M)   # comentários do .bib
        d = re.search(r"\n\s*doi\s*=\s*[{\"]([^}\"]+)", corpo)
        u = re.search(r"\n\s*url\s*=\s*[{\"]([^}\"]+)", corpo)
        e = re.search(r"\n\s*eprint\s*=\s*[{\"]([^}\"]+)", corpo)
        if d:
            fora.append((chave, "doi", d.group(1).strip()))
        elif u:
            fora.append((chave, "url", u.group(1).strip()))
        elif e:
            fora.append((chave, "arxiv", e.group(1).strip()))
        else:
            fora.append((chave, "sem-id", ""))
    return fora


def segue(url: str) -> tuple[int, str]:
    """Devolve (codigo, destino final). 0 = falha de rede, não de bibliografia."""
    try:
        req = urllib.request.Request(url, headers=UA, method="GET")
        with urllib.request.urlopen(req, timeout=TEMPO) as r:
            return r.getcode(), r.geturl()
    except urllib.error.HTTPError as ex:
        # 403 é frequente em editoras que bloqueiam robôs: a ligação existe, o robô é que não entra
        return ex.code, getattr(ex, "url", url)
    except Exception as ex:  # rede, DNS, TLS
        return 0, f"{type(ex).__name__}: {ex}"


def main() -> int:
    if not BIB.exists():
        print("ERRO: não encontrei a bibliografia em", BIB)
        return 2

    todas = entradas()
    print(f"{len(todas)} entradas no .bib\n")

    maus, avisos, rede, ok = [], [], [], 0
    for chave, tipo, valor in todas:
        if tipo == "sem-id":
            avisos.append((chave, "sem identificador nenhum", ""))
            continue
        alvo = {"doi": f"https://doi.org/{valor}",
                "url": valor,
                "arxiv": f"https://arxiv.org/abs/{valor}"}[tipo]
        codigo, destino = segue(alvo)
        if codigo == 200:
            ok += 1
            print(f"  ok   {chave:26s} {tipo:5s} -> {destino[:74]}")
        elif codigo in (202, 401, 403):
            # ⚠️ O 202 é o desafio anti-robô do IEEE Xplore, e o 403 é o equivalente de outras
            # editoras. Nos dois casos o DOI JÁ redireccionou para a página certa: o que falha é
            # o robô entrar, não a ligação existir. Contá-los como partidos seria alarme falso.
            avisos.append((chave, f"HTTP {codigo} (a editora bloqueia robôs)", destino))
            print(f"  ~~   {chave:26s} {tipo:5s} HTTP {codigo}  {destino[:56]}")
        elif codigo == 0:
            rede.append((chave, destino, ""))
            print(f"  ??   {chave:26s} {tipo:5s} rede: {destino[:60]}")
        else:
            maus.append((chave, f"HTTP {codigo}", destino))
            print(f"  !!   {chave:26s} {tipo:5s} HTTP {codigo}  {destino[:56]}")
        time.sleep(0.35)   # não martelar os servidores

    print(f"\nresolvem: {ok} · bloqueiam robôs: {len(avisos)} · falham: {len(maus)} · "
          f"rede: {len(rede)}")
    for chave, porque, destino in maus:
        print(f"  !! {chave}: {porque}  {destino[:70]}")
    for chave, porque, _ in avisos:
        print(f"  ~~ {chave}: {porque}")

    if maus:
        print("\nUma ligação que não resolve é uma que o júri vai clicar e não abrir.")
        return 1
    if rede:
        print("\nHouve falhas de REDE, não da bibliografia. Correr outra vez com ligação estável.")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
