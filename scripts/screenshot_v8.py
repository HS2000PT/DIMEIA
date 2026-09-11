"""Capturas de revisão do painel atual (o nome do comando mantém compatibilidade).

Por omissão escreve em output/painel-v9. As figuras históricas das dissertações não são
substituídas: isso exige rever, em ambas as línguas, a data, os números e a legenda.

    python scripts/screenshot_v8.py --ticker AAPL
    python scripts/screenshot_v8.py --url http://127.0.0.1:8879

O intervalo de seis meses e a ressalva do ajuste fazem parte da captura da empresa.
O modal mostra decisões registadas; não inventa um percurso linear pelas portas.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# A aplicacao imprime o sinal menos tipografico (U+2212) e a consola do Windows e cp1252:
# sem isto o script morre DEPOIS de capturar, ao imprimir o que capturou. E a mesma classe
# que a sessao 68 corrigiu no check_prontidao_defesa -- um script que rebenta a relatar o
# que fez e indistinguivel de um script que falhou.
for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = Path(__file__).resolve().parents[1]
PROD = "https://investigator-ddc9d8618935.herokuapp.com"


def capturar(url: str, ticker: str, destino: Path, sufixo: str = "v9") -> None:
    from playwright.sync_api import sync_playwright

    destino.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1420, "height": 1100},
                                device_scale_factor=2, color_scheme="light", locale="en-GB")
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.locator("#empresas .company").first.wait_for(timeout=45000)
        if ticker:
            page.locator(f'#empresas .company[data-t="{ticker.upper()}"]').click()
        page.locator(".d-ver").wait_for(timeout=30000)
        page.locator("#graf canvas").first.wait_for(timeout=30000)
        chosen = page.locator('.company[aria-pressed="true"]').get_attribute("data-t")
        if ticker and chosen != ticker.upper():
            raise RuntimeError(f"Pedido {ticker}, obtido {chosen}")
        page.screenshot(path=str(destino / f"app_{sufixo}_painel.png"))

        page.get_by_role("button", name="6M", exact=True).click()
        page.locator(".fit-details summary").click()
        page.locator(".chart-options summary").click()
        page.get_by_label("Rarity scale (z)", exact=True).check()
        page.locator("#grafZ canvas").first.wait_for()
        page.locator(".chart-options summary").click()

        def crop(selector, name):
            # Canvas em capturas de elemento já saiu em branco: recortar a página inteira.
            box = page.locator(selector).evaluate("""e => {
                const r=e.getBoundingClientRect();
                return {x:r.x+scrollX, y:r.y+scrollY, width:r.width, height:r.height};
            }""")
            page.screenshot(path=str(destino / f"app_{sufixo}_{name}.png"),
                            full_page=True, clip=box)

        # A vista da empresa vai com o painel da conta FECHADO, que é como a aplicação abre e
        # é o que mantém o rácio da figura dentro de uma página; a conta sai em figura própria.
        page.locator(".fit-details summary").click()
        crop("#detalhe", "empresa")
        page.locator(".fit-details summary").click()
        page.locator(".f-conta").wait_for(timeout=10000)
        crop(".fit-details", "conta")
        print("Conta:", page.locator(".f-conta").inner_text().replace(chr(10), " | "))
        print("Empresa:", chosen, page.locator(".d-cab .mv").inner_text())
        print("Veredicto:", page.locator(".d-ver").inner_text())
        print("Ajuste:", page.locator(".fit-details").inner_text())
        page.get_by_role("button", name="Recorded news decisions", exact=True).click()
        page.locator(".decision-list").wait_for(timeout=30000)
        crop("#modal", "decisoes")
        print("Decisões:", page.locator(".decision-list").inner_text())
        if errors:
            raise RuntimeError(f"Erros JavaScript na captura: {errors}")
        browser.close()
    print("Capturas:", destino)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=PROD)
    parser.add_argument("--ticker", default="")
    parser.add_argument("--sufixo", default="v9")
    parser.add_argument("--output", type=Path, default=RAIZ / "output/painel-v9")
    args = parser.parse_args()
    capturar(args.url, args.ticker, args.output, args.sufixo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
