"""Avaliação da QI4 — duas métricas, porque uma só mediria o braço errado.

A §5.3 avalia a recuperação pela **pertença ao setor**. É uma aproximação verificável à
relevância, e serve o que a §5.3 pergunta. Mas não sabe nada sobre materialidade: um
codificador ajustado para aproximar movimentos de grandeza parecida pode descer nessa métrica
e, ao mesmo tempo, estar a fazer exactamente aquilo para que foi treinado. Avaliar o braço
principal só por setor seria julgá-lo pela métrica de outro trabalho.

Por isso duas métricas, sobre as mesmas consultas e o mesmo protocolo:

- **comparabilidade de materialidade** — diferença média, em pontos, entre a grandeza do
  movimento da consulta e a dos precedentes devolvidos. Menor é melhor;
- **precisão@k por setor** — a métrica da §5.3, para mostrar o que o ajuste custa (ou não) em
  relevância temática.

As máscaras são as da tese: nunca a própria empresa; na variante causal, nunca um candidato
com data igual ou posterior à da consulta — que é a restrição sob a qual o sistema implantado
vive, conforme a §4.6.1.
"""

from __future__ import annotations

import numpy as np


def amostrar_consultas(n_total: int, n_consultas: int, seed: int) -> np.ndarray:
    """Índices distintos das consultas, fixados pela semente."""
    rng = np.random.default_rng(seed)
    return rng.choice(n_total, size=min(n_consultas, n_total), replace=False)


def mascara(consultas: np.ndarray, tickers: np.ndarray, datas: np.ndarray | None,
            datas_consulta: np.ndarray | None) -> np.ndarray:
    """Matriz `(n_consultas, n_candidatos)` de elegibilidade.

    Exclui sempre os candidatos da mesma empresa — o que exclui também a própria consulta.
    Com `datas`, exclui ainda tudo o que não seja **estritamente anterior**: o mesmo dia conta
    como futuro, porque o desfecho do dia ainda não é conhecido quando a notícia sai.
    """
    m = tickers[None, :] != tickers[consultas][:, None]
    if datas is not None and datas_consulta is not None:
        m &= datas[None, :] < datas_consulta[:, None]
    return m


def topo_k(vetores: np.ndarray, consultas: np.ndarray, tickers: np.ndarray, k: int,
           datas: np.ndarray | None, datas_consulta: np.ndarray | None = None) -> np.ndarray:
    """Índices dos `k` candidatos mais próximos por cosseno, respeitando a máscara.

    Os vetores entram normalizados, pelo que o produto interno é o cosseno. Candidatos
    inelegíveis recebem `-inf` em vez de serem removidos: mantém a matriz rectangular e o
    índice original, que é o que as métricas depois usam.
    """
    sims = vetores[consultas] @ vetores.T
    elegivel = mascara(consultas, tickers, datas,
                       datas_consulta if datas_consulta is not None
                       else (datas[consultas] if datas is not None else None))
    sims = np.where(elegivel, sims, -np.inf)
    return np.argsort(-sims, axis=1)[:, :k]


def comparabilidade(grandeza_consulta: np.ndarray, grandeza_vizinhos: np.ndarray) -> float:
    """Diferença média absoluta de grandeza entre a consulta e os seus vizinhos.

    À mão: consulta a 5%, vizinhos a 3% e 6% dão `(|5−3| + |5−6|)/2 = 1,5` pontos, ou seja
    `0,015` nas unidades em que os retornos entram.
    """
    return float(np.mean(np.abs(grandeza_vizinhos - grandeza_consulta[:, None])))


def precisao_setor(consultas: np.ndarray, vizinhos: np.ndarray,
                   setores: np.ndarray) -> float:
    """Fração dos vizinhos que pertencem ao setor da consulta."""
    return float(np.mean(setores[vizinhos] == setores[consultas][:, None]))
