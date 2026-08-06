"""Testes da camada de instantâneo da v4 — a parte pura, sem rede nem Streamlit."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from app.snapshot_io import carregar, resumo_do_dia, tira_distribuicao


def _escrever(tmp_path, gerado, linhas):
    p = tmp_path / "snap.json"
    p.write_text(json.dumps({"generated_at": gerado, "rows": linhas}), encoding="utf-8")
    return p


def test_instantaneo_fresco_e_lido(tmp_path):
    agora = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
    p = _escrever(tmp_path, (agora - timedelta(seconds=30)).isoformat(),
                  [{"ticker": "NVDA", "z": 0.4, "move": 0.01}])
    s = carregar(p, agora=agora)
    assert s is not None
    assert s.fresco and s.idade_s == 30
    assert s.idade_legivel == "30s ago"


def test_instantaneo_velho_e_lido_MAS_marcado_como_nao_fresco(tmp_path):
    """Velho não é o mesmo que ausente: mostra-se, com a idade à vista (critério P3)."""
    agora = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
    p = _escrever(tmp_path, (agora - timedelta(minutes=40)).isoformat(),
                  [{"ticker": "NVDA", "z": 0.4}])
    s = carregar(p, agora=agora)
    assert s is not None
    assert not s.fresco
    assert s.idade_legivel == "40m ago"


def test_ficheiro_ausente_ou_corrompido_devolve_None_e_nao_rebenta(tmp_path):
    assert carregar(tmp_path / "nao-existe.json") is None
    mau = tmp_path / "mau.json"
    mau.write_text("{ isto não é json", encoding="utf-8")
    assert carregar(mau) is None
    vazio = tmp_path / "vazio.json"
    vazio.write_text(json.dumps({"generated_at": "2026-08-06T12:00:00+00:00", "rows": []}),
                     encoding="utf-8")
    assert carregar(vazio) is None, "sem linhas é o mesmo que sem instantâneo"


def test_resumo_do_dia_responde_antes_de_mostrar_numeros():
    calmo = [{"ticker": t, "z": 0.3} for t in ("AAPL", "MSFT", "NVDA")]
    assert "Nothing stood out" in resumo_do_dia(calmo)

    um = [{"ticker": "NVDA", "z": 3.1}] + [{"ticker": "AAPL", "z": 0.2}]
    frase = resumo_do_dia(um)
    assert "One name stood out" in frase and "NVDA" in frase

    varios = [{"ticker": "NVDA", "z": 3.1}, {"ticker": "AMD", "z": -2.4},
              {"ticker": "AAPL", "z": 0.2}]
    assert "2 of 3 stood out" in resumo_do_dia(varios)


def test_resumo_nunca_usa_vocabulario_de_previsao():
    """H2: zero números previstos, zero linguagem de previsão."""
    proibido = ("will ", "expect", "forecast", "predict", "target", "should rise", "likely to")
    for linhas in ([{"ticker": "NVDA", "z": 4.0}],
                   [{"ticker": "A", "z": 0.1}, {"ticker": "B", "z": 0.1}],
                   []):
        frase = resumo_do_dia(linhas).lower()
        for termo in proibido:
            assert termo not in frase, f"{termo!r} em {frase!r}"


def test_tira_de_distribuicao_reflecte_a_proporcao():
    rara = tira_distribuicao(2, 250)
    comum = tira_distribuicao(200, 250)
    assert rara.count("strip-on") < comum.count("strip-on")
    assert tira_distribuicao(None, 250) == ""
    assert tira_distribuicao(5, None) == ""


def test_tira_com_zero_excedencias_nao_acende_nada():
    """'Nenhum outro dia se moveu assim' tem de ser visível como tira vazia."""
    assert tira_distribuicao(0, 249).count("strip-on") == 0
