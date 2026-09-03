"""Constrói o conjunto canónico da marca InvestiGator.

A geometria da cauda vem de ``app/assets/logo.svg`` e o nome usa os ficheiros IBM Plex
que já acompanham a interface. As letras são convertidas em contornos SVG: nenhum ficheiro
final depende de tipos de letra instalados na máquina que o abre.

Uso:
    python scripts/build_brand_assets.py

Saídas:
    * cinco peças SVG, cada uma em claro, escuro e monocromático;
    * aliases legados do nome, para não partir consumidores antigos;
    * PNG de 512 px das cinco peças claras e o avatar do Telegram;
    * folha de comparação da decisão cromática.
"""

from __future__ import annotations

import html
import json
import pathlib
import sys
from dataclasses import dataclass

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont
except ImportError as exc:  # pragma: no cover - mensagem de instalação para uso manual
    raise SystemExit(
        "Falta FontTools. Instala as dependências de desenvolvimento antes de regenerar a marca."
    ) from exc


ROOT = pathlib.Path(__file__).resolve().parents[1]
ASSETS = ROOT / "app" / "assets"
FONTS = ROOT / "web" / "assets" / "fonts"
PNG_DIR = ASSETS / "brand" / "png"
COMPARISON = ROOT / "docs" / "design" / "brand-comparison.png"

WORDMARK = "InvestiGator"
SLOGAN = "Markets move. We investigate."
TAIL_D = (
    "M22 206 C 74 202, 122 180, 158 142 C 182 116, 202 86, 226 52 "
    "L 214 46 L 202 70 L 186 60 L 170 88 L 152 78 L 134 108 L 112 98 "
    "L 92 130 L 66 120 L 44 154 L 16 146 Z"
)


@dataclass(frozen=True)
class Palette:
    suffix: str
    ink: str
    accent: str
    label: str


PALETTES = (
    Palette("", "#14171A", "#0A8F52", "para fundo claro"),
    Palette("-dark", "#F3F7F5", "#00E37A", "para fundo escuro"),
    Palette("-mono", "currentColor", "currentColor", "monocromática"),
)

PIECES = (
    "logo-lockup",
    "logo-lockup-tagline",
    "logo-empilhado",
    "logo-marca",
    "logo-nome",
)


class OutlineFont:
    """Converte texto ASCII em elementos ``path`` posicionados."""

    def __init__(self, path: pathlib.Path) -> None:
        try:
            self.font = TTFont(path)
        except ImportError as exc:  # WOFF2 requer Brotli no FontTools
            raise SystemExit(
                "Falta Brotli para ler os WOFF2. Instala `brotli` e volta a executar."
            ) from exc
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.metrics = self.font["hmtx"].metrics
        self.units_per_em = self.font["head"].unitsPerEm

    def width(self, value: str, size: float, tracking: float = 0.0) -> float:
        advances = sum(self.metrics[self._glyph_name(char)][0] for char in value)
        tracking_total = max(0, len(value) - 1) * tracking
        return (advances + tracking_total) * size / self.units_per_em

    def paths(
        self,
        value: str,
        *,
        x: float,
        baseline: float,
        size: float,
        split: int | None = None,
        first_fill: str,
        second_fill: str | None = None,
        tracking: float = 0.0,
        prefix: str,
    ) -> str:
        scale = size / self.units_per_em
        cursor = 0.0
        first: list[str] = []
        second: list[str] = []

        for index, char in enumerate(value):
            glyph_name = self._glyph_name(char)
            glyph = self.glyphs[glyph_name]
            pen = SVGPathPen(self.glyphs)
            transformed = TransformPen(
                pen,
                (scale, 0.0, 0.0, -scale, x + cursor * scale, baseline),
            )
            glyph.draw(transformed)
            commands = pen.getCommands()
            if commands:
                target = second if split is not None and index >= split else first
                target.append(f'    <path d="{commands}"/>')
            cursor += self.metrics[glyph_name][0] + tracking

        blocks: list[str] = []
        if first:
            part = "investi" if split is not None else prefix
            blocks.append(
                f'<g id="{prefix}-{part}" data-part="{part}" fill="{first_fill}">\n'
                + "\n".join(first)
                + "\n  </g>"
            )
        if second:
            part = "gator"
            blocks.append(
                f'<g id="{prefix}-{part}" data-part="{part}" '
                f'fill="{second_fill or first_fill}">\n'
                + "\n".join(second)
                + "\n  </g>"
            )
        return "\n  ".join(blocks)

    def _glyph_name(self, char: str) -> str:
        try:
            return self.cmap[ord(char)]
        except KeyError as exc:
            raise ValueError(f"O tipo de letra não contém {char!r}") from exc


def _tail(*, x: float, y: float, width: float, fill: str) -> str:
    """Coloca a geometria canónica pelo seu limite visível, não pela viewBox antiga."""
    scale = width / 210.0  # limites visíveis em x: 16..226
    tx = x - 16 * scale
    ty = y - 46 * scale
    return (
        f'<g data-part="mark" fill="{fill}" '
        f'transform="translate({_num(tx)} {_num(ty)}) scale({_num(scale)})">\n'
        f'    <path d="{TAIL_D}"/>\n'
        "  </g>"
    )


