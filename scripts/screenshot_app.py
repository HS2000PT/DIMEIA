"""Captura um screenshot REAL do dashboard Streamlit (Fig. 4.5 da tese).

Arranca a app localmente (headless), espera o gráfico renderizar e grava um PNG com Playwright.
Reprodutível: não fabrica nada — é a app implantada a correr. Usa a marca atual (logo "The Stare"
+ slogan "Every move investigated, never predicted.").

Uso:
    python scripts/screenshot_app.py                          # → thesis/figures/app_dashboard.png
    python scripts/screenshot_app.py --out /tmp/app.png --port 8533
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _wait_health(port: int, timeout: float = 60.0) -> bool:
    url = f"http://localhost:{port}/_stcore/health"
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2) as r:  # noqa: S310 (localhost)
                if r.status == 200 and r.read().strip() == b"ok":
                    return True
        except Exception:  # noqa: BLE001
            time.sleep(1.0)
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Screenshot real do dashboard")
    ap.add_argument("--out", default=str(REPO / "thesis" / "figures" / "app_dashboard.png"))
    ap.add_argument("--port", type=int, default=8533)
    ap.add_argument("--width", type=int, default=1500)
    ap.add_argument("--height", type=int, default=850)
    args = ap.parse_args()

    app = REPO / "app" / "streamlit_app.py"
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(app),
         "--server.headless", "true", "--server.port", str(args.port),
         "--browser.gatherUsageStats", "false"],
        cwd=str(REPO), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        if not _wait_health(args.port):
            print("A app não respondeu no health endpoint a tempo.")
            return 1
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": args.width, "height": args.height},
                                    device_scale_factor=2)
            page.goto(f"http://localhost:{args.port}", wait_until="networkidle", timeout=60000)
            # Esperar o gráfico grande (a peça central: preço + replay de eventos detetados).
            try:
                page.wait_for_selector(".js-plotly-plot", timeout=30000)
            except Exception:  # noqa: BLE001
                page.wait_for_selector("text=Alert history", timeout=10000)  # fallback sem plotly
            page.wait_for_timeout(4000)  # replay dos eventos + animação do gráfico
            Path(args.out).parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=args.out)
            browser.close()
        print(f"Screenshot: {args.out}")
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:  # noqa: BLE001
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
