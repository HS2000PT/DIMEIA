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


def test_teto_diario_por_ticker_nas_noticias(tmp_path):
    """Anti-fadiga: no máximo N alertas de notícia por ticker por dia (config)."""
    from datetime import date

    from scripts.run_alerts import filter_new_alerts, load_state

    st = load_state(tmp_path / "none.json", today=date(2026, 7, 11))
    news = [("TSLA", "manchete 1"), ("TSLA", "manchete 2"), ("TSLA", "manchete 3")]
    keep = filter_new_alerts([], news, st, max_per_ticker=2)
    assert len(keep) == 2  # a 3.ª cai no teto
    # outro ticker não é afetado pelo teto da TSLA
    keep2 = filter_new_alerts([], [("NVDA", "manchete nvda")], st, max_per_ticker=2)
    assert keep2 == [("NVDA", "manchete nvda")]


def test_seed_do_historico_partilhado_impede_duplicados_entre_produtores(tmp_path):
    """VM e Actions partilham memória via alerts-history: o que UM enviou, o outro não repete."""
    from datetime import date

    from investigator.alerts_history import HistoryEntry
    from scripts.run_alerts import (
        filter_new_alerts,
        load_state,
        news_key,
        seed_state_from_shared_history,
    )

    st = load_state(tmp_path / "none.json", today=date(2026, 7, 11))
    entries = [
        HistoryEntry(date="2026-07-11", ticker="TSLA", kind="market", text="Anomaly detected"),
        HistoryEntry(date="2026-07-11", ticker="NVDA", kind="news", text="News alert for NVDA",
                     key=news_key("NVDA", "News alert for NVDA")),
        HistoryEntry(date="2026-07-10", ticker="AAPL", kind="market", text="ontem"),
        HistoryEntry(date="2026-07-11", ticker="MARKET", kind="summary",
                     text="Daily close summary"),
    ]
    seed_state_from_shared_history(st, entries, "2026-07-11")
    assert st["summary_sent"] is True
    assert "AAPL" not in st["alerted_market"]  # entradas de outros dias não contam
    keep = filter_new_alerts(
        [("TSLA", "Anomaly detected"), ("AAPL", "Anomaly detected for AAPL")],
        [("NVDA", "News alert for NVDA")], st)
    assert keep == [("AAPL", "Anomaly detected for AAPL")]  # TSLA e a notícia NVDA já foram


def test_build_daily_summary_com_e_sem_anomalias():
    from scripts.run_alerts import build_daily_summary

    calmo = build_daily_summary([("AAPL", _res(False, 0.5)), ("TSLA", _res(False, -1.2))], 2.0)
    assert "Daily close summary" in calmo
    assert "No anomalies today" in calmo and "±" not in calmo
    assert "not advice" in calmo
    agitado = build_daily_summary([("TSLA", _res(True, 2.6))], 2.0)
    assert "📈 TSLA" in agitado and "anomaly" in agitado.lower()
    assert build_daily_summary([], 2.0) == ""


def test_maybe_daily_summary_uma_vez_por_dia_apos_21utc(tmp_path):
    from datetime import date

    from scripts.run_alerts import load_state, maybe_daily_summary

    st = load_state(tmp_path / "none.json", today=date(2026, 7, 11))
    resultados = [("AAPL", _res(False, 0.5))]
    assert maybe_daily_summary(st, resultados, 2.0, hour_utc=15) is None  # cedo demais
    texto = maybe_daily_summary(st, resultados, 2.0, hour_utc=21)
    assert texto and "Daily close summary" in texto
    assert maybe_daily_summary(st, resultados, 2.0, hour_utc=22) is None  # já enviado hoje
    st2 = load_state(tmp_path / "none.json", today=date(2026, 7, 11))
    assert maybe_daily_summary(st2, [], 2.0, hour_utc=22) is None  # sem resultados, nada a dizer


def _r(last_return: float) -> AnomalyResult:
    """AnomalyResult com o retorno que eu quiser (o _res fixa last_return=0.05)."""
    return AnomalyResult(is_anomaly=False, z_score=0.0, last_return=last_return,
                         mean=0.0, std=0.01, window=20, threshold=1.5)


