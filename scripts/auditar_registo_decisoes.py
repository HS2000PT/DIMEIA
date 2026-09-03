"""O registo de decisões dá para retreinar? Cobertura, duplicação e esquema.

Primeiro passo do `docs/planos/RETREINO_CONTROLADO.md`: antes de construir treino nenhum,
inventariar o que o registo tem. Um retreino sobre um registo mal caracterizado produz um
candidato tecnicamente novo assente em evidência incompatível, e isso é pior do que não o fazer.

O que este relatório responde, e cada resposta é uma restrição ao protocolo de aceitação:

1. **Quantas linhas, que período, que empresas.** O tamanho do bloco de comparação.
2. **Quantos títulos distintos.** O sistema repontua a mesma manchete a cada ciclo de sessenta
   segundos, logo o número de linhas não é o número de observações.
3. **Como se distribui `kept`.** Com orçamento diário ligado a triagem deixa de vetar, e uma
   coluna constante não pode sustentar a comparação entre mantidas e suprimidas.
4. **Que fração tem `feature_snapshot` e `model_info`.** As linhas sem eles não são
   reproduzíveis a partir do registo: recalcular as entradas hoje usaria uma série de preços
   que já contém o futuro daquele dia.
5. **Se `as_of` é anterior à data da notícia.** É a assimetria temporal do `ret_event` que a
   dissertação declara, agora observável linha a linha.

Não treina, não escreve em `models/`, não altera nenhum número da tese.

USO:  python scripts/auditar_registo_decisoes.py
      python scripts/auditar_registo_decisoes.py --ficheiro data/predictions_log.jsonl
SAI:  docs/evaluation/registo_decisoes_auditoria.md
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import pathlib
import statistics
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

SAIDA = RAIZ / "docs" / "evaluation" / "registo_decisoes_auditoria.md"
BRANCH = "origin/alerts-history"
FICHEIRO = "predictions_log.jsonl"


def _da_branch() -> list[dict]:
    r = subprocess.run(["git", "show", f"{BRANCH}:{FICHEIRO}"], capture_output=True, cwd=RAIZ)
    if r.returncode:
        print(f"ERRO: não consegui ler {BRANCH}:{FICHEIRO}. Correr `git fetch` primeiro, ou "
              "passar --ficheiro.", file=sys.stderr)
        raise SystemExit(2)
    return _linhas(r.stdout.decode("utf-8", "replace"))


def _linhas(texto: str) -> list[dict]:
    out = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if linha:
            out.append(json.loads(linha))
    return out


def _tabela(cabecalho: list[str], linhas: list[list[str]]) -> str:
    cab = "| " + " | ".join(cabecalho) + " |"
    sep = "|" + "|".join(["---"] * len(cabecalho)) + "|"
    corpo = "\n".join("| " + " | ".join(c) + " |" for c in linhas)
    return f"{cab}\n{sep}\n{corpo}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ficheiro", default=None,
                    help="ler de um ficheiro local em vez da branch de dados.")
    ap.add_argument("--saida", default=str(SAIDA))
    args = ap.parse_args()

    if args.ficheiro:
        origem = str(args.ficheiro)
        registos = _linhas(pathlib.Path(args.ficheiro).read_text(encoding="utf-8"))
    else:
        origem = f"`{BRANCH}:{FICHEIRO}`"
        registos = _da_branch()

    if not registos:
        print("ERRO: registo vazio — nada a auditar.", file=sys.stderr)
        raise SystemExit(2)

    destino = pathlib.Path(args.saida)
    if not destino.is_absolute():
        destino = RAIZ / destino

    n = len(registos)
    datas = sorted(r.get("news_date") for r in registos if r.get("news_date"))
    carimbos = sorted(r.get("ts") for r in registos if r.get("ts"))
    tickers = collections.Counter(r.get("ticker") for r in registos)

    chave = lambda r: (r.get("news_date"), r.get("ticker"), r.get("headline"))  # noqa: E731
    distintos = collections.Counter(chave(r) for r in registos)
    por_titulo = sorted(distintos.values())
    por_ticker_dist: collections.Counter = collections.Counter(k[1] for k in distintos)

    com_prob = sum(1 for r in registos if r.get("prob") is not None)
    com_snap = sum(1 for r in registos if r.get("feature_snapshot"))
    com_modelo = sum(1 for r in registos if r.get("model_info"))
    mantidas = sum(1 for r in registos if r.get("kept"))

    # Primeira linha com snapshot: marca a fronteira entre o registo antigo e o auditável.
    primeiro_snap = next((r.get("ts") for r in registos if r.get("feature_snapshot")), None)

    # Assimetria temporal: `as_of` é a última barra usada; comparada com a data da notícia.
    anterior = igual = posterior = sem_as_of = 0
    for r in registos:
        snap = r.get("feature_snapshot") or {}
        as_of = (snap.get("as_of") or "")[:10]
        nd = (r.get("news_date") or "")[:10]
        if not as_of or not nd:
            sem_as_of += 1 if snap else 0
        elif as_of < nd:
            anterior += 1
        elif as_of == nd:
            igual += 1
        else:
            posterior += 1

    # Títulos distintos por dia de notícia.
    por_dia: collections.Counter = collections.Counter(k[0] for k in distintos)
    mediana_dia = statistics.median(por_dia.values()) if por_dia else 0

    esquemas = collections.Counter(
        (r.get("feature_snapshot") or {}).get("schema")
        for r in registos if r.get("feature_snapshot")
    )

    tab_tickers = _tabela(
        ["Ticker", "Decisões", "Títulos distintos", "Decisões por título"],
        [[t, str(c), str(por_ticker_dist[t]),
          f"{c / por_ticker_dist[t]:.0f}" if por_ticker_dist[t] else "—"]
         for t, c in tickers.most_common()],
    )

    pc = lambda x: f"{100 * x / n:.1f}%"  # noqa: E731

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(f"""# O registo de decisões dá para retreinar?

