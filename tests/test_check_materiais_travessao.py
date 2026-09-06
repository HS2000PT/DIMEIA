"""A regra «zero travessões em prosa» tem de ver as DUAS formas do travessão.

Porque é que este teste existe. Até 2026-09-06 o `check_materiais.py` procurava apenas
`` --- ``, a forma que se escreve em LaTeX. O caráter `—` (U+2014) **rende exatamente igual no
PDF** e passava invisível: três travessões estavam na prosa da dissertação havia sessões, e
dois foram escritos nesse mesmo dia sem a porta dizer nada.

⚠️ E o teste guarda também o lado oposto, que é onde este projeto se magoa mais vezes: ligar o
caráter sem escopo deu **151 achados**, quase todos legítimos, porque a regra vem do brief de
reescrita da dissertação e os documentos de defesa são notas em Markdown onde um `—` num título
é pontuação corrente. Um verificador que grita de mais deixa de ser lido.
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
VERIFICADOR = RAIZ / "scripts" / "check_materiais.py"

BS = chr(92)
TRAVESSAO = chr(0x2014)


def _monta(base: Path, prosa_tese: str, material: str, ext: str = ".tex") -> None:
    """Uma árvore mínima: um capítulo da tese e um material de estudo."""
    for sub in ("frontmatter", "ch1", "ch2", "ch3", "ch4", "ch5", "ch6", "appendices"):
        (base / "tese-pt" / sub).mkdir(parents=True, exist_ok=True)
    (base / "tese-pt" / "frontmatter" / "frontmatter.tex").write_text("resumo\n",
                                                                     encoding="utf-8")
    for i in range(1, 7):
        (base / "tese-pt" / f"ch{i}" / f"chapter{i}.tex").write_text(
            prosa_tese if i == 1 else "prosa\n", encoding="utf-8")
    for x in "AB":
        (base / "tese-pt" / "appendices" / f"appendix{x}.tex").write_text("anexo\n",
                                                                         encoding="utf-8")
    (base / "tese-pt" / "slides").mkdir(parents=True, exist_ok=True)
    (base / "tese-pt" / "slides" / "main.tex").write_text(material if ext == ".tex" else "x\n",
                                                          encoding="utf-8")
    (base / "docs" / "defence").mkdir(parents=True, exist_ok=True)
    (base / "docs" / "defence" / "notas.md").write_text(material if ext == ".md" else "x\n",
                                                        encoding="utf-8")
    (base / "docs" / "evaluation").mkdir(parents=True, exist_ok=True)


def _corre(base: Path) -> subprocess.CompletedProcess:
    codigo = (
        "import runpy, pathlib, sys\n"
        f"raiz = pathlib.Path(r'{base}')\n"
        "sys.argv = ['check_materiais.py']\n"
        f"mod = runpy.run_path(r'{VERIFICADOR}', run_name='nao_main')\n"
        # ⚠️ `run_path` devolve uma cópia dos globals: sem tocar no `__globals__` da função,
        # o verificador corria contra o repositório real e o teste passava sempre.
        "g = mod['main'].__globals__\n"
        "g['RAIZ'] = raiz\n"
        "g['T'] = raiz / 'tese-pt'\n"
        "g['PROSA'] = ([raiz / 'tese-pt' / 'frontmatter' / 'frontmatter.tex']\n"
        "              + [raiz / 'tese-pt' / f'ch{i}' / f'chapter{i}.tex' "
        "for i in range(1, 7)])\n"
        "g['MATERIAIS'] = ([raiz / 'tese-pt' / 'slides' / 'main.tex']\n"
        "                  + sorted((raiz / 'docs' / 'defence').glob('*.md')))\n"
        "sys.exit(mod['main']())\n"
    )
    return subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True)


LIMPO = "Uma frase de prosa sem travessao nenhum.\n"


def test_corpus_limpo_nao_grita(tmp_path):
    _monta(tmp_path, LIMPO, LIMPO)
    r = _corre(tmp_path)
    assert "travessoes em prosa: 0" in r.stdout, r.stdout + r.stderr


def test_forma_latex_na_tese_dispara(tmp_path):
    _monta(tmp_path, "A porta parou aqui --- o orcamento diario.\n", LIMPO)
    r = _corre(tmp_path)
    assert "travessoes em prosa: 1" in r.stdout, r.stdout + r.stderr


def test_caracter_unicode_na_tese_dispara(tmp_path):
    """O defeito de 2026-09-06: rende igual ao `---` e a porta nao o via."""
    _monta(tmp_path, f"A porta parou aqui {TRAVESSAO} o orcamento diario.\n", LIMPO)
    r = _corre(tmp_path)
    assert "travessoes em prosa: 1" in r.stdout, r.stdout + r.stderr


def test_caracter_unicode_em_markdown_nao_dispara(tmp_path):
    """A regra e da dissertacao. Num documento de defesa, `—` num titulo e pontuacao."""
    _monta(tmp_path, LIMPO, f"## Bloco 1 {TRAVESSAO} o que isto e\n", ext=".md")
    r = _corre(tmp_path)
    assert "travessoes em prosa: 0" in r.stdout, r.stdout + r.stderr
