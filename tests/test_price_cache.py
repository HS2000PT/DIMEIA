"""O corpus está fixado por `sha256`. Os preços não estavam fixados por nada.

`load_close_series` ia à rede em cada construção da base de conhecimento, e por baixo tinha
uma cadeia de cinco fontes: yfinance, Tiingo, Polygon, Stooq, Alpha Vantage. Duas
consequências, nenhuma delas visível em quem lê o resultado:

1. os fechos ajustados são reescritos retroativamente a cada dividendo ou desdobramento, pelo
   que a mesma janela devolve séries diferentes em meses diferentes;
2. se o yfinance falhar num ticker, **outra fonte serve** — e ninguém fica a saber.

A 2026-09-09 mediu-se o desvio contra a amostra congelada e ele era nulo (2,3e-07, ruído de
serialização). Isso é sorte, não garantia. Estes testes definem a cache que transforma a sorte
em facto: quem constrói passa `cache_dir`, e a partir daí a série vem do disco, com a fonte e a
soma de controlo registadas.

A cache é OPCIONAL de propósito: a camada viva (maturação no Actions) tem de continuar a ir à
rede, e por isso o comportamento sem `cache_dir` fica exatamente como estava.
"""

from __future__ import annotations

import hashlib
import json

import pandas as pd
import pytest

from investigator.market_data import price_cache as pc
from investigator.market_data import prices as mod


def serie(valores: list[float], inicio: str = "2020-01-02") -> pd.Series:
    idx = pd.bdate_range(inicio, periods=len(valores))
    return pd.Series(valores, index=idx, dtype="float64")


def moldura(s: pd.Series) -> pd.DataFrame:
    return pd.DataFrame({"Close": s.values}, index=s.index)


# ── a cache em si ─────────────────────────────────────────────────────────────

def test_guardar_e_carregar_devolve_a_serie_identica(tmp_path):
    s = serie([100.0, 101.25, 99.875, 1234.5678901234])
    pc.guardar(tmp_path, "AAPL", "2020-01-01", "2020-12-31", s, "yfinance")
    lida = pc.carregar(tmp_path, "AAPL", "2020-01-01", "2020-12-31")
    assert lida is not None
    # `check_exact=True` é o ponto do teste: uma cache que perde dígitos não serve para fixar
    # nada. O `assert_series_equal` compara com tolerância relativa de 1e-5 por omissão, o que
    # deixaria passar precisamente o defeito que aqui interessa apanhar.
    # `check_freq=False` porque o fixture usa `bdate_range` e traz `freq=<BusinessDay>`; uma
    # série real de preços nunca tem frequência declarada.
    pd.testing.assert_series_equal(lida, s, check_names=False, check_freq=False,
                                   check_exact=True)


def test_o_valor_sobrevive_ao_disco_ate_ao_ultimo_digito(tmp_path):
    """Verificação à mão: o pior caso de float64 tem de voltar bit a bit.

    0,1+0,2 vale 0,30000000000000004 em dupla precisão — dezassete dígitos significativos.
    Se a gravação truncar, é aqui que se vê.
    """
    valor = 0.1 + 0.2
    assert repr(valor) == "0.30000000000000004"
    pc.guardar(tmp_path, "TST", "2020-01-01", "2020-12-31", serie([valor]), "teste")
    lida = pc.carregar(tmp_path, "TST", "2020-01-01", "2020-12-31")
    assert lida.iloc[0] == valor
    assert repr(float(lida.iloc[0])) == "0.30000000000000004"


def test_carregar_sem_ficheiro_devolve_none(tmp_path):
    assert pc.carregar(tmp_path, "AAPL", "2020-01-01", "2020-12-31") is None


def test_a_janela_faz_parte_da_chave(tmp_path):
    """Duas janelas do mesmo ticker são duas séries — não podem partilhar ficheiro."""
    s = serie([1.0, 2.0])
    pc.guardar(tmp_path, "AAPL", "2020-01-01", "2020-12-31", s, "yfinance")
    assert pc.carregar(tmp_path, "AAPL", "2021-01-01", "2021-12-31") is None


def test_o_ticker_e_normalizado(tmp_path):
    s = serie([1.0, 2.0])
    pc.guardar(tmp_path, "aapl", "2020-01-01", "2020-12-31", s, "yfinance")
    assert pc.carregar(tmp_path, "AAPL", "2020-01-01", "2020-12-31") is not None


def test_o_manifesto_regista_fonte_e_soma_de_controlo(tmp_path):
    s = serie([100.0, 101.0, 102.0])
    pc.guardar(tmp_path, "XOM", "2018-01-01", "2023-12-31", s, "stooq")
    m = pc.manifesto(tmp_path)
    reg = m["series"]["XOM_2018-01-01_2023-12-31"]
    assert reg["fonte"] == "stooq"
    assert reg["dias"] == 3
    assert reg["primeiro"] == "2018-01-01" or reg["primeiro"] == str(s.index[0].date())
    assert reg["ultimo"] == str(s.index[-1].date())
    caminho = tmp_path / reg["ficheiro"]
    esperado = hashlib.sha256(caminho.read_bytes()).hexdigest()
    assert reg["sha256"] == esperado


def test_o_manifesto_acumula_series_em_vez_de_as_substituir(tmp_path):
    pc.guardar(tmp_path, "AAPL", "2018-01-01", "2023-12-31", serie([1.0]), "yfinance")
    pc.guardar(tmp_path, "XOM", "2018-01-01", "2023-12-31", serie([2.0]), "yfinance")
    m = json.loads((tmp_path / "manifesto.json").read_text(encoding="utf-8"))
    assert len(m["series"]) == 2


