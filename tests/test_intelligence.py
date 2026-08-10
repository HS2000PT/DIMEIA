"""Testes da camada de inteligência — guarda de ancoragem, pacotes de evidência, analista.

**Todos offline.** Nenhum teste chama um LLM: injecta-se `complete_fn`. Um teste que depende
de um fornecedor externo mede a Internet, não o código, e falha por razões que não são defeitos.

Segue a regra que este projecto aprendeu à sua custa: **cada regra da guarda tem controlo nos
DOIS sentidos**. Um detector partido e um corpus limpo são indistinguíveis no ecrã, e um teste
que só verifica que a coisa proibida é rejeitada não distingue uma guarda que funciona de uma
guarda que rejeita tudo.

Metade destes testes são **exploits reproduzidos** por um red team de seis lentes adversárias
(114 ataques, 21 reproduzidos) contra a primeira versão da guarda. Ficam aqui como regressão
permanente, pela mesma razão que os 21 exploits do narrador ficaram: um furo fechado sem teste
volta a abrir na próxima alteração.
"""

from __future__ import annotations

import pytest

from investigator.intelligence.analyst import Plan, ask, route_with_rules
from investigator.intelligence.context import build_asset_bundle, build_market_bundle
from investigator.intelligence.guard import check_grounding, strip_anchors
from investigator.intelligence.report import (
    ASSET_SECTIONS,
    MARKET_SECTIONS,
    deterministic_report,
    generate_report,
)

ROW = {
    "ticker": "XOM", "move": 0.0447, "z": 2.65, "flagged": True,
    "rarity": {"count": 2, "n": 249, "move": 0.0437, "same_direction": 2},
    "decomp": {"market": 0.0002, "sector": 0.0337, "company": 0.0108, "driver": "sector"},
    "vol_ratio": 2.4,
}
ROWS = [
    ROW,
    {"ticker": "NVDA", "move": -0.0235, "z": -0.99, "flagged": False,
     "rarity": {"count": 72, "n": 249, "move": -0.0238, "same_direction": 35},
     "decomp": {"market": -0.001, "sector": -0.004, "company": -0.018, "driver": "company"}},
    {"ticker": "AAPL", "move": 0.0031, "z": 0.15, "flagged": False,
     "rarity": {"count": 202, "n": 249, "move": 0.0031, "same_direction": 100},
     "decomp": {"market": 0.003, "sector": -0.0005, "company": 0.0002, "driver": "market"}},
]
HEADS = [{"headline": "Exxon Mobil Earnings Expected to Grow", "source": "Zacks",
          "date": "2026-08-08", "published_at": "2026-08-08T12:00:00Z"}]
PRECS = [{"headline": "Oil majors rally on supply news", "date": "2026-05-02",
          "impact_pct": 1.84, "similarity": 0.61}]


def fid(bundle, kind: str, ticker: str | None = None) -> str:
    """O identificador de um facto, resolvido pelo TIPO e pelo activo.

    Fixar `f9` num teste foi um erro real cometido a escrever este ficheiro: a numeração muda
    com a composição do pacote, e um teste que cita o facto errado ou falha por engano ou —
    pior — passa por engano. O teste tem de pedir "o movimento da NVDA", não "o nono facto".
    """
    for f in bundle.facts:
        if f.kind == kind and (ticker is None or f.detail.get("ticker") == ticker):
            return f.fid
    raise AssertionError(f"sem facto {kind} para {ticker}")


@pytest.fixture
def market():
    return build_market_bundle(ROWS, "2026-08-10T17:00:00+00:00")


@pytest.fixture
def asset():
    return build_asset_bundle(ROW, "2026-08-10T17:00:00+00:00", headlines=HEADS,
                              precedents=PRECS, triage={"prob": 0.4, "contributions": []})


# ══ Pacote de evidência ══════════════════════════════════════════════════════

def test_factos_tem_identificador_unico_e_sequencial(market):
    ids = [f.fid for f in market.facts]
    assert ids == [f"f{i + 1}" for i in range(len(ids))]


