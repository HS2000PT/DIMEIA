"""Inventário do que se consegue, hoje, voltar a produzir nesta máquina.

Regra do autor (2026-09-09): **o que não se conseguir reproduzir aqui é para desconsiderar**,
nem que isso obrigue a descarregar modelos e conjuntos de dados de raiz.

Este script não julga — inventaria. Para cada resultado congelado em `docs/evaluation/`,
descobre o script que o gerou, os ficheiros de que esse script precisa, e diz quais existem.
A classificação final é do leitor; o que aqui interessa é que a lista seja completa e que
nenhum artefacto fique de fora por esquecimento.

Uso:
    .venv\\Scripts\\python.exe -m scripts.auditar_reprodutibilidade
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from investigator.console import force_utf8_stdout

REPO = Path(__file__).resolve().parents[1]
AVAL = REPO / "docs" / "evaluation"

#: Onde os scripts vão buscar entradas. Padrões suficientes para apanhar caminhos literais.
PADRAO_ENTRADA = re.compile(
    r'["\'](?:\.\./)*((?:data|models|docs)/[A-Za-z0-9_./\-]+)["\']')
PADRAO_DATA_DIR = re.compile(
    r'REPO\s*/\s*"(data|models)"\s*/\s*"([A-Za-z0-9_.\-]+)"(?:\s*/\s*"([A-Za-z0-9_.\-]+)")?')
PADRAO_GERADOR = re.compile(r"Gerado por[^`]*`([^`]+)`")


def gerador(doc: Path) -> str | None:
    texto = doc.read_text(encoding="utf-8", errors="replace")
    m = PADRAO_GERADOR.search(texto)
    if not m:
        return None
    alvo = m.group(1).strip()
    alvo = alvo.split()[0].rstrip("`.,;:")
    return alvo


def entradas(script: Path) -> set[str]:
    if not script.exists():
        return set()
    fonte = script.read_text(encoding="utf-8", errors="replace")
    achados: set[str] = set()
    for m in PADRAO_ENTRADA.finditer(fonte):
        achados.add(m.group(1))
    for m in PADRAO_DATA_DIR.finditer(fonte):
        partes = [p for p in m.groups() if p]
        achados.add("/".join(partes))
    # só entradas: um caminho que o script escreve não conta como dependência
    return {a for a in achados
            if not a.startswith("docs/evaluation/") and not a.endswith(".md")}


def main() -> int:
    force_utf8_stdout()
    linhas: list[dict] = []
    for doc in sorted(AVAL.glob("*.md")):
        g = gerador(doc)
        script = (REPO / g) if g else None
        deps = sorted(entradas(script)) if script else []
        em_falta = [d for d in deps if not (REPO / d).exists()]
        linhas.append({
            "doc": doc.name,
            "gerador": g,
            "gerador_existe": bool(script and script.exists()),
            "entradas": deps,
            "em_falta": em_falta,
        })

    reprod = [x for x in linhas if x["gerador_existe"] and not x["em_falta"] and x["entradas"]]
    quebrados = [x for x in linhas if x["em_falta"]]
    sem_gerador = [x for x in linhas if not x["gerador"]]
    sem_deps = [x for x in linhas
                if x["gerador_existe"] and not x["entradas"] and not x["em_falta"]]

    print(f"{len(linhas)} documentos em docs/evaluation/\n")

    print(f"■ COM ENTRADA EM FALTA — {len(quebrados)}")
    for x in quebrados:
        print(f"  {x['doc']}")
        print(f"     gerador: {x['gerador']}")
        for d in x["em_falta"]:
            print(f"     FALTA:   {d}")
    print()

    print(f"■ GERADOR IDENTIFICADO E ENTRADAS PRESENTES — {len(reprod)}")
    for x in reprod:
        print(f"  {x['doc']}  <- {x['gerador']}")
    print()

    print(f"■ SEM LINHA «Gerado por» — {len(sem_gerador)} (verificar à mão)")
    for x in sem_gerador:
        print(f"  {x['doc']}")
    print()

    print(f"■ GERADOR SEM ENTRADAS DETECTADAS — {len(sem_deps)} (verificar à mão)")
    for x in sem_deps:
        print(f"  {x['doc']}  <- {x['gerador']}")

    destino = REPO / "docs" / "design" / "auditoria_reprodutibilidade.json"
    destino.write_text(json.dumps(linhas, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nInventário: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
