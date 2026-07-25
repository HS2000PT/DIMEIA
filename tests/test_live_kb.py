"""Testes da KB viva — maturação, dedup, decaimento por idade (puro, sem rede)."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from investigator.historical_kb.embedder import HashingEmbedder
from investigator.historical_kb.knowledge_base import HistoricalKB
from investigator.historical_kb.record import NewsRecord
from investigator.live_kb import (
    MIN_AGE_DAYS,
    PendingNews,
    add_pending,
    append_records,
    embed_text,
    load_pending,
    mature_entry,
    mature_ready,
    merged_precedents,
    recency_weight,
    save_pending,
)


def _serie(dias: int, inicio: str = "2026-06-01") -> pd.Series:
    idx = pd.bdate_range(start=inicio, periods=dias)
    return pd.Series(100.0 + np.arange(dias, dtype="float64"), index=idx)


def _pend(d: str, ticker: str = "AAPL", key: str = "k1") -> PendingNews:
    return PendingNews(date=d, ticker=ticker, headline="Apple sobe", key=key,
                       embedding=[0.6, 0.8])


def test_embed_text_junta_summary_so_em_memoria():
    assert embed_text("Titulo", "Resumo curto.") == "Titulo. Resumo curto."
    assert embed_text("Titulo", "") == "Titulo"


def test_mature_entry_calcula_impactos_corretos():
    """Preços 100,101,102,...: +1d=1/100, +3d=3/100, +5d=5/100 a partir do dia do evento."""
    closes = _serie(10)  # 10 dias úteis a partir de 2026-06-01
    rec = mature_entry(_pend("2026-06-01"), closes)
    assert rec is not None
    assert abs(rec.impacts["1"] - 0.01) < 1e-12
    assert abs(rec.impacts["3"] - 0.03) < 1e-12
    assert abs(rec.impacts["5"] - 0.05) < 1e-12
    assert rec.embedding == [0.6, 0.8]


def test_mature_entry_alinha_ao_primeiro_dia_util():
    """Notícia de sábado 2026-06-06 → evento = segunda 2026-06-08 (preço 105→106…110)."""
    closes = _serie(15)
    rec = mature_entry(_pend("2026-06-06"), closes)
    assert rec is not None
    base = float(closes.loc["2026-06-08"])
    assert abs(rec.impacts["5"] - (base + 5 - base) / base) < 1e-12


def test_mature_entry_espera_pela_barra_mais_5d():
    closes = _serie(4)  # só 4 barras: +5d não observável
    assert mature_entry(_pend("2026-06-01"), closes) is None
    assert mature_entry(_pend("2026-06-01"), None) is None


def test_mature_ready_respeita_idade_e_lote(tmp_path):
    hoje = date(2026, 7, 11)
    fresca = _pend("2026-07-10", key="fresca")  # <MIN_AGE_DAYS → fica pendente
    pronta = _pend("2026-06-01", key="pronta")
    closes = {"AAPL": _serie(30)}
    matured, still = mature_ready([fresca, pronta], closes, hoje)
    assert [r.headline for r in matured] and len(matured) == 1
    assert [e.key for e in still] == ["fresca"]
    assert (hoje - date(2026, 7, 10)).days < MIN_AGE_DAYS  # sanidade do fixture


def test_pending_roundtrip_e_dedup(tmp_path):
    p = tmp_path / "live_pending.jsonl"
    save_pending([_pend("2026-06-01", key="a")], p)
    carregados = load_pending(p)
    assert len(carregados) == 1 and carregados[0].key == "a"
    juntos = add_pending(carregados, [_pend("2026-06-02", key="a"),  # dup — ignora
                                      _pend("2026-06-03", key="b")])
    assert [e.key for e in juntos] == ["a", "b"]
    assert load_pending(tmp_path / "nao_existe.jsonl") == []


def test_append_records_acrescenta_formato_newsrecord(tmp_path):
    p = tmp_path / "live_kb.jsonl"
    rec = NewsRecord(date="2026-06-01", ticker="AAPL", headline="h",
                     impacts={"1": 0.01, "3": 0.03, "5": 0.05}, embedding=[0.6, 0.8])
    append_records([rec], p)
    append_records([rec], p)  # append é cumulativo (dedup é responsabilidade da captura)
    kb = HistoricalKB.load(p)
    assert len(kb) == 2 and kb.records[0].impacts["5"] == 0.05


def test_recency_weight_meia_vida():
    hoje = date(2026, 7, 11)
    assert recency_weight("2026-07-11", hoje, 365) == 1.0
    um_ano = recency_weight("2025-07-11", hoje, 365)
    assert abs(um_ano - 0.5) < 0.01
    assert recency_weight("data-invalida", hoje, 365) == 0.0


def test_merged_precedents_prefere_recente_com_cosseno_igual():
    """Dois casos identicamente semelhantes: o RECENTE ganha; a sim mostrada é o cosseno real."""
    emb = HashingEmbedder(dim=16)
    vec = [float(x) for x in emb.encode(["apple sobe forte"])[0]]
    antigo = NewsRecord(date="2019-01-02", ticker="AAPL", headline="apple sobe forte",
                        impacts={"5": 0.05}, embedding=vec)
    recente = NewsRecord(date="2026-06-30", ticker="MSFT", headline="apple sobe forte",
                         impacts={"5": 0.02}, embedding=vec)
    kb_antiga, kb_viva = HistoricalKB([antigo]), HistoricalKB([recente])
    out = merged_precedents("apple sobe forte", [kb_viva, kb_antiga], emb, top_k=2,
                            today=date(2026, 7, 11))
    assert out[0][0].date == "2026-06-30"  # o recente primeiro
    assert abs(out[0][1] - 1.0) < 1e-9      # cosseno real, sem decaimento aplicado ao valor


def test_merged_precedents_max_age_corta_antigos():
    emb = HashingEmbedder(dim=16)
    vec = [float(x) for x in emb.encode(["apple sobe forte"])[0]]
    antigo = NewsRecord(date="2019-01-02", ticker="AAPL", headline="apple sobe forte",
                        impacts={}, embedding=vec)
    kb = HistoricalKB([antigo])
    out = merged_precedents("apple sobe forte", [kb], emb, top_k=3,
                            today=date(2026, 7, 11), max_age_days=180)
    assert out == []  # o botão "só 6 meses" corta tudo o que é velho
    sem_corte = merged_precedents("apple sobe forte", [kb], emb, top_k=3,
                                  today=date(2026, 7, 11))
    assert len(sem_corte) == 1


def test_merged_precedents_max_age_tolera_data_corrompida():
    """Regressão (fail-open): com max_age_days ativo, um registo com data não-ISO na KB
    não pode rebentar a recuperação — é descartado, como já fazia `recency_weight`. Antes
    da correção, `date.fromisoformat` levantava ValueError e a consulta abortava."""
    emb = HashingEmbedder(dim=16)
    vec = [float(x) for x in emb.encode(["apple sobe forte"])[0]]
    bom = NewsRecord(date="2026-06-30", ticker="MSFT", headline="apple sobe forte",
                     impacts={"5": 0.02}, embedding=vec)
    corrompido = NewsRecord(date="2026/06/30", ticker="AAPL", headline="apple sobe forte",
                            impacts={}, embedding=vec)
    out = merged_precedents("apple sobe forte", [HistoricalKB([bom, corrompido])], emb,
                            top_k=3, today=date(2026, 7, 11), max_age_days=180)
    assert [r.ticker for r, _ in out] == ["MSFT"]  # data inválida cai; o registo bom fica


def test_merged_precedents_kb_vazia_fail_open():
    emb = HashingEmbedder(dim=16)
    assert merged_precedents("q", [HistoricalKB([]), None], emb, top_k=3,
                             today=date(2026, 7, 11)) == []
