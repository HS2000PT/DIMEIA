"""Build the mascot-free web identity. Run: python -m scripts.build_web_brand.

Reuses the existing outline exporter; does not regenerate historical thesis assets.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from PIL import Image, ImageDraw, ImageFont

from scripts.build_brand_assets import OutlineFont

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web" / "assets"
EXPORT = ROOT / "docs" / "design" / "brand-v9"
GREEN = "#0a7f4f"


def svg(body: str, width: float, height: float, label: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}" '
            f'role="img" aria-label="{label}">\n{body}\n</svg>\n')


def main() -> None:
    EXPORT.mkdir(parents=True, exist_ok=True)
    font = OutlineFont(WEB / "fonts" / "IBMPlexSans-SemiBold.woff2")
    width = round(font.width("InvestiGator", 40, tracking=-15) + 4, 2)
    paths = font.paths("InvestiGator", x=2, baseline=36, size=40,
                       first_fill="currentColor", tracking=-15, prefix="wordmark")
    adaptive = ('<style>:root{color:#0f1216}'
                '@media(prefers-color-scheme:dark){:root{color:#eef0f2}}</style>')
    (WEB / "wordmark.svg").write_text(svg(adaptive + paths, width, 46, "InvestiGator"),
                                      encoding="utf-8")
    for name, colour in (("light", "#0f1216"), ("dark", "#eef0f2")):
        (EXPORT / f"wordmark-{name}.svg").write_text(
            svg(paths.replace("currentColor", colour), width, 46, "InvestiGator"),
            encoding="utf-8")

    # Use exactly the wordmark's I, centred by its visible outline, not its advance.
    pen = BoundsPen(font.glyphs)
    font.glyphs[font.cmap[ord("I")]].draw(pen)
    x0, y0, x1, y1 = pen.bounds
    scale = 36 / (y1 - y0)
    mark = font.paths("I", x=32 - (x0 + x1) * scale / 2,
                      baseline=32 + (y0 + y1) * scale / 2,
                      size=font.units_per_em * scale, first_fill="#ffffff", prefix="monogram")
    icon = svg(f'<rect width="64" height="64" rx="12" fill="{GREEN}"/>{mark}',
               64, 64, "InvestiGator")
    (WEB / "icon.svg").write_text(icon, encoding="utf-8")
    (EXPORT / "monogram.svg").write_text(icon, encoding="utf-8")

    # Raster export from the same font, with safe space for Telegram's circular crop.
    stream = BytesIO()
    font.font.flavor = None
    font.font.save(stream)
    stream.seek(0)
    raster_font = ImageFont.truetype(stream, round(font.units_per_em * scale * 32))
    canvas = Image.new("RGB", (2048, 2048), GREEN)
    draw = ImageDraw.Draw(canvas)
    left, top, right, bottom = draw.textbbox((0, 0), "I", font=raster_font)
    draw.text((1024 - (left + right) / 2, 1024 - (top + bottom) / 2), "I",
              font=raster_font, fill="#ffffff")
    canvas.resize((512, 512), Image.Resampling.LANCZOS).save(EXPORT / "telegram-avatar.png")
    print(f"Brand assets written to {WEB} and {EXPORT}")


if __name__ == "__main__":
    main()
