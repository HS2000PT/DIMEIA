"""Os critérios de escrita da v3, em forma executável. Puros: sem rede, sem Streamlit."""

from __future__ import annotations

import itertools

import pytest

from app.verdict import (
    FLAG_EXPLAINER,
    PROIBIDO,
    card_html,
    driver_sentence,
    gloss_z,
    precedent_framing,
    rarity_sentence,
    sparkline_svg,
    verdict,
)
from investigator.anomaly_detector.frequency import Exceedance
from investigator.correlation_engine.decomposition import VERDICT, VERDICT_SHORT


def _exc(count: int, n: int = 249, move: float = -0.05) -> Exceedance:
    return Exceedance(move=move, n=n, count=count, same_direction=count)


# ── raridade ─────────────────────────────────────────────────────────────────────────

def test_recorde_diz_recorde() -> None:
    assert rarity_sentence(_exc(0, 249, -0.076)) == "Its biggest fall in 249 trading days."
    assert rarity_sentence(_exc(0, 249, +0.14)) == "Its biggest move in 249 trading days."


@pytest.mark.parametrize(("count", "trecho"), [
    (1, "Only 1 of the last 249"), (5, "Only 5 of the last 249"),
    (6, "6 of the last 249"), (25, "25 of the last 249"),
])
def test_bandas_de_raridade(count: int, trecho: str) -> None:
    assert trecho in rarity_sentence(_exc(count))


def test_dia_banal_diz_banal() -> None:
    frase = rarity_sentence(_exc(203), "JPM")
    assert "ordinary day for JPM" in frase


def test_o_n_vem_dos_dados_e_nunca_e_250() -> None:
    """Uma série de 59 observações não pode dizer "250 dias" (critério V5)."""
    frase = rarity_sentence(_exc(3, n=58))
    assert "58 trading days" in frase
    assert "250" not in frase


def test_sem_dados_nao_inventa_frase() -> None:
    assert rarity_sentence(None) == ""


# ── motor do movimento ───────────────────────────────────────────────────────────────

def test_cala_se_quando_o_motor_e_a_empresa() -> None:
    """Repetir "foi específico da empresa" a seguir ao nome e ao número não acrescenta nada."""
    assert driver_sentence({"driver": "company", "fallback": False}) == ""


def test_fala_quando_surpreende() -> None:
    assert driver_sentence({"driver": "market", "fallback": False}) == VERDICT_SHORT["market"]
    assert driver_sentence({"driver": "sector", "fallback": False}) == VERDICT_SHORT["sector"]


def test_avisa_quando_o_beta_nao_foi_estimado() -> None:
    frase = driver_sentence({"driver": "market", "fallback": True})
    assert "indicative" in frase


def test_sem_decomposicao_nao_inventa() -> None:
    assert driver_sentence(None) == ""
    assert driver_sentence({}) == ""


# ── veredicto ────────────────────────────────────────────────────────────────────────

def test_dia_calmo_mostra_que_e_calmo_em_vez_de_o_afirmar() -> None:
    """Um rótulo pede confiança; uma contagem dispensa-a, e custa a mesma linha.

    Quem vê +3,23% ao lado da palavra "Quiet" não tem razão para acreditar. Quem vê
    "203 dos últimos 249 dias moveram-se tanto ou mais" acredita sem confiar em nós.
    """
    frase = verdict("Apple", _exc(203), None, flagged=False)
    assert "Quiet" in frase
    assert "203 of the last 249" in frase


def test_dia_calmo_sem_historia_ainda_diz_alguma_coisa() -> None:
    frase = verdict("Apple", None, None, flagged=False)
    assert "Quiet" in frase and "Apple" in frase


def test_veredicto_nao_contem_nenhum_numero_tecnico() -> None:
    """A lei de desenho: nenhum número aparece antes da frase que ele sustenta."""
    frase = verdict("NVIDIA", _exc(0, 249, -0.076),
                    {"driver": "market", "fallback": False}, flagged=True)
    assert "z " not in frase
    assert "%" not in frase
    assert frase.startswith("Its biggest fall")


def test_sessao_aberta_e_dita() -> None:
    frase = verdict("Tesla", _exc(2), {"driver": "company"}, flagged=True, market_open=True)
    assert "session is not over" in frase


