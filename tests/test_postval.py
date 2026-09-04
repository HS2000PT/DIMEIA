"""Testes do loop de pós-validação (M5.5): registo, dedup, rotulagem ao maturar, métricas."""

from __future__ import annotations

import json
from datetime import date

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


# --- R1: o registo passa a receber a população real de candidatas ------------------------


class _Item:
    """Manchete mínima com a forma que o varrimento usa (`date`, `headline`)."""

    def __init__(self, date: str, headline: str) -> None:
        self.date = date
        self.headline = headline


def test_registo_nao_repete_a_mesma_manchete(tmp_path, monkeypatch):
    """O varrimento repontua de 60 em 60 s; o registo tem de guardar UMA linha por título.

    Sem a guarda a mediana era de 78 linhas por título distinto (máximo 1406), e o peso de
    cada empresa passava a ser a frequência com que o sistema a republica.
    """
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    monkeypatch.setattr(runner, "_DECISOES_VISTAS", None)
    for _ in range(5):
        runner._log_decision_safe("2026-09-04", "NVDA", "mesma manchete",
                                  (0.36, []), 0.4, kept=False, stage="not_latest")
    linhas = (tmp_path / "pred.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 1


def test_registo_distingue_manchetes_diferentes(tmp_path, monkeypatch):
    """Controlo no sentido oposto: a guarda não pode engolir títulos genuinamente distintos."""
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    monkeypatch.setattr(runner, "_DECISOES_VISTAS", None)
    for h in ("primeira", "segunda", "terceira"):
        runner._log_decision_safe("2026-09-04", "NVDA", h, None, None, kept=False)
    linhas = (tmp_path / "pred.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 3


def test_stage_vai_para_o_registo(tmp_path, monkeypatch):
    """`kept` deixou de discriminar (100% verdadeiro); a porta é a variável que ficou."""
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    monkeypatch.setattr(runner, "_DECISOES_VISTAS", None)
    runner._log_decision_safe("2026-09-04", "NVDA", "h", None, None,
                              kept=False, stage="weak_precedent")
    rec = json.loads((tmp_path / "pred.jsonl").read_text(encoding="utf-8").strip())
    assert rec["stage"] == "weak_precedent"


def test_registo_sem_stage_mantem_o_formato_antigo(tmp_path, monkeypatch):
    """Retrocompatibilidade: sem `stage` o registo não ganha o campo."""
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    monkeypatch.setattr(runner, "_DECISOES_VISTAS", None)
    runner._log_decision_safe("2026-09-04", "NVDA", "h", None, None, kept=True)
    rec = json.loads((tmp_path / "pred.jsonl").read_text(encoding="utf-8").strip())
    assert "stage" not in rec


def test_candidatas_nao_escolhidas_ficam_registadas(tmp_path, monkeypatch):
    """R1: as manchetes que o ciclo NÃO escolhe entram no registo, com a porta onde morreram.

    Antes disto o conjunto de retreino era um sobrevivente das portas — o varrimento pontua
    uma manchete por empresa por ciclo — e um candidato treinado nele herdava o enviesamento.
    """
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    monkeypatch.setattr(runner, "_DECISOES_VISTAS", None)
    hoje = date(2026, 9, 4)
    latest = _Item("2026-09-04", "a escolhida")
    outras = [_Item("2026-09-04", "outra de hoje"), _Item("2026-08-01", "uma velha")]
    runner._registar_candidatas_safe([*outras, latest], latest, "NVDA",
                                     None, 0.4, 2, hoje)
    recs = [json.loads(x) for x in
            (tmp_path / "pred.jsonl").read_text(encoding="utf-8").strip().splitlines()]
    etapas = {r["headline"]: r["stage"] for r in recs}
    # a escolhida é registada a jusante, com a porta REAL onde acabar — não aqui
    assert "a escolhida" not in etapas
    assert etapas["outra de hoje"] == "not_latest"
    assert etapas["uma velha"] == "stale"


def test_candidatas_sem_modelo_nao_levanta(tmp_path, monkeypatch):
    """Fail-open: sem bundle regista na mesma, sem probabilidade e sem travar o alerta."""
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    monkeypatch.setattr(runner, "_DECISOES_VISTAS", None)
    latest = _Item("2026-09-04", "escolhida")
    runner._registar_candidatas_safe([_Item("2026-09-04", "outra"), latest], latest,
                                     "NVDA", None, None, 2, date(2026, 9, 4))
    rec = json.loads((tmp_path / "pred.jsonl").read_text(encoding="utf-8").strip())
    assert rec["prob"] is None and rec["stage"] == "not_latest"


def test_candidatas_uma_so_manchete_nao_escreve_nada(tmp_path, monkeypatch):
    """Se a única relevante é a escolhida, não há candidata extra a registar."""
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    monkeypatch.setattr(runner, "_DECISOES_VISTAS", None)
    latest = _Item("2026-09-04", "unica")
    runner._registar_candidatas_safe([latest], latest, "NVDA", None, None, 2,
                                     date(2026, 9, 4))
    assert not (tmp_path / "pred.jsonl").exists()


def test_scan_news_busca_precos_uma_so_vez_por_empresa(monkeypatch, tmp_path):
    """Uma busca de precos por empresa por varrimento. Duas apagam a pontuacao em silencio.

    Regressao de 2026-09-04, encontrada SO em producao. O registo das candidatas (decisao R1)
    ia buscar a serie por sua conta, o que somava uma segunda chamada por empresa e por ciclo.
    O yfinance passou a devolver 14 dias em vez do historico completo, `vol20` saiu NaN, e a
    triagem deixou de pontuar no sistema inteiro: 139 linhas `[triagem]` antes da implantacao,
    zero depois. Nenhum teste falhou e o `exit code` foi zero.
    """
    chamadas: list[str] = []

    def _falso_hist(ticker, cache):
        chamadas.append(ticker)
        if ticker not in cache:
            cache[ticker] = {"Close": pd.Series([1.0, 2.0, 3.0])}
        return cache[ticker]

    monkeypatch.setattr(runner, "_hist_cached", _falso_hist)
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    monkeypatch.setattr(runner, "_DECISOES_VISTAS", None)

    # o helper NAO pode ir buscar precos: recebe-os ja obtidos
    cache: dict = {}
    close = _falso_hist("NVDA", cache)["Close"]
    latest = _Item("2026-09-04", "escolhida")
    runner._registar_candidatas_safe(
        [_Item("2026-09-04", "a"), _Item("2026-09-04", "b"), latest],
        latest, "NVDA", None, 0.4, 2, date(2026, 9, 4), close=close,
    )
    assert chamadas == ["NVDA"], (
        f"esperava UMA busca de precos, houve {len(chamadas)}: {chamadas}"
    )


def test_linha_nua_pode_ser_promovida_uma_vez(tmp_path, monkeypatch):
    """Um titulo registado sem snapshot aceita UMA reescrita, e so se ela trouxer snapshot.

    A 2026-09-04 a barra do dia por liquidar desligou a pontuacao e 678 titulos entraram no
    registo sem `feature_snapshot`. Sem esta promocao a guarda de dedup prendia-os nesse estado
    para sempre, e sao 678 titulos que o retreino nunca poderia usar.
    """
    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    monkeypatch.setattr(runner, "_DECISOES_VISTAS", None)
    # 1) linha nua (a pontuacao falhou)
    runner._log_decision_safe("2026-09-04", "NVDA", "h", None, None, kept=False, stage="not_latest")
    # 2) outra tentativa sem snapshot: nao acrescenta nada
    runner._log_decision_safe("2026-09-04", "NVDA", "h", None, None, kept=False, stage="not_latest")
    linhas = (tmp_path / "pred.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 1, "linha nua repetida"
    # 3) a pontuacao recupera: promove
    runner._log_decision_safe("2026-09-04", "NVDA", "h", (0.42, []), 0.5, kept=False,
                              feature_snapshot={"schema": "triage-context-v1", "values": {}},
                              stage="not_latest")
    linhas = (tmp_path / "pred.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 2, "a promocao nao foi escrita"
    # 4) e nao volta a escrever depois de completa
    runner._log_decision_safe("2026-09-04", "NVDA", "h", (0.42, []), 0.5, kept=False,
                              feature_snapshot={"schema": "triage-context-v1", "values": {}},
                              stage="not_latest")
    linhas = (tmp_path / "pred.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(linhas) == 2, "escreveu depois de ja estar completa"
    assert json.loads(linhas[-1])["feature_snapshot"]["schema"] == "triage-context-v1"


def test_candidata_velha_nao_e_pontuada(tmp_path, monkeypatch):
    """Uma manchete velha nao pode receber snapshot: seria lookahead.

    `score_latest` usa a ULTIMA barra disponivel, logo uma manchete de ha dias seria descrita
    por um mercado que ja viu o desfecho que o rotulo mede em (data, data+3]. Medido a
    2026-09-04 no registo real: as `stale` tinham as_of de +1 a +107 dias sobre a data da
    noticia, enquanto as `not_latest` ficavam em -1 a 0. Eram 430 linhas que pareciam material
    de treino e nao eram.
    """
    import pandas as pd

    monkeypatch.setattr(runner, "_PRED_LOG", tmp_path / "pred.jsonl")
    monkeypatch.setattr(runner, "_DECISOES_VISTAS", None)
    bundle = {"_model_info": {"artifact": "x"}}
    close = pd.Series([1.0] * 60, index=pd.bdate_range("2026-06-01", periods=60))

    chamadas = []

    def _falso(*a, **k):
        chamadas.append(1)
        return (0.5, []), {"schema": "s", "as_of": "2026-09-04", "values": {}}

    import investigator.triage.infer as inf
    monkeypatch.setattr(inf, "score_latest_with_snapshot", _falso)

    latest = _Item("2026-09-04", "a escolhida")
    velha = _Item("2026-08-01", "manchete de ha um mes")
    fresca = _Item("2026-09-04", "outra de hoje")
    runner._registar_candidatas_safe([velha, fresca, latest], latest, "NVDA",
                                     bundle, 0.5, 2, date(2026, 9, 4), close=close)

    recs = [json.loads(x) for x in
            (tmp_path / "pred.jsonl").read_text(encoding="utf-8").strip().splitlines()]
    por_etapa = {r["stage"]: r for r in recs}
    assert "feature_snapshot" not in por_etapa["stale"], "a velha foi pontuada"
    assert por_etapa["stale"]["prob"] is None
    assert "feature_snapshot" in por_etapa["not_latest"], "a fresca deixou de ser pontuada"
    assert len(chamadas) == 1, f"pontuou {len(chamadas)} vezes; so a fresca devia"
