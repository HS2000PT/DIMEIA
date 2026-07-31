"""Predição conformal split para a triagem — a garantia que uma probabilidade não dá.

*O problema.* A triagem devolve uma probabilidade calibrada por Platt. Calibração é uma
afirmação **agregada**: "entre os itens a que chamei 60%, cerca de 60% eram materiais". Não
diz nada sobre um item concreto, e não vem com garantia nenhuma se o modelo estiver a ser
usado fora do regime em que foi ajustado.

*O que a predição conformal acrescenta.* Uma garantia **livre de distribuição** e de amostra
finita: escolhido um α, o conjunto devolvido contém a classe verdadeira em pelo menos 1−α dos
casos. Não assume normalidade, nem que o modelo esteja bem especificado, nem sequer que seja
bom. Assume **uma** coisa: permutabilidade entre o conjunto de calibração e o que se vai
prever. Essa é a suposição a interrogar, e o script de avaliação interroga-a de propósito com
uma divisão temporal, além da aleatória.

*Porque encaixa nesta tese.* Num problema binário o conjunto pode vir com os dois rótulos lá
dentro, e isso lê-se como **"não sei"** — dito de forma explícita, com uma garantia por trás,
em vez de um 0,51 que finge decidir. É a mesma postura que leva o sistema a recusar prever
preços.

Tudo NumPy puro: sem sklearn, sem estado, testável linha a linha.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Os dois rótulos do problema de triagem: 0 = não material, 1 = material.
LABELS: tuple[int, int] = (0, 1)


def nonconformity(probs_positive: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Pontuação de não-conformidade: ``1 − p̂(classe verdadeira)``.

    Alta = o modelo achou a verdade improvável = exemplo estranho. É a escolha canónica para
    classificação e a mais fácil de explicar: mede exatamente o quanto o modelo se enganou
    naquele caso.
    """
    p = np.asarray(probs_positive, dtype=np.float64)
    y = np.asarray(labels)
    if p.shape != y.shape:
        raise ValueError(f"formatos diferentes: probs {p.shape} vs labels {y.shape}")
    p_true = np.where(y == 1, p, 1.0 - p)
    return 1.0 - p_true


def conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    """O limiar ``q̂`` da calibração conformal split.

    Usa a correção de amostra finita ``⌈(n+1)(1−α)⌉ / n`` e **não** o quantil empírico simples.
    A diferença é pequena e é exatamente ela que transforma "costuma cobrir" numa garantia:
    sem o ``+1``, a cobertura fica sistematicamente abaixo do nominal em amostras pequenas.

    Devolve 1.0 quando o nível pedido excede o que ``n`` pontos conseguem sustentar — o que é
    honesto (o conjunto passa a conter tudo) e não um erro silencioso.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha tem de estar em (0,1), recebi {alpha}")
    s = np.sort(np.asarray(scores, dtype=np.float64))
    n = s.size
    if n == 0:
        raise ValueError("não há pontos de calibração")
    rank = int(np.ceil((n + 1) * (1.0 - alpha)))
    if rank > n:
        # n pequeno demais para este alpha: nenhum limiar finito garante a cobertura.
        return 1.0
    return float(s[rank - 1])


def prediction_sets(probs_positive: np.ndarray, qhat: float) -> np.ndarray:
    """Conjuntos de predição como máscara booleana ``(n, 2)``, colunas = classes 0 e 1.

    A classe ``y`` entra no conjunto quando a sua não-conformidade não excede ``q̂``, isto é,
    quando ``p̂(y) ≥ 1 − q̂``.
    """
    p = np.asarray(probs_positive, dtype=np.float64).reshape(-1, 1)
    probs_by_class = np.hstack([1.0 - p, p])  # colunas: classe 0, classe 1
    return (1.0 - probs_by_class) <= qhat


def set_sizes(sets: np.ndarray) -> np.ndarray:
    """Quantos rótulos cada conjunto contém (0, 1 ou 2)."""
    return sets.sum(axis=1)


def empirical_coverage(sets: np.ndarray, labels: np.ndarray) -> float:
    """Fração de casos em que a classe verdadeira está no conjunto.

    É este o número que se compara com o 1−α nominal. Se ficar sistematicamente abaixo, a
    permutabilidade falhou — e isso é informação, não uma avaria.
    """
    y = np.asarray(labels).astype(int)
    if sets.shape[0] != y.size:
        raise ValueError(f"{sets.shape[0]} conjuntos para {y.size} rótulos")
    return float(sets[np.arange(y.size), y].mean())


@dataclass(frozen=True)
class ConformalReport:
    """O que uma corrida conformal produz, num só objeto."""

    alpha: float
    qhat: float
    coverage: float
    avg_set_size: float
    frac_singleton: float  # decisões definidas
    frac_both: float  # "não sei", declarado
    frac_empty: float  # nem uma classe é plausível
    n_cal: int
    n_eval: int

    @property
    def nominal(self) -> float:
        return 1.0 - self.alpha

    @property
    def covers(self) -> bool:
        """A cobertura empírica atinge o nominal?

        Com uma folga de tolerância de amostragem: a cobertura é ela própria uma estimativa
        sobre ``n_eval`` pontos, pelo que exigir igualdade exata seria exigir sorte. A folga
        é dois erros-padrão binomiais no nominal.
        """
        se = float(np.sqrt(self.nominal * self.alpha / max(self.n_eval, 1)))
        return self.coverage >= self.nominal - 2.0 * se


def run_split_conformal(
    probs_cal: np.ndarray,
    labels_cal: np.ndarray,
    probs_eval: np.ndarray,
    labels_eval: np.ndarray,
    alpha: float,
) -> ConformalReport:
    """Calibra num conjunto e mede a cobertura noutro. É a experiência inteira."""
    qhat = conformal_quantile(nonconformity(probs_cal, labels_cal), alpha)
    sets = prediction_sets(probs_eval, qhat)
    sizes = set_sizes(sets)
    return ConformalReport(
        alpha=alpha,
        qhat=qhat,
        coverage=empirical_coverage(sets, labels_eval),
        avg_set_size=float(sizes.mean()),
        frac_singleton=float((sizes == 1).mean()),
        frac_both=float((sizes == 2).mean()),
        frac_empty=float((sizes == 0).mean()),
        n_cal=int(np.asarray(probs_cal).size),
        n_eval=int(np.asarray(probs_eval).size),
    )
