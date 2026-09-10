"""O corpus de notícias do Finnhub descreve-se a si próprio, e o manifesto tem de bater certo.

**Porque este ficheiro existe.** O corpus da §5.3 não estava fixado por nada, e a 2026-09-10
descobriu-se que a janela declarada nunca tinha sido a janela recolhida: a API devolve no máximo
~250 itens por pedido e, ao bater nesse tecto, ignora o `from`. A consequência não era um erro —
era um corpus com a forma certa e o período errado, com a cobertura a variar de 3 a 28 dias
segundo o volume de notícias de cada empresa.

O que estes testes guardam é a **proveniência**: que o ficheiro em disco é o que o manifesto diz
que é, que a truncagem residual continua a ser a declarada, e que a composição setorial é medida
e não suposta. Os valores em si ficam guardados pelo git, que é onde uma alteração tem de
aparecer.

⚠️ Saltam quando o CSV não está presente. `data/` está gitignored — é grande e é regenerável —
logo estes testes correm na máquina que tem o corpus e saltam na CI. Um teste que inventasse
dados para poder correr não estaria a verificar nada.

Ver `docs/design/plano_53_fnspid.md`.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MANIFESTO = RAIZ / "docs" / "design" / "finnhub_corpus_manifest.json"
CORPUS = RAIZ / "data" / "finnhub_news.csv"

pytestmark = pytest.mark.skipif(
    not (MANIFESTO.exists() and CORPUS.exists()),
    reason="precisa de data/finnhub_news.csv (gitignored) e do manifesto",
)


@pytest.fixture(scope="module")
def manifesto() -> dict:
    return json.loads(MANIFESTO.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def corpus():
    import pandas as pd

    return pd.read_csv(CORPUS)


def test_a_soma_de_controlo_descreve_o_ficheiro_em_disco(manifesto):
    """A prova de proveniência. Se falhar, o corpus mudou sem o manifesto mudar."""
    h = hashlib.sha256()
    with CORPUS.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    assert h.hexdigest() == manifesto["sha256"], (
        "o CSV em disco não é o que o manifesto declara — regenerar o manifesto com "
        "scripts/fixar_corpus_finnhub.py, e perceber porque mudou antes de o aceitar"
    )


def test_as_contagens_batem_certo(manifesto, corpus):
    assert len(corpus) == manifesto["manchetes"]
    assert corpus["ticker"].nunique() == manifesto["empresas"]
    soma_empresas = sum(v["manchetes"] for v in manifesto["por_empresa"].values())
    assert soma_empresas == manifesto["manchetes"], "as parcelas por empresa não somam ao total"
    soma_setores = sum(v["manchetes"] for v in manifesto["por_setor"].values())
    assert soma_setores == manifesto["manchetes"], "as parcelas por setor não somam ao total"


def test_todas_as_empresas_cobrem_a_janela_declarada(manifesto):
    """É esta a propriedade que o corpus antigo NÃO tinha.

    Sem fatiar, a NVDA cobria três dias e o KO vinte e oito, na mesma «janela de 27 dias». Com a
    janela partida em fatias de um dia, todas as empresas chegam ao início da janela — e é isso
    que torna verdadeira a frase que declara o período.
    """
    inicio = manifesto["janela"]["primeiro"]
    atrasadas = {
        tk: v["primeiro"] for tk, v in manifesto["por_empresa"].items() if v["primeiro"] != inicio
    }
    assert not atrasadas, (
        f"empresas que não chegam ao início da janela ({inicio}): {atrasadas}. "
        "Sinal de que a recolha bateu no tecto da API e a janela declarada não é a recolhida."
    )


def test_a_truncagem_residual_continua_a_ser_a_declarada(manifesto, corpus):
    """A truncagem que sobra é irredutível, e por isso é medida e não escondida.

    O dia é a granularidade mínima da API, logo um dia em que uma só empresa gere mais de ~250
    manchetes não pode ser pedido em pedaços. O que não é aceitável é que isso não esteja escrito.
    """
    import pandas as pd

    from scripts.fixar_corpus_finnhub import TECTO_API

    dias = pd.to_datetime(corpus["date"]).dt.date
    por_dia = corpus.assign(d=dias).groupby(["ticker", "d"]).size()
    truncados = por_dia[por_dia >= TECTO_API]

    decl = manifesto["truncagem_residual"]
    assert int(len(por_dia)) == decl["pares_ticker_dia"]
    assert int(len(truncados)) == decl["pares_no_tecto"]
    assert sorted({tk for tk, _ in truncados.index}) == decl["empresas"]
    assert decl["fracao_pares"] < 0.05, (
        f"truncagem residual em {decl['fracao_pares']:.1%} dos pares — acima do que a recolha "
        "fatiada devia deixar. Rever a fatia antes de usar o corpus."
    )


def test_a_composicao_setorial_e_medida_e_nao_a_proporcao_de_empresas(manifesto):
    """O achado que motivou tudo isto, virado em porta.

    No corpus truncado cada empresa contribuía com ~248 manchetes independentemente do seu
    volume real, pelo que a fração de cada setor era a **proporção de empresas** desse setor:
    tecnologia dava `7/15 = 0,467`, e os outros quatro setores davam `2/15 = 0,133` cada um. Se
    a composição voltar a parecer-se com isso, a recolha truncou outra vez.
    """
    fracoes = {s: v["fracao"] for s, v in manifesto["por_setor"].items()}
    suspeitas = {s: f for s, f in fracoes.items() if abs(f - 2 / 15) < 0.01}
    assert len(suspeitas) < 3, (
        f"{len(suspeitas)} setores com fração ≈ 2/15 ({suspeitas}) — é a impressão digital do "
        "tecto da API, onde cada empresa contribui com o mesmo número de manchetes."
    )
    assert abs(sum(fracoes.values()) - 1.0) < 0.01, "as frações por setor não somam a um"
