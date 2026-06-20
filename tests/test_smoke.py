"""Smoke test placeholder — garante que a verificação corre verde desde a Sessão 0.

Substituído/expandido pelo smoke test real da thin slice (~Sessão 10).
"""

import importlib


def test_pacote_src_importavel():
    """O pacote src deve ser importável (esqueleto presente)."""
    assert importlib.import_module("src") is not None
