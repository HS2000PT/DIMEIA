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


def test_append_retem_por_dias_e_nao_por_linhas(tmp_path):
    """A retenção conta-se em DIAS, senão muda de significado quando a cadência muda.

    Regressão do defeito medido a 2026-08-15: o tecto de 5000 linhas foi dimensionado para
    um agendador de 30 em 30 minutos e, com o ciclo de 60 segundos, passou a guardar menos
    de um dia — esvaziando a vista que existe para tornar o silêncio inspeccionável.
    """
    path = tmp_path / "gate.jsonl"
    for dia in range(1, 11):  # 10 dias, 3 registos cada
        append_jsonl([GateRecord(f"2026-08-{dia:02d}", f"T{i}", "alerted") for i in range(3)],
                     path, max_days=3)
    dias = {r.date for r in load_jsonl(path)}
    assert dias == {"2026-08-08", "2026-08-09", "2026-08-10"}


def test_um_dia_movimentado_nao_apaga_os_dias_anteriores(tmp_path):
    """É este o caso que o tecto de linhas fazia mal: um dia cheio expulsava os outros.

    O teste compara os DOIS regimes sobre exatamente os mesmos dados, senão não distingue
    a correcção de um limite generoso.
    """
    dados = ([GateRecord("2026-08-01", "AAPL", "alerted")],
             [GateRecord("2026-08-02", f"T{i}", "weak_precedent") for i in range(400)])

    # regime antigo: só tecto de linhas, dimensionado para a cadência antiga
    antigo = tmp_path / "antigo.jsonl"
    for lote in dados:
        append_jsonl(lote, antigo, max_days=0, max_entries=100)
    assert "2026-08-01" not in {r.date for r in load_jsonl(antigo)}, (
        "o teste não discrimina: o dia calmo devia morrer no regime antigo")

    # regime novo: retenção por dias
    novo = tmp_path / "novo.jsonl"
    for lote in dados:
        append_jsonl(lote, novo, max_days=3, max_entries=100000)
    assert "2026-08-01" in {r.date for r in load_jsonl(novo)}, (
        "o dia calmo tem de sobreviver a um dia movimentado")


def test_tecto_de_linhas_continua_a_ser_rede_de_seguranca(tmp_path):
    """Mesmo dentro da janela de dias, o ficheiro não pode crescer sem limite: é publicado
    a cada ciclo."""
    path = tmp_path / "gate.jsonl"
    append_jsonl([GateRecord("2026-08-01", f"T{i}", "alerted") for i in range(50)],
                 path, max_days=7, max_entries=10)
    assert len(load_jsonl(path)) == 10


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
