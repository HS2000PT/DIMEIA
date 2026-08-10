"""Testes da cadeia de fornecedores do narrador — todos OFFLINE (nunca tocam na rede)."""

from __future__ import annotations

import pytest

from investigator.narrator import providers


@pytest.fixture(autouse=True)
def _sem_rede(monkeypatch):
    """Rede proibida por omissão: qualquer teste que escape ao mock falha alto, em vez de
    fazer um pedido real e ficar lento/instável no CI."""
    def _proibido(*a, **k):
        raise AssertionError("teste tentou usar a rede")

    monkeypatch.setattr(providers.requests, "post", _proibido)


def _com_chaves(monkeypatch, groq: str | None = "g", gemini: str | None = "m"):
    monkeypatch.setattr(providers.config, "GROQ_API_KEY", groq)
    monkeypatch.setattr(providers.config, "GEMINI_API_KEY", gemini)


def test_sem_chaves_nao_ha_fornecedores_e_complete_devolve_none(monkeypatch):
    """Contrato fundamental: zero chaves é uma configuração válida, não uma avaria."""
    _com_chaves(monkeypatch, None, None)
    assert providers.available() == []
    assert providers.complete("olá") is None


def test_groq_e_o_primeiro_por_medicao(monkeypatch):
    """A ordem foi invertida por sondagem (Gemini dava 404/429). Fixada em teste para não
    regredir sem querer."""
    _com_chaves(monkeypatch)
    assert providers.available() == ["groq", "gemini"]

    monkeypatch.setattr(providers, "_post_groq", lambda p, t, m=None: "do groq")
    monkeypatch.setattr(providers, "_post_gemini", lambda p, t, m=None: "do gemini")
    r = providers.complete("olá")
    assert r is not None and r.provider == "groq" and r.text == "do groq"


def test_cai_para_gemini_quando_o_groq_falha(monkeypatch):
    _com_chaves(monkeypatch)

    def _rebenta(p, t):
        raise RuntimeError("429 rate limit")

    monkeypatch.setattr(providers, "_post_groq", _rebenta)
    monkeypatch.setattr(providers, "_post_gemini", lambda p, t, m=None: "do gemini")
    r = providers.complete("olá")
    assert r is not None and r.provider == "gemini" and r.text == "do gemini"


def test_todos_a_falhar_devolve_none_sem_levantar(monkeypatch):
    """Fail-open: um ciclo de alertas nunca pode morrer por causa do LLM."""
    _com_chaves(monkeypatch)

    def _rebenta(p, t):
        raise RuntimeError("em baixo")

    monkeypatch.setattr(providers, "_post_groq", _rebenta)
    monkeypatch.setattr(providers, "_post_gemini", _rebenta)
    assert providers.complete("olá") is None


def test_resposta_vazia_conta_como_falha_e_passa_ao_seguinte(monkeypatch):
    """Medido: modelos de raciocínio devolvem HTTP 200 SEM texto. Uma string vazia não pode
    passar por resposta válida — senão o alerta sairia mudo."""
    _com_chaves(monkeypatch)
    monkeypatch.setattr(providers, "_post_groq", lambda p, t, m=None: "")
    monkeypatch.setattr(providers, "_post_gemini", lambda p, t, m=None: "do gemini")
    r = providers.complete("olá")
    assert r is not None and r.provider == "gemini"


def test_fornecedor_sem_chave_e_saltado_em_silencio(monkeypatch):
    _com_chaves(monkeypatch, groq=None, gemini="m")
    assert providers.available() == ["gemini"]
    monkeypatch.setattr(providers, "_post_gemini", lambda p, t, m=None: "do gemini")
    r = providers.complete("olá")
    assert r is not None and r.provider == "gemini"


def test_resposta_traz_proveniencia(monkeypatch):
    """Saber QUEM serviu é o que permite medir fiabilidade em vez de a afirmar."""
    _com_chaves(monkeypatch)
    monkeypatch.setattr(providers, "_post_groq", lambda p, t, m=None: "texto")
    r = providers.complete("olá")
    assert r is not None
    assert r.model == providers.GROQ_MODEL
    assert r.latency_s >= 0.0


def test_timeout_e_propagado_ao_fornecedor(monkeypatch):
    """Um timeout generoso demais deixaria um ciclo pendurado à espera do LLM."""
    _com_chaves(monkeypatch, groq="g", gemini=None)
    visto = {}

    def _captura(p, t, m=None):
        visto["timeout"] = t
        visto["max_tokens"] = m
        return "ok"

    monkeypatch.setattr(providers, "_post_groq", _captura)
    providers.complete("olá", timeout=3.5)
    assert visto["timeout"] == 3.5


def test_orcamento_de_saida_e_propagado(monkeypatch):
    """O relatório de situação tem cinco secções e não cabe no orçamento de um alerta.

    Com os 300 tokens por defeito o texto era cortado a meio de uma frase — e um relatório
    que acaba a meio parece uma avaria, não um limite.
    """
    _com_chaves(monkeypatch, groq="g", gemini=None)
    visto = {}

    def _captura(p, t, m=None):
        visto["max_tokens"] = m
        return "ok"

    monkeypatch.setattr(providers, "_post_groq", _captura)
    providers.complete("olá", max_tokens=900)
    assert visto["max_tokens"] == 900
