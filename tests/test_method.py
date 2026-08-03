"""Os números da página do método têm de existir no ficheiro congelado que os produziu.

É este teste que impede a página de envelhecer em silêncio. Se alguém recorrer uma
avaliação e um valor mudar, isto parte — em vez de o produto continuar a afirmar, com toda
a confiança, um número que os documentos já não sustentam.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.method import (
    ALL_NUMBERS,
    ANOMALY,
    RETRIEVAL,
    TRIAGE,
    TRIAGE_BUDGET,
    TRIAGE_VERDICT,
    Number,
)
from app.verdict import PROIBIDO

RAIZ = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("num", ALL_NUMBERS, ids=lambda n: f"{n.value}-{Path(n.source).stem}")
def test_cada_numero_existe_no_ficheiro_congelado(num: Number) -> None:
    caminho = RAIZ / num.source
    assert caminho.exists(), f"a fonte de '{num.label}' não existe: {num.source}"
    texto = caminho.read_text(encoding="utf-8")
    assert num.value in texto, (
        f"'{num.value}' ({num.label}) já não aparece em {num.source} — "
        f"ou a avaliação foi recorrida, ou a página do método está desactualizada")


def test_nenhum_numero_e_inventado_sem_fonte() -> None:
    for num in ALL_NUMBERS:
        assert num.source.startswith("docs/evaluation/"), num.label
        assert num.value.strip(), num.label


def test_o_veredicto_da_triagem_continua_a_dizer_que_o_texto_perdeu() -> None:
    """A honestidade do resultado negativo é conteúdo, não uma ressalva a suavizar.

    Se alguém reescrever isto para soar melhor, este teste diz que não.
    """
    baixo = TRIAGE_VERDICT.lower()
    assert "no text model beat" in baixo
    assert "0.632" in TRIAGE_VERDICT and "0.163" in TRIAGE_VERDICT


def test_a_pagina_do_metodo_nao_preve_nada() -> None:
    """H2 vale aqui como em todo o lado — inclusive nos rótulos dos resultados."""
    alvo = " ".join([n.label + " " + n.note for n in ALL_NUMBERS] + [TRIAGE_VERDICT]).lower()
    for palavra in PROIBIDO:
        assert palavra not in alvo, f"'{palavra}' apareceu na página do método"


def test_a_volatilidade_continua_a_ganhar_a_todos_os_modelos_com_texto() -> None:
    """A ordem dos resultados é o resultado. Trocá-la seria inverter a conclusão da RQ4."""
    por_rotulo = {n.label: float(n.value) for n in TRIAGE}
    vol = por_rotulo["Volatility only (the simple baseline)"]
    for rotulo, valor in por_rotulo.items():
        if "text" in rotulo.lower():
            assert valor < vol, f"{rotulo} ({valor}) não pode bater a volatilidade ({vol})"


def test_a_recuperacao_semantica_bate_todas_as_baselines() -> None:
    por_rotulo = {n.label: float(n.value) for n in RETRIEVAL}
    minilm = por_rotulo["Semantic (MiniLM) — the model in this product"]
    for rotulo in ("Word overlap (lexical baseline)", "Most recent (recency baseline)",
                   "Random (chance)"):
        assert minilm > por_rotulo[rotulo], rotulo


def test_o_z_score_dispara_de_forma_muito_mais_consistente_do_que_o_limiar_fixo() -> None:
    amplitudes = {n.label: float(n.value) for n in ANOMALY}
    z = amplitudes["Rolling z-score — spread in firing rate across companies"]
    fixo = amplitudes["Fixed percentage threshold — same spread"]
    assert z < fixo / 10, "o argumento principal da RQ1 é a consistência da taxa de disparo"


def test_a_triagem_a_orcamento_fixo_ganha_ao_alertar_sempre() -> None:
    valores = [float(n.value) for n in TRIAGE_BUDGET]
    assert valores[0] > valores[1] * 3
