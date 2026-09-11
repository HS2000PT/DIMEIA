"""Guardas da porta que compara a classe LaTeX com o modelo oficial do MEIA.

⚠️ ESTES TESTES EXISTEM POR CAUSA DE UM DEFEITO QUE A PORTA TEVE NO SEU SEGUNDO DIA DE VIDA, e
é a metade «grita de mais» do par que este repositório documenta desde a sessão 63. A porta
avisava que a opção `openany` estava activa procurando a palavra no ficheiro inteiro. No momento
em que o autor decidiu retirar a opção, o comentário que explica a remoção passou a conter a
palavra — e a porta continuou a reportar uma não-conformidade **já resolvida**.

Um verificador que acusa o que já foi corrigido é um verificador em que se deixa de olhar, e é
tão inútil como um que não vê nada. O que decide é o caso do meio: a palavra num comentário no
FIM de uma linha de opções, que é onde uma leitura ingénua acerta mais facilmente.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location(
        "check_modelo_oficial", RAIZ / "scripts" / "check_modelo_oficial.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


CLASSE = chr(92) + "documentclass["


def _escreve(tmp_path, corpo: str) -> pathlib.Path:
    p = tmp_path / "main.tex"
    p.write_text(corpo, encoding="utf-8")
    return p


def test_ve_a_opcao_quando_ela_esta_na_lista(mod, tmp_path):
    p = _escreve(tmp_path, f"{CLASSE}\n11pt,\nopenany,\nenglish,\n]{{meia-style}}")
    assert mod._opcao_activa(p, "openany") is True


def test_nao_confunde_a_palavra_num_comentario_de_linha_inteira(mod, tmp_path):
    """O caso que tornou a porta errada: o comentário que EXPLICA a remoção."""
    p = _escreve(tmp_path,
                 f"% `openany` foi retirado por decisao do autor\n"
                 f"{CLASSE}\n11pt,\nenglish,\n]{{meia-style}}")
    assert mod._opcao_activa(p, "openany") is False


def test_nao_confunde_a_palavra_num_comentario_NO_FIM_de_uma_linha_de_opcoes(mod, tmp_path):
    """⚠️ O caso que decide, porque é o mais fácil de falhar.

    A palavra está DENTRO da lista de opções, no ficheiro; o que a torna inactiva é o `%` que
    a precede. Uma leitura que corte comentários só em linhas que COMEÇAM por `%` aprova isto
    como opção activa.
    """
    p = _escreve(tmp_path,
                 f"{CLASSE}\n11pt, % openany era aqui\nenglish,\n]{{meia-style}}")
    assert mod._opcao_activa(p, "openany") is False


def test_nao_inventa_a_opcao_quando_ela_nao_existe(mod, tmp_path):
    p = _escreve(tmp_path, f"{CLASSE}\n11pt,\nenglish,\n]{{meia-style}}")
    assert mod._opcao_activa(p, "openany") is False


def test_nao_confunde_uma_opcao_que_contem_a_outra(mod, tmp_path):
    """`openright` contém `open` e não é `openany`: a comparação é por opção inteira."""
    p = _escreve(tmp_path, f"{CLASSE}\n11pt,\nopenright,\nenglish,\n]{{meia-style}}")
    assert mod._opcao_activa(p, "openany") is False
    assert mod._opcao_activa(p, "openright") is True


def test_falha_aberto_sem_documentclass(mod, tmp_path):
    """Sem `\\documentclass` não se afirma nada — não se inventa uma não-conformidade."""
    p = _escreve(tmp_path, "% um ficheiro que nao e' o principal\n")
    assert mod._opcao_activa(p, "openany") is False


def test_as_duas_arvores_estao_conformes_hoje(mod):
    """O estado real: `openright` activo nas duas, `openany` fora das duas.

    ⚠️ Isto fixa a DECISÃO DO AUTOR de 2026-09-11 — seguir a convenção do modelo e das quatro
    dissertações aprovadas, ao preço dos versos em branco. Se alguém voltar a pôr `openany`
    para poupar páginas, este teste falha e obriga a que seja uma decisão outra vez, e não um
    atalho.
    """
    for arvore in ("tese-pt", "tese-eng"):
        p = RAIZ / arvore / "main.tex"
        assert p.exists(), f"{arvore}/main.tex desapareceu"
        assert mod._opcao_activa(p, "openany") is False, (
            f"{arvore}: `openany` voltou, e afasta-se do modelo oficial"
        )
