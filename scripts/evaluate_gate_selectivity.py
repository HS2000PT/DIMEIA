"""O portão de triagem está a escolher NOTÍCIAS ou EMPRESAS?

Motivação: o utilizador do sistema reportou três queixas ao mesmo tempo — recebe alertas a
mais, quase sempre das mesmas empresas, e nunca recebe nada sobre outras. As três têm a mesma
causa, e ela mede-se.

O portão implantado é um **limiar fixo** sobre a probabilidade calibrada da triagem
(`news.min_materiality`, hoje 0.50). Este script pergunta se esse limiar separa manchetes ou
se separa tickers, usando as decisões **realmente registadas em produção**.

A pergunta é a mesma que o Capítulo da avaliação já faz para os preços: um limiar fixo sobre
o retorno mede a volatilidade da empresa e não a raridade do dia. Aqui aplica-se um nível
acima, ao score do modelo.

USO:  python scripts/evaluate_gate_selectivity.py
SAI:  docs/evaluation/evaluation_gate_selectivity.md
"""

from __future__ import annotations

import collections
import json
import pathlib
import statistics
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_gate_selectivity.md"
BRANCH = "origin/alerts-history"
PISO = 0.50
MIN_POR_TICKER = 20


def decisoes() -> list[dict]:
    r = subprocess.run(["git", "show", f"{BRANCH}:predictions_log.jsonl"],
                       capture_output=True, cwd=RAIZ)
    if r.returncode:
        print(f"ERRO: não consegui ler {BRANCH}:predictions_log.jsonl. Correr `git fetch`.",
              file=sys.stderr)
        raise SystemExit(2)
    linhas = r.stdout.decode("utf-8", "replace").strip().splitlines()
    todas = [json.loads(x) for x in linhas if x.strip()]
    return [p for p in todas if p.get("prob") is not None]


