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
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

MANIFESTO = "manifesto.json"


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
