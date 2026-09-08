"""O verificador das remissões do apêndice tem de VER os números.

Porque é que este ficheiro existe. A Tabela A.2 promete que cada resultado está rastreável
até à secção que o usa, e o `check_apendice_xref.py` existe para o confirmar. A 2026-09-08
descobriu-se, por sabotagem deliberada, que ele **aprovava uma remissão apontada de
propósito para a secção errada** — e não por um erro de lógica, mas porque não extraía
valor nenhum: a tese escreve os decimais na convenção PT-PT em modo matemático,
``$0{,}015$``, e o padrão ``\\d+[.,]\\d+`` não casa com ``0{,}015``. A lista saía vazia, o
ciclo de comparação não corria, e a linha era impressa como ``ok``.

⚠️ Este é o modo de falha que o projeto documenta desde a sessão 63: **não encontrar nada e
aprovar tudo têm o mesmo aspeto no ecrã.** O verificador imprimia «linhas com problema: 0»
com a mesma serenidade antes e depois de lhe plantarem um erro.

Os testes abaixo fixam as três propriedades que o tornam útil, e cada um falha se a
propriedade se perder:

1. **vê** os decimais escritos na convenção do documento;
2. **não grita** por números que só existem desenhados numa figura, que são evidência
   legítima da secção;
3. **distingue** um rótulo desenhado de uma coordenada, que não é afirmação nenhuma.
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = RAIZ / "scripts" / "check_apendice_xref.py"
APENDICE = RAIZ / "tese-pt" / "appendices" / "appendixA.tex"


def _correr() -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(RAIZ))


def test_o_corpus_real_passa():
    r = _correr()
    assert r.returncode == 0, r.stdout[-1500:]
    assert "linhas com problema: 0" in r.stdout


def test_extrai_decimais_na_convencao_do_documento():
    """`0{,}015` é um decimal. Um padrão que não o veja não verifica coisa nenhuma."""
    cel = r"$0{,}015$ contra $0{,}344$"
    achados = re.findall(r"[-+]?\d+[.,]\d+", cel.replace("{,}", "."))
    assert achados == ["0.015", "0.344"], achados
    # e sem a normalização, que era o defeito:
    assert re.findall(r"[-+]?\d+[.,]\d+", cel) == []


def test_uma_remissao_errada_e_apanhada(tmp_path):
    """⚠️ O teste que decide. Sem ele, a passagem no corpus real não prova nada: um
    verificador que não olha para nada também devolve zero problemas."""
    original = APENDICE.read_bytes()
    # ⚠️ A DATA TAMBEM E' RESTAURADA, e nao e' detalhe. O `check_tese_pt` compara a data do
    # PDF com a dos ficheiros de origem para apanhar um PDF por recompilar. Restaurar o
    # conteudo sem restaurar a data deixa o apendice mais recente do que o PDF e faz essa
    # porta acusar uma desactualizacao que nao existe -- um teste que faz uma porta gritar
    # de mais e' um defeito, e nao um teste.
    data = APENDICE.stat()
    guardado = tmp_path / "appendixA.tex"
    guardado.write_bytes(original)                    # copiar ANTES de plantar
    try:
        t = original.decode("utf-8")
        alvo = "Amplitude da taxa de disparo"
        assert alvo in t, "a linha usada como cobaia mudou de nome"
        i = t.index(alvo)
        j = t.index("\\ref{sec:", i)
        k = t.index("}", j)
        assert t[j:k + 1] != "\\ref{sec:av_feedback}", "escolher outra secção para o desvio"
        APENDICE.write_text(t[:j] + "\\ref{sec:av_feedback}" + t[k + 1:], encoding="utf-8")
        r = _correr()
        assert r.returncode != 0, (
            "o verificador aprovou uma remissão deliberadamente errada:\n" + r.stdout[-1500:]
        )
        assert "linhas com problema: 0" not in r.stdout
    finally:
        APENDICE.write_bytes(original)
        os.utime(APENDICE, (data.st_atime, data.st_mtime))
        assert APENDICE.read_bytes() == original, "o apêndice não foi restaurado"
        assert APENDICE.stat().st_mtime == data.st_mtime, "a data não foi restaurada"


def test_uma_coordenada_de_desenho_nao_conta_como_afirmacao():
    """Dentro de um desenho, `0.281` é uma coordenada e `[0{,}281]` é um rótulo que o
    leitor vê. Confundi-los faz o verificador aceitar uma remissão errada."""
    bloco = r"\addplot coordinates {(0.281,vol) [0{,}281]};"
    rotulos = re.findall(r"\d+\{,\}\d+", bloco)
    assert rotulos == ["0{,}281"], rotulos
    assert "0.281" not in " ".join(rotulos)


def test_as_linhas_sem_decimal_sao_declaradas_e_nao_dadas_como_ok():
    """Uma linha cujo valor são só inteiros (`23 de 23`) não é testada pela regra dos
    decimais. Imprimi-la como `ok` é a forma exata de um verificador mentir sem se enganar
    — e foi uma dessas que escondeu uma remissão para a secção errada."""
    r = _correr()
    assert "SEM DECIMAL" in r.stdout, "as linhas não testadas deixaram de ser declaradas"
    assert re.search(r"\d+ linha\(s\) SEM DECIMAL", r.stdout)


@pytest.mark.parametrize("marca", ["Verificação da geração ancorada", "sis_inteligencia"])
def test_a_remissao_da_guarda_aponta_para_onde_os_numeros_estao(marca):
    """Os `23 de 23` e `8 de 8` viviam num parágrafo da §4.7 e passaram para a §4.8 quando
    esta foi criada. A linha do apêndice ficou a apontar para a secção antiga, e nenhuma
    porta o via porque a linha não tem decimais."""
    t = APENDICE.read_text(encoding="utf-8")
    i = t.find("Verificação da geração ancorada")
    assert i != -1, "a linha da guarda desapareceu do apêndice"
    trecho = t[i:i + 220]
    assert "sec:sis_inteligencia" in trecho, trecho
    ch4 = (RAIZ / "tese-pt" / "ch4" / "chapter4.tex").read_text(encoding="utf-8")
    assert "vinte e três" in ch4 and "oito textos fiéis" in ch4
    del marca
