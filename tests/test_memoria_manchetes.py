"""A memória das manchetes tem de sobreviver a um reinício.

O que estes testes guardam é o incidente de 2026-09-04, medido no histórico de produção:
das 566 entradas, 31 grupos estavam duplicados; trinta com o mesmo `message_id`, ou seja
registados duas vezes e entregues uma, e **um** com `message_id` diferente — entregue duas
vezes ao leitor.

Esse caso tem as duas mensagens com o MESMO título e precedentes DIFERENTES: a base de casos
maturou entre os dois ciclos. A chave de deduplicação diária é um resumo do texto
renderizado, e os precedentes fazem parte dele — muda o texto, muda a chave, e o «já
alertada hoje» não reconhece a repetição. A verificação que apanha isso compara manchetes,
que são estáveis, mas a sua memória vivia só no disco efémero do dyno.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_alerts import (  # noqa: E402
    _manchete_do_alerta,
    load_state,
    seed_state_from_shared_history,
)

TITULO = ("Dow Jones Futures: Stocks Jump On Fed's Waller; Tesla Cybercab Event Private, "
          "Jobs Report In Focus")


def _entrada(texto: str, chave: str, dia: str = "2026-09-04"):
    class E:
        date = dia
        kind = "news"
        ticker = "TSLA"
        key = chave
        text = texto
    return E()


def _alerta(titulo: str, precedentes: str) -> str:
    return ('\U0001f4f0 News alert for TSLA (Tesla) (2026-09-03)\n'
            f'"{titulo}"\n'
            'https://example.invalid/x\n'
            f'{precedentes}\n')


def test_extrai_a_manchete_do_texto_do_alerta():
    t = _alerta(TITULO, "3 similar past headlines.")
    assert _manchete_do_alerta(t) == TITULO


def test_sem_citacao_devolve_vazio_e_nao_inventa():
    assert _manchete_do_alerta("Market open · watchlist snapshot") == ""
    assert _manchete_do_alerta("") == ""


def test_o_reinicio_repoe_a_memoria_da_manchete(tmp_path):
    """O caso real: mesma manchete, precedentes diferentes, chaves diferentes.

    Sem a reposição, o estado depois de um reinício não conhece a manchete e a segunda
    mensagem sai. É o que aconteceu na TSLA a 2026-09-04.
    """
    primeiro = _alerta(TITULO, "3 similar past headlines. +2.90% to +14.81% (average +6.91%)")
    estado = load_state(tmp_path / "s.json", today=None)
    estado["date"] = "2026-09-04"
    seed_state_from_shared_history(estado, [_entrada(primeiro, "9880c70c9fde")], "2026-09-04")

    palavras = estado["news_words"].get("TSLA", [])
    assert palavras, "a manchete do alerta já entregue tem de ficar na memória"

    from investigator.dedup import is_near_duplicate

    assert is_near_duplicate(TITULO, palavras), (
        "a mesma manchete, com precedentes diferentes, tem de ser reconhecida"
    )


def test_a_reposicao_nao_duplica_a_mesma_manchete(tmp_path):
    """Semear duas vezes o mesmo alerta não pode encher a memória de cópias."""
    t = _alerta(TITULO, "3 similar past headlines.")
    estado = load_state(tmp_path / "s.json", today=None)
    estado["date"] = "2026-09-04"
    entradas = [_entrada(t, "aaa"), _entrada(t, "aaa")]
    seed_state_from_shared_history(estado, entradas, "2026-09-04")
    assert len(estado["news_words"]["TSLA"]) == 1


def test_manchete_diferente_nao_e_suprimida(tmp_path):
    """Controlo no sentido oposto: uma memória que apanhe tudo suprimiria notícia legítima."""
    estado = load_state(tmp_path / "s.json", today=None)
    estado["date"] = "2026-09-04"
    seed_state_from_shared_history(
        estado, [_entrada(_alerta(TITULO, "x"), "k1")], "2026-09-04")

    from investigator.dedup import is_near_duplicate

    outra = "Tesla Recalls 12,000 Vehicles Over Suspension Bolt Defect"
    assert not is_near_duplicate(outra, estado["news_words"]["TSLA"]), (
        "uma história diferente da mesma empresa tem de continuar a passar"
    )
