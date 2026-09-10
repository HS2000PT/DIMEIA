"""O verificador da bibliografia nao pode chamar «nao resolve» a um DOI que resolve.

O caso que motivou estes testes: `10.1609/aimag.v12i2.895` (Kolodner, AI Magazine, 1991).
A AAAI nao depositou os numeros de 1991 no Crossref, pelo que `api.crossref.org` devolve 404 --
mas `https://doi.org/...` redireciona com 200 para a pagina do editor. O verificador dizia
«DOI **nao resolve**», o que e falso, e um relatorio que afirma isso engana quem o le.

Regra que estes testes fixam:
  - Crossref tem registo            -> verificacao campo a campo, como antes;
  - Crossref nao tem, doi.org tem   -> NOTA (nao achado), a dizer onde foi verificado;
  - nem Crossref nem doi.org        -> ACHADO, com a mensagem antiga.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def carregar():
    """Importa o script por caminho: vive em scripts/ e nao e um modulo do pacote."""
    caminho = RAIZ / "scripts" / "verify_bibliography.py"
    espec = importlib.util.spec_from_file_location("verify_bibliography", caminho)
    modulo = importlib.util.module_from_spec(espec)
    sys.modules["verify_bibliography"] = modulo
    espec.loader.exec_module(modulo)
    return modulo


@pytest.fixture()
def vb():
    return carregar()


def entrada(**campos):
    base = {"author": "Kolodner, Janet L.", "title": "Improving Human Decision Making",
            "year": "1991", "journal": "AI Magazine"}
    base.update(campos)
    return {"ficheiro": "references.bib", "chave": "teste", "tipo": "article", "campos": base}


# --------------------------------------------------------------- o caso que motivou tudo
def test_doi_fora_do_crossref_mas_vivo_e_nota_e_nao_achado(vb, monkeypatch):
    monkeypatch.setattr(vb, "crossref_por_doi", lambda doi: None)
    monkeypatch.setattr(vb, "doi_resolve", lambda doi: True)
    r = vb.verificar(entrada(doi="10.1609/aimag.v12i2.895"))
    assert r["achados"] == [], f"nao devia acusar: {r['achados']}"
    assert any("doi.org" in n for n in r["notas"]), r["notas"]
    assert "doi.org" in r["resolvido"]


def test_doi_morto_continua_a_ser_achado(vb, monkeypatch):
    monkeypatch.setattr(vb, "crossref_por_doi", lambda doi: None)
    monkeypatch.setattr(vb, "doi_resolve", lambda doi: False)
    r = vb.verificar(entrada(doi="10.0000/nao-existe"))
    assert any("não resolve" in a for a in r["achados"]), r["achados"]
    assert r["notas"] == [] or all("doi.org" not in n for n in r["notas"])


def test_com_registo_no_crossref_nao_se_chama_doi_org(vb, monkeypatch):
    """O caminho normal nao pode ganhar uma consulta de rede extra por entrada."""
    chamadas = []
    registo = {
        "title": ["Improving Human Decision Making"],
        "issued": {"date-parts": [[1991]]},
        "container-title": ["AI Magazine"],
        "author": [{"family": "Kolodner", "given": "Janet L."}],
    }
    monkeypatch.setattr(vb, "crossref_por_doi", lambda doi: registo)
    monkeypatch.setattr(vb, "doi_resolve", lambda doi: chamadas.append(doi) or True)
    r = vb.verificar(entrada(doi="10.1609/aimag.v12i2.895"))
    assert chamadas == [], "doi_resolve nao devia ser chamado quando o Crossref responde"
    assert r["resolvido"].startswith("Crossref")


# ------------------------------------------------------------- a funcao nova, isoladamente
def test_doi_resolve_devolve_falso_quando_a_rede_falha(vb, monkeypatch):
    def rebenta(url, **kwargs):
        raise OSError("sem rede")

    monkeypatch.setattr(vb, "obter", rebenta)
    assert vb.doi_resolve("10.1234/seja-o-que-for") is False


def test_doi_resolve_pede_o_endereco_certo(vb, monkeypatch):
    vistos = []

    def falso(url, **kwargs):
        vistos.append(url)
        return b""

    monkeypatch.setattr(vb, "obter", falso)
    assert vb.doi_resolve("10.1609/aimag.v12i2.895") is True
    assert vistos == ["https://doi.org/10.1609/aimag.v12i2.895"]


def test_doi_resolve_codifica_caracteres_estranhos(vb, monkeypatch):
    vistos = []
    monkeypatch.setattr(vb, "obter", lambda url, **k: vistos.append(url) or b"")
    vb.doi_resolve("10.1016/0304-405X(85)90042-X")
    assert vistos[0].startswith("https://doi.org/10.1016/0304-405X")


# ------------------------------------------------------- o resto do comportamento mantem-se
def test_sem_identificador_continua_a_ser_achado(vb):
    r = vb.verificar(entrada())
    assert any("sem identificador" in a for a in r["achados"]), r["achados"]
