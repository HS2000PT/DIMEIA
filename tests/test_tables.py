"""Os filtros da tabela de eventos, em forma executável. Puros: sem rede, sem Streamlit."""

from __future__ import annotations

from app.tables import (
    MAGNITUDES,
    ORDERS,
    anchor,
    filter_events,
    paginate,
    sort_events,
    within,
)

# Uma semana de sessões: 6ª feira, depois o salto do fim de semana, depois 2ª e 3ª.
SESSOES = ["2026-07-17", "2026-07-20", "2026-07-21", "2026-07-22"]

LINHAS = [
    {"date": "2026-07-24", "headline": "Nvidia beats on earnings", "d1": 0.031, "d5": 0.052},
    {"date": "2026-07-23", "headline": "Chip export curbs widen", "d1": -0.024, "d5": -0.061},
    {"date": "2026-07-22", "headline": "Analyst note on AI demand", "d1": 0.004, "d5": -0.012},
    {"date": "2026-07-21", "headline": "Partnership with AMKR", "d1": None, "d5": None},
    {"date": "2026-07-20", "headline": "Quiet session for chips", "d1": -0.002, "d5": 0.003},
]


# ── filtro por texto ─────────────────────────────────────────────────────────────────

def test_procura_ignora_maiusculas() -> None:
    assert len(filter_events(LINHAS, query="NVIDIA")) == 1
    assert len(filter_events(LINHAS, query="nvidia")) == 1


def test_procura_vazia_nao_filtra_nada() -> None:
    assert len(filter_events(LINHAS, query="   ")) == len(LINHAS)


def test_procura_sem_resultados_devolve_lista_vazia_e_nao_a_lista_toda() -> None:
    """O modo de falha que se disfarça: um filtro que não bate e "falha aberto"."""
    assert filter_events(LINHAS, query="zzz não existe") == []


# ── filtro por direcção e magnitude ──────────────────────────────────────────────────

def test_direccao_separa_subidas_de_descidas() -> None:
    assert [r["date"] for r in filter_events(LINHAS, direction="Up")] == \
        ["2026-07-24", "2026-07-22"]
    assert [r["date"] for r in filter_events(LINHAS, direction="Down")] == \
        ["2026-07-23", "2026-07-20"]


def test_magnitude_corta_pelo_valor_absoluto() -> None:
    datas = [r["date"] for r in filter_events(LINHAS, min_abs=MAGNITUDES["≥2%"])]
    assert datas == ["2026-07-24", "2026-07-23"]


def test_registo_sem_impacto_passa_quando_nao_se_filtra_por_impacto() -> None:
    """Uma notícia recente demais para o horizonte ter fechado continua a ser notícia."""
    assert any(r["d1"] is None for r in filter_events(LINHAS, query="AMKR"))


def test_registo_sem_impacto_cai_quando_se_filtra_por_impacto() -> None:
    """Ausência não é zero. Quem pede "quedas ≥2%" não pode receber uma medição que falta."""
    assert not any(r["d1"] is None for r in filter_events(LINHAS, direction="Down"))
    assert not any(r["d1"] is None for r in filter_events(LINHAS, min_abs=0.01))


def test_nan_e_tratado_como_ausencia_e_nao_como_numero() -> None:
    linhas = [*LINHAS, {"date": "2026-07-19", "headline": "x", "d1": float("nan")}]
    assert not any(r["date"] == "2026-07-19"
                   for r in filter_events(linhas, direction="Up"))


# ── ordenação ────────────────────────────────────────────────────────────────────────

def test_ordem_por_defeito_e_a_mais_recente_primeiro() -> None:
    assert sort_events(LINHAS)[0]["date"] == "2026-07-24"
    assert sort_events(LINHAS, "Oldest first")[0]["date"] == "2026-07-20"


def test_maior_movimento_usa_o_modulo_e_nao_o_sinal() -> None:
    """Uma queda de 2,4% é um movimento maior do que uma subida de 0,4%."""
    ordenado = sort_events(LINHAS, "Largest move first")
    assert [r["date"] for r in ordenado[:3]] == \
        ["2026-07-24", "2026-07-23", "2026-07-22"]