def test_sem_raridade_ainda_ha_veredicto() -> None:
    """Falta de história não pode deixar o cartão mudo."""
    frase = verdict("AMD", None, None, flagged=True)
    assert "AMD" in frase and frase.strip()


# ── H2: zero previsões, varrido sobre combinações ────────────────────────────────────

def test_nenhuma_combinacao_produz_vocabulario_de_previsao() -> None:
    """Varre o espaço de frases em vez de inspeccionar uma captura de ecrã.

    É isto que um módulo puro compra: a proibição de prever passa de coisa que se confere
    a olho para coisa que se verifica sobre centenas de casos.
    """
    contagens = [0, 1, 5, 6, 25, 26, 203]
    motores = [None, {"driver": "market", "fallback": False},
               {"driver": "sector", "fallback": True},
               {"driver": "company", "fallback": False}]
    combinacoes = itertools.product(contagens, motores, [True, False], [True, False])
    for count, decomp, flagged, aberto in combinacoes:
        frase = verdict("NVIDIA", _exc(count), decomp, flagged, aberto).lower()
        for palavra in PROIBIDO:
            assert palavra not in frase, f"'{palavra}' apareceu em: {frase}"


def test_o_mapa_longo_tambem_esta_limpo() -> None:
    for frase in list(VERDICT.values()) + list(VERDICT_SHORT.values()):
        for palavra in PROIBIDO:
            assert palavra not in frase.lower()


# ── glosa do z (V4) ──────────────────────────────────────────────────────────────────

def test_o_z_nunca_aparece_nu() -> None:
    texto = gloss_z(-3.41)
    assert "-3.41" in texto
    assert texto.endswith("vs 20-day norm")


def test_o_z_positivo_leva_sinal() -> None:
    assert gloss_z(1.13).startswith("z +1.13")


# ── cartão: a lei de ordenação, em forma executável ──────────────────────────────────

def _cartao(flagged: bool = True, chips: list[str] | None = None) -> str:
    return card_html(
        ticker="NVDA", name="NVIDIA", move=-0.0764, icone="▼", cor="#FF5A5F",
        frase="Its biggest fall in 249 trading days.", flagged=flagged,
        chips=chips if chips is not None else ["z -3.41 vs 20-day norm", "3.3x usual volume"],
        spark=sparkline_svg([1, 2, 3, 2.5], "#FF5A5F") if flagged else "")


def test_v2_o_veredicto_vem_antes_de_qualquer_numero_tecnico() -> None:
    """A percentagem do dia pode vir antes — é o facto que a frase explica, não jargão.

    O que tem de vir depois é o z-score e o rácio de volume, que foi a queixa real
    ("não sei o que os números querem dizer"). Ver §6.3.1 do documento de critérios.
    """
    html = _cartao()
    assert html.index('class="verdict"') < html.index("z -3.41")
    assert html.index('class="verdict"') < html.index("3.3x usual volume")


def test_o_cartao_tem_exactamente_um_veredicto() -> None:
    assert _cartao().count('class="verdict"') == 1


def test_a_ligacao_e_profunda_e_abre_na_mesma_janela() -> None:
    html = _cartao()
    assert 'href="?t=NVDA"' in html
    assert 'target="_self"' in html


def test_cartao_calmo_e_mais_vazio_nao_mais_pequeno() -> None:
    """O vazio é o sinal: sem sparkline, sem chips, sem pílula."""
    html = _cartao(flagged=False)
    assert "card--quiet" in html
    assert "<svg" not in html
    assert "chips" not in html
    assert "UNUSUAL" not in html


def test_cartao_sinalizado_tem_a_palavra_e_nao_so_a_cor() -> None:
    """Critério V3: quatro canais redundantes, nunca só cor."""
    html = _cartao()
    assert "UNUSUAL" in html
    assert "card--flagged" in html
    assert "<svg" in html


def test_chips_so_aparecem_quando_ha_algo_a_dizer() -> None:
    assert "chips" not in _cartao(chips=[])


