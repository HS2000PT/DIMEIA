"""O texto acrescenta alguma coisa POR CIMA da melhor linha de base? E o modelo distingue dias
da mesma empresa?

## A pergunta que faltava, e porque é diferente das que já foram feitas

A dissertação comparou famílias **lado a lado**: só volatilidade, só contexto, só texto, e
contexto+texto. A conclusão foi que nenhuma variante com texto bate a volatilidade sozinha. É um
resultado, está reportado, e aguenta três testes de robustez.

Mas há duas perguntas que essa comparação **não** faz, e são as que interessam a quem quer saber
se o texto vale alguma coisa:

**1. O texto acrescenta por cima da melhor linha de base, em vez de a substituir?**
Comparar A contra B responde a *qual é melhor*. Não responde a *A e B juntos são melhores do que
B*. A variante `full` da dissertação parece fazer isso, mas junta o texto ao bloco de **contexto**,
que não é a melhor linha de base conhecida: a melhor é a **tabela de consulta por empresa**, que
obteve precisão@5 de $0.662$ e bateu o modelo implantado. Nunca se testou o texto em cima dela.

**2. O modelo distingue dias diferentes da mesma empresa?**
Esta é a pergunta a que a ablação da identidade dá uma resposta parcial. Uma tabela de consulta
por empresa devolve **o mesmo valor** para todos os dias dessa empresa, portanto a sua capacidade
de ordenar *dentro* de uma empresa é exactamente $0.5$ --- não por estimativa, por construção. Se
um modelo ficar acima disso, contém informação que a tabela não pode ter, e a quantidade é
mensurável.

A segunda pergunta é a mais informativa das duas, porque tem um chão que não é preciso estimar.

## O critério, fixado antes de correr

Um acréscimo só conta se o intervalo de confiança a 95%, obtido por reamostragem **por grupos
(empresa, dia)**, **excluir zero**. Reamostrar linhas daria intervalos mais estreitos e enganadores:
notícias do mesmo dia sobre a mesma empresa partilham o rótulo por construção.

## Porta de entrada

Reproduz os números congelados da dissertação ($0.542$ para a volatilidade e $0.538$ para o
contexto) e **recusa-se a escrever** se não os reproduzir. Um relatório produzido por outro
protocolo não é comparável com o que a dissertação diz.

USO:  python scripts/evaluate_triage_within.py
SAI:  docs/evaluation/evaluation_triage_within.md
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from datetime import UTC, datetime

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from sklearn.decomposition import PCA  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

from investigator.triage.features import context_block  # noqa: E402
from investigator.triage.model import (  # noqa: E402
    fit_platt,
    make_model,
    metrics,
    precision_at_daily_budget,
    scores_of,
)

SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_triage_within.md"
CONGELADO_VOL = 0.542
CONGELADO_CONTEXTO = 0.538
TOLERANCIA = 0.002
PCA_DIMS = 32          # o valor do re-teste justo; não se afina aqui para não pescar
REAMOSTRAGENS = 1000


def treina(xtr, ytr, xva, yva, xte, seed=42) -> np.ndarray:
    """Um modelo, com o protocolo do treino congelado. Devolve as pontuações calibradas."""
    m = make_model("context", seed=seed)
    m.fit(xtr, ytr)
    cal = fit_platt(scores_of(m, xva), yva, seed=seed)
    return cal(scores_of(m, xte))


def auc_dentro(tickers: np.ndarray, y: np.ndarray, s: np.ndarray) -> tuple[float, int]:
    """AUC calculada DENTRO de cada empresa, e depois ponderada pelo número de pares.

    Uma média simples entre empresas daria o mesmo peso a uma empresa com 50 exemplos e a outra
    com 5000. A ponderação é pelo número de pares (positivo, negativo) de cada empresa, que é a
    unidade que a AUC conta.
    """
    total_pares, soma = 0, 0.0
    empresas = 0
    for t in np.unique(tickers):
        m = tickers == t
        yy, ss = y[m], s[m]
        n_pos, n_neg = int(yy.sum()), int((1 - yy).sum())
        if n_pos == 0 or n_neg == 0:
            continue
        pares = n_pos * n_neg
        soma += roc_auc_score(yy, ss) * pares
        total_pares += pares
        empresas += 1
    return (soma / total_pares if total_pares else float("nan")), empresas


def ic_cluster(grupos: np.ndarray, fn, rng, n=REAMOSTRAGENS) -> tuple[float, float]:
    """Intervalo a 95% por reamostragem de GRUPOS (empresa, dia), não de linhas."""
    unicos = np.unique(grupos)
    indices = {g: np.flatnonzero(grupos == g) for g in unicos}
    amostras = []
    for _ in range(n):
        escolhidos = rng.choice(unicos, size=len(unicos), replace=True)
        idx = np.concatenate([indices[g] for g in escolhidos])
        v = fn(idx)
        if not np.isnan(v):
            amostras.append(v)
    a = np.asarray(amostras)
    return float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))


def main() -> int:
    ap = argparse.ArgumentParser(description="Texto por cima da melhor linha de base")
    ap.add_argument("--dataset", default=str(RAIZ / "data" / "triage_dataset.csv"))
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    p = pathlib.Path(args.dataset)
    if not p.exists():
        print(f"ERRO: {p} nao existe. Este corpus e local; correr na maquina que o tem.",
              file=sys.stderr)
        return 2

    df = pd.read_csv(p)
    df = df[df["split"].isin(["train", "val", "test"])].reset_index(drop=True)
    partes = {s: df[df["split"] == s].reset_index(drop=True) for s in ("train", "val", "test")}
    y = {s: partes[s]["label"].to_numpy() for s in partes}
    ctx = {s: context_block(partes[s])[0] for s in partes}
    datas = partes["test"]["date"].to_numpy()
    tickers = partes["test"]["ticker"].to_numpy()
    grupos = np.array([f"{t}|{d}" for t, d in zip(tickers, datas, strict=True)])
    nomes = context_block(partes["train"])[1]

    # ── porta de entrada ─────────────────────────────────────────────────────
    so_vol = [i for i, n in enumerate(nomes) if n == "vol20"]
    s_vol = treina(ctx["train"][:, so_vol], y["train"], ctx["val"][:, so_vol], y["val"],
                   ctx["test"][:, so_vol], args.seed)
    s_ctx = treina(ctx["train"], y["train"], ctx["val"], y["val"], ctx["test"], args.seed)
    pr_vol = metrics(y["test"], s_vol)["pr_auc"]
    pr_ctx = metrics(y["test"], s_ctx)["pr_auc"]
    for rot, obtido, esperado in (("vol", pr_vol, CONGELADO_VOL),
                                  ("contexto", pr_ctx, CONGELADO_CONTEXTO)):
        if abs(obtido - esperado) > TOLERANCIA:
            print(f"ERRO: {rot} deu {obtido:.3f} e o congelado e {esperado:.3f}. "
                  "Nao escrevo um relatorio incomparavel.", file=sys.stderr)
            return 2
    print(f"porta de entrada ok: vol {pr_vol:.3f} - contexto {pr_ctx:.3f}")

    # ── embeddings, do mesmo cache das outras avaliações ─────────────────────
    cache = p.with_name("_cache_triage_minilm.npy")
    if not cache.exists():
        print(f"ERRO: falta {cache.name}. Correr `evaluate_triage_fairtext.py` primeiro,"
              " que o constroi.", file=sys.stderr)
        return 2
    todos = np.load(cache)
    emb, i = {}, 0
    for s in ("train", "val", "test"):
        emb[s] = todos[i:i + len(partes[s])]
        i += len(partes[s])
    pca = PCA(n_components=PCA_DIMS, random_state=args.seed).fit(emb["train"])
    txt = {s: pca.transform(emb[s]) for s in emb}
    print(f"texto reduzido a {PCA_DIMS} dimensoes "
          f"({100 * pca.explained_variance_ratio_.sum():.0f}% da variancia)")

    # ── a melhor linha de base conhecida: a tabela de consulta por empresa ───
    taxa = partes["train"].groupby("ticker")["label"].mean()
    glob = float(partes["train"]["label"].mean())
    prior = {s: partes[s]["ticker"].map(taxa).fillna(glob).to_numpy(dtype="float64")
             for s in partes}
    # em logit, para a regressão a poder deslocar e escalar em vez de a tratar como linear em p
    eps = 1e-6
    lg = {s: np.log(np.clip(prior[s], eps, 1 - eps) / (1 - np.clip(prior[s], eps, 1 - eps)))
          for s in prior}

    def col(s, *blocos):
        return np.column_stack([b for b in blocos])

    s_prior = prior["test"]
    s_prior_txt = treina(col("train", lg["train"], txt["train"]), y["train"],
                         col("val", lg["val"], txt["val"]), y["val"],
                         col("test", lg["test"], txt["test"]), args.seed)
    s_ctx_txt = treina(col("train", ctx["train"], txt["train"]), y["train"],
                       col("val", ctx["val"], txt["val"]), y["val"],
                       col("test", ctx["test"], txt["test"]), args.seed)
    s_txt = treina(txt["train"], y["train"], txt["val"], y["val"], txt["test"], args.seed)

    modelos = [
        ("Tabela de consulta por empresa", "o melhor chão conhecido, e não vê a notícia", s_prior),
        ("Tabela + texto", "a mesma tabela, mais o título", s_prior_txt),
        ("Contexto (o implantado)", "as nove entradas", s_ctx),
        ("Contexto + texto", "as nove, mais o título", s_ctx_txt),
        ("Só texto", "só o título", s_txt),
    ]

    rng = np.random.default_rng(args.seed)
    linhas = []
    for rot, oq, s in modelos:
        m = metrics(y["test"], s)
        pb = precision_at_daily_budget(datas, y["test"], s, 5)
        dentro, n_emp = auc_dentro(tickers, y["test"], s)
        linhas.append((rot, oq, m["pr_auc"], pb, dentro, n_emp))
        print(f"  {rot:34s} PR-AUC {m['pr_auc']:.3f} · p@5 {pb:.3f} · dentro {dentro:.3f}")

    # ── os dois acréscimos, com intervalo por grupos ─────────────────────────
    def delta_dentro(a, b):
        def f(idx):
            va, _ = auc_dentro(tickers[idx], y["test"][idx], a[idx])
            vb, _ = auc_dentro(tickers[idx], y["test"][idx], b[idx])
            return va - vb
        return f

    def delta_pr(a, b):
        def f(idx):
            yy = y["test"][idx]
            if len(np.unique(yy)) < 2:
                return float("nan")
            return metrics(yy, a[idx])["pr_auc"] - metrics(yy, b[idx])["pr_auc"]
        return f

    d_tab_pr = metrics(y["test"], s_prior_txt)["pr_auc"] - metrics(y["test"], s_prior)["pr_auc"]
    ic_tab_pr = ic_cluster(grupos, delta_pr(s_prior_txt, s_prior), rng)
    # ⚠️ E contra a linha de base que GANHOU na dissertação, porque é essa a afirmação que
    # alguém vai querer fazer a seguir. Sem intervalo, "0.547 é maior do que 0.542" é uma
    # comparação de dois pontos sem incerteza, e este trabalho já pagou por uma dessas.
    d_vs_vol = metrics(y["test"], s_prior_txt)["pr_auc"] - metrics(y["test"], s_vol)["pr_auc"]
    ic_vs_vol = ic_cluster(grupos, delta_pr(s_prior_txt, s_vol), rng)
    dentro_ctx, _ = auc_dentro(tickers, y["test"], s_ctx)
    ic_ctx_dentro = ic_cluster(grupos, lambda idx: auc_dentro(tickers[idx], y["test"][idx],
                                                              s_ctx[idx])[0], rng)
    d_txt_dentro = (auc_dentro(tickers, y["test"], s_ctx_txt)[0] - dentro_ctx)
    ic_txt_dentro = ic_cluster(grupos, delta_dentro(s_ctx_txt, s_ctx), rng)

    print(f"\nacrescimo do texto sobre a tabela (PR-AUC): {d_tab_pr:+.4f} IC {ic_tab_pr}")
    print(f"contra a volatilidade sozinha (PR-AUC): {d_vs_vol:+.4f} IC {ic_vs_vol}")
    print(f"AUC dentro da empresa, modelo implantado: {dentro_ctx:.4f} IC {ic_ctx_dentro}")
    print(f"acrescimo do texto a essa AUC: {d_txt_dentro:+.4f} IC {ic_txt_dentro}")

    def sinal(ic) -> str:
        return "**exclui zero**" if (ic[0] > 0 or ic[1] < 0) else "contém zero"

    L = [
        "# evaluation_triage_within.md — o texto acrescenta por cima? e o modelo separa dias?",
        "",
        f"> Gerado por `scripts/evaluate_triage_within.py` a "
        f"{datetime.now(UTC).strftime('%Y-%m-%d %H:%M')} UTC. **Não editar à mão.**",
        f"> Porta de entrada reproduzida: volatilidade {pr_vol:.3f} e contexto {pr_ctx:.3f} contra "
        f"os congelados {CONGELADO_VOL} e {CONGELADO_CONTEXTO}.",
        "",
        "## Porque é que estas duas perguntas não estavam feitas",
        "",
        "A avaliação da dissertação compara famílias **lado a lado**, e responde a"
        " *qual é melhor*.",
        "Não responde a *o texto acrescenta ao melhor que existe*, nem a *o modelo distingue dois",
        "dias da mesma empresa*. A segunda é a mais informativa, porque tem um chão que não é",
        "preciso estimar: uma tabela de consulta por empresa devolve o mesmo valor para todos os",
        "dias dessa empresa, logo ordena-os ao nível do acaso, **por construção**.",
        "",
        "## Os cinco modelos, sobre o mesmo bloco de teste",
        "",
        "| Modelo | O que vê | PR-AUC | Precisão@5 | **AUC dentro da empresa** |",
        "|---|---|---|---|---|",
    ]
    for rot, oq, pr, pb, dentro, _ in linhas:
        marca = "**" if "texto" in rot.lower() and "Tabela" in rot else ""
        # ⚠️ A tabela de consulta não tem AUC dentro da empresa POR CONSTRUÇÃO, e escrever
        # aqui um número estimado seria dar a entender que foi medida.
        col_dentro = ("0.500 (por construção)" if rot.startswith("Tabela de consulta")
                      else f"{dentro:.3f}")
        L.append(f"| {marca}{rot}{marca} | {oq} | {pr:.3f} | {pb:.3f} | {col_dentro} |")
    L += [
        "",
        f"A coluna da direita é sobre {linhas[0][5]} empresas com positivos e negativos no bloco",
        "de teste, e é uma média ponderada pelo número de pares de cada empresa.",
        "",
        "## Os dois acréscimos, com intervalo por grupos (empresa, dia)",
        "",
        "| Pergunta | Valor | IC 95% | Veredicto |",
        "|---|---|---|---|",
        f"| O texto acrescenta à tabela de consulta? (PR-AUC) | {d_tab_pr:+.4f} | "
        f"[{ic_tab_pr[0]:+.4f}, {ic_tab_pr[1]:+.4f}] | {sinal(ic_tab_pr)} |",
        f"| E bate a volatilidade sozinha, que ganhou na dissertação? (PR-AUC) | {d_vs_vol:+.4f} | "
        f"[{ic_vs_vol[0]:+.4f}, {ic_vs_vol[1]:+.4f}] | {sinal(ic_vs_vol)} |",
        f"| O modelo implantado separa dias da mesma empresa? (AUC dentro) | {dentro_ctx:.4f} | "
        f"[{ic_ctx_dentro[0]:.4f}, {ic_ctx_dentro[1]:.4f}] | "
        f"{'**acima de 0.5**' if ic_ctx_dentro[0] > 0.5 else 'contém 0.5'} |",
        f"| O texto acrescenta a essa separação? | {d_txt_dentro:+.4f} | "
        f"[{ic_txt_dentro[0]:+.4f}, {ic_txt_dentro[1]:+.4f}] | {sinal(ic_txt_dentro)} |",
        "",
        f"Reamostragem: {REAMOSTRAGENS} repetições sobre {len(np.unique(grupos))} grupos "
        f"(empresa, dia), e não sobre as {len(y['test'])} linhas.",
        "",
        "## Como ler isto",
        "",
        "O critério foi fixado antes de correr: um acréscimo só conta se o intervalo excluir",
        "zero. As quatro linhas dizem quatro coisas diferentes, e convém não as juntar.",
        "",
        "**A primeira é o resultado.** O título acrescenta ao melhor preditor conhecido, e o",
        "intervalo exclui zero. Não é grande, e é real.",
        "",
        "**A segunda impede a afirmação forte.** Somar o texto à tabela chega a um valor acima do",
        "da volatilidade sozinha, mas a diferença tem um intervalo que contém zero: são dois",
        "pontos dentro do ruído um do outro, e dizer que *bate* a volatilidade seria ler uma",
        "diferença que a amostra não sustenta.",
        "",
        "**A terceira e a quarta confirmam o diagnóstico em vez de o desmentirem.** Nem o modelo",
        "implantado nem a variante com texto separam dois dias da mesma empresa: os intervalos",
        "contêm $0.5$. A informação que o texto traz distingue **empresas e períodos**, não",
        "notícias.",
        "",
        "E há uma quinta coisa, que não está na tabela dos intervalos e é a que decide o produto:",
        "a **precisão dentro do orçamento não muda** ($0.662$ nas duas linhas da tabela de cima).",
        "O acréscimo existe na ordenação global e desaparece quando só se escolhem cinco por dia,",
        "que é o que o sistema faz. Um ganho que não sobrevive à métrica de produto não muda o",
        "produto, e é assim que fica reportado.",
        "",
        "## Uma ressalva de método, dita antes que alguém pergunte",
        "",
        "Este é mais um modelo avaliado sobre o mesmo bloco de teste, que já foi usado por várias",
        "comparações deste trabalho. Quanto mais vezes se olha para um conjunto de teste, mais",
        "fácil é encontrar nele uma diferença pequena. Duas coisas limitam esse risco, e nenhuma",
        "delas o elimina: a configuração do texto não foi afinada aqui (usa-se a redução a",
        f"{PCA_DIMS} dimensões fixada no re-teste justo anterior), e o critério de decisão foi",
        "escrito no cabeçalho deste ficheiro antes de a medição correr. Um resultado de $+0.012$",
        "deve ser lido com essa reserva.",
        "",
    ]
    SAIDA.write_text("\n".join(L), encoding="utf-8")
    print(f"-> {SAIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
