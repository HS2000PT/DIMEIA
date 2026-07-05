"""Testes do dataset de triagem: rótulos à mão, ANTI-LOOKAHEAD e embargo temporal."""

from __future__ import annotations

import math

import pandas as pd
import pytest

from investigator.correlation_engine.event_study import abnormal_returns
from investigator.triage.dataset import abnormal_label, assign_splits, event_features


def _serie(valores) -> pd.Series:
    return pd.Series([float(v) for v in valores])


# ── Retorno anormal (rótulo) — casos calculados à mão ─────────────────────────

def test_retorno_anormal_calculado_a_mao():
    # Ticker sobe 10% em 1 dia; mercado sobe 5% → anormal = 0.10 − 0.05 = 0.05.
    ticker = _serie([100, 110, 110, 110])
    market = _serie([100, 105, 105, 105])
    ar = abnormal_returns(ticker, market, event_idx=0, horizons=(1,))
    assert ar[1] == pytest.approx(0.05)


def test_retorno_anormal_nan_sem_futuro():
    ticker = _serie([100, 110])
    market = _serie([100, 105])
    ar = abnormal_returns(ticker, market, event_idx=1, horizons=(3,))
    assert math.isnan(ar[3])


def test_retorno_anormal_exige_series_alinhadas():
    with pytest.raises(ValueError):
        abnormal_returns(_serie([1, 2, 3]), _serie([1, 2]), event_idx=0)


def test_rotulo_material_e_nao_material():
    # Anormal a +3d: ticker +8% vs mercado 0% → 8% ≥ 2% → material (1).
    ticker = _serie([100] * 30 + [100, 102, 104, 108])
    market = _serie([100] * 34)
    assert abnormal_label(ticker, market, event_idx=30, tau=0.02, horizon=3) == 1
    # Movimento igual ao do mercado → anormal ≈ 0 → não-material (0).
    tudo_igual = _serie([100] * 30 + [100, 102, 104, 108])
    assert abnormal_label(tudo_igual, tudo_igual, event_idx=30, tau=0.02, horizon=3) == 0


def test_rotulo_none_quando_evento_demasiado_recente():
    ticker = _serie([100] * 32)
    assert abnormal_label(ticker, ticker, event_idx=31, tau=0.02, horizon=3) is None


# ── Features — convenção temporal e ANTI-LOOKAHEAD ────────────────────────────

def test_features_valores_a_mao():
    # 25 fechos constantes → vol20 = 0, mom5 = 0; depois um salto no dia do evento.
    closes = [100.0] * 25 + [110.0]  # evento no índice 25 (fecho 100 → 110)
    f = event_features(_serie(closes), event_idx=25)
    assert f["vol20"] == pytest.approx(0.0)
    assert f["mom5"] == pytest.approx(0.0)
    assert f["ret_event"] == pytest.approx(math.log(110 / 100))


def test_features_none_sem_historico():
    assert event_features(_serie([100.0] * 10), event_idx=5) is None


def test_anti_lookahead_mutar_o_futuro_nao_muda_features():
    """A garantia central (§6.5): nada depois do fecho do dia do evento entra nas features."""
    base = [100.0 + i * 0.1 for i in range(30)]
    futuro_a = base + [200.0, 300.0, 400.0]   # futuros absurdos A
    futuro_b = base + [50.0, 10.0, 1.0]       # futuros absurdos B
    d = len(base) - 1  # evento no último dia de `base`
    fa = event_features(_serie(futuro_a), event_idx=d)
    fb = event_features(_serie(futuro_b), event_idx=d)
    assert fa == fb  # features idênticas ⇒ o futuro não vaza


def test_anti_lookahead_mutar_o_futuro_muda_o_rotulo_mas_nao_as_features():
    base = [100.0] * 25
    sobe = _serie(base + [100, 110, 120, 130])   # movimento anormal enorme
    plano = _serie(base + [100, 100, 100, 100])  # nada acontece
    mercado = _serie([100.0] * 29)
    d = 25
    assert event_features(sobe, d) == event_features(plano, d)          # features iguais
    assert abnormal_label(sobe, mercado, d, 0.02, 3) == 1               # rótulos diferentes
    assert abnormal_label(plano, mercado, d, 0.02, 3) == 0


# ── Divisão temporal com embargo ──────────────────────────────────────────────

def test_split_temporal_ordem_e_embargo():
    # 20 dias únicos, 2 linhas por dia → train=14 dias, embargo=2, val=1, embargo=2, test=1.
    dias = pd.to_datetime([f"2024-01-{d:02d}" for d in range(1, 21)])
    datas = pd.Series(list(dias) * 2)
    tags = assign_splits(datas, train_frac=0.70, val_frac=0.15, embargo_days=2)
    por_dia = pd.DataFrame({"data": datas, "tag": tags}).groupby("data")["tag"].nunique()
    assert (por_dia == 1).all()  # o mesmo dia nunca fica em dois blocos
    df = pd.DataFrame({"data": datas, "tag": tags})
    max_train = df[df.tag == "train"].data.max()
    min_val = df[df.tag == "val"].data.min()
    min_test = df[df.tag == "test"].data.min()
    assert max_train < min_val < min_test  # ordem temporal estrita
    # Embargo: nenhum dia de val nos 2 dias únicos imediatamente após o fim do treino.
    dias_unicos = sorted(datas.unique())
    pos_train = dias_unicos.index(max_train)
    proibidos = set(dias_unicos[pos_train + 1 : pos_train + 3])
    assert proibidos.isdisjoint(set(df[df.tag == "val"].data.unique()))


def test_split_fracoes_aproximadas():
    dias = pd.to_datetime([f"2024-{m:02d}-{d:02d}" for m in range(1, 11) for d in range(1, 11)])
    tags = assign_splits(pd.Series(dias), embargo_days=5)
    frac_train = (tags == "train").mean()
    assert 0.65 <= frac_train <= 0.75
    assert set(tags.unique()) <= {"train", "val", "test", "embargo"}
