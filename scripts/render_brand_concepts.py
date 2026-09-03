"""Folha de comparacao das marcas, as escalas reais.

O criterio escrito em docs/design/brand.md diz que uma marca nova so entra se for legivel a
16 px com a silhueta reconhecivel. Isso nao se decide a olhar para um SVG a 512 px, que e o
erro que fez "The Stare" ser escolhida e depois cair. Portanto: render de verdade, aos tamanhos
onde a marca vive, com a ACTUAL como controlo -- sem controlo nao se sabe se o novo e melhor
ou so diferente.
"""

import pathlib

from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "app/assets/concepts/comparacao.png"
TAMANHOS = [16, 24, 32, 48, 88, 160]

MARCAS = [
    ("ACTUAL — The Tail", RAIZ / "app/assets/logo.svg"),
    ("B — Pupil Tick", RAIZ / "app/assets/concepts/pupil-tick.svg"),
    ("D — Chartback (final)", RAIZ / "app/assets/concepts/chartback.svg"),
]

linhas = []
for nome, caminho in MARCAS:
    if not caminho.exists():
        continue
    svg = caminho.read_text(encoding="utf-8")
    celulas = "".join(
        f'<td><div class="box" style="width:{s}px;height:{s}px">{svg}</div>'
        f'<div class="cap">{s}px</div></td>'
        for s in TAMANHOS
    )
    linhas.append(f'<tr><th>{nome}</th>{celulas}</tr>')

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
 body {{ background:#F4F7FA; font:13px/1.4 ui-sans-serif,system-ui,sans-serif; padding:22px;
         color:#0F141B; }}
 table {{ border-collapse:collapse }}
 th {{ text-align:left; padding:14px 20px 14px 0; font-weight:650; white-space:nowrap }}
 td {{ padding:14px 18px; text-align:center; vertical-align:middle }}
 .box svg {{ width:100%; height:100% ; display:block }}
 .box {{ display:inline-block }}
 .cap {{ font:11px ui-monospace,monospace; color:#63728A; margin-top:7px }}
 tr:nth-child(even) {{ background:#EAF0F6 }}
 h2 {{ margin:0 0 4px; font-size:15px }}
 p  {{ margin:0 0 18px; color:#48566B }}
 .dark {{ background:#0B0E13; margin-top:26px; padding:18px; border-radius:10px }}
 .dark th {{ color:#EDF1F7 }} .dark .cap {{ color:#7C8AA3 }}
 .dark tr:nth-child(even) {{ background:#131820 }}
</style></head><body>
 <h2>Marcas as escalas reais &mdash; a ACTUAL como controlo</h2>
 <p>16&nbsp;px e onde vive um favicon. Uma marca que so funciona a 160&nbsp;px nao serve.</p>
 <table>{''.join(linhas)}</table>
 <div class="dark"><table>{''.join(linhas)}</table></div>
</body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1180, "height": 900})
    pg.set_content(html)
    pg.wait_for_timeout(600)
    pg.screenshot(path=str(SAIDA), full_page=True)
    b.close()
print("->", SAIDA)