def main() -> None:
    pred = decisoes()
    if len(pred) < 200:
        print(f"ERRO: só {len(pred)} decisões pontuadas. Não escrevo um relatório sobre isto.",
              file=sys.stderr)
        raise SystemExit(2)

    por_t: dict[str, list[float]] = collections.defaultdict(list)
    for p in pred:
        por_t[p["ticker"]].append(p["prob"])

    datas = sorted(str(p.get("ts", ""))[:10] for p in pred if p.get("ts"))

    # ── dispersão dentro vs entre ────────────────────────────────────────────
    amplitudes = {t: max(ps) - min(ps) for t, ps in por_t.items()}
    medianas = {t: statistics.median(ps) for t, ps in por_t.items()}
    dentro = statistics.mean(amplitudes.values())
    entre = max(medianas.values()) - min(medianas.values())

    # ── o piso chega a decidir? ──────────────────────────────────────────────
    sempre_sim = sorted(t for t, ps in por_t.items() if min(ps) >= PISO)
    sempre_nao = sorted(t for t, ps in por_t.items() if max(ps) < PISO)
    mistos = sorted(t for t in por_t if t not in sempre_sim and t not in sempre_nao)
    n_mistos = sum(len(por_t[t]) for t in mistos)
    pc_determinado = 100.0 * (len(pred) - n_mistos) / len(pred)

    def veredicto(t: str) -> str:
        if t in sempre_sim:
            return "sempre passa"
        return "nunca passa" if t in sempre_nao else "o piso decide"

    tab = "\n".join(
        f"| {t} | {len(ps)} | {min(ps):.3f} | {statistics.median(ps):.3f} | {max(ps):.3f} | "
        f"{amplitudes[t]:.3f} | {veredicto(t)} |"
        for t, ps in sorted(por_t.items(), key=lambda kv: -len(kv[1]))
    )

    # ── e se o piso fosse relativo a cada empresa? ───────────────────────────
    linhas_rel = []
    for q in (0.05, 0.10, 0.20):
        lim = {t: statistics.quantiles(ps, n=100)[int((1 - q) * 100) - 1]
               for t, ps in por_t.items() if len(ps) >= MIN_POR_TICKER}
        passa = [p for p in pred if p["prob"] >= lim.get(p["ticker"], 9.0)]
        c = collections.Counter(p["ticker"] for p in passa)
        pior = c.most_common(1)[0] if c else ("-", 0)
        linhas_rel.append(
            f"| top {q:.0%} de cada empresa | {len(passa)} ({100*len(passa)/len(pred):.0f}%) | "
            f"{len(c)}/{len(por_t)} | {pior[0]} com {pior[1]} |")
    rel = "\n".join(linhas_rel)

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(f"""# O portão de triagem separa notícias ou empresas?

> **Gerado por** `scripts/evaluate_gate_selectivity.py`. Não editar à mão.
> **Fonte:** `{BRANCH}:predictions_log.jsonl` — as decisões **realmente tomadas em produção**.
> **Decisões pontuadas:** {len(pred)} · **período:** {datas[0]} a {datas[-1]} ·
> **piso implantado:** {PISO}

## 1. A distribuição do score, empresa a empresa

| Ticker | Decisões | Mín | Mediana | Máx | Amplitude | O piso {PISO} |
|---|---|---|---|---|---|---|
{tab}

- **Amplitude média DENTRO de cada empresa:** `{dentro:.3f}`
- **Amplitude ENTRE as medianas das empresas:** `{entre:.3f}`
- **Razão entre/dentro: {entre/dentro:.1f}×**

## 2. O resultado

- Empresas que passam **sempre**: {len(sempre_sim)} — {', '.join(sempre_sim) or '(nenhuma)'}
- Empresas que **nunca** passam: {len(sempre_nao)} — {', '.join(sempre_nao) or '(nenhuma)'}
- Empresas em que o piso **chega a decidir**: {len(mistos)} — {', '.join(mistos) or '(nenhuma)'}

> **Em {pc_determinado:.0f}% das decisões o resultado estava determinado pela EMPRESA antes de
> se ler a manchete.**

Isto explica, de uma só vez, as três queixas do utilizador: recebe demasiados alertas (as
empresas que passam sempre saturam o tecto diário), recebe-os sempre das mesmas, e nunca recebe
nada sobre as restantes, aconteça o que acontecer.

É o mesmo defeito que a dissertação já identifica nos preços — um limiar fixo mede a
volatilidade da empresa e não a raridade do dia — mas um nível acima, sobre o score do modelo.

## 3. E se o piso fosse relativo a cada empresa?

A correcção aparentemente óbvia é tornar o piso relativo, tal como o *z*-score fez para os
preços. Simulada sobre as mesmas decisões:

| Regime | Passariam | Empresas representadas | Concentração |
|---|---|---|---|
| piso fixo em {PISO} (actual) | {sum(1 for p in pred if p['prob'] >= PISO)} \
({100*sum(1 for p in pred if p['prob'] >= PISO)/len(pred):.0f}%) | \
{len(sempre_sim) + len(mistos)}/{len(por_t)} | \
{collections.Counter(p['ticker'] for p in pred if p['prob'] >= PISO).most_common(1)[0][0]} com \
{collections.Counter(p['ticker'] for p in pred if p['prob'] >= PISO).most_common(1)[0][1]} |
{rel}

**Resolve metade e cria outro problema.** Todas as empresas passam a estar representadas, o que
é o efeito pretendido. Mas nas empresas cujo score é quase constante — as de amplitude mais
baixa nesta tabela — o percentil cai **em cima** da constante e quase todas as decisões empatam
acima dele. O regime relativo passa a seleccionar por desempate, que é exactamente o artefacto
que a dissertação documenta noutro sítio.

## 4. Leitura honesta

A conclusão não é que falta afinar o piso. É mais funda, e é coerente com o resultado negativo
já reportado para a questão da triagem:

> **Dentro de uma empresa, o score do modelo quase não varia com a manchete.**
> A amplitude média dentro de cada empresa é `{dentro:.3f}`, contra `{entre:.3f}` entre empresas.
> Nenhuma regra de decisão aplicada a este score o pode tornar sensível à notícia, porque a
> informação que distinguiria uma manchete da seguinte não está lá.

O que isto implica para o produto é que **o score da triagem não deve ser o critério principal
de alerta**. Serve para ordenar entre empresas, que é para o que tem informação, e para ser
mostrado com a ressalva que já tem. O critério que decide *se* se interrompe alguém precisa de
assentar em quantidades que variem com o acontecimento: o movimento do próprio dia, a força da
evidência recuperada, e a novidade da história.
""", encoding="utf-8")

    print(f"decisões        : {len(pred)}  ({datas[0]} a {datas[-1]})")
    print(f"dentro / entre  : {dentro:.3f} / {entre:.3f}  ({entre/dentro:.1f}x)")
    print(f"sempre passa    : {sempre_sim}")
    print(f"nunca passa     : {sempre_nao}")
    print(f"determinado pela empresa: {pc_determinado:.0f}% das decisões")
    print(f"-> {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
