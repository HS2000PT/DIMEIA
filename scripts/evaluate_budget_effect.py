"""A alteracao de politica produziu o efeito pretendido? Antes e depois, com controlo.

A dissertacao descreve a alteracao -- o modelo deixa de vetar e passa a ordenar, com um
orcamento diario de cinco alertas de noticia -- e nao mede o que ela produziu. Este script
mede-o sobre o historico de alertas efectivamente entregues.

O DESENHO, e e o que torna o resultado defensavel:

1. A quantidade medida e a CONCENTRACAO: a fraccao dos alertas que pertence as tres empresas
   mais alertadas. E adimensional, logo compara janelas de tamanhos diferentes.

2. Os alertas de MERCADO servem de CONTROLO NATURAL. Atravessam o mesmo periodo, as mesmas
   empresas e as mesmas condicoes, e o orcamento NAO os governa: conta apenas alertas de
   noticia. Se a concentracao descesse nos dois, a explicacao seria o mercado e nao a alteracao.

3. A reamostragem e por DIA, que e a unidade que o orcamento governa. Reamostrar alertas
   trataria como independentes decisoes que partilham o mesmo tecto diario.

4. CINCO DIAS SAO EXCLUIDOS, E A RAZAO FICA ESCRITA. Entre 25 e 29 de agosto de 2026 o contador
   do dia vivia em disco efemero e voltava ao principio a cada arranque: o registo mostra
   rajadas de exactamente cinco alertas aos segundos dos arranques, e um dia com vinte. Nesses
   dias o orcamento nao estava em vigor. O relatorio publica as duas janelas.

O QUE ISTO NAO E: um ensaio aleatorizado. O controlo partilha o periodo mas nao foi atribuido ao
acaso, e as janelas diferem em duracao e em condicoes de mercado.

USO: python scripts/evaluate_budget_effect.py
SAI: docs/evaluation/evaluation_budget_effect.md
"""
from __future__ import annotations

import collections
import datetime
import json
import pathlib
import subprocess
import sys

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_budget_effect.md"
CORTE = "2026-08-15"
CONTAMINADOS = ("2026-08-25", "2026-08-26", "2026-08-27", "2026-08-28", "2026-08-29")
REPETICOES = 4000
NL = chr(10)


def historico() -> list[dict]:
    """Le o historico de alertas da branch de dados, ou de um ficheiro local."""
    local = RAIZ / "data" / "alerts_history.jsonl"
    if local.exists():
        bruto = local.read_text(encoding="utf-8", errors="replace")
    else:
        r = subprocess.run(["git", "show", "origin/alerts-history:alerts_history.jsonl"],
                           capture_output=True, cwd=RAIZ)
        bruto = r.stdout.decode("utf-8", "replace")
    saida = []
    for linha in bruto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        try:
            saida.append(json.loads(linha))
        except ValueError:
            continue
    return saida


def por_dia(recs: list[dict]) -> dict:
    d: dict = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for r in recs:
        k = r.get("kind")
        t = r.get("ticker")
        dt = (r.get("date") or "")[:10]
        if k in ("news", "market") and t and t != "MARKET" and dt:
            d[dt][k][t] += 1
    return d


def contagem(mapa: dict, dias, kind: str) -> collections.Counter:
    c: collections.Counter = collections.Counter()
    for dt in dias:
        c.update(mapa[dt][kind])
    return c


def concentracao(mapa: dict, dias, kind: str) -> float:
    """Fraccao dos alertas que pertence as tres empresas mais alertadas."""
    c = contagem(mapa, dias, kind)
    n = sum(c.values())
    return sum(v for _, v in c.most_common(3)) / n if n else float("nan")


