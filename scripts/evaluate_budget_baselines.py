"""evaluate_budget_baselines.py — o que "escolher às cegas" vale de facto no orçamento diário.

## Porque é que este script existe

A tese afirma, no Caso 4 e no Cap. 6, que a triagem sobe a fracção de alertas materiais de
**0,163 (picking blindly) para 0,632, quase quatro vezes**. O `0,163` vem da linha
`alertar-sempre` da tabela congelada, e essa linha é produzida assim:

    always_scores = np.ones(len(test_df))          # scripts/train_triage.py
    ...
    order = np.argsort(-scores, kind="stable")     # investigator/triage/model.py

Com um score **constante**, um `argsort` **estável** devolve as linhas pela ordem em que estão
no ficheiro, e o ficheiro está ordenado por `(date, ticker)`. Ou seja: o "chão" não escolhe às
cegas — escolhe **por ordem alfabética do ticker**. Medido, as 1.105 linhas que ele selecciona
são **todas AAPL**, o nome alfabeticamente primeiro entre os que têm manchete.

Isto não é uma objecção teórica: um chão errado inflaciona o ganho que a tese reivindica, e o
ganho reivindicado é a **única afirmação positiva** que sustenta a RQ4.

## O que se mede aqui

Quatro ordenações, todas sob a MESMA métrica, o mesmo bloco de teste e o mesmo orçamento:

1. **alertar-sempre** — o chão publicado, reproduzido para se poder falar dele;
2. **aleatório** — o que "às cegas" quer realmente dizer, com a variabilidade entre sementes;
3. **prior por ticker** — a mediana de `vol20` de cada nome, calculada **só no treino**: uma
   tabela de constantes, sem manchete, sem modelo, sem inferência;
4. **modelo só-contexto congelado** — o que está implantado.

⚠️ **O script RECUSA-SE a escrever** se não reproduzir o número congelado do modelo. Um
comparador que não reproduz o congelado não está a medir o mesmo protocolo, e nesse caso as
outras três linhas também não valem nada.

USO
---
    python scripts/evaluate_budget_baselines.py
"""

from __future__ import annotations

import pathlib
import sys
from collections import Counter

import joblib
import numpy as np
import pandas as pd

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from investigator.triage.features import context_block  # noqa: E402
from investigator.triage.model import precision_at_daily_budget  # noqa: E402

DATASET = RAIZ / "data" / "triage_dataset.csv"
BUNDLE = RAIZ / "models" / "triage_context_lr.joblib"
SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_budget_baselines.md"

CONGELADO = 0.632          # docs/evaluation/evaluation_triage.md, linha "LR só-contexto"
TOLERANCIA = 0.0015        # reproduz ao milésimo, como as outras avaliações do projecto
SEMENTES = 40
ORCAMENTO = 5


def seleccionadas(dates: np.ndarray, scores: np.ndarray, budget: int) -> list[int]:
    """As MESMAS linhas que `precision_at_daily_budget` conta, para se poder ver quais são."""
    order = np.argsort(-np.asarray(scores, dtype="float64"), kind="stable")
    by_day: dict[object, int] = {}
    sel: list[int] = []
    for i in order:
        d = dates[i]
        if by_day.get(d, 0) < budget:
            by_day[d] = by_day.get(d, 0) + 1
            sel.append(int(i))
    return sel


