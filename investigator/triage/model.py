"""Modelos de triagem: treino, calibração (Platt), métricas e persistência.

Quatro famílias (ML_PLAN §2), todas sklearn/CPU e determinísticas com seed:
- "always"  — alertar-sempre (score constante; PR-AUC = prevalência) — chão honesto.
- "vol"     — regressão logística SÓ com vol20 (a baseline forte que o revisor pergunta).
- "context"/"text"/"full" — LR nas ablações só-contexto / só-texto / ambos (principal: "full").
- "gbm"     — HistGradientBoosting no bloco completo (aprendiz mais forte, menos interpretável).

Calibração: Platt (sigmóide ajustada na VALIDAÇÃO, nunca no teste) implementada à mão —
pequena, determinística e fácil de explicar ao júri.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

VOL_IDX = 0  # posição de vol20 no bloco de contexto (CONTEXT_COLS[0])


def make_model(name: str, seed: int = 42):
    """Constrói o estimador (não treinado) para cada família."""
    if name in {"vol", "context", "text", "full"}:
        return Pipeline([
            ("scale", StandardScaler()),
            ("lr", LogisticRegression(max_iter=2000, class_weight="balanced",
                                      random_state=seed)),
        ])
    if name == "gbm":
        return HistGradientBoostingClassifier(random_state=seed, class_weight="balanced")
    raise ValueError(f"Modelo desconhecido: {name}")


def scores_of(model, x: np.ndarray) -> np.ndarray:
    """Score não-calibrado em [0,1] (probabilidade do sklearn)."""
    return model.predict_proba(x)[:, 1]


# ── Calibração de Platt (na validação) ────────────────────────────────────────
@dataclass
class PlattCalibrator:
    """p_calibrada = sigmóide(a·score + b), com (a,b) ajustados na validação."""

    a: float
    b: float

    def __call__(self, scores: np.ndarray) -> np.ndarray:
        z = self.a * np.asarray(scores, dtype="float64") + self.b
        return 1.0 / (1.0 + np.exp(-z))


def fit_platt(scores_val: np.ndarray, y_val: np.ndarray, seed: int = 42) -> PlattCalibrator:
    lr = LogisticRegression(max_iter=1000, random_state=seed)
    lr.fit(np.asarray(scores_val, dtype="float64").reshape(-1, 1), y_val)
    return PlattCalibrator(a=float(lr.coef_[0][0]), b=float(lr.intercept_[0]))


# ── Métricas ──────────────────────────────────────────────────────────────────
def metrics(y_true: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    """PR-AUC (principal), ROC-AUC e Brier. Robusto a classe única (devolve NaN)."""
    y = np.asarray(y_true)
    s = np.asarray(scores, dtype="float64")
    if len(np.unique(y)) < 2:
        return {"pr_auc": float("nan"), "roc_auc": float("nan"),
                "brier": float(brier_score_loss(y, s))}
    return {
        "pr_auc": float(average_precision_score(y, s)),
        "roc_auc": float(roc_auc_score(y, s)),
        "brier": float(brier_score_loss(y, s)),
    }


def precision_at_daily_budget(dates: np.ndarray, y_true: np.ndarray,
                              scores: np.ndarray, budget: int = 5) -> float:
    """Métrica de produto: em cada dia, alertar só o top-`budget`; precisão dos selecionados.

    Reflete o custo real (fadiga de alertas): o utilizador aguenta N alertas/dia, não todos.
    """
    sel_true: list[int] = []
    order = np.argsort(-np.asarray(scores, dtype="float64"), kind="stable")
    by_day: dict[object, int] = {}
    for i in order:
        d = dates[i]
        if by_day.get(d, 0) < budget:
            by_day[d] = by_day.get(d, 0) + 1
            sel_true.append(int(y_true[i]))
    if not sel_true:
        return float("nan")
    return float(np.mean(sel_true))


# ── Persistência ──────────────────────────────────────────────────────────────
def save_bundle(path: str | Path, model, calibrator: PlattCalibrator,
                feature_names: list[str], meta: dict) -> None:
    """Grava modelo + calibrador + nomes de features (joblib) e metadados (JSON ao lado)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "calibrator": calibrator, "feature_names": feature_names}, path)
    path.with_suffix(".json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def load_bundle(path: str | Path) -> dict:
    """Carrega o bundle {model, calibrator, feature_names}."""
    return joblib.load(Path(path))
