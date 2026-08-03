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

import pytest

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


def test_cortar_a_serie_antes_ou_depois_de_detectar_da_o_mesmo() -> None:
    """A equivalência de que depende a optimização do `_replay`.

    O `_replay` deixou de receber o tamanho da janela mostrada — corria `detect_all` de
    novo a cada troca de intervalo, porque cada janela era uma chave de cache diferente.
    Agora corre uma vez sobre o ano e quem desenha filtra.

    Isso só é seguro porque a norma de `detect_all` é **causal**: o z do dia *i* usa os 20
    dias imediatamente antes dele, nunca a série inteira. Este teste é a afirmação em forma
    executável — detectar sobre a série toda e filtrar tem de dar exactamente os mesmos
    dias, com exactamente os mesmos z, que detectar só sobre a cauda. Uma optimização de
    desempenho que muda os números em silêncio é um defeito, não uma optimização.
    """
    import numpy as np
    import pandas as pd

    from investigator.anomaly_detector.detector import detect_all

    janela, cauda = 20, 60
    rng = np.random.default_rng(20260803)
    retornos = pd.Series(rng.normal(0, 0.015, 250),
                         index=pd.date_range("2025-08-01", periods=250, freq="B"))
    retornos.iloc[210] = 0.09  # garante pelo menos um dia sinalizado dentro da cauda

    inteiro = detect_all(retornos, window=janela, threshold=1.5)
    # A cauda leva `janela` dias de história atrás do primeiro dia visível — a mesma
    # margem que a versão anterior reservava com `tail(days + WINDOW + 5)`.
    parcial = detect_all(retornos.tail(cauda + janela), window=janela, threshold=1.5)

    visiveis = set(retornos.tail(cauda).index)
    filtrado = [(d, r) for d, r in inteiro if d in visiveis]
    so_da_cauda = [(d, r) for d, r in parcial if d in visiveis]

    assert filtrado, "o teste não prova nada se não houver dias sinalizados na janela"
    assert [d for d, _ in filtrado] == [d for d, _ in so_da_cauda]
    for (_, a), (_, b) in zip(filtrado, so_da_cauda, strict=True):
        assert a.z_score == pytest.approx(b.z_score)
        assert a.last_return == pytest.approx(b.last_return)


def test_config_e_lida_por_caminho_ancorado() -> None:
    """A watchlist não pode depender do directório de trabalho.

    Com um caminho relativo, lançar a app de outra pasta faz a leitura falhar; e como o
    caminho falha aberto, a lista de reserva apareceria **em silêncio** no lugar da
    watchlist configurada — um ecrã errado sem nenhuma mensagem de erro.
    """
    fonte = PAINEL.read_text(encoding="utf-8")
    assert 'open("config/alerts.yaml"' not in fonte
    assert '_ROOT / "config" / "alerts.yaml"' in fonte
