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


# ══ VOTOS: O DEFEITO DE 2026-09-02 ══════════════════════════════════════════════════════════
# O registo de votos usava o `publish_blob`, que substitui. Com um disco efémero isso significa
# que o primeiro voto a chegar depois de um reinício apaga tudo o que foi recolhido antes.
# Aconteceu: seis votos desapareceram no deploy das 19:10. Estes testes fixam a correcção.


def _voto(chave: str, votante: str, at: str) -> str:
    return json.dumps({"chave_alerta": chave, "votante": votante, "acao": "u", "at": at})


def _rede(corpo_remoto: str | None, enviado: dict, sha: str = "abc123", erro_get: int = 0):
    """Rede falsa. `corpo_remoto=None` + `erro_get=404` simula o ficheiro ainda não existir."""
    import urllib.error

    def falso(url, token, method="GET", payload=None):
        if method == "GET":
            if erro_get:
                raise urllib.error.HTTPError(url, erro_get, "", {}, None)
            return {"sha": sha, "content": base64.b64encode((corpo_remoto or "").encode()).decode()}
        enviado.update(payload)
        return {}

    return falso


def test_os_votos_juntam_se_e_nunca_substituem(tmp_path, monkeypatch):
    """⚠️ O defeito, exactamente. Um dyno reiniciado tem um ficheiro local com UM voto; a branch
    tem seis. Substituir deixaria um. Juntar deixa sete."""
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")

    remoto = "\n".join(_voto(f"k{i}", "v1", f"2026-09-01T10:0{i}:00Z") for i in range(6))
    enviado: dict = {}
    monkeypatch.setattr(hp, "_request", _rede(remoto, enviado))

    p = tmp_path / "feedback.jsonl"
    p.write_text(_voto("k-novo", "v2", "2026-09-02T00:09:00Z") + "\n", encoding="utf-8")

    msg = hp.publish_jsonl_merge(p, "feedback.jsonl")
    escrito = base64.b64decode(enviado["content"]).decode()
    assert escrito.count("\n") == 7, f"perdeu linhas: {msg}"
    assert "k0" in escrito and "k5" in escrito, "apagou os votos que já lá estavam"
    assert "k-novo" in escrito, "não publicou o voto novo"
    assert enviado["sha"] == "abc123", "sem o sha lido não há deteção de conflito"


def test_as_linhas_remotas_ficam_primeiro_e_pela_ordem(tmp_path, monkeypatch):
    """O registo é append-only e a `votos_efetivos` lê-o assumindo que o último vence.

    Se a junção baralhasse a ordem, uma mudança de voto passaria a contar ao contrário — e nada
    daria erro.
    """
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    remoto = _voto("k1", "v1", "2026-09-01T10:00:00Z")
    enviado: dict = {}
    monkeypatch.setattr(hp, "_request", _rede(remoto, enviado))

    p = tmp_path / "f.jsonl"
    p.write_text(_voto("k1", "v1", "2026-09-02T11:00:00Z") + "\n", encoding="utf-8")

    hp.publish_jsonl_merge(p, "feedback.jsonl")
    linhas = base64.b64decode(enviado["content"]).decode().strip().splitlines()
    assert "10:00:00" in linhas[0] and "11:00:00" in linhas[1], "a ordem inverteu-se"


def test_uma_linha_repetida_nao_entra_duas_vezes(tmp_path, monkeypatch):
    """Um reenvio do mesmo voto é ruído, não um voto novo."""
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    linha = _voto("k1", "v1", "2026-09-01T10:00:00Z")
    enviado: dict = {}
    monkeypatch.setattr(hp, "_request", _rede(linha, enviado))
    p = tmp_path / "f.jsonl"
    p.write_text(linha + "\n", encoding="utf-8")

    msg = hp.publish_jsonl_merge(p, "feedback.jsonl")
    assert "já tinha tudo" in msg
    assert not enviado, "escreveu sem ter nada de novo para escrever"


