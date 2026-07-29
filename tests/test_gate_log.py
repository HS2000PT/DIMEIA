"""Testes do funil de gates (investigator/gate_log.py) — puro, sem rede."""

from __future__ import annotations

import pytest

from investigator.gate_log import (
    STAGES,
    GateRecord,
    append_jsonl,
    attrition_table,
    load_jsonl,
    per_ticker,
    summarise,
)


def _amostra() -> list[GateRecord]:
    """Reproduz em miniatura o padrão real: TSLA alerta, AAPL nunca alerta."""
    return [
        GateRecord("2026-07-27", "TSLA", "alerted", "Optimus"),
        GateRecord("2026-07-27", "AAPL", "weak_precedent", "melhor sim 0.31 < 0.45"),
        GateRecord("2026-07-28", "AAPL", "weak_precedent", "melhor sim 0.29 < 0.45"),
        GateRecord("2026-07-28", "AAPL", "triage_suppressed", "P=0.41 < 0.50"),
        GateRecord("2026-07-28", "TSLA", "alerted", "earnings"),
        GateRecord("2026-07-28", "JPM", "none_relevant", "12 manchete(s) brutas"),
    ]


def test_etapa_desconhecida_e_rejeitada():
    """Um typo numa etapa corromperia silenciosamente o relatório do funil."""
    with pytest.raises(ValueError, match="etapa desconhecida"):
        GateRecord("2026-07-28", "AAPL", "gate_inventado")


def test_summarise_inclui_todas_as_etapas_mesmo_a_zero():
    """Uma etapa que desaparece do relatório quando não dispara esconde a informação."""
    resumo = summarise(_amostra())
    assert set(resumo) == set(STAGES)
    assert resumo["alerted"] == 2
    assert resumo["weak_precedent"] == 2
    assert resumo["stale"] == 0  # presente, a zero


def test_per_ticker_responde_ao_que_mata_a_aapl():
    porticker = per_ticker(_amostra())
    assert porticker["AAPL"]["weak_precedent"] == 2
    assert porticker["AAPL"]["triage_suppressed"] == 1
    assert porticker["AAPL"]["alerted"] == 0
    assert porticker["TSLA"]["alerted"] == 2


def test_attrition_table_poe_os_tickers_silenciosos_primeiro():
    tabela = attrition_table(_amostra())
    assert tabela[0][0] in {"AAPL", "JPM"}       # os de 0 alertas vêm à cabeça
    assert tabela[-1] == ("TSLA", 2, "-")        # alerta sempre, sem bloqueador
    aapl = next(r for r in tabela if r[0] == "AAPL")
    assert aapl[1] == 0 and aapl[2] == "weak_precedent"  # o gate dominante


def test_roundtrip_jsonl(tmp_path):
    path = tmp_path / "gate.jsonl"
    append_jsonl(_amostra(), path)
    assert load_jsonl(path) == _amostra()


def test_append_acumula_entre_corridas(tmp_path):
    path = tmp_path / "gate.jsonl"
    append_jsonl([GateRecord("2026-07-27", "TSLA", "alerted")], path)
    append_jsonl([GateRecord("2026-07-28", "AAPL", "stale", "mais recente 2026-07-20 > 2d")], path)
    carregado = load_jsonl(path)
    assert [r.ticker for r in carregado] == ["TSLA", "AAPL"]


def test_append_apara_ao_limite(tmp_path):
    path = tmp_path / "gate.jsonl"
    append_jsonl([GateRecord("2026-07-27", f"T{i}", "alerted") for i in range(5)],
                 path, max_entries=3)
    assert [r.ticker for r in load_jsonl(path)] == ["T2", "T3", "T4"]


def test_append_vazio_nao_cria_ficheiro(tmp_path):
    path = tmp_path / "gate.jsonl"
    append_jsonl([], path)
    assert not path.exists()


def test_load_ignora_linhas_invalidas_e_etapas_desconhecidas(tmp_path):
    path = tmp_path / "gate.jsonl"
    path.write_text(
        '{"date":"2026-07-28","ticker":"AAPL","stage":"stale","detail":"x"}\n'
        "nao-json\n"
        '{"date":"2026-07-28","ticker":"X","stage":"etapa_do_futuro"}\n',
        encoding="utf-8",
    )
    carregado = load_jsonl(path)
    assert len(carregado) == 1 and carregado[0].ticker == "AAPL"


def test_load_ficheiro_em_falta_devolve_vazio(tmp_path):
    assert load_jsonl(tmp_path / "nao_existe.jsonl") == []
