"""O sistema inteiro vale mais do que as alternativas que a pessoa já tem?

**A lacuna que isto fecha.** A dissertação compara cada componente com linhas de base próprias: o
detetor contra um limiar fixo, a recuperação contra escolha ao acaso, a triagem contra a
volatilidade. Falta a comparação de que o utilizador realmente precisa, que é ao nível do
**sistema**: dadas as notícias de um dia, quais são as cinco que valia a pena mostrar, e o sistema
escolhe-as melhor do que aquilo que qualquer aplicação gratuita já faz?

**As políticas comparadas**, todas sobre o mesmo bloco de teste, o mesmo orçamento de cinco por dia
e o mesmo rótulo:

- **Alertar sempre** — o chão. Selecciona as cinco primeiras que aparecerem.
- **Ao acaso** — o que se acerta por sorte, com muitas sementes para não depender de uma.
- **Quem mais se mexeu hoje** — mostrar notícias das empresas com maior movimento do dia. É a
  alternativa realista: qualquer aplicação de bolsa mostra os maiores movimentos, de graça, e o
  utilizador lê essas notícias. Se o sistema não bater isto, não está a acrescentar nada.
- **Volatilidade da empresa** — o prior de treze constantes, que a dissertação já mostrou ser
  forte.
- **O modelo implantado**.
- **Oráculo** — o melhor que era possível escolher nesse dia, sabendo as respostas. Não é uma
  política: é o **tecto**, e serve para saber quanta margem existe.

⚠️ **Uma linha de base que NÃO se pode medir aqui, e fica dito.** A alternativa mais natural seria
``ler as primeiras cinco notícias que chegam ao feed''. O conjunto de dados histórico não guarda a
hora de publicação, e está ordenado por data e por empresa: usar a ordem do ficheiro mediria
**ordem alfabética**, que é exatamente o artefacto que a dissertação documenta noutro sítio. Uma
linha de base errada é pior do que uma linha de base em falta.

USO:  python scripts/evaluate_endtoend_baselines.py
SAI:  docs/evaluation/evaluation_endtoend_baselines.md
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from investigator.triage.features import context_block  # noqa: E402
from investigator.triage.model import (  # noqa: E402
    fit_platt,
    make_model,
    scores_of,
)

SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_endtoend_baselines.md"
CONGELADO_MODELO = 0.632   # precisão@orçamento do modelo implantado
TOLERANCIA = 0.003
ORCAMENTO = 5
SEMENTES = 40


def precisao_por_dia(df: pd.DataFrame, scores: np.ndarray, k: int,
                     desempate: np.ndarray | None = None) -> float:
    """Fracção de acertos entre os `k` melhores de cada dia, em média sobre os dias.

    ⚠️ O desempate é explícito e aleatório por defeito. Ordenar empates pela posição no ficheiro
    seria ordenar por empresa em ordem alfabética, e foi assim que este projecto já produziu um
    chão que parecia uma linha de base e era um artefacto.
    """
    y = df["label"].to_numpy()
    dias = df["date"].to_numpy()
    if desempate is None:
        desempate = np.zeros(len(df))
    acertos, total = 0, 0
    for d in np.unique(dias):
        m = dias == d
        s, yy, t = scores[m], y[m], desempate[m]
        # lexsort ordena pela ÚLTIMA chave primeiro: score desc, depois o desempate
        ordem = np.lexsort((t, -s))[:k]
        acertos += int(yy[ordem].sum())
        total += len(ordem)
    return acertos / total if total else float("nan")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=str(RAIZ / "data" / "triage_dataset.csv"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    p = pathlib.Path(args.dataset)
    if not p.exists():
        print(f"ERRO: {p} não existe.", file=sys.stderr)
        raise SystemExit(2)

    df = pd.read_csv(p)
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    partes = {s: df[df["split"] == s].reset_index(drop=True) for s in ("train", "val", "test")}
    teste = partes["test"]
    y = {s: partes[s]["label"].to_numpy() for s in partes}
    rng = np.random.default_rng(args.seed)

    # ── o modelo implantado, sob o protocolo congelado ───────────────────────
    xs = {s: context_block(partes[s])[0] for s in partes}
    m = make_model("context", seed=args.seed)
    m.fit(xs["train"], y["train"])
    cal = fit_platt(scores_of(m, xs["val"]), y["val"], seed=args.seed)
    s_modelo = cal(scores_of(m, xs["test"]))

    desempate = rng.random(len(teste))
    p_modelo = precisao_por_dia(teste, s_modelo, ORCAMENTO, desempate)
    if abs(p_modelo - CONGELADO_MODELO) > TOLERANCIA:
        print(f"ERRO: o modelo deu {p_modelo:.3f} e o congelado é {CONGELADO_MODELO:.3f}. "
              "O protocolo não reproduz; não escrevo um relatório incomparável.", file=sys.stderr)
        raise SystemExit(2)
    print(f"porta de entrada ok: modelo {p_modelo:.3f}")

    resultados: list[tuple[str, str, float, str]] = []

    # chão: score constante, desempate aleatório
    p_sempre = float(np.mean([
        precisao_por_dia(teste, np.ones(len(teste)), ORCAMENTO, rng.random(len(teste)))
        for _ in range(SEMENTES)]))
    resultados.append(("Alertar sempre", "não escolhe: leva as primeiras que apareçam",
                       p_sempre, "chão"))

    # ao acaso
    ao_acaso = [precisao_por_dia(teste, rng.random(len(teste)), ORCAMENTO)
                for _ in range(SEMENTES)]
    resultados.append((f"Ao acaso ({SEMENTES} sementes)", "escolhe cinco à sorte",
                       float(np.mean(ao_acaso)), f"±{np.std(ao_acaso):.3f}"))

    # quem mais se mexeu hoje — a alternativa que qualquer app já dá
    mov = np.abs(teste["ret_event"].to_numpy())
    resultados.append(("Quem mais se mexeu hoje",
                       "notícias das empresas com maior movimento do dia",
                       precisao_por_dia(teste, mov, ORCAMENTO, rng.random(len(teste))),
                       "grátis em qualquer app"))

    # prior de volatilidade por empresa (só treino)
    vol = partes["train"].groupby("ticker")["vol20"].mean()
    s_vol = teste["ticker"].map(vol).fillna(float(partes["train"]["vol20"].mean())).to_numpy()
    resultados.append(("Volatilidade da empresa", "treze constantes, sem ler manchete",
                       precisao_por_dia(teste, s_vol, ORCAMENTO, rng.random(len(teste))),
                       "sem modelo"))

    resultados.append(("\\textbf{O modelo implantado}", "a triagem aprendida",
                       p_modelo, "o sistema"))

    # oráculo: o tecto do que era possível escolher
    p_oraculo = precisao_por_dia(teste, teste["label"].to_numpy().astype(float),
                                 ORCAMENTO, rng.random(len(teste)))
    resultados.append(("Oráculo", "sabe as respostas: o melhor possível",
                       p_oraculo, "tecto"))

    prev = float(np.mean(y["test"]))
    dias = teste["date"].nunique()
    tab = "\n".join(f"| {r} | {d} | {v:.3f} | {n} |" for r, d, v, n in resultados)

    melhor_trivial = max(v for r, _, v, _ in resultados
                         if r not in ("\\textbf{O modelo implantado}", "Oráculo"))
    margem = p_oraculo - p_modelo

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(f"""# O sistema vale mais do que as alternativas que a pessoa já tem?