# ── integração com load_close_series ──────────────────────────────────────────

def test_com_cache_a_segunda_chamada_nao_vai_a_rede(tmp_path, monkeypatch):
    """É este o teste que interessa: reconstruir a base não pode voltar a pedir preços."""
    chamadas = {"n": 0}

    def falso(ticker, *, period=None, start=None, end=None, interval="1d"):
        chamadas["n"] += 1
        return moldura(serie([10.0, 11.0, 12.0]))

    monkeypatch.setattr(mod, "_yf_history", falso)

    a = mod.load_close_series(["AAPL"], "2018-01-01", "2023-12-31", cache_dir=tmp_path)
    assert chamadas["n"] == 1
    b = mod.load_close_series(["AAPL"], "2018-01-01", "2023-12-31", cache_dir=tmp_path)
    assert chamadas["n"] == 1, "a segunda chamada foi à rede — a cache não serviu"
    pd.testing.assert_series_equal(a["AAPL"], b["AAPL"], check_names=False, check_freq=False)


def test_sem_cache_o_comportamento_fica_como_estava(tmp_path, monkeypatch):
    chamadas = {"n": 0}

    def falso(ticker, *, period=None, start=None, end=None, interval="1d"):
        chamadas["n"] += 1
        return moldura(serie([10.0, 11.0]))

    monkeypatch.setattr(mod, "_yf_history", falso)

    mod.load_close_series(["AAPL"], "2018-01-01", "2023-12-31")
    mod.load_close_series(["AAPL"], "2018-01-01", "2023-12-31")
    assert chamadas["n"] == 2
    assert not list(tmp_path.iterdir()), "sem cache_dir não se escreve nada em disco"


def test_a_cache_regista_a_fonte_que_serviu(tmp_path, monkeypatch):
    """Se o yfinance falhar e outra fonte servir, isso tem de ficar escrito."""
    def falha(ticker, *, period=None, start=None, end=None, interval="1d"):
        raise RuntimeError("yfinance indisponível")

    monkeypatch.setattr(mod, "_yf_history", falha)
    monkeypatch.setattr(mod, "fallback_daily",
                        lambda t, s, e: (moldura(serie([5.0, 6.0])), "stooq"))

    mod.load_close_series(["PFE"], "2018-01-01", "2023-12-31", cache_dir=tmp_path)
    reg = pc.manifesto(tmp_path)["series"]["PFE_2018-01-01_2023-12-31"]
    assert reg["fonte"] == "stooq"


def test_refrescar_ignora_a_cache_e_reescreve(tmp_path, monkeypatch):
    chamadas = {"n": 0}

    def falso(ticker, *, period=None, start=None, end=None, interval="1d"):
        chamadas["n"] += 1
        return moldura(serie([float(chamadas["n"]), 2.0]))

    monkeypatch.setattr(mod, "_yf_history", falso)

    mod.load_close_series(["KO"], "2018-01-01", "2023-12-31", cache_dir=tmp_path)
    r = mod.load_close_series(["KO"], "2018-01-01", "2023-12-31",
                              cache_dir=tmp_path, refrescar=True)
    assert chamadas["n"] == 2
    assert r["KO"].iloc[0] == pytest.approx(2.0)


def test_um_ticker_sem_dados_nao_entra_na_cache(tmp_path, monkeypatch):
    def falha(ticker, *, period=None, start=None, end=None, interval="1d"):
        raise RuntimeError("sem dados")

    monkeypatch.setattr(mod, "_yf_history", falha)
    monkeypatch.setattr(mod, "fallback_daily",
                        lambda t, s, e: (_ for _ in ()).throw(RuntimeError("nada")))

    r = mod.load_close_series(["ZZZZ"], "2018-01-01", "2023-12-31", cache_dir=tmp_path)
    assert r == {}
    assert pc.manifesto(tmp_path)["series"] == {}


# ── a colisão que quase aconteceu ─────────────────────────────────────────────

def test_as_duas_caches_nao_podem_partilhar_pasta():
    """Duas caches, o mesmo nome de ficheiro, esquemas diferentes.

    O `scripts/build_dataset.py` guarda a sua cache em `data/prices/` com o nome
    `{ticker}_{inicio}_{fim}.csv` — exactamente o nome que este módulo usa. Mas grava um
    `Series` com o índice (colunas `Date,Close`) e lê `["Close"]`, enquanto aqui se grava
    `date,close`. Na mesma pasta, um leria o ficheiro do outro: `KeyError` no melhor caso,
    valores errados no pior.

    A primeira versão desta cache apontava para `data/prices/` e chegou a escrever catorze
    ficheiros lá. Este teste existe para que a separação seja uma propriedade verificada, e
    não um comentário que alguém há de ler.
    """
    assert pc.PASTA_PADRAO != pc.PASTA_BUILD_DATASET
    from pathlib import Path as _P
    assert _P(pc.PASTA_PADRAO).resolve() != _P(pc.PASTA_BUILD_DATASET).resolve()


def test_o_build_kb_aponta_para_a_pasta_desta_cache():
    """A porta que interessa: o valor por omissão do script tem de ser o certo."""
    import re
    from pathlib import Path as _P

    fonte = (_P(__file__).resolve().parents[1] / "scripts" / "build_kb.py").read_text(
        encoding="utf-8")
    m = re.search(r'"--precos-cache",\s*default="([^"]+)"', fonte)
    assert m, "o build_kb.py deixou de declarar --precos-cache"
    assert m.group(1) == pc.PASTA_PADRAO, (
        f"o build_kb.py aponta para {m.group(1)!r}, e a pasta desta cache é "
        f"{pc.PASTA_PADRAO!r}")
