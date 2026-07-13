"""Testes da deteção intradiária (V3) — puro, sem rede."""

from __future__ import annotations

import numpy as np
import pytest

from investigator.anomaly_detector.detector import detect_intraday
from investigator.explanation_engine.explainer import explain_intraday, plain_text


def _retornos_calmos(n: int = 30) -> list[float]:
    rng = np.random.default_rng(7)
    return list(rng.normal(0.0, 0.01, n))  # ~1%/dia de desvio


def test_movimento_em_curso_anomalo_dispara():
    res = detect_intraday(-0.048, _retornos_calmos(), window=20, threshold=2.0)
    assert res.is_anomaly and res.z_score < -2.0
    assert res.last_return == -0.048


def test_movimento_normal_nao_dispara():
    res = detect_intraday(0.004, _retornos_calmos(), window=20, threshold=2.0)
    assert not res.is_anomaly


def test_norma_usa_so_dias_completos_sem_lookahead():
    """A norma vem dos últimos `window` retornos DIÁRIOS fornecidos — o running return de
    hoje nunca entra na média/desvio (seria contaminar a norma com o próprio avaliado)."""
    base = [0.0] * 19 + [0.01]
    res = detect_intraday(0.10, base, window=20, threshold=2.0)
    assert abs(res.mean - 0.0005) < 1e-12  # média dos 20 dias completos, sem o 0.10


def test_serie_curta_levanta():
    with pytest.raises(ValueError, match="pelo menos 20"):
        detect_intraday(0.05, [0.01] * 5, window=20)


def test_explicacao_intradiaria_e_fiel_e_diz_em_curso():
    res = detect_intraday(-0.048, _retornos_calmos(), window=20, threshold=2.0)
    texto = plain_text(explain_intraday("TSLA", res))
    # UX 2026-07-12: o header ganhou o nome da empresa ("(Tesla)") — leigos não sabem símbolos
    assert "Unusual intraday move for TSLA (Tesla): -4.80% so far today" in texto
    assert "the session is not over" in texto
    assert f"z-score: {res.z_score:+.2f}" in texto  # fidelidade: o número exato
    assert "not advice" in texto


def test_collect_intraday_desligado_devolve_vazio():
    from scripts.run_alerts import collect_intraday_results

    cfg_off = {"market": {"enabled": True, "intraday": {"enabled": False}}}
    assert collect_intraday_results(cfg_off) == []
    assert collect_intraday_results({"market": {"enabled": False}}) == []


def test_build_intraday_alerts_so_para_anomalias():
    from investigator.anomaly_detector.detector import AnomalyResult
    from scripts.run_alerts import build_intraday_alerts

    calmo = AnomalyResult(is_anomaly=False, z_score=0.4, last_return=0.002,
                          mean=0.0, std=0.01, window=20, threshold=1.5)
    agitado = AnomalyResult(is_anomaly=True, z_score=-3.2, last_return=-0.048,
                            mean=0.0, std=0.015, window=20, threshold=1.5)
    alerts = build_intraday_alerts([("AAPL", calmo), ("TSLA", agitado)])
    assert len(alerts) == 1
    assert alerts[0][0] == "TSLA"
    assert "Unusual intraday move" in alerts[0][1]


def test_janela_de_sessao_us():
    """Fora da sessão, a cotação é estagnada — o intradiário tem de saltar (bug real
    apanhado em teste ao vivo num sábado: re-alertaria o movimento de sexta)."""
    from datetime import datetime

    from scripts.run_alerts import is_us_market_session

    assert is_us_market_session(datetime(2026, 7, 10, 15, 0))       # sexta, 15:00 UTC
    assert not is_us_market_session(datetime(2026, 7, 11, 15, 0))   # sábado
    assert not is_us_market_session(datetime(2026, 7, 10, 9, 0))    # sexta, pré-mercado
    assert not is_us_market_session(datetime(2026, 7, 10, 22, 30))  # sexta, pós-fecho
    assert is_us_market_session(datetime(2026, 7, 10, 21, 15))      # fecho de inverno
