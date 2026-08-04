"""Logótipos reais das tecnologias para os slides e para o guia de estudo.

PORQUÊ ESTE SCRIPT
------------------
Desde a sessão 40 que os três decks chamam `\\techlogo{...}` / `\\glogo{...}`, macros que
mostram o logótipo **se o PNG existir** e degradam para um badge de nome se não existir.
Nunca existiu nenhum PNG: `slides/logos/` só tinha um README a explicar como os obter à mão.
Ou seja, o mecanismo estava ligado e a mostrar sempre o caminho de recurso. Isto resolve isso
sem trabalho manual e, mais importante, de forma **reproduzível**.

DE ONDE VÊM
-----------
`simple-icons`, o conjunto de ícones de marca que a maior parte da indústria usa. Três razões
para o preferir a andar a apanhar PNGs em sites oficiais:

1. **Licença clara.** O conjunto de ícones é CC0 1.0 (domínio público). As *marcas* continuam,
   claro, a pertencer aos seus donos — o uso aqui é nominativo (identificar a tecnologia
   usada), que é o uso normal num deck académico. Fica dito no MANIFEST.
2. **Uniformidade.** Todos partilham a mesma grelha de 24×24 e o mesmo peso óptico, portanto
   uma linha de logótipos alinha. Logótipos apanhados um a um em sites diferentes vêm com
   margens e proporções diferentes e a linha fica torta — foi por isso que o README antigo
   avisava "ou pões todos os de uma linha, ou nenhum".
3. **Cor oficial da própria fonte.** O hex de cada marca é lido do ficheiro de dados do
   pacote, não escolhido a olho.

VERSÃO FIXADA, e não `@latest`: um deck que compila com logótipos diferentes consoante o dia
em que se corre o script não é reproduzível, e este projecto fixa o SHA256 até do modelo ONNX.

O QUE FALHA ABERTO
------------------
`finnhub` e o `sentence-transformers` não existem no simple-icons. Vão a fontes próprias e, se
essas falharem, o ficheiro simplesmente não é escrito — a macro do LaTeX volta ao badge de
nome, que é exactamente o comportamento desenhado. Falhar aberto, mas em voz alta: o resumo
final diz quais ficaram por obter.

USO
---
    python scripts/fetch_slide_logos.py            # tecnologias
    python scripts/fetch_slide_logos.py --empresas # + as 12 da watchlist
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "slides" / "logos"
DESTINO_EMPRESAS = DESTINO / "companies"
LOGOS_APP = RAIZ / "app" / "assets" / "logos"

# Fixada de propósito. Actualizar é uma decisão consciente, não um efeito secundário do relógio.
VERSAO = "16.28.0"
CDN = f"https://cdn.jsdelivr.net/npm/simple-icons@{VERSAO}"

ALTURA_PX = 512  # renderiza grande e deixa o LaTeX reduzir para 13pt: bordos limpos

# ficheiro esperado pelo .tex  ->  slug no simple-icons
#
# `yfinance` usa o logótipo do Yahoo porque a biblioteca é um cliente da Yahoo Finance e é
# essa a fonte de dados que o slide está a creditar — é o que o README já sugeria.
TECNOLOGIAS: dict[str, str] = {
    "huggingface": "huggingface",
    "rss": "rss",
    "scikit-learn": "scikitlearn",
    "pytorch": "pytorch",
    "onnx": "onnx",
    "telegram": "telegram",
    "streamlit": "streamlit",
    "plotly": "plotly",
    "python": "python",
    "githubactions": "githubactions",
    "pytest": "pytest",
    # Disponíveis para frames futuros; custam um pedido cada e evitam nova ida à rede.
    "github": "github",
    "pandas": "pandas",
    "numpy": "numpy",
    "ruff": "ruff",
    "scipy": "scipy",
    "jupyter": "jupyter",
    "latex": "latex",
}

# Sem entrada no simple-icons (o conjunto retira marcas a pedido dos donos — o Yahoo e a
# Heroku já não estão lá, e um `@latest` do jsDelivr chegou a devolver 200 para um ficheiro
# que a versão fixada não tem: mais uma vez, o código de estado não é a verificação).
# Fontes próprias, e cada uma pode falhar sem partir nada.
FORA_DO_CONJUNTO: dict[str, list[str]] = {
    "yfinance": [
        # A biblioteca não tem logótipo próprio; o slide credita a fonte de dados, que é a
        # Yahoo Finance. É o que o README desta pasta já sugeria.
        "https://s.yimg.com/rz/p/yahoo_finance_en-US_h_p_finance_2.png",
    ],
    "heroku": [
        "https://upload.wikimedia.org/wikipedia/commons/e/ec/Heroku_logo.svg",
    ],
    "finnhub": [
        "https://finnhub.io/static/img/finnhub_logo.svg",
        "https://finnhub.io/static/img/logo.png",
        "https://finnhub.io/favicon.ico",
    ],
    "sbert": [
        "https://www.sbert.net/_static/logo.png",
        "https://sbert.net/_static/logo.png",
    ],
}


def buscar(url: str, timeout: int = 30) -> bytes:
    pedido = urllib.request.Request(url, headers={"User-Agent": "InvestiGator/1.0 (thesis)"})
    with urllib.request.urlopen(pedido, timeout=timeout) as resposta:
        return resposta.read()


def cores_das_marcas() -> dict[str, str]:
    """O hex oficial de cada marca, lido do ficheiro de dados do próprio pacote."""
    bruto = json.loads(buscar(f"{CDN}/data/simple-icons.json").decode("utf-8"))
    icones = bruto["icons"] if isinstance(bruto, dict) else bruto
    cores: dict[str, str] = {}
    for icone in icones:
        titulo = icone.get("title", "")
        slug = icone.get("slug") or re.sub(r"[^a-z0-9]", "", titulo.lower())
        cores[slug] = icone.get("hex", "000000")
    return cores


def colorir(svg: str, hex_cor: str) -> str:
    """Injecta a cor da marca no <svg>. Sem isto, o simple-icons renderiza preto."""
    if "fill=" in svg.split(">", 1)[0]:
        return svg
    return svg.replace("<svg ", f'<svg fill="#{hex_cor}" ', 1)


def svg_para_png(pagina, svg: str, lado: int = ALTURA_PX) -> bytes:
    """Rasteriza com o Chromium do Playwright.

    O `cairosvg` seria o caminho óbvio, mas em Windows arrasta bibliotecas nativas do Cairo
    que costumam não instalar. O Playwright já é dependência deste projecto (é com ele que as
    figuras da tese são capturadas), portanto é uma dependência a menos e um motor a mais.
    """
    pagina.set_viewport_size({"width": lado, "height": lado})
    pagina.set_content(
        "<style>html,body{margin:0;padding:0;background:transparent}"
        f"svg{{width:{lado}px;height:{lado}px;display:block}}</style>{svg}"
    )
    elemento = pagina.query_selector("svg")
    if elemento is None:
        raise RuntimeError("o SVG não chegou ao DOM")
    return elemento.screenshot(omit_background=True)


def normalizar_empresa(origem: pathlib.Path, altura: int = 256) -> bytes:
    """Logótipo de empresa -> PNG de altura fixa, com a proporção preservada.

    Os ficheiros vêm da Polygon em três formatos (webp/jpg/png) e em tamanhos diferentes.
    Numa linha de slide isso lê-se como desalinhamento, não como variedade.
    """
    from PIL import Image

    with Image.open(origem) as img:
        img = img.convert("RGBA")
        # Os JPEG vêm com fundo branco sólido; num slide de fundo branco (tema Madrid) não se
        # nota, mas a caixa nota-se. Aparar a moldura uniforme resolve os dois casos.
        fundo = img.getpixel((0, 0))
        if fundo[3] == 255 and all(canal > 245 for canal in fundo[:3]):
            from PIL import ImageChops

            solido = Image.new("RGBA", img.size, fundo)
            caixa = (
                ImageChops.difference(img, solido)
                .convert("L")
                .point(lambda p: 255 if p > 12 else 0)
            )
            limites = caixa.getbbox()
            if limites:
                img = img.crop(limites)
        largura = max(1, round(img.width * altura / img.height))
        img = img.resize((largura, altura), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()


def main() -> int:
    analisador = argparse.ArgumentParser(description=__doc__)
    analisador.add_argument(
        "--empresas",
        action="store_true",
        help="converter também os logótipos das empresas de app/assets/logos/",
    )
    argumentos = analisador.parse_args()

    DESTINO.mkdir(parents=True, exist_ok=True)
    escritos: list[tuple[str, int, str]] = []
    falhados: list[tuple[str, str]] = []

    print(f"simple-icons {VERSAO} (fixada)")
    cores = cores_das_marcas()
    print(f"  {len(cores)} marcas no ficheiro de dados\n")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page()

        for ficheiro, slug in TECNOLOGIAS.items():
            try:
                svg = buscar(f"{CDN}/icons/{slug}.svg").decode("utf-8")
                png = svg_para_png(pagina, colorir(svg, cores.get(slug, "000000")))
                caminho = DESTINO / f"{ficheiro}.png"
                caminho.write_bytes(png)
                digest = hashlib.sha256(png).hexdigest()
                escritos.append((f"{ficheiro}.png", len(png), digest))
                print(f"  OK    {ficheiro:16s} <- simple-icons/{slug}  #{cores.get(slug, '?')}")
            except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError, OSError) as erro:
                falhados.append((ficheiro, str(erro)))
                print(f"  FALHA {ficheiro:16s} {erro}")

        for ficheiro, urls in FORA_DO_CONJUNTO.items():
            for url in urls:
                try:
                    dados = buscar(url, timeout=20)
                    if url.endswith(".svg"):
                        dados = svg_para_png(pagina, dados.decode("utf-8"))
                    else:
                        from PIL import Image

                        with Image.open(io.BytesIO(dados)) as img:
                            img = img.convert("RGBA")
                            escala = ALTURA_PX / max(img.width, img.height)
                            img = img.resize(
                                (
                                    max(1, round(img.width * escala)),
                                    max(1, round(img.height * escala)),
                                ),
                                Image.LANCZOS,
                            )
                            buffer = io.BytesIO()
                            img.save(buffer, format="PNG")
                            dados = buffer.getvalue()
                    caminho = DESTINO / f"{ficheiro}.png"
                    caminho.write_bytes(dados)
                    escritos.append(
                        (f"{ficheiro}.png", len(dados), hashlib.sha256(dados).hexdigest())
                    )
                    print(f"  OK    {ficheiro:16s} <- {url}")
                    break
                except Exception as erro:  # noqa: BLE001 — qualquer falha aqui degrada para badge
                    ultimo = f"{url}: {erro}"
            else:
                falhados.append((ficheiro, ultimo))
                print(f"  FALHA {ficheiro:16s} sem fonte utilizável -> fica badge de nome")

        navegador.close()

    if argumentos.empresas:
        print()
        DESTINO_EMPRESAS.mkdir(parents=True, exist_ok=True)
        if not LOGOS_APP.exists():
            print(f"  FALHA  {LOGOS_APP} não existe — corre scripts/fetch_logos.py primeiro")
        else:
            for origem in sorted(LOGOS_APP.iterdir()):
                if origem.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                    continue
                try:
                    png = normalizar_empresa(origem)
                    caminho = DESTINO_EMPRESAS / f"{origem.stem}.png"
                    caminho.write_bytes(png)
                    escritos.append(
                        (f"companies/{origem.stem}.png", len(png), hashlib.sha256(png).hexdigest())
                    )
                    print(f"  OK    {origem.stem:16s} <- app/assets/logos/{origem.name}")
                except Exception as erro:  # noqa: BLE001
                    falhados.append((origem.stem, str(erro)))
                    print(f"  FALHA {origem.stem:16s} {erro}")

    linhas = [
        "# Logótipos — proveniência",
        "",
        "> Gerado por `python scripts/fetch_slide_logos.py`. **Não editar à mão.**",
        "",
        f"- Conjunto de ícones: **simple-icons {VERSAO}** (versão fixada), licença **CC0 1.0**.",
        "- As marcas pertencem aos respectivos donos; o uso aqui é nominativo — identificar a",
        "  tecnologia usada num deck académico.",
        "- Logótipos de empresas: obtidos pela Polygon.io (`scripts/fetch_logos.py`) e",
        "  normalizados para altura fixa. Marcas dos respectivos donos.",
        "- A cor de cada ícone é o hex oficial declarado pelo próprio pacote,",
        "  não escolhido à vista.",
        "",
        "| ficheiro | bytes | sha256 |",
        "|---|---:|---|",
    ]
    for nome, tamanho, digest in sorted(escritos):
        linhas.append(f"| `{nome}` | {tamanho} | `{digest[:16]}…` |")
    if falhados:
        linhas += [
            "",
            "## Sem logótipo (o LaTeX mostra o badge de nome, por desenho)",
            "",
        ]
        linhas += [f"- `{nome}` — {razao}" for nome, razao in falhados]
    (DESTINO / "MANIFEST.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print(f"\n{len(escritos)} escritos, {len(falhados)} sem logótipo -> {DESTINO / 'MANIFEST.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
