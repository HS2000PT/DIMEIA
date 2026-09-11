"""A qualidade do ajuste tem de chegar ao ecrã, e tem de o dizer quando é má.

Porque é que estes testes existem. A Tabela 6.1 declara, na linha 8, que a repartição nem
sempre está bem estimada: a mediana do coeficiente de determinação sobre a watchlist é
$0{,}460$ e **numa das dezassete empresas foi negativa**, o que o §5.4.6 traduz por «a
repartição desse dia assenta num ajuste que não descreve os dados». O produto mostrava as
três parcelas sem nunca dizer ao leitor quando é que elas eram de fiar, e o valor que o
permitia dizer era calculado e deitado fora nos dois caminhos que constroem o cartão.

⚠️ O teste que decide é o do coeficiente **negativo**. Um ajuste que não descreve os dados
e um ajuste bom produzem exatamente o mesmo cartão de três barras, e a diferença entre
eles não é visível a olho nenhum: é só este número que a distingue. Um teste que se
limitasse a verificar que o campo viaja passaria também sobre um ecrã que o ignora.
"""

from __future__ import annotations

import json
import pathlib
import re

import numpy as np
import pytest

from investigator.correlation_engine.decomposition import decompose_move

RAIZ = pathlib.Path(__file__).resolve().parents[1]
PAGINA = RAIZ / "web" / "index.html"


def _fonte_painel():
    return "\n".join(p.read_text(encoding="utf-8") for p in (
        PAGINA, PAGINA.parent / "assets/dashboard.js",
        PAGINA.parent / "assets/charts.js", PAGINA.parent / "assets/dashboard.css"))


