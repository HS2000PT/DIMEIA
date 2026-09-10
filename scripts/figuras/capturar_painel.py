#!/usr/bin/env python3
"""Capturas de revisão v9 em output/painel-v9-congelado, sem substituir as teses.

Histórico do gerador (v7/v8):
Gera as tres capturas do painel para o Capitulo 4, a partir de um instantaneo congelado.

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
FIGURAS = REPO / "output" / "painel-v9-congelado"
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
    def do_GET(self):
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(self.path)
        if parsed.path == "/api/alerts":
            query = parse_qs(parsed.query)
            payload = json.loads((DADOS / "alerts.json").read_text(encoding="utf-8"))
            rows = payload["rows"]
            ticker = query.get("ticker", [None])[0]
            if ticker:
                rows = [r for r in rows if r["ticker"] == ticker]
            limit = min(200, max(1, int(query.get("limit", [200])[0])))
            # Primeira página; o total declara só a cobertura capturada, nunca o canal todo.
            body = json.dumps({"rows": rows[-limit:], "total": len(rows),
                               "remaining": max(0, len(rows)-limit),
                               "next_before": None, "stale": False}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

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
    if any("price_day" not in row for row in linhas.values()):
        sys.exit("Dados anteriores à v9. Correr --dados para capturar o contrato atual.")
    d = (linhas.get(ALVO_DETALHE) or {}).get("decomp") or {}
    mov, emp = (linhas.get(ALVO_DETALHE) or {}).get("move"), d.get("company")
    if mov is None or emp is None or (mov < 0) == (emp < 0):
        sys.exit(f"!! {ALVO_DETALHE} deixou de ter titular e parcela da empresa em sinais "
                 f"opostos (titular {mov}, empresa {emp}); escolher outra empresa.")
    print(f"  {ALVO_DETALHE}: titular {mov * 100:+.2f}%, "
          f"parcela da empresa {emp * 100:+.2f}% — serve")


def capturar() -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "captura_atual", REPO / "scripts/screenshot_v8.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.capturar(f"http://127.0.0.1:{PORTA}", ALVO_DETALHE, FIGURAS)


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
