"""Testes da linha de base BM25 na recuperação (puros, determinísticos).

A §5.3.2 da dissertação declara que a linha lexical avaliada é a forma mais elementar da sua
família — contagem de palavras, sem ponderação pela raridade dos termos, sem saturação da
frequência e sem normalização pelo comprimento — e que «a comparação com uma função de ordenação
bem parametrizada constitui trabalho por realizar, e é a que tornaria esta conclusão mais forte».

O BM25 (Robertson e Zaragoza 2009) acrescenta exatamente as três peças em falta. Estes testes
fixam o seu comportamento contra valores calculados à mão antes de a função existir.
"""

import math

import numpy as np
import pytest

from investigator.evaluation.retrieval_bm25 import Bm25Index, bm25_precision_at_k
from investigator.evaluation.retrieval_eval import expected_random_precision, same_ticker_forbid

# ---------------------------------------------------------------------------
# Valores calculados à mão
#
# IDF(t) = ln( (N - n(t) + 0,5) / (n(t) + 0,5) + 1 )
# score(q,d) = Σ_t IDF(t) · f(t,d)·(k1+1) / ( f(t,d) + k1·(1 - b + b·|d|/avgdl) )
# com k1 = 1,5 e b = 0,75.
# ---------------------------------------------------------------------------


def test_idf_e_saturacao_valor_calculado_a_mao():
    """Corpus de 3 documentos de comprimento igual: a normalização de comprimento é neutra.

    d0 = "apple earnings beat"  |d0| = 3
    d1 = "apple earnings miss"  |d1| = 3
    d2 = "oil price war"        |d2| = 3      →  avgdl = 3

    N = 3; n(apple) = n(earnings) = 2.
    IDF = ln((3 - 2 + 0,5)/(2 + 0,5) + 1) = ln(1,6) = 0,470003629…

    Com |d| = avgdl, o fator de normalização é k1·(1 - b + b·1) = k1 = 1,5, pelo que
    f·(k1+1)/(f + 1,5) = 1·2,5/2,5 = 1,0 exatamente.

    Consulta "apple earnings" → score(d0) = score(d1) = 2 × 0,470003629 = 0,940007258.
    """
    docs = ["apple earnings beat", "apple earnings miss", "oil price war"]
    idx = Bm25Index(docs, k1=1.5, b=0.75)
    scores = idx.scores(["apple earnings"])[0]

    idf = np.log(1.6)
    assert idf == pytest.approx(0.4700036292457356)
    assert scores[0] == pytest.approx(2 * idf)
    assert scores[1] == pytest.approx(2 * idf)
    assert scores[2] == pytest.approx(0.0)


def test_normalizacao_pelo_comprimento_valor_calculado_a_mao():
    """Dois documentos com o mesmo termo, comprimentos diferentes: o mais curto pontua mais.

    d0 = "apple beat"                     |d0| = 2
    d1 = "apple beat miss loss gain drop" |d1| = 6      →  avgdl = 4

    N = 2; n(apple) = 2  →  IDF = ln((2 - 2 + 0,5)/(2 + 0,5) + 1) = ln(1,2) = 0,182321557…

    d0: norm = 1,5·(0,25 + 0,75·2/4) = 0,9375  →  2,5/(1 + 0,9375) = 2,5/1,9375 = 40/31
        score = ln(1,2) · 40/31
    d1: norm = 1,5·(0,25 + 0,75·6/4) = 2,0625  →  2,5/(1 + 2,0625) = 2,5/3,0625 = 40/49
        score = ln(1,2) · 40/49

    As duas frações são exatas: 2,5/1,9375 = 25000/19375 = 40/31 e 2,5/3,0625 = 25000/30625
    = 40/49. Escreve-se a expectativa nesta forma fechada, e não numa aproximação decimal,
    por duas razões: é o valor exato em precisão dupla, e a derivação continua a ser feita à
    mão em vez de reproduzir o cálculo da implementação.
    """
    docs = ["apple beat", "apple beat miss loss gain drop"]
    idx = Bm25Index(docs, k1=1.5, b=0.75)
    scores = idx.scores(["apple"])[0]

    idf = math.log(1.2)
    assert idf == pytest.approx(0.18232155679395463)
    assert scores[0] == pytest.approx(idf * 40 / 31, rel=1e-12)
    assert scores[1] == pytest.approx(idf * 40 / 49, rel=1e-12)
    assert scores[0] > scores[1]
    # o quociente entre as duas pontuações é (40/31)/(40/49) = 49/31, independente do IDF
    assert scores[0] / scores[1] == pytest.approx(49 / 31, rel=1e-12)