def test_nenhum_facto_e_de_origem_gerada(market, asset):
    """O gerador não produz factos. Se um dia produzir, este teste parte primeiro."""
    for b in (market, asset):
        assert {f.origin for f in b.facts} <= {"measured", "computed", "model"}


def test_manchete_entra_no_pacote_entre_aspas(asset):
    """A fronteira entre o que a fonte disse e o que nós afirmamos é marcada com aspas."""
    h = next(f for f in asset.facts if f.kind == "headline")
    assert str(h.value).startswith('"') and str(h.value).endswith('"')


# ══ Guarda: números ligados ao facto citado ══════════════════════════════════

def test_numero_da_evidencia_passa(market):
    x = fid(market, "price_move", "XOM")
    assert check_grounding(f"XOM moved +4.47% [{x}].", market).ok


def test_numero_inventado_e_rejeitado(market):
    x = fid(market, "price_move", "XOM")
    r = check_grounding(f"XOM moved +9.99% [{x}].", market)
    assert not r.ok and "+9.99" in r.ungrounded_numbers


def test_sinal_invertido_e_rejeitado(market):
    """O dígito mais consequente é o sinal. -2.35 existe; +2.35 não."""
    n = fid(market, "price_move", "NVDA")
    assert check_grounding(f"NVDA moved -2.35% [{n}].", market).ok
    assert not check_grounding(f"NVDA moved +2.35% [{n}].", market).ok


def test_numero_de_outro_facto_e_rejeitado(market):
    """⚠️ O achado CRÍTICO do red team: citar um facto e usar o número de outro.

    Enquanto o conjunto numérico era global isto passava — dava para citar o volume da XOM e
    escrever o retorno da NVDA ao lado, com a citação a emprestar-lhe autoridade. É a
    diferença entre "este número existe algures" e "este número é deste facto".
    """
    vol = fid(market, "volume", "XOM")
    assert not check_grounding(f"NVDA moved -2.35% [{vol}].", market).ok


def test_retorno_restituido_como_zscore_e_rejeitado(market):
    """Tipos não são intermutáveis: +4.47 é um retorno, não um z-score."""
    z = fid(market, "zscore", "XOM")
    assert not check_grounding(f"XOM has a z-score of +4.47 [{z}].", market).ok


def test_arredondamento_nao_cunha_numeros(market):
    """2.65 a zero casas dava "3", e "3" passava a ser citável como se um motor o tivesse
    calculado. Tolerar formatação não pode custar inventar quantidades."""
    z = fid(market, "zscore", "XOM")
    assert not check_grounding(f"XOM has a z-score of 3 [{z}].", market).ok


def test_numero_por_extenso_e_verificado(market):
    """"up four percent" não tem dígitos e passava por baixo da verificação inteira."""
    x = fid(market, "price_move", "XOM")
    assert not check_grounding(f"XOM moved up four percent [{x}].", market).ok


def test_par_ordenado_invertido_e_rejeitado(market):
    """`2 up, 1 down` reescrito como `1 up, 2 down` usa dois números legítimos e inverte o
    veredicto do dia inteiro. Números soltos não sabem de que lado são."""
    b = fid(market, "breadth")
    assert check_grounding(f"Today 2 names were up and 1 down [{b}].", market).ok
    assert not check_grounding(f"Today 1 name was up and 2 down [{b}].", market).ok


def test_preco_fabricado_com_dois_pontos_e_rejeitado(market):
    """A máscara de horas era `\\d{1,2}:\\d{2}` sem contexto, e "at 92:50 per share" ficava
    invisível à verificação numérica."""
    x = fid(market, "price_move", "XOM")
    assert not check_grounding(f"XOM changed hands at 92:50 per share [{x}].", market).ok


# ══ Guarda: linguagem, com controlo nos dois sentidos ════════════════════════

