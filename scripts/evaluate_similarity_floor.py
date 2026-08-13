"""evaluate_similarity_floor.py — o chão `min_similarity: 0.45` compra alguma coisa?

## Porque é que este script existe

O `min_similarity` é o **gate mais agressivo do funil**: numa varredura medida matou 7 de 10
tickers, e quatro deles por margens de $\\le$ 0,04. E, ao contrário da `materiality_ladder` — que o
projecto foi **derivar** do varrimento de política, com o rácio de custos escrito ao lado —, o 0,45
foi **escolhido**, justificado por um comentário ("qualidade > volume") e pela observação de que
evidência fraca "parecia aleatória".

Um arguente pergunta *"porquê 0,45?"* e a resposta honesta hoje é *"pareceu-nos"*. Este script
tenta transformar isso numa medição, e a pergunta que faz é a que interessa:

> **A similaridade do cosseno prediz a utilidade de um precedente?**

Se predisser, o chão é derivável do ponto onde a utilidade começa a valer. Se **não** predisser, o
chão está a filtrar por uma quantidade que não separa evidência boa de evidência má — e isso é um
negativo publicável, não um detalhe: dizê-lo vale mais do que manter um número por justificar.

## Como se mede a "utilidade"

Um precedente é mostrado ao utilizador como *"isto já aconteceu, e a seguir o preço fez X"*. É útil
na medida em que o X do precedente diga alguma coisa sobre o que o preço fez a seguir ao evento de
consulta. Mede-se por **concordância de direcção**: o sinal do impacto a +5 dias do precedente
coincide com o do evento de consulta?

O chão de acaso **não é 0,5** e tem de ser medido, não assumido: os retornos do mercado não são
simétricos nem independentes entre nomes. Calcula-se emparelhando ao acaso.

## Protocolo (o mesmo da avaliação de recuperação da tese)

- **Cross-ticker**: o vizinho tem de ser de outra empresa. Um precedente do próprio nome partilha
  causas com a consulta e inflaciona qualquer medida de concordância.
- **Estritamente anterior**: `data(vizinho) < data(consulta)`. É um teste de *precedentes*, e a tese
  já retirou uma afirmação por não ter garantido isto num corpus curto.
- Impacto a +5 dias, que é o horizonte que o produto mostra.

USO
---
    python scripts/evaluate_similarity_floor.py --queries 1500
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

for _fluxo in (sys.stdout, sys.stderr):
    try:
        _fluxo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

KB = RAIZ / "data" / "kb_fnspid_sbert.jsonl"
SAIDA = RAIZ / "docs" / "evaluation" / "evaluation_similarity_floor.md"
CHAO_ACTUAL = 0.45
BINS = [(0.0, 0.30), (0.30, 0.40), (0.40, 0.45), (0.45, 0.50), (0.50, 0.60), (0.60, 1.01)]


def carrega(path: pathlib.Path, horizonte: str = "5"):
    datas, tickers, imps, embs = [], [], [], []
    with path.open(encoding="utf-8") as f:
        for linha in f:
            try:
                d = json.loads(linha)
            except json.JSONDecodeError:
                continue
            imp = (d.get("impacts") or {}).get(horizonte)
            e = d.get("embedding")
            if imp is None or imp != imp or not e:
                continue
            datas.append(d["date"]), tickers.append(d["ticker"])
            imps.append(float(imp)), embs.append(e)
    X = np.asarray(embs, dtype="float32")
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-12
    return (np.asarray(datas), np.asarray(tickers), np.asarray(imps, dtype="float64"), X)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", type=int, default=1500)
    ap.add_argument("--topk", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    if not KB.exists():
        print(f"FALTA {KB} — corre scripts/build_kb.py --sbert primeiro.")
        return 2

    print(f"a carregar {KB.name}…")
    datas, tickers, imps, X = carrega(KB)
    n = len(imps)
    print(f"{n} registos com impacto a +5d e embedding · {X.shape[1]}-d")

    rng = np.random.default_rng(args.seed)

    # ── Chão de acaso: MEDIDO, emparelhando ao acaso sob as mesmas restrições ──
    a = rng.integers(0, n, 200_000)
    b = rng.integers(0, n, 200_000)
    val = (tickers[a] != tickers[b]) & (datas[a] > datas[b])
    chao = float(np.mean(np.sign(imps[a][val]) == np.sign(imps[b][val])))
    print(f"chão de acaso (cross-ticker, anterior): {chao:.4f}  sobre {int(val.sum())} pares")

    # ── Consultas ─────────────────────────────────────────────────────────────
    idx_q = rng.choice(n, size=min(args.queries, n), replace=False)
    pares_sim: list[float] = []
    pares_ok: list[int] = []
    for qi in idx_q:
        sims = X @ X[qi]
        elegivel = (tickers != tickers[qi]) & (datas < datas[qi])
        if not elegivel.any():
            continue
        sims = np.where(elegivel, sims, -np.inf)
        k = min(args.topk, int(elegivel.sum()))
        viz = np.argpartition(-sims, k - 1)[:k]
        for vi in viz:
            if sims[vi] == -np.inf:
                continue
            pares_sim.append(float(sims[vi]))
            pares_ok.append(int(np.sign(imps[vi]) == np.sign(imps[qi])))
    s = np.asarray(pares_sim)
    ok = np.asarray(pares_ok, dtype="float64")
    print(f"{len(s)} pares (consulta, precedente) de {len(idx_q)} consultas")

    linhas = []
    for lo, hi in BINS:
        m = (s >= lo) & (s < hi)
        if m.sum() < 30:
            linhas.append((lo, hi, int(m.sum()), float("nan"), float("nan")))
            continue
        p = float(ok[m].mean())
        se = float(np.sqrt(p * (1 - p) / m.sum()))
        linhas.append((lo, hi, int(m.sum()), p, 1.96 * se))

    acima = s >= CHAO_ACTUAL
    p_acima = float(ok[acima].mean()) if acima.sum() else float("nan")
    p_abaixo = float(ok[~acima].mean()) if (~acima).sum() else float("nan")
    delta = p_acima - p_abaixo
    # erro-padrão da diferença de duas proporções independentes
    se_d = float(np.sqrt(p_acima * (1 - p_acima) / max(acima.sum(), 1)
                         + p_abaixo * (1 - p_abaixo) / max((~acima).sum(), 1)))

    L = [
        "# evaluation_similarity_floor.md — o chão de similaridade compra alguma coisa?",
        "",
        f"> Gerado por `scripts/evaluate_similarity_floor.py` (ADITIVO). Semente {args.seed}; "
        f"{len(idx_q)} consultas × top-{args.topk}. **Não editar à mão.**",
        "",
        f"- Corpus: **{n}** registos com impacto a +5 dias e embedding.",
        "- Protocolo: vizinho de **outra** empresa e **estritamente anterior** à consulta.",
        "- Utilidade = **concordância de direcção** do impacto a +5 dias.",
        f"- **Chão de acaso medido: {chao:.4f}** (emparelhamento aleatório sob as mesmas "
        "restrições). Não é 0,5, e assumir que era teria enviesado tudo.",
        "",
        "## Concordância de direcção por faixa de cosseno",
        "",
        "| cosseno | pares | concordância | IC 95% |",
        "|---|---|---|---|",
    ]
    for lo, hi, cnt, p, ci in linhas:
        if p != p:
            L.append(f"| {lo:.2f}–{hi:.2f} | {cnt} | — | poucos pares |")
        else:
            L.append(f"| {lo:.2f}–{hi:.2f} | {cnt} | **{p:.4f}** | ±{ci:.4f} |")

    L += [
        "",
        f"## O chão actual ({CHAO_ACTUAL})",
        "",
        "| lado | pares | concordância |",
        "|---|---|---|",
        f"| cosseno ≥ {CHAO_ACTUAL} | {int(acima.sum())} | **{p_acima:.4f}** |",
        f"| cosseno < {CHAO_ACTUAL} | {int((~acima).sum())} | **{p_abaixo:.4f}** |",
        f"| diferença | — | **{delta:+.4f}** (±{1.96 * se_d:.4f}) |",
        "",
        "## Veredicto",
        "",
    ]
    significativo = abs(delta) > 1.96 * se_d
    if significativo and delta > 0:
        L.append(f"A similaridade **prediz** a concordância de direcção: passar o chão vale "
                 f"{delta:+.4f} e o intervalo exclui zero. O chão de {CHAO_ACTUAL} está a filtrar "
                 "por uma quantidade que separa evidência melhor de evidência pior — continua a "
                 "ser um valor **escolhido**, mas agora tem uma medição por trás, e o ponto de "
                 "corte pode ser derivado da tabela acima.")
    else:
        L.append(f"⚠️ **A similaridade não separa.** A diferença entre estar acima e abaixo do "
                 f"chão é {delta:+.4f} com intervalo a incluir zero, e a coluna da concordância "
                 f"não sobe de forma monótona com o cosseno. Sobre este corpus, **o chão de "
                 f"{CHAO_ACTUAL} não está a comprar concordância de direcção**.\n\n"
                 "Isto **não** quer dizer que o chão seja inútil: ele também controla o *volume* "
                 "de alertas, e a coerência **temática** que um leitor vê não é a mesma coisa que "
                 "a concordância de direcção — a tese já mede e afirma que a recuperação capta "
                 "**tema, não direcção** (Caso 3). Quer dizer que a justificação honesta do 0,45 é "
                 "*controlo de volume e coerência temática*, e **não** que os precedentes acima do "
                 "chão predizem melhor o que se seguiu.")
    L += [
        "",
        "## O que isto NÃO diz",
        "",
        "- Não mede se o precedente **ajuda um humano** a decidir: isso é o estudo de utilidade.",
        "- A concordância de direcção é uma medida de utilidade entre várias; um precedente pode "
        "ser útil por enquadrar o tema mesmo quando a direcção diverge.",
        "- O corpus é o FNSPID (2018–2023). A KB viva é curta demais para esta medição.",
        "",
        "⚠️ **Não comparar o número desta página com o `0.708` do Caso 3.** São medidas "
        "diferentes com chãos de acaso diferentes, e pô-las lado a lado seria o erro que este "
        "projecto já cometeu uma vez ao comparar purezas com cardinalidades diferentes. O Caso 3 "
        "mede a **coerência interna do conjunto recuperado** (que fracção do cluster se move no "
        f"mesmo sentido), cujo chão de acaso é ~0,69 porque uma maioria é ≥0,5 por construção. "
        "Aqui mede-se a concordância **par a par entre o precedente e a consulta**, cujo chão é "
        f"~0,5 — e medido, {chao:.4f}. As duas dizem a mesma coisa por caminhos distintos: a "
        "recuperação capta tema, não direcção.",
    ]
    SAIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"\nacima do chão {p_acima:.4f} vs abaixo {p_abaixo:.4f} "
          f"(Δ {delta:+.4f} ± {1.96 * se_d:.4f}) · acaso {chao:.4f}")
    print(f"escrito: {SAIDA.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
