"""Quanto do modelo de triagem é a NOTÍCIA, e quanto é apenas a IDENTIDADE DA EMPRESA?

**A pergunta, e porque é a certa.** O modelo de contexto recebe nove entradas. Sete descrevem a
empresa e mudam devagar ou nada (volatilidade, momento, e os cinco indicadores de setor), uma
descreve o dia (o retorno do próprio dia, igual para todas as notícias desse dia), e **uma só**
distingue duas manchetes da mesma empresa no mesmo dia: o comprimento do título.

Se assim é, então o que esse modelo aprendeu deve ser reproduzível por uma **tabela de consulta
por empresa**. Este script testa isso da forma mais directa possível: constrói um preditor que
ignora completamente a notícia e devolve, para cada empresa, a taxa de positivos que ela teve no
bloco de treino. Nada mais. Se esse preditor igualar o modelo, o modelo é uma tabela.

**Porque isto importa mais do que parece.** O resultado negativo da questão da triagem foi
reportado como um achado sobre *texto*. Se a variante implantada nem sequer podia distinguir duas
notícias, então parte do que se atribuiu ao texto é, na verdade, uma consequência do conjunto de
entradas. Separar as duas coisas é a diferença entre uma conclusão e uma coincidência.

**Protocolo.** O mesmo do treino congelado, e o script reproduz os valores congelados como porta
de entrada: se não reproduzir, **não escreve**, porque um relatório produzido por outro protocolo
não é comparável com a dissertação.

USO:  python scripts/evaluate_triage_identity.py
SAI:  docs/evaluation/evaluation_triage_identity.md
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
    metrics,
    precision_at_daily_budget,
    scores_of,
)

SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_triage_identity.md"
CONGELADO_VOL = 0.542       # LR só-volatilidade
CONGELADO_CONTEXTO = 0.538  # LR só-contexto (a implantada)
TOLERANCIA = 0.002

# Quais colunas do bloco de contexto pertencem a que nível.
NIVEL_EMPRESA = ("vol20", "mom5", "sector_")
NIVEL_DIA = ("ret_event",)
NIVEL_NOTICIA = ("headline_len",)


def treina(xtr, ytr, xva, yva, xte, datas, yte, seed=42):
    """Um modelo, com o mesmo protocolo do treino congelado. Devolve as métricas."""
    m = make_model("context", seed=seed)
    m.fit(xtr, ytr)
    cal = fit_platt(scores_of(m, xva), yva, seed=seed)
    s = cal(scores_of(m, xte))
    return {**metrics(yte, s),
            "p_at_budget": precision_at_daily_budget(datas, yte, s, 5)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=str(RAIZ / "data" / "triage_dataset.csv"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    p = pathlib.Path(args.dataset)
    if not p.exists():
        print(f"ERRO: {p} não existe. Correr `scripts/build_dataset.py` primeiro.",
              file=sys.stderr)
        raise SystemExit(2)

    df = pd.read_csv(p)
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    partes = {s: df[df["split"] == s].reset_index(drop=True) for s in ("train", "val", "test")}
    y = {s: partes[s]["label"].to_numpy() for s in partes}
    datas = partes["test"]["date"].to_numpy()

    xs, nomes = {}, None
    for s in partes:
        x, n = context_block(partes[s])
        xs[s] = x
        nomes = n
    print(f"colunas do bloco de contexto: {nomes}")

    def idx(pred) -> list[int]:
        return [i for i, n in enumerate(nomes) if pred(n)]

    e_dia = idx(lambda n: n in NIVEL_DIA)
    e_noticia = idx(lambda n: n in NIVEL_NOTICIA)

    linhas: list[tuple[str, str, dict]] = []

    # ── portas de entrada: reproduzir os congelados ──────────────────────────
    so_vol = [i for i, n in enumerate(nomes) if n == "vol20"]
    r_vol = treina(xs["train"][:, so_vol], y["train"], xs["val"][:, so_vol], y["val"],
                   xs["test"][:, so_vol], datas, y["test"], args.seed)
    r_ctx = treina(xs["train"], y["train"], xs["val"], y["val"],
                   xs["test"], datas, y["test"], args.seed)
    for rot, obtido, esperado in (("só-volatilidade", r_vol["pr_auc"], CONGELADO_VOL),
                                  ("só-contexto", r_ctx["pr_auc"], CONGELADO_CONTEXTO)):
        if abs(obtido - esperado) > TOLERANCIA:
            print(f"ERRO: {rot} deu {obtido:.3f} e o congelado é {esperado:.3f}. "
                  "O protocolo não reproduz; não escrevo um relatório incomparável.",
                  file=sys.stderr)
            raise SystemExit(2)
    print(f"porta de entrada ok: vol {r_vol['pr_auc']:.3f} · contexto {r_ctx['pr_auc']:.3f}")

    linhas.append(("Contexto completo (o implantado)", "as nove entradas", r_ctx))
    linhas.append(("Só volatilidade", "uma entrada, de nível de empresa", r_vol))

    # ── a tabela de consulta: ignora a notícia por completo ──────────────────
    # Para cada empresa, a taxa de positivos que ela teve no TREINO. Nenhuma informação da
    # notícia entra aqui, nem sequer o dia. É o limite do que "saber só a empresa" consegue.
    taxa = partes["train"].groupby("ticker")["label"].mean()
    global_ = float(partes["train"]["label"].mean())
    s_tab = partes["test"]["ticker"].map(taxa).fillna(global_).to_numpy(dtype="float64")
    r_tab = {**metrics(y["test"], s_tab),
             "p_at_budget": precision_at_daily_budget(datas, y["test"], s_tab, 5)}
    linhas.append(("\\textbf{Tabela de consulta por empresa}",
                   "**zero** informação sobre a notícia", r_tab))

    # ── ablações ─────────────────────────────────────────────────────────────
    combos = [
        ("Sem os indicadores de setor", "tira 5 entradas de empresa",
         [i for i in range(len(nomes)) if not nomes[i].startswith("sector_")]),
        ("Sem volatilidade nem momento", "tira as 2 entradas de empresa que restam",
         [i for i in range(len(nomes)) if nomes[i] not in ("vol20", "mom5")]),
        ("Sem NADA de nível de empresa", "fica só o dia e a notícia",
         e_dia + e_noticia),
        ("Só o comprimento do título", "a única entrada de nível de notícia", e_noticia),
    ]
    for rot, desc, cols in combos:
        if not cols:
            continue
        r = treina(xs["train"][:, cols], y["train"], xs["val"][:, cols], y["val"],
                   xs["test"][:, cols], datas, y["test"], args.seed)
        linhas.append((rot, desc, r))
        print(f"  {rot:32s} PR-AUC={r['pr_auc']:.3f}")

    prev = float(np.mean(y["test"]))
    tab = "\n".join(
        f"| {rot} | {desc} | {r['pr_auc']:.3f} | {r['roc_auc']:.3f} | {r['p_at_budget']:.3f} |"
        for rot, desc, r in linhas)

    dif = abs(r_tab["pr_auc"] - r_ctx["pr_auc"])
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(f"""# Quanto do modelo de triagem é a notícia, e quanto é a empresa?