@pytest.mark.parametrize("texto", [
    "XOM moved +4.47% [X] and is likely to rebound.",
    "XOM moved +4.47% [X]. Buy the stock now.",
    "XOM moved +4.47% [X] because of the news.",
    "The headline drove the move [X].",
    "XOM moved +4.47% [X]. Price targets suggest more.",
    "XOM moved +4.47% [X] and looks attractive here.",
    "XOM moved +4.47% [X]. Investors may wish to take profits.",
    "XOM moved +4.47% [X] in response to the announcement.",
    "XOM moved +4.47% [X]. The news triggered the move.",
    "XOM moved +4.47% [X] and every previous time this happened it continued.",
    "XOM moved +4.47% [X], a bullish signal.",
    "XOM moved +4.47% [X] and the news sent shares higher.",
])
def test_linguagem_proibida_e_rejeitada(market, texto):
    t = texto.replace("[X]", f"[{fid(market, 'price_move', 'XOM')}]")
    assert not check_grounding(t, market).ok, t


@pytest.mark.parametrize("texto", [
    "XOM moved +4.47% [X]. This contains no forecast.",
    "XOM moved +4.47% [X]. This is not advice.",
    "The headline coincided with the move [X].",
    "The headline was published shortly before the move [X]. Temporal proximity only.",
    "XOM moved +4.47% [X]. Measured history and computed statistics only.",
])
def test_linguagem_honesta_passa(market, texto):
    """⚠️ O CONTROLO QUE IMPORTA MAIS.

    A frase que este produto precisa de poder escrever — *"contains no forecast"* — é
    exactamente a que uma blocklist ingénua proíbe, porque contém a palavra que ela procura.
    Esta classe de defeito apareceu **quatro vezes** neste projecto. Sem este teste, a guarda
    podia ficar a rejeitar o texto mais honesto do sistema e ninguém dava por isso.
    """
    t = texto.replace("[X]", f"[{fid(market, 'price_move', 'XOM')}]")
    r = check_grounding(t, market)
    assert r.ok, (t, r.violations)


def test_ressalva_nao_desliga_a_blocklist(market):
    """⚠️ A janela de negação de 40 caracteres da primeira versão DESLIGAVA a blocklist:
    bastava pôr um "no" perto para qualquer previsão passar. Foi substituída por uma allowlist
    fechada de ressalvas — uma heurística de negação é superfície de ataque, não defesa."""
    x = fid(market, "price_move", "XOM")
    t = (f"This contains no forecast [{x}]. XOM will rise sharply.")
    assert not check_grounding(t, market).ok


# ══ Guarda: citações verbatim ════════════════════════════════════════════════

def test_manchete_citada_com_palavra_proibida_passa(asset):
    """Uma manchete real pode conter a previsão de um analista: é um facto sobre o mundo que o
    sistema captou, com fonte e carimbo. O que o sistema não pode é *fazer* a previsão com a
    sua própria voz."""
    hid = next(f.fid for f in asset.facts if f.kind == "headline")
    x = fid(asset, "price_move", "XOM")
    t = (f'XOM moved +4.47% [{x}]. The captured headline reads '
         f'"Exxon Mobil Earnings Expected to Grow" [{hid}].')
    r = check_grounding(t, asset)
    assert r.ok, r.violations


def test_previsao_inventada_entre_aspas_e_rejeitada(asset):
    """O contrário do teste anterior: aspas não isentam o que não é verbatim na evidência."""
    hid = next(f.fid for f in asset.facts if f.kind == "headline")
    x = fid(asset, "price_move", "XOM")
    t = (f'XOM moved +4.47% [{x}]. We note '
         f'"XOM is expected to rise 20% next week" [{hid}].')
    assert not check_grounding(t, asset).ok


# ══ Guarda: âncoras ══════════════════════════════════════════════════════════

def test_ancora_inexistente_e_rejeitada(market):
    r = check_grounding("XOM moved +4.47% [f999].", market)
    assert not r.ok and "f999" in r.unknown_anchors


def test_afirmacao_sem_ancora_e_rejeitada(market):
    t = "XOM moved sharply higher against its own recent trading range in today's session."
    assert not check_grounding(t, market).ok


def test_afirmacao_curta_sem_ancora_e_rejeitada(market):
    """O corte de 40 caracteres da primeira versão deixava passar afirmações curtas."""
    assert not check_grounding("XOM: +4.47%.", market).ok


