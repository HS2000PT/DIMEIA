"""Deteção de deriva de distribuição — PSI e Kolmogorov-Smirnov de duas amostras.

*A lacuna que fecha.* O modelo de triagem foi treinado em FNSPID 2018-2023 e corre em 2026.
A tese **afirma** essa distância como limitação, mas nunca a **mediu**. Uma limitação afirmada
é uma opinião; uma limitação medida é um resultado.

*Duas medidas, de propósito, porque veem coisas diferentes.*

- O **PSI** (Population Stability Index) compara massas por intervalo. É o padrão de facto em
  risco de crédito, tem bandas de interpretação convencionadas, e é fácil de explicar: quanto
  é que a massa se mudou de sítio.
- O **KS** compara funções de distribuição acumulada e devolve um valor-p. É sensível a
  desvios que o PSI dilui — nomeadamente deslocações pequenas mas sistemáticas.

Uma amostra grande faz o KS rejeitar quase sempre, e por isso o valor-p sozinho é quase
inútil aqui. O que se lê é a **estatística** D (o tamanho do efeito) ao lado do PSI. Reportar
só o valor-p seria transformar "a amostra é grande" em "a deriva é grave".

NumPy puro (o KS usa `scipy` só se estiver disponível; caso contrário calcula D à mão e
declara o valor-p indisponível, em vez de fingir um).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Bandas convencionais do PSI, herdadas da prática de risco de crédito.
PSI_STABLE = 0.10
PSI_MODERATE = 0.25


def _bin_edges(reference: np.ndarray, bins: int) -> np.ndarray:
    """Arestas por quantis da REFERÊNCIA, com duplicados colapsados.

    Quantis e não larguras iguais: com features financeiras muito assimétricas (a
    volatilidade é sempre positiva e tem cauda longa), intervalos de largura igual põem quase
    tudo no primeiro e o PSI fica dominado por ruído nos intervalos vazios.
    """
    qs = np.linspace(0.0, 1.0, bins + 1)
    edges = np.unique(np.quantile(np.asarray(reference, dtype=np.float64), qs))
    if edges.size < 2:  # feature constante na referência
        edges = np.array([edges[0] - 0.5, edges[0] + 0.5])
    edges[0], edges[-1] = -np.inf, np.inf
    return edges


def population_stability_index(
    reference: np.ndarray, current: np.ndarray, bins: int = 10
) -> float:
    """PSI entre uma distribuição de referência e uma atual.

    ``PSI = Σ (p_atual − p_ref) · ln(p_atual / p_ref)``, simétrico e sempre ≥ 0.

    Intervalos vazios recebem um epsilon em vez de produzirem ``inf``: um intervalo que a
    amostra atual não visitou é informação sobre deriva, não uma divisão por zero, e deixar o
    PSI ir a infinito apagaria todo o resto do sinal.
    """
    ref = np.asarray(reference, dtype=np.float64)
    cur = np.asarray(current, dtype=np.float64)
    ref = ref[np.isfinite(ref)]
    cur = cur[np.isfinite(cur)]
    if ref.size == 0 or cur.size == 0:
        return float("nan")

    edges = _bin_edges(ref, bins)
    ref_counts, _ = np.histogram(ref, bins=edges)
    cur_counts, _ = np.histogram(cur, bins=edges)

    eps = 1e-6
    p_ref = np.maximum(ref_counts / ref.size, eps)
    p_cur = np.maximum(cur_counts / cur.size, eps)
    return float(np.sum((p_cur - p_ref) * np.log(p_cur / p_ref)))


def psi_band(psi: float) -> str:
    """A leitura convencionada do PSI."""
    if not np.isfinite(psi):
        return "n/a"
    if psi < PSI_STABLE:
        return "estável"
    if psi < PSI_MODERATE:
        return "moderada"
    return "significativa"


def ks_statistic(reference: np.ndarray, current: np.ndarray) -> tuple[float, float | None]:
    """Estatística D de Kolmogorov-Smirnov e, se possível, o valor-p.

    D é a distância vertical máxima entre as duas acumuladas: um **tamanho de efeito** em
    [0,1], que não cresce só por a amostra ser grande. É esse o número a ler.
    """
    ref = np.asarray(reference, dtype=np.float64)
    cur = np.asarray(current, dtype=np.float64)
    ref = ref[np.isfinite(ref)]
    cur = cur[np.isfinite(cur)]
    if ref.size == 0 or cur.size == 0:
        return float("nan"), None
    try:
        from scipy.stats import ks_2samp

        out = ks_2samp(ref, cur)
        return float(out.statistic), float(out.pvalue)
    except ImportError:
        # D à mão; sem valor-p, e a dizê-lo, em vez de inventar um.
        todos = np.sort(np.concatenate([ref, cur]))
        cdf_ref = np.searchsorted(np.sort(ref), todos, side="right") / ref.size
        cdf_cur = np.searchsorted(np.sort(cur), todos, side="right") / cur.size
        return float(np.max(np.abs(cdf_ref - cdf_cur))), None


@dataclass(frozen=True)
class FeatureDrift:
    """Veredicto de deriva para uma feature."""

    name: str
    psi: float
    ks_d: float
    ks_p: float | None
    ref_mean: float
    cur_mean: float
    ref_std: float
    cur_std: float
    n_ref: int
    n_cur: int

    @property
    def band(self) -> str:
        return psi_band(self.psi)

    @property
    def mean_shift_sd(self) -> float:
        """Deslocação da média em desvios-padrão da referência.

        Comparável entre features com unidades diferentes, que é o que permite dizer qual
        derivou *mais* sem comparar volatilidade com número de caracteres.
        """
        if not np.isfinite(self.ref_std) or self.ref_std <= 0:
            return float("nan")
        return (self.cur_mean - self.ref_mean) / self.ref_std


def compare_distributions(
    reference: dict[str, np.ndarray],
    current: dict[str, np.ndarray],
    bins: int = 10,
) -> list[FeatureDrift]:
    """Deriva feature a feature, ordenada pela mais grave primeiro."""
    faltam = set(reference) ^ set(current)
    if faltam:
        raise ValueError(f"features desemparelhadas entre referência e atual: {sorted(faltam)}")

    saida: list[FeatureDrift] = []
    for name in reference:
        ref = np.asarray(reference[name], dtype=np.float64)
        cur = np.asarray(current[name], dtype=np.float64)
        d, p = ks_statistic(ref, cur)
        saida.append(
            FeatureDrift(
                name=name,
                psi=population_stability_index(ref, cur, bins),
                ks_d=d,
                ks_p=p,
                ref_mean=float(np.nanmean(ref)),
                cur_mean=float(np.nanmean(cur)),
                ref_std=float(np.nanstd(ref)),
                cur_std=float(np.nanstd(cur)),
                n_ref=int(np.isfinite(ref).sum()),
                n_cur=int(np.isfinite(cur).sum()),
            )
        )
    return sorted(saida, key=lambda f: (-f.psi if np.isfinite(f.psi) else 0.0))