def test_build_opening_note_snapshot():
    from scripts.run_alerts import build_opening_note

    note = build_opening_note([("NVDA", _r(0.024)), ("AAPL", _r(0.004)), ("TSLA", _r(-0.018))])
    assert "Market open" in note
    assert "📈 NVDA: +2.40% vs yesterday's close" in note   # verde a subir
    assert "📉 TSLA: -1.80% vs yesterday's close" in note    # vermelho a descer
    assert "Flat at the open: AAPL +0.4%" in note            # <1% comprimido
    assert note.index("NVDA") < note.index("TSLA")           # ordenado por |movimento|
    assert "not advice" in note
    assert build_opening_note([]) == ""


def test_maybe_opening_note_uma_vez_por_dia_na_abertura(tmp_path):
    from datetime import date

    from scripts.run_alerts import load_state, maybe_opening_note

    st = load_state(tmp_path / "none.json", today=date(2026, 7, 13))
    res = [("AAPL", _r(0.02))]
    assert maybe_opening_note(st, res, hour_utc=13) is None   # antes da janela de abertura
    txt = maybe_opening_note(st, res, hour_utc=14)
    assert txt and "Market open" in txt
    assert maybe_opening_note(st, res, hour_utc=15) is None   # já enviado hoje
    st2 = load_state(tmp_path / "none.json", today=date(2026, 7, 13))
    assert maybe_opening_note(st2, [], hour_utc=14) is None   # sem resultados → nada a dizer


def test_overrides_failopen_sem_ficheiro_e_sem_url():
    """Fail-open: sem ficheiro local e sem history_url, os overrides são {} (comportamento base)."""
    from scripts.run_alerts import _branch_overrides, _local_overrides

    assert _local_overrides() == {}          # não há config/alerts_overrides.yaml no repo
    assert _branch_overrides({}) == {}       # sem public.history_url → sem fetch


def test_effective_config_merge_local(tmp_path, monkeypatch):
    """effective_config funde overrides locais válidos sobre a base, limitando a valores sãos."""
    import scripts.run_alerts as ra

    monkeypatch.setattr(ra, "_local_overrides", lambda: {"market_threshold": 99})  # acima do teto
    monkeypatch.setattr(ra, "_branch_overrides", lambda cfg: {})
    cfg = ra.effective_config()
    assert cfg["market"]["threshold"] == 5.0  # limitado ao máximo são (não 99)


def test_precedents_are_strong_aplica_o_chao():
    from scripts.run_alerts import precedents_are_strong

    fracos = [(object(), 0.38), (object(), 0.35)]
    fortes = [(object(), 0.61), (object(), 0.35)]
    assert not precedents_are_strong(fracos, 0.45)
    assert precedents_are_strong(fortes, 0.45)
    assert not precedents_are_strong([], 0.45)


# ── Decomposição anexada aos alertas de mercado (A2b, 2026-07-29) ─────────────
def _serie_precos(n=80, seed=1):
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2026-01-01", periods=n)
    mercado = np.cumprod(1 + rng.normal(0, 0.01, n)) * 500
    return idx, mercado


def _fake_hist(mult: float, seed: int):
    import pandas as pd

    idx, base = _serie_precos(seed=seed)
    return pd.DataFrame({"Close": base * mult}, index=idx)


def test_decomposicao_anexa_linha_ao_alerta(monkeypatch):
    """Caminho feliz: a linha entra e nomeia as três componentes."""
    import scripts.run_alerts as ra

    monkeypatch.setattr(ra, "_hist_cached", lambda t, c: _fake_hist(1.0, seed=1))
    out = ra._attach_decomposition_safe("NVDA", "ALERTA", {})
    assert out.startswith("ALERTA\n")
    linha = out.split("\n")[1]
    assert "market" in linha and "sector" in linha and "company-specific" in linha


