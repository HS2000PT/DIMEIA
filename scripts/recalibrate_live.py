"""Recalibra o modelo de triagem para a população que ele de facto vê em produção.

O PROBLEMA, EM UMA FRASE
-----------------------
O modelo foi ajustado num corpus com prevalência de materialidade de **0,378** e é aplicado a
um conjunto onde ela corre a **0,626** — porque só chegam à triagem manchetes que já passaram
os filtros de relevância e de frescura. Os filtros a montante fizeram metade do trabalho antes
de o modelo ser consultado, e as probabilidades que ele emite ficam na escala errada: medido,
itens pontuados perto de 0,50 revelam-se materiais 0,66 das vezes. Um utilizador que lê "50%"
está a ler um número honesto para o corpus de treino e enganador para o dele.

O QUE ESTE SCRIPT FAZ, E O QUE SE RECUSA A FAZER
------------------------------------------------
Reajusta **apenas a camada de calibração** (dois parâmetros de Platt) sobre as decisões ao vivo
já rotuladas pelo desfecho. Não re-treina o modelo: com poucas centenas de decisões rotuladas,
e agrupadas em poucas dezenas de pares (ticker, dia), reajustar nove coeficientes seria ajustar
ruído com aparência de método.

**E recusa-se a escrever se a discriminação estiver ao nível do acaso.** Esta é a regra que dá
sentido ao script, e vale a pena dizer porquê. A calibração de Platt é uma sigmóide crescente,
portanto uma transformação **monótona**: preserva a ordenação exactamente. Se o score não
ordena, recalibrar melhora o Brier — os números aproximam-se da taxa-base e o erro quadrático
desce — sem melhorar **nada** na decisão que o produto toma. Escrever um artefacto novo nesse
caso produziria um número melhor e um sistema igual, que é a definição de métrica cosmética.
O script exige por isso que o limite inferior do IC de ROC-AUC ultrapasse `--min-auc`.

O artefacto novo é escrito AO LADO do congelado (`*_live.joblib`), nunca por cima: os números
da tese vêm do congelado e têm de continuar a poder ser reproduzidos.

USO
---
    python scripts/recalibrate_live.py --dry-run     # mede e reporta, não escreve
    python scripts/recalibrate_live.py               # escreve se a discriminação justificar
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from datetime import UTC, datetime

import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

CONGELADO = RAIZ / "models" / "triage_context_lr.joblib"
SAIDA = RAIZ / "models" / "triage_context_lr_live.joblib"
SEMENTE = 42


def main() -> int:
    ap = argparse.ArgumentParser(description="Recalibração ao vivo da triagem")
    ap.add_argument("--log", default="")
    ap.add_argument("--tau", type=float, default=0.02)
    ap.add_argument("--horizon", type=int, default=3)
    ap.add_argument("--min-auc", type=float, default=0.55,
                    help="limite INFERIOR do IC de ROC-AUC exigido para escrever")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=str(SAIDA))
    args = ap.parse_args()

    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    from investigator.console import force_utf8_stdout
    from investigator.triage.model import PlattCalibrator, load_bundle, save_bundle
    from scripts.evaluate_live_transfer import _maturar

    force_utf8_stdout()

    caminho = pathlib.Path(args.log) if args.log else RAIZ / "data" / "_live_predictions.jsonl"
    if not caminho.exists():
        raise SystemExit(f"Sem log de decisões em {caminho}. Corre evaluate_live_transfer.py "
                         "primeiro, ou passa --log.")

    maturadas = _maturar(caminho, args.tau, args.horizon)
    p = np.array([float(d["prob"]) for d in maturadas])
    y = np.array([int(d["label"]) for d in maturadas])
    clusters = np.array([f"{d['ticker']}|{d['news_date'][:10]}" for d in maturadas])
    n, base = len(y), float(y.mean())

    # A porta: discriminação medida com IC de cluster (o rótulo é por ticker-dia).
    roc = float(roc_auc_score(y, p))
    rng = np.random.default_rng(SEMENTE)
    uniq = np.unique(clusters)
    idx = {c: np.flatnonzero(clusters == c) for c in uniq}
    boots = []
    for _ in range(2000):
        i = np.concatenate([idx[c] for c in rng.choice(uniq, size=len(uniq), replace=True)])
        if len(np.unique(y[i])) > 1:
            boots.append(roc_auc_score(y[i], p[i]))
    lo = float(np.percentile(boots, 2.5))

    print(f"decisoes maturadas: {n} em {len(uniq)} pares (ticker,dia)")
    print(f"prevalencia ao vivo: {base:.3f}  (treino 0.378)")
    print(f"ROC-AUC {roc:.3f}  IC95% inferior {lo:.3f}  (exigido > {args.min_auc:.2f})")

    if lo <= args.min_auc:
        print()
        print("RECUSADO: a discriminacao nao supera o acaso com margem.")
        print("A calibracao de Platt e monotona: preserva a ordem. Recalibrar melhoraria o")
        print("Brier sem mudar UMA decisao do gate. Escrever um artefacto novo aqui seria")
        print("produzir um numero melhor e um sistema igual.")
        print()
        print("O que isto indica NAO e 'afinar o limiar': e que o score nao transfere para")
        print("esta populacao. Ver docs/evaluation/evaluation_live_transfer.md.")
        return 2

    # Só chega aqui se houver ordenação real para preservar.
    lr = LogisticRegression(max_iter=1000, random_state=SEMENTE)
    lr.fit(p.reshape(-1, 1), y)
    cal = PlattCalibrator(a=float(lr.coef_[0][0]), b=float(lr.intercept_[0]))
    antes = float(np.mean((p - y) ** 2))
    depois = float(np.mean((cal(p) - y) ** 2))
    print(f"Brier {antes:.4f} -> {depois:.4f} ({depois - antes:+.4f})")

    if args.dry_run:
        print("dry-run: nada escrito.")
        return 0

    b = load_bundle(CONGELADO)
    meta = {
        "gerado": datetime.now(UTC).isoformat(timespec="seconds"),
        "origem": "recalibrate_live.py",
        "base_congelada": CONGELADO.name,
        "decisoes": n, "clusters": int(len(uniq)),
        "prevalencia_viva": base, "roc_auc": roc, "roc_auc_ic_inferior": lo,
        "brier_antes": antes, "brier_depois": depois,
        "nota": "SO a camada de calibracao foi reajustada; os coeficientes vem do congelado.",
    }
    save_bundle(pathlib.Path(args.out), b["model"], cal, b["feature_names"], meta)
    print(f"Escrito: {args.out}")
    print(json.dumps(meta, indent=1)[:400])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
