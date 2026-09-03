"""Loop de pós-validação (M5.5): registar decisões → rotular ao maturar → métricas ao vivo.

A ideia "RL" do aluno na forma defensável: cada decisão do gatilho de notícias fica registada
(probabilidade da triagem, gate, mantida ou suprimida); dias depois, quando a janela do rótulo
já fechou ((d, d+h] passou), sabemos O QUE REALMENTE ACONTECEU e rotulamos a decisão com o
MESMO rótulo de materialidade do treino (|retorno anormal vs SPY| ≥ τ, via `abnormal_label`).
Isto dá métricas ao vivo (precisão das decisões mantidas, Brier das probabilidades, base rate)
e dados novos para retreino periódico — **aprendizagem contínua com rótulos atrasados +
monitorização (MLOps)**, não RL clássico (não há MDP: os nossos alertas não afetam o mercado).

Tudo puro exceto o append/leitura do JSONL; o I/O de preços vive em scripts/post_validate.py.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from investigator.triage.dataset import abnormal_label


def log_decision(path: str | Path, *, news_date: str, ticker: str, headline: str,
                 prob: float | None, gate: float | None, kept: bool,
                 feature_snapshot: dict | None = None,
                 model_info: dict | None = None,
                 stage: str | None = None) -> None:
    """Acrescenta UMA decisão ao registo JSONL (cria ficheiro/pasta se preciso).

    `prob`/`gate` = None quando a triagem não pontuou (sem modelo/histórico);
    `kept` = a decisão final (alerta mantido vs suprimido pelo gate).

    `stage` é a porta onde a candidata morreu, e existe porque `kept` deixou de discriminar:
    com orçamento diário ligado a triagem ordena e não veta, logo `kept` é constante e não
    sustenta comparação nenhuma. A porta é a variável que ficou no lugar dele.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": datetime.now(UTC).isoformat(timespec="seconds"),
        "news_date": news_date, "ticker": ticker, "headline": headline,
        "prob": prob, "gate": gate, "kept": kept,
    }
    if feature_snapshot is not None:
        rec["feature_snapshot"] = feature_snapshot
    if model_info is not None:
        rec["model_info"] = model_info
    if stage is not None:
        rec["stage"] = stage
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_log(path: str | Path) -> list[dict]:
    """Lê o registo JSONL; [] se o ficheiro não existir (loop ainda sem decisões)."""
    path = Path(path)
    if not path.exists():
        return []
    out: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def dedup_decisions(decisions: list[dict]) -> list[dict]:
    """Remove repetições (o runner é sem estado e pode registar a mesma notícia em dias
    seguidos): mantém a PRIMEIRA ocorrência de cada (news_date, ticker, headline)."""
    seen: set[tuple] = set()
    out: list[dict] = []
    for d in decisions:
        key = (d.get("news_date"), d.get("ticker"), d.get("headline"))
        if key not in seen:
            seen.add(key)
            out.append(d)
    return out


def label_decision(decision: dict, ticker_close: pd.Series, market_close: pd.Series,
                   tau: float = 0.02, horizon: int = 3) -> int | None:
    """Rotula UMA decisão com o resultado real, na MESMA convenção do treino.

    Alinha as séries (inner join por data), encontra o dia do evento (1.º dia de negociação
    ≥ news_date — regra da KB/dataset) e aplica `abnormal_label`. Devolve None enquanto a
    decisão não maturar (janela (d, d+h] ainda não fechou) ou se a data cair fora da série.
    """
    aligned = pd.DataFrame({"t": ticker_close, "m": market_close}).dropna()
    if aligned.empty:
        return None
    idx = int(aligned.index.searchsorted(pd.to_datetime(decision["news_date"])))
    if idx >= len(aligned):
        return None
    return abnormal_label(aligned["t"], aligned["m"], idx, tau, horizon)


def live_report(labeled: list[dict]) -> dict:
    """Métricas ao vivo sobre decisões JÁ rotuladas (cada dict tem 'label' 0/1).

    Devolve: n, n_mantidas, precisao_mantidas (fração de mantidas que foram materiais),
    n_suprimidas e precisao_suprimidas (o mesmo para as que a porta deitou fora — é este o
    contraste que responde a "a porta escolhe melhor do que o acaso?"), base_rate (fração
    material de TODAS — o chão honesto), brier (só onde há prob) e bins de calibração
    [(p_médio, fração_observada, n), ...] em 3 faixas.
    """
    n = len(labeled)
    kept = [d for d in labeled if d.get("kept")]
    dropped = [d for d in labeled if not d.get("kept")]
    with_prob = [d for d in labeled if d.get("prob") is not None]
    rep: dict = {
        "n": n,
        "n_mantidas": len(kept),
        "precisao_mantidas": (float(np.mean([d["label"] for d in kept])) if kept else float("nan")),
        "n_suprimidas": len(dropped),
        "precisao_suprimidas": (float(np.mean([d["label"] for d in dropped]))
                                if dropped else float("nan")),
        "base_rate": (float(np.mean([d["label"] for d in labeled])) if labeled else float("nan")),
        "brier": (float(np.mean([(d["prob"] - d["label"]) ** 2 for d in with_prob]))
                  if with_prob else float("nan")),
        "calibracao": [],
    }
    for lo, hi in [(0.0, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 1.0001)]:
        faixa = [d for d in with_prob if lo <= d["prob"] < hi]
        if faixa:
            rep["calibracao"].append((
                float(np.mean([d["prob"] for d in faixa])),
                float(np.mean([d["label"] for d in faixa])),
                len(faixa),
            ))
    return rep
