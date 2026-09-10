"""Extrai texto dos PDFs de literatura para .txt ao lado do PDF.

Uso: python scripts\\_extrair_pdf.py [padrao]
Nao inventa nada: escreve o texto tal como sai do extractor, com marcas de pagina.
"""
import glob
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, "data", "literature")


def extractor():
    try:
        import fitz  # PyMuPDF

        def ler(caminho):
            doc = fitz.open(caminho)
            paginas = [pag.get_text("text") for pag in doc]
            doc.close()
            return paginas

        return "pymupdf", ler
    except ImportError:
        pass
    try:
        import pdfplumber

        def ler(caminho):
            with pdfplumber.open(caminho) as doc:
                return [pag.extract_text() or "" for pag in doc.pages]

        return "pdfplumber", ler
    except ImportError:
        pass
    try:
        from pypdf import PdfReader

        def ler(caminho):
            leitor = PdfReader(caminho)
            return [pag.extract_text() or "" for pag in leitor.pages]

        return "pypdf", ler
    except ImportError:
        pass
    return None, None


def main():
    nome, ler = extractor()
    if ler is None:
        print("SEM_EXTRACTOR: instalar pymupdf ou pdfplumber ou pypdf")
        raise SystemExit(1)
    print("extractor:", nome)
    padrao = sys.argv[1] if len(sys.argv) > 1 else "*.pdf"
    for caminho in sorted(glob.glob(os.path.join(PASTA, padrao))):
        destino = os.path.splitext(caminho)[0] + ".txt"
        try:
            paginas = ler(caminho)
        except Exception as erro:  # noqa: BLE001
            print("FALHOU", os.path.basename(caminho), erro)
            continue
        with open(destino, "w", encoding="utf-8") as fh:
            for i, texto in enumerate(paginas, start=1):
                fh.write(f"\n===== PAGINA {i} =====\n")
                fh.write(texto)
        total = sum(len(p) for p in paginas)
        print(
            f"OK {os.path.basename(caminho)} -> {os.path.basename(destino)} "
            f"| {len(paginas)} paginas | {total} chars"
        )


if __name__ == "__main__":
    main()
