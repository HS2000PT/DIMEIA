#!/usr/bin/env python3
"""Gera as tres capturas do painel para o Capitulo 4, a partir de um instantaneo congelado.

## Porque existe

As figuras do painel eram capturadas a mao, o que trazia tres problemas: dependiam de apanhar o
ecra num bom momento, nao eram regeneraveis quando a pagina mudasse, e o texto da dissertacao
ficava a descrever numeros de uma captura que ja nao existia — foi exatamente o que aconteceu com
a versao anterior desta figura, cujo paragrafo descrevia uma empresa que a imagem ja nao mostrava.

Aqui a captura e reprodutivel: os dados vem de ficheiros JSON descarregados uma vez da API, um
servidor local serve a pagina real sobre eles, e o Playwright fotografa. O script imprime no fim
os valores que cada figura mostra, para serem conferidos contra o texto — a regra e que o numero
da dissertacao vem daqui, e nunca da leitura da imagem.

## Quatro armadilhas que custaram tempo e ficam registadas

1. **`element.screenshot()` devolve as telas do grafico em branco** no Chromium sem interface. O
   recorte tem de ser feito com `page.screenshot(full_page=True, clip=...)`.
2. **`bounding_box()` da coordenadas do *viewport*; o `clip` de um `full_page` quer coordenadas
   da pagina.** Somar o scroll nao e detalhe: sem isso sai uma imagem plausivel, do sitio errado.
3. **Sem `locale` valido o `lightweight-charts` nao pinta.** O contentor corre com a etiqueta
   `en-US@posix`, que o `Intl` rejeita; a excecao rebenta no meio do desenho, as telas ficam no
   tamanho por defeito (300x150) e o grafico sai em branco — sem erro visivel na pagina. Uma
   figura de tese com o grafico em branco passaria despercebida ate a defesa.
4. **O cabecalho e `position: sticky`** e num `full_page` o Chromium desenha-o a meio do recorte.
   Fixa-se so para a captura.

## Porque 960 pixeis de largura

Nao e um numero redondo por acaso. A 1500 pixeis a pagina mostra a coluna do feed ao lado da
watchlist, e a figura fica com o dobro da informacao e metade do tamanho de letra depois de
reduzida a caixa de texto do documento — foi capturada assim uma vez e o texto da interface
ficou ilegivel em papel. A 960 a grelha reorganiza-se: cinco indicadores numa linha, quatro
empresas por linha, e o feed passa para baixo. A figura fica mais alta, mas cada palavra
sobrevive a reducao. A largura esta escrita na legenda da figura, para nao parecer arbitraria a
quem a le.

## Escolha das empresas, e porque nao e arbitraria

`ALVO_DETALHE` e escolhida por o titular e a parcela da empresa discordarem em sinal: e o caso
que ilustra a segunda questao de investigacao. `ALVO_MODAL` e uma empresa que nao gerou alerta.
Ambas sao verificadas contra o instantaneo antes de capturar; se a escolha deixar de servir, o
script diz e nao gera figura nenhuma.

## Uso

    pip install playwright && playwright install chromium
    python scripts/figuras/capturar_painel.py --dados    # descarrega o instantaneo
    python scripts/figuras/capturar_painel.py            # gera as figuras
"""

from __future__ import annotations

import argparse
import http.server
import json
import socketserver
import sys
import threading
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WEB = REPO / "web"
DADOS = REPO / "tmp" / "painel_snapshot"
FIGURAS = REPO / "tese-v2" / "figures"
BASE = "https://investigator-ddc9d8618935.herokuapp.com"
PORTA = 8899

ALVO_DETALHE = "NFLX"
ALVO_MODAL = "JNJ"
ROTAS = ["health", "overview", "screener", "alerts", "feedback"]
ATIVOS = ["MSFT", "TSLA", "NFLX", "AAPL", "JNJ"]


def descarregar() -> None:
    DADOS.mkdir(parents=True, exist_ok=True)
    for r in ROTAS:
        bruto = urllib.request.urlopen(f"{BASE}/api/{r}", timeout=60).read()
        (DADOS / f"{r}.json").write_bytes(bruto)
        print(f"  {r}.json")
    for t in ATIVOS:
        alvo = DADOS / f"asset_{t}.json"
        alvo.write_bytes(urllib.request.urlopen(f"{BASE}/api/asset/{t}", timeout=60).read())
        print(f"  asset_{t}.json")


