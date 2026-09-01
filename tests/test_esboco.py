"""Testes do alerta em dois tempos — o esboço que sai primeiro e a análise que o substitui.

A propriedade que importa acima de todas: **o cabeçalho é byte a byte o mesmo nos dois**. Se
mudasse, quem já tivesse lido o esboço veria o facto alterar-se debaixo dos olhos na edição, e
um sistema cuja tese é «a afirmação vem com a evidência anexada» não pode ter a afirmação a
mudar de forma entre o primeiro e o segundo segundo.
"""

from __future__ import annotations

import pytest

from investigator.explanation_engine.explainer import (
    AVISO_CURTO,
    ESTADO_A_INVESTIGAR,
    _cabecalho_noticia,
    esboco_news_impact,
    explain_news_impact,
)

ARGS = dict(ticker="TSLA", headline="Tesla recalls 12k vehicles", date="2026-09-01",
            move=0.0536, move_note="12 of the last 249 trading days moved this much or more",
            source="Reuters", url="https://example.com/a")


def test_o_esboco_e_o_completo_partilham_o_cabecalho_exato():
    cab = _cabecalho_noticia(ARGS["ticker"], ARGS["headline"], ARGS["date"], ARGS["move"],
                             ARGS["move_note"], ARGS["source"], ARGS["url"])
    assert esboco_news_impact(**ARGS).startswith(cab)
    assert explain_news_impact(precedents=[], **ARGS).startswith(cab)


def test_o_esboco_traz_o_facto_todo_que_ja_se_sabe():
    e = esboco_news_impact(**ARGS)
    for esperado in ("TSLA", "Tesla recalls 12k vehicles", "+5.36%", "Reuters",
                     "https://example.com/a", "2026-09-01"):
        assert esperado in e


def test_o_esboco_diz_que_esta_a_investigar():
    assert ESTADO_A_INVESTIGAR in esboco_news_impact(**ARGS)


def test_o_esboco_leva_a_advertencia_desde_o_primeiro_segundo():
    """Uma mensagem que sai sem a advertência, mesmo por oito segundos, é uma mensagem que saiu
    sem a advertência. É a única posição ética que este trabalho assume em voz alta."""
    assert AVISO_CURTO in esboco_news_impact(**ARGS)


def test_o_esboco_nao_promete_direcao():
    """Procura AFIRMAÇÕES preditivas, não a palavra «prediction» — que aparece, e aparece
    negada: «never a price prediction». Um varrimento por substrings castigaria exatamente a
    frase que existe para impedir o problema."""
    e = esboco_news_impact(**ARGS).lower()
    for proibida in ("will rise", "will fall", "we expect", "forecast", "price target",
                     "should rise", "should fall", "buy ", "sell "):
        assert proibida not in e, f"o esboço não pode conter {proibida!r}"
    assert "never a price prediction" in e


def test_o_esboco_nao_afirma_precedentes_que_ainda_nao_procurou():
    """Dizer «sem casos semelhantes» seria afirmar que se procurou. Ainda não se procurou — e
    confundir «não há» com «não vimos» é exatamente o silêncio que este trabalho recusa."""
    e = esboco_news_impact(**ARGS)
    assert "No similar historical precedents" not in e
    assert "similar past headlines" not in e
    assert "comparable past cases" in e  # a pergunta em aberto, e não a afirmação


@pytest.mark.parametrize("faltam", [
    {"source": "", "url": ""},
    {"move": None, "move_note": None},
    {"date": ""},
])
def test_o_esboco_aguenta_campos_em_falta(faltam):
    args = {**ARGS, **faltam}
    e = esboco_news_impact(**args)
    assert e.startswith("📰 <b>News alert for TSLA")
    assert ESTADO_A_INVESTIGAR in e and AVISO_CURTO in e


def test_a_edicao_nao_encolhe_a_mensagem():
    """A análise substitui o esboço, e tem de acrescentar. Se o completo fosse mais curto do
    que o esboço, alguma coisa se teria perdido no caminho."""
    from investigator.historical_kb.record import NewsRecord

    prec = [(NewsRecord(ticker="NVDA", date="2025-03-04", headline="Chip recall widens",
                        impacts={"3": 0.012}), 0.71)]
    completo = explain_news_impact(precedents=prec, **ARGS)
    assert len(completo) > len(esboco_news_impact(**ARGS))