def test_decomposicao_fail_open_quando_precos_falham(monkeypatch):
    """Rede em baixo não pode impedir o alerta — a linha é contexto, nunca condição."""
    import scripts.run_alerts as ra

    def _rebenta(t, c):
        raise RuntimeError("yfinance bloqueado")

    monkeypatch.setattr(ra, "_hist_cached", _rebenta)
    assert ra._attach_decomposition_safe("NVDA", "ALERTA", {}) == "ALERTA"


def test_decomposicao_fail_open_com_historico_curto(monkeypatch):
    """Poucos dias alinhados → sem linha, mas o alerta sobrevive intacto."""
    import pandas as pd

    import scripts.run_alerts as ra

    curta = pd.DataFrame({"Close": [100.0, 101.0, 99.0]},
                         index=pd.bdate_range("2026-07-01", periods=3))
    monkeypatch.setattr(ra, "_hist_cached", lambda t, c: curta)
    assert ra._attach_decomposition_safe("NVDA", "ALERTA", {}) == "ALERTA"


def test_decomposicao_usa_uma_busca_por_simbolo(monkeypatch):
    """SPY e o ETF de setor são buscados 1× por ciclo, não 1× por ticker."""
    import scripts.run_alerts as ra

    pedidos: list[str] = []

    def _contado(t, c):
        pedidos.append(t)
        if t not in c:
            c[t] = _fake_hist(1.0, seed=1)
        return c[t]

    monkeypatch.setattr(ra, "_hist_cached", _contado)
    cache: dict = {}
    ra._attach_decomposition_safe("NVDA", "A", cache)
    ra._attach_decomposition_safe("AMD", "B", cache)   # mesmo setor (XLK) e mesmo índice
    assert sorted(cache) == ["AMD", "NVDA", "SPY", "XLK"]


def test_ticker_sem_setor_mapeado_decompoe_so_contra_o_mercado(monkeypatch):
    import scripts.run_alerts as ra

    monkeypatch.setattr(ra, "_hist_cached", lambda t, c: _fake_hist(1.0, seed=1))
    cache: dict = {}
    out = ra._attach_decomposition_safe("ZZZZ", "ALERTA", cache)
    assert "ZZZZ" not in [k for k in cache if k in ("XLK", "XLF", "XLE")]
    assert "market" in out


# ── Narrador ligado ao runner (A5c, 2026-07-29) ──────────────────────────────
def _ev_amd():
    from investigator.narrator.evidence import AlertEvidence

    return AlertEvidence(ticker="AMD", date="2026-07-28", kind="market",
                         move_pct="-8.50", z_score="-1.82", threshold="1.5", window_days=20)


def test_narrador_desligado_nao_toca_no_alerta():
    """Defeito de produção: `narrator.enabled` false → comportamento de sempre."""
    import scripts.run_alerts as ra

    assert ra._narrate_safe("ALERTA", _ev_amd(), {}) == "ALERTA"
    assert ra._narrate_safe("ALERTA", _ev_amd(), {"narrator": {"enabled": False}}) == "ALERTA"


def test_narrador_antepoe_paragrafo_quando_a_guarda_aceita(monkeypatch):
    import scripts.run_alerts as ra
    from investigator.narrator.core import NarrationResult

    bom = NarrationResult(text="AMD moved -8.50% on 2026-07-28.", source="groq",
                          guarded=False, latency_s=0.5)
    monkeypatch.setattr("investigator.narrator.core.narrate", lambda ev: bom)
    out = ra._narrate_safe("ALERTA", _ev_amd(), {"narrator": {"enabled": True}})
    assert out.startswith("AMD moved -8.50% on 2026-07-28.")
    assert out.endswith("ALERTA")


def test_guarda_a_rejeitar_deixa_o_alerta_INTACTO(monkeypatch):
    """A decisão de desenho que interessa: nunca se antepõe o template, que só repetiria
    o que o corpo do alerta já diz. O narrador só acrescenta, nunca degrada."""
    import scripts.run_alerts as ra
    from investigator.narrator.core import NarrationResult

    mau = NarrationResult(text="(template)", source="template", guarded=True,
                          violations=["número não-fiel: 47"])
    monkeypatch.setattr("investigator.narrator.core.narrate", lambda ev: mau)
    assert ra._narrate_safe("ALERTA", _ev_amd(), {"narrator": {"enabled": True}}) == "ALERTA"