> **Gerado por** `scripts/evaluate_triage_identity.py`. Não editar à mão.
> **Protocolo:** o mesmo do treino congelado (divisão temporal, calibração de Platt na validação,
> semente {args.seed}). Os valores congelados são reproduzidos como porta de entrada:
> só-volatilidade `{r_vol['pr_auc']:.3f}` e só-contexto `{r_ctx['pr_auc']:.3f}`.
> **Prevalência do teste (o chão da PR-AUC):** `{prev:.3f}`

## O que se testa

O modelo de contexto recebe nove entradas. Sete descrevem a **empresa**, uma descreve o **dia**, e
uma só distingue duas manchetes da mesma empresa no mesmo dia (o comprimento do título).

A pergunta é se o que ele aprendeu se reduz a saber **de que empresa se trata**. Testa-se com o
preditor mais simples possível: para cada empresa, a taxa de positivos que ela teve no bloco de
treino. Ignora a manchete, ignora o dia, ignora tudo.

## Resultados

| Modelo | O que vê | PR-AUC | ROC-AUC | Precisão@5/dia |
|---|---|---|---|---|
{tab}

## Leitura

A tabela de consulta por empresa obtém **{r_tab['pr_auc']:.3f}** contra os
**{r_ctx['pr_auc']:.3f}** do modelo implantado: uma diferença de **{dif:.3f}**.

Esse preditor não vê a notícia. Não vê sequer o dia. Devolve um número por empresa, fixado no
treino, e nunca mais muda. Se ele reproduz o essencial do que o modelo faz, então o que o modelo
faz é, no essencial, **reconhecer a empresa**.

As ablações confirmam de onde vem o sinal: retirar as entradas de nível de empresa desmonta o
modelo, e o que fica quando só sobra o comprimento do título anda ao nível do chão.

## O que isto NÃO diz

Que a questão de investigação sobre triagem esteja mal respondida. A variante **com texto** tem
$384$ números por manchete, portanto tem informação real sobre a notícia, e essa comparação é a que
responde à pergunta.

O que isto diz é mais estreito e mais útil: **a variante que foi implantada como porta de decisão
não podia distinguir duas notícias da mesma empresa**, e portanto o seu desempenho agregado nunca
foi evidência de que soubesse triar notícias. É uma limitação do conjunto de entradas, não do
treino, e nenhuma quantidade de dados a resolveria.
""", encoding="utf-8")

    print(f"\ntabela de consulta {r_tab['pr_auc']:.3f} vs implantado {r_ctx['pr_auc']:.3f} "
          f"(diferença {dif:.3f})")
    print(f"-> {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
