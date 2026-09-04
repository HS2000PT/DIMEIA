"""Captura a página a partir da app IMPLANTADA, para as três figuras da dissertação.

Aponta para produção de propósito. A alternativa — capturar um servidor local — produz uma
figura que documenta o que está na máquina de quem a tirou, e este projecto já pagou esse
defeito: durante uma sessão inteira a figura do painel descreveu um ecrã que já não estava
no ar.

⚠️ **AS FIGURAS v7 NÃO TINHAM GERADOR.** Foram feitas à mão, e uma figura sem fonte não se
volta a produzir: quando a página muda, ou se refaz o recorte de memória ou fica a figura
antiga. Este script é a fonte que faltava.

As três, e o que cada uma existe para mostrar:

  1. `app_v8_painel.png`   — o dia inteiro: a frase, os cinco números que repartem a
     watchlist, e a grelha de empresas com o estado de cada uma. É onde se vê que o
     silêncio é a resposta mais frequente.
  2. `app_v8_empresa.png`  — a empresa escolhida: o veredicto em palavras, a repartição do
     movimento em mercado, setor e empresa, e o gráfico com os dias assinalados. É onde se
     veem duas das três perguntas do Capítulo 1.
  3. `app_v8_silencio.png` — a lista de empresas com o estado de cada uma, incluindo a
     porta onde parou. É a parte que o canal não pode mostrar, e a razão de a página
     existir.

O recorte é de ELEMENTOS e não da página inteira: uma página com cinco mil píxeis de
altura, encolhida para a largura de uma A4, fica ilegível — e uma figura ilegível numa
dissertação é pior do que nenhuma, porque ocupa espaço e não se lê.

O QUE TEM DE BATER COM A PROSA, quando estas figuras substituirem as v7
-----------------------------------------------------------------------
A sessao 63 pagou esta licao: trocar so a imagem MUDA O DEFEITO DE SITIO, porque o texto
ao lado descreve o ecra antigo numero a numero. Antes de substituir, conferir:

  1. A LEGENDA DIZ "largura de captura de 960 pixeis" e este script usa 1420. Ou se muda a
     legenda, ou se muda o script -- mas os dois tem de dizer o mesmo.
  2. A LEGENDA DA FIGURA DA EMPRESA diz que mostra "o intervalo de seis meses", e a pagina
     abre no dia corrente. Sem escolher 6M antes de recortar, a legenda descreve outra
     figura. E e' em 6M que a distincao entre assinalar e comunicar se torna observavel,
     que e' a razao pela qual a legenda o pede.
  3. A PROSA A SEGUIR AS FIGURAS usa a empresa como caso ilustrativo da segunda questao,
     e precisa de DISCORDANCIA: preco a descer com a parcela da propria empresa POSITIVA.
     A captura de 2026-09-04 (Apple, -2,54%) tem as tres parcelas negativas e nao serve
     para esse paragrafo. Escolher a empresa com --ticker, ou reescrever o paragrafo.
  4. A DATA na legenda.

USO
---
    python scripts/screenshot_v8.py                          # produção
    python scripts/screenshot_v8.py --ticker AAPL            # empresa fixa
    python scripts/screenshot_v8.py --url http://127.0.0.1:8010
"""

from __future__ import annotations

import argparse
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
FIGURAS = RAIZ / "tese-pt" / "figures"
PROD = "https://investigator-ddc9d8618935.herokuapp.com"


