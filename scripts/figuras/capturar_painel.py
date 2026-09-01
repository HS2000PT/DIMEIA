#!/usr/bin/env python3
"""Gera as capturas do painel para o Capítulo 4, a partir de um instantâneo congelado.

## Porque existe

As figuras do painel eram capturadas à mão, o que trazia três problemas: dependiam de apanhar o
ecrã num bom momento, não eram regeneráveis quando a página mudasse, e o texto da dissertação
ficava a descrever números de uma captura que já não existia — foi exatamente o que aconteceu
com a versão anterior desta figura, cujo parágrafo descrevia uma empresa que a imagem já não
mostrava.

Aqui a captura é reprodutível: os dados vêm de ficheiros JSON descarregados uma vez da API, um
servidor local serve a página real sobre eles, e o Playwright fotografa. O script imprime no fim
os valores que a figura mostra, para serem conferidos contra o texto — a regra é que o número da
dissertação vem daqui, e nunca da leitura da imagem.

## Duas armadilhas que custaram tempo e ficam registadas

1. **`element.screenshot()` devolve as telas do gráfico em branco** no Chromium sem interface. O
   recorte tem de ser feito com `page.screenshot(full_page=True, clip=...)`.
2. **O `lightweight-charts` fica no tamanho por defeito (300x150) neste arnês** e não pinta. O
   gráfico de preço tem figura própria no capítulo, por isso a vista da empresa é recortada
   antes dele — o que esta figura precisa de mostrar é o veredicto e a repartição.

## Uso

    pip install playwright && playwright install chromium
    python scripts/figuras/capturar_painel.py --dados    # descarrega o instantâneo
    python scripts/figuras/capturar_painel.py            # gera as figuras
"""

from __future__ import annotations

import argparse
import http.server
import socketserver
import threading
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BASE = "https://investigator-ddc9d8618935.herokuapp.com"
DADOS = RAIZ / "tmp" / "painel_snapshot"
FIGURAS = RAIZ / "tese-v2" / "figures"
PORTA = 8899
# A empresa da figura é escolhida por ser o caso mais nítido de discordância entre a variação
# percentual e a repartição: a ação desce e a parcela da própria empresa é positiva.
EMPRESA = "NFLX"
TICKERS = "AAPL MSFT NVDA TSLA AMZN GOOGL META JPM AMD NFLX XOM JNJ".split()


def _guardar(url: str, destino: Path) -> None:
    with urllib.request.urlopen(url, timeout=30) as r:
        destino.write_bytes(r.read())


def descarregar() -> None:
    (DADOS / "api").mkdir(parents=True, exist_ok=True)
    (DADOS / "assets" / "logos").mkdir(parents=True, exist_ok=True)
    (DADOS / "assets" / "vendor").mkdir(parents=True, exist_ok=True)
    for r in ("health", "overview", "screener", "alerts"):
        _guardar(f"{BASE}/api/{r}", DADOS / "api" / f"{r}.json")
    for t in TICKERS:
        _guardar(f"{BASE}/api/asset/{t}", DADOS / "api" / f"asset_{t}.json")
        _guardar(f"{BASE}/assets/logos/{t}.png", DADOS / "assets" / "logos" / f"{t}.png")
    _guardar(f"{BASE}/assets/vendor/lightweight-charts.js",
             DADOS / "assets" / "vendor" / "lightweight-charts.js")
    _guardar(f"{BASE}/assets/icon.svg", DADOS / "assets" / "icon.svg")
    (DADOS / "index.html").write_bytes((RAIZ / "web" / "index.html").read_bytes())
    print(f"[painel] instantaneo em {DADOS}")


class _Servidor(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = path.split("?")[0]
        if p.startswith("/api/asset/"):
            t = p.rsplit("/", 1)[-1].upper()
            f = DADOS / "api" / f"asset_{t}.json"
            return str(f if f.exists() else DADOS / "api" / "asset_TSLA.json")
        if p.startswith("/api/"):
            return str(DADOS / "api" / (p[len("/api/"):] + ".json"))
        return str(DADOS / "index.html") if p in ("/", "") else str(DADOS / p.lstrip("/"))

    def log_message(self, *a):
        pass


def _clip(pg, x, y, w, h, destino: Path) -> None:
    pg.screenshot(path=str(destino), full_page=True, clip={
        "x": round(x) - 2, "y": round(y) - 6, "width": round(w) + 4, "height": round(h) + 14})
    print(f"[painel] {destino.name}: {round(w)}x{round(h)} px de CSS")


def capturar() -> int:
    from playwright.sync_api import sync_playwright

    if not (DADOS / "index.html").exists():
        raise SystemExit("Sem instantaneo. Corre primeiro com --dados.")
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORTA), _Servidor)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 860, "height": 1400}, device_scale_factor=3)
            pg.goto(f"http://127.0.0.1:{PORTA}/?t={EMPRESA}", wait_until="load", timeout=60000)
            pg.wait_for_selector(".porta", timeout=30000)
            pg.wait_for_timeout(4000)

            a = pg.query_selector(".quem").bounding_box()
            z = pg.query_selector("#veredicto").bounding_box()
            r = pg.query_selector(".rep").bounding_box()
            _clip(pg, a["x"], a["y"], a["width"],
                  max(z["y"] + z["height"], r["y"] + r["height"]) - a["y"],
                  FIGURAS / "app_v6_empresa.png")

            s = pg.query_selector(
                "xpath=//h2[contains(., 'Why it stayed quiet')]/parent::section").bounding_box()
            _clip(pg, s["x"], s["y"], s["width"], s["height"], FIGURAS / "app_v6_silencio.png")

            print("[painel] valores das figuras, para conferir contra o texto do ch4:")
            print("   ", pg.eval_on_selector("#nome", "e => e.innerText"),
                  pg.eval_on_selector("#mv", "e => e.innerText"))
            print("   ", pg.eval_on_selector(".rep", "e => e.innerText.replace(/\\n/g, ' | ')"))
            for el in pg.query_selector_all(".porta"):
                print("    porta:", " - ".join(el.inner_text().split("\n")))
            b.close()
    finally:
        srv.shutdown()
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dados", action="store_true", help="descarrega o instantaneo da API")
    args = ap.parse_args()
    if args.dados:
        descarregar()
    else:
        raise SystemExit(capturar())
