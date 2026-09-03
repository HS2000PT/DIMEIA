"""Build a separate, same-width print proof; never modify the thesis."""
from copy import deepcopy
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/pdf/comparacao-ciclo-modelo.pdf"
WIDTH = 390.0


def main():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle("Ciclo do modelo - comparação a largura igual")
    c.setFont("Helvetica-Bold", 16)
    c.drawString(48, 795, "Ciclo do modelo: prova de comparação")
    c.setFont("Helvetica", 10)
    c.drawString(48, 774, "Imprimir a 100%. Ambas as figuras ocupam 137,6 mm de largura.")
    c.drawString(48, 744, "A. Figura atual da tese (página física 70)")
    c.drawString(48, 562, "B. Piloto Figma - não incorporado na tese")
    c.drawString(48, 280, "Versão revista: rótulos e fases com 8,03 pt à largura final.")
    c.drawString(48, 264, "A leitura recupera a escala da atual; o piloto ocupa mais altura.")
    c.drawString(48, 240, "Proposta para aprovação. A figura da tese não foi substituída.")
    c.save()
    page = PdfReader(buffer).pages[0]
    thesis = deepcopy(PdfReader(ROOT / "tese-v2/main.pdf").pages[69])
    h = float(thesis.mediabox.height)
    thesis.cropbox = RectangleObject([90, h - 216, 480, h - 96])
    page.merge_transformed_page(thesis, Transformation().translate(-90 + 48, -(h - 216) + 600))
    pilot = PdfReader(ROOT / "output/pdf/piloto-ciclo-modelo.pdf").pages[0]
    scale = WIDTH / float(pilot.mediabox.width)
    page.merge_transformed_page(pilot, Transformation().scale(scale).translate(48, 300))
    writer = PdfWriter()
    writer.add_page(page)
    writer.add_metadata({"/Title": "Comparacao do ciclo de vida do modelo"})
    with OUT.open("wb") as stream:
        writer.write(stream)
    print(OUT)


if __name__ == "__main__":
    main()
