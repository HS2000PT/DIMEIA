"""Testes das vistas da v4 — os critérios de aceitação em forma executável."""

from __future__ import annotations

import itertools

from app.v4_views import (
    contem_previsao,
    explicar_silencio,
    linhas_decomposicao,
    moldura_precedentes,
    rotulo_atribuicao,
    rotulo_raridade,
)


def test_raridade_e_contagem_e_nunca_probabilidade():
    assert rotulo_raridade(52, 250) == "52 of the last 250 trading days moved this much or more."
    assert "Only 1" in rotulo_raridade(1, 249)
    assert "No other day" in rotulo_raridade(0, 249)
    assert "Not enough history" in rotulo_raridade(None, None)
    for c, n in ((0, 249), (1, 249), (52, 250), (240, 249)):
        frase = rotulo_raridade(c, n)
        assert "%" not in frase and "probab" not in frase.lower()


def test_motor_e_a_maior_do_MESMO_SINAL_nao_a_maior_em_modulo():
    """O caso NVDA medido: +0,25% no total com o setor a −1,54%."""
    d = {"market": 0.0038, "sector": -0.0154, "company": 0.0141, "driver": "company"}
    frase = rotulo_atribuicao(d, move=0.0025)
    assert "the company itself" in frase, "o setor puxou ao contrário; dizer 'foi o setor' é falso"
    assert "pulled the other way" in frase, "a componente contrária tem de ser dita, não escondida"


def test_atribuicao_ausente_diz_que_esta_ausente():
    assert "unavailable" in rotulo_atribuicao(None, 0.01)


def test_as_tres_componentes_somam_ao_movimento():
    d = {"market": -0.0166, "sector": -0.0037, "company": 0.0019, "driver": "market"}
    linhas = linhas_decomposicao(d, move=-0.0184)
    assert len(linhas) == 3
    assert abs(sum(v for _, v, _ in linhas) - (-0.0184)) < 1e-9
    assert sum(1 for _, _, motor in linhas if motor) == 1


def test_H2_varrimento_sobre_TODAS_as_frases_que_o_produto_sabe_produzir():
    """Não um exemplo: o produto cartesiano dos estados possíveis."""
    frases = []
    for c, n in itertools.product((None, 0, 1, 2, 52, 172, 249), (None, 60, 249, 250)):
        frases.append(rotulo_raridade(c, n))
    # cada motor x cada sinal do total x com e sem componente a puxar ao contrário
    for motor in ("market", "sector", "company"):
        for sinal in (0.02, -0.02):
            for contra in (True, False):
                d = {"market": 0.01, "sector": -0.005 if contra else 0.004,
                     "company": 0.002, "driver": motor}
                frases.append(rotulo_atribuicao(d, sinal))
    frases.append(rotulo_atribuicao(None, 0.01))
    for u, dn in itertools.product(range(5), range(5)):
        frases.append(moldura_precedentes(u, dn))
    for g in ("no_news", "none_relevant", "stale", "weak_precedent", "triage_suppressed",
              "error", "alerted", "desconhecido"):
        for det in ("", "best match 0.42 < floor 0.45", "P=0.31 < gate 0.50"):
            frases.extend(explicar_silencio(g, det))
    assert len(frases) > 100, "o varrimento tem de ser largo, não simbólico"
    maus = [f for f in frases if contem_previsao(f)]
    assert not maus, f"linguagem de previsão: {maus}"


def test_moldura_de_precedentes_diz_sempre_tema_diferente_de_direccao():
    for u, d in ((3, 0), (0, 3), (2, 1)):
        m = moldura_precedentes(u, d)
        assert "not similar in direction" in m
    assert "No comparable past cases" in moldura_precedentes(0, 0)


def test_precedentes_todos_no_mesmo_sentido_nao_viram_previsao():
    """O caso que o próprio aluno leu como incoerência."""
    m = moldura_precedentes(0, 3)
    assert "not a forecast" in m
    assert not contem_previsao(m)


def test_silencio_diz_a_margem_que_faltou():
    titulo, texto = explicar_silencio("weak_precedent", "best match 0.42 < floor 0.45")
    assert "No close precedent" in titulo
    assert "0.42" in texto and "0.45" in texto, "a margem é o que torna isto verificável"


def test_gate_desconhecido_nao_rebenta_nem_inventa():
    titulo, texto = explicar_silencio("um_gate_que_nao_existe")
    assert titulo and texto and not contem_previsao(texto)


def test_a_mascara_de_H2_reconhece_negacoes_mas_NAO_e_cega():
    """Controlo nos dois sentidos: sem isto, um detector partido e um corpus limpo
    são indistinguíveis no ecrã.

    É a 3.ª vez que esta classe de defeito aparece no projecto — o red team do narrador,
    o 'price target' dentro de 'No price targets', e agora o 'not a forecast' da própria
    moldura de honestidade.
    """
    # NEGADAS: são exactamente as frases honestas do produto, e têm de passar.
    for ok in ("an observed pattern, not a forecast",
               "No price targets are shown",
               "this is never predicted",
               "measured outcomes rather than a projection",
               "the system does not forecast prices"):
        assert not contem_previsao(ok), f"falso positivo: {ok!r}"

    # AFIRMADAS: têm de disparar. Se este bloco passar em silêncio, a máscara está morta.
    for mau in ("the price target is 240",
                "we expect the stock to recover",
                "this forecast suggests upside",
                "shares are poised to rise",
                "our projection for the quarter"):
        assert contem_previsao(mau), f"falso negativo: {mau!r}"