def test_a_pilula_saiu_da_linha_do_nome() -> None:
    """A1: `UNUSUAL` já não disputa a linha do topo com o nome da empresa.

    Verificado por posição e não a olho: a pílula tem de vir **depois** do número grande,
    que é o último elemento da linha do topo. Enquanto estava lá dentro, o nome era o
    único item sem largura própria e portanto o único que cedia — "JPMorgan Chase"
    truncava para a palavra caber.
    """
    html = _cartao()
    assert html.index("card-state") > html.index("card-move")
    assert html.index("card-state") < html.index('class="verdict"')


def test_cartao_calmo_nao_tem_linha_de_estado() -> None:
    """Num dia calmo não há pílula nem a linha que a segura: o vazio é o sinal."""
    assert "card-state" not in _cartao(flagged=False)


# ── B: a resposta a "o que é isto?" ──────────────────────────────────────────────────

def test_a_explicacao_lidera_pela_consequencia_nao_pela_estatistica() -> None:
    """A queixa era que a explicação explicava o mecanismo a quem perguntou o significado.

    A versão anterior abria com "1,5 desvios-padrão numa janela de 20 dias". Estes
    asserts fixam a inversão: a primeira frase diz o que significa, e o vocabulário da
    estatística não aparece de todo.
    """
    assert FLAG_EXPLAINER.startswith("Flagged means")
    for jargao in ("standard deviation", "z-score", "z score", "threshold", "window"):
        assert jargao not in FLAG_EXPLAINER.lower(), jargao


def test_a_explicacao_diz_que_cada_empresa_e_julgada_contra_si_propria() -> None:
    """Sem esta metade, 3% da Apple e 3% da Tesla parecem o mesmo caso julgado ao contrário."""
    assert "against itself" in FLAG_EXPLAINER
    assert "3%" in FLAG_EXPLAINER


def test_a_explicacao_nao_promete_nada_sobre_o_futuro() -> None:
    """H2 aplica-se a todo o texto de produto, não só aos veredictos dos cartões."""
    for palavra in PROIBIDO:
        assert palavra not in FLAG_EXPLAINER.lower(), palavra


# ── H3: a moldura tema ≠ direcção dos precedentes ────────────────────────────────────

def test_direccoes_mistas_mostram_a_reparticao_e_nao_uma_media() -> None:
    """Uma média sobre casos que foram a +4% e a −8% descreve um valor que nunca aconteceu."""
    frase = precedent_framing(up=2, down=3)
    assert "both directions" in frase
    assert "2 up, 3 down" in frase
    assert "not in direction" in frase


def test_direccao_unanime_continua_a_dizer_que_nao_fala_deste_caso() -> None:
    """O caso do CS3: unanimidade no passado não é uma afirmação sobre o presente."""
    for frase in (precedent_framing(up=4, down=0), precedent_framing(up=0, down=4)):
        assert "topic-similar" in frase
        assert "not a statement about this one" in frase


def test_sem_desfechos_medidos_nao_se_inventa_uma_direccao() -> None:
    """Casos recentes demais para o horizonte ter fechado não são "sem movimento"."""
    frase = precedent_framing(0, 0)
    assert "measured outcome" in frase
    assert "moved" not in frase


def test_a_moldura_nunca_e_vazia() -> None:
    """H3 torna-a obrigatória: não pode haver combinação que devolva ""."""
    for up in range(4):
        for down in range(4):
            assert precedent_framing(up, down).strip()


def test_a_moldura_nunca_preve() -> None:
    for up in range(5):
        for down in range(5):
            frase = precedent_framing(up, down).lower()
            for palavra in PROIBIDO:
                assert palavra not in frase, f"'{palavra}' em: {frase}"


# ── sparkline ────────────────────────────────────────────────────────────────────────

def test_serie_plana_nao_divide_por_zero() -> None:
    svg = sparkline_svg([100.0] * 20, "#00D68F")
    assert svg.startswith("<svg") and "nan" not in svg.lower()


def test_serie_curta_nao_desenha_nada() -> None:
    assert sparkline_svg([1.0], "#00D68F") == ""
    assert sparkline_svg([], "#00D68F") == ""


def test_nan_nao_entram_no_traco() -> None:
    svg = sparkline_svg([1.0, float("nan"), 3.0], "#00D68F")
    assert "nan" not in svg.lower()
    # O NaN sai, sobram dois pontos. Cada ponto é "x,y", logo duas vírgulas — não uma.
    pontos = svg.split('points="')[1].split('"')[0].split()
    assert len(pontos) == 2