def test_ressalva_sem_afirmacao_nao_precisa_de_ancora(market):
    """Um parágrafo que não afirma nada verificável não tem o que citar, e exigir-lhe uma
    âncora produziria citações decorativas — que ensinam o leitor a não clicar nelas."""
    t = "This report states measured history and computed statistics only."
    assert check_grounding(t, market).ok


# ══ O chão determinístico ════════════════════════════════════════════════════

@pytest.mark.parametrize("scope", ["market", "asset"])
def test_chao_deterministico_passa_a_propria_guarda(market, asset, scope):
    """Se o chão violasse a guarda, uma falha do LLM deixava o utilizador sem texto nenhum."""
    b = market if scope == "market" else asset
    secs = MARKET_SECTIONS if scope == "market" else ASSET_SECTIONS
    for s in deterministic_report(b, secs):
        r = check_grounding(s.text, b)
        assert r.ok, (s.title, r.violations)


def test_sem_llm_sai_o_chao(market):
    r = generate_report(market, complete_fn=lambda *a, **k: None)
    assert r.source == "deterministic" and not r.generated and r.sections


def test_llm_que_viola_e_substituido_seccao_a_seccao(market):
    """Rejeitar o relatório inteiro por uma frase deitaria fora sínteses boas por causa de uma
    má; aceitar tudo seria não ter guarda. A unidade de rejeição é a secção."""
    b = fid(market, "breadth")

    class R:
        text = (f"[SITUATION] Today 2 names were up and 1 down [{b}].\n"
                "[MOVEMENT] XOM will rise 40% next week.\n")
        provider, latency_s = "fake", 0.1

    r = generate_report(market, complete_fn=lambda *a, **k: R())
    assert r.guarded
    sit = next(s for s in r.sections if s.key == "situation")
    mov = next(s for s in r.sections if s.key == "movement")
    assert "2 names were up" in sit.text     # a boa sobreviveu
    assert "40%" not in mov.text             # a má foi substituída


def test_relatorio_nunca_rebenta_com_fornecedor_a_explodir(market):
    def boom(*a, **k):
        raise RuntimeError("provider down")
    r = generate_report(market, complete_fn=boom)
    assert r.sections and r.source == "deterministic"


# ══ Analista ═════════════════════════════════════════════════════════════════

TICKERS = ["XOM", "NVDA", "AAPL", "TSLA"]


def test_router_resolve_pronome_pelo_contexto():
    """"Porque é que subiu?" só tem sentido com o activo à frente."""
    assert route_with_rules("why did it move?", TICKERS, {"ticker": "NVDA"}).ticker == "NVDA"


def test_router_encontra_o_ticker_no_texto():
    assert route_with_rules("what about XOM today?", TICKERS, {}).ticker == "XOM"


def test_router_apanha_o_portao():
    p = route_with_rules("why was it quiet?", TICKERS, {"ticker": "AAPL"})
    assert "gate" in p.wants


def test_router_funciona_sem_llm():
    """A interface conversacional tem de funcionar com zero chaves de API — é uma restrição
    fundadora deste trabalho, não um detalhe de implantação."""
    p = route_with_rules("what stood out today?", TICKERS, {})
    assert p.routed_by == "rules" and p.wants


def test_resposta_sem_llm_e_ancorada(market):
    plan = Plan("market", None, ["move"], {"type": "none"}, "q", "rules")
    a = ask("what moved?", market, plan, complete_fn=lambda *x, **k: None)
    assert a.source == "deterministic" and a.anchors
    assert check_grounding(a.text, market).ok


def test_resposta_do_llm_que_viola_cai_no_chao(market):
    class R:
        text = "XOM is a great buy right now and will rise 30%."
        provider, latency_s = "fake", 0.2
    plan = Plan("market", None, ["move"], {"type": "none"}, "q", "llm")
    a = ask("should i buy?", market, plan, complete_fn=lambda *x, **k: R())
    assert a.guarded and a.source == "deterministic"
    assert "great buy" not in a.text


# ══ Utilitários ══════════════════════════════════════════════════════════════

def test_strip_anchors_limpa_para_canais_sem_interface():
    assert strip_anchors("XOM moved +4.47% [f5] today.") == "XOM moved +4.47% today."
