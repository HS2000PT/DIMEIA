"""Testes da anomalia de volume.

O que tem mesmo de ser protegido: a **ausência de lookahead** (a norma do dia *t* não pode
tocar em *t* nem em nada depois), e a assimetria deliberada (só a cauda superior conta).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from investigator.anomaly_detector.volume import (
    detect_volume_latest,
    volume_z_series,
)


def _volumes_estaveis(n: int = 40, base: float = 1_000_000.0) -> list[float]:
    """Volumes com ruído pequeno e reprodutível."""
    rng = np.random.default_rng(0)
    return list(base * np.exp(rng.normal(scale=0.10, size=n)))


# ── Deteção do último dia ─────────────────────────────────────────────────────
def test_volume_na_norma_nao_e_invulgar() -> None:
    """Um último dia colocado DELIBERADAMENTE na mediana da janela não pode disparar.

    A primeira versão deste teste usava um último dia aleatório e falhou com z=2,16: o sorteio
    tinha produzido um dia genuinamente invulgar. O teste é que estava errado, não o código.
    Trocar a semente até passar seria pesca; fixar o último dia na norma testa a propriedade
    que se quer mesmo.
    """
    vols = _volumes_estaveis(40)
    vols[-1] = float(np.median(vols[-21:-1]))
    res = detect_volume_latest(vols)
    assert not res.is_unusual
    assert abs(res.z_score) < 1.0


def test_taxa_de_disparo_em_dias_normais_e_baixa() -> None:
    """A propriedade agregada, que é a que interessa a um funil de alertas.

    Sobre muitas séries sem qualquer evento injetado, a fração de dias sinalizados tem de ficar
    perto da cauda implicada pelo limiar (z>2 numa distribuição aproximadamente normal ronda
    2%), e não em qualquer valor. É o mesmo argumento de *consistência da taxa de disparo* que
    a tese usa para defender o detetor de preço.
    """
    disparos = 0
    for semente in range(300):
        rng = np.random.default_rng(semente)
        vols = list(1_000_000.0 * np.exp(rng.normal(scale=0.10, size=40)))
        if detect_volume_latest(vols).is_unusual:
            disparos += 1
    taxa = disparos / 300
    assert taxa < 0.06, f"taxa de disparo {taxa:.3f} alta demais para dias sem evento"


def test_pico_de_volume_e_detetado() -> None:
    vols = _volumes_estaveis()
    vols[-1] = vols[-1] * 6.0  # dia de notícia
    res = detect_volume_latest(vols)
    assert res.is_unusual
    assert res.z_score > 2.0
    assert res.ratio > 4.0


def test_volume_baixo_nao_e_sinalizado() -> None:
    """Assimetria deliberada: volume baixo é feriado ou meia sessão, não acontecimento."""
    vols = _volumes_estaveis()
    vols[-1] = vols[-1] / 8.0
    res = detect_volume_latest(vols)
    assert res.z_score < -2.0  # o z REGISTA a anomalia…
    assert not res.is_unusual  # …mas não a sinaliza como evento


def test_ratio_e_legivel_face_a_mediana() -> None:
    vols = [1_000_000.0] * 30
    vols[-1] = 3_000_000.0
    res = detect_volume_latest(vols)
    assert res.ratio == pytest.approx(3.0)


def test_serie_curta_e_rejeitada() -> None:
    with pytest.raises(ValueError, match="pelo menos"):
        detect_volume_latest([1_000_000.0] * 10, window=20)


def test_volumes_invalidos_sao_descartados_e_nao_rebentam_o_log() -> None:
    """Volume 0 ou negativo é dado corrompido; log(0) rebentaria."""
    vols = _volumes_estaveis(45)
    vols[5] = 0.0
    vols[7] = -100.0
    vols[9] = float("nan")
    res = detect_volume_latest(vols)  # não levanta
    assert math.isfinite(res.z_score)


def test_volume_constante_nao_divide_por_zero() -> None:
    res = detect_volume_latest([1_000_000.0] * 30)
    assert res.z_score == 0.0


# ── A série completa ──────────────────────────────────────────────────────────
def test_serie_produz_nan_enquanto_nao_ha_norma() -> None:
    z = volume_z_series(_volumes_estaveis(40), window=20)
    assert z.iloc[:20].isna().all()
    assert z.iloc[21:].notna().all()


def test_serie_concorda_com_a_detecao_do_ultimo_dia() -> None:
    """As duas vias têm de dar o MESMO número, ou uma delas mente.

    É o mesmo teste de consistência que protege o detetor de preço: a via usada ao vivo
    (`detect_volume_latest`) e a via usada na avaliação offline (`volume_z_series`) partilham a
    definição, e uma divergência silenciosa entre elas invalidaria qualquer comparação.
    """
    vols = _volumes_estaveis(60)
    vols[-1] = vols[-1] * 4.0
    z_serie = volume_z_series(vols, window=20).iloc[-1]
    z_ultimo = detect_volume_latest(vols, window=20).z_score
    assert z_serie == pytest.approx(z_ultimo, abs=1e-9)


def test_serie_nao_usa_o_futuro() -> None:
    """Mutar um dia FUTURO não pode alterar o z de um dia anterior.

    É a prova directa de ausência de lookahead, no mesmo espírito do teste que muta preços
    futuros no dataset de triagem.
    """
    vols = _volumes_estaveis(60)
    z_antes = volume_z_series(vols, window=20)

    mutados = list(vols)
    mutados[-1] = mutados[-1] * 50.0  # explode SÓ o último dia
    z_depois = volume_z_series(mutados, window=20)

    # Todos os dias menos o último têm de ficar exatamente iguais.
    pd.testing.assert_series_equal(z_antes.iloc[:-1], z_depois.iloc[:-1])
    # E o último tem mesmo de mudar, senão o teste não estaria a testar nada.
    assert z_antes.iloc[-1] != z_depois.iloc[-1]
