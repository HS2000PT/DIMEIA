"""A caixa do Capitulo 4 declara-se «reproduzida do registo sem edicao». E?

Porque e que este teste existe. A afirmacao central da dissertacao e que a evidencia que o
sistema mostra e verbatim e conferivel. A Figura 4.6 reproduz um alerta real dentro de uma
`tcolorbox`, e a legenda diz «copiado do registo do canal sem edicao». Nada verificava essa
frase: a caixa e LaTeX escrito a mao, e uma alteracao ali compila a zero erros.

Nao e hipotetico. A sessao 61 encontrou uma citacao alterada em silencio -- o travessao de
`Coronavirus - Another Severe Hit To The Automotive Industry` trocado por dois pontos --
numa tabela que declarava os titulos reais, quase de certeza por causa da regra «zero
travessoes», que se aplica a PROSA e nao a texto citado. Numa tese cuja tese e que a
evidencia nao se altera, e o unico defeito que ataca o proprio argumento.

O alerta foi conferido contra `origin/alerts-history:alerts_history.jsonl` a 2026-09-06 e
congelado em `tests/alerta_ch4_verbatim.txt`, para o teste correr offline. O que se compara
sao as CITACOES, caractere a caractere, porque e nelas que a garantia vive: as marcas
`[1]`..`[4]` e a indentacao sao transcricao tipografica, e a legenda declara-as.
"""

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REGISTO = Path(__file__).with_name("alerta_ch4_verbatim.txt")
BS = chr(92)


def _alerta_do_registo() -> str:
    linhas = REGISTO.read_text(encoding="utf-8").splitlines()
    return "\n".join(x for x in linhas if not x.startswith("#")).strip()


def _caixa(arvore: str, ficheiro: str) -> str:
    """A `tcolorbox` do capitulo, com o LaTeX de composicao desfeito."""
    t = (RAIZ / arvore / ficheiro).read_text(encoding="utf-8")
    i, j = t.find("begin{tcolorbox}"), t.find("end{tcolorbox}")
    assert i != -1 and j > i, f"nao encontrei a caixa em {arvore}/{ficheiro}"
    cx = t[i:j].replace(BS + BS + "\n", " ")
    cx = re.sub(re.escape(BS) + r"hspace\*\{\d+em\}", "", cx)
    cx = re.sub(re.escape(BS + BS) + r"\[4pt\]", " ", cx)
    return re.sub(r"\s+", " ", cx.replace(BS + "$", "$").replace(BS + "%", "%"))


def _citacoes(texto: str) -> list[str]:
    return re.findall(r'"([^"]+)"', texto)


def test_as_citacoes_da_caixa_sao_identicas_ao_registo():
    """Caractere a caractere: apostrofos, cifroes e travessoes incluidos."""
    esperadas = _citacoes(_alerta_do_registo())
    assert len(esperadas) == 4, "o registo congelado devia trazer quatro citacoes"
    obtidas = _citacoes(_caixa("tese-pt", "ch4/chapter4.tex"))
    assert obtidas == esperadas, (
        "a caixa do Capitulo 4 diverge do alerta entregue:\n"
        + "\n".join(f"  registo: {a!r}\n  tese:    {b!r}"
                    for a, b in zip(esperadas, obtidas, strict=False) if a != b))


def test_a_arvore_inglesa_reproduz_o_mesmo_alerta():
    """O alerta e ingles nas duas arvores: traduzi-lo quebraria a verificabilidade."""
    esperadas = _citacoes(_alerta_do_registo())
    assert _citacoes(_caixa("tese-eng", "ch4/chapter4.tex")) == esperadas


def test_os_valores_do_alerta_estao_todos_na_caixa():
    """As semelhancas, os impactos e a probabilidade, tal como foram entregues."""
    caixa = _caixa("tese-pt", "ch4/chapter4.tex")
    for valor in ("0.56", "0.51", "0.47", "-2.73", "57"):
        assert valor in caixa, f"{valor} desapareceu da caixa"


def test_o_registo_congelado_declara_a_sua_origem():
    """Um artefacto sem proveniencia nao serve de referencia para nada."""
    cab = REGISTO.read_text(encoding="utf-8")
    assert "alerts_history.jsonl" in cab
    assert "2026-08-13" in cab and "AMZN" in cab


def test_os_tres_precedentes_sao_do_mesmo_dia():
    """Nao e um defeito: e o caso que a Seccao «Discordancia» analisa em seguida.

    Se um dia alguem trocar este exemplo por outro, este teste falha e obriga a
    reler essa seccao, que cita esta figura pelo nome e explica que os tres
    impactos identicos sao um dia observado tres vezes.
    """
    reg = _alerta_do_registo()
    assert reg.count("AAPL 2026-08-05") == 3
    ch4 = (RAIZ / "tese-pt" / "ch4" / "chapter4.tex").read_text(encoding="utf-8")
    assert "Discord" in ch4 and "sis_alerta" in ch4


def test_o_registo_congelado_e_json_valido_quando_reconstruido():
    """Guardado como texto puro, mas tem de sobreviver a uma volta por JSON."""
    a = _alerta_do_registo()
    assert json.loads(json.dumps(a)) == a
    assert a.startswith("\U0001f4f0"), "o registo comeca pelo emoji do canal"
