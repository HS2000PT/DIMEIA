"""Ajuste do codificador da QI4 — treinar o modelo, não uma cabeça por cima dele.

É aqui que esta extensão se separa de [Jeong26], que treinou uma cabeça siamesa sobre
embeddings **congelados** do FinBERT e reportou separação ao nível do acaso, declarando o
descongelamento como limitação por custo. Neste trabalho o codificador é ajustado.

Duas decisões declaradas, ambas com alternativa medida em vez de assumida:

**A perda.** Por omissão a `CoSENT`, que ordena pares por similaridade graduada e não impõe
uma escala à saída do cosseno. A alternativa clássica, `CosineSimilarityLoss`, minimiza o erro
quadrático entre o cosseno e o alvo — é mais fácil de explicar mas obriga o cosseno a viver na
escala do alvo. Correm-se as duas; a §5.5 reporta a diferença.

**O modelo base.** O braço principal e o de replicação partem do mesmo `all-MiniLM-L6-v2` que
a tese usa, para que a comparação com a §5.3 seja de igual para igual. O braço de controlo
parte de um codificador de domínio.

A reprodutibilidade é tratada como requisito: `fixar_sementes` cobre o `random`, o `numpy` e o
`torch`, e o manifesto guarda a configuração inteira ao lado dos pesos.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd

#: Perdas disponíveis. A chave é o nome que aparece no manifesto e nos relatórios.
PERDAS = ("cosent", "cosseno")

#: Modelo base do braço principal e do de replicação — o mesmo da §5.3, de propósito.
BASE_PADRAO = "all-MiniLM-L6-v2"


def fixar_sementes(seed: int) -> None:
    """Fixa as três fontes de aleatoriedade que este treino usa."""
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(False)  # CPU: já é determinístico; evita recusas


def exemplos(pares: pd.DataFrame):
    """Converte o quadro de pares nos objetos que a biblioteca de treino consome."""
    from sentence_transformers import InputExample

    return [
        InputExample(texts=[str(a), str(b)], label=float(t))
        for a, b, t in zip(pares["texto_a"], pares["texto_b"], pares["alvo"], strict=True)
    ]


def _perda(nome: str, modelo):
    try:  # sentence-transformers >= 5.6 mudou o caminho do módulo
        from sentence_transformers.sentence_transformer import losses
    except ImportError:  # pragma: no cover - versões anteriores
        from sentence_transformers import losses

    if nome not in PERDAS:
        raise ValueError(f"perda desconhecida: {nome!r}; esperado um de {PERDAS}")
    return (losses.CoSENTLoss(modelo) if nome == "cosent"
            else losses.CosineSimilarityLoss(modelo))


def ajustar(pares: pd.DataFrame, *, saida: Path | str, modelo_base: str = BASE_PADRAO,
            epocas: int = 1, lote: int = 32, taxa: float = 2e-5, seed: int = 42,
            perda: str = "cosent", passos_max: int | None = None) -> dict:
    """Ajusta o codificador sobre os pares e grava-o, com o manifesto ao lado.

    Args:
        pares: quadro de `investigator.qi4.pares.construir_pares`.
        saida: pasta onde o modelo ajustado é gravado.
        modelo_base: ponto de partida (o da tese, ou um codificador de domínio).
        epocas, lote, taxa: hiperparâmetros do treino.
        seed: fixa amostragem, inicialização e ordem dos lotes.
        perda: `cosent` (por omissão) ou `cosseno`.
        passos_max: corta o treino a este número de passos. Serve os testes; em produção fica
            a `None` para que o número de passos seja o que as épocas ditam.

    Returns:
        O manifesto: configuração, dimensão do treino, duração e caminho dos pesos.
    """
    if perda not in PERDAS:
        raise ValueError(f"perda desconhecida: {perda!r}; esperado um de {PERDAS}")

    from sentence_transformers import SentenceTransformer
    from torch.utils.data import DataLoader

    fixar_sementes(seed)
    modelo = SentenceTransformer(modelo_base)
    dados = exemplos(pares)
    carregador = DataLoader(dados, shuffle=True, batch_size=lote, drop_last=False)
    objetivo = _perda(perda, modelo)

    passos_por_epoca = passos_max if passos_max is not None else len(carregador)
    t0 = time.time()
    modelo.fit(
        train_objectives=[(carregador, objetivo)],
        epochs=epocas,
        steps_per_epoch=passos_por_epoca,
        warmup_steps=max(1, int(0.1 * passos_por_epoca * epocas)),
        optimizer_params={"lr": taxa},
        show_progress_bar=False,
    )
    duracao = time.time() - t0

    destino = Path(saida)
    destino.mkdir(parents=True, exist_ok=True)
    modelo.save(str(destino))

    manifesto = {
        "modelo_base": modelo_base,
        "perda": perda,
        "epocas": epocas,
        "lote": lote,
        "taxa": taxa,
        "seed": seed,
        "n_pares": int(len(pares)),
        "passos_por_epoca": int(passos_por_epoca),
        "segundos": round(duracao, 1),
        "dim": int(modelo.get_embedding_dimension()
                   if hasattr(modelo, "get_embedding_dimension")
                   else modelo.get_sentence_embedding_dimension()),
    }
    (destino / "manifesto_qi4.json").write_text(
        json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifesto
