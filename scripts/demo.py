"""Demo do InvestiGator — corre os dois gatilhos SEM chaves nem configuração.

Correr:  python scripts/demo.py   (ou ./.venv/Scripts/python.exe scripts/demo.py)

- Gatilho de notícia: usa a base de conhecimento de amostra (offline, determinístico).
- Gatilho de mercado: tenta preços ao vivo (se houver internet); NÃO envia nada.

É o ponto de partida para "ver a app a funcionar" sem configurar Telegram/APIs.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permitir "python scripts/demo.py" a partir da raiz do repo (põe a raiz no sys.path).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.console import force_utf8_stdout  # noqa: E402  (depois do sys.path)


def _rule(title: str) -> None:
    print("=" * 72)
    print(title)
    print("=" * 72)


def demo_noticia() -> None:
    """Gatilho 2 (notícia): recupera precedentes da KB de amostra e explica o impacto."""
    from src.main import run_news_trigger

    _rule("GATILHO DE NOTÍCIA  (offline, base de conhecimento de amostra)")
    _, text = run_news_trigger(
        ticker="NVDA",
        headline="Nvidia demand surges on AI chip orders",
        top_k=3,
        horizon=5,
        send=False,
    )
    print(text)


def demo_mercado() -> None:
    """Gatilho 1 (mercado): z-score sobre preços ao vivo (não envia)."""
    print()
    _rule("GATILHO DE MERCADO  (preços ao vivo; não envia)")
    try:
        from src.anomaly_detector.detector import detect_latest
        from src.explanation_engine.explainer import explain_anomaly, explain_normal
        from src.market_data.prices import get_price_history, log_returns

        returns = log_returns(get_price_history("AAPL")["Close"])
        res = detect_latest(returns, window=20, threshold=3.0)
        print(explain_anomaly("AAPL", res) if res.is_anomaly else explain_normal("AAPL", res))
        print(f"[is_anomaly={res.is_anomaly}  z={res.z_score:+.2f}]")
    except Exception as exc:  # noqa: BLE001  (rede pode falhar; a demo continua útil)
        print(f"(Sem internet ou erro: {type(exc).__name__}.")
        print(" O gatilho de notícia acima corre sempre, offline.)")


def main() -> None:
    force_utf8_stdout()
    demo_noticia()
    demo_mercado()
    print()
    print("Feito. Nada foi enviado.")
    print("Para enviar ao Telegram, ver docs/design/how_to_run.md (precisa de .env).")


if __name__ == "__main__":
    main()
