# analise_template_latex.md — Análise do template LaTeX ISEP

> **Fase A.** Análise de `Modelo Dissertacao MEIA_latex v2/`. Todo o trabalho LaTeX respeita este template sem exceção.

Notas iniciais (Sessão 0):
- Classe nativa `meia-style.cls`; `main.tex` com bloco THESIS INFORMATION (título, autor, nº, orientador, etc.).
- Bibliografia: `biblatex` estilo `authoryear-comp`, backend `biber`; ficheiro `mainbibliography.bib`.
- Glossário/acrónimos via `makenoidxglossaries` (compatível Overleaf).
- Estrutura: `frontmatter/`, `ch1/ ch2/ ch3/` (assets por capítulo), `appendices/`; build via `Makefile`/`latexmk` para `build/`.
- Língua já em `english`; 11pt; mín. 60 / máx. 120 páginas; impressão frente-e-verso.

A completar na Fase A: estrutura de ficheiros completa, pacotes e versões, regras de formatação/estilos/convenções,
o que é predefinido vs. o que tem de ser preenchido/adaptado.
