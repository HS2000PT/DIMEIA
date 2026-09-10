"""A decomposicao de um movimento, medida sobre o mapa de setores alargado.

⚠️ A POPULACAO SAO OS 17 DE `SECTOR_OF`, e nao os 12 da lista vigiada. Este ficheiro
dizia «a watchlist implantada» e a seccao 2 do relatorio chamava-se «A watchlist toda»,
enquanto o `main()` percorre `sorted(SECTOR_OF)`. A designacao errada propagou-se para
dois sitios do Capitulo 4 e para a etiqueta da porta dos numeros: a mediana de 0,460 era
atribuida a doze empresas e e' medida sobre dezassete. Corrigido a 2026-09-10 na raiz,
para uma regeneracao nao reintroduzir o erro.

Responde a segunda das tres perguntas do trabalho: *foi a empresa, ou foi o mercado?*
Produz (a) um exemplo trabalhado com todos os passos intermedios, para a tese, e (b) a
distribuicao das tres componentes sobre a watchlist, para se saber com que frequencia a
resposta e "foi o mercado".

Corre com:
    python scripts/evaluate_decomposition.py

Escreve `docs/evaluation/evaluation_decomposition.md`, que a dissertacao CITA.

⚠️ ESTE FICHEIRO E' CONGELADO NA PRATICA, e o docstring dizia o contrario ate 2026-09-10
(«Nao toca em nada congelado»). A §5.5 cita dele a mediana `0,460`, a quota mediana `0,487`
e o caso trabalhado da AMD. Uma corrida sem `--out` substitui os tres.

⚠️ E A CORRIDA NAO E' REPRODUTIVEL: o caso trabalhado e' o maior movimento do DIA em que o
script corre, sobre precos buscados ao vivo. Regenerar muda o exemplo -- verificado, passou
de AMD `+6,2944%` a META `+6,3486%` -- e obriga a propagar para a §5.5. Usar `--out` para
qualquer verificacao, e regenerar so' com intencao.
"""

from __future__ import annotations

import datetime as _dt
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from investigator.correlation_engine.decomposition import (  # noqa: E402
    MIN_WINDOW,
    PRIOR_BETA_MARKET,
    PRIOR_BETA_SD,
    PRIOR_BETA_SECTOR,
    decompose_move,
)
from investigator.market_data.prices import load_close_series  # noqa: E402
from investigator.news_fetcher.relevance import (  # noqa: E402
    MARKET_INDEX,
    SECTOR_OF,
    sector_etf,
)

MERCADO = MARKET_INDEX
JANELA = 20
SAIDA = pathlib.Path("docs/evaluation/evaluation_decomposition.md")


def retornos(fecho) -> np.ndarray:
    v = np.asarray(fecho, dtype=float)
    return np.diff(np.log(v))


