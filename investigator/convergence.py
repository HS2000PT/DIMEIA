"""Convergência multi-sinal: quantos sinais independentes apontam para o mesmo nome, hoje?

*De onde vem a ideia.* Adaptada de `worldmonitor.app`, recomendado pelo coorientador Rafael Silva.
O que lá se aproveita não é a escala (dezenas de camadas e de fornecedores de dados, fora do
âmbito de um projeto que só usa APIs gratuitas), é o **princípio**: um acontecimento em que
várias fontes independentes convergem merece mais atenção do que um em que só uma dispara.

*O que aqui se traduz.* O sistema já calcula quatro coisas sobre um par (ticker, dia) e trata-as
separadamente:

- o **preço** mexeu-se de forma invulgar para aquela ação (z-score do detetor);
- o **volume** foi invulgar (`anomaly_detector/volume.py`);
- houve **notícia**, e quanta (intensidade do fluxo nesse dia);
- a **triagem** achou o material provável (probabilidade calibrada do modelo congelado).

Cada um responde a uma pergunta diferente e nenhum vê os outros. Fundi-los pergunta se o
*acordo* entre eles vale mais do que o melhor deles isolado.

*A regra que este módulo respeita.* Os pesos **não são escolhidos à mão**. São derivados dos
dados por regressão logística ajustada na validação, pela mesma disciplina que transformou o
limiar de materialidade de constante arbitrária em ponto de operação derivado
(`docs/evaluation/evaluation_policy_sweep.md`). Um score de convergência com pesos inventados
seria exatamente o tipo de número que esta tese recusa mostrar.

*E se não ganhar?* Reporta-se que não ganhou. O projeto já tem registo de negativos honestos
(o texto não bate a volatilidade; cinco features de contexto não ajudaram), e um a mais não
enfraquece a tese: fortalece o que ela diz sobre os outros.

Puro: sem I/O, sem estado, sem sklearn em tempo de execução (os pesos entram já ajustados).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# Os sinais fundidos, por ordem fixa. A ordem é parte do contrato: os pesos são guardados
# posicionalmente, e trocá-la em silêncio trocaria o significado do score.
SIGNALS: tuple[str, ...] = ("price_z", "volume_z", "news_intensity", "triage_p")


@dataclass(frozen=True)
class ConvergenceWeights:
    """Pesos derivados dos dados, mais a normalização com que foram ajustados.

    A normalização viaja **com** os pesos de propósito. Um peso ajustado sobre sinais
    estandardizados não significa nada aplicado a sinais brutos, e separar as duas coisas é a
    forma mais fácil de produzir um score que parece correr bem e está errado.
    """

    coefficients: tuple[float, ...]
    intercept: float
    means: tuple[float, ...]
    stds: tuple[float, ...]
    names: tuple[str, ...] = SIGNALS

    def __post_init__(self) -> None:
        n = len(self.names)
        for attr in ("coefficients", "means", "stds"):
            if len(getattr(self, attr)) != n:
                raise ValueError(
                    f"{attr} tem {len(getattr(self, attr))} valores para {n} sinais"
                )

    def to_dict(self) -> dict:
        return {
            "names": list(self.names),
            "coefficients": list(self.coefficients),
            "intercept": self.intercept,
            "means": list(self.means),
            "stds": list(self.stds),
        }

    @classmethod
    def from_dict(cls, payload: dict) -> ConvergenceWeights:
        return cls(
            coefficients=tuple(payload["coefficients"]),
            intercept=float(payload["intercept"]),
            means=tuple(payload["means"]),
            stds=tuple(payload["stds"]),
            names=tuple(payload.get("names", SIGNALS)),
        )


@dataclass(frozen=True)
class ConvergenceScore:
    """O score de um par (ticker, dia), com a decomposição que o torna explicável."""

    score: float
    contributions: dict[str, float] = field(default_factory=dict)

    @property
    def driver(self) -> str:
        """O sinal que mais empurrou o score para cima.

        Só contribuições POSITIVAS podem ser o motor: um sinal que puxou o score para baixo não
        é a razão por que o alerta subiu. É o mesmo erro que foi corrigido na decomposição de
        retornos, onde escolher a maior componente em módulo dizia "foi o setor" quando o setor
        puxava ao contrário.
        """
        positivos = {k: v for k, v in self.contributions.items() if v > 0}
        if not positivos:
            return "none"
        return max(positivos.items(), key=lambda kv: kv[1])[0]


def _standardise(matrix: np.ndarray, means, stds) -> np.ndarray:
    mu = np.asarray(means, dtype=np.float64)
    sd = np.asarray(stds, dtype=np.float64)
    # Um sinal constante no ajuste tem desvio zero; dividir por ele daria inf. Fica a zero,
    # que é a leitura correta: um sinal sem variação não distingue nada.
    sd_safe = np.where(sd > 0, sd, 1.0)
    out = (np.asarray(matrix, dtype=np.float64) - mu) / sd_safe
    return np.where(np.isfinite(out), out, 0.0)


def score_matrix(signals: np.ndarray, weights: ConvergenceWeights) -> np.ndarray:
    """Score de convergência para muitas linhas de uma vez, em [0, 1]."""
    arr = np.atleast_2d(np.asarray(signals, dtype=np.float64))
    if arr.shape[1] != len(weights.names):
        raise ValueError(
            f"{arr.shape[1]} sinais recebidos, {len(weights.names)} esperados "
            f"({', '.join(weights.names)})"
        )
    z = _standardise(arr, weights.means, weights.stds)
    logit = z @ np.asarray(weights.coefficients, dtype=np.float64) + weights.intercept
    return 1.0 / (1.0 + np.exp(-logit))


def score_one(values: dict[str, float], weights: ConvergenceWeights) -> ConvergenceScore:
    """Score de um par (ticker, dia), com as contribuições aditivas por sinal.

    As contribuições são exatas e não aproximadas: o modelo é linear no log-odds, pelo que a
    contribuição de cada sinal é literalmente o seu termo na soma. É a mesma propriedade que
    torna a triagem explicável, e é a razão para o modelo de fusão ser linear.
    """
    faltam = set(weights.names) - set(values)
    if faltam:
        raise ValueError(f"sinais em falta: {sorted(faltam)}")
    row = np.array([[float(values[n]) for n in weights.names]], dtype=np.float64)
    z = _standardise(row, weights.means, weights.stds)[0]
    contribs = {
        name: float(z[i] * weights.coefficients[i]) for i, name in enumerate(weights.names)
    }
    logit = sum(contribs.values()) + weights.intercept
    return ConvergenceScore(score=float(1.0 / (1.0 + np.exp(-logit))), contributions=contribs)


def agreement_count(values: dict[str, float], thresholds: dict[str, float]) -> int:
    """Quantos sinais ultrapassam o seu próprio limiar — a leitura *humana* da convergência.

    O score fundido é o que ordena; este número é o que se mostra. "Três dos quatro sinais
    dispararam" comunica de imediato, e um utilizador consegue verificá-lo olhando para os
    componentes. Um score de 0,73 não se verifica de lado nenhum.
    """
    return sum(
        1 for name, limiar in thresholds.items()
        if name in values and np.isfinite(values[name]) and values[name] >= limiar
    )
