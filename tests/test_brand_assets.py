"""Portas do conjunto canónico da marca, sem rede."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app" / "assets"
SVG_NS = {"svg": "http://www.w3.org/2000/svg"}
PIECES = (
    "logo-lockup",
    "logo-lockup-tagline",
    "logo-empilhado",
    "logo-marca",
    "logo-nome",
)
PALETTES = {
    "": ("#14171A", "#0A8F52"),
    "-dark": ("#F3F7F5", "#00E37A"),
    "-mono": ("currentColor", "currentColor"),
}
TAIL_D = (
    "M22 206 C 74 202, 122 180, 158 142 C 182 116, 202 86, 226 52 "
    "L 214 46 L 202 70 L 186 60 L 170 88 L 152 78 L 134 108 L 112 98 "
    "L 92 130 L 66 120 L 44 154 L 16 146 Z"
)


def _normalise_path(value: str) -> str:
    return " ".join(value.replace(",", " ").split())


@pytest.mark.parametrize("piece", PIECES)
@pytest.mark.parametrize("suffix", PALETTES)
def test_canonical_svg_is_portable_and_valid(piece: str, suffix: str) -> None:
    path = ASSETS / f"{piece}{suffix}.svg"
    source = path.read_text(encoding="utf-8")

    assert "<text" not in source.lower()
    assert "font-family" not in source.lower()
    root = ET.fromstring(source)
    assert root.attrib["role"] == "img"
    assert root.attrib["aria-label"]
    assert root.findall(".//svg:path", SVG_NS)


@pytest.mark.parametrize("piece", ("logo-lockup", "logo-lockup-tagline", "logo-empilhado"))
@pytest.mark.parametrize("suffix", PALETTES)
def test_every_composed_asset_uses_the_canonical_tail(piece: str, suffix: str) -> None:
    root = ET.parse(ASSETS / f"{piece}{suffix}.svg").getroot()
    paths = root.findall(".//svg:path", SVG_NS)
    assert _normalise_path(paths[0].attrib["d"]) == _normalise_path(TAIL_D)


@pytest.mark.parametrize(
    "piece",
    ("logo-lockup", "logo-lockup-tagline", "logo-empilhado", "logo-nome"),
)
@pytest.mark.parametrize("suffix", PALETTES)
def test_gator_is_a_complete_colour_unit(piece: str, suffix: str) -> None:
    ink, accent = PALETTES[suffix]
    root = ET.parse(ASSETS / f"{piece}{suffix}.svg").getroot()
    investi = root.find(".//svg:g[@data-part='investi']", SVG_NS)
    gator = root.find(".//svg:g[@data-part='gator']", SVG_NS)

    assert investi is not None and investi.attrib["fill"] == ink
    assert gator is not None and gator.attrib["fill"] == accent
    assert len(gator.findall("svg:path", SVG_NS)) == len("Gator")


def test_tagline_is_outlined_and_current() -> None:
    source = (ASSETS / "logo-lockup-tagline.svg").read_text(encoding="utf-8")
    root = ET.fromstring(source)
    tagline = root.find(".//svg:g[@data-part='tagline']", SVG_NS)

    assert tagline is not None
    assert "Markets move. We investigate." in root.attrib["aria-label"]
    assert "Every move investigated" not in source


def test_web_header_uses_the_same_tail_and_colour_split() -> None:
    source = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    match = re.search(
        r'<a class="marca".*?<svg.*?<path d="([^"]+)"',
        source,
        flags=re.DOTALL,
    )

    assert match is not None
    assert _normalise_path(match.group(1)) == _normalise_path(TAIL_D)
    assert "<b>Investi<i>Gator</i></b>" in source
    assert re.search(r"\.marca b i\s*\{[^}]*color:var\(--acento\)", source)


@pytest.mark.parametrize("suffix", PALETTES)
def test_legacy_wordmark_alias_stays_identical(suffix: str) -> None:
    canonical = (ASSETS / f"logo-nome{suffix}.svg").read_bytes()
    legacy = (ASSETS / f"logo-wordmark{suffix}.svg").read_bytes()
    assert legacy == canonical


def test_manifest_describes_the_closed_set() -> None:
    manifest = json.loads((ASSETS / "brand" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "InvestiGator"
    assert manifest["slogan"] == "Markets move. We investigate."
    assert manifest["pieces"] == list(PIECES)
    assert manifest["variants"] == ["light", "dark", "mono"]
    assert manifest["wordmark_split"] == {"ink": "Investi", "accent": "Gator"}


@pytest.mark.parametrize("piece", PIECES)
def test_light_png_exports_have_512_pixel_width(piece: str) -> None:
    path = ASSETS / "brand" / "png" / f"{piece}-512.png"
    with Image.open(path) as image:
        assert image.width == 512
        assert image.mode == "RGBA"


def test_telegram_avatar_is_square_with_a_rounded_opaque_container() -> None:
    with Image.open(ASSETS / "telegram_avatar.png") as image:
        assert image.size == (512, 512)
        assert image.mode == "RGBA"
        assert image.getpixel((256, 256))[3] == 255
        assert image.getpixel((0, 0))[3] == 0
