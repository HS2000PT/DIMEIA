"""Testes do modelo de triagem: treino determinístico, calibração, métricas, XAI, persistência."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.historical_kb.embedder import HashingEmbedder
from src.triage.explain import lr_group_contributions, materiality_line
from src.triage.features import CONTEXT_COLS, assemble
from src.triage.model import (
    fit_platt,
    load_bundle,
    make_model,
    metrics,
    precision_at_daily_budget,
    save_bundle,
    scores_of,
)


def _df_sintetico(n: int = 240, seed: int = 7) -> pd.DataFrame:
    """Dataset sintético separável: vol alta + palavra 'earnings' ⇒ material."""
    rng = np.random.default_rng(seed)
    label = rng.integers(0, 2, size=n)
    vol = np.where(label == 1, 0.030, 0.010) + rng.normal(0, 0.002, n)
    head = np.where(label == 1, "earnings shock guidance cut", "routine product update")
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=n, freq="D").strftime("%Y-%m-%d"),
        "sector": rng.choice(["tech", "banking"], size=n),
        "headline": head,
        "headline_len": [len(h) for h in head],
        "vol20": vol,
        "mom5": rng.normal(0, 0.01, n),
        "ret_event": rng.normal(0, 0.01, n),
        "label": label,
    })


def test_treino_determinista_e_separa_o_sintetico():
    df = _df_sintetico()
    blocks = assemble(df, HashingEmbedder(dim=32))
    x, _ = blocks["full"]
    y = df["label"].to_numpy()
    m1 = make_model("full", seed=42).fit(x, y)
    m2 = make_model("full", seed=42).fit(x, y)
    s1, s2 = scores_of(m1, x), scores_of(m2, x)
    assert np.allclose(s1, s2)                       # mesma seed ⇒ mesmos scores
    assert metrics(y, s1)["pr_auc"] > 0.95           # sintético separável ⇒ quase perfeito


def test_platt_e_monotona_e_limitada():
    cal = fit_platt(np.array([0.1, 0.4, 0.6, 0.9]), np.array([0, 0, 1, 1]))
    p = cal(np.array([0.0, 0.5, 1.0]))
    assert np.all((0 <= p) & (p <= 1))
    assert p[0] < p[1] < p[2]                        # monótona no score


def test_precisao_com_orcamento_diario_caso_a_mao():
    # 2 dias, orçamento 1: seleciona o melhor score de cada dia → labels [1, 0] → precisão 0.5.
    dates = np.array(["d1", "d1", "d2", "d2"])
    y = np.array([1, 0, 0, 1])
    scores = np.array([0.9, 0.2, 0.8, 0.3])
    assert precision_at_daily_budget(dates, y, scores, budget=1) == pytest.approx(0.5)


def test_contribuicoes_agrupadas_e_linha_de_materialidade():
    df = _df_sintetico(80)
    blocks = assemble(df, HashingEmbedder(dim=16))
    x, names = blocks["full"]
    model = make_model("full", seed=0).fit(x, df["label"].to_numpy())
    contribs = lr_group_contributions(model, x[0], names)
    grupos = {g for g, _ in contribs}
    assert "headline content" in grupos and "sector" in grupos
    assert any(g.startswith("recent volatility") for g in grupos)
    linha = materiality_line(0.73, contribs)
    assert "73%" in linha and "not a forecast" in linha


def test_bundle_roundtrip(tmp_path):
    df = _df_sintetico(60)
    blocks = assemble(df, HashingEmbedder(dim=16))
    x, names = blocks["full"]
    y = df["label"].to_numpy()
    model = make_model("full", seed=1).fit(x, y)
    cal = fit_platt(scores_of(model, x), y)
    p = tmp_path / "b.joblib"
    save_bundle(p, model, cal, names, {"nota": "teste"})
    b = load_bundle(p)
    assert b["feature_names"] == names
    assert np.allclose(b["calibrator"](scores_of(b["model"], x)), cal(scores_of(model, x)))
    assert p.with_suffix(".json").exists()


def test_bloco_de_contexto_tem_ordem_fixa():
    df = _df_sintetico(10)
    blocks = assemble(df, HashingEmbedder(dim=8))
    _, names = blocks["context"]
    assert names[: len(CONTEXT_COLS)] == CONTEXT_COLS  # vol20 primeiro (usado pelo modelo 'vol')