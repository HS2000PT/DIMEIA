"""Testes do M5: inferência leve (bundle só-contexto), gate do runner e linha no explainer."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from investigator.explanation_engine.explainer import explain_news_impact
from investigator.historical_kb.record import NewsRecord
from investigator.triage.explain import materiality_line
from investigator.triage.features import context_block
from investigator.triage.infer import (
    DEFAULT_BUNDLE,
    load_context_bundle,
    score_background,
    score_context,
    score_latest,
)
from investigator.triage.model import fit_platt, make_model, save_bundle
from scripts.run_alerts import apply_materiality


def _tiny_bundle(tmp_path) -> dict:
    """Treina um bundle só-contexto minúsculo, separável por vol20 por construção."""
    rng = np.random.default_rng(0)
    n = 300
    df = pd.DataFrame({
        "vol20": rng.uniform(0.005, 0.05, n),
        "mom5": rng.normal(0, 0.03, n),
        "ret_event": rng.normal(0, 0.02, n),
        "headline_len": rng.integers(20, 120, n).astype("float64"),
        "sector": rng.choice(["tech", "banking"], n),
    })
    x, names = context_block(df)
    y = (df["vol20"].to_numpy() > 0.025).astype(int)
    model = make_model("context", seed=0)
    model.fit(x, y)
    cal = fit_platt(model.predict_proba(x)[:, 1], y, seed=0)
    path = tmp_path / "triage_context_lr.joblib"
    save_bundle(path, model, cal, names, {"modelo": "context"})
    return load_context_bundle(path)


# ── infer.py ──────────────────────────────────────────────────────────────────
def test_load_ausente_devolve_none(tmp_path):
    assert load_context_bundle(tmp_path / "nao_existe.joblib") is None


def test_score_context_prob_valida_e_monotona_na_vol(tmp_path):
    b = _tiny_bundle(tmp_path)
    hi, contribs = score_context(b, 0.045, 0.0, 0.0, "abc", "NVDA")
    lo, _ = score_context(b, 0.006, 0.0, 0.0, "abc", "NVDA")
    assert 0.0 <= lo <= 1.0 and 0.0 <= hi <= 1.0
    assert hi > lo  # vol20 separa as classes por construção
    nomes = [n for n, _ in contribs]
    assert "recent volatility (20d)" in nomes and "sector" in nomes


def test_ticker_desconhecido_pontua_sem_setor(tmp_path):
    b = _tiny_bundle(tmp_path)
    prob, _ = score_context(b, 0.02, 0.0, 0.0, "abc", "ZZZZ")  # fora do mapa de setores
    assert 0.0 <= prob <= 1.0


def test_bundle_incompativel_levanta_erro(tmp_path):
    b = _tiny_bundle(tmp_path)
    b["feature_names"] = ["errado"]
    with pytest.raises(ValueError, match="retreinar"):
        score_context(b, 0.02, 0.0, 0.0, "abc", "NVDA")


def test_score_latest_fail_open_sem_historico(tmp_path):
    b = _tiny_bundle(tmp_path)
    assert score_latest(b, pd.Series(np.linspace(100, 101, 10)), "abc", "NVDA") is None
    rng = np.random.default_rng(2)
    longa = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 60))))
    assert score_latest(b, longa, "abc", "NVDA") is not None


def test_score_background_pontua_sem_manchete(tmp_path):
    """O 'risco de fundo' (painel ao vivo) pontua qualquer dia, mesmo sem notícia nenhuma."""
    b = _tiny_bundle(tmp_path)
    rng = np.random.default_rng(3)
    close = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 60))))
    scored = score_background(b, close, "NVDA")
    assert scored is not None
    prob, contribs = scored
    assert 0.0 <= prob <= 1.0
    # Mesma matemática que score_latest com título vazio (headline_len=0) — não é magia à parte.
    assert scored == score_latest(b, close, "", "NVDA")


def test_bundle_do_repo_carrega_na_stack_leve():
    """Regressão: o bundle COMMITADO tem de carregar e pontuar sem SBERT (nuvem/runner)."""
    b = load_context_bundle(DEFAULT_BUNDLE)
    if b is None:
        pytest.skip("models/triage_context_lr.joblib ainda não treinado")
    prob, contribs = score_context(b, 0.02, 0.01, -0.03, "Company beats earnings", "AAPL")
    assert 0.0 <= prob <= 1.0 and contribs


# ── gate do runner (puro) ─────────────────────────────────────────────────────
def test_apply_materiality_fail_open_sem_score():
    assert apply_materiality("alerta", None, gate=0.5) == "alerta"


def test_apply_materiality_suprime_abaixo_do_gate():
    scored = (0.2, [("recent volatility (20d)", 0.4)])
    assert apply_materiality("alerta", scored, gate=0.5) is None


def test_apply_materiality_anexa_linha_acima_do_gate():
    scored = (0.8, [("recent volatility (20d)", 0.4), ("sector", -0.1)])
    out = apply_materiality("alerta", scored, gate=0.5)
    assert out is not None and out.startswith("alerta\n")
    assert "80%" in out and "not a price forecast" in out


# ── linha no explainer (off por defeito) ──────────────────────────────────────
def _precedentes() -> list[tuple[NewsRecord, float]]:
    return [
        (NewsRecord(date="2023-05-25", ticker="NVDA", headline="AI chips demand soars",
                    impacts={"1": 0.02, "3": 0.04, "5": 0.05}), 0.91),
    ]


def test_explainer_sem_materialidade_e_identico():
    a = explain_news_impact("NVDA", "t", _precedentes(), horizon=3)
    b = explain_news_impact("NVDA", "t", _precedentes(), horizon=3, materiality=None)
    assert a == b and "Materiality estimate" not in a


def test_explainer_com_materialidade_inclui_linha_nos_dois_ramos():
    linha = materiality_line(0.7, [("recent volatility (20d)", 0.5)])
    com = explain_news_impact("NVDA", "t", _precedentes(), horizon=3, materiality=linha)
    sem_prec = explain_news_impact("NVDA", "t", [], horizon=3, materiality=linha)
    assert "Materiality estimate (learned triage)" in com
    assert "Materiality estimate (learned triage)" in sem_prec


def test_linha_de_materialidade_nao_afirma_que_nao_e_previsao():
    """A linha DÁ uma probabilidade sobre os próximos dias — chamar-lhe "não é previsão"
    seria falso, e o critério H2 do painel bane este número precisamente por ser sobre o
    futuro. O que a linha pode afirmar, e afirma, é que não prevê a DIREÇÃO."""
    linha = materiality_line(0.56, [("recent volatility (20d)", 0.4)])
    assert "not a forecast" not in linha
    assert "EITHER direction" in linha
    assert "not a price forecast" in linha
