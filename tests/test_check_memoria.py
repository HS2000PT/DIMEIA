"""O verificador de continuidade tem de apanhar o rodape que fica para tras.

Porque e que este teste existe. A 2026-09-06 o `AGENTS.md` declarava «Sessao n:
61 · Ultima atualizacao: 2026-08-23» com o Estado Atual imediatamente acima ja
na sessao 65. O bloco do topo era espelhado a cada sessao e o rodape nao, pelo
que um agente que lesse o rodape para saber onde estava ficava cinco sessoes
atras, com o resto do ficheiro a contradize-lo. Nada disparava: sao duas linhas
de texto valido.

O que estes testes fixam nao e o defeito de 2026-09-06 -- esse esta corrigido --
mas as tres regras que o apanhariam, incluindo a que um simples `diff` entre os
dois ficheiros deixaria passar: os DOIS rodapes ficarem para tras ao mesmo
tempo. Um verificador partido e um corpus limpo sao indistinguiveis no ecra.
"""

import datetime as dt
import runpy
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
VERIFICADOR = RAIZ / "scripts" / "check_memoria.py"

HOJE = dt.date(2026, 9, 6)

LIMPO = (
    "- **SESSAO 66 (2026-09-06): o que aconteceu.**\n"
    "- **SESSAO 65 (2026-09-05): o que aconteceu antes.**\n"
    "- **Sessao n:** 66 (uma frase)\n"
    "- **Ultima atualizacao:** 2026-09-06\n"
)


def _mod():
    """O modulo carregado sem correr o main."""
    return runpy.run_path(str(VERIFICADOR), run_name="nao_main")


def _achados(a: str, b: str, hoje: dt.date = HOJE) -> list[str]:
    m = _mod()
    return m["achados"]({"A.md": a, "B.md": b}, hoje)


# O corpus de teste usa os rotulos SEM acento, e as expressoes do verificador exigem-nos
# COM acento. Constroi-se aqui a ponte, para o teste falar da regra e nao da ortografia.
def _acentuado(s: str) -> str:
    return (s.replace("SESSAO", "SESSÃO")
             .replace("Sessao n:", "Sessão nº:")
             .replace("Ultima atualizacao:", "Última atualização:"))


def test_autoteste_do_proprio_verificador_passa():
    """O controlo negativo embutido tem de passar, senao nada abaixo dele vale."""
    assert _mod()["autoteste"]() is True


def test_corpus_coerente_nao_dispara():
    assert _achados(_acentuado(LIMPO), _acentuado(LIMPO)) == []


def test_rodape_de_um_ficheiro_para_tras_dispara():
    """O defeito real de 2026-09-06: o AGENTS.md cinco sessoes atras do seu proprio topo."""
    velho = LIMPO.replace("Sessao n:** 66", "Sessao n:** 61").replace(
        "atualizacao:** 2026-09-06", "atualizacao:** 2026-08-23")
    fora = _achados(_acentuado(LIMPO), _acentuado(velho))
    assert any("diverge entre os ficheiros" in f for f in fora)
    # A mensagem tem acentos; afirma-se sobre os dois numeros, que sao a parte estavel.
    assert any("61" in f and "66" in f and f.startswith("B.md") for f in fora)


def test_os_dois_rodapes_para_tras_dispara():
    """A regra que um diff entre os dois ficheiros NAO apanharia: iguais e ambos errados."""
    velho = _acentuado(LIMPO.replace("Sessao n:** 66", "Sessao n:** 64"))
    fora = _achados(velho, velho)
    assert fora, "dois rodapes iguais e ambos desactualizados tem de disparar"
    assert not any("diverge entre os ficheiros" in f for f in fora)


def test_data_no_futuro_dispara():
    futuro = _acentuado(LIMPO.replace("atualizacao:** 2026-09-06",
                                      "atualizacao:** 2027-01-01"))
    assert any("futuro" in f for f in _achados(futuro, futuro))


def test_rodape_ausente_dispara():
    """Apagar a linha nao pode ser uma forma de a porta passar."""
    sem = _acentuado(LIMPO.replace("- **Sessao n:** 66 (uma frase)\n", ""))
    assert _achados(_acentuado(LIMPO), sem)


def test_cabecalho_em_prosa_nao_conta_como_sessao():
    """Ha linhas de corpo com «SESSAO 40» la dentro; so os cabecalhos contam."""
    com_prosa = _acentuado(LIMPO) + "  **Ver o bloco SESSÃO 99 abaixo.**\n"
    assert _achados(com_prosa, com_prosa) == [], "prosa nao e um cabecalho de sessao"


def test_ficheiros_reais_do_repositorio_estao_coerentes():
    """A porta a serio: o CLAUDE.md e o AGENTS.md como estao no disco."""
    textos = {n: (RAIZ / n).read_text(encoding="utf-8", errors="replace")
              for n in _mod()["FICHEIROS"]}
    assert _mod()["achados"](textos, dt.date.today()) == []
