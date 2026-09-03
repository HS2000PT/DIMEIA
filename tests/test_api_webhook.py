"""A rota `/telegram/webhook` — o contrato com o Telegram, testado ponta a ponta sem rede.

A rota é fina de propósito: verifica o segredo, lê o corpo, delega. O que estes testes fixam é
o **contrato**, que é a parte que não pode mudar sem consequências do lado do Telegram:

- **403 só no segredo.** É o único caso em que queremos que a outra ponta desista.
- **200 em tudo o resto**, incluindo corpo ilegível e update desconhecido. Um estatuto de erro
  faz o Telegram reenviar o mesmo update com recuo crescente, durante horas.
- **O identificador do votante nunca chega ao ficheiro.** É a verificação que torna a posição
  de privacidade da tese observável, e não apenas declarada.
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

import api.main as M
from investigator import config

SEGREDO = "segredo-de-teste"
CABECALHO = "X-Telegram-Bot-Api-Secret-Token"


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "TELEGRAM_WEBHOOK_SECRET", SEGREDO, raising=False)
    monkeypatch.setattr(config, "FEEDBACK_SALT", "sal-de-teste", raising=False)
    monkeypatch.setattr(M, "_VOTOS", tmp_path / "feedback.jsonl", raising=False)
    # Nada de rede nos testes: as três saídas do Telegram e a publicação são substituídas.
    from investigator import history_publish
    from investigator.telegram_bot import sender

    monkeypatch.setattr(sender, "send_message", lambda *a, **k: {"ok": True})
    monkeypatch.setattr(sender, "answer_callback_query", lambda *a, **k: {"ok": True})
    monkeypatch.setattr(sender, "edit_message_reply_markup", lambda *a, **k: {"ok": True})
    monkeypatch.setattr(history_publish, "seed_jsonl_once", lambda *a, **k: True)
    monkeypatch.setattr(history_publish, "publish_jsonl_merge", lambda *a, **k: "")
    return TestClient(M.app)


def _voto(dados="fb|u|abc123def456", user=7):
    return {"callback_query": {"id": "cb1", "data": dados, "from": {"id": user},
                               "message": {"message_id": 99, "chat": {"id": -100123}}}}


def test_sem_cabecalho_e_403(cliente):
    assert cliente.post("/telegram/webhook", json=_voto()).status_code == 403


def test_segredo_errado_e_403(cliente):
    r = cliente.post("/telegram/webhook", json=_voto(), headers={CABECALHO: "outro"})
    assert r.status_code == 403


def test_segredo_certo_grava_o_voto(cliente, tmp_path):
    r = cliente.post("/telegram/webhook", json=_voto(), headers={CABECALHO: SEGREDO})
    assert r.status_code == 200 and r.json()["ok"] is True
    linhas = (tmp_path / "feedback.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 1
    carga = json.loads(linhas[0])
    assert carga["acao"] == "u"
    # O identificador do Telegram NUNCA aparece no ficheiro: é o resumo que é guardado.
    assert carga["votante"] != "7" and "7" != carga["votante"][:1] * len(carga["votante"])
    assert len(carga["votante"]) == 24


def test_corpo_ilegivel_devolve_200(cliente):
    """Um 500 aqui faria o Telegram repetir o mesmo corpo mau durante horas."""
    r = cliente.post("/telegram/webhook", content=b"isto nao e json",
                     headers={CABECALHO: SEGREDO, "content-type": "application/json"})
    assert r.status_code == 200


def test_update_desconhecido_devolve_200(cliente):
    r = cliente.post("/telegram/webhook", json={"my_chat_member": {"chat": {"id": 1}}},
                     headers={CABECALHO: SEGREDO})
    assert r.status_code == 200


def test_dois_leitores_contam_como_duas_pessoas(cliente, tmp_path):
    from investigator import feedback_log as FL

    cliente.post("/telegram/webhook", json=_voto(user=1), headers={CABECALHO: SEGREDO})
    cliente.post("/telegram/webhook", json=_voto("fb|n|abc123def456", user=2),
                 headers={CABECALHO: SEGREDO})
    resumo = FL.resumo(FL.load_jsonl(tmp_path / "feedback.jsonl"))
    assert resumo["pessoas"] == 2
    assert (resumo["uteis"], resumo["inuteis"]) == (1, 1)
