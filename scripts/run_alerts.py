"""Runner de alertas agendado — varre uma watchlist e envia alertas explicáveis para o Telegram.

Lê `config/alerts.yaml` (definições não-secretas) e reutiliza as funções já validadas do
InvestiGator. Corre na **stack leve** (sem torch). Seguro por defeito: se o Telegram não estiver
configurado, imprime os alertas e sai com código 0 — assim um job agendado fica verde antes de
definires os segredos.

Uso:
    python scripts/run_alerts.py            # varre + envia (se o Telegram estiver configurado)
    python scripts/run_alerts.py --dry-run  # varre + imprime apenas, nunca envia

Pensado para ser chamado por `.github/workflows/alerts.yml` (cron) — ver docs/design/going_live.md.
"""

from __future__ import annotations

import argparse
import os
from datetime import date, timedelta
from pathlib import Path

import yaml

# Permitir correr como `python scripts/run_alerts.py` a partir da raiz do repo.
from investigator.console import force_utf8_stdout

_CONFIG = Path(__file__).resolve().parents[1] / "config" / "alerts.yaml"
_STATE = Path(__file__).resolve().parents[1] / "data" / "alerts_state.json"
# No workflow, INVESTIGATOR_HISTORY_PATH aponta para o checkout da branch `alerts-history`
# (ver .github/workflows/alerts.yml); localmente cai num ficheiro gitignored inofensivo.
_HISTORY = Path(os.environ.get(
    "INVESTIGATOR_HISTORY_PATH",
    str(Path(__file__).resolve().parents[1] / "data" / "alerts_history.jsonl"),
))
# KB VIVA: vive ao lado do histórico partilhado (mesma branch de dados `alerts-history`),
# por isso é publicada/lida pelos mesmos mecanismos (workflow + VM + app via raw URL).
_LIVE_PENDING = _HISTORY.parent / "live_pending.jsonl"
_LIVE_KB = _HISTORY.parent / "live_kb.jsonl"
# LOG DE PREDIÇÕES (loop de pós-validação M5.5): também na branch partilhada, para PERSISTIR
# entre corridas do Actions (o runner é efémero — antes o log era gitignored em data/ e nunca
# acumulava na nuvem; o loop de pós-fecho só corria no PC do aluno). Agora `git add -A` do
# workflow publica-o e o post_validate corre em cima dele ao fecho.
_PRED_LOG = _HISTORY.parent / "predictions_log.jsonl"


# ── Estado entre corridas (intradiário, anti-duplicado) ───────────────────────
# Com o cron a correr de 30 em 30 min durante o mercado, o runner tem de se lembrar do que
# JÁ alertou hoje (o job do Actions é efémero; o workflow persiste este ficheiro via cache).
def load_state(path: str | Path = _STATE, today: date | None = None) -> dict:
    """Lê o estado; se for de outro dia, zera as marcas do dia mas PRESERVA o offset do bot."""
    import json

    today = today or date.today()
    state = {"date": today.isoformat(), "alerted_market": [], "alerted_news": [],
             "news_count": {}, "opening_sent": False, "summary_sent": False, "bot_offset": None}
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        state["bot_offset"] = raw.get("bot_offset")
        if raw.get("date") == today.isoformat():
            state["alerted_market"] = list(raw.get("alerted_market", []))
            state["alerted_news"] = list(raw.get("alerted_news", []))
            state["news_count"] = dict(raw.get("news_count", {}))
            state["opening_sent"] = bool(raw.get("opening_sent", False))
            state["summary_sent"] = bool(raw.get("summary_sent", False))
    except (OSError, ValueError):
        pass  # sem estado (1.ª corrida do dia/da cache) → começa limpo
    return state


def save_state(state: dict, path: str | Path = _STATE) -> None:
    import json

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def news_key(ticker: str, text: str) -> str:
    """Chave estável de um alerta de notícia, calculada sobre o texto SEM tags (plain_text)
    — assim a VM, o Actions e o histórico partilhado produzem sempre a mesma chave."""
    import hashlib

    from investigator.explanation_engine.explainer import plain_text

    return hashlib.sha1(f"{ticker}|{plain_text(text)}".encode()).hexdigest()[:12]


def seed_state_from_shared_history(state: dict, entries: list, today: str) -> None:
    """Puro: semeia o estado com o que QUALQUER produtor já enviou hoje.

    Com dois produtores possíveis (a VM em modo --watch e o cron do Actions como rede de
    segurança), o estado local de cada um não chega — o histórico partilhado (branch
    `alerts-history`) é a memória comum que impede alertas duplicados no canal.
    """
    for e in entries:
        if e.date != today:
            continue
        if e.kind == "market" and e.ticker not in state["alerted_market"]:
            state["alerted_market"].append(e.ticker)
        elif e.kind == "news":
            k = e.key or news_key(e.ticker, e.text)
            if k not in state["alerted_news"]:
                state["alerted_news"].append(k)
                state["news_count"][e.ticker] = state["news_count"].get(e.ticker, 0) + 1
        elif e.kind == "summary":
            state["summary_sent"] = True
        elif e.kind == "open":
            state["opening_sent"] = True


