"""Testes do histórico partilhado (investigator/alerts_history.py) — puro, sem rede/git."""

from __future__ import annotations

import json
from datetime import UTC

from investigator.alerts_history import (
    HistoryEntry,
    append_and_trim,
    classify_kind,
    fetch_remote,
    load_jsonl,
    parse_jsonl_lines,
    save_jsonl,
    utc_stamp,
)


def test_classify_kind_deteta_mercado_e_noticia():
    assert classify_kind("🔺 Anomaly detected for AAPL: +2.10% today") == "market"
    assert classify_kind("🔻 TSLA (Tesla) · -8.40% today") == "market"   # setas ambas
    assert classify_kind("📰 News alert for NVDA") == "news"
    assert classify_kind("📊 Daily close summary\n🔺 AAPL ...") == "summary"
    assert classify_kind("🔔 Market open — watchlist snapshot") == "open"   # nota de abertura
    # bug latente corrigido: intradiário sem "Anomaly detected for" já não vai para "news"
    assert classify_kind("Unusual intraday move for TSLA") == "market"


def test_append_and_trim_apara_ao_limite_mantendo_recentes():
    existing = [HistoryEntry("2026-07-01", "AAPL", "market", "a"),
                HistoryEntry("2026-07-02", "AAPL", "market", "b")]
    new = [HistoryEntry("2026-07-03", "AAPL", "news", "c")]
    out = append_and_trim(existing, new, max_entries=2)
    assert [e.text for e in out] == ["b", "c"]  # o mais antigo cai fora


def test_append_and_trim_sem_limite_mantem_tudo():
    existing = [HistoryEntry("2026-07-01", "AAPL", "market", "a")]
    new = [HistoryEntry("2026-07-02", "AAPL", "news", "b")]
    out = append_and_trim(existing, new, max_entries=0)
    assert len(out) == 2


def test_save_e_load_roundtrip(tmp_path):
    path = tmp_path / "history.jsonl"
    entries = [
        HistoryEntry("2026-07-01", "TSLA", "market", "z=+7.61"),
        HistoryEntry("2026-07-02", "NVDA", "news", "AI demand"),
    ]
    save_jsonl(entries, path)
    loaded = load_jsonl(path)
    assert loaded == entries


def test_load_jsonl_ficheiro_em_falta_devolve_vazio(tmp_path):
    assert load_jsonl(tmp_path / "nao_existe.jsonl") == []


def test_load_jsonl_ignora_linhas_invalidas(tmp_path):
    path = tmp_path / "history.jsonl"
    path.write_text('{"date":"2026-07-01","ticker":"AAPL","kind":"market","text":"ok"}\n'
                     'linha invalida nao-json\n'
                     '{"campo_errado": true}\n', encoding="utf-8")
    loaded = load_jsonl(path)
    assert len(loaded) == 1 and loaded[0].text == "ok"


def test_parse_jsonl_lines_e_load_jsonl_sao_consistentes(tmp_path):
    lines = ['{"date":"2026-07-01","ticker":"NVDA","kind":"news","text":"AI demand"}']
    assert parse_jsonl_lines(lines) == [
        HistoryEntry("2026-07-01", "NVDA", "news", "AI demand")
    ]


def test_fetch_remote_falha_devolve_lista_vazia(monkeypatch):
    """Fail-open: qualquer erro de rede/parsing devolve [] em vez de levantar."""
    import requests

    def _rebenta(*a, **k):
        raise requests.exceptions.ConnectionError("sem rede")

    monkeypatch.setattr(requests, "get", _rebenta)
    assert fetch_remote("https://example.invalid/history.jsonl") == []


def test_fetch_remote_sucesso_faz_parse(monkeypatch):
    import requests

    class _FakeResp:
        text = '{"date":"2026-07-08","ticker":"TSLA","kind":"market","text":"z=+2.1"}\n'

        def raise_for_status(self):
            return None

    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResp())
    entries = fetch_remote("https://example.invalid/history.jsonl")
    assert entries == [HistoryEntry("2026-07-08", "TSLA", "market", "z=+2.1")]


# ── Instrumentação de tempo (2026-07-29) ──────────────────────────────────────
def test_entradas_antigas_sem_carimbos_continuam_a_ler_se():
    """Retrocompatibilidade: o histórico já publicado não tem os campos novos."""
    linha = '{"date":"2026-07-27","ticker":"AMD","kind":"market","text":"-8.64%","key":""}'
    (entry,) = parse_jsonl_lines([linha])
    assert entry.ticker == "AMD"
    assert entry.event_at == "" and entry.detected_at == "" and entry.sent_at == ""
    assert entry.latency_seconds() is None  # sem carimbos não se inventa latência


def test_campos_desconhecidos_sao_descartados_em_vez_de_rebentar():
    """Sem isto, um leitor ANTIGO em produção deixaria de ver os alertas novos em silêncio."""
    linha = ('{"date":"2026-07-29","ticker":"NVDA","kind":"news","text":"x",'
             '"campo_do_futuro":123,"outro":"abc"}')
    (entry,) = parse_jsonl_lines([linha])
    assert entry.ticker == "NVDA" and entry.text == "x"


def test_latencia_medida_do_facto_ate_a_entrega():
    e = HistoryEntry(
        "2026-07-29", "TSLA", "news", "x",
        event_at="2026-07-29T13:00:00Z",
        detected_at="2026-07-29T13:41:00Z",
        sent_at="2026-07-29T13:41:02Z",
    )
    assert e.latency_seconds() == 2462.0   # publicação → entrega (o que o utilizador sente)
    assert e.pipeline_seconds() == 2.0     # deteção → entrega (o nosso lado)


def test_latencia_ignora_carimbos_ilegiveis():
    e = HistoryEntry("2026-07-29", "TSLA", "news", "x",
                     event_at="ontem à tarde", sent_at="2026-07-29T13:41:02Z")
    assert e.latency_seconds() is None


def test_carimbos_vazios_nao_sao_escritos_no_ficheiro(tmp_path):
    """O JSONL (e a branch git) não devem encher de campos vazios em cada linha."""
    path = tmp_path / "h.jsonl"
    save_jsonl([HistoryEntry("2026-07-01", "TSLA", "market", "z=+7.61")], path)
    payload = json.loads(path.read_text(encoding="utf-8").strip())
    assert "event_at" not in payload and "sent_at" not in payload
    assert payload["date"] == "2026-07-01"


def test_roundtrip_preserva_carimbos(tmp_path):
    path = tmp_path / "h.jsonl"
    entries = [HistoryEntry("2026-07-29", "AMD", "market", "-8.9%",
                            detected_at="2026-07-29T20:05:00Z",
                            sent_at="2026-07-29T20:05:01Z",
                            price_source="tiingo")]
    save_jsonl(entries, path)
    assert load_jsonl(path) == entries


def test_utc_stamp_formato_iso_com_z():
    from datetime import datetime

    fixo = datetime(2026, 7, 29, 14, 32, 7, tzinfo=UTC)
    assert utc_stamp(fixo) == "2026-07-29T14:32:07Z"
