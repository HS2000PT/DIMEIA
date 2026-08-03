"""Testes da contagem empírica de excedências. Puros, sem rede e sem Streamlit."""

from __future__ import annotations

import numpy as np
import pytest

from investigator.anomaly_detector.frequency import (
    Exceedance,
    empirical_exceedance,
)


def _serie(valores) -> list[float]:
    return [float(v) for v in valores]


def test_hoje_nao_conta_para_a_propria_raridade() -> None:
    """Se hoje é o maior movimento da janela, a contagem é ZERO.

    Incluir o próprio dia tornaria a contagem ≥1 por construção, e "o maior movimento do
    ano" passaria a ser impossível de dizer mesmo quando é verdade.
    """
    r = empirical_exceedance(_serie([0.001] * 40 + [0.20]))
    assert r is not None
    assert r.count == 0
    assert r.is_record
    assert r.n == 40  # os 40 anteriores, sem o de hoje


def test_empates_contam() -> None:
    """Igualar conta como exceder: a pergunta é "pelo menos isto"."""
    r = empirical_exceedance(_serie([0.05, 0.05] + [0.001] * 38 + [0.05]))
    assert r is not None
    assert r.count == 2


def test_direccao_e_um_subconjunto_da_magnitude() -> None:
    r = empirical_exceedance(_serie([0.06, -0.06, 0.07] + [0.001] * 37 + [0.05]))
    assert r is not None
    assert r.same_direction <= r.count
    assert r.count == 3  # os três excedem em módulo
    assert r.same_direction == 2  # só dois são subidas, como hoje


def test_n_vem_dos_dados_e_nunca_da_constante() -> None:
    """Uma série curta tem de dizer 58, não 250.

    Escrever o tamanho da janela à mão na frase é como se inventa um facto sem dar por
    isso: a interface diria "dos últimos 250 dias" sobre 59 observações.
    """
    r = empirical_exceedance(_serie(list(np.linspace(-0.02, 0.02, 60))))
    assert r is not None
    assert r.n == 59
    assert r.n != 250


def test_lookback_limita_a_janela() -> None:
    r = empirical_exceedance(_serie([0.001] * 600 + [0.05]), lookback=250)
    assert r is not None
    assert r.n == 250


def test_historia_curta_nao_produz_frase() -> None:
    """Com 20 observações, "2 dos últimos 19 dias" é ruído. Melhor não dizer nada."""
    assert empirical_exceedance(_serie([0.01] * 20)) is None
    assert empirical_exceedance(_serie([0.01])) is None
    assert empirical_exceedance(_serie([])) is None


def test_nan_sao_descartados_sem_rebentar() -> None:
    valores = [0.01] * 20 + [float("nan")] * 3 + [0.02] * 20 + [0.5]
    r = empirical_exceedance(valores)
    assert r is not None
    assert r.n == 40  # os NaN saíram, hoje continua de fora
    assert r.count == 0


def test_share_e_uma_fraccao_legivel() -> None:
    r = empirical_exceedance(_serie([0.10] * 10 + [0.001] * 30 + [0.05]))
    assert r is not None
    assert r.count == 10
    assert r.share == pytest.approx(10 / 40)


def test_dia_calmo_e_comum_por_construcao() -> None:
    """Um movimento pequeno tem de sair como banal, não como raro."""
    r = empirical_exceedance(_serie(list(np.linspace(-0.05, 0.05, 200)) + [0.0001]))
    assert r is not None
    assert r.count > r.n // 2


def test_contagem_e_de_dois_lados() -> None:
    """A pergunta é "um movimento deste tamanho", não "uma queda destas"."""
    r = empirical_exceedance(_serie([-0.09] * 5 + [0.001] * 35 + [0.08]))
    assert r is not None
    assert r.count == 5  # cinco quedas excedem em módulo uma subida
    assert r.same_direction == 0  # nenhuma no mesmo sentido


def test_dataclass_e_imutavel() -> None:
    r = empirical_exceedance(_serie([0.001] * 40 + [0.2]))
    assert isinstance(r, Exceedance)
    with pytest.raises(AttributeError):
        r.count = 99  # type: ignore[misc]
