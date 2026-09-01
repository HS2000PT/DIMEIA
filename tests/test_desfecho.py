"""Testes do desfecho observado — o bloco que se anexa dias depois à mensagem original.

O que protegem, por ordem de importância:

1. **Nunca reescreve a afirmação original.** Reescrever depois de saber o resultado é a forma
   mais eficaz de um sistema parecer sempre certo.
2. **Só edita quando há informação nova.** Cada edição é uma notificação; uma edição vazia é a
   única maneira de esta funcionalidade incomodar quem a recebe.
3. **Nada de espaços reservados.** A primeira versão escrevia «+5d not yet available», e isso
   fazia o sistema concluir, no dia em que o valor chegasse, que a linha já existia — e não
   editar. Um espaço reservado que impede a informação de chegar é pior do que a sua ausência.
4. **O aviso de que não é causa nem previsão está sempre presente.**
"""

from __future__ import annotations

from datetime import date

import pytest

from investigator.explanation_engine import desfecho as D

ORIGINAL = ('📰 <b>News alert for TSLA (Tesla)</b> (2026-09-01)\n'
            '"Tesla recalls 12k vehicles"\n'
            'Right now: <b>+5.36%</b> today\n'
            '<i>Observed past outcomes after similar news, not a price prediction.</i>')


def _d(medidos: dict[int, float] | None = None):
    """Os três horizontes, com valor só nos que o teste diz terem sido medidos."""
    medidos = medidos or {}
    return [D.Desfecho(h, medidos.get(h)) for h in D.HORIZONTES]


# ── acrescenta, nunca reescreve ──────────────────────────────────────────────────────────

def test_o_texto_original_fica_intacto():
    novo = D.anotar(ORIGINAL, _d({1: 0.021}))
    assert novo.startswith(ORIGINAL)


def test_o_bloco_traz_sempre_o_aviso_de_que_nao_e_causa_nem_previsao():
    novo = D.anotar(ORIGINAL, _d({1: 0.021, 3: -0.004, 5: 0.011}))
    assert "not a claim that the alert caused it" in novo
    assert "none of it was knowable when the alert was sent" in novo


def test_sem_nada_medido_devolve_o_original_sem_tocar():
    assert D.anotar(ORIGINAL, _d()) == ORIGINAL
    assert D.anotacao(_d()) == ""


# ── progressivo e idempotente ────────────────────────────────────────────────────────────

def test_correr_duas_vezes_com_o_mesmo_nao_duplica():
    uma = D.anotar(ORIGINAL, _d({1: 0.021}))
    assert D.anotar(uma, _d({1: 0.021})) == uma
    assert uma.count(D.TITULO) == 1


def test_um_horizonte_novo_substitui_o_bloco_e_nao_o_soma():
    uma = D.anotar(ORIGINAL, _d({1: 0.021}))
    duas = D.anotar(uma, _d({1: 0.021, 3: -0.004}))
    assert duas.count(D.TITULO) == 1
    assert "+1d · +2.10%" in duas and "+3d · −0.40%" in duas
    assert duas.startswith(ORIGINAL)


def test_horizonte_por_medir_nao_aparece_como_espaco_reservado():
    """Esta é a regressão que custou a primeira versão: com «+5d not yet available» escrito, o
    sistema via a linha do quinto dia já presente e nunca a atualizava quando o valor chegava."""
    uma = D.anotar(ORIGINAL, _d({1: 0.021}))
    assert "+5d" not in uma
    assert D.precisa_de_edicao(uma, _d({1: 0.021, 5: 0.011})) is True


def test_so_edita_quando_ha_novidade():
    uma = D.anotar(ORIGINAL, _d({1: 0.021}))
    assert D.precisa_de_edicao(uma, _d({1: 0.021})) is False
    assert D.precisa_de_edicao(uma, _d({1: 0.021, 3: -0.004})) is True
    assert D.precisa_de_edicao(ORIGINAL, _d()) is False


def test_esta_anotado():
    assert D.esta_anotado(ORIGINAL) is False
    assert D.esta_anotado(D.anotar(ORIGINAL, _d({1: 0.01}))) is True


# ── formatação ───────────────────────────────────────────────────────────────────────────

def test_o_negativo_usa_o_menos_tipografico_para_alinhar():
    """Num telemóvel, «-0.40%» com hífen não alinha com «+0.40%»: o hífen é mais estreito."""
    assert D._pct(-0.004) == "−0.40%"
    assert D._pct(0.004) == "+0.40%"
    assert D._pct(0.0) == "+0.00%"


def test_os_horizontes_saem_por_ordem_mesmo_desordenados():
    texto = D.anotacao([D.Desfecho(5, 0.03), D.Desfecho(1, 0.01), D.Desfecho(3, 0.02)])
    assert texto.index("+1d") < texto.index("+3d") < texto.index("+5d")


# ── seleção das mensagens a anotar ───────────────────────────────────────────────────────

def _entrada(**kw):
    from investigator.alerts_history import HistoryEntry

    base = {"date": "2026-09-01", "ticker": "TSLA", "kind": "news", "text": ORIGINAL,
            "text_html": ORIGINAL, "message_id": 637}
    base.update(kw)
    return HistoryEntry(**base)


@pytest.fixture
def selecao():
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "anotar_desfechos", Path(__file__).resolve().parents[1] / "scripts" / "anotar_desfechos.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_so_alertas_de_noticia_com_mensagem_alcancavel(selecao):
    entradas = [
        _entrada(),                                  # entra
        _entrada(kind="summary"),                    # resumo diário não é um alerta
        _entrada(message_id=0),                      # anterior a guardarmos o message_id
        _entrada(date=""),                           # sem dia não há de onde medir
        _entrada(text_html=""),                      # sem o HTML exato, editar degradaria
    ]
    escolhidas = selecao.entradas_a_anotar(entradas, date(2026, 9, 3))
    assert len(escolhidas) == 1 and escolhidas[0].kind == "news"


def test_a_janela_fecha_e_o_futuro_nao_entra(selecao):
    entradas = [_entrada(date="2026-09-01"), _entrada(date="2026-08-10"),
                _entrada(date="2026-09-30")]
    escolhidas = selecao.entradas_a_anotar(entradas, date(2026, 9, 3))
    assert [e.date for e in escolhidas] == ["2026-09-01"]


def test_data_invalida_e_ignorada_sem_levantar(selecao):
    assert selecao.entradas_a_anotar([_entrada(date="ontem")], date(2026, 9, 3)) == []
