"""Testes do webhook — a orquestração, com as saídas todas falsificadas.

O que estes testes protegem:

1. **O `answerCallbackQuery` acontece SEMPRE**, incluindo quando a gravação falhou. Sem ele o
   Telegram reenvia o mesmo update e um erro de escrita transforma-se numa repetição sem fim.
2. **A rota fecha sem segredo configurado.** O caso perigoso não é o segredo errado — é o
   segredo em falta, porque abriria a rota a quem descobrisse o endereço e a amostra da tese
   deixaria de significar o que diz significar.
3. **Nada do que corre a seguir à gravação pode perder um voto.** A atualização do teclado e a
   publicação falham em silêncio de propósito; o voto já está no ficheiro.
4. **Um comando continua a ter resposta.** Registar o webhook desliga o `getUpdates`; se o
   ramo dos comandos não existisse, o `/watch` morria sem que nada o assinalasse.
"""

from __future__ import annotations

import pytest

from investigator import feedback_log as FL
from investigator.telegram_bot import feedback as F
from investigator.telegram_bot import webhook as W

SAL = "sal-de-teste"


class Espia:
    """Regista as chamadas em vez de as fazer. `explode` simula uma saída indisponível."""

    def __init__(self, explode: bool = False):
        self.chamadas: list[tuple] = []
        self.explode = explode

    def __call__(self, *args, **kwargs):
        self.chamadas.append((args, kwargs))
        if self.explode:
            raise RuntimeError("saída indisponível")
        return {"ok": True}


def _ctx(tmp_path, **kw):
    base = {
        "sal": SAL,
        "caminho_votos": tmp_path / "feedback.jsonl",
        "enviar": Espia(),
        "responder_callback": Espia(),
        "editar_teclado": Espia(),
        "publicar": Espia(),
        "ligacao_db": None,
    }
    base.update(kw)
    return W.Contexto(**base)


def _voto(dados="fb|u|abc123def456", user=7, message_id=99, chat=-100123):
    return {"callback_query": {"id": "cb1", "data": dados, "from": {"id": user},
                               "message": {"message_id": message_id, "chat": {"id": chat}}}}


# ── segredo ──────────────────────────────────────────────────────────────────────────────

def test_segredo_em_falta_fecha_a_rota():
    """O caso perigoso é este, e não o segredo errado: um webhook sem verificação aceita
    votos de qualquer pessoa que descubra o endereço."""
    assert W.segredo_confere("seja-o-que-for", "") is False
    assert W.segredo_confere(None, "") is False


def test_segredo_certo_abre_e_errado_fecha():
    assert W.segredo_confere("abc", "abc") is True
    assert W.segredo_confere("abd", "abc") is False
    assert W.segredo_confere(None, "abc") is False


# ── voto ─────────────────────────────────────────────────────────────────────────────────

def test_voto_e_gravado_respondido_e_publicado(tmp_path):
    ctx = _ctx(tmp_path)
    linha = W.processar(_voto(), ctx)
    registos = FL.load_jsonl(ctx.caminho_votos)
    assert len(registos) == 1 and registos[0].acao == F.UTIL
    assert len(ctx.responder_callback.chamadas) == 1
    assert len(ctx.publicar.chamadas) == 1
    assert "voto u" in linha


def test_o_teclado_e_atualizado_com_a_contagem(tmp_path):
    ctx = _ctx(tmp_path)
    W.processar(_voto(user=1), ctx)
    W.processar(_voto(user=2), ctx)
    (_args, kwargs) = ctx.editar_teclado.chamadas[-1][0], ctx.editar_teclado.chamadas[-1][1]
    teclado = _args[1]
    assert teclado["inline_keyboard"][0][0]["text"].endswith("2")
    assert kwargs["chat_id"] == "-100123"


