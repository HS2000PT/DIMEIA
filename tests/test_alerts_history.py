"""Testes do histórico partilhado (investigator/alerts_history.py) — puro, sem rede/git."""

from __future__ import annotations

from investigator.alerts_history import (
    HistoryEntry,
    append_and_trim,
    classify_kind,
    fetch_remote,
    load_jsonl,
    parse_jsonl_lines,
    save_jsonl,
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
