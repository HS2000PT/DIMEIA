"""Quão raro é o movimento de hoje, contado nos dados em vez de assumido.

**O problema que isto resolve.** O z-score é a estatística com que o detector dispara, mas
não é legível: quando o aluno reviu o painel, "não sei o que os números querem dizer" foi
uma das quatro queixas. A tradução óbvia — converter z numa probabilidade ("há 0,2% de
hipótese de um movimento destes") — seria **desonesta**: exige assumir normalidade, e os
retornos diários de acções têm caudas pesadas, portanto essa probabilidade estaria errada
precisamente nos dias que interessam.

**A alternativa, que não assume nada.** Contar. *"6 dos últimos 248 dias de negociação
moveram-se pelo menos isto."* É uma afirmação sobre uma amostra observada, verificável por
qualquer pessoa com a mesma série de preços, e descreve o passado — pelo que respeita a
mesma regra que o resto do produto (medir o desfecho ≠ prever o próximo).

**Três decisões que parecem detalhes e não são:**

1. **Hoje fica de fora da contagem.** Incluí-lo tornaria a contagem ≥1 por construção, e
   "o maior movimento do ano" passaria a ser impossível de dizer mesmo quando é verdade.
2. **O `n` vem dos dados, nunca da constante.** Uma série curta tem de dizer "58 dias", não
   "250". Escrever o número da janela à mão é como se inventa um facto sem dar por isso.
3. **A contagem é em módulo (dois lados).** A pergunta do investidor é "um movimento *deste
   tamanho*", não "uma queda desta". A direcção é reportada à parte, em `same_direction`,
   para quem a quiser.

**Isto não substitui o z-score.** São réguas diferentes e podem discordar: o z mede contra
os **20 dias anteriores**, a contagem contra o **ano**. Uma acção num período calmo pode ter
z = +3,2 e ainda assim ser só o 15.º maior movimento do ano — e isso não é uma contradição,
é uma afirmação sobre o regime recente, que vale a pena dizer em voz alta.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# Abaixo disto a contagem não diz nada de útil: com 20 observações, "2 dos últimos 19 dias"
# é ruído. Devolver None e não mostrar frase nenhuma é melhor do que mostrar uma fraca.
MIN_OBSERVACOES = 30
LOOKBACK = 250  # ~um ano de sessões


@dataclass(frozen=True)
class Exceedance:
    """Quantos dias do passado recente se moveram pelo menos tanto como hoje."""

    move: float  # o retorno de hoje (log), com sinal
    n: int  # dias ANTERIORES considerados — o que se escreve na frase
    count: int  # quantos desses igualaram ou excederam |move|
    same_direction: int  # …e destes, quantos foram no mesmo sentido

    @property
    def is_record(self) -> bool:
        """Nenhum dia anterior da janela se moveu tanto."""
        return self.count == 0

    @property
    def share(self) -> float:
        """Fracção da janela que igualou ou excedeu. `count/n`, em [0, 1]."""
        return self.count / self.n if self.n else float("nan")


def empirical_exceedance(
    returns, lookback: int = LOOKBACK, min_obs: int = MIN_OBSERVACOES
) -> Exceedance | None:
    """Conta os dias anteriores que se moveram pelo menos tanto como o último.

    Args:
        returns: série de retornos; o ÚLTIMO é o dia a caracterizar. A mesma série que
            `detect_latest` pontua, para as duas afirmações não poderem divergir.
        lookback: quantos dias ANTERIORES no máximo entram na contagem.
        min_obs: abaixo disto devolve `None` em vez de uma frase sem força.

    Returns:
        `Exceedance`, ou `None` se não houver história suficiente.
    """
    serie = pd.Series(returns, dtype="float64").dropna()
    if len(serie) < 2:
        return None

    valores = serie.to_numpy()
    hoje = float(valores[-1])
    # `[-(lookback+1):-1]` — a janela anterior, com o dia de hoje EXCLUÍDO.
    anteriores = valores[-(lookback + 1) : -1]
    n = int(anteriores.size)
    if n < min_obs:
        return None

    magnitude = np.abs(anteriores) >= abs(hoje)
    return Exceedance(
        move=hoje,
        n=n,
        count=int(magnitude.sum()),
        same_direction=int((magnitude & (anteriores * hoje > 0)).sum()),
    )