> **Gerado por** `scripts/auditar_registo_decisoes.py`. Não editar à mão.
> **Fonte:** {origem} · **Gerado a:** {dt.datetime.now(dt.UTC).strftime('%Y-%m-%d %H:%M')} UTC.

## 1. Dimensão

| | |
|---|---|
| Linhas | {n} |
| Títulos distintos (`news_date`, `ticker`, `headline`) | {len(distintos)} |
| Datas de notícia | {datas[0]} a {datas[-1]} |
| Carimbos de decisão | {carimbos[0] if carimbos else '—'} a {carimbos[-1] if carimbos else '—'} |
| Empresas | {len(tickers)} |
| Dias com pelo menos um título | {len(por_dia)} |
| Mediana de títulos distintos por dia | {mediana_dia:.0f} |

**O número de linhas não é o número de observações.** Mediana de
{statistics.median(por_titulo):.0f} decisões por título distinto; máximo de {max(por_titulo)}.

{tab_tickers}

## 2. Esquema

| Campo | Linhas | Fração |
|---|---:|---:|
| `prob` presente | {com_prob} | {pc(com_prob)} |
| `feature_snapshot` presente | {com_snap} | {pc(com_snap)} |
| `model_info` presente | {com_modelo} | {pc(com_modelo)} |
| `kept` verdadeiro | {mantidas} | {pc(mantidas)} |

Primeira linha com `feature_snapshot`: {primeiro_snap or '**nenhuma**'}.
Esquemas de features observados: {dict(esquemas) or 'nenhum'}.

## 3. Momento das entradas

Comparação entre `feature_snapshot.as_of` — a última barra de preço usada — e a data da notícia:

| Relação | Linhas |
|---|---:|
| `as_of` anterior à notícia | {anterior} |
| `as_of` igual à notícia | {igual} |
| `as_of` posterior à notícia | {posterior} |
| snapshot sem `as_of` | {sem_as_of} |

Uma barra anterior à notícia significa que `ret_event` descreve a véspera e não o dia do
acontecimento. É a assimetria que a dissertação declara entre treino e produção; aqui fica
contada em vez de suposta.

## 4. O que isto permite e o que não permite

- Linhas **sem** `feature_snapshot` não são reproduzíveis a partir do registo. Recalcular hoje
  as entradas daquele dia usaria uma série de preços que já contém o que veio a seguir. Essas
  linhas servem para caracterizar a operação; **não servem como conjunto de treino**.
- Se `kept` for constante, a comparação entre decisões mantidas e suprimidas não é recalculável
  sobre esta janela. Com orçamento diário ligado, a triagem ordena e não veta.
- A contagem de títulos distintos por dia é o tamanho real do bloco de comparação. Fixar os
  mínimos de dias e de classes **a partir deste número**, e antes de observar qualquer
  candidato.
""", encoding="utf-8")

    print(f"linhas / títulos : {n} / {len(distintos)}")
    print(f"com snapshot     : {com_snap} ({pc(com_snap)})")
    print(f"kept verdadeiro  : {mantidas} ({pc(mantidas)})")
    print(f"-> {destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
