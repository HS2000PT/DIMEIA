"""O verificador de escapes tem de VER um CR solto, e nao so um TAB.

Porque e que este teste existe. O `check_tex_escapes.py` lia os .tex com
`Path.read_text`, que em modo de texto traduz mudancas de linha. Um `\\r`
solto (que e exactamente o que o escape de `\\ref` deixa para tras) chegava
la dentro ja convertido, e o verificador ficava cego a metade dos defeitos
que existe para apanhar: acusava `\\textbf` partido e deixava passar `\\ref`
partido. Aconteceu, e so se viu porque o defeito estava mesmo la.

Um verificador cego e um corpus limpo sao indistinguiveis no ecra, e por isso
a garantia tem de ser um teste que planta os dois defeitos e exige os dois.
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
VERIFICADOR = RAIZ / "scripts" / "check_tex_escapes.py"

CR = chr(13)
TAB = chr(9)


def _corre(dir_tex: Path) -> subprocess.CompletedProcess:
    """Corre o verificador com ALVOS apontado a um directorio de teste."""
    codigo = (
        "import runpy, sys, pathlib\n"
        "sys.argv = ['check_tex_escapes.py']\n"
        f"mod = runpy.run_path(r'{VERIFICADOR}', run_name='nao_main')\n"
        "g = mod['main'].__globals__\n"
        f"g['RAIZ'] = pathlib.Path(r'{dir_tex.parent}')\n"
        f"g['ALVOS'] = [r'{dir_tex.name}']\n"
        "sys.exit(mod['main']())\n"
    )
    return subprocess.run(
        [sys.executable, "-c", codigo], capture_output=True, text=True, encoding="utf-8"
    )


def test_apanha_um_ref_partido_por_um_CR(tmp_path):
    """O caso que escapava: CR + 'ef', que e o que sobra de um \\ref comido."""
    d = tmp_path / "tese"
    d.mkdir()
    (d / "c.tex").write_bytes(("Ver a Seccao~" + CR + "ef{sec:x}.\n").encode("utf-8"))

    r = _corre(d)
    assert r.returncode != 0, "um \\ref partido tem de fazer a porta falhar"
    assert "'ef'" in r.stdout


def test_apanha_um_textbf_partido_por_um_TAB(tmp_path):
    """O caso que ja era apanhado, mantido para a correccao nao trocar um pelo outro."""
    d = tmp_path / "tese"
    d.mkdir()
    (d / "c.tex").write_bytes(("Isto e " + TAB + "extbf{importante}.\n").encode("utf-8"))

    r = _corre(d)
    assert r.returncode != 0
    assert "extbf" in r.stdout


def test_nao_grita_sobre_um_ficheiro_limpo(tmp_path):
    """Controlo no sentido oposto: sem isto, um verificador que acusa tudo passaria."""
    d = tmp_path / "tese"
    d.mkdir()
    limpo = "Ver a Secção~" + chr(92) + "ref{sec:x}, a " + chr(92) + "textbf{negrito}.\n"
    (d / "c.tex").write_bytes(limpo.encode("utf-8"))

    r = _corre(d)
    assert r.returncode == 0, r.stdout


def test_ficheiros_com_fim_de_linha_do_windows_nao_sao_falsos_positivos(tmp_path):
    """CRLF e normal num repositorio em Windows: so o CR SOLTO e defeito."""
    d = tmp_path / "tese"
    d.mkdir()
    linha = "Ver a Secção " + chr(92) + "ref{sec:x}."
    (d / "c.tex").write_bytes((linha + "\r\n" + linha + "\r\n").encode("utf-8"))

    r = _corre(d)
    assert r.returncode == 0, r.stdout
