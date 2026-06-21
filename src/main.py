"""Ponto de entrada — thin slice end-to-end (Gatilho 1: movimento abrupto de mercado).

Fluxo: market_data (yfinance) -> anomaly_detector (z-score) -> explanation_engine -> telegram_bot.
Os componentes (correlação/precedentes, notícias) entram em fases posteriores.
"""

from __future__ import annotations


def run_thin_slice(ticker: str = "AAPL", window: int = 20, threshold: float = 3.0,
                   send: bool = True) -> tuple[object, str]:
    """Corre a fatia fina: deteta anomalia no ticker e envia (opcional) alerta Telegram.

    Devolve o resultado da deteção e o texto da explicação/alerta.
    """
    from src.anomaly_detector.detector import detect_latest
    from src.explanation_engine.explainer import explain_anomaly, explain_normal
    from src.market_data.prices import get_price_history, log_returns
    from src.telegram_bot.sender import send_message

    df = get_price_history(ticker)
    returns = log_returns(df["Close"])
    result = detect_latest(returns, window=window, threshold=threshold)
    text = explain_anomaly(ticker, result) if result.is_anomaly else explain_normal(ticker, result)
    if send:
        send_message(text)
    return result, text


def main() -> None:
    """Arranque simples da thin slice para um ticker por defeito."""
    result, text = run_thin_slice()
    print(text)
    print(f"[is_anomaly={result.is_anomaly} z={result.z_score:+.2f}]")


if __name__ == "__main__":
    main()
