"""Os materiais nao podem ensinar como facto um numero que a tese ja retirou.

Porque e que este teste existe. A 2026-09-06 quatro afirmacoes retiradas viviam
em cinco documentos de estudo, e a porta que os guarda via-os alinhados: o
`check_materiais` compara VALORES decimais, e nenhuma das quatro e um decimal
com par em falta. «84% das decisoes», «944 titulos -> 42 alertas», «22:1» e «~1 s
ate entregar» sao inteiros, que essa porta nem olha; e o `0,064` tem par, porque
a tese o declara em voz alta como a janela anterior e mais curta.

O pior deles estava na resposta modelo do slide do guia intitulado «a pergunta
mais dura, e a tua melhor resposta» -- ou seja na frase que o autor decora para
dizer em voz alta a um juri que tem o documento aberto.

O que estes testes fixam nao e o defeito -- esse esta corrigido -- mas o
mecanismo, e sobretudo os dois sentidos. Uma porta que so soubesse disparar
acusaria a tabela de «nao digas / diz» que existe para nomear estes numeros, e a
correccao seria apaga-la. Por isso metade dos casos exige SILENCIO.
"""

import runpy
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
VERIFICADOR = RAIZ / "scripts" / "check_numeros_retirados.py"


def _mod():
    """O modulo carregado sem correr o main."""
    return runpy.run_path(str(VERIFICADOR), run_name="nao_main")


def _achados(texto: str):
    return _mod()["achados"]({"m.md": texto})


# --- o que tem de disparar -------------------------------------------------

def test_a_fraccao_por_decisao_dispara():
    """84% e a contagem por decisao, que a repontuacao de minuto a minuto infla."""
    assert _achados("Em 84% das decisoes o resultado estava determinado.")


def test_o_funil_antigo_dispara():
    """944 -> 42 misturava avaliacoes de um lado com casos cumulativos do outro."""
    assert _achados("944 titulos relevantes capturados, 42 alertas, uma razao de 22:1.")


def test_a_latencia_de_um_segundo_dispara():
    """O 1 s era a era do agendador, com n=28. A medicao actual sao 5 s sobre 278."""
    assert _achados("O alerta chega em ~1 s desde a detecao.")


def test_a_amplitude_da_janela_antiga_dispara():
    assert _achados("A pontuacao varia 0,064 dentro de cada empresa.")


def test_o_quadruplica_dispara():
    assert _achados("A triagem quase quadruplica a precisao da selecao diaria.")


def test_o_teste_do_onnx_que_a_tese_curta_nao_tem_dispara():
    assert _achados("Provo que continua a ser o mesmo: top-3 identicos em 20 de 23 consultas.")


# --- o que NAO pode disparar, que e metade do valor -------------------------

def test_dentro_de_um_aviso_e_o_uso_certo():
    """Um numero retirado citado para ser evitado e exactamente o que se quer."""
    assert not _achados('Nao digas «84% das decisoes»: foi retirado, diz 48% dos titulos.')


def test_o_frame_onde_me_enganei_nao_dispara():
    """O melhor momento da defesa cita o erro de proposito."""
    assert not _achados("Onde me enganei: eu tinha escrito que quase quadruplica a precisao.")


def test_a_prevalencia_do_rotulo_nao_e_a_amplitude():
    """0,385 e TAMBEM a prevalencia por bloco, sem relacao nenhuma com isto.

    Este foi um falso positivo real deste verificador, sobre quatro documentos
    correctos, na sua primeira corrida.
    """
    assert not _achados("Prevalencia por bloco: 0,385 / 0,470 / 0,378, sem tendencia.")


def test_a_correccao_citada_ao_lado_do_erro_nao_dispara():
    """Tambem foi falso positivo: a resposta do quizz ensina a correccao."""
    assert not _achados("A linha de base reduziu o ganho anunciado de quase quatro vezes "
                        "para 1,67 vezes.")


def test_o_texto_actual_nao_dispara():
    assert not _achados("Sobre 36 925 decisoes, a amplitude dentro de cada empresa e de 0,072 "
                        "e entre as medianas 0,392, ou seja 5,4 vezes.")


# --- o proprio detector -----------------------------------------------------

def test_o_autoteste_do_verificador_passa():
    """Um verificador partido e um corpus limpo sao indistinguiveis no ecra."""
    assert _mod()["autoteste"]() is True


def test_o_registo_dos_retirados_nao_se_verifica_a_si_proprio():
    """O LEIA-ME-PRIMEIRO existe para os nomear; acusa-lo seria acusar a solucao."""
    nomes = {f.name for f in _mod()["corpus"]()}
    assert "LEIA-ME-PRIMEIRO.md" not in nomes
    assert len(nomes) >= 8, "sem corpus, um 'nenhum achado' nao vale nada"


def test_o_corpus_real_esta_limpo():
    """A porta tem de estar verde no repositorio como ele esta."""
    m = _mod()
    textos = {f.relative_to(RAIZ).as_posix(): f.read_text(encoding="utf-8", errors="replace")
              for f in m["corpus"]()}
    fora = m["achados"](textos)
    assert not fora, "\n".join(f"{n}:{ln} [{i}] {c}" for n, ln, i, c, _ in fora)
