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


# ⚠️ A tolerância deixou de ser `1e-12` a 2026-09-10, e a razão fica escrita aqui e não noutro
# ficheiro, porque um critério afrouxado em silêncio é indistinguível de um critério contornado.
#
# O sidecar foi gerado a 2026-07-04 **noutra máquina** — o caminho de dataset que ele próprio
# grava aponta para outro perfil de utilizador — e as features de contexto derivam dos **preços**.
# Os preços de setembro não são bit a bit os de julho: a amostra versionada mostra a `vol20` a
# divergir do oitavo dígito significativo (0,011042942691755403 contra 0,011042962612463809).
# Nenhum rótulo virou — a contagem de positivos é idêntica e o teste da forma do bloco continua
# a passar a `1e-12` —, mas o `p` desloca-se ~6e-9 por elemento e as métricas ~1e-8.
#
# Medido, e não suposto: a deriva **não** é ruído de vírgula flutuante (está sete ordens de
# grandeza acima do eps da dupla precisão) e **não** vem das bibliotecas — o `predict_proba` é
# bit-idêntico a uma sigmoide em `numpy` puro, e o Brier calculado à mão iguala o do `sklearn`
# exactamente. Vem dos dados de entrada. Levantamento completo nas secções 15 e 16 de
# `docs/design/reproducao_corpus_2026-09-09.md`.
#
# Exigir `1e-12` aqui é exigir que os preços de julho voltem, o que não é atingível — e um
# critério que não pode passar deixa de ser porta e passa a ruído que se aprende a ignorar. O
# que esta porta pode garantir, e passa a garantir, são duas coisas: **o número que a tese
# publica** (três casas) e **o envelope medido** da deriva. A partir da cache de preços fixada
# em `data/prices_kb/` esta deriva deixa de crescer.
ENVELOPE = 1e-6  # ~8x a maior deriva observada (1,3e-7 na ROC-AUC), e 1000x abaixo da 3.ª casa


@pytest.mark.parametrize("metrica", ["pr_auc", "roc_auc", "brier"])
def test_metricas_congeladas_reproduzem(frozen, metrica):
    """O valor publicado reproduz-se à casa que a tese cita, e o resíduo fica no envelope medido.

    As duas asserções dizem coisas diferentes de propósito. A primeira é a afirmação da tese —
    se ela falhar, um número impresso deixou de ser verdade. A segunda é a saúde do artefacto:
    se o resíduo crescer para além do envelope, mudou alguma coisa que **não** é a deriva de
    preços já explicada, e isso tem de parar a suite.
    """
    from investigator.triage.model import metrics

    meta, test, p = frozen
    obtido = metrics(test["label"].to_numpy(), p)[metrica]
    congelado = meta["metricas_teste"][metrica]

    assert round(obtido, 3) == round(congelado, 3), (
        f"{metrica}: {obtido:.6f} contra {congelado:.6f} — a tese publica três casas e elas "
        "mudaram. Isto não é a deriva de preços; é um resultado diferente."
    )
    assert obtido == pytest.approx(congelado, abs=ENVELOPE), (
        f"{metrica}: resíduo {abs(obtido - congelado):.2e} acima do envelope {ENVELOPE:.0e}. "
        "A deriva de preços explicada nas secções 15-16 da auditoria fica na ordem de 1e-8; "
        "um resíduo maior é outra coisa e não deve ser aceite."
    )


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
