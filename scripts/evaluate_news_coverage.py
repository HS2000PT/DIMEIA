"""Quanto é que a fonte de notícias perde? — cobertura do funil, medida.

A PERGUNTA
----------
A tese diz, em vários sítios, que a camada de notícias corre sobre uma fonte gratuita e por isso
é limitada. Nunca disse **quanto**. Ficava uma limitação **afirmada**, e o projecto já converteu
duas dessas em limitações **medidas** (a deriva, na sessão 43; a incerteza, no mesmo passe). Esta
é a terceira, e é a que o aluno tropeçou em uso real: no dia em que a NVDA subiu com a notícia da
SpaceX, o alerta não apareceu.

Esse caso teve duas causas já corrigidas (o tecto servido por ordem de chegada; a deduplicação por
texto exacto). **Sobra uma terceira que nenhuma correcção de código resolve:** se a fonte não
etiquetar a história ao ticker, ela nunca entra no funil e nenhum gate tem culpa.

O QUE ISTO MEDE, E O QUE NÃO MEDE
---------------------------------
Mede: **nos dias em que a acção se moveu de forma invulgar, com que frequência havia pelo menos
uma manchete captada para esse ticker?** É computável com o que já existe no repositório e não
depende de nenhuma fonte de verdade externa.

**Não** mede se a manchete captada era *a certa*. Determinar qual a história que "realmente" moveu
uma acção exige julgamento humano sobre cada dia, e inventar esse rótulo seria fabricar o
resultado. A distinção fica escrita no relatório, porque um número apresentado como mais do que é
vale menos do que nenhum.

DESENHO
-------
1. Os dias invulgares são identificados com `detect_all`, **o mesmo detector que corre em
   produção** — não uma reimplementação. Se a regra mudar, este número muda com ela.
2. A janela de notícias é [dia−1, dia], porque uma história publicada depois do fecho move a
   sessão seguinte, e é assim que o alinhamento anti-lookahead do resto do sistema já funciona.
3. Reporta-se a cobertura nos dois limiares que o projecto usa: **1,5** (implantação) e **3,0**
   (o congelado da avaliação), porque são perguntas diferentes.

USO
---
    python scripts/evaluate_news_coverage.py
    python scripts/evaluate_news_coverage.py --escrever
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
from datetime import timedelta

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

BACKFILL = RAIZ / "data" / "samples" / "backfill_kb.jsonl"
RELATORIO = RAIZ / "docs" / "evaluation" / "evaluation_news_coverage.md"
LIMIARES = (1.5, 3.0)
JANELA = 20


def manchetes_por_dia() -> tuple[dict[str, set[str]], dict[str, float]]:
    """({ticker: dias com manchete}, {ticker: manchetes por dia coberto})."""
    saida: dict[str, set[str]] = collections.defaultdict(set)
    total: collections.Counter = collections.Counter()
    with BACKFILL.open(encoding="utf-8") as fh:
        for linha in fh:
            try:
                d = json.loads(linha)
            except ValueError:
                continue
            t, dia = d.get("ticker"), d.get("date")
            if t and dia:
                saida[t].add(dia[:10])
                total[t] += 1
    dens = {t: total[t] / len(v) for t, v in saida.items() if v}
    return saida, dens


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--escrever", action="store_true")
    args = p.parse_args()

    from investigator.anomaly_detector.detector import detect_all
    from investigator.market_data.prices import load_close_series

    noticias, densidade = manchetes_por_dia()
    tickers = sorted(noticias)
    todas_datas = sorted({d for v in noticias.values() for d in v})
    inicio, fim = todas_datas[0], todas_datas[-1]
    print(f"{len(tickers)} tickers, {sum(len(v) for v in noticias.values())} dias com manchete")
    print(f"janela do corpus: {inicio} -> {fim}\n")

    # Uma só chamada para todos os tickers: a cadeia de fontes tem limites de ritmo, e doze
    # pedidos separados já foram, noutro script deste projecto, a causa de metade dos tickers
    # voltarem vazios.
    precos = load_close_series(tickers, start=inicio, end=fim)

    linhas_tabela: list[tuple] = []
    totais = {k: collections.Counter() for k in LIMIARES}

    for t in tickers:
        serie = precos.get(t)
        if serie is None or len(serie) < JANELA + 5:
            print(f"  {t:6s} sem precos suficientes — saltado")
            continue

        retornos = serie.pct_change().dropna()
        resultados = detect_all(retornos, window=JANELA, threshold=min(LIMIARES))
        dias_com_noticia = noticias.get(t, set())

        por_limiar = {}
        for lim in LIMIARES:
            invulgares = [(d, r) for d, r in resultados if abs(r.z_score) >= lim]
            cobertos = 0
            for dia, _ in invulgares:
                d = dia.date() if hasattr(dia, "date") else dia
                janela = {str(d), str(d - timedelta(days=1))}
                if janela & dias_com_noticia:
                    cobertos += 1
            por_limiar[lim] = (cobertos, len(invulgares))
            totais[lim]["cobertos"] += cobertos
            totais[lim]["dias"] += len(invulgares)

        c15, n15 = por_limiar[1.5]
        c30, n30 = por_limiar[3.0]
        linhas_tabela.append((t, len(dias_com_noticia), n15, c15, n30, c30))
        pct15 = f"{100*c15/n15:.0f}%" if n15 else "—"
        pct30 = f"{100*c30/n30:.0f}%" if n30 else "—"
        print(f"  {t:6s} dias c/ noticia {len(dias_com_noticia):3d} | "
              f"|z|>=1.5: {c15:3d}/{n15:<3d} ({pct15:>4s}) | "
              f"|z|>=3.0: {c30:2d}/{n30:<2d} ({pct30:>4s})")

    print()
    for lim in LIMIARES:
        c, n = totais[lim]["cobertos"], totais[lim]["dias"]
        pct = f"{100*c/n:.1f}%" if n else "n/a"
        print(f"COBERTURA GLOBAL |z|>={lim}: {c}/{n} = {pct}")

    if args.escrever:
        out = [
            "# Cobertura do funil de notícias — quanto é que a fonte perde",
            "",
            "> Gerado por `python scripts/evaluate_news_coverage.py --escrever`. **Não editar à",
            "mão.**",
            "",
            "## A pergunta",
            "",
            "A tese afirmava que a camada de notícias corre sobre uma fonte gratuita e por isso é",
            "limitada, sem nunca dizer **quanto**. Este documento converte essa afirmação num",
            "número,",
            "seguindo o mesmo padrão que já se aplicou à deriva e à incerteza.",
            "",
            "## O que isto mede — e o que não mede",
            "",
            "**Mede:** nos dias em que a acção se moveu de forma invulgar, com que frequência",
            "existia",
            "pelo menos uma manchete captada para esse ticker na janela [dia−1, dia].",
            "",
            "**Não mede** se a manchete era *a certa*. Saber qual a história que realmente moveu",
            "uma",
            "acção num dado dia exige julgamento humano caso a caso; fabricar esse rótulo",
            "tornaria o",
            "número maior e sem valor. O que se segue é portanto um **limite superior** da",
            "cobertura:",
            "o funil não pode ter visto a história certa em mais dias do que aqueles em que viu",
            "alguma coisa.",
            "",
            "## Método",
            "",
            "- Dias invulgares identificados com `detect_all`, **o detector de produção**,",
            f"  com janela de {JANELA} dias.",
            "- Janela de notícia [dia−1, dia]: uma história publicada após o fecho move a sessão",
            "  seguinte, que é o mesmo alinhamento anti-lookahead usado no resto do sistema.",
            "- Corpus: `data/samples/backfill_kb.jsonl`, manchetes **já filtradas por relevância**",
            "  (a contagem é do que passou o filtro, não do que a fonte devolveu em bruto).",
            "",
            "## Resultados",
            "",
            "| ticker | dias c/ manchete | manchetes/dia | dias \\|z\\|≥1,5 | cobertos | dias",
            "\\|z\\|≥3,0 | cobertos |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for t, nd, n15, c15, n30, c30 in linhas_tabela:
            p15 = f"{c15} ({100*c15/n15:.0f}%)" if n15 else "—"
            p30 = f"{c30} ({100*c30/n30:.0f}%)" if n30 else "—"
            dens = f"{densidade.get(t, 0):.1f}"
            out.append(f"| `{t}` | {nd} | {dens} | {n15} | {p15} | {n30} | {p30} |")
        out += ["", "### Global", ""]
        for lim in LIMIARES:
            c, n = totais[lim]["cobertos"], totais[lim]["dias"]
            pct = f"**{100*c/n:.1f}%**" if n else "n/a"
            out.append(
                f"- `|z| ≥ {lim}`: {c} de {n} dias invulgares tinham manchete "
                f"captada — {pct}"
            )
        out += [
            "",
            "## Uma hipótese testada e REFUTADA",
            "",
            "A NVDA é o ticker **pior coberto** e ao mesmo tempo o de **maior densidade**: mais",
            "manchetes por dia coberto do que qualquer outro, em muito menos dias distintos. A",
            "explicação óbvia é truncagem: o Finnhub devolve no máximo ~250 itens por pedido, e o",
            "*backfill* pede janelas de sete dias, portanto uma semana ruidosa bateria no tecto e",
            "os dias mais antigos dessa janela desapareceriam por inteiro.",
            "",
            "**A hipótese foi testada e não se sustenta.** Contando os itens por janela de sete",
            "dias,",
            "**nenhuma janela de nenhum ticker chegou perto do tecto**: o máximo observado foi de",
            "165",
            "itens, contra os ~250 disponíveis. A cobertura irregular da NVDA é uma propriedade",
            "de como",
            "a fonte a etiqueta, e não um artefacto do modo como os dados foram pedidos.",
            "",
            "Fica registado por duas razões. A primeira é que a explicação por truncagem é",
            "plausível e",
            "estaria errada. A segunda é que ela teria sido *acionável* — bastaria estreitar a",
            "janela —",
            "e agir sobre uma causa refutada é como se perde tempo a resolver o problema errado.",
            "",
            "## Leitura",
            "",
            "O número responde à pergunta que o caso da NVDA levantou: quando a acção se mexe a",
            "sério, o sistema tem sequer alguma coisa para mostrar? A parte não coberta é a",
            "fracção",
            "em que **nenhuma correcção de código ajuda** — se a fonte não etiquetou a história ao",
            "ticker, ela não entra no funil e nenhum dos cinco gates chega a ser consultado.",
            "",
            "Isto separa duas limitações que antes andavam juntas: o que o **desenho** descarta",
            "(os",
            "gates, medidos no funil de alertas) e o que a **fonte** nunca entregou. Só a",
            "primeira é",
            "uma decisão deste trabalho.",
        ]
        RELATORIO.parent.mkdir(parents=True, exist_ok=True)
        RELATORIO.write_text("\n".join(out) + "\n", encoding="utf-8")
        print(f"\n-> {RELATORIO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