def test_ausencias_vao_para_o_fim_e_nunca_para_o_topo() -> None:
    """No topo, uma ausência lê-se como se fosse o maior movimento da lista."""
    assert sort_events(LINHAS, "Largest move first")[-1]["d1"] is None


def test_ordenar_nunca_perde_uma_linha() -> None:
    for ordem in ORDERS:
        assert len(sort_events(LINHAS, ordem)) == len(LINHAS)


# ── paginação ────────────────────────────────────────────────────────────────────────

def test_paginacao_parte_a_lista_sem_sobrepor_nem_saltar() -> None:
    p1, _, n = paginate(LINHAS, page=1, per_page=2)
    p2, _, _ = paginate(LINHAS, page=2, per_page=2)
    p3, _, _ = paginate(LINHAS, page=3, per_page=2)
    assert n == 3
    assert [r["date"] for r in p1 + p2 + p3] == [r["date"] for r in LINHAS]


def test_pagina_alem_do_fim_e_corrigida_em_vez_de_devolver_vazio() -> None:
    """O defeito clássico: filtrar estando na página 5 e ficar com uma tabela vazia.

    Com dados, com filtros que combinam, e sem mensagem nenhuma — o utilizador conclui
    que não há nada. A página devolvida é a corrigida, para o ecrã poder dizer "3 de 3".
    """
    fatia, pagina, n_pages = paginate(LINHAS, page=99, per_page=2)
    assert pagina == n_pages == 3
    assert fatia


def test_pagina_zero_ou_negativa_nao_rebenta() -> None:
    fatia, pagina, _ = paginate(LINHAS, page=0, per_page=2)
    assert pagina == 1 and len(fatia) == 2
    assert paginate(LINHAS, page=-7, per_page=2)[1] == 1


def test_lista_vazia_tem_uma_pagina_e_nao_zero() -> None:
    """"Page 1 of 0" não quer dizer nada."""
    fatia, pagina, n_pages = paginate([], page=1, per_page=8)
    assert fatia == [] and pagina == 1 and n_pages == 1


# ── janela do gráfico ────────────────────────────────────────────────────────────────

def test_a_janela_e_inclusiva_nos_dois_extremos() -> None:
    """Um marcador desenhado exactamente no primeiro dia do gráfico tem de ter linha."""
    datas = [r["date"] for r in within(LINHAS, "2026-07-21", "2026-07-23")]
    assert datas == ["2026-07-23", "2026-07-22", "2026-07-21"]


def test_sem_janela_nao_filtra() -> None:
    assert len(within(LINHAS, None, None)) == len(LINHAS)


def test_linha_sem_data_nao_entra_numa_janela() -> None:
    """Sem data não se pode afirmar que está na janela, logo não se afirma."""
    assert within([{"date": "", "headline": "x"}], "2026-01-01", "2026-12-31") == []


# ── âncora: onde uma notícia de fim de semana se desenha ─────────────────────────────

def test_uma_data_que_e_sessao_ancora_em_si_propria() -> None:
    """`bisect_right` desviaria TODAS as marcas um dia — invisível a olho, e errado."""
    for dia in SESSOES:
        assert anchor(SESSOES, dia) == dia


def test_noticia_de_fim_de_semana_ancora_na_sessao_seguinte() -> None:
    """Sábado e domingo caem na segunda — a mesma regra com que o impacto foi medido."""
    assert anchor(SESSOES, "2026-07-18") == "2026-07-20"
    assert anchor(SESSOES, "2026-07-19") == "2026-07-20"


def test_data_anterior_a_janela_nao_ancora_na_primeira_barra() -> None:
    """O caso que empilharia um ano de marcas num só ponto do lado esquerdo."""
    assert anchor(SESSOES, "2026-01-05") is None


def test_data_posterior_a_janela_nao_ancora() -> None:
    assert anchor(SESSOES, "2026-08-30") is None


def test_lista_de_sessoes_vazia_nao_rebenta() -> None:
    assert anchor([], "2026-07-20") is None