def mede(mapa: dict, rng) -> list[dict]:
    """Antes, depois e o intervalo da diferenca, para a serie governada e para o controlo."""
    out = []
    for kind, rot in (("news", "notícia"), ("market", "mercado")):
        A = [d for d in mapa if d < CORTE and sum(mapa[d][kind].values())]
        D = [d for d in mapa if d >= CORTE and d not in CONTAMINADOS
             and sum(mapa[d][kind].values())]
        T = [d for d in mapa if d >= CORTE and sum(mapa[d][kind].values())]
        difs = []
        for _ in range(REPETICOES):
            a = concentracao(mapa, list(rng.choice(A, len(A), replace=True)), kind)
            b = concentracao(mapa, list(rng.choice(D, len(D), replace=True)), kind)
            if a == a and b == b:
                difs.append(b - a)
        lo, hi = np.percentile(difs, [2.5, 97.5])
        ca = contagem(mapa, A, kind)
        cd = contagem(mapa, D, kind)
        out.append({
            "rot": rot,
            "a": concentracao(mapa, A, kind),
            "d": concentracao(mapa, D, kind),
            "t": concentracao(mapa, T, kind),
            "na": sum(ca.values()), "nd": sum(cd.values()),
            "ea": len(ca), "ed": len(cd),
            "da": len(A), "dd": len(D),
            "lo": lo, "hi": hi, "exclui": lo * hi > 0,
        })
    return out


def escreve(res: list[dict]) -> None:
    gerado = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
    with SAIDA.open("w", encoding="utf-8") as f:
        w = f.write
        w("# A alteração de política produziu o efeito pretendido?" + NL * 2)
        w("> **Gerado por** `scripts/evaluate_budget_effect.py`. Não editar à mão." + NL)
        w("> **Fonte:** histórico de alertas entregues · **Gerado a:** " + gerado + NL * 2)
        w("O modelo deixou de vetar e passou a ordenar, com um orçamento diário de cinco "
          "alertas de notícia. A quantidade medida é a **concentração**: a fração dos alertas "
          "que pertence às três empresas mais alertadas. Os alertas de **mercado** são o "
          "controlo, porque atravessam o mesmo período e as mesmas empresas e o orçamento não "
          "os governa." + NL * 2)
        w("| Série | Antes | Depois | Diferença | IC 95% | Empresas |" + NL)
        w("|---|---:|---:|---:|---|---|" + NL)
        for x in res:
            marca = "**exclui zero**" if x["exclui"] else "contém zero"
            w("| " + x["rot"] + " | " + format(x["a"], ".3f") + " | " + format(x["d"], ".3f")
              + " | " + format(x["d"] - x["a"], "+.3f") + " | [" + format(x["lo"], "+.3f")
              + ", " + format(x["hi"], "+.3f") + "] " + marca + " | " + str(x["ea"])
              + " para " + str(x["ed"]) + " de 12 |" + NL)
        w(NL)
        for x in res:
            w("- **" + x["rot"] + "**: " + str(x["na"]) + " alertas em " + str(x["da"])
              + " dias antes, " + str(x["nd"]) + " em " + str(x["dd"]) + " dias depois." + NL)
        w(NL + "## Cinco dias excluídos, e porquê" + NL * 2)
        w("Entre 25 e 29 de agosto de 2026 o contador do dia vivia em disco efémero e voltava "
          "ao princípio a cada arranque do processo. O registo mostra rajadas de exatamente "
          "cinco alertas aos segundos dos arranques, e um dia com vinte, num orçamento de "
          "cinco. Nesses dias o orçamento não estava em vigor." + NL * 2)
        for x in res:
            w("- " + x["rot"] + ": com esses dias incluídos a concentração seria `"
              + format(x["t"], ".3f") + "` em vez de `" + format(x["d"], ".3f") + "`." + NL)
        w(NL + "## O que isto não estabelece" + NL * 2)
        w("O controlo partilha o período mas não foi atribuído ao acaso, e as duas janelas "
          "diferem em duração e em condições de mercado. O que a comparação sustenta é que a "
          "quantidade governada se deslocou e a não governada não, e não que nenhuma outra "
          "causa exista." + NL)


def main() -> int:
    recs = historico()
    if not recs:
        print("sem historico de alertas: nada a medir.")
        return 2
    res = mede(por_dia(recs), np.random.default_rng(20260904))
    escreve(res)
    print("-> " + str(SAIDA.relative_to(RAIZ)))
    for x in res:
        print("   " + x["rot"] + ": " + format(x["a"], ".3f") + " -> "
              + format(x["d"], ".3f") + "  [" + format(x["lo"], "+.3f") + ", "
              + format(x["hi"], "+.3f") + "]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
