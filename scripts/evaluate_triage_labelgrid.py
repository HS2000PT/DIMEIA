"""evaluate_triage_labelgrid.py — o veredicto da RQ4 sobrevive a outra definição de rótulo?

## Porque é que este script existe

Todo o veredicto da RQ4 — *"nenhum modelo com texto bate a volatilidade"* — assenta num único
rótulo: movimento anormal $\\ge$ 2% na janela (d, d+3]. Esse par (τ, h) foi escolhido uma vez e
nunca mais foi questionado, e um resultado negativo que só valha para uma definição de rótulo é
frágil de uma maneira que um arguente encontra em duas perguntas.

A sensibilidade **já estava paga em disco e ninguém a tinha ido buscar**: o `build_dataset.py`
escreve NOVE colunas `label_t{τ}_h{h}` (τ ∈ {0,015, 0,02, 0,03} × h ∈ {1, 3, 5}) e nenhum script
alguma vez as leu. Este script lê-as.

## O que se mede

Para cada uma das nove definições, treinam-se as **três famílias que decidem a comparação**
(só-volatilidade, só-contexto, contexto+texto) sob EXACTAMENTE o mesmo protocolo do congelado:
mesmo split temporal por dias únicos com embargo, calibração de Platt na validação, PR-AUC no
teste. A pergunta é uma só e é binária:

> **A volatilidade bate o contexto+texto em todas as nove células?**

O bloco de texto é embebido **uma vez** — as features não dependem do rótulo, só o alvo muda.

⚠️ **O script RECUSA-SE a escrever** se a célula (τ=0,02, h=3) não reproduzir os congelados. Se o
protocolo aqui não é o mesmo, as outras oito células não valem nada.

USO
---
    python scripts/evaluate_triage_labelgrid.py            # SBERT (some minutos)
    python scripts/evaluate_triage_labelgrid.py --embedder hashing   # rápido, para fumo
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np
import pandas as pd

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from sklearn.metrics import average_precision_score  # noqa: E402

from investigator.triage.features import context_block, text_block  # noqa: E402
from investigator.triage.model import fit_platt, make_model, scores_of  # noqa: E402

SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_triage_labelgrid.md"
TAUS = (0.015, 0.02, 0.03)
HORIZONTES = (1, 3, 5)
FAMILIAS = ("vol", "context", "full")
# A célula congelada e os seus valores publicados (docs/evaluation/evaluation_triage.md).
CELULA_CONGELADA = (0.02, 3)
CONGELADO = {"vol": 0.542, "context": 0.538, "full": 0.496}
TOLERANCIA = 0.0015


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default=str(RAIZ / "data" / "triage_dataset.csv"))
    ap.add_argument("--embedder", choices=["sbert", "hashing"], default="sbert")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    p = pathlib.Path(args.dataset)
    if not p.exists():
        print(f"FALTA {p} — corre scripts/build_dataset.py primeiro.")
        return 2

    df = pd.read_csv(p)
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    parts = {s: df[df["split"] == s].reset_index(drop=True) for s in ("train", "val", "test")}

    ctx = {s: context_block(parts[s]) for s in parts}
    blocos = {
        "context": ctx,
        "vol": {s: (ctx[s][0][:, :1], ctx[s][1][:1]) for s in parts},
    }
    if args.embedder == "hashing":
        from investigator.historical_kb.embedder import HashingEmbedder

        emb = HashingEmbedder(dim=64)
    else:
        from investigator.historical_kb.embedder import SbertEmbedder

        emb = SbertEmbedder()
    print(f"A embeder o bloco de texto ({args.embedder}) — uma vez para as nove células…")
    txt = {s: text_block(parts[s], emb) for s in parts}
    blocos["full"] = {
        s: (np.hstack([ctx[s][0], txt[s][0]]), ctx[s][1] + txt[s][1]) for s in parts
    }

    grelha: dict[tuple[float, int], dict[str, float]] = {}
    prevalencias: dict[tuple[float, int], float] = {}

    for tau in TAUS:
        for h in HORIZONTES:
            col = f"label_t{tau}_h{h}"
            if col not in df.columns:
                print(f"!! coluna em falta: {col}")
                return 2
            y = {s: parts[s][col].to_numpy() for s in parts}
            prevalencias[(tau, h)] = float(y["test"].mean())
            linha: dict[str, float] = {}
            for nome in FAMILIAS:
                if len(np.unique(y["train"])) < 2 or len(np.unique(y["val"])) < 2:
                    linha[nome] = float("nan")
                    continue
                m = make_model(nome, seed=args.seed)
                m.fit(blocos[nome]["train"][0], y["train"])
                cal = fit_platt(scores_of(m, blocos[nome]["val"][0]), y["val"], seed=args.seed)
                s = cal(scores_of(m, blocos[nome]["test"][0]))
                linha[nome] = float(average_precision_score(y["test"], s))
            grelha[(tau, h)] = linha
            marca = "  <- congelada" if (tau, h) == CELULA_CONGELADA else ""
            print(f"  tau={tau:<5} h={h}  " + "  ".join(
                f"{k}={v:.3f}" for k, v in linha.items()) + marca)

    # ── Porta de reprodução ───────────────────────────────────────────────────
    ref = grelha[CELULA_CONGELADA]
    desvios = {k: abs(ref[k] - v) for k, v in CONGELADO.items()}
    if args.embedder == "sbert" and max(desvios.values()) > TOLERANCIA:
        print("\nRECUSADO: a célula congelada não reproduz "
              f"({', '.join(f'{k} {ref[k]:.3f} vs {v:.3f}' for k, v in CONGELADO.items())}). "
              "Protocolo diferente ⇒ não se escreve nada.")
        return 1

    vitorias_vol = sum(1 for c in grelha.values() if c["vol"] >= c["full"])
    n = len(grelha)

    L = [
        "# evaluation_triage_labelgrid.md — o negativo da RQ4 sobrevive à definição de rótulo?",
        "",
        f"> Gerado por `scripts/evaluate_triage_labelgrid.py` (ADITIVO; não altera congelados). "
        f"Embedder **{args.embedder}**, seed {args.seed}. **Não editar à mão.**",
        "",
        "As nove colunas de rótulo já eram escritas pelo `build_dataset.py` e nunca tinham sido "
        "lidas. Cada célula treina as três famílias que decidem a comparação, sob o mesmo split "
        "temporal, a mesma calibração de Platt e a mesma métrica do congelado.",
        "",
        f"- Porta de reprodução: a célula (τ={CELULA_CONGELADA[0]}, h={CELULA_CONGELADA[1]}) dá "
        f"{', '.join(f'**{k} {ref[k]:.3f}**' for k in FAMILIAS)} contra os congelados "
        f"{', '.join(f'{v:.3f}' for v in CONGELADO.values())}.",
        "",
        "## A grelha (PR-AUC no teste)",
        "",
        "| τ | h | prevalência | só-volatilidade | só-contexto | contexto+texto | vol ≥ full? |",
        "|---|---|---|---|---|---|---|",
    ]
    for (tau, h), c in grelha.items():
        ok = "**sim**" if c["vol"] >= c["full"] else "NÃO"
        marca = " ←" if (tau, h) == CELULA_CONGELADA else ""
        L.append(f"| {tau} | {h} | {prevalencias[(tau, h)]:.3f} | {c['vol']:.3f} | "
                 f"{c['context']:.3f} | {c['full']:.3f} | {ok}{marca} |")

    L += [
        "",
        "## Veredicto",
        "",
        f"A volatilidade bate ou iguala o contexto+texto em **{vitorias_vol} de {n}** células.",
        "",
    ]
    if vitorias_vol == n:
        L.append("O negativo da RQ4 **não depende da definição de rótulo**: vale nas três "
                 "amplitudes e nos três horizontes, com prevalências entre "
                 f"{min(prevalencias.values()):.3f} e {max(prevalencias.values()):.3f}. "
                 "A escolha (τ=0,02, h=3) deixa de ser um ponto de ataque.")
    else:
        perdidas = [f"(τ={t}, h={h})" for (t, h), c in grelha.items() if c["vol"] < c["full"]]
        L.append(f"⚠️ **O negativo NÃO é uniforme.** O texto bate a volatilidade em "
                 f"{', '.join(perdidas)}. Isto tem de ser reportado na tese: o veredicto da RQ4 "
                 "passa a valer *para a definição de rótulo escolhida*, e não em geral.")
    L += [
        "",
        "## O que isto NÃO diz",
        "",
        "- Não é uma re-avaliação do modelo implantado: as famílias são re-treinadas por célula, "
        "e o congelado continua a ser a célula (τ=0,02, h=3).",
        "- Não corrige a dimensionalidade do bloco de texto (isso é o re-teste justo, "
        "`evaluation_triage_fairtext.md`); mede apenas a sensibilidade ao **alvo**.",
    ]
    SAIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nvolatilidade ≥ contexto+texto em {vitorias_vol}/{n} células")
    print(f"escrito: {SAIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
