"""Captura um screenshot REAL do dashboard Streamlit (Fig. 4.5 da tese).

Arranca a app localmente (headless), espera o gráfico renderizar e grava um PNG com Playwright.
Reprodutível: não fabrica nada — é a app implantada a correr, com a marca atual ("The Tail",
`app/assets/logo.svg`) e o slogan "Markets move. We investigate.".

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

    # Aponta para a app PROMOVIDA. Ficou a apontar para a v1 depois da promoção, o que
    # produziria uma figura da tese a mostrar um ecrã que já não está no ar — a Fig. 4.5
    # tem de ser uma captura do que o leitor encontra se abrir o URL.
    # 2026-08-09: a promoção da v4 repetiu exactamente o defeito que este comentário descreve.
    # O alvo passa a ser `dashboard_v4.py`, que é o que o `Procfile` serve.
    app = REPO / "app" / "dashboard_v4.py"
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
            # O ecrã de abertura da v4 é a grelha que LÊ o instantâneo. Esperar por um cartão
            # (`.name`) e não por um rótulo de ecrã: os rótulos mudam a cada redesenho e
            # deixam este script a esperar por algo que já não existe — foi o que aconteceu
            # na promoção anterior. O cartão é a última peça a chegar.
            page.wait_for_selector(".grid .name", timeout=45000)
            for marca in ("text=trading days", "text=Nothing stood out", "text=No market data"):
                try:
                    page.wait_for_selector(marca, timeout=25000)
                    break
                except Exception:  # noqa: BLE001
                    continue
            page.wait_for_timeout(6000)  # logótipos, sparklines e render final
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
