@echo off
REM Compila a tese -> thesis\main.pdf (precisa de LaTeX/MiKTeX com latexmk instalado).
cd /d "%~dp0..\thesis"
latexmk -pdf -interaction=nonstopmode main.tex
pause
