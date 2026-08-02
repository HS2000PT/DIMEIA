"""Testes da camada de logótipos. Nenhum toca na rede."""

from __future__ import annotations

import base64

import pytest

from investigator.branding.logos import (
    _suffix_for,
    cached_logo,
    data_uri,
    parse_branding,
)

WEBP = b"RIFF" + b"\x00\x00\x00\x00" + b"WEBP" + b"VP8 resto"
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF"
PNG = b"\x89PNG\r\n\x1a\n"
SVG = b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'


@pytest.mark.parametrize(
    ("raw", "esperado"),
    [(WEBP, ".webp"), (JPEG, ".jpg"), (PNG, ".png"), (SVG, ".svg"),
     (b"  <?xml version=\"1.0\"?><svg/>", ".svg"), (b"lixo qualquer", ".bin")],
)
def test_extensao_vem_dos_bytes_nao_do_url(raw: bytes, esperado: str) -> None:
    assert _suffix_for(raw) == esperado


def test_webp_e_reconhecido() -> None:
    """Regressão: sem isto, a Apple parecia uma empresa sem logótipo.

    O ficheiro chegava inteiro e era descartado como formato desconhecido, porque o WebP
    não se distingue pelos primeiros bytes (`RIFF`, partilhado com WAV e AVI) — a marca
    está no oitavo.
    """
    assert _suffix_for(WEBP) == ".webp"
    # Um RIFF que NÃO é WebP não pode passar por um.
    assert _suffix_for(b"RIFF\x00\x00\x00\x00WAVEfmt ") == ".bin"


def test_parse_branding_prefere_o_icone_quadrado() -> None:
    payload = {"results": {"branding": {"logo_url": "L", "icon_url": "I"}}}
    assert parse_branding(payload) == "I"


def test_parse_branding_cai_para_o_outro_tipo() -> None:
    assert parse_branding({"results": {"branding": {"logo_url": "L"}}}) == "L"


@pytest.mark.parametrize("payload", [{}, {"results": {}}, {"results": {"branding": {}}}])
def test_parse_branding_sem_marca_devolve_none(payload: dict) -> None:
    assert parse_branding(payload) is None


def test_data_uri_usa_o_mime_certo() -> None:
    assert data_uri(SVG, ".svg").startswith("data:image/svg+xml;base64,")
    assert data_uri(WEBP, ".webp").startswith("data:image/webp;base64,")
    corpo = data_uri(JPEG, ".jpg").split(",", 1)[1]
    assert base64.b64decode(corpo) == JPEG


def test_cached_logo_sem_ficheiro_devolve_none(tmp_path) -> None:
    """Sem logótipo a interface desenha as iniciais — nunca um ícone partido."""
    assert cached_logo("ZZZZ", directory=tmp_path) is None


def test_cached_logo_le_do_disco(tmp_path) -> None:
    (tmp_path / "NVDA.png").write_bytes(PNG)
    assert cached_logo("nvda", directory=tmp_path).startswith("data:image/png;base64,")


def test_cached_logo_ignora_bin(tmp_path) -> None:
    """Um `.bin` é um formato que não soubemos ler; servi-lo daria uma imagem partida."""
    (tmp_path / "XX.bin").write_bytes(b"lixo")
    assert cached_logo("XX", directory=tmp_path) is None