def test_mudar_de_voto_nao_soma(tmp_path):
    ctx = _ctx(tmp_path)
    W.processar(_voto("fb|u|abc123def456", user=1), ctx)
    W.processar(_voto("fb|n|abc123def456", user=1), ctx)
    assert FL.contagem(FL.load_jsonl(ctx.caminho_votos), "abc123def456") == (0, 1)
    # e a mudança fica registada, que é a razão de o ficheiro ser de acrescento
    assert FL.resumo(FL.load_jsonl(ctx.caminho_votos))["mudancas_de_voto"] == 1


def test_responde_ao_telegram_mesmo_quando_a_gravacao_falha(tmp_path):
    """Um caminho que não existe faz a escrita falhar. A resposta tem de sair na mesma, ou o
    Telegram reenvia o update para sempre."""
    ctx = _ctx(tmp_path, caminho_votos=tmp_path / "nao" / "\x00invalido" / "f.jsonl")
    linha = W.processar(_voto(), ctx)
    assert len(ctx.responder_callback.chamadas) == 1
    assert "não consegui" in ctx.responder_callback.chamadas[0][0][1].lower()
    assert "perdido" in linha


def test_teclado_indisponivel_nao_perde_o_voto(tmp_path):
    ctx = _ctx(tmp_path, editar_teclado=Espia(explode=True))
    linha = W.processar(_voto(), ctx)
    assert len(FL.load_jsonl(ctx.caminho_votos)) == 1
    assert "voto u" in linha


def test_publicacao_indisponivel_nao_perde_o_voto(tmp_path):
    ctx = _ctx(tmp_path, publicar=Espia(explode=True))
    W.processar(_voto(), ctx)
    assert len(FL.load_jsonl(ctx.caminho_votos)) == 1


def test_sem_publicador_continua_a_gravar(tmp_path):
    """É a configuração de desenvolvimento local: sem branch de dados, mas com votos."""
    ctx = _ctx(tmp_path, publicar=None, editar_teclado=None)
    W.processar(_voto(), ctx)
    assert len(FL.load_jsonl(ctx.caminho_votos)) == 1


# ── comandos ─────────────────────────────────────────────────────────────────────────────

def test_um_comando_continua_a_ter_resposta(tmp_path):
    """Registar o webhook desliga o getUpdates. Sem este ramo, /watch morria em silêncio."""
    import sqlite3

    from investigator.telegram_bot import store

    conn = store.connect(tmp_path / "bot.db")
    ctx = _ctx(tmp_path, ligacao_db=lambda: conn)
    linha = W.processar({"message": {"text": "/watch TSLA", "chat": {"id": 42}}}, ctx)
    assert "/watch" in linha
    resposta = ctx.enviar.chamadas[0][0][0]
    assert "TSLA" in resposta
    assert isinstance(conn, sqlite3.Connection)


def test_comando_sem_base_avisa_em_vez_de_ficar_calado(tmp_path):
    ctx = _ctx(tmp_path, ligacao_db=None)
    W.processar({"message": {"text": "/list", "chat": {"id": 42}}}, ctx)
    assert ctx.enviar.chamadas, "um comando sem resposta lê-se como bot avariado"


@pytest.mark.parametrize("update", [
    {}, {"edited_message": {"chat": {"id": 1}}}, {"message": {"chat": {"id": 1}}},
    {"my_chat_member": {"chat": {"id": 1}}},
])
def test_updates_irrelevantes_sao_ignorados_sem_levantar(tmp_path, update):
    ctx = _ctx(tmp_path)
    linha = W.processar(update, ctx)
    assert isinstance(linha, str)
    assert not ctx.responder_callback.chamadas


def test_nunca_levanta_mesmo_com_um_contexto_partido(tmp_path):
    """A rota devolve 200 quase sempre, e é `processar` que tem de garantir isso."""
    ctx = _ctx(tmp_path, responder_callback=Espia(explode=True))
    linha = W.processar(_voto(), ctx)
    assert "resposta falhou" in linha
