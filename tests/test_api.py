"""Testes do CAMINHO VIVO — a API que o produto implantado serve.

⚠️ **Porque é que este ficheiro existe.** Até aqui a suíte tinha **zero** testes a tocar em `api/`
ou `web/` — os 359 + 352 linhas que estão de facto no ar — enquanto o Streamlit **retirado** tinha
67. A cobertura estava toda no que já não se serve.

**Todos offline.** O `api.services` vai à rede buscar o instantâneo e o histórico; aqui é
substituído por dados sintéticos, para o teste medir o código e não a ligação. Um teste que depende
da Internet mede a Internet.

A regra que estes testes protegem, e que é a mais fácil de partir sem dar por isso:
**nenhum número é calculado na API.** Se um dia alguém recalcular aqui, o produto e a avaliação
podem divergir em silêncio — é a classe de defeito que este projecto já pagou três vezes.
"""

from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from api import main as api_main  # noqa: E402
from api import services as S  # noqa: E402

SNAP = {
    "as_of": "2026-08-14T17:00:00+00:00",
    "age_label": "1 min ago",
    "age_s": 60.0,
    "fresh": True,
    "remote": False,
    "rows": [
        {"ticker": "NVDA", "move": -0.0235, "z": -0.99, "flagged": False,
         "rarity": {"count": 72, "n": 249, "move": -0.0235, "same_direction": 35},
         "decomp": {"market": -0.001, "sector": -0.004, "company": -0.018, "driver": "company"},
         "vol_ratio": 1.2, "closes": [["2026-08-13", 100.0], ["2026-08-14", 97.65]],
         "events": [], "intraday": []},
        {"ticker": "XOM", "move": 0.0447, "z": 2.65, "flagged": True,
         "rarity": {"count": 2, "n": 249, "move": 0.0447, "same_direction": 2},
         "decomp": {"market": 0.0002, "sector": 0.0337, "company": 0.0108, "driver": "sector"},
         "vol_ratio": 2.4, "closes": [["2026-08-14", 110.0]], "events": [], "intraday": []},
    ],
}


@pytest.fixture(autouse=True)
def _sem_rede(monkeypatch):
    monkeypatch.setattr(S, "snapshot", lambda: SNAP)
    monkeypatch.setattr(S, "alerts", lambda: [
        {"date": "2026-08-14", "ticker": "NVDA", "kind": "news", "text": "News alert for NVDA"},
    ])
    monkeypatch.setattr(S, "news_days", lambda t, limit=400: [])
    monkeypatch.setattr(S, "screener", lambda: [
        {"ticker": "XOM", "stage": "weak_precedent", "detail": "sim 0.31 < 0.45"},
    ])
    monkeypatch.setattr(S, "market_state", lambda: {"open": False, "label": "closed"})
    monkeypatch.setattr(S, "watchlist", lambda: ["NVDA", "XOM"])


@pytest.fixture
def client():
    return TestClient(api_main.app)


def test_health_responde_e_declara_a_frescura(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["as_of"] == SNAP["as_of"]


def test_overview_serve_tudo_num_pedido(client):
    """O critério de desempenho da v5 é 'a primeira pintura num só pedido'. Se alguém partir o
    overview em duas rotas, o critério vai-se e ninguém dá por isso."""
    d = client.get("/api/overview").json()
    for chave in ("rows", "market", "watchlist", "as_of", "window", "threshold"):
        assert chave in d, f"falta {chave} — a primeira pintura deixaria de caber num pedido"
    assert len(d["rows"]) == 2


def test_overview_decora_com_veredicto_e_nome(client):
    """O veredicto é calculado em Python (29 testes) e não em JavaScript, de propósito: reescrevê-lo
    no cliente criava uma segunda verdade que ninguém testaria."""
    linhas = {r["ticker"]: r for r in client.get("/api/overview").json()["rows"]}
    assert linhas["XOM"]["verdict"], "sem veredicto — a página abriria com números e sem frase"
    assert linhas["XOM"]["name"] and linhas["XOM"]["name"] != "XOM"


def test_asset_desconhecido_devolve_404_e_nao_500(client):
    r = client.get("/api/asset/ZZZZ")
    assert r.status_code == 404
    assert "watchlist" in r.json()["error"]


def test_asset_devolve_a_serie_sem_recalcular_nada(client):
    d = client.get("/api/asset/NVDA").json()
    assert d["ticker"] == "NVDA"
    # Os valores têm de ser os do instantâneo, byte a byte: a API serve, não calcula.
    assert d["move"] == SNAP["rows"][0]["move"]
    assert d["z"] == SNAP["rows"][0]["z"]
    assert d["decomp"] == SNAP["rows"][0]["decomp"]


def test_screener_expoe_a_etapa_e_a_margem(client):
    """A vista existe para tornar o silêncio inspeccionável; sem a margem, dizia 'não' sem dizer
    por quanto."""
    linhas = client.get("/api/screener").json()["rows"]
    assert linhas and linhas[0]["stage"] == "weak_precedent"
    assert "0.45" in linhas[0]["detail"]


def test_evidence_declara_proveniencia_e_nao_tem_facto_gerado(client):
    """A garantia central da camada de inteligência: o gerador escreve prosa, nunca factos.
    Se algum registo aparecer com proveniência 'generated', a afirmação da tese cai."""
    d = client.get("/api/evidence?scope=market").json()
    assert d["facts"], "pacote vazio — o relatório não teria o que citar"
    origens = {f["origin"] for f in d["facts"]}
    assert origens <= {"measured", "computed", "model"}, f"proveniência inesperada: {origens}"
    assert all(f["id"].startswith("f") for f in d["facts"])


def test_spa_serve_o_index_em_rotas_profundas(client):
    """`?t=NVDA` e o botão 'voltar' do browser só funcionam se qualquer caminho cair no index."""
    r = client.get("/qualquer/caminho/inexistente")
    assert r.status_code == 200
    assert "html" in r.headers.get("content-type", "")


def test_precedentes_indisponiveis_degradam_em_vez_de_rebentar(client, monkeypatch):
    """Fail-open em toda a superfície: uma rota que devolve 500 porque o modelo não está presente
    transforma uma indisponibilidade parcial numa página branca."""
    monkeypatch.setattr(S, "precedents", lambda t, top_k=4, query=None: None)
    d = client.get("/api/precedents/NVDA").json()
    assert d["available"] is False
    assert d["reason"]
