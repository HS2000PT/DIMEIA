"""Runner de alertas agendado — varre uma watchlist e envia alertas explicáveis para o Telegram.

Lê `config/alerts.yaml` (definições não-secretas) e reutiliza as funções já validadas do
InvestiGator. Corre na **stack leve** (sem torch). Seguro por defeito: se o Telegram não estiver configurado,
imprime os alertas e sai com código 0 — assim um job agendado fica verde antes de definires os
segredos.

Uso:
    python scripts/run_alerts.py            # varre + envia (se o Telegram estiver configurado)
    python scripts/run_alerts.py --dry-run  # varre + imprime apenas, nunca envia

Pensado para ser chamado por `.github/workflows/alerts.yml` (cron) — ver docs/design/going_live.md.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

# Permitir correr como `python scripts/run_alerts.py` a partir da raiz do repo.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_CONFIG = Path(__file__).resolve().parents[1] / "config" / "alerts.yaml"


def _stdout_utf8() -> None:
    """No Windows a consola é cp1252 e rebenta com os emojis dos alertas; forçar UTF-8."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def load_config(path: str | Path = _CONFIG) -> dict:
    """Carrega o ficheiro de definições YAML."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_market_alerts(results: list[tuple[str, object]]) -> list[str]:
    """Puro: dado [(ticker, AnomalyResult)], devolve os textos de alerta só das anomalias."""
    from src.explanation_engine.explainer import explain_anomaly

    return [explain_anomaly(ticker, res) for ticker, res in results if res.is_anomaly]


def scan_market(cfg: dict) -> list[str]:
    """Busca preços de cada ticker, deteta anomalias e devolve os textos de alerta."""
    from src.anomaly_detector.detector import detect_latest
    from src.market_data.prices import get_price_history, log_returns

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


def scan_news(cfg: dict) -> list[str]:
    """Opcional: notícias recentes por ticker -> precedentes (best-effort, pode repetir)."""
    n = cfg.get("news", {})
    if not n.get("enabled", False):
        return []
    from src import config
    from src.main import run_news_trigger
    from src.news_fetcher.fetcher import fetch_finnhub_company_news

    if not config.FINNHUB_API_KEY:
        print("[noticias] FINNHUB_API_KEY em falta — a saltar o scan de noticias.")
        return []
    horizon = int(n.get("horizon", 5))
    top_k = int(n.get("top_k", 3))
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
            alerts.append(text)
        except Exception as exc:  # noqa: BLE001
            print(f"[saltar noticias {ticker}] {type(exc).__name__}: {exc}")
    return alerts


def main() -> int:
    _stdout_utf8()
    parser = argparse.ArgumentParser(description="InvestiGator — runner de alertas agendado")
    parser.add_argument("--dry-run", action="store_true", help="varre e imprime; nunca envia")
    args = parser.parse_args()

    cfg = load_config()
    alerts = scan_market(cfg) + scan_news(cfg)

    if not alerts:
        print("Sem alertas hoje (nenhuma anomalia acima do limiar).")
        return 0

    from src import config

    can_send = bool(config.TELEGRAM_BOT_TOKEN and config.TELEGRAM_CHAT_ID) and not args.dry_run
    for text in alerts:
        print("-" * 60)
        print(text)
        if can_send:
            from src.telegram_bot.sender import send_message

            send_message(text)

    if can_send:
        print(f"\n[{len(alerts)} alerta(s) enviado(s) para o Telegram]")
    else:
        why = "modo --dry-run" if args.dry_run else "Telegram nao configurado (nada enviado)"
        print(f"\n[{len(alerts)} alerta(s); {why}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
