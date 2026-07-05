"""Inferência de triagem na stack LEVE (produção): variante só-contexto, sem SBERT.

O modelo principal da tese (LR contexto+texto) precisa do embedding SBERT do título — stack
pesada. O runner de alertas e a app na nuvem correm a stack leve, por isso o treino grava
também a variante SÓ-CONTEXTO (`models/triage_context_lr.joblib`): volatilidade, momentum,
reação do dia, comprimento do título e setor. Honestidade: o texto que acompanha o score
identifica sempre a variante usada; os números da tese vêm da avaliação, não daqui.

Ausência graciosa: sem o ficheiro do modelo, `load_context_bundle` devolve None e quem chama
segue sem triagem (comportamento antigo intacto — integração off-by-default, ML_PLAN M5).
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from investigator.triage.dataset import SECTORS, event_features
from investigator.triage.explain import lr_group_contributions
from investigator.triage.features import context_block

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = _REPO / "models" / "triage_context_lr.joblib"


def load_context_bundle(path: str | Path = DEFAULT_BUNDLE) -> dict | None:
    """Carrega o bundle só-contexto; None se o ficheiro não existir (ausência graciosa)."""
    p = Path(path)
    if not p.exists():
        return None
    from investigator.triage.model import load_bundle  # import tardio (joblib/sklearn)

    return load_bundle(p)


def score_context(bundle: dict, vol20: float, mom5: float, ret_event: float,
                  headline: str, ticker: str) -> tuple[float, list[tuple[str, float]]]:
    """Probabilidade calibrada + contribuições (XAI) a partir das features de contexto.

    Ticker fora do mapa de setores → one-hot todo a zeros ("setor desconhecido") — o modelo
    pontua na mesma, só sem o sinal de setor.
    """
    df = pd.DataFrame([{
        "vol20": vol20, "mom5": mom5, "ret_event": ret_event,
        "headline_len": float(len(headline)),
        "sector": SECTORS.get(ticker.upper(), ""),
    }])
    x, names = context_block(df)
    if names != bundle["feature_names"]:  # bundle velho vs features novas (guarda tipo R1)
        raise ValueError("Bundle incompatível com as features atuais — retreinar "
                         "(scripts/train_triage.py).")
    prob = float(bundle["calibrator"](bundle["model"].predict_proba(x)[:, 1])[0])
    contribs = lr_group_contributions(bundle["model"], x[0], bundle["feature_names"])
    return prob, contribs


def score_latest(bundle: dict, close: pd.Series, headline: str, ticker: str,
                 ) -> tuple[float, list[tuple[str, float]]] | None:
    """Score do dia mais recente da série de fechos; None se faltar histórico (fail-open)."""
    feats = event_features(close, len(close) - 1)
    if feats is None:
        return None
    return score_context(bundle, feats["vol20"], feats["mom5"], feats["ret_event"],
                         headline, ticker)
