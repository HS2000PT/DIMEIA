"""O painel tem de arrancar como o `streamlit run` o arranca — não como eu o testei.

Este ficheiro existe por causa de um defeito real: a app foi verificada com
`python -m streamlit`, e o `-m` acrescenta o directório actual ao `sys.path`. O comando
normal, `streamlit run app/dashboard.py`, põe lá a pasta **do script** (`app/`) e mais
nada, por isso `from app import ui_tokens` rebentava com `ModuleNotFoundError` na primeira
execução verdadeira. A verificação passou porque reproduzia a coisa errada.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PAINEL = RAIZ / "app" / "dashboard.py"


def test_importa_sem_a_raiz_no_path() -> None:
    """Carrega o módulo com o `sys.path` que o `streamlit run` monta.

    Subprocesso e não `importlib` aqui mesmo: a suite corre com a raiz já no caminho, e
    dentro deste processo o defeito era invisível — que é exactamente como ele escapou.
    """
    guiao = (
        "import sys, importlib.util\n"
        # exactamente o que o `streamlit run` faz: só a pasta do script.
        f"sys.path = [r'{PAINEL.parent}'] + [p for p in sys.path[1:]"
        f" if p and p != r'{RAIZ}']\n"
        f"spec = importlib.util.spec_from_file_location('dashboard', r'{PAINEL}')\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n"
        "assert hasattr(mod, 'main')\n"
        "print('OK')\n"
    )
    res = subprocess.run(  # noqa: S603
        [sys.executable, "-c", guiao], capture_output=True, text=True, timeout=180,
        cwd=str(RAIZ.parent),  # de outra pasta, como quem lança de fora do repositório
    )
    assert res.returncode == 0, f"o painel não arranca:\n{res.stderr[-1500:]}"
    assert "OK" in res.stdout


def test_config_e_lida_por_caminho_ancorado() -> None:
    """A watchlist não pode depender do directório de trabalho.

    Com um caminho relativo, lançar a app de outra pasta faz a leitura falhar; e como o
    caminho falha aberto, a lista de reserva apareceria **em silêncio** no lugar da
    watchlist configurada — um ecrã errado sem nenhuma mensagem de erro.
    """
    fonte = PAINEL.read_text(encoding="utf-8")
    assert 'open("config/alerts.yaml"' not in fonte
    assert '_ROOT / "config" / "alerts.yaml"' in fonte