def filter_new_alerts(market: list[tuple[str, str]], news: list[tuple[str, str]],
                      state: dict, max_per_ticker: int = 2) -> list[tuple[str, str]]:
    """Puro: mantém só o que ainda NÃO foi alertado hoje e marca-o no estado.

    Notícias têm um TETO por ticker por dia (`max_per_ticker`, config
    `news.max_per_ticker_per_day`) — anti-fadiga: 12 alertas/dia do mesmo ticker treinam
    o utilizador a ignorar o canal.
    """
    keep: list[tuple[str, str]] = []
    for ticker, text in market:
        if ticker not in state["alerted_market"]:
            state["alerted_market"].append(ticker)
            keep.append((ticker, text))
        else:
            print(f"[{ticker}] já alertado hoje — sem repetição.")
    for ticker, text in news:
        k = news_key(ticker, text)
        if k in state["alerted_news"]:
            print(f"[noticias {ticker}] já alertada hoje — sem repetição.")
            continue
        if state["news_count"].get(ticker, 0) >= max_per_ticker:
            print(f"[noticias {ticker}] teto diário atingido ({max_per_ticker}) "
                  "— sem mais alertas deste ticker hoje.")
            continue
        state["alerted_news"].append(k)
        state["news_count"][ticker] = state["news_count"].get(ticker, 0) + 1
        keep.append((ticker, text))
    return keep


def _log_decision_safe(news_date: str, ticker: str, headline: str,
                       scored: tuple | None, gate: float | None, kept: bool) -> None:
    """Regista a decisão de notícia para o loop de pós-validação (M5.5, `scripts/
    post_validate.py`). Ficheiro local gitignored; uma falha aqui NUNCA pára o runner."""
    try:
        from investigator.triage.postval import log_decision

        log_decision(_PRED_LOG, news_date=news_date, ticker=ticker, headline=headline,
                     prob=(float(scored[0]) if scored is not None else None),
                     gate=(gate if scored is not None else None), kept=kept)
    except Exception as exc:  # noqa: BLE001
        print(f"[postval] registo falhou (ignorado): {type(exc).__name__}: {exc}")


