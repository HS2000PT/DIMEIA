"""Fixa a série de fechos da avaliação da QI1, para a §5.2 deixar de depender da rede.

⚠️ POR QUE E QUE ISTO EXISTE. O `evaluate_anomaly.py` e o `evaluate_anomaly_ext.py` chamavam
`yf.Ticker(t).history(...)` ao vivo, sem cache e sem ficheiro fixado, e o segundo tem por baixo
uma cadeia de cinco fontes. São as duas únicas avaliações do trabalho que dependem da rede no
momento da leitura, e produzem números que a dissertação cita: a amplitude da taxa de disparo
(`0,015` contra `0,344`), o `F1` de `0,530`, e o `0,269` do Isolation Forest.

**A deriva não é hipotética: foi medida.** A 2026-09-10 a mesma janela devolveu o `F1` do
Isolation Forest a `0,270` contra o `0,271` do artefacto congelado a 2026-07-04. Tudo o resto
reproduziu ao milésimo. Os fechos ajustados são reescritos retroativamente a cada dividendo e
desdobramento, e basta um ponto no limiar mudar de lado para o detetor aprendido, que sinaliza
uma fração fixa, trocar uma decisão.

O módulo que resolve isto **já existia** (`investigator/market_data/price_cache.py`, escrito
para a construção da base de casos, com o mesmo aviso no topo) e nunca tinha sido aplicado aqui.
Este script só o invoca sobre a janela da QI1.

⚠️ E A PASTA É VERSIONADA DE PROPÓSITO. O `data/**` está gitignored, e `data/prices/` tem zero
ficheiros versionados: fixar lá tornava a corrida determinística **só nesta máquina**, o que não
é reprodutibilidade. A pasta canónica desta série é `data/samples/precos_qi1/`, que o
`.gitignore` deixa passar pela exceção de `data/samples/**`.

    python scripts/fixar_precos_qi1.py            # fixa (não sobrescreve o que já existe)
    python scripts/fixar_precos_qi1.py --verificar # só confere as somas de controlo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from investigator.market_data import price_cache  # noqa: E402

#: A pasta desta serie. NAO e' `data/prices/` (esquema diferente, ver o aviso do price_cache)
#: nem `data/prices_kb/` (nao versionada).
PASTA = "data/samples/precos_qi1"

#: Os quinze da avaliacao da QI1. Identicos nos dois scripts -- verificado a 2026-09-10 --,
#: e e' por isso que uma so serie fixada serve os dois.
TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "NVDA", "TSLA", "META", "JPM",
    "BAC", "XOM", "CVX", "JNJ", "PFE", "WMT", "KO",
]

INICIO, FIM = "2023-06-01", "2026-06-01"


def fixar(pasta: Path, inicio: str, fim: str, *, forcar: bool) -> int:
    import yfinance as yf

    novos = falhas = 0
    for t in TICKERS:
        if not forcar and price_cache.carregar(pasta, t, inicio, fim) is not None:
            print(f"  [ja fixado] {t}")
            continue
        df = yf.Ticker(t).history(start=inicio, end=fim, interval="1d")
        if df is None or df.empty:
            print(f"  [!] sem dados: {t}")
            falhas += 1
            continue
        serie = df["Close"]
        serie.index = serie.index.tz_localize(None) if serie.index.tz else serie.index
        price_cache.guardar(pasta, t, inicio, fim, serie, fonte="yfinance")
        print(f"  [fixado] {t}: {len(serie)} fechos")
        novos += 1
    if falhas:
        # ⚠️ Falhar ALTO. Uma serie em falta faz a avaliacao correr sobre catorze tickers e
        # reportar uma amplitude entre catorze, que se le exactamente como a de quinze.
        print(f"\nFALHA: {falhas} ticker(s) sem dados. A serie fixada ficaria incompleta.")
        return 1
    print(f"\n{novos} serie(s) nova(s) em {pasta}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Fixa os fechos da avaliação da QI1.")
    p.add_argument("--pasta", default=PASTA)
    p.add_argument("--inicio", default=INICIO)
    p.add_argument("--fim", default=FIM)
    p.add_argument("--forcar", action="store_true",
                   help="rebusca e sobrescreve séries já fixadas (muda os números; usar com "
                        "intenção e regenerar os artefactos a seguir)")
    p.add_argument("--verificar", action="store_true",
                   help="só confere as somas de controlo do manifesto")
    a = p.parse_args()
    pasta = REPO / a.pasta

    if a.verificar:
        if not pasta.exists():
            print(f"FALHA: {a.pasta} não existe. Correr sem --verificar primeiro.")
            return 1
        problemas = price_cache.verificar(pasta)
        man = price_cache.manifesto(pasta)
        print(f"séries no manifesto: {len(man.get('series', man))}")
        if problemas:
            print("\nFALHA — somas de controlo que não batem:")
            for x in problemas:
                print(f"  {x}")
            return 1
        print("todas as somas de controlo batem.")
        return 0

    pasta.mkdir(parents=True, exist_ok=True)
    return fixar(pasta, a.inicio, a.fim, forcar=a.forcar)


if __name__ == "__main__":
    raise SystemExit(main())
