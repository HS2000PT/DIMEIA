"""Testes do feedback do leitor — a parte pura, sem rede.

O que estes testes protegem, por ordem de importância:

1. **O `callback_data` cabe nos 64 bytes do Telegram.** Um botão que excede o limite não dá
   erro: deixa de funcionar, em silêncio, e a amostra fica sem os alertas cujo identificador
   era mais longo. É a falha mais cara porque é invisível.
2. **Um update estranho devolve `None` e não uma exceção.** O webhook é público. Tráfego
   malformado é normal, e uma exceção ali transformar-se-ia em 500, que faz o Telegram
   reenviar o mesmo update indefinidamente.
3. **Mudar de voto substitui, e fica registado como mudança.** É a diferença entre um
   ficheiro que conta pessoas e um que conta cliques.
4. **Uma linha corrompida não faz perder as boas.** O dyno reinicia; uma escrita pode ficar a
   meio.
"""

from __future__ import annotations

import json

import pytest

from investigator import feedback_log as FL
from investigator.telegram_bot import feedback as F
from investigator.telegram_bot import sender as S

SAL = "sal-de-teste"


# ── callback_data ────────────────────────────────────────────────────────────────────────

def test_callback_data_cabe_sempre_no_limite_do_telegram():
    for chave in ("", "abc123def456", "2026-09-01:TSLA", "x" * 500, "chave com espaços e ç"):
        for acao in (F.UTIL, F.INUTIL):
            dados = F.dados_callback(chave, acao)
            assert len(dados.encode("utf-8")) <= F.MAX_CALLBACK_DATA, chave


def test_chave_curta_e_alfanumerica_passa_intacta():
    """A chave do histórico é sha1[:12] e já é o identificador do alerta. Resumi-la outra vez
    perderia a ligação direta ao histórico partilhado sem ganhar nada."""
    assert F.encurtar_chave("abc123def456") == "abc123def456"


def test_chave_longa_ou_com_pontuacao_e_resumida_de_forma_estavel():
    a = F.encurtar_chave("2026-09-01:TSLA")
    b = F.encurtar_chave("2026-09-01:TSLA")
    assert a == b and len(a) == F.TAM_CHAVE and a.isalnum()
    assert F.encurtar_chave("2026-09-01:NVDA") != a


def test_acao_desconhecida_e_rejeitada():
    with pytest.raises(ValueError):
        F.dados_callback("k", "talvez")


def test_teclado_tem_uma_linha_e_dois_botoes():
    t = F.teclado("abc123def456")
    assert len(t["inline_keyboard"]) == 1
    assert len(t["inline_keyboard"][0]) == 2


def test_teclado_com_contagem_omite_o_zero():
    """Um «0» ao lado do botão lê-se como resultado, e não como ausência de votos."""
    t = F.teclado_com_contagem("abc123def456", 0, 0)
    assert t["inline_keyboard"][0][0]["text"] == F.ROTULO_UTIL
    t2 = F.teclado_com_contagem("abc123def456", 3, 1)
    assert t2["inline_keyboard"][0][0]["text"].endswith("3")
    assert t2["inline_keyboard"][0][1]["text"].endswith("1")


# ── resumo do votante ────────────────────────────────────────────────────────────────────

def test_resumo_do_votante_e_estavel_e_depende_do_sal():
    a = F.resumir_votante(4242, SAL)
    assert a == F.resumir_votante("4242", SAL)  # int e str dão o mesmo
    assert a != F.resumir_votante(4242, "outro-sal")
    assert str(4242) not in a


def test_resumo_sem_sal_e_recusado():
    """Sem sal, o resumo é percorrível por força bruta: o espaço de identificadores do
    Telegram é pequeno. Falhar alto aqui é melhor do que guardar um resumo reversível."""
    with pytest.raises(ValueError):
        F.resumir_votante(4242, "")


# ── interpretação do update ──────────────────────────────────────────────────────────────

def _update(dados="fb|u|abc123def456", user=7, message_id=99, chat=-100123):
    return {"callback_query": {"id": "cb1", "data": dados, "from": {"id": user},
                               "message": {"message_id": message_id, "chat": {"id": chat}}}}


def test_interpreta_um_voto_valido():
    v = F.interpretar(_update(), SAL)
    assert v is not None
    assert v.chave_alerta == "abc123def456"
    assert v.util is True
    assert v.message_id == 99
    assert v.chat_id == "-100123"
    assert v.votante == F.resumir_votante(7, SAL)


def test_voto_negativo():
    v = F.interpretar(_update("fb|n|abc123def456"), SAL)
    assert v is not None and v.util is False


@pytest.mark.parametrize("update", [
    None, {}, [], "texto",
    {"message": {"text": "/help"}},                                  # é um comando, não um voto
    _update("outro|u|k"),                                            # prefixo alheio
    _update("fb|x|k"),                                               # ação desconhecida
    _update("fb|u"),                                                 # partes a menos
    {"callback_query": {"id": "c", "data": "fb|u|k", "message": {}}},  # sem `from`
    {"callback_query": {"id": "c", "data": 42, "from": {"id": 1}}},   # data não é texto
    _update(message_id="não-é-número"),
])
def test_updates_que_nao_sao_votos_devolvem_none_sem_levantar(update):
    assert F.interpretar(update, SAL) is None