def carregar(tickers: list[str], dias: int = 120) -> dict[str, np.ndarray]:
    """Uma so chamada de rede para todas as series, convertidas em log-retornos."""
    fim = _dt.date.today()
    inicio = fim - _dt.timedelta(days=int(dias * 1.6))  # folga para fins de semana e feriados
    bruto = load_close_series(tickers, inicio.isoformat(), fim.isoformat())
    saida = {}
    for tk, s in bruto.items():
        v = np.asarray(s.dropna(), dtype=float)
        if len(v) < JANELA + 5:
            print(f"  [aviso] {tk}: serie curta demais ({len(v)}).")
            continue
        saida[tk] = retornos(v)
    return saida


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Decomposicao de um movimento.")
    # ⚠️ O DEFAULT E' O CAMINHO CONGELADO, de proposito: mudar o default mudaria o
    # comportamento de quem regenera legitimamente. O que faltava era a POSSIBILIDADE de
    # nao o escrever, e era essa ausencia que tornava impossivel seguir a regra do brief.
    ap.add_argument("--out", default=str(SAIDA),
                    help="destino do relatorio; usar um caminho fora de docs/ para "
                         "qualquer verificacao, para nao substituir o artefacto citado")
    args = ap.parse_args()
    saida = pathlib.Path(args.out)

    tickers = sorted(SECTOR_OF)
    etfs = sorted({e for e in (sector_etf(t) for t in tickers) if e})
    print(f"A carregar {len(tickers)} tickers + mercado + {len(etfs)} setores...")

    series = carregar([MERCADO, *etfs, *tickers])
    r_mercado = series.get(MERCADO)
    if r_mercado is None:
        print("ERRO: sem serie de mercado, nao ha decomposicao possivel.")
        return 2

    linhas = []
    for t in tickers:
        r_t = series.get(t)
        if r_t is None:
            continue
        etf = sector_etf(t)
        r_s = series.get(etf)
        n = min(len(r_t), len(r_mercado), len(r_s) if r_s is not None else len(r_t))
        d = decompose_move(
            r_t[-n:], r_mercado[-n:], r_s[-n:] if r_s is not None else None, window=JANELA
        )
        linhas.append((t, etf, d))
    # O exemplo trabalhado e o MAIOR movimento em que alguma componente puxou ao
    # contrario: e o caso que justifica a tecnica existir, e um movimento grande torna as
    # tres parcelas legiveis. Escolher o primeiro alfabetico daria um caso trivial.
    if not linhas:
        print("ERRO: nenhuma serie utilizavel. Nao se escreve o documento.")
        return 2

    candidatos = [r for r in linhas if r[2].opposed and not r[2].fallback]
    exemplo = max(candidatos or linhas, key=lambda r: abs(r[2].total))

    t, etf, d = exemplo
    quota = [x[2].idiosyncratic_share for x in linhas if np.isfinite(x[2].idiosyncratic_share)]
    motores = {}
    for _, _, dd in linhas:
        motores[dd.driver] = motores.get(dd.driver, 0) + 1

    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open("w", encoding="utf-8") as f:
        w = f.write
        w("# Decomposicao de um movimento: mercado, setor, empresa\n\n")
        w("> Gerado por `scripts/evaluate_decomposition.py`. Nao editar a mao.\n")
        w(f"> Mercado: `{MERCADO}` · janela de estimacao: {JANELA} dias anteriores ao dia\n")
        w(
            "> explicado · encolhimento de Vasicek com priors "
            f"mercado={PRIOR_BETA_MARKET} e setor={PRIOR_BETA_SECTOR}\n"
        )
        w(
            f"> desvio-padrao comum={PRIOR_BETA_SD} "
            f"(variancia={PRIOR_BETA_SD**2}) · minimo de {MIN_WINDOW} dias para estimar.\n\n"
        )

        w("## 1. Um caso trabalhado\n\n")
        w(f"Ticker **{t}** (setor `{etf}`), movimento do dia **{d.total:+.4%}**.\n\n")
        w("| Passo | Valor |\n|---|---|\n")
        w(f"| beta de mercado (apos encolhimento) | {d.beta_market:.4f} |\n")
        w(f"| beta de setor (apos encolhimento) | {d.beta_sector:.4f} |\n")
        w(f"| R^2 do ajuste na janela | {d.r_squared:.4f} |\n")
        w(f"| dias usados na estimacao | {d.window} |\n")
        w(f"| **componente de mercado** | **{d.market:+.4%}** |\n")
        w(f"| **componente de setor** | **{d.sector:+.4%}** |\n")
        w(f"| **componente da empresa** | **{d.idiosyncratic:+.4%}** |\n")
        soma = d.market + d.sector + d.idiosyncratic
        w(f"| soma das tres | {soma:+.4%} |\n")
        w(f"| movimento observado | {d.total:+.4%} |\n")
        w(f"| diferenca | {abs(soma - d.total):.2e} |\n\n")
        w(f"Motor identificado: **{d.driver}**. ")
        if d.opposed:
            w(f"Componentes que puxaram ao contrario: **{', '.join(d.opposed)}**.\n\n")
        else:
            w("Nenhuma componente puxou ao contrario.\n\n")
        w("A soma fecha por construcao: o alfa e o residuo do dia entram na componente da\n")
        w("empresa, que e por definicao o que mercado e setor nao explicam.\n\n")

        w("## 2. As dezassete empresas do mapa de setores, no mesmo dia\n\n")
        w("| Ticker | Setor | Total | Mercado | Setor | Empresa | Motor | beta_m |\n")
        w("|---|---|---|---|---|---|---|---|\n")
        for tk, e, dd in linhas:
            marca = " *" if dd.fallback else ""
            w(f"| {tk}{marca} | {e or '--'} | {dd.total:+.2%} | {dd.market:+.2%} | "
              f"{dd.sector:+.2%} | {dd.idiosyncratic:+.2%} | {dd.driver} | "
              f"{dd.beta_market:.2f} |\n")
        w("\n`*` = betas nao estimaveis; assumiu-se beta 1.0 no mercado.\n\n")

        w("## 3. Com que frequencia a resposta e 'nao foi a tua empresa'\n\n")
        w(f"- Tickers decompostos: **{len(linhas)}**\n")
        for k in ("market", "sector", "company"):
            n = motores.get(k, 0)
            w(f"- Motor `{k}`: **{n}** ({n / len(linhas):.1%})\n")
        if quota:
            w(f"- Quota especifica da empresa: mediana **{float(np.median(quota)):.3f}**, "
              f"minimo {min(quota):.3f}, maximo {max(quota):.3f}\n")
        r2s = [dd.r_squared for _, _, dd in linhas if np.isfinite(dd.r_squared)]
        if r2s:
            maus = sum(1 for r in r2s if r <= 0)
            w("\n### A qualidade do ajuste, dita em voz alta\n\n")
            w(f"- R^2 mediano na janela de estimacao: **{float(np.median(r2s)):.3f}**\n")
            w(f"- Tickers com R^2 <= 0: **{maus}** de {len(r2s)}\n\n")
            w("Isto importa e nao se esconde. As tres componentes somam **sempre** o movimento\n")
            w("observado, porque a componente da empresa e definida como o resto; a soma fechar\n")
            w("nao e portanto prova de que a reparticao esteja bem estimada. Um R^2 nulo ou\n")
            w("negativo diz que, naquela janela, mercado e setor nao explicam a variacao daquele\n")
            w("ticker melhor do que a media, e a reparticao desse dia deve ler-se como\n")
            w("indicativa e nao como uma atribuicao de confianca.\n")

        w("\nEste e um unico dia e nao e uma estimativa estavel: serve para mostrar que a\n")
        w("decomposicao produz respostas diferentes para empresas diferentes no mesmo dia,\n")
        w("que e a condicao minima para a pergunta valer a pena ser feita.\n")

    print(f"\nEscrito: {saida}")
    print(f"Exemplo: {t} {d.total:+.2%} = {d.market:+.2%} mercado · "
          f"{d.sector:+.2%} setor · {d.idiosyncratic:+.2%} empresa (motor: {d.driver})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
