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
    plano = AnomalyResult(
        is_anomaly=True, z_score=0.0, last_return=0.05, mean=0.0, std=0.0,
        window=20, threshold=2.0, zero_variance=True,
    )
    texto_plano = build_daily_summary([("FLAT", plano)], 2.0)
    assert "flat 20-day baseline" in texto_plano
    assert "z +0.00" not in texto_plano
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


def test_ordem_de_entrega_serve_por_materialidade(tmp_path):
    """A ordenação por materialidade, dita pelo que ela É: ordem de ENTREGA num ciclo.

    ⚠️ Este teste chegou a chamar-se "o teto serve por materialidade" e a documentar a correcção
    do caso da NVDA. **Estava a validar um cenário que a produção não sabe produzir:** três
    manchetes do MESMO ticker numa só chamada. O `scan_news` emite uma manchete por ticker por
    ciclo, portanto duas candidatas ao mesmo teto (que é por ticker) nunca coexistem no lote, e
    a ordenação nunca as pode reordenar. O controlo do teto é o piso escalonado, coberto pelo
    teste seguinte, que percorre CICLOS separados como a produção faz.

    O que fica aqui coberto é real e vale por si: dentro de um ciclo, o canal entrega primeiro
    a mais material.

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


def test_piso_escalonado_guarda_a_quota_para_a_noticia_da_tarde(tmp_path):
    """O caso da NVDA, agora no cenário que a PRODUÇÃO produz: um ciclo, um alerta por ticker.

    Três ciclos ao longo do dia (o worker corre a 60 s; aqui só interessa a sequência). Duas
    manchetes mornas de manhã, a que interessa à tarde. Com o teto a 2 e sem piso escalonado, as
    duas de manhã gastam a quota e a da tarde é descartada — e a ordenação por materialidade não
    salva nada, porque nunca vê duas candidatas ao mesmo tempo.

    Com o piso escalonado, o segundo slot exige τ*(R=0,5)=0,64 e a manchete de 55% não o alcança,
    portanto a quota fica guardada e a notícia da SpaceX sai.

    ⚠️ **Os P's são todos ≥ 0,50 de propósito.** A primeira versão deste teste usava 0,11 e 0,08
    e o teste apanhou-me: com `min_materiality: 0.5` em produção, essas manchetes nunca chegam a
    esta função — são suprimidas antes. Um cenário abaixo do gate testaria um caminho que a
    produção não percorre, que é exactamente o defeito do teste que este substitui.
    """
    from datetime import date

    from scripts.run_alerts import filter_new_alerts, load_state, news_key

    ciclos = [
        ("NVDA", "analyst note repeats hold rating"),          # manhã, P=0,52
        ("NVDA", "seven cheap stocks to watch this week"),      # meio-dia, P=0,55
        ("NVDA", "SpaceX to use Nvidia chips exclusively, says Musk"),  # tarde, P=0,65
    ]
    mat = {news_key(t, x): p for (t, x), p in zip(ciclos, (0.52, 0.55, 0.65), strict=True)}
    escada = [0.49, 0.64]

    # Sem piso: o defeito reproduz-se, um ciclo por chamada.
    st = load_state(tmp_path / "sem.json", today=date(2026, 8, 5))
    saiu_sem = [t for c in ciclos for _, t in filter_new_alerts([], [c], st, 2, mat, None, None)]
    assert not any("SpaceX" in t for t in saiu_sem), (
        "sem piso escalonado a notícia material tem de ser descartada — se este assert falhar, "
        "o defeito que motivou a correcção deixou de existir por outra via e a correcção "
        "precisa de ser rejustificada"
    )

    # Com piso: a segunda manchete menor não alcança 0,64, a quota sobra para a da tarde.
    st2 = load_state(tmp_path / "com.json", today=date(2026, 8, 5))
    saiu = [t for c in ciclos for _, t in filter_new_alerts([], [c], st2, 2, mat, None, escada)]
    assert any("SpaceX" in t for t in saiu), "a notícia material tem de sair"
    assert len(saiu) == 2, "e sem estourar o teto"


def test_piso_escalonado_falha_aberto_sem_score(tmp_path):
    """Triagem desligada ou modelo ausente: sem P não há piso a aplicar.

    Suprimir por falta de informação seria decidir com base em nada — e transformaria uma
    configuração incompleta em silêncio do canal.
    """
    from datetime import date

    from scripts.run_alerts import filter_new_alerts, load_state

    ciclos = [("AMD", "primeira"), ("AMD", "segunda")]
    st = load_state(tmp_path / "d.json", today=date(2026, 8, 5))
    saiu = [t for c in ciclos
            for _, t in filter_new_alerts([], [c], st, 2, {}, None, [0.49, 0.64])]
    assert saiu == ["primeira", "segunda"]


def test_piso_escalonado_nao_estorva_o_primeiro_alerta(tmp_path):
    """O 1.º slot mantém o gate normal: quem passou a triagem passa o piso."""
    from datetime import date

    from scripts.run_alerts import filter_new_alerts, load_state, news_key

    item = ("JNJ", "FDA clears new indication")
    mat = {news_key(*item): 0.51}
    st = load_state(tmp_path / "e.json", today=date(2026, 8, 5))
    assert filter_new_alerts([], [item], st, 2, mat, None, [0.49, 0.64])


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


def test_excecao_de_rede_nao_escreve_a_chave_no_registo():
    """Fuga real, apanhada a 2026-08-06 nos registos do Heroku.

    A mensagem de uma HTTPError inclui o URL do pedido, e o URL leva o token. Bastou a API
    responder 503 -- e respondeu a tudo nesse dia -- para a chave ficar escrita centenas de
    vezes no registo. O codigo nunca imprimiu a chave; imprimiu a EXCECAO.
    """
    from scripts.run_alerts import sem_segredos

    chave = "d8nco1hr01qvvn95orv0d8nco1hr01qvvn95orvg"
    bruto = (f"HTTPError: 503 Server Error: Service Unavailable for url: "
             f"https://finnhub.io/api/v1/company-news?symbol=JNJ&from=2026-07-30&token={chave}")
    limpo = sem_segredos(bruto)
    assert chave not in limpo, "a chave nao pode sobreviver a mascara"
    assert "<REDACTED>" in limpo
    assert "finnhub.io" in limpo, "o URL continua util para diagnostico"
    assert "symbol=JNJ" in limpo, "os parametros nao-secretos ficam"


def test_mascara_cobre_os_varios_nomes_de_parametro():
    """Nao chega mascarar `token=`: cada fornecedor chama-lhe outra coisa."""
    from scripts.run_alerts import sem_segredos

    for nome in ("token", "key", "apikey", "api_key", "apiKey", "access_token"):
        s = sem_segredos(f"https://exemplo.com/v1?symbol=X&{nome}=SEGREDO123456&b=2")
        assert "SEGREDO123456" not in s, f"{nome} passou"
        assert "b=2" in s, "parametros seguintes nao podem ser comidos"


def test_investigacao_cruzada_nao_oferece_noticia_POSTERIOR_ao_movimento(monkeypatch):
    """A seta causal não pode apontar ao contrário.

    A escolha era `max(por data)` na janela de 48h, sem verificar se a manchete é ANTERIOR ao
    movimento que diz explicar. Num alerta intradiário ("-1,6% até agora") isso oferecia como
    *possible explanation* uma notícia publicada DEPOIS da leitura. A linha é uma hipótese e
    não uma causa provada, mas oferecer o futuro como explicação do passado é errado mesmo
    com ressalva.
    """
    import scripts.run_alerts as ra
    from investigator.news_fetcher.fetcher import NewsItem

    antes = NewsItem(date="2026-08-10", ticker="NVDA", headline="Nvidia ANTES do movimento",
                     published_at="2026-08-10T13:00:00Z")
    depois = NewsItem(date="2026-08-10", ticker="NVDA", headline="Nvidia DEPOIS do movimento",
                      published_at="2026-08-10T18:00:00Z")

    import investigator.config as cfg
    monkeypatch.setattr(cfg, "FINNHUB_API_KEY", "x", raising=False)
    monkeypatch.setattr("investigator.news_fetcher.fetcher.fetch_finnhub_company_news",
                        lambda *a, **k: [antes, depois])

    saida = ra._investigate_anomaly_safe("NVDA", "alerta", observado_em="2026-08-10T15:00:00Z")
    assert "ANTES do movimento" in saida
    assert "DEPOIS do movimento" not in saida, "ofereceu uma notícia posterior como explicação"


# ── O funil tem de dizer a verdade sobre o que foi ENTREGUE ────────────────────
# ⚠️ Regressão de um defeito visível no ecrã e invisível a todos os testes que existiam:
# `_gate()` corre dentro do `scan_news`, e o tecto/escada/quase-repetição correm DEPOIS, no
# `filter_new_alerts`. Nada reetiquetava o que elas suprimiam, portanto `stage="alerted"`
# significava "sobreviveu à varredura" e o screener traduzia-o para "Alert sent" — dizendo ao
# utilizador que um alerta saiu quando não saiu, na vista que existe para tornar o silêncio
# inspeccionável.

def _gate_rec(ticker: str, stage: str, detail: str = ""):
    from investigator.gate_log import GateRecord

    return GateRecord(date="2026-08-14", ticker=ticker, stage=stage, detail=detail)


def test_tecto_diario_reetiqueta_o_funil_em_vez_de_dizer_alerted(tmp_path):
    from datetime import date

    from scripts.run_alerts import _reconcile_gates, filter_new_alerts, load_state

    st = load_state(tmp_path / "none.json", today=date(2026, 8, 14))
    st["news_count"]["NVDA"] = 2  # tecto de 2/dia já gasto
    sup: dict[str, tuple[str, str]] = {}
    keep = filter_new_alerts([], [("NVDA", "News alert for NVDA\nmanchete nova")], st,
                             max_per_ticker=2, suppressed=sup)
    assert keep == []                      # não foi entregue
    assert sup["NVDA"][0] == "daily_cap"   # e sabe-se porquê

    recs = [_gate_rec("NVDA", "alerted"), _gate_rec("XOM", "weak_precedent", "sim 0.31 < 0.45")]
    _reconcile_gates(recs, sup)
    assert recs[0].stage == "daily_cap"        # deixou de mentir
    assert "cap" in recs[0].detail
    assert recs[1].stage == "weak_precedent"   # e não reescreveu quem já tinha morrido antes


def test_reconciliacao_nao_toca_em_quem_foi_mesmo_entregue(tmp_path):
    """Controlo no sentido oposto: sem supressão, `alerted` continua a ser `alerted`.

    Sem este teste, uma reconciliação que reetiquetasse tudo seria indistinguível de uma que
    funciona — e o screener passaria a dizer que nunca se envia nada."""
    from scripts.run_alerts import _reconcile_gates

    recs = [_gate_rec("NVDA", "alerted")]
    _reconcile_gates(recs, {})
    assert recs[0].stage == "alerted"


def test_todas_as_etapas_pos_varredura_existem_no_gate_log():
    """As etapas novas têm de estar declaradas, senão o screener recebe uma etapa que não sabe
    desenhar e cai no rótulo por defeito."""
    from investigator.gate_log import STAGES

    for etapa in ("daily_cap", "ladder_floor", "duplicate_story", "already_sent",
                  "daily_budget"):
        assert etapa in STAGES


def test_publicacao_lenta_estrangula_por_tempo(tmp_path, capsys):
    """⚠️ Regressão do ciclo de aprendizagem parado (medido a 2026-08-15).

    A base de casos viva estava congelada em 2026-07-27 e havia 1785 pendentes de Julho por
    maturar. A causa é de escala: `live_kb` e `live_pending` pesam dezenas de MB e não podem
    ser publicados a cada ciclo de 60 s. Este teste fixa o estrangulamento — a segunda chamada
    seguida não pode voltar a publicar.
    """
    from scripts.run_alerts import _ULTIMA_PUB, _publish_lento_safe

    _ULTIMA_PUB.clear()
    p = tmp_path / "live_kb.jsonl"
    p.write_text('{"date":"2026-08-15"}\n', encoding="utf-8")

    _publish_lento_safe(p, "live_kb.jsonl", minutos=30)
    marca = dict(_ULTIMA_PUB)
    _publish_lento_safe(p, "live_kb.jsonl", minutos=30)

    assert "live_kb.jsonl" in marca, "a primeira chamada tem de tentar publicar"
    assert _ULTIMA_PUB == marca, "a segunda chamada seguida não pode voltar a publicar"


def test_orcamento_global_limita_o_TOTAL_e_nao_so_cada_empresa():
    """⚠️ O tecto por ticker não limita o total: 12 empresas x 2 = 24 mensagens num dia.

    O que o utilizador sente é o total. O orçamento é global e vem antes do tecto.
    """
    from scripts.run_alerts import filter_new_alerts

    estado: dict = {"day": "2026-08-15", "alerted_market": [], "alerted_news": [],
                    "news_count": {}, "news_words": {}}
    candidatas = [(t, f"News alert for {t}\nlinha") for t in
                  ("AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META")]
    suprimidas: dict[str, tuple[str, str]] = {}

    saida = filter_new_alerts([], candidatas, estado, suppressed=suprimidas, daily_budget=3)

    assert len(saida) == 3, "o orçamento tem de limitar o total, não cada empresa"
    assert suprimidas.get("GOOGL", ("", ""))[0] == "daily_budget"


def test_sem_orcamento_o_comportamento_e_o_de_sempre():
    """O caminho antigo é o caso particular: sem orçamento, nada muda."""
    from scripts.run_alerts import filter_new_alerts

    estado: dict = {"day": "2026-08-15", "alerted_market": [], "alerted_news": [],
                    "news_count": {}, "news_words": {}}
    candidatas = [(t, f"News alert for {t}\nlinha") for t in
                  ("AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META")]

    saida = filter_new_alerts([], candidatas, estado)

    assert len(saida) == 7, "sem orçamento não pode haver limite global"


def test_orcamento_serve_as_mais_materiais_primeiro():
    """O orçamento só vale alguma coisa se gastar os lugares nas melhores candidatas.

    É a única coisa para que a medição sustenta usar o score do modelo: ordenar ENTRE
    empresas.
    """
    from scripts.run_alerts import filter_new_alerts, news_key

    estado: dict = {"day": "2026-08-15", "alerted_market": [], "alerted_news": [],
                    "news_count": {}, "news_words": {}}
    cands = [(t, f"News alert for {t}\nlinha") for t in ("AAPL", "MSFT", "NVDA")]
    mat = {news_key(t, x): p for (t, x), p in zip(cands, (0.30, 0.90, 0.60), strict=True)}

    saida = filter_new_alerts([], cands, estado, materiality=mat, daily_budget=2)

    assert [t for t, _ in saida] == ["MSFT", "NVDA"], (
        "com orçamento de 2, os lugares vão para as duas mais materiais")


def test_manchete_ja_enviada_hoje_e_registada_como_supressao():
    """⚠️ Regressão do defeito medido a 2026-08-15.

    A supressão ``esta manchete exacta já foi alertada hoje`` fazia ``continue`` sem registar
    nada, ao contrário das outras três. Com o ciclo de 60 s a mesma manchete é reavaliada todos
    os minutos, e o funil contava-a como ``alerted`` de cada vez: **330 registos `alerted` num
    dia em que o canal recebeu 4 mensagens**.
    """
    from scripts.run_alerts import filter_new_alerts, news_key

    texto = "News alert for NVDA\nqualquer coisa"
    estado: dict = {"day": "2026-08-15", "alerted_news": [news_key("NVDA", texto)],
                    "news_count": {}, "news_words": {}}
    suprimidas: dict[str, tuple[str, str]] = {}

    saida = filter_new_alerts([], [("NVDA", texto)], estado, suppressed=suprimidas)

    assert saida == [], "uma manchete já entregue não pode ser reenviada"
    assert suprimidas.get("NVDA", ("", ""))[0] == "already_sent", (
        "a supressão tem de ficar registada, senão o funil continua a dizer 'alerted'")


def test_semear_nao_sobrescreve_ficheiro_local_com_conteudo(tmp_path):
    """⚠️ O disco do dyno é efémero: sem semear, publicar escreveria por cima da branch com só
    os registos desde o último arranque — apagaria a série. Mas semear NUNCA pode destruir
    trabalho local, senão trocava-se um modo de perder dados por outro."""
    from scripts.run_alerts import _seed_from_branch_safe

    p = tmp_path / "gate_log.jsonl"
    p.write_text('{"date":"2026-08-15","ticker":"NVDA","stage":"alerted","detail":""}\n',
                 encoding="utf-8")
    antes = p.read_text(encoding="utf-8")
    _seed_from_branch_safe(p, "gate_log.jsonl")   # ficheiro tem conteúdo -> não toca
    assert p.read_text(encoding="utf-8") == antes


def test_semear_e_publicar_falham_abertos(tmp_path, monkeypatch):
    """Nenhum dos dois pode travar um ciclo de alertas: um painel desactualizado é um
    inconveniente, um canal parado por causa dele seria trocar o essencial pelo acessório."""
    from scripts.run_alerts import _publish_data_safe, _seed_from_branch_safe

    monkeypatch.setenv("INVESTIGATOR_HISTORY_REPO", "nao/existe-de-todo")
    _seed_from_branch_safe(tmp_path / "ausente.jsonl", "gate_log.jsonl")   # não levanta
    _publish_data_safe(tmp_path / "ausente.jsonl", "gate_log.jsonl")       # não levanta


# ══ O ORÇAMENTO DIÁRIO E A MEMÓRIA DO DIA ═══════════════════════════════════════════════════
# ⚠️ **O defeito, medido no registo público a 2026-09-02.** O canal tem orçamento de cinco
# alertas de notícia por dia. O histórico partilhado mostra **vinte** no dia 26 de agosto, em
# quatro rajadas de exactamente cinco, aos segundos coincidentes com arranques do processo
# (00:03, 07:38, 13:04 e 22:24) — e as MESMAS cinco empresas nas quatro. O mesmo padrão nos dias
# 25, 27, 28 e 29.
#
# A causa não é a política: é o contador. Vive em `data/alerts_state.json`, no disco efémero do
# dyno, e volta a zero a cada arranque. O `seed_state_from_shared_history` existe justamente
# para o repor a partir do histórico partilhado — mas era chamado com um `[]` indistinguível de
# «não consegui ler», e um processo que não consegue ler fica a acreditar que ainda não enviou
# nada.
#
# A correcção é uma distinção: `None` (não sei) contra `[]` (sei, e não saiu nada). E, só nesta
# porta, falha FECHADA. Todo o resto do runner falha aberto de propósito; aqui o custo do erro
# não é simétrico — não enviar perde um alerta, enviar sem saber enche o canal.


def _estado_limpo(dia: str = "2026-08-15") -> dict:
    return {"date": dia, "day": dia, "alerted_market": [], "alerted_news": [],
            "news_count": {}, "news_words": {}}


def test_sem_memoria_do_dia_o_orcamento_fecha():
    """Um processo que não sabe o que já saiu hoje não gasta orçamento nenhum."""
    from scripts.run_alerts import filter_new_alerts

    estado = _estado_limpo() | {"memoria_do_dia": False}
    cands = [(t, f"News alert for {t}\nlinha") for t in ("AAPL", "MSFT", "NVDA")]
    suprimidas: dict[str, tuple[str, str]] = {}

    saida = filter_new_alerts([], cands, estado, suppressed=suprimidas, daily_budget=5)

    assert saida == [], "enviou sem saber quantos já tinham saído hoje"
    assert suprimidas["AAPL"][0] == "daily_budget"
    assert "unknown" in suprimidas["AAPL"][1], "a supressão tem de dizer que foi por não saber"


def test_com_memoria_do_dia_o_orcamento_deixa_passar():
    """A porta nova só fecha na ausência de informação; com informação, nada muda."""
    from scripts.run_alerts import filter_new_alerts

    estado = _estado_limpo() | {"memoria_do_dia": True}
    cands = [(t, f"News alert for {t}\nlinha") for t in ("AAPL", "MSFT", "NVDA")]

    assert len(filter_new_alerts([], cands, estado, daily_budget=5)) == 3


def test_o_defeito_por_omissao_nao_muda_os_chamadores_antigos():
    """`memoria_do_dia` é um facto que o chamador fornece; sem ele, o comportamento é o antigo.

    A função é pura e tem outros chamadores (testes, dry-runs, o cron). Fazer o defeito ser
    «fechado» calaria todos eles sem nada ter corrido mal. Quem tem de o afirmar é o `run_once`,
    que é o único caminho de produção — e o teste seguinte fixa isso.
    """
    from scripts.run_alerts import filter_new_alerts

    estado = _estado_limpo()          # sem a chave
    cands = [("AAPL", "News alert for AAPL\nlinha")]
    assert len(filter_new_alerts([], cands, estado, daily_budget=5)) == 1


def test_o_historico_partilhado_distingue_vazio_de_ilegivel(monkeypatch):
    """`[]` autoriza gastar o orçamento; `None` não. São coisas diferentes e têm de o parecer."""
    import scripts.run_alerts as R

    assert R._fetch_shared_history_safe({}) is None, "sem URL configurado não se sabe nada"

    import investigator.alerts_history as AH

    monkeypatch.setattr(AH, "fetch_remote", lambda url: [])
    cfg = {"public": {"history_url": "https://exemplo/x.jsonl"}}
    assert R._fetch_shared_history_safe(cfg) == [], "leu e estava vazio: isso é saber"

    def rebenta(url):
        raise OSError("rede em baixo")

    monkeypatch.setattr(AH, "fetch_remote", rebenta)
    assert R._fetch_shared_history_safe(cfg) is None, "falhou a leitura: isso é não saber"


def test_run_once_afirma_a_memoria_do_dia():
    """A garantia tem de estar no caminho de produção, e não só na função pura.

    Sem esta linha no `run_cycle`, o defeito permissivo da função pura voltaria a ser o
    comportamento de produção — que é exactamente o defeito que isto corrige.
    """
    import inspect

    import scripts.run_alerts as R

    fonte = inspect.getsource(R.run_cycle)
    assert 'state["memoria_do_dia"]' in fonte, (
        "o run_cycle deixou de afirmar se sabe o que já saiu hoje")
    assert "partilhado is not None" in fonte, (
        "a memória do dia voltou a não distinguir «li e estava vazio» de «não li»")


REGISTO_KB = ('{"date": "2026-01-01", "ticker": "NVDA", "headline": "h", '
              '"impacts": {"1": 0.0}, "embedding": null}')


# -- As bases vivem o PROCESSO, nao o ciclo ------------------------------------
# Medido a 2026-09-04: o `scan_news` corre a cada 60 s e recarregava tudo do disco de cada
# vez -- 10 968 registos da base viva, mais a do ano, mais uma sessao ONNX nova. Cerca de
# 44 MB retidos e pico de 187 MB de alocacoes Python POR MINUTO, num contentor de 512. O
# alocador do Python nao devolve arenas ao sistema operativo, logo o RSS subia e ficava:
# entre 518 e 970 MB, com R14 a cada poucos minutos.

def _sem_bases(r, tmp_path, monkeypatch):
    """Aponta as bases opcionais para ficheiros que nao existem e limpa a cache."""
    monkeypatch.setattr(r, "_LIVE_KB", tmp_path / "nao-existe.jsonl")
    monkeypatch.setattr(r, "_BACKFILL_META", tmp_path / "nem-esta.jsonl")
    monkeypatch.setattr(r, "_BACKFILL_VEC", tmp_path / "nem-esta.npy")
    monkeypatch.setattr(r, "_KBS_CACHE", {})


def test_kbs_nao_sao_recarregadas_quando_nada_muda(tmp_path, monkeypatch):
    """Duas chamadas seguidas sem alteracao nos ficheiros devolvem o MESMO objecto."""
    import scripts.run_alerts as r

    kb = tmp_path / "curada.jsonl"
    kb.write_text("", encoding="utf-8")
    _sem_bases(r, tmp_path, monkeypatch)
    assert r._kbs_cached(kb) is r._kbs_cached(kb), "recarregou sem nada ter mudado"


def test_kbs_recarregam_quando_o_ficheiro_muda(tmp_path, monkeypatch):
    """Controlo no sentido oposto: a maturacao acrescenta casos, e isso TEM de ser visto.

    Uma cache que nao invalida seria pior do que nao ter cache nenhuma: o sistema deixaria
    de ver os casos novos e ninguem daria por isso.
    """
    import time

    import scripts.run_alerts as r

    kb = tmp_path / "curada.jsonl"
    kb.write_text("", encoding="utf-8")
    _sem_bases(r, tmp_path, monkeypatch)

    primeira = r._kbs_cached(kb)
    assinatura = r._assinatura_kbs(kb)
    time.sleep(0.02)
    kb.write_text(REGISTO_KB, encoding="utf-8")
    assert r._assinatura_kbs(kb) != assinatura, "a assinatura nao viu a alteracao"
    assert r._kbs_cached(kb) is not primeira, "nao recarregou depois de o ficheiro mudar"


def test_embedder_carregado_uma_so_vez_por_processo(monkeypatch):
    """A sessao ONNX e cara e nao muda: uma por processo, nao uma por ciclo."""
    import pathlib as _pl

    import investigator.main as main_mod
    import scripts.run_alerts as r

    chamadas = []
    monkeypatch.setattr(r, "_RETRIEVAL_CACHE", {})

    def _falso(auto_download=True):
        chamadas.append(1)
        return _pl.Path("kb.jsonl"), object()

    monkeypatch.setattr(main_mod, "product_retrieval", _falso)
    assert r._retrieval_cached() is r._retrieval_cached()
    assert len(chamadas) == 1, f"product_retrieval chamado {len(chamadas)} vezes"