# ── registo ──────────────────────────────────────────────────────────────────────────────

def _r(chave, votante, acao, at="2026-09-01T10:00:00Z"):
    return FL.FeedbackRecord(chave_alerta=chave, votante=votante, acao=acao, at=at)


def test_acrescentar_e_ler(tmp_path):
    p = tmp_path / "feedback.jsonl"
    FL.append_jsonl(_r("k1", "v1", FL.UTIL), p)
    FL.append_jsonl(_r("k1", "v2", FL.INUTIL), p)
    lidos = FL.load_jsonl(p)
    assert [r.acao for r in lidos] == [FL.UTIL, FL.INUTIL]


def test_ficheiro_inexistente_e_lista_vazia(tmp_path):
    assert FL.load_jsonl(tmp_path / "ainda-nao-existe.jsonl") == []


def test_linha_corrompida_nao_faz_perder_as_boas(tmp_path):
    p = tmp_path / "feedback.jsonl"
    FL.append_jsonl(_r("k1", "v1", FL.UTIL), p)
    with p.open("a", encoding="utf-8") as f:
        f.write('{"chave_alerta": "k2", "vot\n')   # escrita truncada a meio
    FL.append_jsonl(_r("k3", "v2", FL.INUTIL), p)
    assert [r.chave_alerta for r in FL.load_jsonl(p)] == ["k1", "k3"]


def test_campo_desconhecido_no_ficheiro_nao_parte_a_leitura(tmp_path):
    """Retrocompatibilidade nos dois sentidos: uma versão futura que acrescente um campo não
    pode partir uma versão antiga a ler o mesmo ficheiro."""
    p = tmp_path / "feedback.jsonl"
    p.write_text(json.dumps({"chave_alerta": "k", "votante": "v", "acao": "u",
                             "at": "2026-09-01T10:00:00Z", "campo_do_futuro": 1}) + "\n",
                 encoding="utf-8")
    assert len(FL.load_jsonl(p)) == 1


def test_ultimo_voto_de_cada_pessoa_ganha():
    rs = [_r("k1", "v1", FL.UTIL), _r("k1", "v2", FL.INUTIL), _r("k1", "v1", FL.INUTIL)]
    assert FL.contagem(rs, "k1") == (0, 2)


def test_contagem_e_por_alerta():
    rs = [_r("k1", "v1", FL.UTIL), _r("k2", "v1", FL.INUTIL)]
    assert FL.contagem(rs, "k1") == (1, 0)
    assert FL.contagem(rs, "k2") == (0, 1)


def test_resumo_separa_votos_de_pessoas():
    """O número que a tese vai reportar não é o de votos. Um leitor entusiasta que vote em
    trinta alertas não são trinta leitores, e é este campo que impede essa leitura."""
    rs = [_r("k1", "v1", FL.UTIL), _r("k2", "v1", FL.UTIL), _r("k1", "v1", FL.INUTIL),
          _r("k1", "v2", FL.UTIL)]
    s = FL.resumo(rs)
    assert s["votos_brutos"] == 4
    assert s["votos_efetivos"] == 3
    assert s["pessoas"] == 2
    assert s["alertas_votados"] == 2
    assert s["mudancas_de_voto"] == 1
    assert (s["uteis"], s["inuteis"]) == (2, 1)


def test_aparar_mantem_os_mais_recentes(tmp_path):
    p = tmp_path / "feedback.jsonl"
    for i in range(12):
        FL.append_jsonl(_r(f"k{i}", "v", FL.UTIL), p, max_entries=5)
    lidos = FL.load_jsonl(p)
    assert len(lidos) == 5
    assert lidos[-1].chave_alerta == "k11"


# ── sender: as partes puras, sem tocar na rede ───────────────────────────────────────────

def test_message_id_e_extraido_da_resposta():
    assert S.message_id_de({"ok": True, "result": {"message_id": 512}}) == 512


@pytest.mark.parametrize("resposta", [None, {}, {"result": {}}, {"result": {"message_id": "x"}}])
def test_message_id_ausente_devolve_none(resposta):
    assert S.message_id_de(resposta) is None


class _Resp:
    def __init__(self, status): self.status_code = status


@pytest.mark.parametrize("status,descricao,esperado", [
    (200, "", True),
    (400, "Bad Request: message is not modified", True),
    (400, "Bad Request: message to edit not found", True),
    (400, "Bad Request: can't parse entities", False),
    (429, "Too Many Requests", False),
])
def test_erros_benignos_do_telegram_nao_sao_falhas(status, descricao, esperado):
    """Reeditar uma mensagem com o mesmo texto, ou uma mensagem que o leitor apagou, não é um
    defeito nosso. Levantar exceção nestes dois casos faria o ciclo de reedição diária falhar
    em todos os dias calmos, que são a maioria."""
    assert S._benigno(_Resp(status), {"description": descricao}) is esperado