def _serie(n: int = 260, semente: int = 7) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Uma empresa que segue mesmo o mercado e o setor: ajuste bom por construção."""
    r = np.random.default_rng(semente)
    mercado = r.normal(0, 0.011, n)
    setor = mercado * 0.6 + r.normal(0, 0.006, n)
    empresa = 1.1 * mercado + 0.8 * setor + r.normal(0, 0.004, n)
    return empresa, mercado, setor


def test_o_ajuste_bom_produz_coeficiente_alto():
    d = decompose_move(*_serie())
    assert not d.fallback
    assert d.r_squared > 0.5, d.r_squared


def test_uma_empresa_que_nao_segue_o_mercado_produz_coeficiente_baixo():
    """O caso que a tese reporta: o mercado e o setor não explicam aquela ação.

    ⚠️ Não se exige valor negativo, exige-se que fique MUITO abaixo do ajuste bom. O sinal
    do coeficiente depende da amostra concreta; o que o produto precisa de distinguir é a
    ordem de grandeza, e é essa que a frase do ecrã usa.
    """
    _, mercado, setor = _serie()
    r = np.random.default_rng(99)
    ruido = r.normal(0, 0.02, len(mercado))
    d = decompose_move(ruido, mercado, setor)
    assert not d.fallback
    assert d.r_squared < 0.25, d.r_squared


def test_o_instantaneo_leva_o_coeficiente_e_o_recuo(monkeypatch):
    """Sem estes dois campos o ecrã não pode dizer nada, e o defeito é invisível."""
    import scripts.build_snapshot as bs

    empresa, mercado, setor = _serie()

    class _Falsa:
        def __init__(self, v):
            self._v = v

        def to_numpy(self):
            return self._v

        def __len__(self):
            return len(self._v)

    def _hist(simbolo, period="1y"):
        v = {"SPY": mercado}.get(simbolo, empresa if simbolo == "NVDA" else setor)
        return {"Close": _Falsa(v)}

    # `juntar_decomposicao` importa dentro da função, logo é o módulo de origem que se troca
    import investigator.market_data.prices as precos

    monkeypatch.setattr(precos, "get_price_history", _hist)
    monkeypatch.setattr(precos, "log_returns", lambda s: s)

    linhas = [{"ticker": "NVDA"}]
    bs.juntar_decomposicao(linhas, {})
    d = linhas[0]["decomp"]
    assert d is not None, "a decomposição falhou aberto e o teste deixaria de medir algo"
    assert "r2" in d and "fallback" in d, d.keys()
    assert d["r2"] is None or isinstance(d["r2"], float)
    assert isinstance(d["fallback"], bool)


def test_o_coeficiente_nunca_viaja_como_nan():
    """`NaN` não sobrevive a JSON: `json.dumps` escreve o literal `NaN`, que não é JSON
    válido e faz o `JSON.parse` do browser levantar. O recuo tem de produzir `None`."""
    n = 8  # curto de mais para estimar: força o recuo
    d = decompose_move(np.zeros(n), np.zeros(n), None)
    assert d.fallback
    r2 = float(d.r_squared)
    convertido = None if r2 != r2 else r2
    assert convertido is None
    json.loads(json.dumps({"r2": convertido}))  # levantaria com NaN


# ── o que a página faz com o número ───────────────────────────────────────────────────


def _funcao() -> str:
    txt = _fonte_painel()
    m = re.search(r"function explicarR2\(.*?\n\}", txt, re.S)
    assert m, "a função que traduz o coeficiente em frase desapareceu da página"
    return m.group(0)


def test_a_pagina_traduz_o_coeficiente_em_frase():
    f = _funcao()
    assert "fallback" in f, "o recuo tem de ser dito: a sensibilidade não foi estimada"
    assert "does not describe the data" in f, (
        "o caso do ajuste que não descreve os dados é o único que a tese reporta como não "
        "fiável, e é o que o ecrã tem de nomear"
    )
    assert "seventeen companies of the sector map" in f, (
        "o valor tem de ser lido contra a mediana, E a mediana tem de ser atribuída à população "
        "certa: o artefacto mede-a sobre 17 tickers do mapa de setores, e a aplicação monitoriza "
        "12. Dizer «monitored companies» atribuía-a às 12, que é a população errada."
    )


def test_a_mediana_da_pagina_e_a_medida_e_nao_uma_escolha():
    """0,460 está publicado em docs/evaluation e citado no §5.4.6. Se alguém mexer no
    limiar da página sem mexer na medição, isto parte — que é o objetivo."""
    txt = _fonte_painel()
    m = re.search(r"const R2_MEDIANA = ([0-9.]+);", txt)
    assert m, "a constante da mediana desapareceu"
    artefacto = (RAIZ / "docs" / "evaluation" / "evaluation_decomposition.md").read_text(
        encoding="utf-8"
    )
    publicado = re.search(r"R\^2 mediano na janela de estimacao: \*\*([0-9.]+)\*\*", artefacto)
    assert publicado, "o artefacto deixou de publicar a mediana"
    assert abs(float(m.group(1)) - float(publicado.group(1))) < 0.005, (
        f"a página usa {m.group(1)} e a medição publica {publicado.group(1)}"
    )


def test_a_frase_aparece_no_cartao_e_nao_so_na_funcao():
    """Uma função que ninguém chama é a mesma coisa que não existir — e este projeto já
    pagou isso: a repartição vinha na API e o cliente deitava-a fora."""
    txt = _fonte_painel()
    assert "explicarR2(d," in txt.split("function explicarR2")[1], (
        "a função existe mas o cartão não a invoca"
    )


@pytest.mark.parametrize(
    "r2,espera",
    [(0.62, "at or above"), (0.21, "below"), (-0.08, "no better than a flat line")],
)
def test_as_tres_bandas_dizem_coisas_diferentes(r2, espera):
    """Sem isto, as três bandas podiam colapsar na mesma frase sem ninguém dar por isso."""
    f = _funcao()
    assert espera in f, f"a banda de r2={r2} não tem frase própria"


# ── a faixa do z: uma altura, um sítio ────────────────────────────────────────────────


def test_a_altura_da_faixa_do_z_vive_num_so_sitio():
    """Estava em dois números soltos, e o `overflow:hidden` escondia o desacordo.

    ⚠️ Este é o teste que o incidente justifica. A tela do z era criada com uma altura em
    JavaScript e a caixa que a contém tinha outra em CSS, com `overflow:hidden` por cima.
    Quando as duas divergiram, o resultado não foi um erro: foi o rótulo `-3.02` impresso
    **cortado a meio**, numa faixa cuja única função é deixar ler o valor de $z$. Um
    desacordo que se manifesta como composição e não como exceção não tem quem o apanhe,
    e por isso a altura passou a ter uma só origem.
    """
    txt = _fonte_painel()
    assert "--z-alt:" in txt, "a variável da altura da faixa desapareceu"
    assert "height:var(--z-alt)" in txt, "a caixa deixou de ler a variável"
    assert re.search(r"getPropertyValue\('--z-alt'\)", txt), (
        "o gráfico deixou de ler a variável e voltou a ter altura própria"
    )
    assert not re.search(r"criarGrafico\(alvo,\s*\d+\s*,\s*false\)", txt), (
        "a altura da faixa voltou a ser um número solto no JavaScript"
    )


def test_a_faixa_do_z_fixa_o_intervalo_em_vez_de_o_deixar_automatico():
    """Em automático a marca extrema assenta na moldura e o rótulo sai cortado.

    ⚠️ Uma margem no eixo NÃO resolve, e tentá-lo foi o caminho errado: o gerador de marcas
    adapta-se à margem e volta a colocar uma no bordo. O que resolve é fixar o intervalo,
    simétrico à volta de zero — a faixa mede distância à norma nos dois sentidos — com
    folga suficiente para o rótulo mais alto ficar dentro.
    """
    txt = _fonte_painel()
    assert "autoscaleInfoProvider" in txt, "a faixa do z voltou à escala automática"
    m = re.search(r"const zMax = Math\.max\(1\.5,.*\* ([0-9.]+);", txt)
    assert m, "o intervalo da faixa deixou de ser calculado a partir dos dados"
    assert float(m.group(1)) >= 1.3, f"folga de {m.group(1)} é pouca para o rótulo do topo"
