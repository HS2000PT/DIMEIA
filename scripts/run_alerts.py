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


def build_market_alerts(results: list[tuple[str, object]]) -> list[str]:
    """Puro: dado [(ticker, AnomalyResult)], devolve os textos de alerta só das anomalias."""
    from investigator.explanation_engine.explainer import explain_anomaly

    return [explain_anomaly(ticker, res) for ticker, res in results if res.is_anomaly]


def scan_market(cfg: dict) -> list[str]:
    """Busca preços de cada ticker, deteta anomalias e devolve os textos de alerta."""
    from investigator.anomaly_detector.detector import detect_latest
    from investigator.market_data.prices import get_price_history, log_returns

    m = cfg.get("market", {})
    if not m.get("enabled", False):
        return []
    window = int(m.get("window", 20))
    threshold = float(m.get("threshold", 3.0))
    results: list[tuple[str, object]] = []
    for ticker in m.get("tickers", []):
        try:
            returns = log_returns(get_price_history(ticker)["Close"])
            results.append((ticker, detect_latest(returns, window=window, threshold=threshold)))
        except Exception as exc:  # noqa: BLE001  (um ticker/rede a falhar não pode parar a varredura)
            print(f"[saltar {ticker}] {type(exc).__name__}: {exc}")
    return build_market_alerts(results)


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


def scan_news(cfg: dict) -> list[str]:
    """Opcional: notícias recentes por ticker -> precedentes (best-effort, pode repetir)."""
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
    alerts: list[str] = []
    for ticker in n.get("tickers", []):
        try:
            items = fetch_finnhub_company_news(ticker, start, end)
            if not items:
                continue
            latest = max(items, key=lambda it: it.date)  # o mais recente
            _, text = run_news_trigger(
                ticker=ticker, headline=latest.headline, top_k=top_k, horizon=horizon, send=False
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
            alerts.append(text)
        except Exception as exc:  # noqa: BLE001
            print(f"[saltar noticias {ticker}] {type(exc).__name__}: {exc}")
    return alerts


def main() -> int:
    force_utf8_stdout()
    parser = argparse.ArgumentParser(description="InvestiGator — runner de alertas agendado")
    parser.add_argument("--dry-run", action="store_true", help="varre e imprime; nunca envia")
    args = parser.parse_args()

    cfg = load_config()
    alerts = scan_market(cfg) + scan_news(cfg)

    if not alerts:
        print("Sem alertas hoje (nenhuma anomalia acima do limiar).")
        return 0

    from investigator import config

    can_send = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID) and not args.dry_run
    for text in alerts:
        print("-" * 60)
        print(text)
        if can_send:
            from investigator.telegram_bot.sender import send_message

            send_message(text)

    if can_send:
        print(f"\n[{len(alerts)} alerta(s) enviado(s) para o Telegram]")
    else:
        why = "modo --dry-run" if args.dry_run else "Telegram nao configurado (nada enviado)"
        print(f"\n[{len(alerts)} alerta(s); {why}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
