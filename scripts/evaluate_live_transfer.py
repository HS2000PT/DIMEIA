"""O modelo de triagem transfere para a população que de facto vê? E se não, o que falha?

PORQUE É QUE ISTO EXISTE
------------------------
A pós-validação (`post_validate.py`) mede uma coisa: os alertas MANTIDOS foram materiais mais
vezes do que a taxa-base? Sobre 530 decisões maturadas a resposta é **não** (0,592 mantidos
contra 0,647 suprimidos, p=0,20). Isso diz que o gate não está a ajudar, mas **não diz porquê**,
e as duas causas possíveis pedem correcções opostas:

- **Discriminação partida** — o score não ordena. Nenhuma recalibração salva isto, porque
  recalibrar é uma transformação *monótona*: preserva a ordem exactamente. Se a ordem está
  errada, mudar o mapa de probabilidades não muda nada de nada.
- **Calibração partida** — o score ordena bem, mas os números estão na escala errada para esta
  população, e o corte a 0,5 cai no sítio errado. Isto **é** reparável, e barato: dois
  parâmetros.

Distinguir as duas é a única forma de decidir o que fazer a seguir sem adivinhar. É a diferença
entre "o modelo não serve aqui" e "o limiar está mal posto".

O QUE MEDE
----------
1. **Discriminação** na população implantada: ROC-AUC (probabilidade de um positivo aleatório
   ser pontuado acima de um negativo aleatório) e PR-AUC contra a prevalência ao vivo como chão.
   ROC-AUC ≈ 0,5 significa ordenação ao nível do acaso.
2. **Calibração**: Brier, e a curva fiabilidade por decis.
3. **A decomposição que decide**: se houver discriminação, ajusta-se uma Platt nova SOBRE os
   dados ao vivo, com validação cruzada (senão mede-se o ajuste a si próprio), e reporta-se
   quanto do Brier era calibração e quanto era ordenação.
4. **O limiar** re-derivado para esta população sob a mesma razão de custo do varrimento de
   política, para o número ser derivado e não escolhido.

⚠️ **Limite declarado:** o rótulo ao vivo só existe para decisões cuja janela já fechou, e o
conjunto é pequeno (centenas, não dezenas de milhares). Os intervalos são largos e são
reportados. Isto é monitorização com estatística, não uma segunda avaliação da tese.

USO
---
    python scripts/evaluate_live_transfer.py
    python scripts/evaluate_live_transfer.py --log <caminho>  # log já descarregado
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import urllib.request
from datetime import UTC, datetime
from statistics import NormalDist

import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

DESTINO = RAIZ / "docs" / "evaluation" / "evaluation_live_transfer.md"
LOG_REMOTO = ("https://raw.githubusercontent.com/HS2000PT/DIMEIA/"
              "alerts-history/predictions_log.jsonl")
MERCADO = "SPY"
SEMENTE = 42


def _wilson(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    z = NormalDist().inv_cdf(1 - (1 - conf) / 2)
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    meio = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (centro - meio, centro + meio)


def _maturar(caminho: pathlib.Path, tau: float, horizonte: int) -> list[dict]:
    """Rotula cada decisão cuja janela já fechou, com a MESMA regra do treino."""
    # Reutiliza o carregador da pós-validação em vez de o reimplementar: duas versões da
    # mesma busca de preços divergiriam em silêncio, que é a classe de defeito que este
    # projecto já pagou noutros sítios.
    from investigator.triage.postval import dedup_decisions, label_decision, read_log
    from scripts.post_validate import _load_all

    decisoes = dedup_decisions(read_log(caminho))
    tickers = sorted({d["ticker"] for d in decisoes})
    inicio = min(d["news_date"] for d in decisoes if d.get("news_date"))[:10]

    series = _load_all([*tickers, MERCADO], inicio)
    spy = series.get(MERCADO)
    if spy is None:
        raise SystemExit("Sem série do mercado — impossível rotular.")

    maturadas = []
    for d in decisoes:
        serie = series.get(d["ticker"])
        if serie is None:
            continue
        y = label_decision(d, serie, spy, tau=tau, horizon=horizonte)
        if y is not None:
            maturadas.append({**d, "label": y})
    return maturadas


def _fiabilidade(p: np.ndarray, y: np.ndarray, bins: int = 5) -> list[tuple]:
    """Curva de fiabilidade por quantis de p (quantis, não larguras iguais: os scores
    concentram-se e bins de largura fixa ficariam vazios)."""
    if len(p) < bins * 4:
        bins = max(2, len(p) // 20)
    cortes = np.quantile(p, np.linspace(0, 1, bins + 1))
    cortes[-1] += 1e-9
    linhas = []
    for i in range(bins):
        m = (p >= cortes[i]) & (p < cortes[i + 1])
        if m.sum() == 0:
            continue
        linhas.append((float(p[m].mean()), float(y[m].mean()), int(m.sum())))
    return linhas


def main() -> int:
    ap = argparse.ArgumentParser(description="Transferência do modelo para a população ao vivo")
    ap.add_argument("--log", default="")
    ap.add_argument("--tau", type=float, default=0.02)
    ap.add_argument("--horizon", type=int, default=3)
    ap.add_argument("--out", default=str(DESTINO))
    args = ap.parse_args()

    from investigator.console import force_utf8_stdout

    force_utf8_stdout()

    caminho = pathlib.Path(args.log) if args.log else None
    if caminho is None:
        caminho = RAIZ / "data" / "_live_predictions.jsonl"
        print(f"a descarregar o log de produção -> {caminho.name}")
        urllib.request.urlopen(LOG_REMOTO, timeout=60)  # noqa: S310
        caminho.write_bytes(urllib.request.urlopen(LOG_REMOTO, timeout=60).read())  # noqa: S310

    maturadas = _maturar(caminho, args.tau, args.horizon)
    if len(maturadas) < 50:
        raise SystemExit(f"Só {len(maturadas)} decisões maturadas — poucas para concluir.")

    p = np.array([float(d["prob"]) for d in maturadas])
    y = np.array([int(d["label"]) for d in maturadas])
    kept = np.array([bool(d["kept"]) for d in maturadas])
    # O rótulo é por (ticker, dia): todas as manchetes da mesma empresa no mesmo dia partilham
    # o mesmo desfecho. Tratar as linhas como independentes estreitaria o IC de forma
    # enganadora — é exactamente a correcção que o Cap. 5 já aplica à avaliação offline, e
    # seria incoerente não a aplicar aqui.
    clusters = np.array([f"{d['ticker']}|{d['news_date'][:10]}" for d in maturadas])
    n, base = len(y), float(y.mean())
    n_clusters = len(np.unique(clusters))

    from sklearn.metrics import average_precision_score, roc_auc_score

    roc = float(roc_auc_score(y, p))
    pr = float(average_precision_score(y, p))
    brier = float(np.mean((p - y) ** 2))

    # (1) Discriminação, com IC por BOOTSTRAP DE CLUSTER: reamostram-se pares (ticker, dia)
    # inteiros, não linhas soltas.
    rng = np.random.default_rng(SEMENTE)
    uniq = np.unique(clusters)
    por_cluster = {c: np.flatnonzero(clusters == c) for c in uniq}
    boots = []
    for _ in range(2000):
        escolhidos = rng.choice(uniq, size=len(uniq), replace=True)
        i = np.concatenate([por_cluster[c] for c in escolhidos])
        if len(np.unique(y[i])) < 2:
            continue
        boots.append(roc_auc_score(y[i], p[i]))
    lo_roc, hi_roc = (float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)))

    # (2) Recalibração ao vivo, com validação cruzada. Sem CV isto mede o ajuste a si próprio.
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold

    p_recal = np.zeros(n)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMENTE)
    for tr, te in skf.split(p.reshape(-1, 1), y):
        lr = LogisticRegression(max_iter=1000)
        lr.fit(p[tr].reshape(-1, 1), y[tr])
        p_recal[te] = lr.predict_proba(p[te].reshape(-1, 1))[:, 1]
    brier_recal = float(np.mean((p_recal - y) ** 2))

    # (3) O que o gate fez, e o que faria com o limiar re-derivado.
    keep_p = float(y[kept].mean()) if kept.any() else float("nan")
    sup_p = float(y[~kept].mean()) if (~kept).any() else float("nan")

    linhas = [
        "# evaluation_live_transfer.md — o modelo transfere para a população implantada?",
        "",
        "> Gerado por `scripts/evaluate_live_transfer.py` a "
        f"{datetime.now(UTC):%Y-%m-%d %H:%M} UTC.",
        "> **Não editar à mão.** Semente fixa; re-correr sobre o mesmo log reproduz.",
        "",
        f"- Decisões maturadas: **{n}** linhas em **{n_clusters}** pares (ticker, dia) · rótulo "
        f"|retorno anormal vs {MERCADO} em (d, d+{args.horizon}]| ≥ {args.tau:.2f}",
        f"- Prevalência ao vivo: **{base:.3f}** (treino: 0.378)",
        "",
        "⚠️ O rótulo é por (ticker, dia), pelo que as linhas vêm em grupos e a amostra efectiva",
        f"é de {n_clusters} unidades e não de {n}. O IC abaixo vem de bootstrap **de cluster**;",
        "um bootstrap sobre linhas daria um intervalo mais estreito e enganador.",
        "",
        "## 1. Discriminação — o score ordena?",
        "",
        "| métrica | valor | chão |",
        "|---|---|---|",
        f"| ROC-AUC | **{roc:.3f}** (IC 95% de cluster [{lo_roc:.3f}, {hi_roc:.3f}]) | 0.500 |",
        f"| PR-AUC | {pr:.3f} | {base:.3f} (prevalência) |",
        "",
        "## 2. Calibração — os números estão na escala certa?",
        "",
        "| métrica | valor |",
        "|---|---|",
        f"| Brier, probabilidades tal como enviadas | **{brier:.4f}** |",
        f"| Brier, recalibrado ao vivo (Platt, CV 5 folds) | **{brier_recal:.4f}** |",
        f"| ganho da recalibração | {brier - brier_recal:+.4f} |",
        "",
        "Fiabilidade por quintis (previsto vs observado):",
        "",
        "| p previsto (média) | fração observada | n |",
        "|---|---|---|",
    ]
    for pm, ym, cnt in _fiabilidade(p, y):
        linhas.append(f"| {pm:.3f} | {ym:.3f} | {cnt} |")

    lo_k, hi_k = _wilson(int(y[kept].sum()), int(kept.sum()))
    lo_s, hi_s = _wilson(int(y[~kept].sum()), int((~kept).sum()))
    linhas += [
        "",
        "## 3. O que o gate fez",
        "",
        "| conjunto | materiais | n | IC 95% |",
        "|---|---|---|---|",
        f"| mantidos (p ≥ 0.5) | {keep_p:.3f} | {int(kept.sum())} | [{lo_k:.3f}, {hi_k:.3f}] |",
        f"| suprimidos (p < 0.5) | {sup_p:.3f} | {int((~kept).sum())} | [{lo_s:.3f}, {hi_s:.3f}] |",
        "",
    ]
    saida = pathlib.Path(args.out)
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print(f"n={n} prevalencia={base:.3f}")
    print(f"ROC-AUC {roc:.3f} IC[{lo_roc:.3f},{hi_roc:.3f}] · PR-AUC {pr:.3f} (chao {base:.3f})")
    print(f"Brier {brier:.4f} -> recalibrado {brier_recal:.4f} ({brier - brier_recal:+.4f})")
    print(f"mantidos {keep_p:.3f} ({int(kept.sum())}) · suprimidos {sup_p:.3f} "
          f"({int((~kept).sum())})")
    print(f"Escrito: {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
