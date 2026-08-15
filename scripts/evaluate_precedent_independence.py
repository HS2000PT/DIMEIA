"""Quantos dias DISTINTOS estão por trás dos precedentes que um alerta mostra?

O impacto é medido por `(ticker, dia)`. Três manchetes da mesma empresa no mesmo dia partilham,
**por construção**, exactamente o mesmo impacto. Um alerta que mostra três casos e afirma
*"3 of 3 shown cases moved down"* pode, portanto, estar a contar **um** dia observado três vezes,
e a apresentar como concordância aquilo que é uma repetição.

Isto não é uma hipótese: mede-se sobre os alertas **realmente entregues** ao canal, lidos da
branch de dados. Nada é reconstruído nem simulado.

USO:  python scripts/evaluate_precedent_independence.py
SAI:  docs/evaluation/evaluation_precedent_independence.md
"""

from __future__ import annotations

import collections
import json
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_precedent_independence.md"
BRANCH = "origin/alerts-history"
FICHEIRO = "alerts_history.jsonl"

# "▸ -2.73% in 5d · AAPL 2026-08-05 (8d ago) · "..." (sim 0.56)"
RX_CASO = re.compile(r"·\s*([A-Z]{1,5})\s+(\d{4}-\d{2}-\d{2})\s*\(")
RX_UNANIME = re.compile(r"(\d+) of (\d+) shown cases moved")


def historico() -> list[dict]:
    r = subprocess.run(["git", "show", f"{BRANCH}:{FICHEIRO}"],
                       capture_output=True, cwd=RAIZ)
    if r.returncode:
        print(f"ERRO: não consegui ler {BRANCH}:{FICHEIRO}. Correr `git fetch` primeiro.",
              file=sys.stderr)
        raise SystemExit(2)
    linhas = r.stdout.decode("utf-8", "replace").strip().splitlines()
    return [json.loads(x) for x in linhas if x.strip()]


def main() -> None:
    alertas = historico()
    noticias = [a for a in alertas if a.get("kind") == "news"]

    dist: collections.Counter = collections.Counter()
    com_prec = 0
    unanimes = 0
    unanimes_um_dia = 0
    primeiro, ultimo = None, None

    for a in noticias:
        casos = RX_CASO.findall(a.get("text", ""))
        if not casos:
            continue
        com_prec += 1
        d = a.get("date")
        primeiro = d if primeiro is None or d < primeiro else primeiro
        ultimo = d if ultimo is None or d > ultimo else ultimo
        dist[(len(casos), len(set(casos)))] += 1
        m = RX_UNANIME.search(a["text"])
        if m and m.group(1) == m.group(2):
            unanimes += 1
            if len(set(casos)) == 1:
                unanimes_um_dia += 1

    if not com_prec:
        print("ERRO: nenhum alerta com precedentes. Não escrevo um relatório vazio.",
              file=sys.stderr)
        raise SystemExit(2)

    colapsados = sum(c for (n, u), c in dist.items() if n > 1 and u < n)
    so_um = sum(c for (n, u), c in dist.items() if n > 1 and u == 1)
    pc = 100.0 / com_prec

    linhas_tab = "\n".join(
        f"| {n} | {u} | {c} | {c*pc:.1f}% |"
        for (n, u), c in sorted(dist.items())
    )

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(f"""# Independência dos precedentes mostrados

> **Gerado por** `scripts/evaluate_precedent_independence.py`. Não editar à mão.
> **Fonte:** os alertas **realmente entregues** ao canal, lidos de `{BRANCH}:{FICHEIRO}`.
> Nada é reconstruído nem simulado.

## O que se mede, e porquê

O impacto de uma notícia é medido por `(ticker, dia)`. Logo, **duas manchetes da mesma empresa
no mesmo dia partilham exactamente o mesmo impacto por construção** — não porque o mercado tenha
reagido duas vezes da mesma maneira, mas porque é o mesmo dia.

Um alerta que mostra três precedentes e diz *"3 of 3 shown cases moved down"* está a apresentar
isso como **concordância entre casos**. Se os três forem do mesmo dia, é **um** caso repetido três
vezes, e a frase promete mais evidência do que existe.

## Resultado

- Alertas de notícia com precedentes: **{com_prec}**
- Período: **{primeiro}** a **{ultimo}**

| Casos mostrados | Dias distintos por trás | Alertas | % |
|---|---|---|---|
{linhas_tab}

- Com **menos dias distintos** do que casos mostrados: **{colapsados}/{com_prec}
  ({colapsados*pc:.1f}%)**
- Com **todos os casos do mesmo dia**: **{so_um}/{com_prec} ({so_um*pc:.1f}%)**
- Alertas que afirmam unanimidade (*"N of N shown cases moved"*): **{unanimes}**
  - destes, apoiados num **único** dia observado: **{unanimes_um_dia}**
    ({100.0*unanimes_um_dia/unanimes:.1f}% dos unânimes)

## Leitura honesta

A recuperação **não está errada**: as manchetes recuperadas são genuinamente as mais parecidas, e
o impacto de cada uma é o impacto real daquele dia. O que está errado é a **forma de apresentar**:
contar casos quando o que varia são dias.

Isto **não afecta** nenhuma métrica de recuperação reportada na dissertação. A precisão@5 conta
manchetes relevantes, não dias, e a concordância de direcção é medida par a par sobre o corpus
histórico, não sobre estes alertas.

O que afecta é a **força que o alerta reivindica** quando fala ao utilizador, e é por isso que fica
registado como limitação em vez de ser corrigido em silêncio.
""", encoding="utf-8")

    print(f"alertas com precedentes : {com_prec}  ({primeiro} a {ultimo})")
    print(f"colapsados              : {colapsados} ({colapsados*pc:.1f}%)")
    print(f"todos do mesmo dia      : {so_um} ({so_um*pc:.1f}%)")
    print(f"unanimes num so dia     : {unanimes_um_dia}/{unanimes}")
    print(f"-> {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