def load_config(path: str | Path = _CONFIG) -> dict:
    """Carrega o ficheiro de definições YAML."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def news_is_fresh(news_date: str, today: date, max_age_days: int = 2) -> bool:
    """Puro: só alertamos notícias recentes.

    O scan apanha "a mais recente da última semana"; sem este filtro a MESMA manchete
    podia alertar dias a fio (spam = fadiga de alertas). 2 dias por defeito cobre o
    fim de semana (notícia de sábado ainda alerta na segunda).
    """
    try:
        d = date.fromisoformat(str(news_date)[:10])
    except ValueError:
        return False
    return 0 <= (today - d).days <= max_age_days


def bar_is_fresh(last_bar: date, today: date) -> bool:
    """Puro: só perguntamos "hoje é anómalo?" se a última barra de preços é de HOJE.

    Evita dois defeitos reais: repetir num feriado de segunda o alerta da barra de sexta
    (já enviado na sexta) e "avaliar" dados estagnados quando o mercado não abriu.
    """
    return last_bar >= today


def build_market_alerts(results: list[tuple[str, object]]) -> list[str]:
    """Puro: dado [(ticker, AnomalyResult)], devolve os textos de alerta só das anomalias."""
    from investigator.explanation_engine.explainer import explain_anomaly

    return [explain_anomaly(ticker, res) for ticker, res in results if res.is_anomaly]


def _hist_cached(ticker: str, cache: dict) -> object:
    """UMA busca de preços por ticker por ciclo (fecho + intradiário partilham a cadeia
    de fallback de `get_price_history` — sem isto, cada ciclo duplicava as chamadas)."""
    if ticker not in cache:
        from investigator.market_data.prices import get_price_history

        cache[ticker] = get_price_history(ticker)
    return cache[ticker]


def collect_market_results(cfg: dict, cache: dict | None = None) -> list[tuple[str, object]]:
    """Busca preços e avalia cada ticker; devolve [(ticker, AnomalyResult)] dos dias frescos.

    Base tanto dos alertas de anomalia como do resumo diário de fecho — uma só passagem
    pelos preços por corrida.
    """
    from investigator.anomaly_detector.detector import detect_latest
    from investigator.market_data.prices import log_returns

    m = cfg.get("market", {})
    if not m.get("enabled", False):
        return []
    cache = {} if cache is None else cache
    window = int(m.get("window", 20))
    threshold = float(m.get("threshold", 3.0))
    require_fresh = bool(m.get("require_fresh_bar", True))
    results: list[tuple[str, object]] = []
    for ticker in m.get("tickers", []):
        try:
            hist = _hist_cached(ticker, cache)
            last_bar = hist.index[-1].date()
            if require_fresh and not bar_is_fresh(last_bar, date.today()):
                print(f"[{ticker}] última barra é de {last_bar} (sem sessão nova hoje) "
                      "— sem avaliação (anti-duplicado).")
                continue
            returns = log_returns(hist["Close"])
            results.append((ticker, detect_latest(returns, window=window, threshold=threshold)))
        except Exception as exc:  # noqa: BLE001  (um ticker/rede a falhar não pode parar a varredura)
            print(f"[saltar {ticker}] {type(exc).__name__}: {exc}")
    return results


def scan_market(cfg: dict) -> list[tuple[str, str]]:
    """Deteta anomalias e devolve pares (ticker, texto de alerta)."""
    results = collect_market_results(cfg)
    # Mesmo filtro e mesma ordem de build_market_alerts (puro, testado) → zip alinha por construção.
    tickers_anomalos = [t for t, r in results if r.is_anomaly]
    return list(zip(tickers_anomalos, build_market_alerts(results), strict=True))


def build_daily_summary(results: list[tuple[str, object]], threshold: float) -> str:
    """Puro: a mensagem única de fecho — o batimento cardíaco diário do canal.

    Sem isto, em dias calmos o canal ficava mudo sobre o mercado e o utilizador não via o
    detetor a trabalhar. Uma mensagem por dia: cada ticker com o movimento e o z-score,
    anomalias destacadas; honesto quando não há nenhuma.
    """
    if not results:
        return ""
    from investigator.explanation_engine.explainer import direction_icon

    ordenados = sorted(results, key=lambda tr: -abs(tr[1].z_score))
    linhas = ["📊 <b>Daily close summary</b>"]
    # Hierarquia visual (UX 2026-07-12): movers em destaque, um por linha; os calmos
    # (<1% e sem anomalia) comprimidos numa linha só — 10 linhas monótonas não se leem.
    # A seta segue SEMPRE o sinal do movimento (direction_icon, fonte única): anomalias
    # levam os triângulos de alerta 🔺/🔻; os movers normais as setas finas ⬆/⬇.
    calmos: list[str] = []
    for ticker, r in ordenados:
        if r.is_anomaly:
            icon = direction_icon(r.last_return)
            linhas.append(f"{icon} {ticker}: {r.last_return * 100:+.2f}% (z {r.z_score:+.2f})")
        elif abs(r.last_return) >= 0.01:
            seta = "⬆" if r.last_return > 0 else "⬇"
            linhas.append(f"{seta} {ticker}: {r.last_return * 100:+.2f}% (z {r.z_score:+.2f})")
        else:
            calmos.append(f"{ticker} {r.last_return * 100:+.1f}%")
    if calmos:
        linhas.append("• Quiet: " + " · ".join(calmos))
    n_anom = sum(1 for _, r in results if r.is_anomaly)
    if n_anom:
        linhas.append(f"{n_anom} anomaly(ies) today (|z| ≥ {threshold:g}); alerted above.")
    else:
        linhas.append(f"No anomalies today (threshold |z| ≥ {threshold:g}); a normal day.")
    linhas.append("<i>An observed snapshot of the watchlist, not advice.</i>")
    return "\n".join(linhas)


def build_opening_note(results: list[tuple[str, object]]) -> str:
    """Puro: a mensagem de ABERTURA — como a watchlist está a abrir vs o fecho de ontem.

    O par matinal do resumo de fecho (o aluno pediu "um alerta de abertura"): dá o pulso da
    manhã (gaps overnight + primeiros minutos da sessão) a partir dos resultados INTRADIÁRIOS
    (cotação ao vivo vs fecho anterior). Sem previsão — só o que já se observa.
    """
    if not results:
        return ""
    from investigator.explanation_engine.explainer import direction_icon

    ordenados = sorted(results, key=lambda tr: -abs(tr[1].last_return))
    linhas = ["🔔 <b>Market open · watchlist snapshot</b>"]
    calmos: list[str] = []
    for ticker, r in ordenados:
        if abs(r.last_return) >= 0.01:
            icon = direction_icon(r.last_return)
            linhas.append(f"{icon} {ticker}: {r.last_return * 100:+.2f}% vs yesterday's close")
        else:
            calmos.append(f"{ticker} {r.last_return * 100:+.1f}%")
    if calmos:
        linhas.append("• Flat at the open: " + " · ".join(calmos))
    linhas.append("<i>How the US session is opening vs yesterday's close. "
                  "An observed snapshot, not advice.</i>")
    return "\n".join(linhas)


def maybe_opening_note(state: dict, results: list[tuple[str, object]],
                       hour_utc: int) -> str | None:
    """Puro: a nota de abertura na 1.ª corrida da janela de abertura (14–15 UTC), 1×/dia.

    A janela cobre verão (abertura 13:30 UTC ⇒ já aberto às 14h) e inverno (abertura 14:30 ⇒
    aberto às 15h). Marca `opening_sent` (partilhado entre corridas e produtores, como o resumo).
    """
    if hour_utc not in (14, 15) or state.get("opening_sent") or not results:
        return None
    state["opening_sent"] = True
    return build_opening_note(results)


def maybe_daily_summary(state: dict, results: list[tuple[str, object]],
                        threshold: float, hour_utc: int) -> str | None:
    """Puro: devolve o resumo de fecho na 1.ª corrida com hora UTC ≥ 21, uma vez por dia.

    Marca `summary_sent` no estado (partilhado entre corridas e, via histórico, entre
    produtores). Sem resultados frescos (mercado fechado) não há nada a resumir.
    """
    if hour_utc < 21 or state.get("summary_sent") or not results:
        return None
    state["summary_sent"] = True
    return build_daily_summary(results, threshold)


def apply_materiality(text: str, scored: tuple | None, gate: float) -> str | None:
    """Puro: aplica o gate da triagem aprendida a um alerta de notícia (ML_PLAN M5).

    `scored` = (probabilidade, contribuições) do modelo só-contexto, ou None quando não foi
    possível pontuar (sem histórico suficiente) — nesse caso FAIL-OPEN: o alerta segue como
    sempre, sem linha. Devolve None se o gate suprimir o alerta; caso contrário o texto com
    a linha de materialidade (honesta: "triage evidence, not a forecast").
    """
    if scored is None:
        return text
    from investigator.triage.explain import materiality_line

    prob, contribs = scored
    if prob < gate:
        return None
    return text + "\n" + materiality_line(prob, contribs)


def precedents_are_strong(precedents: list, min_similarity: float) -> bool:
    """Puro: há pelo menos um precedente com similaridade ≥ chão?

    Evidência fraca (sim ~0,35-0,45) parecia aleatória ao utilizador — com razão. Sem um
    precedente forte, é mais honesto NÃO alertar do que mostrar vizinhos irrelevantes.
    """
    return any(score >= min_similarity for _, score in precedents)


def scan_news(cfg: dict) -> list[tuple[str, str]]:
    """Opcional: notícias recentes por ticker -> pares (ticker, alerta) (best-effort).

    Qualidade primeiro (revisão 2026-07-11, sobre 27 alertas reais): (1) filtro de
    RELEVÂNCIA — a manchete tem de mencionar a empresa e não pode ser boilerplate de
    mercado; (2) chão de SIMILARIDADE — sem um precedente forte, não há alerta; (3) o
    gate de materialidade regista o P de cada ticker no log (diagnóstico visível).
    """
    n = cfg.get("news", {})
    if not n.get("enabled", False):
        return []
    from investigator import config
    from investigator.explanation_engine.explainer import explain_news_impact
    from investigator.historical_kb.knowledge_base import HistoricalKB
    from investigator.live_kb import merged_precedents
    from investigator.news_fetcher.fetcher import fetch_finnhub_company_news
    from investigator.news_fetcher.relevance import is_relevant

    if not config.FINNHUB_API_KEY:
        print("[noticias] FINNHUB_API_KEY em falta — a saltar o scan de noticias.")
        return []
    horizon = int(n.get("horizon", 5))
    top_k = int(n.get("top_k", 3))
    min_sim = float(n.get("min_similarity", 0.45))
    half_life = float(n.get("recency_half_life_days", 365))
    max_prec_age = n.get("max_precedent_age_days")
    max_prec_age = int(max_prec_age) if max_prec_age is not None else None

    # Triagem aprendida (off por defeito): só ativa com min_materiality definido E modelo
    # presente. Sem modelo, avisa e segue com o comportamento de sempre.
    gate = n.get("min_materiality")
    bundle = None
    if gate is not None:
        from investigator.triage.infer import load_context_bundle

        bundle = load_context_bundle()
        if bundle is None:
            print("[triagem] models/triage_context_lr.joblib em falta — gate ignorado.")
        else:
            gate = float(gate)

    # KB + embedder decididos UMA vez (semântico MiniLM-ONNX com fail-open para a amostra;
    # em Actions o modelo vem da cache do workflow, senão desce ~23 MB na primeira corrida).
    # A KB VIVA (casos recentes maturados neste próprio runner) entra em primeiro na fusão:
    # "timeline matters" — a idade desempata a favor do recente, o cosseno decide o tema.
    from investigator.main import product_retrieval

    kb_path, embedder = product_retrieval(auto_download=True)
    kbs = []
    if _LIVE_KB.exists():
        try:
            kb_viva = HistoricalKB.load(_LIVE_KB)
            if len(kb_viva):
                kbs.append(kb_viva)
                print(f"[kb-viva] {len(kb_viva)} caso(s) recente(s) em uso.")
        except Exception as exc:  # noqa: BLE001
            print(f"[kb-viva] ilegível (ignorada): {type(exc).__name__}: {exc}")
    kbs.append(HistoricalKB.load(kb_path))

    end = date.today().isoformat()
    start = (date.today() - timedelta(days=7)).isoformat()
    alerts: list[tuple[str, str]] = []
    for ticker in n.get("tickers", []):
        try:
            items = fetch_finnhub_company_news(ticker, start, end)
            # Filtro de relevância ANTES de escolher: mata as manchetes mal etiquetadas do
            # Finnhub (lei/escritórios, resumos "S&P500 movers"…) que sujavam o canal.
            relevantes = [i for i in items if is_relevant(i.headline, ticker)]
            if items and not relevantes:
                print(f"[noticias {ticker}] {len(items)} manchete(s), nenhuma relevante "
                      "(mal etiquetadas/boilerplate) — sem alerta.")
            if not relevantes:
                continue
            # KB viva: toda a manchete relevante é candidata a precedente futuro (captura
            # fail-open; matura dias depois, quando o impacto for observável).
            _capture_live_safe(relevantes, embedder)
            latest = max(relevantes, key=lambda it: it.date)  # a mais recente RELEVANTE
            max_age = int(n.get("max_age_days", 2))
            if not news_is_fresh(latest.date, date.today(), max_age):
                print(f"[noticias {ticker}] mais recente é de {latest.date} (>{max_age} dias) "
                      "— sem alerta (anti-repetição).")
                continue
            precedents = merged_precedents(
                latest.headline, kbs, embedder, top_k=top_k, today=date.today(),
                half_life_days=half_life, max_age_days=max_prec_age,
            )
            text = explain_news_impact(
                ticker, latest.headline, precedents, horizon=horizon,
                date=latest.date, today=date.today().isoformat(),
            )
            if not precedents_are_strong(precedents, min_sim):
                best = max((s for _, s in precedents), default=0.0)
                print(f"[noticias {ticker}] melhor precedente sim {best:.2f} < {min_sim:.2f} "
                      "— evidência fraca demais, sem alerta.")
                continue
            if bundle is not None:
                from investigator.market_data.prices import get_price_history
                from investigator.triage.infer import score_latest

                scored = score_latest(
                    bundle, get_price_history(ticker)["Close"], latest.headline, ticker
                )
                if scored is not None:
                    print(f"[triagem {ticker}] P(anormal)={scored[0]:.0%} "
                          f"(gate {gate:.0%})")
                gated = apply_materiality(text, scored, gate)
                _log_decision_safe(latest.date, ticker, latest.headline,
                                   scored, gate, kept=gated is not None)
                if gated is None:
                    print(f"[triagem {ticker}] alerta de noticia suprimido pelo gate.")
                    continue
                text = gated
            else:
                _log_decision_safe(latest.date, ticker, latest.headline,
                                   None, None, kept=True)
            alerts.append((ticker, text))
        except Exception as exc:  # noqa: BLE001
            print(f"[saltar noticias {ticker}] {type(exc).__name__}: {exc}")
    return alerts


def _capture_live_safe(items: list, embedder) -> None:
    """Captura manchetes relevantes para a KB viva (pendentes de maturação). Fail-open.

    Só captura com o embedder SEMÂNTICO (guarda R1: embeddings hashing 64-d misturados com
    a KB 384-d dariam vizinhos errados). O summary do Finnhub entra SÓ no embedding, nunca
    é persistido (governança §5.4).
    """
    try:
        if not getattr(embedder, "semantic", False):
            return
        from investigator.live_kb import (
            PendingNews,
            add_pending,
            embed_text,
            load_pending,
            save_pending,
        )

        existentes = load_pending(_LIVE_PENDING)
        chaves = {e.key for e in existentes}
        novos_items = [i for i in items if news_key(i.ticker, i.headline) not in chaves]
        if not novos_items:
            return
        textos = [embed_text(i.headline, getattr(i, "summary", "")) for i in novos_items]
        vetores = embedder.encode(textos)
        novos = [
            PendingNews(date=i.date, ticker=i.ticker, headline=i.headline,
                        key=news_key(i.ticker, i.headline),
                        embedding=[round(float(x), 5) for x in vec])
            for i, vec in zip(novos_items, vetores, strict=True)
        ]
        save_pending(add_pending(existentes, novos), _LIVE_PENDING)
        print(f"[kb-viva] +{len(novos)} pendente(s) capturado(s).")
    except Exception as exc:  # noqa: BLE001
        print(f"[kb-viva] captura falhou (ignorada): {type(exc).__name__}: {exc}")


def _mature_live_safe(today: date | None = None) -> None:
    """Matura pendentes cujo impacto já é observável e move-os para a KB viva. Fail-open."""
    try:
        from investigator.live_kb import append_records, load_pending, mature_ready, save_pending
        from investigator.market_data.prices import load_close_series

        today = today or date.today()
        pending = load_pending(_LIVE_PENDING)
        prontos = [e for e in pending
                   if (today - date.fromisoformat(e.date)).days >= 8]
        if not prontos:
            return
        tickers = sorted({e.ticker for e in prontos})
        start = (min(date.fromisoformat(e.date) for e in prontos)
                 - timedelta(days=5)).isoformat()
        closes = load_close_series(tickers, start, (today + timedelta(days=1)).isoformat())
        matured, still = mature_ready(pending, closes, today)
        if matured:
            append_records(matured, _LIVE_KB)
            save_pending(still, _LIVE_PENDING)
            print(f"[kb-viva] {len(matured)} caso(s) maturado(s) → live_kb.jsonl "
                  f"({len(still)} pendente(s)).")
    except Exception as exc:  # noqa: BLE001
        print(f"[kb-viva] maturação falhou (ignorada): {type(exc).__name__}: {exc}")


def is_us_market_session(now_utc) -> bool:
    """Puro: estamos dentro da sessão US (com folga)? Seg-sex, 13:00–21:30 UTC.

    Fora da sessão, a cotação `c` do Finnhub é o ÚLTIMO negócio (ex.: o fecho de sexta) —
    avaliar isso ao sábado re-alertaria o movimento de ontem como se fosse "em curso".
    A janela cobre verão e inverno (abertura 13:30/14:30, fecho 20:00/21:00 UTC).
    """
    if now_utc.weekday() >= 5:
        return False
    minutos = now_utc.hour * 60 + now_utc.minute
    return 13 * 60 <= minutos <= 21 * 60 + 30


def collect_intraday_results(cfg: dict, cache: dict | None = None) -> list[tuple[str, object]]:
    """Avalia o movimento DE HOJE em curso (cotação Finnhub) vs a norma diária, por ticker.

    Antes só corria no modo --watch (VM); desde 2026-07-13 corre TAMBÉM nas corridas
    agendadas (Actions, de 30 em 30 min) — é o caminho de mercado que NÃO depende do
    yfinance: a cotação vem do Finnhub (autenticado, fiável) e a norma vem do histórico
    diário, que NÃO precisa da barra de hoje (só de dias completos). Auto-protege-se:
    fora da sessão US, sem chave ou desligado → []. Devolve TODOS os tickers avaliados
    (não só anomalias) — o resumo diário também se serve daqui quando o fecho está cego.
    """
    from datetime import UTC, datetime

    m = cfg.get("market", {})
    intra = (m.get("intraday") or {})
    if not (m.get("enabled", False) and intra.get("enabled", False)):
        return []
    if not is_us_market_session(datetime.now(UTC)):
        return []  # fora da sessão, a cotação é estagnada — nada "em curso" a avaliar
    from investigator import config
    from investigator.anomaly_detector.detector import detect_intraday
    from investigator.market_data.prices import log_returns
    from investigator.news_fetcher.fetcher import fetch_finnhub_quote

    if not config.FINNHUB_API_KEY:
        return []
    cache = {} if cache is None else cache
    window = int(m.get("window", 20))
    threshold = float(intra.get("threshold", m.get("threshold", 3.0)))
    results: list[tuple[str, object]] = []
    for ticker in m.get("tickers", []):
        try:
            atual, fecho_anterior = fetch_finnhub_quote(ticker)
            running = atual / fecho_anterior - 1.0
            close = _hist_cached(ticker, cache)["Close"]
            # A norma usa só dias COMPLETOS: se a última barra é a de hoje (parcial,
            # durante a sessão), sai da série antes de calcular retornos.
            if close.index[-1].date() >= date.today():
                close = close.iloc[:-1]
            returns = log_returns(close)
            results.append(
                (ticker, detect_intraday(running, returns, window=window, threshold=threshold))
            )
        except Exception as exc:  # noqa: BLE001  (um ticker a falhar não pára a varredura)
            print(f"[intradiario {ticker}] {type(exc).__name__}: {exc}")
    return results


def build_intraday_alerts(results: list[tuple[str, object]]) -> list[tuple[str, str]]:
    """Puro: [(ticker, texto)] só das anomalias intradiárias. Dedup pelo `alerted_market`
    de sempre (1 alerta de mercado/ticker/dia — o fecho não repete o intradiário)."""
    from investigator.explanation_engine.explainer import explain_intraday

    return [(t, explain_intraday(t, r)) for t, r in results if r.is_anomaly]


def _attach_sector_safe(ticker: str, alert_text: str, moves: dict[str, float]) -> str:
    """Anexa a linha 'Sector check' a um alerta de mercado (fail-open: sem dados de pares
    ou com erro, o alerta segue intacto — a linha é contexto, nunca condição)."""
    try:
        from investigator.explanation_engine.explainer import sector_context_line

        line = sector_context_line(ticker, moves)
        return f"{alert_text}\n{line}" if line else alert_text
    except Exception as exc:  # noqa: BLE001
        print(f"[setor {ticker}] falhou (alerta segue sem linha): {type(exc).__name__}: {exc}")
        return alert_text


def _investigate_anomaly_safe(ticker: str, alert_text: str) -> str:
    """Investigação cruzada: procura a notícia relevante mais recente (48h) que possa
    explicar a anomalia e anexa-a ao alerta; sem notícia, di-lo honestamente.

    Fail-open: sem FINNHUB_API_KEY ou com erro de rede, devolve o alerta original intacto.
    """
    try:
        from investigator import config
        from investigator.explanation_engine.explainer import attach_news_context
        from investigator.news_fetcher.fetcher import fetch_finnhub_company_news
        from investigator.news_fetcher.relevance import is_relevant

        if not config.FINNHUB_API_KEY:
            return alert_text
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=2)).isoformat()
        items = fetch_finnhub_company_news(ticker, start, end)
        relevantes = [i for i in items if is_relevant(i.headline, ticker)]
        if relevantes:
            recente = max(relevantes, key=lambda it: it.date)
            return attach_news_context(alert_text, recente.headline,
                                       news_date=recente.date, today=end)
        return attach_news_context(alert_text, None)
    except Exception as exc:  # noqa: BLE001
        print(f"[investigar {ticker}] falhou (alerta segue sem contexto): "
              f"{type(exc).__name__}: {exc}")
        return alert_text


def _record_history_safe(alerts: list[tuple[str, str]], today: str,
                         path: str | Path = _HISTORY) -> None:
    """Regista os alertas REALMENTE enviados no histórico partilhado — a app lê este ficheiro
    em vez de recalcular, garantindo que mostra exatamente o que o Telegram recebeu.

    Fail-open (mesmo padrão de `_log_decision_safe`): um erro aqui nunca pode impedir o envio
    real ao Telegram nem derrubar o runner.
    """
    try:
        from investigator.alerts_history import (
            HistoryEntry,
            append_and_trim,
            classify_kind,
            load_jsonl,
            save_jsonl,
        )
        from investigator.explanation_engine.explainer import plain_text

        new = []
        for ticker, text in alerts:
            kind = classify_kind(text)
            new.append(HistoryEntry(
                date=today, ticker=ticker, kind=kind, text=plain_text(text),
                key=news_key(ticker, text) if kind == "news" else "",
            ))
        save_jsonl(append_and_trim(load_jsonl(path), new), path)
    except Exception as exc:  # noqa: BLE001
        print(f"[historico] registo falhou (ignorado): {type(exc).__name__}: {exc}")


def _push_history_safe(path: str | Path = _HISTORY) -> None:
    """Publica o histórico na branch `alerts-history` a partir de uma máquina própria (VM).

    Só ativo com INVESTIGATOR_HISTORY_GIT=1 e com o ficheiro dentro de um checkout git da
    branch de dados (ver docs/design/vm_watch.md). No Actions este passo é feito pelo próprio
    workflow — aqui é o equivalente para o modo --watch. Fail-open total.
    """
    import os

    if os.environ.get("INVESTIGATOR_HISTORY_GIT") != "1":
        return
    import subprocess

    d = Path(path).resolve().parent
    try:
        def git(*a: str) -> None:
            subprocess.run(["git", *a], cwd=d, check=True, capture_output=True, timeout=60)

        status = subprocess.run(["git", "status", "--porcelain"], cwd=d, check=True,
                                capture_output=True, text=True, timeout=30)
        if not status.stdout.strip():
            return
        git("add", Path(path).name)
        git("commit", "-m", "Alertas: atualização automática do histórico partilhado")
        git("pull", "--rebase")
        git("push")
        print("[historico] publicado na branch alerts-history.")
    except Exception as exc:  # noqa: BLE001
        print(f"[historico] push falhou (ignorado): {type(exc).__name__}: {exc}")


def _fetch_shared_history_safe(cfg: dict) -> list:
    """Histórico partilhado (fail-open) — a memória comum entre VM e Actions."""
    try:
        from investigator.alerts_history import fetch_remote

        url = (cfg.get("public", {}) or {}).get("history_url")
        return fetch_remote(str(url)) if url else []
    except Exception:  # noqa: BLE001
        return []


def process_bot_commands(state: dict, bot_cfg: dict, *, dry_run: bool) -> None:
    """Fase B SEM servidor: processa em lote os comandos enviados ao bot desde a última corrida.

    Com o cron intradiário, quem escrever /watch TSLA recebe a resposta na corrida seguinte
    (≤30 min em horário de mercado). Não é instantâneo e dizemo-lo com honestidade — mas
    funciona sem nenhuma máquina do operador. (Para respostas imediatas: scripts/run_bot.py.)
    Fail-open: qualquer erro deixa o runner seguir; o offset fica no estado partilhado.
    """
    if not bot_cfg.get("enabled", False):
        return
    if dry_run:
        print("[bot] dry-run — comandos pendentes não são processados nem respondidos.")
        return
    try:
        from investigator import config
        from investigator.telegram_bot import store
        from investigator.telegram_bot.commands import handle_command
        from investigator.telegram_bot.interactive import extract_command, poll_updates
        from investigator.telegram_bot.sender import send_message

        if not config.TELEGRAM_BOT_TOKEN:
            print("[bot] sem TELEGRAM_BOT_TOKEN — comandos saltados.")
            return
        updates = poll_updates(config.TELEGRAM_BOT_TOKEN, state.get("bot_offset"), timeout_s=1)
        if not updates:
            return
        conn = store.connect(Path(bot_cfg.get("db", store.DEFAULT_DB)))
        for upd in updates:
            state["bot_offset"] = int(upd.get("update_id", 0)) + 1
            par = extract_command(upd)
            if par is None:
                continue
            chat_id, text = par
            reply = handle_command(text, chat_id, conn)
            send_message(reply, chat_id=chat_id)
        print(f"[bot] {len(updates)} update(s) processado(s) em lote.")
    except Exception as exc:  # noqa: BLE001  (os comandos nunca podem partir o runner)
        print(f"[bot] processamento de comandos falhou (ignorado): {type(exc).__name__}: {exc}")


def _fanout_safe(alerts: list[tuple[str, str]], bot_cfg: dict, *, dry_run: bool) -> None:
    """Fase B (off por defeito): distribui cada alerta pelos subscritores do ticker.

    Fail-open total: sem `bot.enabled`, sem base de subscritores ou com qualquer erro, o
    runner comporta-se exatamente como sempre (só canal). Nunca levanta exceção.
    """
    if not bot_cfg.get("enabled", False):
        return
    try:
        from investigator.telegram_bot import store

        db = Path(bot_cfg.get("db", store.DEFAULT_DB))
        if not db.exists():
            print("[bot] sem base de subscritores (corre scripts/run_bot.py) — fan-out saltado.")
            return
        conn = store.connect(db)
        enviados = 0
        for ticker, text in alerts:
            for chat in store.subscribers_of(conn, ticker):
                if dry_run:
                    print(f"[bot dry-run] enviaria {ticker} a {chat}")
                    continue
                from investigator.telegram_bot.sender import send_message

                send_message(text, chat_id=chat)
                enviados += 1
        if not dry_run:
            print(f"[bot] fan-out: {enviados} envio(s) a subscritores.")
    except Exception as exc:  # noqa: BLE001  (o fan-out nunca pode partir o runner)
        print(f"[bot] fan-out falhou (ignorado): {type(exc).__name__}: {exc}")


def run_cycle(cfg: dict, *, dry_run: bool, watch: bool = False) -> int:
    """Um ciclo completo de varredura (comandos do bot → scans → filtros → envio → registo).

    Reutilizado pelo modo agendado (1 ciclo por invocação — Actions) e pelo modo --watch
    (loop contínuo na VM/PC). A deteção intradiária corre em AMBOS desde 2026-07-13
    (auto-protegida por sessão/chave/config); `watch` fica na assinatura por
    compatibilidade e para diferenciações futuras. Devolve o nº de mensagens da corrida.
    """
    _ = watch  # ver docstring
    from datetime import UTC, datetime

    bot_cfg = cfg.get("bot", {}) or {}
    state = load_state()
    process_bot_commands(state, bot_cfg, dry_run=dry_run)

    # Memória partilhada entre produtores (VM + Actions): o que QUALQUER um já enviou hoje
    # não se repete — sem isto, dois produtores duplicariam alertas no canal.
    seed_state_from_shared_history(state, _fetch_shared_history_safe(cfg), state["date"])

    # KB viva: maturar pendentes cujo impacto (+5d) já é observável — ANTES dos scans,
    # para os casos recém-maturados contarem já como precedentes nesta corrida.
    _mature_live_safe()

    cache: dict[str, object] = {}  # 1 busca de preços por ticker por ciclo (fecho+intradiário)
    market_results = collect_market_results(cfg, cache)
    tickers_anomalos = [t for t, r in market_results if r.is_anomaly]
    market_alerts = list(zip(tickers_anomalos, build_market_alerts(market_results),
                             strict=True))
    # Deteção intradiária (Actions E --watch desde 2026-07-13): o movimento EM CURSO via
    # cotação Finnhub — o caminho de mercado que não depende do yfinance. O dedup do
    # filter_new_alerts (1 alerta de mercado/ticker/dia) evita que o fecho repita o
    # intradiário do mesmo dia.
    intra_results = collect_intraday_results(cfg, cache)
    market_alerts.extend(build_intraday_alerts(intra_results))
    # Contexto setorial ("a NVIDIA mexe com o setor"): usa SÓ os movimentos já buscados
    # nesta varredura — fecho de hoje quando existe, senão o movimento em curso.
    moves = {t: r.last_return for t, r in market_results}
    for t, r in intra_results:
        moves.setdefault(t, r.last_return)
    market_alerts = [(t, _attach_sector_safe(t, text, moves)) for t, text in market_alerts]
    # Investigação cruzada (anomalia → notícia): o comportamento do trader profissional —
    # vê o movimento, procura a causa. Fail-open: sem rede/chave, o alerta segue sem contexto.
    market_alerts = [(t, _investigate_anomaly_safe(t, text)) for t, text in market_alerts]
    max_per = int((cfg.get("news") or {}).get("max_per_ticker_per_day", 2))
    alerts = filter_new_alerts(market_alerts, scan_news(cfg), state, max_per)

    threshold = float((cfg.get("market") or {}).get("threshold", 3.0))
    hora_utc = datetime.now(UTC).hour
    # Nota de ABERTURA (o par matinal do resumo): como a watchlist abriu vs o fecho de ontem,
    # a partir da cotação intradiária. 1×/dia na janela de abertura (14–15 UTC).
    opening = maybe_opening_note(state, intra_results, hora_utc)
    # Resumo de FECHO: preferir os resultados de fecho; quando o fecho está cego (fontes
    # diárias sem a barra de hoje), os resultados intradiários servem — às 21h+ UTC a
    # sessão já fechou e a cotação Finnhub É o fecho do dia.
    summary = maybe_daily_summary(state, market_results or intra_results, threshold, hora_utc)

    if not dry_run:
        save_state(state)  # persiste marcas do dia + offset do bot (cache no Actions)
    else:
        print("[estado] dry-run — estado não gravado (não interfere com a corrida real).")

    mensagens = alerts + [("MARKET", m) for m in (opening, summary) if m]
    if not mensagens:
        print("Sem alertas novos nesta corrida (nenhuma anomalia nova acima do limiar).")
        return 0

    from investigator import config

    can_send = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID) and not dry_run
    from investigator.explanation_engine.explainer import plain_text

    falhas = 0
    for _ticker, text in mensagens:
        print("-" * 60)
        print(plain_text(text))
        if can_send:
            from investigator.telegram_bot.sender import send_message

            # Um envio falhado (rede/Telegram intermitente) não pode abortar o ciclo nem
            # impedir as mensagens seguintes: o modo agendado (Actions) sairia com código
            # de erro e as restantes ficariam por entregar. Falha-suave e continua.
            try:
                send_message(text)
            except Exception as exc:  # noqa: BLE001
                falhas += 1
                print(f"[!] Falha ao enviar (o ciclo continua): {exc}")

    _fanout_safe(alerts, bot_cfg, dry_run=dry_run)  # fan-out só de alertas por ticker

    if can_send:
        _record_history_safe(mensagens, date.today().isoformat())
        _push_history_safe()  # só ativo na VM (INVESTIGATOR_HISTORY_GIT=1); fail-open
        entregues = len(mensagens) - falhas
        extra = f" ({falhas} falha[s] de envio)" if falhas else ""
        print(f"\n[{entregues}/{len(mensagens)} mensagem(ns) enviada(s) para o Telegram{extra}]")
    else:
        why = "modo --dry-run" if dry_run else "Telegram nao configurado (nada enviado)"
        print(f"\n[{len(mensagens)} mensagem(ns); {why}]")
    return len(mensagens)


def watch_loop(interval_s: int, *, dry_run: bool) -> None:
    """Modo vigia (VM/PC): ciclo contínuo a cada ~interval_s com jitter e paragem limpa.

    Latência de minutos em vez do cron best-effort do GitHub (~1-2h na prática). O estado
    local persiste no disco e o dedup partilhado impede duplicados com o cron de segurança.
    """
    import random
    import signal
    import time

    stop = {"flag": False}

    def _parar(_sig, _frame) -> None:
        stop["flag"] = True

    signal.signal(signal.SIGINT, _parar)
    signal.signal(signal.SIGTERM, _parar)
    print(f"[watch] vigia contínuo: 1 ciclo a cada ~{interval_s}s (SIGTERM/Ctrl+C para parar)")
    while not stop["flag"]:
        try:
            # reler config permite ajustar a quente; watch=True liga a deteção intradiária
            run_cycle(load_config(), dry_run=dry_run, watch=True)
        except Exception as exc:  # noqa: BLE001  (um ciclo falhado nunca mata o vigia)
            print(f"[watch] ciclo falhou (continua): {type(exc).__name__}: {exc}")
        fim = time.monotonic() + interval_s + random.uniform(0, interval_s * 0.2)
        while not stop["flag"] and time.monotonic() < fim:
            time.sleep(1)
    print("[watch] terminado com graça.")


def main() -> int:
    force_utf8_stdout()
    parser = argparse.ArgumentParser(description="InvestiGator — runner de alertas")
    parser.add_argument("--dry-run", action="store_true", help="varre e imprime; nunca envia")
    parser.add_argument("--watch", action="store_true",
                        help="modo vigia: loop contínuo (VM/PC) em vez de 1 ciclo")
    parser.add_argument("--interval", type=int, default=300,
                        help="segundos entre ciclos no modo --watch (defeito: 300)")
    args = parser.parse_args()

    if args.watch:
        watch_loop(max(60, args.interval), dry_run=args.dry_run)
        return 0
    run_cycle(load_config(), dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
