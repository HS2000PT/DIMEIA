"""A porta das contagens de páginas tem de VER uma contagem errada.

Porque é que este ficheiro existe. A 2026-09-08 os materiais de defesa diziam que a
dissertação tem **132 páginas** e termina no fólio **108**; tinha **129** e terminava no
**111**. Os números tinham derrapado ao longo de quatro sessões — as páginas sobem e descem a
cada figura acrescentada — e **nenhuma das dezanove portas via nada**, porque o
``check_materiais`` compara decimais de duas ou três casas e uma contagem de páginas é um
inteiro.

⚠️ O sítio onde isso mais custava era a **resposta preparada para o júri**, que ensinava a
dizer os dois números errados em voz alta. O argumento sobrevivia — 111 continua abaixo do
fólio 120 onde acaba a dissertação aprovada que serve de referência — mas quem o diz com os
números trocados perde-o na mesma.

⚠️ E a lição de método da auditoria do mesmo dia: **uma porta sem autoteste só se sabe viva no
dia em que alguém desconfia dela.** Daí este ficheiro nascer com a porta, e não depois.
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "scripts" / "check_paginas.py"
CHECKLIST = RAIZ / "docs" / "planos" / "CHECKLIST.md"


def _correr() -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(RAIZ))


def test_o_corpus_real_passa():
    r = _correr()
    assert r.returncode == 0, r.stdout[-1200:]
    assert "batem com os PDF" in r.stdout


def test_le_as_paginas_do_proprio_pdf():
    """O número tem de vir do PDF, não de uma constante escrita à mão."""
    r = _correr()
    m = re.search(r"tese-pt: (\d+) paginas fisicas, ultimo folio arabe (\d+)", r.stdout)
    assert m, r.stdout[:600]
    paginas, folio = int(m.group(1)), int(m.group(2))
    assert paginas > 100, paginas
    # o fólio impresso é sempre menor do que a contagem física: há front matter em romano
    assert folio < paginas, (folio, paginas)


def test_uma_contagem_desactualizada_e_apanhada(tmp_path):
    """⚠️ O teste que decide. Sem ele, passar no corpus real não prova nada: uma porta que
    não olha para nada também devolve zero problemas."""
    original = CHECKLIST.read_bytes()
    data = CHECKLIST.stat()
    (tmp_path / "CHECKLIST.md").write_bytes(original)      # copiar ANTES de plantar
    try:
        t = original.decode("utf-8")
        m = re.search(r"\*\*(\d{3}) pp\*\*", t)
        assert m, "o CHECKLIST deixou de afirmar uma contagem de páginas"
        real = m.group(1)
        falso = "132" if real != "132" else "137"
        CHECKLIST.write_text(t.replace(f"**{real} pp**", f"**{falso} pp**", 1), encoding="utf-8")
        r = _correr()
        assert r.returncode != 0, (
            "a porta aprovou uma contagem que nenhum PDF sustenta:\n" + r.stdout[-1200:]
        )
        assert falso in r.stdout
    finally:
        CHECKLIST.write_bytes(original)
        # ⚠️ repor também a data: o `check_tese_pt` compara datas para apanhar um PDF por
        # recompilar, e um teste que o faz gritar de mais é um defeito, não um teste.
        os.utime(CHECKLIST, (data.st_atime, data.st_mtime))
        assert CHECKLIST.read_bytes() == original, "o CHECKLIST não foi restaurado"


def test_os_registos_datados_ficam_de_fora():
    """Um registo de sessão descreve o que era verdade no dia em que foi escrito. Obrigá-lo a
    acompanhar o presente seria falsificar o registo em vez de o actualizar."""
    fonte = SCRIPT.read_text(encoding="utf-8")
    assert "CLAUDE.md" not in fonte.split("VIVOS = [")[1].split("]")[0]
    assert "AUDITORIA" not in fonte.split("VIVOS = [")[1].split("]")[0]


def test_recusa_se_sem_pdf(tmp_path):
    """Um verificador que não encontra o corpus tem de ser indistinguível de um que falha."""
    fonte = SCRIPT.read_text(encoding="utf-8")
    assert "return 2" in fonte
    assert "nao e' seguro validar as cegas" in fonte or "Compilar antes de validar" in fonte
