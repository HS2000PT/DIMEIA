"""Intervalos de confiança para proporções — a estatística partilhada por quem reporta taxas.

**Porque existe como módulo e não como função privada de um script.** O `_wilson` do
`scripts/analyse_usefulness.py` foi escrito para o estudo moderado e testado lá. A análise do
feedback do Telegram precisa exatamente do mesmo intervalo, e copiá-lo criava duas
implementações da mesma estatística — que é a classe de defeito que este projeto já pagou três
vezes noutros sítios, e a pior possível num número que vai para a dissertação.

**Porque Wilson e não o intervalo normal.** Com N pequeno o intervalo normal é errado nos
extremos de uma forma que se vê a olho: com oito acertos em oito dá largura zero, ou seja
afirma certeza absoluta a partir de oito observações. O de Wilson é assimétrico perto de 0 e
de 1 e continua a comportar-se com N de uma dezena, que é a ordem de grandeza que qualquer
piloto desta dimensão vai ter.
"""

from __future__ import annotations

import math


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de Wilson a 95% para uma proporção `k/n`. `(nan, nan)` se `n` for zero.

    Zero observações não são uma proporção de zero: são a ausência de proporção. Devolver
    `(0, 0)` faria um relatório imprimir «0% [0%–0%]» onde a verdade é «ainda não há dados».
    """
    if n <= 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    margem = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centro - margem), min(1.0, centro + margem))


def intervalos_sobrepoem(a: tuple[float, float], b: tuple[float, float]) -> bool:
    """True se dois intervalos se sobrepõem.

    ⚠️ Não sobreposição implica diferença; **sobreposição não implica ausência de diferença**.
    É por isso que esta função só é usada para recusar uma afirmação, nunca para a sustentar:
    com intervalos sobrepostos o relatório escreve «não é possível distinguir», e não «são
    iguais».
    """
    if any(math.isnan(v) for v in (*a, *b)):
        return True  # sem dados não se distingue nada
    return not (a[1] < b[0] or b[1] < a[0])
