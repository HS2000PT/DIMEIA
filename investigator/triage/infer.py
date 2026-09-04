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

import hashlib
import json
import math
from pathlib import Path

import pandas as pd

from investigator.triage.dataset import SECTORS, event_features
from investigator.triage.explain import lr_group_contributions
from investigator.triage.features import context_block

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = _REPO / "models" / "triage_context_lr.joblib"
FEATURE_SCHEMA = "triage-context-v1"


def load_context_bundle(path: str | Path = DEFAULT_BUNDLE) -> dict | None:
    """Carrega o bundle só-contexto; None se o ficheiro não existir (ausência graciosa)."""
    p = Path(path)
    if not p.exists():
        return None
    from investigator.triage.model import load_bundle  # import tardio (joblib/sklearn)

    bundle = load_bundle(p)
    sidecar = p.with_suffix(".json")
    meta: dict = {}
    if sidecar.exists():
        try:
            meta = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            meta = {}
    bundle["_model_info"] = {
        "artifact": p.name,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "trained_at": meta.get("gerado"),
        "model_family": meta.get("modelo"),
        "feature_schema": FEATURE_SCHEMA,
    }
    return bundle


# Setor em tempo de INFERÊNCIA para nomes que a watchlist tem e o corpus de treino não.
#
# ⚠️ Porque isto existe. O `SECTORS` de `dataset.py` é o mapa do CORPUS (14 tickers do FNSPID);
# a watchlist implantada tem doze nomes, e **AMD e NFLX não estão em nenhum dos dois**. Sem esta
# tabela, `SECTORS.get(t, "")` devolvia "" e o `context_block` produzia um one-hot de setor
# **todo a zeros** — um padrão que não existe em **nenhuma** das 79.753 linhas de treino, onde
# toda a linha tem exactamente um setor activo. Dois dos doze nomes implantados eram pontuados
# fora da distribuição, em silêncio.
#
# Não se toca no mapa canónico: ele descreve o corpus, é partilhado com a avaliação de
# recuperação, e alterá-lo mexeria em números congelados. Isto é uma decisão de IMPLANTAÇÃO e
# fica declarada como tal — é uma aproximação (nenhum dos dois esteve no treino) e a alternativa
# era pior.
DEPLOY_SECTORS: dict[str, str] = {"AMD": "tech", "NFLX": "tech"}


def deploy_sector(ticker: str) -> str:
    """O setor a usar na inferência: corpus primeiro, watchlist depois, "" em último."""
    t = ticker.upper()
    return SECTORS.get(t) or DEPLOY_SECTORS.get(t, "")


def score_context(bundle: dict, vol20: float, mom5: float, ret_event: float,
                  headline: str, ticker: str) -> tuple[float, list[tuple[str, float]]]:
    """Probabilidade calibrada + contribuições (XAI) a partir das features de contexto.

    Ticker fora de qualquer mapa → one-hot todo a zeros ("setor desconhecido"). O modelo pontua
    na mesma, mas **fora da distribuição de treino** — ver `DEPLOY_SECTORS`.
    """
    scored, _ = score_context_with_snapshot(
        bundle, vol20, mom5, ret_event, headline, ticker
    )
    return scored


def score_context_with_snapshot(
    bundle: dict, vol20: float, mom5: float, ret_event: float,
    headline: str, ticker: str, *, feature_as_of: str | None = None,
) -> tuple[tuple[float, list[tuple[str, float]]], dict]:
    """Pontua e devolve o vetor exato necessário para reproduzir a decisão.

    O snapshot é apenas evidência de inferência. Não contém rótulos futuros e não afirma que a
    barra usada era um fecho completo; `feature_as_of` regista a data que a fonte entregou.
    """
    df = pd.DataFrame([{
        "vol20": vol20, "mom5": mom5, "ret_event": ret_event,
        "headline_len": float(len(headline)),
        "sector": deploy_sector(ticker),
    }])
    x, names = context_block(df)
    if names != bundle["feature_names"]:  # bundle velho vs features novas (guarda tipo R1)
        raise ValueError("Bundle incompatível com as features atuais — retreinar "
                         "(scripts/train_triage.py).")
    prob = float(bundle["calibrator"](bundle["model"].predict_proba(x)[:, 1])[0])
    contribs = lr_group_contributions(bundle["model"], x[0], bundle["feature_names"])
    snapshot = {
        "schema": FEATURE_SCHEMA,
        "as_of": feature_as_of,
        "values": {name: float(value) for name, value in zip(names, x[0], strict=True)},
    }
    return (prob, contribs), snapshot


