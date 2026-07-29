"""Testes da análise do estudo de utilidade — a estatística tem de estar certa ANTES de
haver dados reais, senão o piloto produz um número errado e ninguém dá por isso.

Puro: só as funções de estatística; nada de rede, nada de ficheiros.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "analyse_usefulness", Path(__file__).resolve().parents[1] / "scripts" / "analyse_usefulness.py"
)
au = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(au)


# ── Intervalo de Wilson ─────────────────────────────────────────────────────────
def test_wilson_e_assimetrico_perto_dos_extremos():
    """A razão de usar Wilson e não o intervalo normal: com 100% de acertos o normal dá
    largura ZERO (0%–0% de margem), o que é absurdo com N pequeno."""
    lo, hi = au._wilson(8, 8)
    assert lo < 1.0, "com n=8 e 8 acertos o limite inferior não pode ser 1.0"
    assert hi == pytest.approx(1.0, abs=1e-9)
    assert lo > 0.6  # mas continua a ser informativo


def test_wilson_nunca_sai_de_zero_um():
    for k, n in ((0, 5), (5, 5), (1, 3), (0, 1)):
        lo, hi = au._wilson(k, n)
        assert 0.0 <= lo <= hi <= 1.0


def test_wilson_estreita_quando_n_cresce():
    largura_pequena = lambda k, n: (lambda t: t[1] - t[0])(au._wilson(k, n))  # noqa: E731
    assert largura_pequena(5, 10) > largura_pequena(50, 100)


def test_wilson_com_n_zero_nao_rebenta():
    lo, hi = au._wilson(0, 0)
    assert lo != lo and hi != hi  # NaN


# ── Wilcoxon emparelhado ────────────────────────────────────────────────────────
def test_wilcoxon_recusa_amostra_pequena_demais():
    """A aproximação normal deixa de ser razoável abaixo de ~6 pares não-empatados. Devolver
    None é a resposta honesta — melhor nenhum p-value do que um p-value inválido."""
    assert au._wilcoxon([(3.0, 4.0), (2.0, 3.0), (3.0, 4.0)]) is None


def test_wilcoxon_ignora_pares_empatados():
    """Empates não contribuem para o teste; se sobrarem poucos, não há teste."""
    pares = [(3.0, 3.0)] * 10 + [(2.0, 4.0), (3.0, 5.0)]
    assert au._wilcoxon(pares) is None  # só 2 pares úteis


def test_wilcoxon_deteta_diferenca_consistente():
    """B melhor do que A em todos os pares → W mínimo e p pequeno."""
    pares = [(2.0, 4.0), (3.0, 5.0), (2.5, 4.5), (3.0, 4.0),
             (2.0, 5.0), (2.5, 4.0), (3.0, 4.5), (2.0, 4.0)]
    res = au._wilcoxon(pares)
    assert res is not None
    w, p = res
    assert w == 0.0        # nenhuma diferença negativa
    assert p < 0.05


def test_wilcoxon_nao_deteta_diferenca_quando_nao_ha():
    pares = [(3.0, 4.0), (4.0, 3.0), (3.0, 2.0), (2.0, 3.0),
             (4.0, 5.0), (5.0, 4.0), (3.0, 4.0), (4.0, 3.0)]
    res = au._wilcoxon(pares)
    assert res is not None
    _w, p = res
    assert p > 0.1


def test_wilcoxon_p_esta_sempre_em_zero_um():
    pares = [(2.0, 5.0)] * 8
    res = au._wilcoxon(pares)
    assert res is not None and 0.0 <= res[1] <= 1.0


# ── O limiar do protocolo ───────────────────────────────────────────────────────
def test_limiar_do_protocolo_esta_fixado_em_8():
    """Fixado ANTES de existirem dados. Se alguém o baixar depois de ver os resultados, isso
    é p-hacking — este teste torna a mudança visível num diff."""
    assert au.WILCOXON_MIN_N == 8
