"""O registo do `message_id` e do HTML exato no histórico — a ligação que torna a anotação
possível.

**Porque merece testes próprios.** É a única oportunidade de guardar a identidade da mensagem:
o Telegram não oferece maneira de reencontrar uma mensagem pelo conteúdo. Se este caminho se
partir, nada falha em voz alta — os alertas continuam a sair, e só semanas depois se descobre
que nenhum é anotável. Os 522 alertas anteriores a 2026-09-01 são exatamente esse cenário, e
não têm remédio.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from investigator.alerts_history import load_jsonl

_SPEC = importlib.util.spec_from_file_location(
    "run_alerts", Path(__file__).resolve().parents[1] / "scripts" / "run_alerts.py")
ra = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(ra)

ALERTA = ('📰 <b>News alert for TSLA (Tesla)</b> (2026-09-01)\n'
          '"Tesla recalls 12k vehicles &amp; issues a fix"\n'
          '<a href="https://ex.com/a">Reuters</a>\n'
          'Right now: <b>+5.36%</b> today')
RESUMO = "📊 <b>Daily summary</b>\nNothing unusual today."


def _grava(tmp_path, mensagens, ids):
    p = tmp_path / "alerts_history.jsonl"
    ra._record_history_safe(mensagens, "2026-09-01", p, detected_at="2026-09-01T14:00:00Z",
                            sent_at="2026-09-01T14:00:05Z", message_ids=ids,
                            chat_id="-1004411506115")
    return load_jsonl(p)


def test_o_message_id_e_gravado_por_indice(tmp_path):
    e = _grava(tmp_path, [("TSLA", ALERTA)], {0: 637})[0]
    assert e.message_id == 637
    assert e.chat_id == "-1004411506115"


def test_o_html_exato_e_guardado_a_par_da_versao_sem_tags(tmp_path):
    """O `text` é o que o painel lê e não pode mudar; o `text_html` é o que uma edição precisa
    de reenviar. Sem o segundo, editar perderia o negrito e, com «&», produziria HTML que o
    Telegram rejeita."""
    e = _grava(tmp_path, [("TSLA", ALERTA)], {0: 637})[0]
    assert e.text_html == ALERTA
    assert "<b>" in e.text_html and "&amp;" in e.text_html
    assert "<b>" not in e.text  # o painel continua a receber a versão sem tags
    assert "&" in e.text and "&amp;" not in e.text  # e com as entidades desfeitas


def test_cada_mensagem_recebe_o_seu_id_e_nao_o_da_primeira(tmp_path):
    """Por índice, e não por texto: duas mensagens iguais são o mesmo objeto em Python, e um
    mapeamento por conteúdo daria às duas o identificador da primeira."""
    entradas = _grava(tmp_path, [("TSLA", ALERTA), ("NVDA", ALERTA)], {0: 637, 1: 638})
    assert [e.message_id for e in entradas] == [637, 638]


def test_uma_mensagem_que_falhou_o_envio_fica_sem_id_e_sem_chat(tmp_path):
    """Guardar o chat sem o `message_id` daria uma entrada que parece alcançável e não é."""
    entradas = _grava(tmp_path, [("TSLA", ALERTA), ("NVDA", ALERTA)], {0: 637})
    assert entradas[1].message_id == 0
    assert entradas[1].chat_id == ""


def test_sem_ids_nenhuns_o_comportamento_e_o_de_sempre(tmp_path):
    """Retrocompatibilidade: um produtor que não passe `message_ids` continua a escrever
    entradas válidas, como as 522 que já existem."""
    e = _grava(tmp_path, [("TSLA", ALERTA)], None)[0]
    assert e.message_id == 0 and e.chat_id == ""
    assert e.ticker == "TSLA" and e.kind == "news" and e.key


def test_o_resumo_diario_tambem_e_registado_mas_sem_chave(tmp_path):
    entradas = _grava(tmp_path, [("TSLA", ALERTA), ("MARKET", RESUMO)], {0: 637, 1: 638})
    assert entradas[1].kind != "news"
    assert entradas[1].key == ""
    assert entradas[1].message_id == 638  # alcançável, ainda que não anotável


def test_a_anotacao_ignora_o_que_nao_pode_editar(tmp_path):
    """O fecho do circuito: só é candidato o que é notícia, tem `message_id` e tem `text_html`."""
    from datetime import date

    spec = importlib.util.spec_from_file_location(
        "anotar_desfechos", Path(__file__).resolve().parents[1] / "scripts" / "anotar_desfechos.py")
    ad = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ad)

    entradas = _grava(tmp_path, [("TSLA", ALERTA), ("NVDA", ALERTA), ("MARKET", RESUMO)],
                      {0: 637, 2: 639})
    escolhidas = ad.entradas_a_anotar(entradas, date(2026, 9, 3))
    assert [e.ticker for e in escolhidas] == ["TSLA"]