def _num(value: float) -> str:
    return f"{value:.5f}".rstrip("0").rstrip(".")


def _svg(
    *,
    width: int,
    height: int,
    label: str,
    body: str,
    piece: str,
    palette: Palette,
) -> str:
    title = html.escape(label)
    metadata = html.escape(
        "InvestiGator brand asset; word outlines derived from IBM Plex Sans/Mono under OFL 1.1. "
        "Source fonts and licence: web/assets/fonts/."
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'role="img" aria-label="{title}" data-piece="{piece}" '
        f'data-variant="{palette.suffix.removeprefix("-") or "light"}">\n'
        f"  <title>{title}</title>\n"
        f"  <metadata>{metadata}</metadata>\n"
        "  <!-- Letras convertidas em contornos: este ficheiro não depende "
        "de fontes instaladas. -->\n"
        f"  {body}\n"
        "</svg>\n"
    )


def _piece_documents(
    palette: Palette,
    sans: OutlineFont,
    mono: OutlineFont,
) -> dict[str, str]:
    wordmark_lockup = sans.paths(
        WORDMARK,
        x=112,
        baseline=79,
        size=70,
        split=len("Investi"),
        first_fill=palette.ink,
        second_fill=palette.accent,
        tracking=-24,
        prefix="wordmark",
    )
    lockup = (
        _tail(x=12, y=18, width=84, fill=palette.accent)
        + "\n  "
        + wordmark_lockup
    )

    tagline = mono.paths(
        SLOGAN.upper(),
        x=114,
        baseline=124,
        size=16,
        first_fill=palette.ink,
        tracking=55,
        prefix="tagline",
    )

    wordmark_name = sans.paths(
        WORDMARK,
        x=12,
        baseline=78,
        size=72,
        split=len("Investi"),
        first_fill=palette.ink,
        second_fill=palette.accent,
        tracking=-24,
        prefix="wordmark",
    )

    stacked_name_width = sans.width(WORDMARK, 70, tracking=-24)
    stacked_x = (430 - stacked_name_width) / 2
    stacked_name = sans.paths(
        WORDMARK,
        x=stacked_x,
        baseline=261,
        size=70,
        split=len("Investi"),
        first_fill=palette.ink,
        second_fill=palette.accent,
        tracking=-24,
        prefix="wordmark",
    )
    stacked = (
        _tail(x=140, y=28, width=150, fill=palette.accent)
        + "\n  "
        + stacked_name
    )

    return {
        "logo-lockup": _svg(
            width=620,
            height=104,
            label="InvestiGator",
            body=lockup,
            piece="lockup",
            palette=palette,
        ),
        "logo-lockup-tagline": _svg(
            width=620,
            height=142,
            label=f"InvestiGator — {SLOGAN}",
            body=lockup + "\n  " + tagline,
            piece="lockup-tagline",
            palette=palette,
        ),
        "logo-empilhado": _svg(
            width=430,
            height=290,
            label="InvestiGator",
            body=stacked,
            piece="stacked",
            palette=palette,
        ),
        "logo-marca": _svg(
            width=256,
            height=256,
            label="InvestiGator — rising market line drawn as an alligator tail",
            body=f'<path data-part="mark" d="{TAIL_D}" fill="{palette.accent}"/>',
            piece="mark",
            palette=palette,
        ),
        "logo-nome": _svg(
            width=430,
            height=100,
            label="InvestiGator",
            body=wordmark_name,
            piece="wordmark",
            palette=palette,
        ),
    }


def _write_svgs() -> dict[str, pathlib.Path]:
    sans = OutlineFont(FONTS / "IBMPlexSans-SemiBold.woff2")
    mono = OutlineFont(FONTS / "IBMPlexMono-SemiBold.woff2")
    outputs: dict[str, pathlib.Path] = {}

    for palette in PALETTES:
        for stem, source in _piece_documents(palette, sans, mono).items():
            path = ASSETS / f"{stem}{palette.suffix}.svg"
            path.write_text(source, encoding="utf-8", newline="\n")
            outputs[path.name] = path

    # Compatibilidade com consumidores antigos. O conteúdo continua a ter uma só fonte de verdade.
    for suffix in ("", "-dark", "-mono"):
        source = (ASSETS / f"logo-nome{suffix}.svg").read_text(encoding="utf-8")
        alias = ASSETS / f"logo-wordmark{suffix}.svg"
        alias.write_text(source, encoding="utf-8", newline="\n")
        outputs[alias.name] = alias

    manifest = {
        "name": WORDMARK,
        "slogan": SLOGAN,
        "source_mark": "app/assets/logo.svg",
        "source_fonts": [
            "web/assets/fonts/IBMPlexSans-SemiBold.woff2",
            "web/assets/fonts/IBMPlexMono-SemiBold.woff2",
        ],
        "pieces": list(PIECES),
        "variants": ["light", "dark", "mono"],
        "wordmark_split": {"ink": "Investi", "accent": "Gator"},
    }
    manifest_path = ASSETS / "brand" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    outputs[manifest_path.name] = manifest_path
    return outputs


