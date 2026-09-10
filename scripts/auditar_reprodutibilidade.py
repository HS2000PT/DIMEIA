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
import subprocess
from pathlib import Path

from investigator.console import force_utf8_stdout

REPO = Path(__file__).resolve().parents[1]
AVAL = REPO / "docs" / "evaluation"

#: Onde os scripts vão buscar entradas. Padrões suficientes para apanhar caminhos literais.
PADRAO_ENTRADA = re.compile(
    r'["\'](?:\.\./)*((?:data|models|docs)/[A-Za-z0-9_./\-]+)["\']')
# ⚠️ ESTE PADRÃO NOMEAVA A VARIÁVEL ERRADA, e era cega a 93% do repositório. Procurava
# `REPO / "data" / …`; medido a 2026-09-10, **55 scripts declaram `RAIZ` e 4 declaram `REPO`** — e
# este ficheiro usa `REPO` para si próprio, pelo que o padrão foi escrito com o nome da sua própria
# variável. Era a causa dos 30 documentos «sem entradas detectadas», que a tarefa C1h.7 registava
# como «ainda não se sabe». Aceitar os dois apanha também o `argparse` de graça: um
# `default=str(RAIZ / "data" / "x.csv")` é a mesma construção.
PADRAO_DATA_DIR = re.compile(
    r'(?:RAIZ|REPO)\s*/\s*"(data|models)"\s*/\s*"([A-Za-z0-9_.\-]+)"'
    r'(?:\s*/\s*"([A-Za-z0-9_.\-]+)")?')
PADRAO_GERADOR = re.compile(r"Gerado por[^`]*`([^`]+)`")

#: Documentos de `docs/evaluation/` que NÃO são artefactos gerados, e por isso não têm gerador.
#: Sem isto leem-se como falha de reprodutibilidade, o que é falso e faz encolher a confiança na
#: lista inteira. A razão fica escrita ao lado, para a isenção não se tornar configuração morta.
PROSA_POR_DESENHO = {
    "kb_fnspid_build.md": "valida em prosa o artefacto construído; não produz números novos",
    "roadmap_rq4.md": "é um roteiro de trabalho, não a saída de uma medição",
    "onnx_minilm_validation.md": "nota de validação escrita à mão e parcialmente"
                                 " supersedida, que remete para a medição reprodutível",
}


def gerador(doc: Path) -> str | None:
    texto = doc.read_text(encoding="utf-8", errors="replace")
    m = PADRAO_GERADOR.search(texto)
    if not m:
        return None
    alvo = m.group(1).strip()
    # ⚠️ O PRIMEIRO TOKEN NÃO É O GERADOR. Vários documentos escrevem «Gerado por `python
    # scripts/evaluate_latency.py --escrever`», e ficar-se pelo primeiro token dá **`python`**, que
    # não é um ficheiro: `gerador_existe` saía falso sobre três scripts que existem. Apanhado a
    # 2026-09-10. É a metade «grita de mais» do par que este projecto documenta — quem lê três
    # falsos «não existe» deixa de olhar para a lista.
    for pedaco in alvo.split():
        pedaco = pedaco.rstrip("`.,;:")
        if pedaco.endswith(".py"):
            return pedaco
    return alvo.split()[0].rstrip("`.,;:")


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


def gitignorado(caminho: str) -> bool:
    """O `.gitignore` exclui este caminho?

    ⚠️ A DISTINÇÃO QUE DECIDE A LEITURA DO RELATÓRIO. Uma entrada em falta que está **gitignored**
    é um intermediário derivado que esta máquina ainda não regenerou — é um pré-requisito, não um
    defeito. Uma entrada em falta que **deveria** estar versionada é que é um defeito. As duas
    pedem acções opostas, e juntá-las fazia o relatório anunciar quatro falhas de
    reprodutibilidade num projecto cuja afirmação central é que tudo se confere.

    Medido a 2026-09-10: os quatro casos são todos gitignored.
    """
    r = subprocess.run(["git", "check-ignore", "-q", caminho],
                       cwd=REPO, capture_output=True)
    return r.returncode == 0


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
    sem_gerador = [x for x in linhas
                   if not x["gerador"] and x["doc"] not in PROSA_POR_DESENHO]
    prosa = [x for x in linhas if x["doc"] in PROSA_POR_DESENHO]
    sem_deps = [x for x in linhas
                if x["gerador_existe"] and not x["entradas"] and not x["em_falta"]]

    print(f"{len(linhas)} documentos em docs/evaluation/\n")

    perdidos = [x for x in quebrados
                if any(not gitignorado(d) for d in x["em_falta"])]
    por_regenerar = [x for x in quebrados if x not in perdidos]

    print(f"■ ENTRADA PERDIDA — {len(perdidos)}  (defeito: deveria estar versionada)")
    for x in perdidos:
        print(f"  {x['doc']}")
        print(f"     gerador: {x['gerador']}")
        for d in x["em_falta"]:
            if not gitignorado(d):
                print(f"     PERDIDA: {d}")
    print()

    print(f"■ INTERMEDIÁRIO POR REGENERAR — {len(por_regenerar)}  (gitignored por desenho; "
          f"não é defeito, é pré-requisito nesta máquina)")
    for x in por_regenerar:
        print(f"  {x['doc']}  <- {x['gerador']}")
        for d in x["em_falta"]:
            print(f"     precisa de: {d}")
    print()

    print(f"■ GERADOR IDENTIFICADO E ENTRADAS PRESENTES — {len(reprod)}")
    for x in reprod:
        print(f"  {x['doc']}  <- {x['gerador']}")
    print()

    print(f"■ SEM LINHA «Gerado por» — {len(sem_gerador)} (verificar à mão)")
    for x in sem_gerador:
        print(f"  {x['doc']}")
    print()

    print(f"■ PROSA POR DESENHO, sem gerador e sem defeito — {len(prosa)}")
    for x in prosa:
        print(f"  {x['doc']}  ({PROSA_POR_DESENHO[x['doc']]})")
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
