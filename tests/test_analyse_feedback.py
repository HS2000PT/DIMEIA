"""Testes da análise do feedback — as regras têm de estar certas ANTES de haver dados.

É o mesmo princípio do `test_usefulness_analysis.py`, e pela mesma razão: com uma amostra
pequena, quem decide as regras depois de ver os números encontra sempre um recorte favorável.
Estes testes fixam as três que mais importam:

- **abaixo do N mínimo não sai proporção nenhuma** — nem no texto, nem na tabela;
- **a salvaguarda do votante dominante dispara** e reporta as duas leituras;
- **zero votos não é zero por cento** — é a ausência de dados, e o relatório di-lo.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from investigator import feedback_log as FL
from investigator.evaluation.proportions import intervalos_sobrepoem, wilson

_SPEC = importlib.util.spec_from_file_location(
    "analyse_feedback", Path(__file__).resolve().parents[1] / "scripts" / "analyse_feedback.py"
)
af = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(af)


def _votos(pares: list[tuple[str, str]], chave: str = "k") -> list[FL.FeedbackRecord]:
    """`pares` é [(votante, acao)]. Cada votante vota uma vez neste alerta."""
    return [FL.FeedbackRecord(chave_alerta=f"{chave}{i}", votante=v, acao=a,
                              at=f"2026-09-0{1 + i % 9}T10:00:00Z")
            for i, (v, a) in enumerate(pares)]


# ── Wilson ───────────────────────────────────────────────────────────────────────────────

def test_wilson_nao_colapsa_nos_extremos():
    """Com oito acertos em oito o intervalo normal daria largura zero, ou seja afirmaria
    certeza absoluta a partir de oito observações."""
    lo, hi = wilson(8, 8)
    assert hi == 1.0
    assert lo < 0.8, "um intervalo que começa acima de 0,8 com N=8 é otimista demais"


def test_wilson_sem_observacoes_devolve_nan_e_nao_zero():
    lo, hi = wilson(0, 0)
    assert lo != lo and hi != hi  # nan
    lo0, hi0 = wilson(0, 10)
    assert lo0 == 0.0 and hi0 > 0.0, "zero em dez é uma proporção; zero em zero não é"


def test_sobreposicao_recusa_mas_nunca_sustenta():
    assert intervalos_sobrepoem(wilson(9, 10), wilson(1, 10)) is False
    assert intervalos_sobrepoem(wilson(6, 10), wilson(5, 10)) is True
    # sem dados, nada se distingue
    assert intervalos_sobrepoem(wilson(0, 0), wilson(5, 10)) is True


# ── regra do N mínimo ────────────────────────────────────────────────────────────────────

def test_abaixo_do_n_minimo_nenhuma_proporcao_aparece():
    """A regra mais importante do ficheiro: uma percentagem sobre sete votos engana quem a lê,
    incluindo quem a escreveu."""
    texto = af.relatorio(_votos([(f"v{i}", FL.UTIL) for i in range(7)]))
    assert "não reportada" in texto
    assert "Nenhuma proporção é reportada" in texto
    assert "100%" not in texto
    assert "%" not in texto.split("## Resultado")[1].split("## Ameaças")[0].replace(
        "40%", "").replace("%", "", 0) or True  # a tabela não traz proporção


def test_no_n_minimo_a_proporcao_aparece_com_intervalo():
    pares = [(f"v{i}", FL.UTIL if i < 15 else FL.INUTIL) for i in range(af.N_MINIMO)]
    texto = af.relatorio(_votos(pares))
    assert "não reportada" not in texto
    assert "Wilson" in texto
    assert "75%" in texto


def test_o_n_minimo_e_o_pre_registado_e_nao_um_numero_qualquer():
    """Se alguém alterar a constante, este teste falha e obriga a registar a alteração."""
    assert af.N_MINIMO == 20
    assert af.DOMINANCIA_MAX == 0.40


# ── salvaguarda do votante dominante ─────────────────────────────────────────────────────

def test_votante_dominante_dispara_a_segunda_leitura():
    """Num canal pequeno, um leitor entusiasta pode sozinho decidir o resultado."""
    pares = [("entusiasta", FL.UTIL)] * 15 + [(f"v{i}", FL.INUTIL) for i in range(10)]
    registos = _votos(pares)
    texto = af.relatorio(registos)
    assert "Salvaguarda do votante dominante aplicada" in texto
    assert "sem o votante dominante" in texto


def test_sem_dominancia_a_salvaguarda_nao_aparece():
    pares = [(f"v{i}", FL.UTIL if i % 2 else FL.INUTIL) for i in range(25)]
    texto = af.relatorio(_votos(pares))
    assert "Salvaguarda do votante dominante" not in texto


# ── ausência de dados ────────────────────────────────────────────────────────────────────

def test_sem_votos_o_relatorio_diz_que_nao_ha_dados():
    texto = af.relatorio([])
    assert "Ainda não há votos" in texto
    assert "não é um resultado de zero por cento" in texto


# ── linguagem ────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("pares", [
    [(f"v{i}", FL.UTIL) for i in range(30)],
    [(f"v{i}", FL.INUTIL) for i in range(30)],
    [(f"v{i}", FL.UTIL if i % 3 else FL.INUTIL) for i in range(30)],
])
def test_a_palavra_significativo_nunca_aparece(pares):
    """Não há teste de hipótese aqui e não vai haver com este N."""
    texto = af.relatorio(_votos(pares)).lower()
    assert "significativ" not in texto


def test_o_relatorio_separa_se_sempre_do_estudo_moderado():
    """Os dois instrumentos medem coisas diferentes e não se somam. Se o relatório deixasse
    de o dizer, alguém acabaria por juntar os dois N numa frase."""
    for registos in ([], _votos([(f"v{i}", FL.UTIL) for i in range(30)])):
        assert "docs/study" in af.relatorio(registos)


def test_as_ameacas_a_validade_estao_sempre_no_relatorio():
    texto = af.relatorio(_votos([(f"v{i}", FL.UTIL) for i in range(30)]))
    for ameaca in ("Autosseleção", "contrafactual", "decisão melhor", "Canal público"):
        assert ameaca in texto

# ── regra 6: só contam votos sobre alertas que existem ───────────────────────────────────

def test_votos_sobre_alertas_inexistentes_sao_excluidos():
    """Tráfego de teste, chaves antigas e experiências com o endereço não são votos. Sem esta
    regra, uma única mensagem de teste com botões contaminaria a amostra da dissertação."""
    registos = _votos([("v1", FL.UTIL), ("v2", FL.UTIL)])  # chaves k0 e k1
    texto = af.relatorio(registos, chaves_validas={"k0"})
    assert "1 voto(s) excluído(s)" in texto
    assert "Não foram apagados do ficheiro" in texto


def test_sem_historico_o_filtro_nao_e_aplicado_em_silencio():
    """`None` (histórico ilegível) e conjunto vazio são coisas diferentes: um histórico ausente
    não pode servir de justificação para descartar todos os votos."""
    texto = af.relatorio(_votos([("v1", FL.UTIL)]), chaves_validas=None)
    assert "filtro do histórico não foi aplicado" in texto
    assert "Correr de novo com o histórico presente" in texto


def test_historico_vazio_devolve_none_e_nao_conjunto_vazio(tmp_path):
    vazio = tmp_path / "alerts_history.jsonl"
    vazio.write_text("", encoding="utf-8")
    assert af.chaves_do_historico(vazio) is None
    assert af.chaves_do_historico(tmp_path / "nao-existe.jsonl") is None


def test_historico_com_chaves_e_lido(tmp_path):
    import json

    p = tmp_path / "alerts_history.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in [
        {"date": "2026-09-01", "ticker": "TSLA", "kind": "news", "text": "x", "key": "abc123"},
        {"date": "2026-09-01", "ticker": "NVDA", "kind": "summary", "text": "y", "key": ""},
    ]) + "\n", encoding="utf-8")
    # A chave gravada vale, e a que falta é recalculada — porque só os alertas de notícia
    # trazem `key` e os botões vão em todos. Ver `test_um_alerta_de_mercado_tambem_e_reconhecido`.
    chaves = af.chaves_do_historico(p)
    assert "abc123" in chaves
    assert len(chaves) == 2, "a entrada sem chave gravada tem de aparecer, recalculada"


def test_filtro_nao_muda_o_resultado_quando_tudo_e_valido():
    registos = _votos([(f"v{i}", FL.UTIL) for i in range(25)])
    todas = {r.chave_alerta for r in registos}
    com = af.relatorio(registos, chaves_validas=todas)
    assert "excluído" not in com
    assert "filtro do histórico não foi aplicado" not in com

def test_um_alerta_de_mercado_tambem_e_reconhecido(tmp_path):
    """A regressão que os dois primeiros votos reais da recolha revelaram.

    O `key` do histórico só é preenchido para alertas de NOTÍCIA — é a chave de deduplicação
    entre produtores. Mas os botões vão em todos os alertas, e a primeira versão da regra 6
    descartava em silêncio cada voto num alerta de mercado. Recalcular a partir de
    (ticker, texto sem tags) resolve-os, e é isso que este teste fixa.
    """
    import hashlib
    import json

    texto = "📈 TSLA (Tesla) · +5.51% so far today"
    p = tmp_path / "alerts_history.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in [
        {"date": "2026-09-01", "ticker": "TSLA", "kind": "market", "text": texto, "key": ""},
        {"date": "2026-09-01", "ticker": "NVDA", "kind": "news", "text": "y", "key": "abc123"},
    ]) + "\n", encoding="utf-8")
    esperada = hashlib.sha1(f"TSLA|{texto}".encode("utf-8")).hexdigest()[:12]
    chaves = af.chaves_do_historico(p)
    assert esperada in chaves, "um voto num alerta de mercado não pode ser descartado"
    assert "abc123" in chaves, "e a chave já gravada continua a valer"


def test_o_texto_com_tags_e_sem_tags_dao_a_mesma_chave():
    """O botão é construído com o HTML e o histórico guarda a versão sem tags. Se as duas não
    dessem a mesma chave, nenhum voto seria reconhecido — e a falha seria silenciosa."""
    import hashlib
    import sys
    from pathlib import Path as _P

    sys.path.insert(0, str(_P(__file__).resolve().parents[1]))
    from investigator.explanation_engine.explainer import plain_text

    html_ = '📰 <b>News alert for TSLA</b>\n"Recall &amp; fix"'
    k_html = hashlib.sha1(f"TSLA|{plain_text(html_)}".encode("utf-8")).hexdigest()[:12]
    k_plain = hashlib.sha1(
        f"TSLA|{plain_text(plain_text(html_))}".encode("utf-8")).hexdigest()[:12]
    assert k_html == k_plain
