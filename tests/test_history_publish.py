"""Testes do publicador do histórico pela API do GitHub.

Todos offline: a rede é substituída. O que interessa proteger é (a) que está DESLIGADO por
omissão, (b) que **nunca** rebenta o ciclo de alertas, e (c) que JUNTA em vez de substituir,
porque substituir apagaria o trabalho do outro produtor.
"""

from __future__ import annotations

import base64
import json

import pytest

from investigator import history_publish as hp
from investigator.alerts_history import HistoryEntry, save_jsonl


def _entrada(key: str, texto: str) -> HistoryEntry:
    return HistoryEntry(date="2026-08-02", ticker="AMD", text=texto, kind="news", key=key)


@pytest.fixture(autouse=True)
def _ambiente_limpo(monkeypatch):
    for v in ("INVESTIGATOR_HISTORY_API", "GITHUB_TOKEN", "INVESTIGATOR_HISTORY_REPO",
              "INVESTIGATOR_HISTORY_BRANCH", "INVESTIGATOR_HISTORY_FILE"):
        monkeypatch.delenv(v, raising=False)


# ── Desligado por omissão ─────────────────────────────────────────────────────
def test_desligado_por_omissao_nao_faz_nada(tmp_path):
    """Sem a variável, nem sequer olha para o ficheiro. Aditivo, como o narrador."""
    assert hp.publish(tmp_path / "seja_o_que_for.jsonl") == ""


def test_ligado_sem_token_avisa_em_vez_de_rebentar(tmp_path, monkeypatch):
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    msg = hp.publish(tmp_path / "x.jsonl")
    assert "GITHUB_TOKEN" in msg


def test_ficheiro_local_vazio_nao_publica(tmp_path, monkeypatch):
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    p = tmp_path / "h.jsonl"
    p.write_text("", encoding="utf-8")
    assert hp.publish(p) == ""


# ── A junção, que é o ponto ───────────────────────────────────────────────────
def test_junta_o_que_falta_e_preserva_o_remoto(tmp_path, monkeypatch):
    """Dois produtores escrevem na mesma branch. Substituir apagaria o do outro."""
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")

    remoto = [_entrada("k-antiga", "alerta do cron")]
    corpo = "\n".join(json.dumps({"date": e.date, "ticker": e.ticker, "text": e.text,
                                  "kind": e.kind, "key": e.key}) for e in remoto)
    enviado = {}

    def falso(url, token, method="GET", payload=None):
        if method == "GET":
            return {"sha": "abc123",
                    "content": base64.b64encode(corpo.encode()).decode()}
        enviado.update(payload)
        return {}

    monkeypatch.setattr(hp, "_request", falso)
    p = tmp_path / "h.jsonl"
    save_jsonl([_entrada("k-nova", "alerta do vigia")], p)

    msg = hp.publish(p)
    assert "1 entrada" in msg
    escrito = base64.b64decode(enviado["content"]).decode()
    assert "alerta do cron" in escrito, "apagou o trabalho do outro produtor"
    assert "alerta do vigia" in escrito
    assert enviado["sha"] == "abc123", "tem de enviar o sha lido, para detetar conflitos"


def test_nada_novo_nao_escreve(tmp_path, monkeypatch):
    """Se o remoto já tem tudo, não faz um commit vazio a cada 60 segundos."""
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    e = _entrada("k1", "o mesmo alerta")
    corpo = json.dumps({"date": e.date, "ticker": e.ticker, "text": e.text,
                        "kind": e.kind, "key": e.key})
    chamadas = []

    def falso(url, token, method="GET", payload=None):
        chamadas.append(method)
        return {"sha": "s", "content": base64.b64encode(corpo.encode()).decode()}

    monkeypatch.setattr(hp, "_request", falso)
    p = tmp_path / "h.jsonl"
    save_jsonl([e], p)
    assert hp.publish(p) == ""
    assert "PUT" not in chamadas


# ── Fail-open ─────────────────────────────────────────────────────────────────
def test_erro_de_rede_nao_propaga(tmp_path, monkeypatch):
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")

    def rebenta(*a, **k):
        raise TimeoutError("rede em baixo")

    monkeypatch.setattr(hp, "_request", rebenta)
    p = tmp_path / "h.jsonl"
    save_jsonl([_entrada("k", "t")], p)
    msg = hp.publish(p)          # não levanta
    assert "ignorado" in msg


def test_publish_safe_engole_tudo(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")

    def rebenta(*a, **k):
        raise RuntimeError("boom")

    monkeypatch.setattr(hp, "publish", rebenta)
    hp.publish_safe(tmp_path / "h.jsonl")   # o ciclo de alertas tem de continuar
    assert "ignorado" in capsys.readouterr().out