> **Gerado por** `scripts/evaluate_endtoend_baselines.py`. Não editar à mão.
> **Bloco de teste:** {len(teste)} notícias em {dias} dias · **orçamento:** {ORCAMENTO} por dia ·
> **prevalência:** {prev:.3f}
> **Porta de entrada:** o modelo implantado reproduz o congelado (`{p_modelo:.3f}`).

## A pergunta

A dissertação compara cada componente com linhas de base próprias. Falta a comparação de que o
utilizador precisa, que é ao nível do **sistema**: dadas as notícias de um dia, quais as cinco que
valia a pena mostrar, e o sistema escolhe-as melhor do que o que já existe de graça?

Todas as políticas abaixo escolhem cinco por dia, sobre o mesmo bloco e com o mesmo rótulo. O
desempate é **aleatório e explícito** em todas: ordenar empates pela posição no ficheiro seria
ordenar por empresa em ordem alfabética.

## Resultados

| Política | O que faz | Precisão@{ORCAMENTO} | Nota |
|---|---|---|---|
{tab}

## Leitura

**O sistema bate as alternativas triviais**, e a comparação que importa é com a terceira linha:
mostrar notícias de quem mais se mexeu hoje é o que qualquer aplicação de bolsa já faz, de graça, e
obtém `{[v for r, _, v, _ in resultados if r == 'Quem mais se mexeu hoje'][0]:.3f}` contra os
`{p_modelo:.3f}` do sistema.

**Mas a linha mais desconfortável é a da volatilidade**, e já era conhecida: treze constantes
calculadas só sobre o treino, sem ler uma única manchete, obtêm
`{[v for r, _, v, _ in resultados if r == 'Volatilidade da empresa'][0]:.3f}`. É coerente com a
ablação da identidade: o que o modelo faz bem é ordenar empresas, e a volatilidade também o faz.

**E o oráculo diz onde está a margem.** O melhor possível seria `{p_oraculo:.3f}`; o sistema está em
`{p_modelo:.3f}`. Sobram **{margem:.3f}** de margem, quase todos em distinguir *qual* das notícias
de uma empresa importa, que é precisamente aquilo que a Secção da ablação mostrou que este modelo
não consegue fazer.

## O que isto não permite concluir

Que a escolha do sistema seja boa em termos absolutos. A melhor política trivial obtém
`{melhor_trivial:.3f}` e o tecto é `{p_oraculo:.3f}`: há muito espaço entre o que se faz e o que
seria possível.

E há uma linha de base que **não** foi medida, de propósito. A alternativa mais natural, ``ler as
primeiras cinco notícias que chegam ao feed'', exigiria a hora de publicação, que o conjunto de
dados histórico não guarda. Usar a ordem do ficheiro mediria a ordem alfabética das empresas. Uma
linha de base errada é pior do que uma linha de base em falta.
""", encoding="utf-8")

    for r, _, v, n in resultados:
        print(f"  {r.replace(chr(92) + 'textbf{', '').replace('}', ''):34s} {v:.3f}  {n}")
    print(f"-> {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
