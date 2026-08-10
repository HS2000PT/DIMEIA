"""Captura as figuras da v5 a partir da app IMPLANTADA.

Aponta para produção de propósito. A alternativa — capturar um servidor local — produz uma
figura que documenta o que está na máquina de quem a tirou, e este projecto já pagou esse
defeito uma vez: a Fig. 4.5 descreveu durante uma sessão inteira um ecrã que já não estava
no ar.

USO
---
    python scripts/screenshot_v5.py                 # produção
    python scripts/screenshot_v5.py --url http://127.0.0.1:8099
"""

from __future__ import annotations

import argparse
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
FIGURAS = RAIZ / "thesis" / "figures"
PROD = "https://investigator-ddc9d8618935.herokuapp.com"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default=PROD)
    args = p.parse_args()

    from playwright.sync_api import sync_playwright

    FIGURAS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1500, "height": 940}, device_scale_factor=2)

        pg.goto(args.url, wait_until="networkidle", timeout=60000)
        pg.wait_for_selector(".card", timeout=30000)
        pg.wait_for_timeout(1200)  # deixa os logótipos entrarem
        pg.screenshot(path=str(FIGURAS / "app_v5_overview.png"))
        print("app_v5_overview.png")

        pg.goto(f"{args.url}/?t=XOM", wait_until="networkidle", timeout=60000)
        pg.wait_for_selector("#chart canvas", timeout=30000)
        pg.wait_for_timeout(1800)
        pg.screenshot(path=str(FIGURAS / "app_v5_asset.png"))
        print("app_v5_asset.png")

        # O painel de inteligência com uma âncora ABERTA: é a figura que prova a travessia
        # frase -> facto, e sem a âncora aberta seria só texto bonito.
        pg.click("#toggle-rail")
        pg.wait_for_timeout(300)
        for sel in ("#gen-report-2", "#gen-report"):
            try:
                pg.click(sel, timeout=3000)
                break
            except Exception:  # noqa: BLE001
                continue
        pg.wait_for_selector(".report-sec", timeout=45000)
        pg.wait_for_timeout(800)
        try:
            pg.click(".anchor", timeout=5000)
            pg.wait_for_selector(".ev.fact", timeout=5000)
            pg.wait_for_timeout(400)
        except Exception:  # noqa: BLE001
            print("  (sem âncora aberta — a guarda pode ter substituído a secção)")
        pg.screenshot(path=str(FIGURAS / "app_v5_intelligence.png"))
        print("app_v5_intelligence.png")
        b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