def _render_svg(page, source: pathlib.Path, target: pathlib.Path, width: int) -> None:
    import xml.etree.ElementTree as ET

    root = ET.fromstring(source.read_text(encoding="utf-8"))
    _, _, view_width, view_height = map(float, root.attrib["viewBox"].split())
    height = max(1, round(width * view_height / view_width))
    page.set_viewport_size({"width": width, "height": height})
    svg = source.read_text(encoding="utf-8")
    page.set_content(
        "<style>html,body{margin:0;background:transparent;overflow:hidden}"
        f"svg{{display:block;width:{width}px;height:{height}px}}</style>{svg}"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    page.locator("svg").screenshot(path=str(target), omit_background=True)


def _render_pngs() -> list[pathlib.Path]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - mensagem de instalação para uso manual
        raise SystemExit(
            "Falta Playwright. Instala-o e executa `playwright install chromium`."
        ) from exc

    outputs: list[pathlib.Path] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(device_scale_factor=1)

        for stem in PIECES:
            target = PNG_DIR / f"{stem}-512.png"
            _render_svg(page, ASSETS / f"{stem}.svg", target, width=512)
            outputs.append(target)

        avatar = ASSETS / "telegram_avatar.png"
        _render_svg(page, ASSETS / "icon.svg", avatar, width=512)
        outputs.append(avatar)

        legacy_dir = ROOT / "tese" / "figures"
        legacy = (
            (ASSETS / "logo-marca.svg", legacy_dir / "logo_tail.png", 1024),
            (ASSETS / "icon.svg", legacy_dir / "logo_tail_icone.png", 512),
            (ASSETS / "logo-lockup.svg", legacy_dir / "logo_lockup.png", 1240),
        )
        for source, target, width in legacy:
            _render_svg(page, source, target, width=width)
            outputs.append(target)

        _render_comparison(page)
        outputs.append(COMPARISON)
        browser.close()
    return outputs


def _render_comparison(page) -> None:
    selected = (ASSETS / "logo-lockup.svg").read_text(encoding="utf-8")
    selected_dark = (ASSETS / "logo-lockup-dark.svg").read_text(encoding="utf-8")
    all_green = selected.replace('data-part="investi" fill="#14171A"',
                                 'data-part="investi" fill="#0A8F52"')
    all_green_dark = selected_dark.replace('data-part="investi" fill="#F3F7F5"',
                                           'data-part="investi" fill="#00E37A"')
    cards = (
        ("SELECTED — semantic split", "Investi / Gator", selected, selected_dark),
        ("REJECTED — one-colour name", "The wordplay disappears", all_green, all_green_dark),
    )
    rows = []
    for title, note, light_svg, dark_svg in cards:
        rows.append(
            '<section><div class="copy"><strong>'
            + html.escape(title)
            + "</strong><span>"
            + html.escape(note)
            + '</span></div><div class="sample light">'
            + light_svg
            + '</div><div class="sample dark">'
            + dark_svg
            + "</div></section>"
        )
    document = """<!doctype html><html><head><meta charset="utf-8"><style>
      *{box-sizing:border-box} body{margin:0;padding:42px;background:#EAF0ED;color:#14171A;
      font-family:Arial,sans-serif} h1{font-size:27px;margin:0 0 8px} p{margin:0 0 30px;
      color:#52615A} section{display:grid;grid-template-columns:235px 1fr 1fr;gap:18px;
      align-items:center;margin:16px 0}.copy{display:flex;flex-direction:column;gap:8px}
      .copy strong{font-size:14px;letter-spacing:.04em}.copy span{font-size:13px;color:#647169}
      .sample{height:142px;border-radius:15px;padding:28px;display:flex;align-items:center;
      box-shadow:0 8px 28px rgba(21,40,31,.08)}.sample svg{width:100%;height:auto;display:block}
      .light{background:#FFF}.dark{background:#0A0E12}.foot{font-size:13px;color:#52615A;
      margin-top:28px;padding-top:18px;border-top:1px solid #C7D2CC}
    </style></head><body><h1>InvestiGator wordmark decision</h1>
    <p>Same geometry, same typeface, two real surfaces. Only the colour split changes.</p>"""
    document += "".join(rows)
    document += (
        '<div class="foot">Decision: colour “Gator” as a complete unit. '
        f'Slogan: “{html.escape(SLOGAN)}”</div></body></html>'
    )
    page.set_viewport_size({"width": 1280, "height": 620})
    page.set_content(document)
    COMPARISON.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(COMPARISON), full_page=True)


def main() -> int:
    svgs = _write_svgs()
    pngs = _render_pngs()
    print(f"SVG/manifesto: {len(svgs)} ficheiros")
    print(f"PNG/comparação: {len(pngs)} ficheiros")
    print(f"Lema: {SLOGAN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
