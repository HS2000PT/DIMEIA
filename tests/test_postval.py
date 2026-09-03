"""Testes do loop de pós-validação (M5.5): registo, dedup, rotulagem ao maturar, métricas."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import scripts.run_alerts as runner
from investigator.triage.postval import (
    dedup_decisions,
    label_decision,
    live_report,
    log_decision,
    read_log,
)


# ── registo JSONL ─────────────────────────────────────────────────────────────
def test_log_e_leitura_ida_e_volta(tmp_path):
    log = tmp_path / "sub" / "pred.jsonl"  # a pasta ainda não existe (é criada)
    log_decision(log, news_date="2026-07-01", ticker="NVDA", headline="títúlo çom acentos",
                 prob=0.36, gate=0.4, kept=False)
    log_decision(log, news_date="2026-07-02", ticker="AAPL", headline="h2",
                 prob=None, gate=None, kept=True)
    recs = read_log(log)
    assert len(recs) == 2
    assert recs[0]["ticker"] == "NVDA" and recs[0]["prob"] == 0.36 and not recs[0]["kept"]
    assert recs[0]["headline"] == "títúlo çom acentos"  # UTF-8 intacto
    assert recs[1]["prob"] is None and recs[1]["kept"]
    assert "ts" in recs[0]


def test_log_guarda_snapshot_e_modelo_sem_quebrar_registos_antigos(tmp_path):
    log = tmp_path / "pred.jsonl"
    snapshot = {
        "schema": "triage-context-v1",
        "as_of": "2026-07-01T00:00:00",
        "values": {"vol20": 0.02, "sector_tech": 1.0},
    }
    model = {"artifact": "triage_context_lr.joblib", "sha256": "a" * 64}
    log_decision(
        log, news_date="2026-07-01", ticker="NVDA", headline="h",
        prob=0.7, gate=0.5, kept=True, feature_snapshot=snapshot, model_info=model,
    )
    log_decision(
        log, news_date="2026-07-02", ticker="AAPL", headline="antigo",
        prob=None, gate=None, kept=True,
    )
    recs = read_log(log)
    assert recs[0]["feature_snapshot"] == snapshot
    assert recs[0]["model_info"] == model
    assert "feature_snapshot" not in recs[1] and "model_info" not in recs[1]


def test_leitura_sem_ficheiro_devolve_vazio(tmp_path):
    assert read_log(tmp_path / "nao_existe.jsonl") == []


def test_dedup_mantem_a_primeira_ocorrencia():
    a = {"news_date": "2026-07-01", "ticker": "NVDA", "headline": "h", "prob": 0.3}
    b = {"news_date": "2026-07-01", "ticker": "NVDA", "headline": "h", "prob": 0.9}
    c = {"news_date": "2026-07-02", "ticker": "NVDA", "headline": "h", "prob": 0.5}
    out = dedup_decisions([a, b, c])
    assert out == [a, c]  # b é repetição (mesma chave); a primeira ganha


# ── rotulagem ao maturar (mesma convenção do treino) ──────────────────────────
_DATES = pd.bdate_range("2026-03-02", periods=12)  # 12 dias úteis a partir de uma 2.ª-feira


def _series(vals) -> pd.Series:
    return pd.Series(np.asarray(vals, dtype="float64"), index=_DATES)


def test_rotulo_material_calculado_a_mao():
    # Ticker salta +10% no dia a seguir ao evento (idx 5); mercado fica plano.
    t = [100.0] * 6 + [110.0] * 6
    m = [500.0] * 12
    d = {"news_date": "2026-03-09"}  # = _DATES[5]
    # retorno anormal (d, d+3] = 10% − 0% = 10% ≥ 2% ⇒ material
    assert label_decision(d, _series(t), _series(m), tau=0.02, horizon=3) == 1


def test_rotulo_nao_material_quando_acompanha_o_mercado():
    # Ticker e mercado sobem os mesmos 10% ⇒ retorno anormal ~0 ⇒ não material.
    t = [100.0] * 6 + [110.0] * 6
    m = [500.0] * 6 + [550.0] * 6
    d = {"news_date": "2026-03-09"}
    assert label_decision(d, _series(t), _series(m), tau=0.02, horizon=3) == 0


def test_fim_de_semana_alinha_ao_dia_util_seguinte():
    # Sábado 2026-03-07 → 1.º dia de negociação ≥ data = 2.ª 2026-03-09 (idx 5).
    t = [100.0] * 6 + [110.0] * 6
    m = [500.0] * 12
    d = {"news_date": "2026-03-07"}
    assert label_decision(d, _series(t), _series(m), tau=0.02, horizon=3) == 1


def test_pendente_enquanto_a_janela_nao_fecha():
    t = [100.0] * 12
    m = [500.0] * 12
    d = {"news_date": str(_DATES[10].date())}  # d+3 sai da série ⇒ ainda não maturou
    assert label_decision(d, _series(t), _series(m), tau=0.02, horizon=3) is None


def test_data_fora_da_serie_devolve_none():
    t = [100.0] * 12
    m = [500.0] * 12
    assert label_decision({"news_date": "2027-01-01"}, _series(t), _series(m)) is None


# ── métricas ao vivo (caso feito à mão) ───────────────────────────────────────
def test_live_report_caso_a_mao():
    labeled = [
        {"kept": True, "prob": 0.8, "label": 1},
        {"kept": True, "prob": 0.6, "label": 0},
        {"kept": False, "prob": 0.2, "label": 1},
        {"kept": True, "prob": None, "label": 1},
    ]
    rep = live_report(labeled)
    assert rep["n"] == 4 and rep["n_mantidas"] == 3
    assert rep["precisao_mantidas"] == pytest.approx(2 / 3)
    assert rep["base_rate"] == pytest.approx(3 / 4)
    # o contraste que interessa: mantidas contra suprimidas, e nao contra a taxa-base
    assert rep["n_suprimidas"] == 1 and rep["precisao_suprimidas"] == pytest.approx(1.0)
    assert rep["brier"] == pytest.approx((0.04 + 0.36 + 0.64) / 3)
    assert rep["calibracao"] == [
        (pytest.approx(0.2), pytest.approx(1.0), 1),
        (pytest.approx(0.6), pytest.approx(0.0), 1),
        (pytest.approx(0.8), pytest.approx(1.0), 1),
    ]


def test_live_report_vazio_e_nan_seguro():
    rep = live_report([])
    assert rep["n"] == 0 and rep["precisao_mantidas"] != rep["precisao_mantidas"]  # NaN
    assert rep["n_suprimidas"] == 0
    assert rep["precisao_suprimidas"] != rep["precisao_suprimidas"]  # NaN


# ── registo no runner (nunca pára a varredura) ────────────────────────────────
def test_runner_regista_decisao(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    runner._log_decision_safe("2026-07-01", "NVDA", "h", (0.36, []), 0.4, kept=False)
    recs = read_log(tmp_path / "pred.jsonl")
    assert len(recs) == 1 and recs[0]["prob"] == 0.36 and recs[0]["gate"] == 0.4


def test_runner_propaga_snapshot_e_identidade_do_modelo(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    snap = {"schema": "triage-context-v1", "as_of": "2026-07-01", "values": {}}
    model = {"artifact": "m.joblib", "sha256": "b" * 64}
    runner._log_decision_safe(
        "2026-07-01", "NVDA", "h", (0.36, []), 0.4, kept=False,
        feature_snapshot=snap, model_info=model,
    )
    rec = read_log(tmp_path / "pred.jsonl")[0]
    assert rec["feature_snapshot"] == snap and rec["model_info"] == model


def test_runner_registo_falhado_nao_levanta(monkeypatch, capsys):
    monkeypatch.setattr(runner, "_PRED_LOG", 123)  # caminho inválido de propósito
    runner._log_decision_safe("2026-07-01", "NVDA", "h", None, None, kept=True)
    assert "registo falhou" in capsys.readouterr().out
