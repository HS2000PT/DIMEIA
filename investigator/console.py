"""Utilitário de consola partilhado pelos pontos de entrada (demo, runner de alertas).

No Windows a consola usa `cp1252` e rebenta ao imprimir os emojis dos alertas (📰, ⚠️).
Forçar UTF-8 no stdout resolve; noutras plataformas é um no-op inofensivo.
"""

from __future__ import annotations

import sys


def force_utf8_stdout() -> None:
    """Reconfigura o stdout para UTF-8 (seguro chamar em qualquer plataforma)."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass  # stdout substituído (testes/pipes) ou sem reconfigure — segue sem forçar
