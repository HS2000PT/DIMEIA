"""Cache em disco das séries de fecho, para que uma reconstrução não dependa da rede.

Porque existe
-------------
O corpus de notícias está fixado por revisão e soma de controlo. Os preços não estavam
fixados por nada: `load_close_series` ia ao yfinance em cada construção, e por baixo tinha
uma cadeia de cinco fontes. Os fechos ajustados são reescritos retroativamente a cada
dividendo, e uma fonte de recurso pode servir um ticker sem que isso apareça no resultado —
duas maneiras de a mesma janela devolver séries diferentes em meses diferentes.

Esta cache guarda cada série pedida num CSV nomeado por `(ticker, início, fim)` e regista,
num manifesto ao lado, a fonte que a serviu e a soma de controlo do ficheiro. A partir daí a
reconstrução é determinística, e a proveniência deixa de se perder.

É **opcional de propósito**: a camada viva tem de continuar a ir à rede, por isso o
comportamento sem `cache_dir` fica exatamente como estava.

⚠️ **Não usar `data/prices/`.** O `scripts/build_dataset.py` já lá guarda a sua própria cache,
com **o mesmo nome de ficheiro** — `{ticker}_{inicio}_{fim}.csv` — e **esquema diferente**:
grava um `Series` com o índice, o que dá as colunas `Date,Close`, e lê `["Close"]`. Este
módulo grava `date,close`. Partilhar a pasta faria um ler o ficheiro do outro e rebentar num
`KeyError`, ou pior, ler valores errados. A pasta canónica deste módulo é `data/prices_kb/`,
e há um teste que impede as duas de coincidirem.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

MANIFESTO = "manifesto.json"

#: Pasta canónica desta cache. NÃO é `data/prices/` — ver o aviso no topo do módulo.
PASTA_PADRAO = "data/prices_kb"

#: Pasta da cache do `scripts/build_dataset.py`, que usa o mesmo nome de ficheiro com outro
#: esquema. Existe aqui para o teste de colisão a poder nomear.
PASTA_BUILD_DATASET = "data/prices"


def chave(ticker: str, inicio: str, fim: str) -> str:
    """Identidade de uma série: o ticker E a janela. Duas janelas são duas séries."""
    return f"{ticker.strip().upper()}_{inicio}_{fim}"


def caminho(cache_dir: Path | str, ticker: str, inicio: str, fim: str) -> Path:
    return Path(cache_dir) / f"{chave(ticker, inicio, fim)}.csv"


def carregar(cache_dir: Path | str, ticker: str, inicio: str, fim: str) -> pd.Series | None:
    """Série guardada, ou `None` se não existir. Nunca vai à rede."""
    p = caminho(cache_dir, ticker, inicio, fim)
    if not p.exists():
        return None
    # `float_precision="round_trip"`: o leitor rápido do pandas erra no último bit, e a
    # gravação com dezassete dígitos não serve de nada se a leitura os deitar fora. Os dois
    # lados têm de ser exactos para a cache fixar o que promete fixar.
    df = pd.read_csv(p, parse_dates=["date"], float_precision="round_trip")
    s = pd.Series(df["close"].to_numpy(dtype="float64"),
                  index=pd.DatetimeIndex(df["date"]))
    return s.sort_index()


def guardar(cache_dir: Path | str, ticker: str, inicio: str, fim: str,
            close: pd.Series, fonte: str) -> Path:
    """Grava a série e regista fonte, dimensão, extremos e soma de controlo no manifesto."""
    d = Path(cache_dir)
    d.mkdir(parents=True, exist_ok=True)
    p = caminho(d, ticker, inicio, fim)

    idx = pd.DatetimeIndex(close.index)
    if idx.tz is not None:
        idx = idx.tz_localize(None)
    df = pd.DataFrame({"date": idx.strftime("%Y-%m-%d"),
                       "close": close.to_numpy(dtype="float64")})
    # `%.17g` e não a formatação por omissão: dezassete dígitos significativos garantem que
    # qualquer float64 volta do disco bit a bit. Sem isto o pandas escreve `0.3` onde o valor
    # era `0.30000000000000004`, e uma cache que perde dígitos não fixa coisa nenhuma — foi
    # exactamente o que o teste do pior caso apanhou.
    df.to_csv(p, index=False, float_format="%.17g")

    m = manifesto(d)
    m["series"][chave(ticker, inicio, fim)] = {
        "ficheiro": p.name,
        "fonte": fonte,
        "dias": int(len(close)),
        "primeiro": str(idx[0].date()) if len(idx) else None,
        "ultimo": str(idx[-1].date()) if len(idx) else None,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
    }
    (d / MANIFESTO).write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
    return p


def manifesto(cache_dir: Path | str) -> dict:
    """Manifesto da cache; devolve a estrutura vazia se ainda não existir."""
    p = Path(cache_dir) / MANIFESTO
    if not p.exists():
        return {"series": {}}
    dados = json.loads(p.read_text(encoding="utf-8"))
    dados.setdefault("series", {})
    return dados


def verificar(cache_dir: Path | str) -> list[str]:
    """Nomes das séries cujo ficheiro falta ou já não bate com a soma registada."""
    d = Path(cache_dir)
    problemas: list[str] = []
    for nome, reg in manifesto(d)["series"].items():
        p = d / reg["ficheiro"]
        if not p.exists():
            problemas.append(f"{nome}: ficheiro ausente")
        elif hashlib.sha256(p.read_bytes()).hexdigest() != reg["sha256"]:
            problemas.append(f"{nome}: soma de controlo não bate")
    return problemas


def retornos_log(cache_dir: Path | str, tickers: list[str], inicio: str, fim: str,
                 ) -> dict:
    """Retornos logarítmicos de cada série FIXADA, ou erro se alguma faltar.

    ⚠️ POR QUE E QUE ESTA FUNCAO VIVE AQUI e não em cada script. O `evaluate_anomaly.py` e o
    `evaluate_anomaly_ext.py` tinham, cada um, o seu `_returns` a ir ao yfinance ao vivo. Duas
    cópias da mesma leitura divergem: a do `_ext` ganhou uma cadeia de cinco fontes de recurso e
    a outra não, pelo que a mesma janela podia ser servida por fornecedores diferentes nos dois
    documentos que a dissertação cita lado a lado. A lição está escrita no projeto desde que o
    `dedup.py` foi extraído: uma biblioteca não se importa de um script.

    ⚠️ E FALHA ALTO, de propósito. Uma série em falta faria a avaliação correr sobre catorze
    empresas e publicar uma amplitude entre catorze, que no ecrã se lê exatamente como a de
    quinze. É a classe de defeito que este projeto documenta desde a sessão 63: não encontrar
    nada e aprovar tudo têm o mesmo aspeto.
    """
    import numpy as np

    d = Path(cache_dir)
    if not d.exists():
        raise FileNotFoundError(
            f"a série fixada não existe em {d}. Correr `python scripts/fixar_precos_qi1.py` "
            f"antes de avaliar, ou passar --rede para ir buscar aos fornecedores."
        )
    faltam = [t for t in tickers if carregar(d, t, inicio, fim) is None]
    if faltam:
        raise FileNotFoundError(
            f"{len(faltam)} de {len(tickers)} séries em falta em {d} para {inicio}..{fim}: "
            f"{', '.join(faltam)}. A avaliação correria sobre menos empresas e publicaria uma "
            f"amplitude que se lê como a de {len(tickers)}."
        )
    out: dict[str, np.ndarray] = {}
    for t in tickers:
        serie = carregar(d, t, inicio, fim)
        out[t] = np.diff(np.log(serie.to_numpy(dtype=float)))
    return out
