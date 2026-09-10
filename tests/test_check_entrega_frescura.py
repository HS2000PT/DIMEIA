"""A porta de frescura tem de VER um capítulo mais recente do que o PDF entregue.

Porque é que este ficheiro existe. A 2026-09-10 a porta comparava ``main.tex`` contra
``main.pdf`` e mais nada. O ``main.tex`` não é tocado há sessões — cada capítulo vive em
``chN/chapterN.tex`` — pelo que a comparação **passava sempre**. Nesse dia editei o
``ch2/chapter2.tex`` às 20:05, o ``main.pdf`` versionado ficou das 19:42, e a porta imprimiu
«143 páginas, compila limpo, **mais recente do que a fonte**» sobre um PDF vinte e três minutos
mais antigo do que a fonte.

⚠️ **Só se viu porque os PDF não apareceram no ``git diff``.** Sem isso, o repositório teria
entregado um PDF que não corresponde ao ``.tex`` — que é exactamente o que esta porta existe para
impedir, e é a classe que este projecto documenta desde a sessão 63: não encontrar nada e aprovar
tudo têm o mesmo aspecto no ecrã.

⚠️ E a árvore **inglesa** não estava na lista, logo a frescura do PDF inglês nunca foi verificada.

O controlo que decide está no ``test_o_build_nao_torna_o_pdf_fresco_por_construcao``: incluir o
``build/`` na varredura faria o PDF parecer fresco sempre, porque é lá que o ``latexmk`` escreve.
Seria a mesma cegueira por outro caminho.
"""

from __future__ import annotations

import os
import pathlib
import runpy
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "scripts" / "check_entrega.py"


@pytest.fixture(scope="module")
def mod():
    guardado = sys.argv
    sys.argv = [str(SCRIPT)]
    try:
        return runpy.run_path(str(SCRIPT))
    finally:
        sys.argv = guardado


def _tex(p: pathlib.Path, quando: float) -> pathlib.Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("olá", encoding="utf-8")
    os.utime(p, (quando, quando))
    return p


def test_escolhe_o_capitulo_e_nao_o_main(tmp_path, mod):
    """⚠️ O DEFEITO EXACTO DE 2026-09-10: o main.tex velho, um capítulo recente."""
    _tex(tmp_path / "main.tex", 1_000_000.0)
    _tex(tmp_path / "ch2" / "chapter2.tex", 2_000_000.0)
    fonte, quando = mod["fonte_mais_recente"](tmp_path)
    assert fonte is not None and fonte.name == "chapter2.tex"
    assert quando == 2_000_000.0


def test_o_build_nao_torna_o_pdf_fresco_por_construcao(tmp_path, mod):
    """⚠️ O CONTROLO QUE DECIDE. O `latexmk` escreve no `build/`; contá-lo apagava a porta."""
    _tex(tmp_path / "ch2" / "chapter2.tex", 2_000_000.0)
    _tex(tmp_path / "build" / "main.tex", 9_000_000.0)
    fonte, quando = mod["fonte_mais_recente"](tmp_path)
    assert fonte is not None and "build" not in fonte.parts
    assert quando == 2_000_000.0


def test_arvore_sem_tex_e_reportada_e_nao_aprovada(tmp_path, mod):
    """Um corpus vazio não pode ler-se como corpus limpo — é a lição da sessão 63."""
    fonte, quando = mod["fonte_mais_recente"](tmp_path)
    assert fonte is None
    assert quando == 0.0


def test_as_duas_arvores_da_tese_estao_na_lista(mod):
    """A inglesa faltava, e por isso a frescura do PDF inglês nunca foi verificada."""
    arvores = {arvore.name for _, _, arvore in mod["PDFS"]}
    assert {"tese-pt", "tese-eng"} <= arvores


def test_os_pdf_entregues_nao_estao_velhos():
    """O corpus real: nenhum PDF versionado é mais antigo do que o `.tex` mais recente."""
    guardado = sys.argv
    sys.argv = [str(SCRIPT)]
    try:
        m = runpy.run_path(str(SCRIPT))
    finally:
        sys.argv = guardado
    for nome, pdf, arvore in m["PDFS"]:
        if not pdf.exists():
            pytest.skip(f"{nome}: PDF não compilado neste contentor")
        fonte, quando = m["fonte_mais_recente"](arvore)
        assert fonte is not None, f"{nome}: nenhum .tex em {arvore}"
        assert quando <= pdf.stat().st_mtime, (
            f"{nome}: {fonte.name} é mais recente do que o {pdf.name} entregue — "
            "recompila e copia o build/ para o PDF versionado"
        )
