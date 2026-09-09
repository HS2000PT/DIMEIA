"""O corpus não pode mudar de identidade sem que alguém o decida.

A 2026-09-08 uma reconstrução do corpus substituiu, em silêncio, o ficheiro sobre o qual a
tese foi avaliada: 78 481 linhas e quinze tickers no lugar de 79 753 e catorze. Nada partiu.
A avaliação de recuperação foi recorrida sobre o corpus errado e devolveu um número
plausível — 0,604 onde a tese diz 0,595 — que só não passou por variação de semente porque
a taxa de acaso também tinha mexido.

Este teste existe para que isso não volte a acontecer em silêncio. Fixa a identidade do
corpus da tese em três níveis: o manifesto (versionado, verificado sempre), o ficheiro de
trabalho (local, verificado quando existe) e a soma de controlo do ficheiro em bruto de
origem. Alterar o corpus passa a exigir alterar este teste — ou seja, uma decisão explícita.

Ver `docs/design/reproducao_corpus_2026-09-09.md` para a auditoria completa.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MANIFESTO = RAIZ / "docs" / "design" / "fnspid_corpus_manifest.json"
CORPUS = RAIZ / "data" / "fnspid_news_subset.csv"

#: Origem fixada. `resolve/main` é um ponteiro móvel e não serve de fonte.
REVISAO = "bf9189c41527198897d1af3e17b1a0095279fc45"
SHA_BRUTO = "1a7a3eb8e6b97ec19f286f2cfca3371542bddb272ab1eb8f36e33ad98fa5c4da"
BYTES_BRUTO = 23_232_979_597

#: Identidade do corpus da tese, reproduzida por varredura completa a 2026-09-09 e
#: conferida contra `docs/evaluation/kb_fnspid_build.md` (build de 2026-07-05).
SHA_CORPUS = "af61708c46ec8a0af10501ea48738e8b1a2cf2b6c61b2764547373b421d0197b"
LINHAS = 79_753
DATA_MIN = "2018-01-01"
DATA_MAX = "2023-12-16"
POR_TICKER = {
    "TSLA": 10_587, "NVDA": 10_059, "AAPL": 9_338, "MSFT": 8_737, "WMT": 8_686,
    "CVX": 7_416, "XOM": 7_346, "KO": 5_236, "AMZN": 5_060, "JPM": 2_883,
    "GOOGL": 1_754, "JNJ": 977, "PFE": 932, "BAC": 742,
}

#: Fecho independente, pelo lado da triagem: os blocos de
#: `docs/evaluation/evaluation_triage.md` mais o embargo declarado na tese.
BLOCOS_TRIAGEM = (28_574, 17_710, 32_649)
EMBARGO = 820


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def test_a_soma_por_ticker_da_o_total_declarado() -> None:
    assert sum(POR_TICKER.values()) == LINHAS
    assert len(POR_TICKER) == 14, "o FNSPID não indexa a META — ver §6 da auditoria"


def test_os_blocos_da_triagem_fecham_no_mesmo_corpus() -> None:
    """Verificação independente: treino+validação+teste+embargo = corpus."""
    assert sum(BLOCOS_TRIAGEM) + EMBARGO == LINHAS


def test_o_manifesto_declara_a_origem_fixada() -> None:
    assert MANIFESTO.exists(), (
        f"manifesto ausente: {MANIFESTO.relative_to(RAIZ)} — "
        "corre `python -m scripts.build_corpus_canonical`")
    m = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    fonte = m["fonte"]
    assert fonte["revisao"] == REVISAO, "a origem deixou de estar fixada na revisão auditada"
    assert fonte["sha256_em_bruto"] == SHA_BRUTO
    assert fonte["bytes_em_bruto"] == BYTES_BRUTO


def test_o_manifesto_descreve_o_corpus_da_tese() -> None:
    m = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    r = m["resultado"]
    assert r["linhas"] == LINHAS, (
        f"o corpus mudou de dimensão: {r['linhas']:,} != {LINHAS:,}. "
        "Se foi de propósito, actualiza este teste E os números da tese.")
    assert r["sha256"] == SHA_CORPUS
    assert r["data_min"] == DATA_MIN and r["data_max"] == DATA_MAX
    assert {k: int(v) for k, v in r["linhas_por_ticker"].items()} == POR_TICKER


def test_o_manifesto_proibe_a_paragem_antecipada() -> None:
    """As dezoito violações medidas tornam a paragem antecipada indefensável."""
    m = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    assert m["parametros"]["early_stop"] is False, (
        "o ficheiro em bruto NÃO está ordenado por ticker (18 violações medidas): "
        "a paragem antecipada trunca o corpus em silêncio")
    assert m["auditoria_varredura"]["violacoes_ordenacao"] > 0


@pytest.mark.skipif(not CORPUS.exists(), reason="corpus local ausente (data/** é gitignored)")
def test_o_corpus_em_disco_e_o_da_tese() -> None:
    obtido = sha256(CORPUS)
    assert obtido == SHA_CORPUS, (
        f"{CORPUS.relative_to(RAIZ)} não é o corpus da tese.\n"
        f"  obtido   {obtido}\n  esperado {SHA_CORPUS}\n"
        "Repõe a partir de data/fnspid_news_canonical.csv, ou reconstrói o canónico.")


@pytest.mark.skipif(not CORPUS.exists(), reason="corpus local ausente (data/** é gitignored)")
def test_o_corpus_em_disco_tem_a_composicao_declarada() -> None:
    with open(CORPUS, encoding="utf-8", newline="") as fh:
        linhas = list(csv.DictReader(fh))
    assert len(linhas) == LINHAS
    assert Counter(linha["ticker"] for linha in linhas) == Counter(POR_TICKER)
    datas = [linha["date"] for linha in linhas]
    assert min(datas) == DATA_MIN and max(datas) == DATA_MAX
