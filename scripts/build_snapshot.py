"""Pré-computa a grelha para um instantâneo estático — o protótipo que decide a stack.

O PORQUÊ, EM UMA FRASE
----------------------
A grelha de entrada chama `_snapshot(t)` para cada um dos doze tickers, e cada chamada puxa um
ano de preços pela rede. São **doze idas à rede antes da primeira pintura**, e é aí que vivem os
~5,5 s de carga a frio — não no CSS, e não no Streamlit.

O que este script faz é o padrão do *data loader* do Observable Framework, e é o que os quatro
agentes do estudo de mercado recomendaram independentemente: **o worker calcula, a página lê**.

O QUE ISTO É E O QUE NÃO É
--------------------------
**É** um protótipo para produzir um número: quanto custa a grelha a ler um ficheiro contra
calcular ao vivo. O briefing exige exactamente isso antes de se propor trocar de stack —
*"mostra um protótipo pequeno a provar o ganho antes de reescrever tudo"*.

**Não é** a v4 nem toca na v3. Escreve um ficheiro; ninguém o lê ainda.

A REGRA QUE O MANTÉM HONESTO
----------------------------
O instantâneo é construído com **as mesmas funções que a app usa** (`detect_latest`,
`empirical_exceedance`, `detect_volume_latest`). Se fossem reimplementadas aqui, o ficheiro
poderia divergir do que a app calcularia e ninguém daria por isso — que é a classe de defeito
que este projecto já pagou em três sítios diferentes.

USO
---
    python scripts/build_snapshot.py
    python scripts/build_snapshot.py --medir    # compara ler-ficheiro vs calcular-ao-vivo
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from datetime import UTC, datetime

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

DESTINO = RAIZ / "data" / "samples" / "dashboard_snapshot.json"
JANELA = 20
LIMIAR = 1.5


def _watchlist() -> list[str]:
    import yaml

    cfg = yaml.safe_load((RAIZ / "config" / "alerts.yaml").read_text(encoding="utf-8")) or {}
    return list(cfg.get("market", {}).get("tickers") or [])


def linha_de(ticker: str) -> dict | None:
    """Tudo o que um cartão da grelha precisa, calculado uma vez."""
    from investigator.anomaly_detector.detector import detect_latest
    from investigator.anomaly_detector.frequency import empirical_exceedance
    from investigator.anomaly_detector.volume import detect_volume_latest
    from investigator.market_data.prices import get_price_history, log_returns

    try:
        frame = get_price_history(ticker, period="1y")
        fecho = frame["Close"]
        retornos = log_returns(fecho)
        res = detect_latest(retornos, window=JANELA, threshold=LIMIAR)
        out: dict = {
            "ticker": ticker,
            "z": float(res.z_score),
            "move": float(res.last_return),
            "flagged": bool(res.is_anomaly),
            "vol_ratio": None,
            "rarity": None,
        }
        exc = empirical_exceedance(retornos)
        if exc is not None:
            out["rarity"] = {"count": int(exc.count), "n": int(exc.n)}
        if "Volume" in frame:
            v = detect_volume_latest(frame["Volume"], window=JANELA, threshold=2.0)
            if v.is_unusual:
                out["vol_ratio"] = float(v.ratio)
        return out
    except Exception as erro:  # noqa: BLE001
        print(f"  {ticker:6s} falhou: {type(erro).__name__}: {erro}")
        return None


def construir() -> dict:
    tickers = _watchlist()
    t0 = time.perf_counter()
    linhas = [x for x in (linha_de(t) for t in tickers) if x]
    custo = time.perf_counter() - t0
    return {
        # Carimbo em UTC: o critério C3 exige que a idade seja VISÍVEL no ecrã e que não passe
        # de 90 s em operação normal. Sem isto, um instantâneo velho é indistinguível de um
        # fresco, e um número velho apresentado como actual é pior do que nenhum número.
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "build_seconds": round(custo, 3),
        "window": JANELA,
        "threshold": LIMIAR,
        "rows": linhas,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--medir", action="store_true", help="comparar ler vs calcular")
    args = p.parse_args()

    print("a construir o instantaneo (calculo ao vivo, como a grelha faz hoje)...")
    snap = construir()
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(json.dumps(snap, indent=1), encoding="utf-8")
    tam = DESTINO.stat().st_size
    print(f"\n{len(snap['rows'])}/{len(_watchlist())} tickers em {snap['build_seconds']:.2f} s")
    print(f"-> {DESTINO}  ({tam/1024:.1f} KB)")

    if args.medir:
        print("\n--- a medicao que decide ---")
        t0 = time.perf_counter()
        lido = json.loads(DESTINO.read_text(encoding="utf-8"))
        ler = time.perf_counter() - t0

        t0 = time.perf_counter()
        _ = [x for x in (linha_de(t) for t in _watchlist()) if x]
        vivo = time.perf_counter() - t0

        print(f"  calcular ao vivo (o que a grelha faz hoje) : {vivo:8.3f} s")
        print(f"  ler o instantaneo do disco                 : {ler:8.3f} s")
        if ler > 0:
            print(f"  razao                                      : {vivo/ler:8.0f}x")
        print(f"\n  linhas no ficheiro: {len(lido['rows'])}")
        print("\n  Nota: 'ao vivo' beneficia da cache HTTP desta corrida, portanto o ganho real")
        print("  numa maquina fria e MAIOR do que este. Mesmo assim ja decide.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
