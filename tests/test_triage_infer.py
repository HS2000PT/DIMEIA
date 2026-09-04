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
    FEATURE_SCHEMA,
    load_context_bundle,
    score_background,
    score_context,
    score_latest,
    score_latest_with_snapshot,
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


def test_score_latest_auditavel_guarda_vetor_data_e_modelo(tmp_path):
    b = _tiny_bundle(tmp_path)
    rng = np.random.default_rng(21)
    idx = pd.bdate_range("2026-01-02", periods=60)
    close = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 60))), index=idx)
    result = score_latest_with_snapshot(b, close, "Company beats earnings", "NVDA")
    assert result is not None
    scored, snapshot = result
    assert scored == score_latest(b, close, "Company beats earnings", "NVDA")
    assert snapshot["schema"] == FEATURE_SCHEMA
    assert snapshot["as_of"] == idx[-1].isoformat()
    assert list(snapshot["values"]) == b["feature_names"]
    assert snapshot["values"]["headline_len"] == len("Company beats earnings")
    assert b["_model_info"]["sha256"] and len(b["_model_info"]["sha256"]) == 64
    assert b["_model_info"]["feature_schema"] == FEATURE_SCHEMA


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


def test_score_latest_falha_aberto_com_precos_em_falta(tmp_path):
    """Regressão de PRODUÇÃO: a 2026-08-04 a fonte de preços devolveu buracos em toda a
    watchlist, as features saíram NaN e o LogisticRegression levantou ValueError 21 vezes num
    dia. O ciclo sobrevivia (o chamador apanha tudo), mas o registo ficava com um stack trace
    onde devia estar "sem dados" — e um dia sem preços é uma condição do mundo, não uma avaria.
    """
    b = _tiny_bundle(tmp_path)
    rng = np.random.default_rng(7)
    close = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 60))))
    assert score_latest(b, close, "abc", "NVDA") is not None      # série sã: pontua
    com_furos = close.copy()
    com_furos.iloc[-5:] = np.nan                                   # o que a fonte devolveu
    assert score_latest(b, com_furos, "abc", "NVDA") is None       # falha ABERTO, não levanta


# ── Nenhum nome da watchlist pode ser pontuado fora da distribuição ────────────
# ⚠️ Regressão: AMD e NFLX estão na watchlist implantada e em nenhum corpus de treino, e o
# `SECTORS.get(t, "")` dava-lhes um one-hot de setor TODO A ZEROS — padrão que não existe em
# nenhuma das 79.753 linhas de treino. Dois dos doze nomes implantados, em silêncio.

def test_todos_os_tickers_da_watchlist_tem_setor_na_inferencia():
    import yaml

    from investigator.triage.infer import deploy_sector
    from scripts.run_alerts import _CONFIG

    cfg = yaml.safe_load(_CONFIG.read_text(encoding="utf-8"))
    tickers = (cfg.get("news") or {}).get("tickers") or []
    assert tickers, "watchlist vazia — o teste deixaria de verificar o que diz verificar"
    sem_setor = [t for t in tickers if not deploy_sector(t)]
    assert not sem_setor, f"pontuados fora da distribuição (one-hot a zeros): {sem_setor}"


def test_o_mapa_do_corpus_continua_a_ganhar_ao_de_implantacao():
    """Controlo no sentido oposto: o mapa canónico não pode ser sobreposto pelo de implantação,
    senão a inferência divergiria do treino para os nomes que ESTIVERAM no treino."""
    from investigator.triage.dataset import SECTORS
    from investigator.triage.infer import deploy_sector

    for t, setor in SECTORS.items():
        assert deploy_sector(t) == setor


def test_barra_final_nan_nao_desliga_a_pontuacao():
    """A barra do dia corrente vem com fecho NaN ate a sessao liquidar; pontuar a ultima
    COMPLETA em vez de desistir.

    Encontrado a 2026-09-04 a verificar producao: 139 linhas `[triagem]` as 23:30 e zero as
    00:07, com a serie a trazer um unico NaN no fim. `ret_event` saia NaN, `score_latest`
    devolvia None, e a triagem deixava de pontuar EM SILENCIO durante parte de cada dia --
    o guard de 2026-08-04 faz falhar aberto, o que evita a excepcao e esconde a paragem.
    """
    import pandas as pd

    from investigator.triage.infer import load_context_bundle, score_latest_with_snapshot

    bundle = load_context_bundle()
    if bundle is None:
        pytest.skip("sem models/triage_context_lr.joblib nesta arvore")
    rng = np.random.default_rng(20260904)
    idx = pd.bdate_range("2026-03-02", periods=80)
    precos = pd.Series(100 * np.exp(np.cumsum(rng.normal(0, 0.01, 80))), index=idx)

    limpa = score_latest_with_snapshot(bundle, precos, "manchete de teste", "NVDA")
    assert limpa is not None, "serie sem NaN tinha de pontuar"

    com_nan = pd.concat([precos, pd.Series([np.nan],
                        index=pd.bdate_range(idx[-1] + pd.Timedelta(days=1), periods=1))])
    resultado = score_latest_with_snapshot(bundle, com_nan, "manchete de teste", "NVDA")
    assert resultado is not None, "a barra NaN final desligou a pontuacao"
    # pontua a ultima COMPLETA, logo o resultado e o mesmo da serie limpa
    assert resultado[0][0] == pytest.approx(limpa[0][0])
    assert resultado[1]["as_of"] == limpa[1]["as_of"]


def test_serie_toda_nan_continua_a_falhar_aberto():
    """Controlo no sentido oposto: sem uma unica barra utilizavel, devolve None e nao rebenta."""
    import pandas as pd

    from investigator.triage.infer import load_context_bundle, score_latest_with_snapshot

    bundle = load_context_bundle()
    if bundle is None:
        pytest.skip("sem models/triage_context_lr.joblib nesta arvore")
    vazia = pd.Series([np.nan] * 5, index=pd.bdate_range("2026-09-01", periods=5))
    assert score_latest_with_snapshot(bundle, vazia, "h", "NVDA") is None
