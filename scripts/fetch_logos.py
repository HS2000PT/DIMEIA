"""Descarrega uma vez os logótipos da watchlist para `app/assets/logos/`.

Corre-se à mão quando a watchlist muda, não em cada ciclo. Os ficheiros são versionados
de propósito: a app implantada desenha-os sem chave, sem rede e sem limite de ritmo.

    python scripts/fetch_logos.py            # só os que faltam
    python scripts/fetch_logos.py --force    # volta a descarregar todos

Sem `POLYGON_API_KEY` sai com aviso e código 0: não ter logótipos é uma interface mais
pobre, não uma avaria.
"""

from __future__ import annotations

import argparse
import sys
import time

import yaml

from investigator.branding.logos import LOGO_DIR, fetch_logo
from investigator.config import POLYGON_API_KEY


def _watchlist() -> list[str]:
    with open("config/alerts.yaml", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}
    return list(cfg.get("market", {}).get("tickers") or cfg.get("tickers") or [])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="volta a descarregar existentes")
    ap.add_argument("--tickers", nargs="*", help="em vez da watchlist")
    ap.add_argument("--sleep", type=float, default=26.0,
                    help="segundos entre tickers (limite de 5 pedidos/min)")
    args = ap.parse_args()

    if not POLYGON_API_KEY:
        print("[logos] sem POLYGON_API_KEY — a interface usa as iniciais. Nada a fazer.")
        return 0

    tickers = args.tickers or _watchlist()
    if not tickers:
        print("[logos] watchlist vazia.")
        return 0

    LOGO_DIR.mkdir(parents=True, exist_ok=True)
    obtidos = saltados = falhados = 0

    for ticker in tickers:
        ticker = ticker.upper()
        existentes = [p for p in LOGO_DIR.glob(f"{ticker}.*") if p.suffix != ".bin"]
        if existentes and not args.force:
            print(f"[logos] {ticker:<6} já existe ({existentes[0].name})")
            saltados += 1
            continue

        # 5 pedidos/min no plano gratuito, 2 por ticker: ~25 s entre tickers.
        if obtidos or falhados:
            time.sleep(args.sleep)
        asset = fetch_logo(ticker, POLYGON_API_KEY)
        if asset is None or asset.suffix == ".bin":
            print(f"[logos] {ticker:<6} sem logótipo utilizável — fica com as iniciais")
            falhados += 1
            continue

        for velho in LOGO_DIR.glob(f"{ticker}.*"):
            velho.unlink()
        asset.path.write_bytes(asset.data)
        print(f"[logos] {ticker:<6} -> {asset.path.name} ({len(asset.data)} bytes)")
        obtidos += 1

    print(f"\n[logos] {obtidos} obtidos · {saltados} já existiam · {falhados} sem logótipo")
    print(f"[logos] destino: {LOGO_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
