"""Encode the approved logo for the web without redrawing it.

The SVG files frame the original image; they are not vector tracings. The source
has a white background, retained in both light and dark themes.
Run: python scripts/prepare_web_logo.py
"""

from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    source = ROOT / "docs/design/brand-final/investigator-logo.png"
    with Image.open(source) as logo:
        width, height = logo.size
        encoded = BytesIO()
        # Format conversion only: preserve composition and pixel dimensions.
        logo.save(encoded, format="WEBP", quality=92, method=6)
    data = base64.b64encode(encoded.getvalue()).decode("ascii")
    for name, viewport in (("logo.svg", "48 245 1158 780"),
                           ("icon.svg", "100 30 1080 1080")):
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewport}" '
               'role="img" aria-label="InvestiGator">'
               '<title>InvestiGator</title>'
               '<rect width="1254" height="1254" fill="white"/>'
               f'<image width="{width}" height="{height}" '
               f'href="data:image/webp;base64,{data}"/></svg>\n')
        # The favicon frames only the head; no second brand or tiny wordmark.
        if name == "icon.svg":
            svg = svg.replace(f'<image width="{width}" height="{height}" ',
                              f'<image width="{width}" height="{height}" '
                              'clip-path="url(#head)" ')
            svg = svg.replace('<title>', '<defs><clipPath id="head">'
                              '<rect x="100" y="245" width="1080" height="575"/>'
                              '</clipPath></defs><title>')
        target = ROOT / "web/assets" / name
        target.write_text(svg, encoding="utf-8")
        print(f"{name}: {target.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
