"""Construção dos pares de treino da QI4, e as garantias que ela tem de dar.

O alvo de um par é `1 - |percentil(a) - percentil(b)|`: dois títulos são tanto mais parecidos
quanto mais próximos ficarem os seus movimentos subsequentes **na distribuição dos movimentos**,
e não em valor absoluto. A escolha é deliberada e tem duas razões.

A primeira é que os retornos têm cauda pesada: uma diferença de meio ponto percentual não
significa o mesmo no meio da distribuição e na cauda, e um alvo construído sobre a diferença
bruta passaria quase todo o seu domínio a distinguir extremos entre si. O percentil é invariante
a transformações monótonas e trata as duas regiões pelo mesmo padrão.

A segunda é que o alvo fica em `[0, 1]` por construção, que é o domínio que a
`CosineSimilarityLoss` espera, sem escala arbitrária a justificar.

**O mapa de percentis ajusta-se ao bloco de treino e reutiliza-se nos outros.** Ajustá-lo sobre
o conjunto todo seria fuga: a distribuição do teste entraria no treino sem que nenhum par
cruzasse fronteira nenhuma. É a fuga que nenhum teste de fronteiras apanha, e é por isso que
`tests/test_qi4_pares.py` lhe dedica o teste mais importante do ficheiro.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

#: Os dois objetivos que a QI4 compara. `magnitude` é o braço principal — materialidade, nunca
#: direção. `direcao` é o braço de replicação, que reproduz [Jeong26] neste mesmo arnês.
ARMAS = ("magnitude", "direcao")

#: Blocos elegíveis por omissão. O `embargo` fica sempre de fora: existe precisamente para
#: separar treino de teste, e um par que o use desfaz a separação que ele garante.
BLOCOS_PADRAO = ("train",)


def mapa_percentil(valores: np.ndarray) -> Callable[[np.ndarray], np.ndarray]:
    """Devolve a função de distribuição empírica de `valores`, saturada fora do apoio.

    O percentil de `x` é a fração de `valores` que não excede `x`. Sobre `[0, 1, 2, 3]`, o
    percentil de 2 é `3/4` — é o valor que `tests/test_qi4_pares.py` confere à mão.

    Satura em vez de extrapolar: um valor abaixo do mínimo observado vale 0 e um acima do
    máximo vale 1. Extrapolar exigiria assumir uma forma para a cauda, e não há razão para o
    fazer quando o alvo só precisa de uma ordem.
    """
    ordenados = np.sort(np.asarray(valores, dtype="float64"))
    if ordenados.size == 0:
        raise ValueError("mapa_percentil: sem valores para ajustar")

    def aplicar(x: np.ndarray) -> np.ndarray:
        pos = np.searchsorted(ordenados, np.asarray(x, dtype="float64"), side="right")
        return pos / ordenados.size

    return aplicar


def alvo_similaridade(pa: np.ndarray, pb: np.ndarray) -> np.ndarray:
    """`1 - |pa - pb|`, com `pa`/`pb` já em percentil. Simétrico e em `[0, 1]`."""
    return 1.0 - np.abs(np.asarray(pa, dtype="float64") - np.asarray(pb, dtype="float64"))


def valores_do_braco(retornos: np.ndarray, arma: str) -> np.ndarray:
    """A definição dos dois braços, num sítio só: um deita o sinal fora, o outro guarda-o.

    É aqui que a QI4 se separa de [Jeong26]. Vale a pena ser explícito sobre o que **não**
    distingue os braços: uma inversão global do sinal de todos os retornos não os distingue,
    porque o alvo assenta em percentis e inverter o sinal apenas inverte a ordem — as
    diferenças de percentil ficam iguais. O que os distingue é o tratamento de um par
    concreto: para `+x` e `−x`, o braço de magnitude dá o alvo máximo e o de direção dá um
    alvo baixo.
    """
    if arma not in ARMAS:
        raise ValueError(f"arma desconhecida: {arma!r}; esperado um de {ARMAS}")
    return np.abs(retornos) if arma == "magnitude" else retornos


def _amostrar_indices(n: int, quantos: int, tickers: np.ndarray,
                      rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """`quantos` pares de índices distintos, de empresas diferentes.

    Amostra em lote e filtra, repetindo até haver pares suficientes: com um bloco realista a
    taxa de rejeição é baixa, e o ciclo evita o custo de um `while` linha a linha. O limite de
    tentativas existe para que um bloco degenerado (uma só empresa) falhe alto em vez de
    entrar em ciclo infinito.
    """
    a_acc: list[np.ndarray] = []
    b_acc: list[np.ndarray] = []
    obtidos = 0
    for _ in range(1000):
        lote = max(quantos - obtidos, 1) * 2
        a = rng.integers(0, n, lote)
        b = rng.integers(0, n, lote)
        ok = (a != b) & (tickers[a] != tickers[b])
        if ok.any():
            a_acc.append(a[ok])
            b_acc.append(b[ok])
            obtidos += int(ok.sum())
        if obtidos >= quantos:
            break
    else:
        raise ValueError(
            "não foi possível formar pares entre empresas diferentes: o bloco tem "
            f"{len(np.unique(tickers))} empresa(s)")
    return np.concatenate(a_acc)[:quantos], np.concatenate(b_acc)[:quantos]


def _amostrar_estratificado(percentis: np.ndarray, quantos: int, tickers: np.ndarray,
                            rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Pares cujo alvo cobre `[0, 1]` de forma aproximadamente uniforme.

    **Porque isto existe.** Amostrando índices ao acaso, a diferença de percentis entre dois
    deles é triangular: média `1/3`, quase nada nos extremos. O alvo `1 − |Δ|` fica então
    concentrado em `0,67`, e um codificador minimiza a perda a prever a média para tudo — que
    é o mesmo que colapsar a representação. Foi exactamente o que aconteceu na primeira
    tentativa: o cosseno entre manchetes diferentes subiu de `0,22` para `0,99`.

    Aqui sorteia-se primeiro a **distância pretendida** `d ~ U(0,1)` e só depois se procuram
    dois pares de percentis que a realizem. O treino passa a ver tanto pares muito parecidos
    como muito diferentes, que é o que um objectivo de semelhança graduada precisa para ter
    sinal.

    ⚠️ **A primeira versão disto estava errada** e vale a pena registar porquê. Sorteava um
    índice e somava-lhe `±d`, cortando o resultado a `[0, 1]`. Mas `E[min(d, 1 − p)] = 1/3`
    quando `d` e `p` são uniformes: o corte devolvia a distribuição exactamente ao triângulo
    que se queria evitar, e o alvo médio dava `0,67` outra vez. A correcção é sortear `d`
    primeiro e só depois o ponto de partida **dentro da margem que `d` admite**, `p_a ~ U(0,
    1 − d)`, de modo que `|Δ| = d` por construção e não por sorte.
    """
    ordem = np.argsort(percentis, kind="stable")
    p_ord = percentis[ordem]
    n = len(percentis)

    d = rng.random(quantos)
    p_a = rng.random(quantos) * (1.0 - d)
    p_b = p_a + d
    trocar = rng.random(quantos) < 0.5
    p_a, p_b = np.where(trocar, p_b, p_a), np.where(trocar, p_a, p_b)

    ia = ordem[np.clip(np.searchsorted(p_ord, p_a), 0, n - 1)]
    pos_b = np.searchsorted(p_ord, p_b)

    ib = np.empty(quantos, dtype="int64")
    for k in range(quantos):
        # janela crescente à volta da posição pretendida, até achar outra empresa
        for raio in (0, 4, 16, 64, 256, n):
            lo, hi = max(0, pos_b[k] - raio - 1), min(n, pos_b[k] + raio + 1)
            cand = ordem[lo:hi]
            ok = cand[(cand != ia[k]) & (tickers[cand] != tickers[ia[k]])]
            if len(ok):
                ib[k] = ok[np.argmin(np.abs(percentis[ok] - p_b[k]))]
                break
        else:  # pragma: no cover - só num bloco de uma só empresa
            raise ValueError("bloco sem empresas suficientes para formar pares")
    return ia, ib


