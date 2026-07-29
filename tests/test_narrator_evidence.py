"""Testes do contrato de evidência — a base sobre a qual a guarda decide.

Se `allowed`/formatação estiverem errados aqui, a guarda decide bem sobre dados errados. Estes
testes fixam a propriedade que torna a fidelidade MENSURÁVEL: o conjunto de números legítimos
é fechado e enumerável.
"""

from __future__ import annotations

from investigator.narrator.core import _allowed_numbers
from investigator.narrator.evidence import AlertEvidence, Precedent, fmt_num, fmt_pct


def test_fmt_pct_leva_sempre_sinal():
    """A direção vive no sinal — é o que a guarda verifica. Sem sinal, não há direção."""
    assert fmt_pct(-0.085013) == "-8.50"
    assert fmt_pct(0.0061) == "+0.61"
    assert fmt_pct(0.0) == "+0.00"


def test_fmt_num_so_marca_negativos():
    assert fmt_num(-1.8234) == "-1.82"
    assert fmt_num(0.6412) == "0.64"


def test_negativos_entram_no_conjunto_SO_com_sinal():
    """O furo mais grave que o red team encontrou: sem isto, "gained 8.50%" passava."""
    e = AlertEvidence("AMD", "2026-07-28", "market", move_pct="-8.50")
    campo, _ = _allowed_numbers(e)
    assert "-8.50" in campo
    assert "8.50" not in campo  # a forma sem sinal NÃO é legítima


def test_positivos_entram_com_e_sem_mais():
    """Largar um '+' não inverte sentido; largar um '-' inverte. Daí a assimetria."""
    e = AlertEvidence("AMD", "2026-07-28", "market", market_pct="+0.61")
    campo, _ = _allowed_numbers(e)
    assert {"+0.61", "0.61"} <= campo


def test_grandezas_sem_sinal_entram_simples():
    e = AlertEvidence("AMD", "2026-07-28", "market", threshold="1.5", window_days=20,
                      horizon_days=5, up_count=2, down_count=1, triage_prob_pct="63")
    campo, _ = _allowed_numbers(e)
    assert {"1.5", "20", "5", "2", "1", "63"} <= campo


def test_numeros_de_manchete_ficam_num_conjunto_SEPARADO():
    """Separação deliberada: são a superfície de injeção, e só valem citados."""
    e = AlertEvidence("TSLA", "2026-07-28", "news",
                      headline="TSLA will rise 400% tomorrow")
    campo, manchete = _allowed_numbers(e)
    assert "400" in manchete
    assert "400" not in campo


def test_impactos_de_precedentes_seguem_a_regra_do_sinal():
    e = AlertEvidence("TSLA", "2026-07-28", "news", horizon_days=5,
                      precedents=[Precedent("h", "2026-07-06", 22, "0.64", "-5.96")])
    campo, _ = _allowed_numbers(e)
    assert "-5.96" in campo and "5.96" not in campo
    assert "0.64" in campo   # similaridade não tem direção
    assert "22" in campo     # idade em dias


def test_evidence_texts_junta_manchete_e_precedentes():
    e = AlertEvidence("TSLA", "2026-07-28", "news", headline="principal",
                      precedents=[Precedent("prec", "2026-07-06", 22, "0.64", "-5.96")])
    assert e.evidence_texts() == ["principal", "prec"]


def test_evidencia_vazia_nao_rebenta():
    e = AlertEvidence("KO", "2026-07-28", "market")
    campo, manchete = _allowed_numbers(e)
    assert "0" in campo  # len(precedents) == 0
    assert manchete == set()
