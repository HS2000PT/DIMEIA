"""Ponto de entrada — orquestração dos dois gatilhos.

- Gatilho 1 (movimento abrupto): market_data -> anomaly_detector -> explanation_engine -> telegram.
- Gatilho 2 (notícia): notícia -> embedding -> KB.find_precedents -> explicação -> telegram.
"""

from __future__ import annotations

from pathlib import Path

_DEFAULT_KB = Path(__file__).resolve().parent.parent / "data" / "samples" / "kb_sample.jsonl"
_LIGHT_KB = Path(__file__).resolve().parent.parent / "data" / "samples" / "kb_fnspid_light.jsonl"


def preferred_light_kb() -> Path:
    """KB para o PRODUTO (app/runner, stack leve): a curada multi-ano FNSPID se existir,
    senão a amostra de sempre. O DEFAULT de `run_news_trigger` não muda — a demo e o
    exemplo do Cap. 3 (+6,46%) continuam a usar `kb_sample.jsonl`, reprodutíveis."""
    return _LIGHT_KB if _LIGHT_KB.exists() else _DEFAULT_KB


def kb_query_embedder(kb_path: str | Path):
    """HashingEmbedder com a dimensão DA PRÓPRIA KB (lida do 1.º registo do ficheiro).

    Auto-coerência sem configuração: a regra "o embedder da consulta tem de coincidir com o
    da construção" (guarda R1) fica garantida por construção, seja a KB 64-d ou 256-d.
    """
    import json

    from investigator.historical_kb.embedder import HashingEmbedder

    with open(kb_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                emb = json.loads(line).get("embedding")
                if emb:
                    return HashingEmbedder(dim=len(emb))
                break
    return HashingEmbedder(dim=64)


def run_thin_slice(ticker: str = "AAPL", window: int = 20, threshold: float = 3.0,
                   send: bool = True) -> tuple[object, str]:
    """Corre a fatia fina: deteta anomalia no ticker e envia (opcional) alerta Telegram.

    Devolve o resultado da deteção e o texto da explicação/alerta.
    """
    from investigator.anomaly_detector.detector import detect_latest
    from investigator.explanation_engine.explainer import explain_anomaly, explain_normal
    from investigator.market_data.prices import get_price_history, log_returns
    from investigator.telegram_bot.sender import send_message

    df = get_price_history(ticker)
    returns = log_returns(df["Close"])
    result = detect_latest(returns, window=window, threshold=threshold)
    text = explain_anomaly(ticker, result) if result.is_anomaly else explain_normal(ticker, result)
    if send:
        send_message(text)
    return result, text


def run_news_trigger(
    ticker: str,
    headline: str,
    date: str = "",
    kb_path: str | Path = _DEFAULT_KB,
    embedder: object | None = None,
    top_k: int = 5,
    horizon: int = 3,
    send: bool = False,
) -> tuple[list, str]:
    """Corre o Gatilho 2: recupera precedentes da KB para uma notícia e explica o impacto.

    Por defeito usa o `HashingEmbedder` (dim 64) — que tem de coincidir com o embedder usado
    para construir a KB (a amostra `kb_sample.jsonl` foi construída assim). Para uma KB SBERT,
    passar `embedder=SbertEmbedder()` e o `kb_path` correspondente.

    Devolve a lista de precedentes (registo, score) e o texto do alerta.
    """
    from investigator.explanation_engine.explainer import explain_news_impact
    from investigator.historical_kb.embedder import HashingEmbedder
    from investigator.historical_kb.knowledge_base import HistoricalKB

    if embedder is None:
        embedder = HashingEmbedder(dim=64)
    kb = HistoricalKB.load(kb_path)
    precedents = kb.find_precedents(headline, embedder, top_k=top_k)
    text = explain_news_impact(ticker, headline, precedents, horizon=horizon, date=date)
    if send:
        from investigator.telegram_bot.sender import send_message

        send_message(text)
    return precedents, text


def main() -> None:
    """Arranque simples da thin slice para um ticker por defeito."""
    result, text = run_thin_slice()
    print(text)
    print(f"[is_anomaly={result.is_anomaly} z={result.z_score:+.2f}]")


if __name__ == "__main__":
    main()