def test_saturacao_da_frequencia_nao_e_linear():
    """Repetir um termo aumenta a pontuação, mas menos do que proporcionalmente."""
    docs = ["gain", "gain gain", "gain gain gain gain"]
    idx = Bm25Index(docs, k1=1.5, b=0.0)  # b = 0 isola a saturação do comprimento
    s = idx.scores(["gain"])[0]
    assert s[1] > s[0]
    assert s[2] > s[1]
    # duplicar de 1 para 2 ocorrências rende mais do que quadruplicar de 2 para 4
    assert (s[1] - s[0]) > (s[2] - s[1])


def test_termo_ausente_do_vocabulario_nao_rebenta():
    idx = Bm25Index(["apple earnings", "oil price"])
    s = idx.scores(["zebra"])[0]
    assert s.shape == (2,)
    assert np.all(s == 0.0)


def test_idf_nunca_negativo():
    """Um termo presente em todos os documentos tem IDF pequeno mas não negativo.

    A variante adotada, ln(… + 1), é sempre não-negativa — ao contrário da forma clássica,
    que fica negativa quando n(t) > N/2 e inverteria a ordenação.
    """
    docs = ["a b", "a c", "a d", "a e"]
    idx = Bm25Index(docs)
    assert idx.idf_of("a") >= 0.0
    assert idx.idf_of("b") > idx.idf_of("a")


# ---------------------------------------------------------------------------
# Integração com o protocolo de avaliação da tese
# ---------------------------------------------------------------------------


def _toy():
    """Mesma forma do conjunto de brincar de test_retrieval_eval.py, agora com texto."""
    docs = [
        "chip maker beats quarterly estimates",      # tech
        "semiconductor firm tops revenue forecast",  # tech
        "software group raises earnings guidance",   # tech
        "lender sets aside loan loss provisions",    # bank
        "bank reports higher net interest income",   # bank
        "credit provider warns on defaults",         # bank
    ]
    sectors = np.array(["tech", "tech", "tech", "bank", "bank", "bank"])
    tickers = np.array(["AAPL", "MSFT", "NVDA", "JPM", "BAC", "C"])
    return docs, sectors, tickers


def test_bm25_respeita_a_proibicao_de_mesma_empresa():
    docs, sectors, tickers = _toy()
    idx = Bm25Index(docs)
    forbid = same_ticker_forbid(tickers, tickers)
    p = bm25_precision_at_k(idx, docs, sectors, sectors, k=2, forbid=forbid)
    assert 0.0 <= p <= 1.0


def test_bm25_nunca_devolve_a_propria_consulta():
    """Com a diagonal proibida, o documento idêntico à consulta não pode ser recuperado."""
    docs, sectors, tickers = _toy()
    idx = Bm25Index(docs)
    forbid = same_ticker_forbid(tickers, tickers)
    top = idx.top_k(docs, k=2, forbid=forbid)
    for i, row in enumerate(top):
        assert i not in row


def test_bm25_e_determinista():
    docs, sectors, tickers = _toy()
    forbid = same_ticker_forbid(tickers, tickers)
    a = bm25_precision_at_k(Bm25Index(docs), docs, sectors, sectors, k=2, forbid=forbid)
    b = bm25_precision_at_k(Bm25Index(docs), docs, sectors, sectors, k=2, forbid=forbid)
    assert a == b


def test_bm25_bate_a_taxa_base_quando_o_vocabulario_separa_setores():
    """Neste conjunto o vocabulário é distintivo, pelo que o BM25 deve superar o acaso."""
    docs, sectors, tickers = _toy()
    forbid = same_ticker_forbid(tickers, tickers)
    p_bm25 = bm25_precision_at_k(Bm25Index(docs), docs, sectors, sectors, k=2, forbid=forbid)
    p_rand = expected_random_precision(sectors, sectors, forbid)
    assert p_bm25 > p_rand


def test_blocos_nao_alteram_o_resultado():
    """A avaliação por blocos existe por memória e não pode mudar o valor medido."""
    docs, sectors, tickers = _toy()
    idx = Bm25Index(docs)
    forbid = same_ticker_forbid(tickers, tickers)
    inteiro = bm25_precision_at_k(idx, docs, sectors, sectors, k=2, forbid=forbid, block=1000)
    partido = bm25_precision_at_k(idx, docs, sectors, sectors, k=2, forbid=forbid, block=2)
    assert inteiro == pytest.approx(partido)