def test_narrador_a_rebentar_nao_parte_o_alerta(monkeypatch):
    import scripts.run_alerts as ra

    def _explode(ev):
        raise RuntimeError("sem rede")

    monkeypatch.setattr("investigator.narrator.core.narrate", _explode)
    assert ra._narrate_safe("ALERTA", _ev_amd(), {"narrator": {"enabled": True}}) == "ALERTA"


def test_evidencia_sem_decomposicao_ainda_e_valida():
    import scripts.run_alerts as ra
    from investigator.anomaly_detector.detector import AnomalyResult

    res = AnomalyResult(is_anomaly=True, z_score=-1.82, last_return=-0.085,
                        mean=0.0, std=0.02, window=20, threshold=1.5)
    ev = ra._market_evidence("AMD", res, None, "2026-07-28")
    assert ev is not None and ev.move_pct == "-8.50" and ev.market_pct is None


def test_evidencia_com_decomposicao_leva_os_tres_componentes():
    import scripts.run_alerts as ra
    from investigator.anomaly_detector.detector import AnomalyResult
    from investigator.correlation_engine.decomposition import MoveDecomposition

    res = AnomalyResult(is_anomaly=True, z_score=-1.82, last_return=-0.085,
                        mean=0.0, std=0.02, window=20, threshold=1.5)
    d = MoveDecomposition(total=-0.085, market=0.0061, sector=-0.036,
                          idiosyncratic=-0.0551, beta_market=2.5, beta_sector=1.8,
                          window=20, r_squared=0.77, fallback=False)
    ev = ra._market_evidence("AMD", res, d, "2026-07-28")
    assert (ev.market_pct, ev.sector_pct, ev.company_pct) == ("+0.61", "-3.60", "-5.51")
    assert ev.driver == "company"


def test_evidencia_do_runner_passa_a_propria_guarda():
    """Ponte crítica: a evidência construída pelo runner tem de ser narrável de facto."""
    import scripts.run_alerts as ra
    from investigator.anomaly_detector.detector import AnomalyResult
    from investigator.narrator.core import check_faithfulness, template_text

    res = AnomalyResult(is_anomaly=True, z_score=-1.82, last_return=-0.085,
                        mean=0.0, std=0.02, window=20, threshold=1.5)
    ev = ra._market_evidence("AMD", res, None, "2026-07-28")
    rel = check_faithfulness(template_text(ev), ev)
    assert rel.ok, rel.violations


def test_teto_diario_serve_por_materialidade_e_nao_por_ordem_de_chegada(tmp_path):
    """O caso da NVDA (2026-08-05): a notícia que interessava chegou DEPOIS da quota gasta.

    Duas manchetes irrelevantes de manhã consumiam o tecto e a notícia material da tarde era
    descartada em silêncio — apesar de existir um modelo de triagem treinado exactamente para
    ordenar por materialidade, que o tecto não consultava.
    """
    from datetime import date

    from scripts.run_alerts import filter_new_alerts, load_state, news_key

    news = [
        ("NVDA", "analyst note repeats hold rating"),
        ("NVDA", "seven cheap stocks to watch this week"),
        ("NVDA", "SpaceX to use Nvidia chips exclusively, says Musk"),
    ]
    mat = {
        news_key("NVDA", news[0][1]): 0.11,
        news_key("NVDA", news[1][1]): 0.08,
        news_key("NVDA", news[2][1]): 0.93,
    }

    st = load_state(tmp_path / "a.json", today=date(2026, 8, 5))
    com = filter_new_alerts([], news, st, max_per_ticker=2, materiality=mat)
    textos = [t for _, t in com]
    assert "SpaceX" in textos[0], "a mais material tem de vir primeiro"
    assert len(com) == 2

    # Sem o canal de materialidade, o defeito reproduz-se: a que interessa NÃO sai.
    st2 = load_state(tmp_path / "b.json", today=date(2026, 8, 5))
    sem = filter_new_alerts([], news, st2, max_per_ticker=2)
    assert not any("SpaceX" in t for _, t in sem), "sem ranking, a notícia material é descartada"