def test_leitura_falhada_desiste_em_vez_de_escrever_as_cegas(tmp_path, monkeypatch):
    """Escrever sem conseguir ler é substituir sem saber o que se está a substituir."""
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    enviado: dict = {}
    monkeypatch.setattr(hp, "_request", _rede(None, enviado, erro_get=500))
    p = tmp_path / "f.jsonl"
    p.write_text(_voto("k1", "v1", "2026-09-01T10:00:00Z") + "\n", encoding="utf-8")

    msg = hp.publish_jsonl_merge(p, "feedback.jsonl")
    assert "leitura falhou" in msg
    assert not enviado, "escreveu às cegas depois de a leitura falhar"


def test_primeira_publicacao_com_404_e_legitima(tmp_path, monkeypatch):
    """404 é «ainda não existe», e aí escrever é criar, não substituir."""
    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")
    enviado: dict = {}
    monkeypatch.setattr(hp, "_request", _rede(None, enviado, erro_get=404))
    p = tmp_path / "f.jsonl"
    p.write_text(_voto("k1", "v1", "2026-09-01T10:00:00Z") + "\n", encoding="utf-8")

    hp.publish_jsonl_merge(p, "feedback.jsonl")
    assert "k1" in base64.b64decode(enviado["content"]).decode()
    assert "sha" not in enviado, "mandou um sha numa criação"


def test_fetch_distingue_vazio_de_nao_consegui_ler(monkeypatch):
    """⚠️ `[]` e `None` não são a mesma coisa, e confundi-los apaga dados.

    `[]` é «li, e está vazio» — autoriza publicar. `None` é «não li» — obriga a desistir. Um
    `fetch` que devolvesse `[]` nos dois casos faria a rota do painel dizer «zero votos» de cada
    vez que o GitHub estivesse em baixo.
    """
    import urllib.error

    monkeypatch.setenv("INVESTIGATOR_HISTORY_API", "1")
    monkeypatch.setenv("GITHUB_TOKEN", "t")

    def erro(code):
        def f(url, token, method="GET", payload=None):
            raise urllib.error.HTTPError(url, code, "", {}, None)
        return f

    monkeypatch.setattr(hp, "_request", erro(404))
    assert hp.fetch_jsonl("feedback.jsonl") == [], "404 é vazio, não é falha"
    monkeypatch.setattr(hp, "_request", erro(503))
    assert hp.fetch_jsonl("feedback.jsonl") is None, "503 tem de ser indistinguível de vazio? não"

    monkeypatch.setattr(hp, "_request", lambda *a, **k: {
        "content": base64.b64encode(b'{"a":1}\n\n{"b":2}\n').decode()})
    assert hp.fetch_jsonl("feedback.jsonl") == ['{"a":1}', '{"b":2}'], "linhas em branco entraram"


def test_desligado_por_omissao_tambem_para_os_votos(tmp_path):
    assert hp.publish_jsonl_merge(tmp_path / "f.jsonl", "feedback.jsonl") == ""
    assert hp.fetch_jsonl("feedback.jsonl") is None


def test_semear_jsonl_recupera_a_contagem_depois_do_reinicio(tmp_path, monkeypatch):
    destino = tmp_path / "feedback.jsonl"
    monkeypatch.setattr(hp, "fetch_jsonl", lambda *a, **k: ['{"a":1}', '{"b":2}'])
    assert hp.seed_jsonl_once(destino, "feedback.jsonl") is True
    assert destino.read_text(encoding="utf-8").splitlines() == ['{"a":1}', '{"b":2}']


def test_semear_jsonl_nunca_sobrescreve_dados_locais(tmp_path, monkeypatch):
    destino = tmp_path / "feedback.jsonl"
    destino.write_text('{"local":1}\n', encoding="utf-8")

    def nao_devia_ser_chamado(*args, **kwargs):
        raise AssertionError("um ficheiro não vazio não pode ser substituído")

    monkeypatch.setattr(hp, "fetch_jsonl", nao_devia_ser_chamado)
    assert hp.seed_jsonl_once(destino, "feedback.jsonl") is True
    assert destino.read_text(encoding="utf-8") == '{"local":1}\n'


def test_semear_jsonl_assinala_leitura_remota_inconclusiva(tmp_path, monkeypatch):
    monkeypatch.setattr(hp, "fetch_jsonl", lambda *a, **k: None)
    assert hp.seed_jsonl_once(tmp_path / "feedback.jsonl", "feedback.jsonl") is False
