"""Sonda de memória TEMPORÁRIA — diagnóstico do worker no Heroku. Apagar depois de usar.

Existe porque `heroku run python -c "..."` estraga as aspas no Windows, e porque adivinhar a
causa de um R15 a partir de fora deu duas hipóteses erradas seguidas (threads do onnxruntime,
tamanho da branch de dados). Isto mede em vez de supor.
"""

from __future__ import annotations

import os
import resource
import sys


def rss_mb() -> float:
    """Pico de RSS em MB (ru_maxrss vem em KB no Linux)."""
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def step(label: str) -> None:
    print(f"  {label:<34} {rss_mb():8.1f} MB", flush=True)


def main() -> int:
    print(f"cpu_count       = {os.cpu_count()}")
    if hasattr(os, "sched_getaffinity"):
        print(f"sched_affinity  = {len(os.sched_getaffinity(0))}")
    print(f"WEB_CONCURRENCY = {os.environ.get('WEB_CONCURRENCY', '(unset)')}")
    print()
    step("baseline")

    import numpy  # noqa: F401
    import pandas  # noqa: F401

    step("+pandas/numpy")

    import yfinance  # noqa: F401

    step("+yfinance")

    import sklearn  # noqa: F401

    step("+sklearn")

    import onnxruntime  # noqa: F401

    step("+onnxruntime")

    from investigator.main import product_retrieval

    step("+import product_retrieval")

    kb, emb = product_retrieval(auto_download=True)
    step(f"+retrieval ({type(emb).__name__})")

    emb.encode(["Nvidia beats earnings on AI demand"])
    step("+1 encode")

    # O passo que o worker faz a seguir e que nunca foi medido: carregar os precedentes.
    try:
        from investigator.historical_kb.knowledge_base import HistoricalKB

        base = HistoricalKB.load(kb)
        step(f"+HistoricalKB.load ({len(base.records)} casos)")
    except Exception as exc:  # noqa: BLE001
        print(f"  (KB.load falhou: {exc})")

    # E o histórico partilhado / KB viva, que crescem com o tempo.
    for name in ("live_kb.jsonl", "live_pending.jsonl"):
        try:
            from investigator.live_kb import load_live_records

            recs = load_live_records(name)
            step(f"+{name} ({len(recs)})")
        except Exception:
            pass

    print(f"\nPICO FINAL: {rss_mb():.1f} MB   (limite do dyno Basic: 512 MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
