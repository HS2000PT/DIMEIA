"""Converte a marca "The Tail" de SVG para PNG, para o LaTeX poder incluí-la.

O LaTeX não lê SVG. A alternativa habitual — redesenhar o glifo em TikZ — cria uma **segunda
cópia** da marca que alguém teria de manter igual à primeira, e uma marca que diverge de si
própria entre o site e os slides é exactamente o defeito que este script existe para evitar.

Aqui há uma só fonte de verdade, `app/assets/logo.svg`, e o PNG é derivado dela.

Duas variantes, porque o fundo mudou de cor conforme o sítio:
  * `logo_tail.png`       verde escuro sobre transparente — slides e guia, fundo claro
  * `logo_tail_icone.png` o ícone com o contentor escuro — onde a plataforma desenha um quadrado

USO
---
    python scripts/render_logo.py
"""

from __future__ import annotations

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
FONTES = RAIZ / "app" / "assets"
DESTINO = RAIZ / "tese" / "figures"

# (svg de origem, png de destino, largura em píxeis)
PECAS = [
    ("logo.svg", "logo_tail.png", 1024),
    ("icon.svg", "logo_tail_icone.png", 512),
    # A marca por extenso: o glifo mais o nome, com o "G" a verde. É esta que vai para a capa
    # dos slides e do guia — o ícone sozinho não diz o nome a quem está a ver pela primeira vez.
    ("logo-lockup.svg", "logo_lockup.png", 1240),
]


def main() -> int:
    from playwright.sync_api import sync_playwright

    DESTINO.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for svg, png, largura in PECAS:
            origem = FONTES / svg
            if not origem.exists():
                print(f"!! falta {origem}")
                return 1
            # A caixa segue a proporção do próprio SVG: a marca é quadrada, o lockup é uma
            # tira larga, e forçar os dois ao mesmo formato deixaria metade em vazio.
            alto = largura if "lockup" not in svg else round(largura * 104 / 620)
            pg = b.new_page(viewport={"width": largura, "height": alto},
                            device_scale_factor=1)
            # Fundo transparente: o glifo do `logo.svg` é nu de propósito, e um fundo branco
            # imprimiria um quadrado branco por cima do slide.
            pg.goto(origem.as_uri())
            pg.eval_on_selector("svg", "e => { e.setAttribute('width','100%');"
                                       " e.setAttribute('height','100%'); }")
            pg.screenshot(path=str(DESTINO / png), omit_background=True)
            pg.close()
            kb = (DESTINO / png).stat().st_size // 1024
            print(f"{png}: {largura}px, {kb} KB")
        b.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
