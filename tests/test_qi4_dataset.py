"""A coluna nova tem de concordar com a antiga.

`abn_h3` é o retorno anormal contínuo que a QI4 introduz. O rótulo binário
`label_t0.02_h3`, esse, já existia e já foi usado em toda a §5.4. Se a coluna nova estiver
certa, o rótulo tem de ser exactamente `|abn_h3| >= 0,02` — e é isso que se verifica aqui,
sobre as 79 753 linhas reais, e não sobre um exemplo inventado.

É uma verificação barata e decisiva: apanha uma troca de horizonte, um sinal perdido, um
desalinhamento de índices, ou a coluna a ser preenchida a partir da série errada.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
QI4 = RAIZ / "data" / "qi4_dataset.csv"
TAU, H = 0.02, 3

pytestmark = pytest.mark.skipif(
    not QI4.exists(), reason="dataset QI4 local ausente (data/** é gitignored)")


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return pd.read_csv(QI4)


def test_traz_as_colunas_continuas(df):
    for h in (1, 3, 5):
        assert f"abn_h{h}" in df.columns


def test_a_dimensao_e_os_blocos_sao_os_da_tese(df):
    assert len(df) == 79_753
    assert df["split"].value_counts().to_dict() == {
        "test": 32_649, "train": 28_574, "val": 17_710, "embargo": 820}


def test_o_rotulo_binario_e_exactamente_o_limiar_sobre_a_coluna_continua(df):
    """⚠️ O teste que valida a coluna nova contra uma que já foi usada na tese inteira."""
    derivado = (df[f"abn_h{H}"].abs() >= TAU).astype(int)
    publicado = pd.to_numeric(df[f"label_t{TAU:g}_h{H}"], errors="coerce")
    divergentes = int((derivado != publicado).sum())
    assert divergentes == 0, (
        f"{divergentes} linhas em que |abn_h{H}| >= {TAU} não bate com o rótulo publicado")


def test_o_rotulo_primario_e_o_mesmo_do_limiar(df):
    """`label` é o rótulo primário; tem de coincidir com o par (τ, h) declarado."""
    assert (df["label"] == pd.to_numeric(df[f"label_t{TAU:g}_h{H}"], errors="coerce")).all()


def test_ha_movimentos_dos_dois_sinais_em_quantidade_comparavel(df):
    """Se a coluna tivesse perdido o sinal, isto denunciava-o."""
    frac_neg = float((df[f"abn_h{H}"] < 0).mean())
    assert 0.35 < frac_neg < 0.65, f"fração de retornos negativos suspeita: {frac_neg:.3f}"
