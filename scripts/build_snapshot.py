"""Pré-computa a grelha para um instantâneo estático — o protótipo que decide a stack.

O PORQUÊ, EM UMA FRASE
----------------------
A grelha de entrada chama `_snapshot(t)` para cada um dos doze tickers, e cada chamada puxa um
ano de preços pela rede. São **doze idas à rede antes da primeira pintura**, e é aí que vivem os
~5,5 s de carga a frio — não no CSS, e não no Streamlit.

O que este script faz é o padrão do *data loader* do Observable Framework, e é o que os quatro
agentes do estudo de mercado recomendaram independentemente: **o worker calcula, a página lê**.

O QUE ISTO É E O QUE NÃO É
--------------------------
**É** um protótipo para produzir um número: quanto custa a grelha a ler um ficheiro contra
calcular ao vivo. O briefing exige exactamente isso antes de se propor trocar de stack —
*"mostra um protótipo pequeno a provar o ganho antes de reescrever tudo"*.

**Não é** a v4 nem toca na v3. Escreve um ficheiro; ninguém o lê ainda.

A REGRA QUE O MANTÉM HONESTO
----------------------------
O instantâneo é construído com **as mesmas funções que a app usa** (`detect_latest`,
`empirical_exceedance`, `detect_volume_latest`). Se fossem reimplementadas aqui, o ficheiro
poderia divergir do que a app calcularia e ninguém daria por isso — que é a classe de defeito
que este projecto já pagou em três sítios diferentes.

USO
---
    python scripts/build_snapshot.py
    python scripts/build_snapshot.py --medir    # compara ler-ficheiro vs calcular-ao-vivo
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from datetime import UTC, datetime

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

DESTINO = RAIZ / "data" / "samples" / "dashboard_snapshot.json"
JANELA = 20
LIMIAR = 1.5


def _watchlist() -> list[str]:
    import yaml

    cfg = yaml.safe_load((RAIZ / "config" / "alerts.yaml").read_text(encoding="utf-8")) or {}
    return list(cfg.get("market", {}).get("tickers") or [])


def linha_de(ticker: str) -> dict | None:
    """Tudo o que um cartão da grelha precisa, calculado uma vez."""
    from investigator.anomaly_detector.detector import detect_latest
    from investigator.anomaly_detector.frequency import empirical_exceedance
    from investigator.anomaly_detector.volume import detect_volume_latest
    from investigator.market_data.prices import get_price_history, log_returns

    try:
        frame = get_price_history(ticker, period="1y")
        fecho = frame["Close"]
        retornos = log_returns(fecho)
        res = detect_latest(retornos, window=JANELA, threshold=LIMIAR)
        out: dict = {
            "ticker": ticker,
            "z": None if res.reported_z is None else float(res.reported_z),
            "move": float(res.last_return),
            "flagged": bool(res.is_anomaly),
            "zero_variance": bool(res.zero_variance),
            "vol_ratio": None,
            "rarity": None,
        }
        exc = empirical_exceedance(retornos)
        if exc is not None:
            # ⚠️ Os QUATRO campos, não dois. `move` e `same_direction` parecem supérfluos até
            # se reconstruir o objecto do outro lado: sem `move`, a frase "a maior queda em
            # 249 dias" não sabe se foi queda ou subida; sem `same_direction`, perde-se a
            # informação de quantos desses dias foram no mesmo sentido.
            out["rarity"] = {"count": int(exc.count), "n": int(exc.n),
                             "move": float(exc.move),
                             "same_direction": int(exc.same_direction)}

        # Série de fechos para o gráfico do detalhe. Vai no instantâneo pela mesma razão que
        # tudo o resto: se o detalhe fosse buscar preços à rede, o clique voltava a pagar o
        # custo que a grelha deixou de pagar, e o painel ficava rápido a abrir e lento a usar.
        # Arredondada a 4 casas — a diferença é invisível num gráfico e corta o ficheiro a meio.
        serie = fecho.tail(260)
        out["closes"] = [
            [d.strftime("%Y-%m-%d"), round(float(v), 4)]
            for d, v in serie.items()
            if v == v  # NaN != NaN: descarta buracos sem os disfarçar
        ]

        # Dias que o detector teria assinalado ao longo do ano — o "replay" da RQ1 sobre o
        # passado. É o que põe eventos no gráfico sem inventar nenhum: é a MESMA regra do
        # `detect_latest`, aplicada a cada dia, e não uma marcação decorativa.
        try:
            from investigator.anomaly_detector.detector import detect_all

            out["events"] = [
                [d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d),
                 None if res.reported_z is None else round(float(res.reported_z), 2),
                 res.baseline_direction]
                for d, res in detect_all(retornos, window=JANELA, threshold=LIMIAR)
            ]
        except Exception:  # noqa: BLE001
            out["events"] = []
        if "Volume" in frame:
            v = detect_volume_latest(frame["Volume"], window=JANELA, threshold=2.0)
            if v.is_unusual:
                out["vol_ratio"] = float(v.ratio)

        # A SESSÃO EM CURSO, em barras de 5 minutos.
        #
        # Porque é que isto vive no instantâneo e não no cliente: o painel abre por defeito em
        # "agora", e "agora" tem de ser a sessão de hoje. Sem esta série, o intervalo 1D não
        # teria nada para mostrar — os dados diários dão UM ponto — e o produto abriria na
        # única vista onde não há nada que ver. Foi um defeito real da v3, registado na
        # sessão 47: o detalhe abria em 1D e nesse intervalo não existe nada.
        #
        # ⚠️ **A honestidade que isto obriga.** Fora de horas, a série é da ÚLTIMA sessão
        # fechada, não de hoje. O carimbo `intraday_day` vai junto exactamente para o ecrã
        # poder dizer de que dia é — o estudo de percursos apanhou uma pessoa a ler o fecho de
        # ontem como o preço de agora, às 08:02, sem nada no ecrã a desmenti-la.
        out["intraday"] = None
        out["intraday_day"] = None
        out["prev_close"] = None
        try:
            import yfinance as yf

            intra = yf.Ticker(ticker).history(period="1d", interval="5m")
            if intra is not None and not intra.empty and "Close" in intra:
                serie = intra["Close"].dropna()
                if len(serie) >= 2:
                    out["intraday"] = [
                        [int(ts.timestamp()), round(float(v), 4)]
                        for ts, v in serie.items()
                    ]
                    out["intraday_day"] = serie.index[-1].strftime("%Y-%m-%d")
                    # O fecho anterior é a referência contra a qual a variação do dia faz
                    # sentido. Sem ele, uma linha intradiária é um preço sem baseline.
                    anteriores = fecho[fecho.index.strftime("%Y-%m-%d") < out["intraday_day"]]
                    if len(anteriores):
                        out["prev_close"] = round(float(anteriores.iloc[-1]), 4)
        except Exception:  # noqa: BLE001  (falha aberto: sem intradiário o painel usa o diário)
            pass
        return out
    except Exception as erro:  # noqa: BLE001
        print(f"  {ticker:6s} falhou: {type(erro).__name__}: {erro}")
        return None


def juntar_decomposicao(linhas: list[dict], fora: dict) -> None:
    """Acrescenta mercado/setor/empresa a cada linha, in-place.

    Vive no instantâneo e não na página porque é a **segunda das três perguntas** do trabalho,
    e o critério C2 exige que as três apareçam sempre, na mesma ordem — incluindo quando a
    resposta é "moveu-se com o mercado". Uma pergunta que só aparece às vezes ensina o leitor a
    não a procurar.

    Custa quase nada: o índice e os ETF de setor são cinco séries partilhadas por doze tickers.
    Falha aberto por ticker — sem decomposição, a linha fica sem ela e o cartão di-lo.
    """
    from investigator.correlation_engine.decomposition import decompose_move
    from investigator.market_data.prices import get_price_history, log_returns
    from investigator.news_fetcher.relevance import MARKET_INDEX, sector_etf

    cache: dict[str, object] = {}

    def serie(simbolo: str):
        if simbolo not in cache:
            try:
                cache[simbolo] = log_returns(get_price_history(simbolo, period="1y")["Close"])
            except Exception:  # noqa: BLE001
                cache[simbolo] = None
        return cache[simbolo]

    mercado = serie(MARKET_INDEX)
    if mercado is None:
        return
    # ⚠️ O retorno do PRÓPRIO índice, e não a contribuição do mercado por empresa. São coisas
    # diferentes: a contribuição é β·r_m, portanto muda de empresa para empresa conforme o beta,
    # e nenhuma delas é «quanto o mercado andou hoje». O painel precisa do segundo número.
    try:
        import math
        fora["market_index"] = MARKET_INDEX
        fora["market_move"] = float(math.exp(float(mercado.to_numpy()[-1])) - 1.0)
    except Exception:  # noqa: BLE001
        fora["market_index"] = MARKET_INDEX
        fora["market_move"] = None
    for linha in linhas:
        try:
            t = linha["ticker"]
            r = log_returns(get_price_history(t, period="1y")["Close"])
            etf = sector_etf(t)
            s = serie(etf) if etf else None
            n = min(len(r), len(mercado), len(s) if s is not None else len(r))
            d = decompose_move(
                r.to_numpy()[-n:],
                mercado.to_numpy()[-n:],
                s.to_numpy()[-n:] if s is not None else None,
            )
            linha["decomp"] = {
                "market": float(d.market),
                "sector": float(d.sector),
                "company": float(d.idiosyncratic),
                "driver": d.driver,
            }
        except Exception:  # noqa: BLE001
            linha["decomp"] = None


def construir() -> dict:
    tickers = _watchlist()
    t0 = time.perf_counter()
    linhas = [x for x in (linha_de(t) for t in tickers) if x]
    extra: dict = {}
    juntar_decomposicao(linhas, extra)
    custo = time.perf_counter() - t0
    return {
        **extra,
        # Carimbo em UTC: o critério C3 exige que a idade seja VISÍVEL no ecrã e que não passe
        # de 90 s em operação normal. Sem isto, um instantâneo velho é indistinguível de um
        # fresco, e um número velho apresentado como actual é pior do que nenhum número.
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "build_seconds": round(custo, 3),
        "window": JANELA,
        "threshold": LIMIAR,
        "rows": linhas,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--medir", action="store_true", help="comparar ler vs calcular")
    args = p.parse_args()

    print("a construir o instantaneo (calculo ao vivo, como a grelha faz hoje)...")
    snap = construir()
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(json.dumps(snap, indent=1), encoding="utf-8")
    tam = DESTINO.stat().st_size
    print(f"\n{len(snap['rows'])}/{len(_watchlist())} tickers em {snap['build_seconds']:.2f} s")
    print(f"-> {DESTINO}  ({tam/1024:.1f} KB)")

    if args.medir:
        print("\n--- a medicao que decide ---")
        t0 = time.perf_counter()
        lido = json.loads(DESTINO.read_text(encoding="utf-8"))
        ler = time.perf_counter() - t0

        t0 = time.perf_counter()
        _ = [x for x in (linha_de(t) for t in _watchlist()) if x]
        vivo = time.perf_counter() - t0

        print(f"  calcular ao vivo (o que a grelha faz hoje) : {vivo:8.3f} s")
        print(f"  ler o instantaneo do disco                 : {ler:8.3f} s")
        if ler > 0:
            print(f"  razao                                      : {vivo/ler:8.0f}x")
        print(f"\n  linhas no ficheiro: {len(lido['rows'])}")
        print("\n  Nota: 'ao vivo' beneficia da cache HTTP desta corrida, portanto o ganho real")
        print("  numa maquina fria e MAIOR do que este. Mesmo assim ja decide.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
