"""Testes do runner de alertas — a parte pura (sem rede)."""

from __future__ import annotations

from investigator.anomaly_detector.detector import AnomalyResult
from scripts.run_alerts import build_market_alerts, load_config, scan_market


def _res(is_anomaly: bool, z: float) -> AnomalyResult:
    return AnomalyResult(
        is_anomaly=is_anomaly, z_score=z, last_return=0.05, mean=0.0,
        std=0.01, window=20, threshold=3.0,
    )


def test_build_market_alerts_so_para_anomalias():
    results = [("AAPL", _res(False, 0.5)), ("TSLA", _res(True, 7.6))]
    alerts = build_market_alerts(results)
    assert len(alerts) == 1
    assert "TSLA" in alerts[0]


def test_build_market_alerts_vazio_quando_nao_ha_anomalia():
    assert build_market_alerts([("AAPL", _res(False, 0.1))]) == []


def test_scan_market_desligado_devolve_vazio():
    assert scan_market({"market": {"enabled": False}}) == []


def test_load_config_le_a_watchlist():
    cfg = load_config()
    assert cfg["market"]["tickers"]  # watchlist não vazia
    assert "threshold" in cfg["market"]


def test_news_is_fresh_anti_repeticao():
    from datetime import date

    from scripts.run_alerts import news_is_fresh

    hoje = date(2026, 7, 6)  # segunda
    assert news_is_fresh("2026-07-06", hoje) is True   # de hoje
    assert news_is_fresh("2026-07-04", hoje) is True   # sábado → ainda alerta na segunda
    assert news_is_fresh("2026-07-03", hoje) is False  # 3 dias → já alertou na altura
    assert news_is_fresh("2026-07-07", hoje) is False  # futuro (dados tortos) → não
    assert news_is_fresh("data-invalida", hoje) is False


def test_bar_is_fresh_anti_duplicado():
    from datetime import date

    from scripts.run_alerts import bar_is_fresh

    assert bar_is_fresh(date(2026, 7, 6), date(2026, 7, 6)) is True   # sessão de hoje
    assert bar_is_fresh(date(2026, 7, 3), date(2026, 7, 6)) is False  # feriado: barra de sexta


def test_load_state_reset_diario_preserva_offset(tmp_path):
    from datetime import date

    from scripts.run_alerts import load_state, save_state

    p = tmp_path / "state.json"
    ontem = {"date": "2026-07-05", "alerted_market": ["TSLA"], "alerted_news": ["abc"],
             "bot_offset": 77}
    save_state(ontem, p)
    st = load_state(p, today=date(2026, 7, 6))  # dia novo
    assert st["alerted_market"] == [] and st["alerted_news"] == []  # listas zeradas
    assert st["bot_offset"] == 77  # offset do bot sobrevive à meia-noite
    st2 = load_state(p, today=date(2026, 7, 5))  # mesmo dia
    assert st2["alerted_market"] == ["TSLA"]


def test_filter_new_alerts_nao_repete(tmp_path):
    from datetime import date

    from scripts.run_alerts import filter_new_alerts, load_state

    st = load_state(tmp_path / "none.json", today=date(2026, 7, 6))
    market = [("TSLA", "alerta tsla"), ("NVDA", "alerta nvda")]
    news = [("AAPL", "noticia aapl")]
    primeira = filter_new_alerts(market, news, st)
    assert len(primeira) == 3
    # 2.a corrida do dia: tudo igual -> nada novo; uma manchete nova -> só essa passa
    segunda = filter_new_alerts(market, [("AAPL", "noticia aapl"), ("AAPL", "OUTRA")], st)
    assert segunda == [("AAPL", "OUTRA")]


def test_record_history_safe_regista_o_texto_exato_enviado(tmp_path):
    """A app lê este ficheiro em vez de recalcular — tem de guardar o texto EXATO (sem HTML)."""
    from investigator.alerts_history import load_jsonl
    from scripts.run_alerts import _record_history_safe

    path = tmp_path / "history.jsonl"
    alertas = [
        ("TSLA", "<b>Anomaly detected for TSLA: +7.61 std</b>"),
        ("NVDA", "📰 <b>News alert for NVDA</b>"),
    ]
    _record_history_safe(alertas, "2026-07-08", path=path)
    entries = load_jsonl(path)
    assert [e.kind for e in entries] == ["market", "news"]
    assert entries[0].text == "Anomaly detected for TSLA: +7.61 std"  # HTML removido
    assert all(e.date == "2026-07-08" for e in entries)


def test_record_history_safe_nunca_rebenta_com_caminho_invalido():
    """Fail-open: um caminho impossível de escrever não pode derrubar o runner."""
    from scripts.run_alerts import _record_history_safe

    _record_history_safe([("AAPL", "texto")], "2026-07-08", path="\0/invalido")  # não levanta