def main() -> int:
    p = argparse.ArgumentParser(description="Capturas da app para a dissertação.")
    p.add_argument("--url", default=PROD)
    p.add_argument("--ticker", default="",
                   help="empresa a mostrar; por omissão, a que a própria página destaca")
    p.add_argument("--sufixo", default="v8", help="prefixo dos ficheiros (app_<sufixo>_*.png)")
    args = p.parse_args()

    from playwright.sync_api import sync_playwright

    FIGURAS.mkdir(parents=True, exist_ok=True)
    alvo = f"{args.url}/?t={args.ticker}" if args.ticker else args.url
    saidas: list[str] = []

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        # Tema claro à força: a dissertação é impressa em papel branco, e um recorte escuro
        # gasta tinta e perde contraste. `device_scale_factor=2` porque a figura é reduzida
        # à largura do texto e a 1x o tipo de letra sairia esfarrapado.
        pg = b.new_page(viewport={"width": 1420, "height": 1100}, device_scale_factor=2,
                        color_scheme="light")
        pg.goto(alvo, wait_until="networkidle", timeout=60000)
        pg.wait_for_selector("#kpis .k", timeout=45000)
        pg.wait_for_selector("#empresas .e", timeout=45000)
        pg.wait_for_timeout(2000)  # as faíscas e o gráfico acabam de ser desenhados

        escolhida = pg.eval_on_selector(
            '.e[aria-pressed="true"]', "e => e.dataset.t || e.textContent.trim().slice(0,6)")
        n_emp = pg.locator("#empresas .e").count()

        # ── 1) o dia inteiro ────────────────────────────────────────────────
        # Recorta do topo da secção do dia até ao fim da grelha de empresas. Sem o recorte
        # entrava metade da coluna das mensagens cortada a meio de uma frase, que é o
        # aspecto de uma captura tirada à pressa.
        caixa = pg.evaluate("""() => {
            const a = document.querySelector('#secHoje').getBoundingClientRect();
            const b = document.querySelector('#empresas').getBoundingClientRect();
            return {x: Math.max(0, a.left - 8), y: a.top + scrollY - 8,
                    width: Math.min(a.width + 16, innerWidth),
                    height: (b.top + scrollY) - (a.top + scrollY) + b.height + 16};
        }""")
        pg.screenshot(path=str(FIGURAS / f"app_{args.sufixo}_painel.png"),
                      clip=caixa, full_page=True)
        saidas.append(f"app_{args.sufixo}_painel.png")
        print(f"painel    · {n_emp} empresas, empresa em destaque: {escolhida}")

        # ── 2) a empresa escolhida ──────────────────────────────────────────
        det = pg.locator("#detalhe")
        det.scroll_into_view_if_needed()
        pg.wait_for_timeout(800)
        det.screenshot(path=str(FIGURAS / f"app_{args.sufixo}_empresa.png"))
        saidas.append(f"app_{args.sufixo}_empresa.png")
        print(f"empresa   · {escolhida}")

        # ── 3) o silêncio ───────────────────────────────────────────────────
        # ⚠️ O que a legenda descreve é o MODAL de uma empresa que parou -- a lista das
        # portas que atravessou, com a rejeição no fim. Não é a grelha: a grelha diz que
        # parou, o modal diz ONDE e porquê, e é isso que torna o silêncio inspeccionável.
        # O gatilho é o rodapé do cartão, não o cartão (que seleciona a empresa).
        travadas = pg.evaluate(
            "() => [...document.querySelectorAll('#empresas .e')]"
            ".filter(e => /stopped/i.test(e.textContent)).map(e => e.dataset.t)")
        if not travadas:
            print("AVISO: nenhuma empresa parada numa porta; o modal do silêncio não foi "
                  "capturado. Repetir num dia com o orçamento esgotado.")
        else:
            pg.set_viewport_size({"width": 1000, "height": 1100})
            pg.wait_for_timeout(500)
            alvo_e = travadas[0]
            pg.locator(f'#empresas .e[data-t="{alvo_e}"] .e-pe').click()
            pg.wait_for_selector("#modal[open]", timeout=10000)
            pg.wait_for_timeout(600)
            pg.locator("#modal").screenshot(
                path=str(FIGURAS / f"app_{args.sufixo}_silencio.png"))
            saidas.append(f"app_{args.sufixo}_silencio.png")
            portas = pg.locator("#modal .m-passos li").count()
            print(f"silêncio  · {alvo_e}, {portas} portas, {len(travadas)} de {n_emp} paradas")

        b.close()

    for f in saidas:
        kb = (FIGURAS / f).stat().st_size // 1024
        print(f"  {f}: {kb} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