class _Servidor(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = path.split("?")[0]
        if p.startswith("/api/asset/"):
            f = DADOS / f"asset_{p.rsplit('/', 1)[-1].upper()}.json"
            return str(f if f.exists() else DADOS / f"asset_{ALVO_DETALHE}.json")
        if p.startswith("/api/"):
            return str(DADOS / (p[len("/api/"):] + ".json"))
        if p in ("/", ""):
            return str(WEB / "index.html")
        return str(WEB / p.lstrip("/"))

    def log_message(self, *a):  # noqa: A002
        pass


def confirmar_escolhas() -> None:
    """A escolha das empresas tem de continuar a servir o argumento. Se deixar de servir, para."""
    ov = json.loads((DADOS / "overview.json").read_text(encoding="utf-8"))
    linhas = {r["ticker"]: r for r in ov.get("rows", [])}
    d = (linhas.get(ALVO_DETALHE) or {}).get("decomp") or {}
    mov, emp = (linhas.get(ALVO_DETALHE) or {}).get("move"), d.get("company")
    if mov is None or emp is None or (mov < 0) == (emp < 0):
        sys.exit(f"!! {ALVO_DETALHE} deixou de ter titular e parcela da empresa em sinais "
                 f"opostos (titular {mov}, empresa {emp}); escolher outra empresa.")
    print(f"  {ALVO_DETALHE}: titular {mov * 100:+.2f}%, "
          f"parcela da empresa {emp * 100:+.2f}% — serve")


def capturar() -> None:
    from playwright.sync_api import sync_playwright

    def recortar(pg, sel, path, folga=(2, 6, 4, 14)):
        bb = pg.eval_on_selector(sel, """e => { const r = e.getBoundingClientRect();
            return {x:r.x+scrollX, y:r.y+scrollY, width:r.width, height:r.height}; }""")
        e, t, w, h = folga
        pg.screenshot(path=str(path), full_page=True,
                      clip={"x": max(0, round(bb["x"] - e)), "y": max(0, round(bb["y"] - t)),
                            "width": round(bb["width"] + w), "height": round(bb["height"] + h)})
        print(f"  {path.name}: {round(bb['width'])}x{round(bb['height'])} css px")

    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 960, "height": 1200},
                            device_scale_factor=2, locale="en-US")  # ver armadilha 3
        pg = ctx.new_page()
        erros: list[str] = []
        pg.on("pageerror", lambda e: erros.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORTA}/", wait_until="load", timeout=60000)
        pg.wait_for_selector(".e", timeout=25000)
        pg.wait_for_timeout(3500)
        pg.add_style_tag(content="header, .barra { position: static !important; }")  # armadilha 4

        print("FIGURA 1 — o estado do dia")
        print("  frase:", pg.eval_on_selector("#frase", "e=>e.innerText"))
        for k in pg.eval_on_selector_all(
                ".k", "els=>els.map(e=>e.innerText.replace(/\\n/g,' · '))"):
            print("  kpi:", k)
        # ⚠️ `#colEsq > .legenda` e nao `.legenda`: desde que o grafico e o modal ganharam
        # legendas proprias, o primeiro `.legenda` do documento pode ser um deles, vazio e
        # escondido — e o recorte saia com doze pixeis de altura, sem erro nenhum.
        fim = pg.eval_on_selector("#colEsq > .legenda",
                                  "e => e.getBoundingClientRect().bottom + scrollY")
        pg.screenshot(path=str(FIGURAS / "app_v7_painel.png"), full_page=True,
                      clip={"x": 0, "y": 0, "width": 960, "height": round(fim) + 12})
        print(f"  app_v7_painel.png: 960x{round(fim) + 12} css px")

        print("FIGURA 2 — a evidencia de", ALVO_DETALHE)
        pg.evaluate("""t => { const b=[...document.querySelectorAll('.e')].find(x=>x.dataset.t===t);
                              if (b) b.click(); }""", ALVO_DETALHE)
        pg.wait_for_timeout(2000)
        # ⚠️ A figura vai em 6M e nao no 1D que a pagina abre por defeito. Nao e para embelezar:
        # o que esta figura tem de mostrar e a distincao entre o que foi assinalado e o que foi
        # enviado, e essa so existe ao longo de meses. O 1D mostra um dia, que e outra pergunta.
        pg.evaluate("""() => { const b=[...document.querySelectorAll('#intervalos button')]
                                 .find(x=>x.dataset.r==='6M'); if (b) b.click(); }""")
        pg.wait_for_timeout(2500)
        pintados = pg.evaluate("""() => {
            const c=document.querySelector('#graf canvas'); if(!c) return 0;
            const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data; let n=0;
            for(let i=3;i<d.length;i+=4) if(d[i]!==0) n++; return n; }""")
        if pintados < 1000:
            sys.exit("!! o grafico saiu em branco (ver armadilha 3); nao usar estas figuras")
        print("  veredicto:", pg.eval_on_selector(".d-ver", "e=>e.innerText"))
        print("  titular:", pg.eval_on_selector(".d-cab .mv", "e=>e.innerText"))
        for linha in pg.eval_on_selector_all(
                ".d-lin", "els=>els.map(e=>e.innerText.replace(/\\n/g,' '))"):
            print("  parcela:", linha)
        recortar(pg, ".d", FIGURAS / "app_v7_empresa.png")

        print("FIGURA 3 — o silencio de", ALVO_MODAL)
        pg.evaluate("""t => { const b=[...document.querySelectorAll('.e')].find(x=>x.dataset.t===t);
                              const pe = b && b.querySelector('.e-pe'); if (pe) pe.click(); }""",
                    ALVO_MODAL)
        pg.wait_for_timeout(1200)
        if not pg.query_selector("#modal[open]"):
            sys.exit(f"!! o modal de {ALVO_MODAL} nao abriu")
        print("  titulo:", pg.eval_on_selector("#mTit", "e=>e.textContent"))
        for li in pg.eval_on_selector_all(".m-passos li",
                                          "els=>els.map(e=>e.innerText.replace(/\\n/g,' — '))"):
            print("  passo:", li)
        recortar(pg, "#modal", FIGURAS / "app_v7_silencio.png")

        maus = [x for x in erros if "Invalid language" not in x]
        print("erros de JS:", maus if maus else "nenhum")
        b.close()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dados", action="store_true", help="descarrega o instantaneo e sai")
    args = ap.parse_args()

    if args.dados:
        print("A descarregar o instantaneo:")
        descarregar()
        return 0
    if not (DADOS / "overview.json").exists():
        print(f"Sem instantaneo em {DADOS}. Correr primeiro com --dados.")
        return 1

    confirmar_escolhas()
    socketserver.TCPServer.allow_reuse_address = True
    servidor = socketserver.TCPServer(("127.0.0.1", PORTA), _Servidor)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    try:
        FIGURAS.mkdir(parents=True, exist_ok=True)
        capturar()
    finally:
        servidor.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
