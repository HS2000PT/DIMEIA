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
from datetime import date, timedelta
from pathlib import Path

import yaml

# Permitir correr como `python scripts/run_alerts.py` a partir da raiz do repo.
from investigator.console import force_utf8_stdout

_CONFIG = Path(__file__).resolve().parents[1] / "config" / "alerts.yaml"
_PRED_LOG = Path(__file__).resolve().parents[1] / "data" / "predictions_log.jsonl"
_STATE = Path(__file__).resolve().parents[1] / "data" / "alerts_state.json"


# ── Estado entre corridas (intradiário, anti-duplicado) ───────────────────────
# Com o cron a correr de 30 em 30 min durante o mercado, o runner tem de se lembrar do que
# JÁ alertou hoje (o job do Actions é efémero; o workflow persiste este ficheiro via cache).
def load_state(path: str | Path = _STATE, today: date | None = None) -> dict:
    """Lê o estado; se for de outro dia, zera as listas do dia mas PRESERVA o offset do bot."""
    import json

    today = today or date.today()
    state = {"date": today.isoformat(), "alerted_market": [], "alerted_news": [],
             "bot_offset": None}
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        state["bot_offset"] = raw.get("bot_offset")
        if raw.get("date") == today.isoformat():
            state["alerted_market"] = list(raw.get("alerted_market", []))
            state["alerted_news"] = list(raw.get("alerted_news", []))
    except (OSError, ValueError):
        pass  # sem estado (1.ª corrida do dia/da cache) → começa limpo
    return state


def save_state(state: dict, path: str | Path = _STATE) -> None:
    import json

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def news_key(ticker: str, text: str) -> str:
    """Chave estável de um alerta de notícia (para não repetir a mesma manchete no mesmo dia)."""
    import hashlib

    return hashlib.sha1(f"{ticker}|{text}".encode()).hexdigest()[:12]


def filter_new_alerts(market: list[tuple[str, str]], news: list[tuple[str, str]],
                      state: dict) -> list[tuple[str, str]]:
    """Puro: mantém só o que ainda NÃO foi alertado hoje e marca-o no estado."""
    keep: list[tuple[str, str]] = []
    for ticker, text in market:
        if ticker not in state["alerted_market"]:
            state["alerted_market"].append(ticker)
            keep.append((ticker, text))
        else:
            print(f"[{ticker}] já alertado hoje — sem repetição.")
    for ticker, text in news:
        k = news_key(ticker, text)
        if k not in state["alerted_news"]:
            state["alerted_news"].append(k)
            keep.append((ticker, text))
        else:
            print(f"[noticias {ticker}] já alertada hoje — sem repetição.")
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


def scan_market(cfg: dict) -> list[tuple[str, str]]:
    """Busca preços de cada ticker, deteta anomalias e devolve pares (ticker, texto de alerta)."""
    from investigator.anomaly_detector.detector import detect_latest
    from investigator.market_data.prices import get_price_history, log_returns

    m = cfg.get("market", {})
    if not m.get("enabled", False):
        return []
    window = int(m.get("window", 20))
    threshold = float(m.get("threshold", 3.0))
    require_fresh = bool(m.get("require_fresh_bar", True))
    results: list[tuple[str, object]] = []
    for ticker in m.get("tickers", []):
        try:
            hist = get_price_history(ticker)
            last_bar = hist.index[-1].date()
            if require_fresh and not bar_is_fresh(last_bar, date.today()):
                print(f"[{ticker}] última barra é de {last_bar} (sem sessão nova hoje) "
                      "— sem avaliação (anti-duplicado).")
                continue
            returns = log_returns(hist["Close"])
            results.append((ticker, detect_latest(returns, window=window, threshold=threshold)))
        except Exception as exc:  # noqa: BLE001  (um ticker/rede a falhar não pode parar a varredura)
            print(f"[saltar {ticker}] {type(exc).__name__}: {exc}")
    # Mesmo filtro e mesma ordem de build_market_alerts (puro, testado) → zip alinha por construção.
    tickers_anomalos = [t for t, r in results if r.is_anomaly]
    return list(zip(tickers_anomalos, build_market_alerts(results), strict=True))


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