def test_sem_triagem_a_ordem_de_chegada_e_preservada(tmp_path):
    """A triagem está OFF por defeito: o comportamento antigo tem de ser o caso particular."""
    from datetime import date

    from scripts.run_alerts import filter_new_alerts, load_state

    news = [("AMD", "primeira"), ("AMD", "segunda"), ("AMD", "terceira")]
    st = load_state(tmp_path / "c.json", today=date(2026, 8, 5))
    keep = filter_new_alerts([], news, st, max_per_ticker=2, materiality={})
    assert [t for _, t in keep] == ["primeira", "segunda"]


def test_mesma_historia_noutras_palavras_nao_repete(tmp_path):
    """`news_key` e hash do texto exacto: dois meios, dois titulos, dois alertas iguais.

    A comparacao e feita sobre a MANCHETE (canal lateral), nunca sobre o texto do alerta --
    o alerta e quase todo template e duas noticias diferentes colidiriam.
    """
    from datetime import date

    from scripts.run_alerts import filter_new_alerts, load_state, news_key

    a_txt, b_txt = "ALERTA A (texto renderizado)", "ALERTA B (texto renderizado)"
    manchetes = {
        news_key("NVDA", a_txt): "SpaceX to use Nvidia chips exclusively, says Musk",
        news_key("NVDA", b_txt): "Musk says SpaceX will use Nvidia chips exclusively",
    }
    st = load_state(tmp_path / "d.json", today=date(2026, 8, 5))
    keep = filter_new_alerts([], [("NVDA", a_txt), ("NVDA", b_txt)], st,
                             max_per_ticker=2, headlines=manchetes)
    assert len(keep) == 1, "a segunda e a mesma historia noutras palavras"


def test_noticias_diferentes_do_mesmo_ticker_nao_sao_confundidas(tmp_path):
    """Controlo positivo: o detector nao pode engolir noticias distintas."""
    from datetime import date

    from scripts.run_alerts import filter_new_alerts, load_state, news_key

    a_txt, b_txt = "ALERTA A", "ALERTA B"
    manchetes = {
        news_key("NVDA", a_txt): "SpaceX to use Nvidia chips exclusively, says Musk",
        news_key("NVDA", b_txt): "Nvidia opens research centre in Israel amid hiring push",
    }
    st = load_state(tmp_path / "e.json", today=date(2026, 8, 5))
    keep = filter_new_alerts([], [("NVDA", a_txt), ("NVDA", b_txt)], st,
                             max_per_ticker=2, headlines=manchetes)
    assert len(keep) == 2, "historias diferentes tem de passar as duas"


def test_alerta_renderizado_nao_serve_para_deduplicar():
    """Porque a comparacao NAO pode ser feita sobre o texto do alerta.

    Dois alertas de noticias DIFERENTES partilham quase todo o template. Se a deteccao de
    quase-repeticao corresse sobre esse texto, o segundo seria suprimido em silencio -- que e
    o mesmo defeito que este trabalho corrige, ao contrario.
    """
    from scripts.run_alerts import conteudo, quase_repetida

    template = ("News alert for NVDA (Nvidia). Similar past cases and their measured impact "
                "at +1, +3 and +5 days. This is evidence from the past, never a forecast.")
    a = template + " Headline: SpaceX to use Nvidia chips exclusively."
    b = template + " Headline: Nvidia opens research centre in Israel."
    assert quase_repetida(b, [sorted(conteudo(a))]), "sobre o alerta inteiro, colidem"

    # Sobre as MANCHETES, que e como o codigo faz, nao colidem.
    ha = "SpaceX to use Nvidia chips exclusively, says Musk"
    hb = "Nvidia opens research centre in Israel amid hiring push"
    assert not quase_repetida(hb, [sorted(conteudo(ha))]), "sobre a manchete, sao distintas"


def test_manchete_curta_falha_aberto():
    """Com poucas palavras de conteudo qualquer par bate: nao se suprime nada."""
    from scripts.run_alerts import conteudo, quase_repetida

    assert not quase_repetida("manchete 2", [sorted(conteudo("manchete 1"))])
