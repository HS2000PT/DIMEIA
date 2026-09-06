"""Os quatro exemplares do resumo: o verificador tem de ver as duas divergências.

Porque é que este teste existe. A 2026-09-06 correram-se três controlos à mão sobre o
`check_resumos.py` — plantar uma divergência, plantar um abstract longo, exigir que os dois
disparem — e um controlo corrido à mão não fica. A suite passou de 990 para 990 nesse dia:
escreveu-se um verificador novo e nenhum teste o guardava.

⚠️ E o defeito que ele existe para apanhar é real e já aconteceu: a sessão 56 encontrou o
resumo português a divergir entre as duas teses, com a cópia dentro da tese inglesa a omitir o
resultado negativo da triagem que a portuguesa trazia. **Nenhuma das duas falhava a compilar**,
porque as duas versões são texto válido.
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
VERIFICADOR = RAIZ / "scripts" / "check_resumos.py"

BS = chr(92)


def _arvore(base: Path, nome: str, proprio: str, traduzido: str) -> None:
    d = base / nome / "frontmatter"
    d.mkdir(parents=True)
    (d / "frontmatter.tex").write_text(
        BS + "begin{abstract}\n" + proprio + "\n" + BS + "end{abstract}\n"
        + BS + "begin{abstractotherlanguage}\n" + traduzido + "\n"
        + BS + "end{abstractotherlanguage}\n",
        encoding="utf-8")


def _corre(base: Path) -> subprocess.CompletedProcess:
    """Corre o verificador com a RAIZ apontada ao directório de teste."""
    codigo = (
        "import runpy, pathlib, sys\n"
        f"raiz = pathlib.Path(r'{base}')\n"
        f"mod = runpy.run_path(r'{VERIFICADOR}', run_name='nao_main')\n"
        # ⚠️ `runpy.run_path` devolve uma CÓPIA dos globals, pelo que alterar o dicionário
        # devolvido não chega à função: é preciso o `__globals__` dela. Sem isto o teste
        # corria o verificador contra o repositório REAL e passava sempre, que é a forma
        # mais silenciosa de um teste não testar nada.
        "mod['main'].__globals__['RAIZ'] = raiz\n"
        "sys.exit(mod['main']())\n"
    )
    return subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True)


PT = "Quando o preco de uma acao se move, o investidor precisa de contexto."
EN = "When a stock price moves, the investor needs context."


def test_quatro_exemplares_iguais_passam(tmp_path):
    _arvore(tmp_path, "tese-pt", PT, EN)
    _arvore(tmp_path, "tese-eng", EN, PT)
    r = _corre(tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_resumo_que_diverge_entre_arvores_dispara(tmp_path):
    """O defeito exacto da sessao 56: uma copia omite o que a outra afirma."""
    _arvore(tmp_path, "tese-pt", PT + " O modelo de triagem nao supera a volatilidade.", EN)
    _arvore(tmp_path, "tese-eng", EN, PT)
    r = _corre(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "DIVERGE" in r.stdout


def test_abstract_acima_do_limite_dispara(tmp_path):
    longo = " ".join(["palavra"] * 201)
    _arvore(tmp_path, "tese-pt", PT, longo)
    _arvore(tmp_path, "tese-eng", longo, PT)
    r = _corre(tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "acima do limite" in r.stdout


def test_arvore_ausente_falha_em_vez_de_passar(tmp_path):
    """Um verificador que nao ve o corpus tem de ser indistinguivel de um que falha."""
    _arvore(tmp_path, "tese-pt", PT, EN)
    r = _corre(tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