def score_latest(bundle: dict, close: pd.Series, headline: str, ticker: str,
                 ) -> tuple[float, list[tuple[str, float]]] | None:
    """Score do dia mais recente da série de fechos; None se faltar histórico (fail-open).

    ⚠️ O guard do NaN foi acrescentado depois de o registo de produção o exigir, e a forma como
    apareceu vale a pena guardar. A 2026-08-04 a fonte de preços devolveu buracos em toda a
    watchlist, as features saíram NaN, e o `LogisticRegression` levantou `ValueError` — 21 vezes
    num dia, 25 no total. O ciclo continuava (o chamador apanha tudo e segue sem triagem), por
    isso nada se perdeu; mas no registo isso ficava como `error` com um stack trace, que é
    **indistinguível de uma avaria real**. Um dia sem preços não é um defeito do sistema, é uma
    condição do mundo, e tem de se ler como tal.

    `event_features` já devolve None quando falta histórico; o que não apanhava era histórico
    presente mas com furos. Agora falha aberto do mesmo modo, e a diferença é que o log passa a
    dizer "sem dados" em vez de rebentar.
    """
    result = score_latest_with_snapshot(bundle, close, headline, ticker)
    return result[0] if result is not None else None


def score_latest_with_snapshot(
    bundle: dict, close: pd.Series, headline: str, ticker: str,
) -> tuple[tuple[float, list[tuple[str, float]]], dict] | None:
    """Versão auditável de :func:`score_latest`, sem alterar a API existente."""
    # A fonte de preços devolve a barra do dia corrente com fecho NaN enquanto a sessão não
    # está liquidada. Pontuar sobre essa barra dá `ret_event` NaN e a função devolvia None —
    # ou seja, a triagem DEIXAVA DE PONTUAR, em silêncio, durante parte de cada dia. Encontrado
    # a 2026-09-04 a verificar produção: 139 linhas `[triagem]` às 23:30 e zero às 00:07, com a
    # série a trazer um único NaN no fim. É a mesma família do incidente de 2026-08-04, e o
    # guard que daí veio faz falhar aberto — o que evita a excepção e esconde a paragem.
    #
    # Cortar só o NaN FINAL e pontuar a última barra COMPLETA é o que a dissertação já descreve
    # como comportamento de produção: `as_of` regista a barra usada, e a assimetria do
    # `ret_event` entre treino e produção está declarada. Não se preenche nem se extrapola nada.
    #
    # ⚠️ UMA barra, e só uma. Duas ou mais em falta não são a sessão por liquidar: são a fonte
    # partida, que foi o que aconteceu a 2026-08-04 em toda a watchlist. Nesse caso pontuar a
    # última completa daria um score de dias antes apresentado como o de hoje, e isso é pior do
    # que não pontuar. Além de uma, continua a falhar ABERTO — o invariante de 2026-08-04
    # mantém-se, e tem teste próprio.
    if hasattr(close, "iloc") and len(close) and close.iloc[-1] != close.iloc[-1]:
        close = close.iloc[:-1]
    if len(close) == 0:
        return None
    feats = event_features(close, len(close) - 1)
    if feats is None:
        return None
    if any(v is None or (isinstance(v, float) and math.isnan(v))
           for v in (feats["vol20"], feats["mom5"], feats["ret_event"])):
        return None
    as_of = None
    if len(close.index):
        stamp = pd.Timestamp(close.index[-1])
        as_of = stamp.isoformat()
    return score_context_with_snapshot(
        bundle, feats["vol20"], feats["mom5"], feats["ret_event"], headline, ticker,
        feature_as_of=as_of,
    )


def score_background(bundle: dict, close: pd.Series, ticker: str,
                     ) -> tuple[float, list[tuple[str, float]]] | None:
    """Risco de "fundo" do ticker HOJE, sem nenhuma notícia concreta (painel ao vivo).

    Mesmo modelo, mesmas features de contexto (volatilidade/momento/reação/setor); o título
    é uma string vazia (`headline_len=0`) — um placeholder honesto e explícito, não uma
    notícia inventada. Distingue-se sempre na UI de um score "para esta notícia".
    """
    return score_latest(bundle, close, "", ticker)
