"""Anomalia de VOLUME: o mesmo z-score sem lookahead, aplicado ao volume negociado.

*Porquê existe.* O detetor de preço responde a "a ação mexeu-se muito?". Falta-lhe a segunda
metade da pergunta que qualquer operador faz a seguir: **"e mexeu-se com quanta gente a
negociar?"**. Um movimento de 3\% com volume normal e um movimento de 3\% com o triplo do volume
habitual não são o mesmo acontecimento, e o sistema não sabia distinguir os dois.

*Custo de dados: zero.* O volume já vem em todas as barras OHLCV que o sistema descarrega. Não é
uma fonte nova, é uma coluna que estava a ser deitada fora.

*A transformação logarítmica, e porquê.* O volume é fortemente assimétrico à direita e estritamente
positivo, pelo que um z-score sobre o valor bruto dispara quase só para cima e é dominado por
alguns dias enormes. Sobre ``log(volume)`` a distribuição fica aproximadamente simétrica e o
z-score volta a significar o que se espera que signifique. É a mesma razão pela qual os retornos
são logarítmicos noutro sítio do sistema.

*Assimetria deliberada na leitura.* Ao contrário do preço, onde ambas as direções interessam, só o
volume **acima** do normal é informativo: volume baixo significa quase sempre feriado, meia sessão
ou desinteresse, e não um acontecimento. `is_unusual` reflete isso e olha apenas para a cauda
superior. O z assinado continua disponível para quem o quiser.

Anti-lookahead pela mesma convenção do detetor de preço: a norma do dia *t* usa apenas dias
anteriores a *t*.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

# Chão de volume: uma barra com volume 0 ou negativo é dado corrompido ou uma sessão que não
# existiu. Entra como ausente em vez de rebentar o logaritmo.
MIN_VOLUME = 1.0


@dataclass(frozen=True)
class VolumeResult:
    """Quão invulgar foi o volume do dia mais recente, e contra que norma."""

    z_score: float
    last_volume: float
    median_volume: float
    window: int
    threshold: float

    @property
    def is_unusual(self) -> bool:
        """Só a cauda SUPERIOR conta.

        Volume anormalmente baixo é quase sempre um feriado ou meia sessão, não um
        acontecimento. Sinalizá-lo encheria o funil de ruído de calendário.
        """
        return self.z_score > self.threshold

    @property
    def ratio(self) -> float:
        """Volume do dia a dividir pela mediana da janela, que é o número legível.

        "3,2x o volume habitual" comunica; "z de +2,4 no log do volume" não. O rácio existe
        para o texto do alerta; o z existe para a decisão.
        """
        if self.median_volume <= 0:
            return float("nan")
        return self.last_volume / self.median_volume


def _log_volumes(volumes) -> pd.Series:
    v = pd.Series(list(volumes), dtype="float64")
    v = v.where(v >= MIN_VOLUME)  # 0, negativos e NaN passam a ausentes
    return v.map(lambda x: math.log(x) if pd.notna(x) else float("nan"))


def detect_volume_latest(volumes, window: int = 20, threshold: float = 2.0) -> VolumeResult:
    """z-score do volume do último dia contra a norma dos ``window`` dias anteriores.

    Args:
        volumes: série de volumes diários; o último elemento é o dia a avaliar.
        window: dias anteriores que formam a norma.
        threshold: z acima do qual o volume conta como invulgar.
    """
    logs = _log_volumes(volumes).dropna().reset_index(drop=True)
    if len(logs) < window + 1:
        raise ValueError(
            f"São precisos pelo menos {window + 1} volumes válidos (recebidos {len(logs)})."
        )

    raw = pd.Series(list(volumes), dtype="float64")
    raw = raw.where(raw >= MIN_VOLUME).dropna().reset_index(drop=True)

    recent = logs.iloc[-window - 1 : -1]  # janela ANTES do último (sem lookahead)
    last_log = float(logs.iloc[-1])
    mu = float(recent.mean())
    sigma = float(recent.std(ddof=1))
    z = (last_log - mu) / sigma if sigma > 0 else 0.0
    return VolumeResult(
        z_score=z,
        last_volume=float(raw.iloc[-1]),
        median_volume=float(raw.iloc[-window - 1 : -1].median()),
        window=window,
        threshold=threshold,
    )


def volume_z_series(volumes, window: int = 20) -> pd.Series:
    """z-score do volume para CADA dia da série, com a mesma norma causal.

    Devolve NaN nos primeiros ``window`` dias, onde não há norma suficiente. Existe para a
    avaliação offline poder pontuar a série inteira sem chamar `detect_volume_latest` num ciclo
    (que recalcularia a janela a cada passo).
    """
    logs = _log_volumes(volumes)
    # shift(1) é o que garante a ausência de lookahead: a norma do dia t termina em t-1.
    prev = logs.shift(1)
    mu = prev.rolling(window, min_periods=window).mean()
    sigma = prev.rolling(window, min_periods=window).std(ddof=1)
    z = (logs - mu) / sigma.where(sigma > 0)
    return z.rename("volume_z")
