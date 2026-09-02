#!/usr/bin/env python3
"""Varrimento do orçamento diário: o que se ganha em cobertura e o que se paga em precisão.

## Porque existe

O orçamento de cinco alertas por dia foi **fixado**, nunca varrido. A `precision_at_daily_budget`
usa `budget=5` por omissão, a configuração de produção usa `daily_budget: 5`, e os dois valores
alinham-se de propósito — mas alinhar a produção com a métrica não é o mesmo que ter medido que
cinco é o número certo. A pergunta «porque cinco?» não tinha resposta medida, e é uma pergunta
óbvia numa defesa.

## O que este varrimento é, e o que NÃO é

É uma **curva de compromisso descritiva**, não uma escolha de hiperparâmetro. A diferença
importa e fica escrita aqui para não se perder: escolher o k que maximiza a precisão neste
bloco de teste seria selecionar sobre o conjunto de teste, exactamente o erro que o resto do
trabalho evita. O que a curva permite é decidir com os olhos abertos onde se quer estar entre
duas coisas que se movem em sentidos contrários — quantos alertas se entregam, e que fração
deles corresponde a um movimento anormal.

O eixo que **não** está aqui é a fadiga do leitor. Quantos alertas por dia uma pessoa aguenta
antes de deixar de os ler é uma questão empírica sobre pessoas, e o estudo de feedback no canal
é que a pode informar. Nenhuma curva de precisão a responde.

Saída: `docs/evaluation/evaluation_budget_sweep.md`. Não editar à mão.
"""

from __future__ import annotations

import pathlib
import sys

import joblib
import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from investigator.triage.features import context_block  # noqa: E402
from investigator.triage.model import precision_at_daily_budget  # noqa: E402

DATASET = RAIZ / "data" / "triage_dataset.csv"
BUNDLE = RAIZ / "models" / "triage_context_lr.joblib"
SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_budget_sweep.md"
KS = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 30]
CONGELADO = 0.632      # o valor publicado para k=5
TOLERANCIA = 0.005


def seleccionados(dates, scores, k: int) -> int:
    """Quantas linhas o orçamento k deixa passar no bloco todo."""
    n = 0
    por_dia: dict[object, int] = {}
    for i in np.argsort(-np.asarray(scores, dtype="float64"), kind="stable"):
        d = dates[i]
        if por_dia.get(d, 0) < k:
            por_dia[d] = por_dia.get(d, 0) + 1
            n += 1
    return n


def main() -> int:
    if not DATASET.exists():
        print(f"FALTA {DATASET} — corre scripts/build_dataset.py primeiro.")
        return 1
    df = pd.read_csv(DATASET)
    test = df[df["split"] == "test"].reset_index(drop=True)
    dates, y = test["date"].to_numpy(), test["label"].to_numpy()
    dias = int(test["date"].nunique())
    prevalencia = float(y.mean())

    b = joblib.load(BUNDLE)
    X, _ = context_block(test)
    # ⚠️ `decision_function` e nao a probabilidade calibrada, pelo mesmo motivo que o
    # `evaluate_budget_baselines.py`: esta metrica so depende da ORDEM, e a calibracao de Platt
    # e monotona, portanto nao a altera. Usar a mesma entrada que o outro script e o que permite
    # comparar os dois resultados.
    scores = b["model"].decision_function(X)

    # Porta de reproducao, igual a do outro script: se o protocolo mudou, nao se escreve nada.
    p5_verificacao = precision_at_daily_budget(dates, y, scores, 5)
    if abs(p5_verificacao - CONGELADO) > TOLERANCIA:
        print(f"RECUSADO: k=5 da {p5_verificacao:.4f} e o congelado e {CONGELADO:.3f}. "
              "O protocolo nao e o mesmo — nao se escreve nada.")
        return 1

    linhas = []
    for k in KS:
        p = precision_at_daily_budget(dates, y, scores, k)
        n = seleccionados(dates, scores, k)
        # positivos apanhados: precisão × selecionados
        apanhados = p * n
        recall = apanhados / float(y.sum())
        linhas.append((k, p, n, n / dias, apanhados, recall))

    L = [
        "# evaluation_budget_sweep.md — o orçamento diário, varrido",
        "",
        "> Gerado por `scripts/evaluate_budget_sweep.py`. **Não editar à mão.**",
        "",
        f"- Bloco de teste: **{len(test)}** linhas · **{dias}** dias · "
        f"prevalência **{prevalencia:.4f}**",
        f"- Ordenação: modelo só-contexto implantado (`{BUNDLE.name}`)",
        "",
        "## 1. A curva",
        "",
        "| orçamento k | precisão@k | selecionados | por dia | positivos apanhados | cobertura |",
        "|---|---|---|---|---|---|",
    ]
    for k, p, n, pd_, ap, rc in linhas:
        marca = " ← em produção" if k == 5 else ""
        L.append(f"| **{k}**{marca} | {p:.4f} | {n} | {pd_:.2f} | {ap:.0f} | {rc:.3f} |")

    p5 = dict((k, p) for k, p, *_ in linhas)[5]
    r5 = dict((k, rc) for k, *_, rc in linhas)[5]
    L += [
        "",
        "## 2. Leitura",
        "",
        f"1. **A precisão cai devagar e a cobertura sobe depressa.** De k=5 para k=10 a precisão "
        f"passa de {p5:.3f} para {p5 and dict((k,p) for k,p,*_ in linhas)[10]:.3f} "
        f"(uma queda de {100*(p5-dict((k,p) for k,p,*_ in linhas)[10])/p5:.1f}%), "
        f"e a cobertura sobe de {r5:.3f} para "
        f"{dict((k,rc) for k,*_,rc in linhas)[10]:.3f}.",
        "2. **Nenhum k é o óptimo, porque a métrica não tem óptimo.** A precisão é monótona "
        "decrescente em k por construção: cada lugar extra é ocupado por uma linha com score "
        "mais baixo do que todas as anteriores. Perguntar qual o k que maximiza a precisão é "
        "perguntar por k=1.",
        "3. **A restrição que falta não está nesta tabela.** O limite real é quantos alertas por "
        "dia uma pessoa lê antes de deixar de os ler, e isso mede-se com pessoas, não com este "
        "conjunto. É precisamente o que a recolha de feedback no canal existe para informar.",
        "",
        "## 3. O que isto NÃO autoriza",
        "",
        "Escolher o k desta tabela e chamar-lhe resultado seria selecionar sobre o conjunto de "
        "teste. A tabela descreve um compromisso; a decisão sobre onde estar nele é de desenho, "
        "e tem de ser justificada por fadiga do leitor e por capacidade do canal, não por esta "
        "coluna de precisão.",
        "",
    ]
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text("\n".join(L), encoding="utf-8")
    print(f"[orcamento] escrito {SAIDA}")
    for k, p, _n, pd_, _ap, rc in linhas:
        print(f"  k={k:<3} precisao={p:.4f}  por dia={pd_:.2f}  cobertura={rc:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