def scan_news(cfg: dict) -> list[tuple[str, str]]:
    """Opcional: notícias recentes por ticker -> pares (ticker, alerta) (best-effort)."""
    n = cfg.get("news", {})
    if not n.get("enabled", False):
        return []
    from investigator import config
    from investigator.main import run_news_trigger
    from investigator.news_fetcher.fetcher import fetch_finnhub_company_news

    if not config.FINNHUB_API_KEY:
        print("[noticias] FINNHUB_API_KEY em falta — a saltar o scan de noticias.")
        return []
    horizon = int(n.get("horizon", 5))
    top_k = int(n.get("top_k", 3))

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

    end = date.today().isoformat()
    start = (date.today() - timedelta(days=7)).isoformat()
    alerts: list[tuple[str, str]] = []
    for ticker in n.get("tickers", []):
        try:
            items = fetch_finnhub_company_news(ticker, start, end)
            if not items:
                continue
            latest = max(items, key=lambda it: it.date)  # o mais recente
            max_age = int(n.get("max_age_days", 2))
            if not news_is_fresh(latest.date, date.today(), max_age):
                print(f"[noticias {ticker}] mais recente é de {latest.date} (>{max_age} dias) "
                      "— sem alerta (anti-repetição).")
                continue
            from investigator.main import kb_query_embedder, preferred_light_kb

            kb_path = preferred_light_kb()
            _, text = run_news_trigger(
                ticker=ticker, headline=latest.headline, kb_path=kb_path,
                embedder=kb_query_embedder(kb_path), top_k=top_k, horizon=horizon, send=False,
            )
            if bundle is not None:
                from investigator.market_data.prices import get_price_history
                from investigator.triage.infer import score_latest

                scored = score_latest(
                    bundle, get_price_history(ticker)["Close"], latest.headline, ticker
                )
                gated = apply_materiality(text, scored, gate)
                _log_decision_safe(latest.date, ticker, latest.headline,
                                   scored, gate, kept=gated is not None)
                if gated is None:
                    print(f"[triagem {ticker}] P(anormal)={scored[0]:.0%} < {gate:.0%} "
                          "— alerta de noticia suprimido.")
                    continue
                text = gated
            else:
                _log_decision_safe(latest.date, ticker, latest.headline,
                                   None, None, kept=True)
            alerts.append((ticker, text))
        except Exception as exc:  # noqa: BLE001
            print(f"[saltar noticias {ticker}] {type(exc).__name__}: {exc}")
    return alerts


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


def main() -> int:
    force_utf8_stdout()
    parser = argparse.ArgumentParser(description="InvestiGator — runner de alertas agendado")
    parser.add_argument("--dry-run", action="store_true", help="varre e imprime; nunca envia")
    args = parser.parse_args()

    cfg = load_config()
    bot_cfg = cfg.get("bot", {}) or {}
    state = load_state()
    process_bot_commands(state, bot_cfg, dry_run=args.dry_run)

    alerts = filter_new_alerts(scan_market(cfg), scan_news(cfg), state)
    if not args.dry_run:
        save_state(state)  # persiste marcas do dia + offset do bot (cache no Actions)
    else:
        print("[estado] dry-run — estado não gravado (não interfere com a corrida real).")

    if not alerts:
        print("Sem alertas novos nesta corrida (nenhuma anomalia nova acima do limiar).")
        return 0

    from investigator import config

    can_send = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID) and not args.dry_run
    for _ticker, text in alerts:
        print("-" * 60)
        print(text)
        if can_send:
            from investigator.telegram_bot.sender import send_message

            send_message(text)

    _fanout_safe(alerts, bot_cfg, dry_run=args.dry_run)

    if can_send:
        print(f"\n[{len(alerts)} alerta(s) enviado(s) para o Telegram]")
    else:
        why = "modo --dry-run" if args.dry_run else "Telegram nao configurado (nada enviado)"
        print(f"\n[{len(alerts)} alerta(s); {why}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
