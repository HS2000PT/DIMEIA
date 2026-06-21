#!/bin/bash
# Compila a dissertação e coloca o PDF em thesis/main.pdf (versionado, para ver no repositório).
# Requer LaTeX local (MiKTeX/TeX Live com latexmk + biber). O CI continua a ser fonte de verdade.
set -euo pipefail
cd "$(dirname "$0")/../thesis"
latexmk -pdf -outdir=build -interaction=nonstopmode main.tex
cp build/main.pdf main.pdf
echo "✅ PDF atualizado: thesis/main.pdf ($(wc -c < main.pdf) bytes)"
