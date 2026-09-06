"""Como e que o modelo ordena a populacao REAL de candidatas?

O instrumento que o `PROTOCOLO_ACEITACAO_RETREINO.md` exige, construido ANTES de existir
resultado. A pos-validacao publicada mede 239 pares empresa-dia que ja tinham atravessado as
portas; a decisao R1 passou a registar toda a candidata relevante, e esta e a primeira vez que
a pergunta se pode fazer sobre a populacao que o modelo teria mesmo de triar.

QUATRO REGRAS QUE ESTE SCRIPT IMPOE, e todas foram fixadas antes de haver dados:

1. TREINABILIDADE. So entram linhas cujo `as_of` seja ANTERIOR OU IGUAL a data da noticia. Uma
   barra posterior descreve um mercado que ja viu o desfecho que o rotulo mede em (d, d+3].
   Medido a 2026-09-04: as candidatas velhas tinham as_of de +1 a +107 dias.

2. DEDUPLICACAO. Uma linha por (news_date, ticker, headline). O varrimento repontuava o mesmo
   titulo a cada ciclo, e sem isto o peso de cada empresa seria a frequencia com que o sistema
   a republica.

3. AGRUPAMENTO. A unidade e o par (ticker, dia), porque o rotulo e o retorno anormal desse par:
   todas as manchetes da mesma empresa no mesmo dia partilham o desfecho por construcao. O
   bootstrap reamostra CLUSTERS, nao linhas. A sessao 55 pagou esta licao uma vez.

4. RECUSA ABAIXO DO MINIMO. Com menos de 80 clusters maturados o script NAO reporta metrica de
   comparacao: escreve "bloco insuficiente" e sai. E o mesmo mecanismo do
   `analyse_usefulness.py`, e existe para que ninguem cite um numero cedo demais.

O QUE ESTE SCRIPT NAO FAZ: nao treina, nao escreve em `models/`, e nao compara candidato nenhum.
Mede a ordenacao do modelo IMPLANTADO contra o acaso e contra a volatilidade isolada, que e a
linha de base que ganha na dissertacao.

USO: python scripts/evaluate_ranking_producao.py [--min-clusters N]
SAI: docs/evaluation/evaluation_ranking_producao.md
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import pathlib
import subprocess
import sys

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_ranking_producao.md"
MIN_CLUSTERS = 80
REPETICOES = 4000
NL = chr(10)


def le_registo() -> list[dict]:
    """Le o registo de decisoes da branch de dados, ou de um ficheiro local."""
    local = RAIZ / "data" / "predictions_log.jsonl"
    if local.exists():
        bruto = local.read_text(encoding="utf-8", errors="replace")
    else:
        r = subprocess.run(["git", "show", "origin/alerts-history:predictions_log.jsonl"],
                           capture_output=True, cwd=RAIZ)
        bruto = r.stdout.decode("utf-8", "replace")
    out = []
    for linha in bruto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        try:
            out.append(json.loads(linha))
        except ValueError:
            continue
    return out


def utilizaveis(recs: list[dict]) -> list[dict]:
    """Regra 1 e 2: classe A com as_of nao posterior a noticia, uma linha por titulo."""
    vistos = set()
    out = []
    for d in recs:
        fs = d.get("feature_snapshot") or {}
        vals = fs.get("values") or {}
        if not vals or d.get("prob") is None:
            continue
        ao = (fs.get("as_of") or "")[:10]
        nd = (d.get("news_date") or "")[:10]
        if not ao or not nd or ao > nd:
            continue
        chave = (nd, d.get("ticker"), d.get("headline"))
        if chave in vistos:
            continue
        vistos.add(chave)
        out.append(d)
    return out


def auc(y: np.ndarray, s: np.ndarray) -> float:
    """Area sob a curva ROC, por contagem de pares concordantes."""
    o = np.argsort(s, kind="stable")
    y = y[o]
    pos = int(y.sum())
    neg = len(y) - pos
    if pos == 0 or neg == 0:
        return float("nan")
    r = np.arange(1, len(y) + 1)
    return float((r[y == 1].sum() - pos * (pos + 1) / 2) / (pos * neg))


def pr_auc(y: np.ndarray, s: np.ndarray) -> float:
    """Precisao media, que e a leitura da area sob a curva de precisao-cobertura."""
    o = np.argsort(-s, kind="stable")
    y = y[o]
    pos = int(y.sum())
    if pos == 0:
        return float("nan")
    tp = np.cumsum(y)
    prec = tp / np.arange(1, len(y) + 1)
    return float((prec * y).sum() / pos)


def rotula(linhas: list[dict]) -> list[dict]:
    """Aplica o rotulo real com precos, na mesma convencao do treino. Fail-open por empresa."""
    from investigator.market_data.prices import load_close_series
    from investigator.triage.postval import label_decision

    tickers = sorted({d["ticker"] for d in linhas})
    datas = sorted((d["news_date"] or "")[:10] for d in linhas)
    ini = (datetime.date.fromisoformat(datas[0]) - datetime.timedelta(days=10)).isoformat()
    fim = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
    series = load_close_series([*tickers, "SPY"], ini, fim)
    mercado = series.get("SPY")
    out = []
    for d in linhas:
        alvo = series.get(d["ticker"])
        if alvo is None or mercado is None:
            continue
        try:
            y = label_decision(d, alvo, mercado)
        except Exception:  # noqa: BLE001 -- uma empresa sem precos nao pode parar a medicao
            y = None
        if y is None:
            continue
        e = dict(d)
        e["label"] = int(y)
        out.append(e)
    return out


def bootstrap(clusters: dict, chaves: list, metrica, coluna: str, rng) -> tuple:
    """Reamostra CLUSTERS e devolve (valor, lo, hi). A unidade e o par empresa-dia."""
    def calcula(sel):
        y, s = [], []
        for k in sel:
            for e in clusters[k]:
                y.append(e["label"])
                s.append(e[coluna])
        return metrica(np.array(y), np.array(s))

    obs = calcula(chaves)
    b = []
    for _ in range(REPETICOES):
        sel = list(rng.choice(len(chaves), len(chaves), replace=True))
        v = calcula([chaves[i] for i in sel])
        if v == v:
            b.append(v)
    if not b:
        return obs, float("nan"), float("nan")
    return obs, float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def projecao(por_dia: dict, minimo: int, prazo: str) -> tuple:
    """Ao ritmo observado, o minimo e alcancavel ate ao prazo?

    Existe para que a recusa nao seja um beco: correr o script em qualquer dia diz `ainda
    nao` E se a recolha esta no caminho certo. Um minimo que so' se descobre inalcancavel
    na vespera nao serve de minimo.
    """
    if not por_dia:
        return 0, 0, 0.0, False
    import statistics
    ritmo = statistics.median(sorted(len(v) for v in por_dia.values()))
    hoje = datetime.date.today()
    fim = datetime.date.fromisoformat(prazo)
    uteis = sum(1 for i in range((fim - hoje).days + 1)
                if (hoje + datetime.timedelta(days=i)).weekday() < 5)
    tem = sum(len(v) for v in por_dia.values())
    previsto = tem + uteis * ritmo
    return tem, uteis, ritmo, previsto >= minimo


def escreve_insuficiente(n_cl: int, minimo: int, n_linhas: int, n_brutas: int,
                         por_dia: dict | None = None,
                         prazo: str = "2026-09-17") -> None:
    gerado = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
    with SAIDA.open("w", encoding="utf-8") as f:
        w = f.write
        w("# Ordenação sobre a população real de candidatas" + NL * 2)
        w("> **Gerado por** `scripts/evaluate_ranking_producao.py`. Não editar à mão." + NL)
        w("> **Gerado a:** " + gerado + NL * 2)
        w("## Bloco insuficiente" + NL * 2)
        w("O protocolo exige **" + str(minimo) + " pares empresa-dia com rótulo maturado** "
          "antes de reportar qualquer métrica de comparação, e existem **" + str(n_cl)
          + "**. Nenhum valor é publicado." + NL * 2)
        w("O mínimo foi fixado antes de haver dados. Reportar abaixo dele produziria um número "
          "que alguém citaria, e o intervalo que o acompanha seria largo ao ponto de não "
          "distinguir o modelo do acaso." + NL * 2)
        w("| | |" + NL + "|---|---:|" + NL)
        w("| Linhas no registo | " + str(n_brutas) + " |" + NL)
        w("| Utilizáveis (classe A, `as_of` não posterior à notícia, sem repetição) | "
          + str(n_linhas) + " |" + NL)
        w("| Pares empresa-dia com rótulo maturado | " + str(n_cl) + " |" + NL)
        w("| Mínimo exigido | " + str(minimo) + " |" + NL)
        tem, uteis, ritmo, ok = projecao(por_dia or {}, minimo, prazo)
        if uteis:
            w(NL + "## A recolha chega ao mínimo a tempo?" + NL * 2)
            veredicto = ("A recolha está no caminho certo." if ok else
                         "**A recolha não chega ao mínimo a tempo.** A decisão do que "
                         "fazer com isso é do autor.")
            w("Ao ritmo observado de **" + format(ritmo, ".0f") + " pares por dia de "
              "bolsa**, e com **" + str(uteis) + " dias de bolsa** até " + prazo
              + ", a projeção é de **" + format(tem + uteis * ritmo, ".0f")
              + " pares**, contra um mínimo de " + str(minimo) + ". " + veredicto + NL * 2)
            # ⚠️ O PRAZO E A DATA DA ULTIMA NOTICIA, NAO A DATA DE CORRER ISTO. Sem esta
            # ressalva o número acima le-se como «a 17/09 tens 120 pares», e nao tens: o
            # rotulo mede (d, d+3] dias de bolsa, pelo que os pares dos ultimos tres dias
            # ainda nao maturaram. Correr o script no proprio prazo devolveria uma recusa
            # que se le como avaria da recolha — o beco que este script existe para nao ter.
            w("⚠️ **" + prazo + " é a última data de NOTÍCIA rotulável, não a data de "
              "correr esta avaliação.** O rótulo mede a janela `(d, d+3]` em dias de bolsa, "
              "pelo que os pares dos últimos três dias de recolha ainda não maturaram nesse "
              "dia. O protocolo fixa o congelamento dos resultados em **~2026-09-22**, que é "
              "quando a projeção acima existe de facto. Correr isto a " + prazo
              + " devolve uma recusa que **não** significa que a recolha falhou." + NL * 2)
            # ⚠️ `tem` conta pares RECOLHIDOS, nao maturados: o `por_dia` e construido
            # sobre as linhas utilizaveis, antes de rotular. Chamar-lhes maturados poria
            # o relatorio a contradizer a sua propria tabela tres linhas acima.
            w("Hoje há **" + str(tem) + "** pares recolhidos, dos quais **" + str(n_cl)
              + "** já maturaram. A projeção supõe que o ritmo se mantém e que o "
              "sistema continua no ar, e não é uma garantia." + NL)
    print("bloco insuficiente: " + str(n_cl) + " clusters maturados, minimo " + str(minimo))


def escreve(res: dict, gerado: str) -> None:
    with SAIDA.open("w", encoding="utf-8") as f:
        w = f.write
        w("# Ordenação sobre a população real de candidatas" + NL * 2)
        w("> **Gerado por** `scripts/evaluate_ranking_producao.py`. Não editar à mão." + NL)
        w("> **Gerado a:** " + gerado + NL * 2)
        w("A pós-validação publicada mede pares que já tinham atravessado as portas. Esta "
          "medição incide sobre a população que o modelo teria de triar, incluindo as "
          "candidatas que as portas elementares removem antes de ele ser invocado." + NL * 2)
        w("| | |" + NL + "|---|---:|" + NL)
        w("| Pares empresa-dia | " + str(res["n_clusters"]) + " |" + NL)
        w("| Decisões utilizáveis | " + str(res["n"]) + " |" + NL)
        w("| Empresas | " + str(res["empresas"]) + " |" + NL)
        w("| Prevalência do rótulo | " + format(res["prevalencia"], ".3f") + " |" + NL * 2)
        w("| Ordenação | ROC-AUC | IC 95% | PR-AUC | IC 95% |" + NL)
        w("|---|---:|---|---:|---|" + NL)
        for nome, r in res["series"]:
            w("| " + nome + " | " + format(r["roc"], ".3f") + " | ["
              + format(r["roc_lo"], ".3f") + ", " + format(r["roc_hi"], ".3f") + "] | "
              + format(r["pr"], ".3f") + " | [" + format(r["pr_lo"], ".3f") + ", "
              + format(r["pr_hi"], ".3f") + "] |" + NL)
        w(NL + "O acaso vale `0.500` na ROC-AUC e a prevalência na PR-AUC. O bootstrap "
          "reamostra pares empresa-dia, e não decisões: todas as manchetes da mesma empresa "
          "no mesmo dia partilham o rótulo por construção." + NL * 2)
        w("## O que esta medição não estabelece" + NL * 2)
        w("Não compara candidato nenhum, uma vez que nenhum foi treinado. Mede a ordenação do "
          "modelo implantado sobre a população real, contra o acaso e contra a volatilidade "
          "isolada, que é a linha de base que vence na dissertação." + NL)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-clusters", type=int, default=MIN_CLUSTERS,
                    help="minimo de pares empresa-dia maturados (o protocolo fixa 80)")
    args = ap.parse_args()

    brutas = le_registo()
    linhas = utilizaveis(brutas)
    if not linhas:
        escreve_insuficiente(0, args.min_clusters, 0, len(brutas))
        return 0
    rotuladas = rotula(linhas)
    clusters: dict = collections.defaultdict(list)
    for d in rotuladas:
        vals = d["feature_snapshot"]["values"]
        d["vol"] = float(vals.get("vol20", float("nan")))
        if d["vol"] != d["vol"]:
            continue
        clusters[(d["ticker"], d["news_date"][:10])].append(d)
    chaves = sorted(clusters)
    if len(chaves) < args.min_clusters:
        pd_ = collections.defaultdict(set)
        for d_ in linhas:
            pd_[d_["news_date"][:10]].add(d_["ticker"])
        escreve_insuficiente(len(chaves), args.min_clusters, len(linhas), len(brutas),
                             por_dia=pd_)
        return 0

    rng = np.random.default_rng(20260904)
    todas = [e for k in chaves for e in clusters[k]]
    prevalencia = float(np.mean([e["label"] for e in todas]))
    series = []
    for nome, coluna in (("modelo implantado", "prob"), ("volatilidade isolada", "vol")):
        roc, rlo, rhi = bootstrap(clusters, chaves, auc, coluna, rng)
        pr, plo, phi = bootstrap(clusters, chaves, pr_auc, coluna, rng)
        series.append((nome, {"roc": roc, "roc_lo": rlo, "roc_hi": rhi,
                              "pr": pr, "pr_lo": plo, "pr_hi": phi}))
    gerado = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
    escreve({"n_clusters": len(chaves), "n": len(todas), "prevalencia": prevalencia,
             "empresas": len({t for t, _ in chaves}), "series": series}, gerado)
    print("-> " + str(SAIDA.relative_to(RAIZ)))
    for nome, r in series:
        print("   " + nome + ": ROC " + format(r["roc"], ".3f")
              + " [" + format(r["roc_lo"], ".3f") + ", " + format(r["roc_hi"], ".3f") + "]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
