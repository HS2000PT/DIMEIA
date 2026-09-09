"""QI4 — o ajuste do codificador: conversão, sementes e um treino mínimo a sério.

Os testes rápidos cobrem as partes puras. O último faz **um passo de treino real** sobre o
modelo da tese: é lento para um teste unitário, mas é a única forma de provar que a montagem
inteira liga — biblioteca, perda, carregador, gravação e manifesto. Sem ele, o resto podia
estar todo verde com um treino que nunca correu.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from investigator.qi4 import ajuste as A


def pares(n: int = 8) -> pd.DataFrame:
    return pd.DataFrame({
        "texto_a": [f"manchete a {i}" for i in range(n)],
        "texto_b": [f"manchete b {i}" for i in range(n)],
        "alvo": [i / (n - 1) for i in range(n)],
    })


def test_a_conversao_preserva_textos_e_alvos():
    p = pares(5)
    ex = A.exemplos(p)
    assert len(ex) == 5
    assert ex[0].texts == ["manchete a 0", "manchete b 0"]
    assert ex[4].label == pytest.approx(1.0)


def test_a_mesma_semente_da_a_mesma_inicializacao():
    import torch

    A.fixar_sementes(7)
    a = torch.randn(4)
    A.fixar_sementes(7)
    b = torch.randn(4)
    assert torch.equal(a, b)


def test_sementes_diferentes_dao_valores_diferentes():
    import torch

    A.fixar_sementes(7)
    a = torch.randn(4)
    A.fixar_sementes(8)
    b = torch.randn(4)
    assert not torch.equal(a, b)


def test_recusa_uma_perda_desconhecida():
    with pytest.raises(ValueError, match="perda"):
        A.ajustar(pares(), saida="/tmp/nao-usado", perda="triplo")


@pytest.mark.sbert
def test_um_passo_de_treino_a_serio_produz_um_modelo_utilizavel(tmp_path):
    """Integração: um passo, e o que sai tem de carregar e codificar.

    Usa a marca `sbert` que o `pyproject.toml` já exclui do ciclo rápido, porque carrega o
    modelo da tese e corre uma retropropagação. Corre com `pytest -m sbert`.
    """
    from sentence_transformers import SentenceTransformer

    destino = tmp_path / "modelo"
    man = A.ajustar(pares(8), saida=destino, epocas=1, lote=4, passos_max=1, seed=42)

    assert man["n_pares"] == 8
    assert man["passos_por_epoca"] == 1
    assert man["dim"] == 384
    assert man["perda"] == "cosent"
    assert json.loads((destino / "manifesto_qi4.json").read_text(encoding="utf-8")) == man

    recarregado = SentenceTransformer(str(destino))
    v = recarregado.encode(["uma manchete qualquer"])
    assert v.shape == (1, 384)