def main() -> int:
    if not DATASET.exists():
        print(f"FALTA {DATASET} — corre scripts/build_dataset.py primeiro.")
        return 2

    df = pd.read_csv(DATASET)
    train = df[df["split"] == "train"].reset_index(drop=True)
    test = df[df["split"] == "test"].reset_index(drop=True)
    dates, y = test["date"].to_numpy(), test["label"].to_numpy()

    ordenado = test.equals(
        test.sort_values(["date", "ticker"], kind="stable").reset_index(drop=True))

    # 4. modelo congelado — primeiro, porque é a porta de entrada
    b = joblib.load(BUNDLE)
    X, _ = context_block(test)
    bruto = b["model"].decision_function(X)
    p_modelo = precision_at_daily_budget(dates, y, bruto, ORCAMENTO)
    if abs(p_modelo - CONGELADO) > TOLERANCIA:
        print(f"RECUSADO: o modelo dá {p_modelo:.4f} e o congelado é {CONGELADO:.3f}. "
              "O protocolo não é o mesmo — não se escreve nada.")
        return 1

    # 1. alertar-sempre
    p_sempre = precision_at_daily_budget(dates, y, np.ones(len(test)), ORCAMENTO)
    sel = seleccionadas(dates, np.ones(len(test)), ORCAMENTO)
    comp = Counter(test.loc[sel, "ticker"])
    dominante, n_dom = comp.most_common(1)[0]
    base_dom = float(test[test["ticker"] == dominante]["label"].mean())

    # 2. aleatório
    vals = [precision_at_daily_budget(
        dates, y, np.random.default_rng(s).random(len(test)), ORCAMENTO)
        for s in range(SEMENTES)]
    p_aleat, sd_aleat = float(np.mean(vals)), float(np.std(vals))

    # 3. prior estático por ticker, ajustado SÓ no treino
    prior = train.groupby("ticker")["vol20"].median()
    s_prior = test["ticker"].map(prior).to_numpy(dtype="float64")
    sem_prior = int(np.isnan(s_prior).sum())
    s_prior = np.nan_to_num(s_prior, nan=float(np.nanmedian(s_prior)))
    p_prior = precision_at_daily_budget(dates, y, s_prior, ORCAMENTO)

    prev = float(y.mean())
    linhas = [
        "# evaluation_budget_baselines.md — o chão da precisão@orçamento",
        "",
        f"> Gerado por `scripts/evaluate_budget_baselines.py`. **Não editar à mão.** "
        f"Sementes fixas (0–{SEMENTES - 1}); re-correr sobre o mesmo dataset reproduz.",
        "",
        f"- Bloco de teste: **{len(test)}** linhas · **{test['date'].nunique()}** dias · "
        f"prevalência **{prev:.4f}**",
        f"- Orçamento: **{ORCAMENTO}** alertas/dia · métrica: `precision_at_daily_budget`",
        f"- Porta de reprodução: o modelo só-contexto dá **{p_modelo:.4f}** contra o congelado "
        f"**{CONGELADO:.3f}** ⇒ mesmo protocolo.",
        "",
        "## 1. O achado",
        "",
        f"O ficheiro de teste está ordenado por `(date, ticker)`: **{ordenado}**. Com o score "
        "constante de `alertar-sempre`, o `argsort` estável não ordena nada — devolve a ordem "
        "do ficheiro. O chão publicado não escolhe ao acaso, escolhe por **ordem alfabética**.",
        "",
        f"Das **{len(sel)}** linhas que ele selecciona, **{n_dom}** são de "
        f"**{dominante}** ({100 * n_dom / len(sel):.0f}%), o nome alfabeticamente primeiro.",
        f"A taxa-base do {dominante} no teste é **{base_dom:.4f}** — abaixo da prevalência "
        f"global de {prev:.4f}, e é essa a origem do número.",
        "",
        "## 2. As quatro ordenações",
        "",
        "| ordenação | precisão@5 | o que é |",
        "|---|---|---|",
        f"| alertar-sempre (chão publicado) | **{p_sempre:.4f}** | ordem alfabética do ticker, "
        "não uma escolha cega |",
        f"| aleatória, {SEMENTES} sementes | **{p_aleat:.4f}** ± {sd_aleat:.4f} | o que "
        "\"às cegas\" quer dizer |",
        f"| prior de volatilidade por ticker (só treino) | **{p_prior:.4f}** | "
        f"{len(prior)} constantes, sem manchete e sem modelo |",
        f"| modelo só-contexto (implantado) | **{p_modelo:.4f}** | o congelado |",
        "",
        "## 3. Leitura",
        "",
        f"1. **O ganho reivindicado encolhe.** Contra um chão que escolhe mesmo às cegas, a "
        f"triagem sobe de {p_aleat:.3f} para {p_modelo:.3f} — um factor de "
        f"**{p_modelo / p_aleat:.2f}×**, não de {p_modelo / p_sempre:.1f}×. O ganho continua a "
        "existir e continua a ser real; o que era falso era a sua dimensão.",
        f"2. **Uma tabela de {len(prior)} constantes bate o modelo treinado** "
        f"({p_prior:.3f} vs {p_modelo:.3f}) nesta métrica. É a terceira vez que o método "
        "simples ganha neste trabalho, depois do z-score contra o Isolation Forest e da "
        "volatilidade contra o texto — e é coerente com o que já se sabia: o score do modelo "
        "é dominado por `vol20`.",
        f"3. **A prevalência é {prev:.4f} e o aleatório dá {p_aleat:.4f}.** Coincidirem é a "
        "verificação de sanidade da própria métrica: seleccionar ao acaso tem de render a "
        "taxa-base.",
        "",
        "## 4. O que isto NÃO diz",
        "",
        "- **Não invalida** o PR-AUC, o ROC-AUC nem o Brier da linha `alertar-sempre` "
        "(0.378 / 0.500 / 0.622). Essas três não dependem da ordem entre empates; só a "
        "coluna da precisão@orçamento depende.",
        "- **Não altera** o resultado negativo da RQ4 (nenhum modelo com texto bate a "
        "volatilidade). Esse não passa por esta métrica.",
        f"- **Não diz** que o prior por ticker deva ser implantado: {sem_prior} linhas de "
        "teste pertencem a nomes sem prior no treino e receberam a mediana global, e um "
        "prior estático não reage a nada. O que ele mostra é o custo de comparar contra o "
        "chão errado.",
    ]
    SAIDA.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print(f"chão publicado      {p_sempre:.4f}  ({n_dom}/{len(sel)} linhas são {dominante})")
    print(f"aleatório           {p_aleat:.4f} ± {sd_aleat:.4f}")
    print(f"prior por ticker    {p_prior:.4f}  ({len(prior)} constantes)")
    print(f"modelo congelado    {p_modelo:.4f}  (congelado {CONGELADO:.3f}) ✓")
    print(f"\nescrito: {SAIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
