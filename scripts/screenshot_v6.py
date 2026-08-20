"""Captura a página (v6.1) a partir da app IMPLANTADA, para a figura da dissertação.

Aponta para produção de propósito. A alternativa — capturar um servidor local — produz uma
figura que documenta o que está na máquina de quem a tirou, e este projecto já pagou esse
defeito: durante uma sessão inteira a figura do painel descreveu um ecrã que já não estava no ar.

Duas capturas, e as duas são recortes de ELEMENTOS e não da página inteira. Uma página inteira
com cinco mil píxeis de altura, encolhida para a largura de uma página A4, fica ilegível — e uma
figura ilegível numa dissertação é pior do que nenhuma, porque ocupa espaço e não se lê.

  1. `app_v6_empresa.png`  — a empresa escolhida: o veredicto em palavras, a repartição do
     movimento e o gráfico com os dias assinalados. É onde se vêem duas das três perguntas.
  2. `app_v6_silencio.png` — o funil das decisões do dia: onde cada empresa parou e a margem
     que faltou. É a parte que o canal não pode mostrar, e a razão de a página existir.

USO
---
    python scripts/screenshot_v6.py                      # produção
    python scripts/screenshot_v6.py --url http://127.0.0.1:8010
"""

from __future__ import annotations

import argparse
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
FIGURAS = RAIZ / "tese" / "figures"
PROD = "https://investigator-ddc9d8618935.herokuapp.com"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", default=PROD)
    p.add_argument("--ticker", default="", help="empresa a mostrar (por defeito, a que a "
                                                "própria página destaca)")
    args = p.parse_args()

    from playwright.sync_api import sync_playwright

    FIGURAS.mkdir(parents=True, exist_ok=True)
    alvo = f"{args.url}/?t={args.ticker}" if args.ticker else args.url

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        # Tema claro à força: a dissertação é impressa em papel branco, e um recorte escuro
        # gasta tinta e perde contraste. `device_scale_factor=2` porque a figura é redimensionada
        # para a largura do texto e a 1x ficaria com o texto esfarrapado.
        pg = b.new_page(viewport={"width": 1420, "height": 1000}, device_scale_factor=2,
                        color_scheme="light")

        pg.goto(alvo, wait_until="networkidle", timeout=60000)
        pg.wait_for_selector("#grafico canvas", timeout=45000)
        pg.wait_for_selector("#dias .dia", timeout=45000)
        pg.wait_for_timeout(1500)   # a linha e as marcas acabam de ser desenhadas

        escolhida = pg.eval_on_selector(
            '.tk[aria-pressed="true"]', "e => e.dataset.t")

        # ⚠️ O recorte é do elemento e não da janela: sem isto entrava meia coluna da direita
        # cortada a meio de uma frase, que é o aspecto de uma captura tirada à pressa.
        pg.locator("section[aria-label='The selected company']").screenshot(
            path=str(FIGURAS / "app_v6_empresa.png"))
        print(f"app_v6_empresa.png   ({escolhida})")

        # O funil está no fim da página: rola-se até lá para que os tipos de letra e as caixas
        # estejam desenhados antes de recortar.
        funil = pg.locator("#funil")
        funil.scroll_into_view_if_needed()
        pg.wait_for_timeout(400)
        etapas = pg.locator(".etapa").count()
        funil.screenshot(path=str(FIGURAS / "app_v6_silencio.png"))
        print(f"app_v6_silencio.png  ({etapas} etapas)")

        b.close()

    for f in ("app_v6_empresa.png", "app_v6_silencio.png"):
        kb = (FIGURAS / f).stat().st_size // 1024
        print(f"  {f}: {kb} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
