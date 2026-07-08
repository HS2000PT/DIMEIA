"""Testes do histórico partilhado (investigator/alerts_history.py) — puro, sem rede/git."""

from __future__ import annotations

from investigator.alerts_history import (
    HistoryEntry,
    append_and_trim,
    classify_kind,
    load_jsonl,
    save_jsonl,
)


def test_classify_kind_deteta_mercado_e_noticia():
    assert classify_kind("🔺 Anomaly detected for AAPL: +2.10% today") == "market"
    assert classify_kind("📰 News alert for NVDA") == "news"


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