def construir_pares(df: pd.DataFrame, *, coluna_retorno: str, arma: str, n_pares: int,
                    seed: int, blocos: tuple[str, ...] = BLOCOS_PADRAO,
                    estratificado: bool = True,
                    mapa: Callable[[np.ndarray], np.ndarray] | None = None) -> pd.DataFrame:
    """Pares `(texto_a, texto_b, alvo)` para ajustar o codificador.

    Args:
        df: precisa de `headline`, `ticker`, `split` e a coluna de retorno.
        coluna_retorno: retorno anormal contínuo, com sinal (ex.: `abn_h3`).
        arma: `magnitude` (braço principal) ou `direcao` (braço de replicação).
        n_pares: número exacto de pares devolvidos.
        seed: fixa a amostragem.
        blocos: blocos elegíveis. O `embargo` nunca entra, mesmo que seja pedido.
        mapa: mapa de percentis já ajustado. **Passar sempre o do treino** quando se constroem
            pares para outro bloco — sem ele, ajusta-se ao próprio bloco, o que é fuga.

    Returns:
        Quadro com `texto_a`, `texto_b`, `ticker_a`, `ticker_b`, `split`, `valor_a`, `valor_b`
        e `alvo` em `[0, 1]`.
    """
    if arma not in ARMAS:
        raise ValueError(f"arma desconhecida: {arma!r}; esperado um de {ARMAS}")

    elegiveis = tuple(b for b in blocos if b != "embargo")
    sub = df[df["split"].isin(elegiveis)].reset_index(drop=True)
    if len(sub) < 2:
        raise ValueError(f"blocos {elegiveis} têm {len(sub)} linhas — insuficiente para pares")

    valores = valores_do_braco(sub[coluna_retorno].to_numpy(dtype="float64"), arma)
    percentil = mapa if mapa is not None else mapa_percentil(valores)

    rng = np.random.default_rng(seed)
    tickers = sub["ticker"].to_numpy()
    if estratificado:
        ia, ib = _amostrar_estratificado(percentil(valores), n_pares, tickers, rng)
    else:
        ia, ib = _amostrar_indices(len(sub), n_pares, tickers, rng)

    pa, pb = percentil(valores[ia]), percentil(valores[ib])
    return pd.DataFrame({
        "texto_a": sub["headline"].to_numpy()[ia],
        "texto_b": sub["headline"].to_numpy()[ib],
        "ticker_a": sub["ticker"].to_numpy()[ia],
        "ticker_b": sub["ticker"].to_numpy()[ib],
        "split": sub["split"].to_numpy()[ia],
        "valor_a": valores[ia],
        "valor_b": valores[ib],
        "alvo": alvo_similaridade(pa, pb),
    })
