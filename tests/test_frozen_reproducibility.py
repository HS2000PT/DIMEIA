"""O bundle CONGELADO reproduz as métricas que o seu próprio sidecar declara?

Porque é que este teste existe. A tese afirma, no Capítulo 3, que o treino é determinístico
dada a semente e que re-correr reproduz os artefactos guardados. Até aqui essa afirmação era
verificada à mão, quando alguém se lembrava. Um teste que a verifica automaticamente muda o
seu estatuto: passa de afirmação para garantia, e se alguém re-treinar com outra semente, com
outro corte ou com outro conjunto de features, a suite parte em vez de a tese continuar a
citar números que o ficheiro já não produz.

⚠️ Salta quando o dataset não está presente. `data/` está gitignored — é grande e é
regenerável — por isso o teste corre na máquina que tem o corpus e salta na CI. Um teste que
inventasse dados para poder correr não estaria a verificar nada.
"""

from __future__ import annotations

import json
import pathlib

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
DATASET = REPO / "data" / "triage_dataset.csv"
BUNDLE = REPO / "models" / "triage_context_lr.joblib"
SIDECAR = REPO / "models" / "triage_context_lr.json"

pytestmark = pytest.mark.skipif(
    not (DATASET.exists() and BUNDLE.exists()),
    reason="precisa de data/triage_dataset.csv (gitignored) e do bundle congelado",
)


@pytest.fixture(scope="module")
def frozen():
    import pandas as pd

    from investigator.triage.features import context_block
    from investigator.triage.model import load_bundle

    meta = json.loads(SIDECAR.read_text(encoding="utf-8"))
    df = pd.read_csv(DATASET)
    test = df[df["split"] == "test"].reset_index(drop=True)
    bundle = load_bundle(BUNDLE)
    x, names = context_block(test)
    assert names == bundle["feature_names"], "as features mudaram debaixo do modelo"
    p = bundle["calibrator"](bundle["model"].predict_proba(x)[:, 1])
    return meta, test, p


def test_o_bloco_de_teste_tem_a_forma_declarada(frozen):
    meta, test, _ = frozen
    assert len(test) == meta["linhas"]["test"]
    assert test["label"].mean() == pytest.approx(meta["positivos"]["test"], abs=1e-12)


@pytest.mark.parametrize("metrica", ["pr_auc", "roc_auc", "brier"])
def test_metricas_congeladas_reproduzem(frozen, metrica):
    """Reprodução EXACTA, não aproximada: o modelo é determinístico e os dados são os mesmos,
    por isso qualquer diferença é uma mudança real e deve falhar."""
    from investigator.triage.model import metrics

    meta, test, p = frozen
    obtido = metrics(test["label"].to_numpy(), p)[metrica]
    assert obtido == pytest.approx(meta["metricas_teste"][metrica], abs=1e-12)


def test_precisao_dentro_do_orcamento_reproduz(frozen):
    """O número que a tese cita como valor de produto (0.632) — mesma definição: ordenar cada
    dia pela probabilidade e admitir os cinco primeiros."""
    meta, test, p = frozen
    topo = test.assign(p=p).sort_values("p", ascending=False).groupby("date").head(5)
    assert topo["label"].mean() == pytest.approx(meta["metricas_teste"]["p_at_budget"], abs=1e-12)


def test_calibrador_e_o_que_a_tese_decompoe(frozen):
    """A Tabela do exemplo trabalhado cita a Platt (a=3.700, c=-2.313). Se o calibrador mudar,
    essa decomposição deixa de reproduzir o 54% que foi realmente enviado ao canal."""
    from investigator.triage.model import load_bundle

    cal = load_bundle(BUNDLE)["calibrator"]
    assert cal.a == pytest.approx(3.700, abs=5e-4)
    assert cal.b == pytest.approx(-2.313, abs=5e-4)
    # E a própria aritmética do exemplo: logit +0.699 -> sigmoide -> Platt -> 0.539.
    p_raw = 1.0 / (1.0 + np.exp(-0.699))
    assert p_raw == pytest.approx(0.668, abs=5e-4)
    assert float(cal(np.array([p_raw]))[0]) == pytest.approx(0.539, abs=1e-3)
