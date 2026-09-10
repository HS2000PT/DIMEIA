"""Controlos do `auditar_numeros.py`, nas duas direções.

⚠️ POR QUE E QUE ESTE FICHEIRO EXISTE. Ate 2026-09-10 o verificador estava CEGO a forma em que
esta tese escreve todos os resultados. Extraia decimais com o padrao `\\d+\\.\\d{2,}` -- com
PONTO -- e a arvore canonica e PT-PT e escreve `$2{,}173$`, com virgula em modo matematico, que
outra porta exige. Declarava «todos os numeros tem origem» depois de examinar **60**, quando a
prosa e as tabelas contem 263. Entre os invisiveis estava a contribuicao nova por inteiro.

E a mesma classe que a sessao 63 corrigiu no `check_tese_numeros`; foi corrigida la e nunca aqui,
porque **nao havia teste nenhum sobre este verificador**. Passa a haver.

O que se testa, e as duas metades importam:
  · que apanha um numero inventado (senao e' inutil);
  · que NAO apanha um arredondamento legitimo nem um corpus limpo (senao deixa de ser lido).

E o controlo que decide, porque e' o risco do que foi acrescentado: um VIZINHO de um valor
publicado tem de disparar. Se `0,995` passasse por ser proximo de `0,9936`, o teste de
arredondamento teria trocado uma cegueira por uma permissividade.
"""

from __future__ import annotations

import pathlib
import runpy

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def mod():
    return runpy.run_path(str(RAIZ / "scripts" / "auditar_numeros.py"),
                          run_name="__nao_main__")


# ─────────────────────────────── extração ───────────────────────────────

def test_extrai_decimal_com_virgula_em_modo_matematico(mod):
    """O defeito de origem: `$0{,}395$` tem de ser visto, e normalizado para a forma com ponto.

    Sem isto o verificador nao ve um unico resultado da arvore portuguesa.
    """
    achados = mod["numeros"](r"a precisao foi de $0{,}395$ no equilibrado")
    assert "0.395" in achados


def test_extrai_decimal_com_ponto(mod):
    """A forma inglesa continua a ser vista: a correcao e aditiva, nao substitutiva."""
    assert "0.395" in mod["numeros"]("precision was 0.395 on the balanced subset")


def test_extrai_inteiro_com_separador_de_milhar(mod):
    assert "36925" in mod["numeros"](r"sobre as $36\,925$ decisoes")


def test_ignora_decimal_de_uma_so_casa(mod):
    """Um decimal de uma casa nao e uma afirmacao de resultado: e composicao ou uma versao."""
    assert mod["numeros"]("largura de 0.5 do texto") == set()


# ──────────────────────── arredondamento: os dois sentidos ────────────────────────

def test_arredondamento_aceita_a_fonte_com_mais_casas(mod):
    """`0,994` na tese e `0,9936` no relatorio sao o MESMO valor.

    O `porta_colapso_direcao_v2` publica quatro casas e a tese imprime tres. Exigir a cadeia
    exacta reportava quatro numeros do diagnostico de degeneracao como sem fonte -- e esse
    diagnostico e precisamente o que torna a QI4 um resultado e nao uma montagem falhada.
    """
    fontes = mod["_valores_das_fontes"]("cosseno entre manchetes diferentes 0,9936")
    assert mod["arredonda_de"]("0.994", fontes) == "0.9936"


def test_arredondamento_RECUSA_um_vizinho(mod):
    """⚠️ O CONTROLO QUE DECIDE. `0,995` nao e `0,9936` arredondado, e tem de disparar.

    Sem este teste, o remedio para a cegueira seria uma permissividade: a porta passaria a
    aprovar gralhas proximas de valores reais, que e a classe de defeito mais dificil de ver.
    """
    fontes = mod["_valores_das_fontes"]("cosseno 0,9936")
    assert mod["arredonda_de"]("0.995", fontes) is None


def test_arredondamento_recusa_fonte_com_MENOS_casas(mod):
    """Uma fonte menos precisa nao sustenta um valor mais preciso.

    Se `0,5` justificasse `0,499`, justificaria tambem `0,503`: um valor sustentaria os dois
    lados de uma afirmacao, e a porta deixava de dizer nada.
    """
    fontes = mod["_valores_das_fontes"]("o alvo tem media 0,5")
    assert mod["arredonda_de"]("0.499", fontes) is None


def test_arredondamento_ignora_inteiro_sem_casas(mod):
    assert mod["arredonda_de"]("36925", mod["_valores_das_fontes"]("36925,4")) is None


# ──────────────────────────── a lista de justificados ────────────────────────────

def test_justificados_tem_razao_escrita_e_nao_vazia(mod):
    """A lista existe para ser accionavel: uma entrada sem razao e folclore.

    A regra esta escrita no proprio ficheiro («Acrescentar aqui exige escrever a razao. Se a
    razao nao se escrever, o numero e um defeito») e este teste torna-a executavel.
    """
    just = mod["JUSTIFICADOS"]
    assert just, "a lista nao pode estar vazia"
    for numero, razao in just.items():
        assert isinstance(razao, str), f"{numero}: a razao tem de ser texto"
        assert len(razao.strip()) >= 30, f"{numero}: razao demasiado curta para justificar nada"


def test_a_pasta_da_QI4_esta_entre_as_fontes():
    """`docs/design/` tem de ser lida: e la que vive o resultado da contribuicao nova.

    O `qi4_resultado_2026-09-09.md` e o `porta_colapso_direcao_v2_*.md` nao estao em
    `docs/evaluation/`. Sem esta pasta, 19 valores que a tese afirma sobre a QI4 ficavam sem
    fonte reconhecivel e a porta acusava o capitulo mais recente por um defeito que era dela.
    """
    fonte = (RAIZ / "scripts" / "auditar_numeros.py").read_text(encoding="utf-8")
    assert "docs/design/*.md" in fonte


def test_o_corpus_real_passa():
    """O corpus como esta' no disco nao dispara. E a outra metade do controlo.

    Uma porta que grita sobre um documento correcto deixa de ser lida, e este projeto pagou
    essa metade tantas vezes como a outra.
    """
    import subprocess
    import sys
    r = subprocess.run([sys.executable, "scripts/auditar_numeros.py"], cwd=RAIZ,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, f"a porta disparou sobre o corpus real:\n{r.stdout}\n{r.stderr}"
    assert "SEM ORIGEM CONHECIDA: 0" in r.stdout


def test_examina_muito_mais_do_que_os_sessenta_de_antes():
    """Guarda contra a cegueira voltar sem ninguem dar por isso.

    Se alguem reverter a extracao da virgula, a contagem cai para ~60 e este teste parte. Sem
    ele, a porta voltaria a dizer «todos tem origem» depois de olhar para um quarto do
    documento, que e' exactamente o estado que existiu ate 2026-09-10.
    """
    import re
    import subprocess
    import sys
    r = subprocess.run([sys.executable, "scripts/auditar_numeros.py"], cwd=RAIZ,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"n[úu]meros de prosa e tabelas: (\d+)", r.stdout)
    assert m, f"nao encontrei a contagem na saida:\n{r.stdout}"
    assert int(m.group(1)) > 200, (
        f"so {m.group(1)} numeros examinados; a extracao da virgula parece ter sido revertida"
    )
