# analise_template_latex.md — Análise do template LaTeX ISEP

> **Fase A.** Análise de `Modelo Dissertacao MEIA_latex v2/` (input local, gitignored até à Fase D).
> **Regra:** todo o trabalho LaTeX respeita este template **sem exceção** (decisão D-004). Integração em
> `thesis/` na Fase D, mantendo a classe e as convenções nativas.

## Estrutura de ficheiros
```
Modelo Dissertacao MEIA_latex v2/
├── main.tex                  # Documento principal: opções, pacotes, THESIS INFORMATION, \input dos capítulos
├── meia-style.cls            # Classe que define formato/layout (NÃO editar normalmente; licença LPPL v1.3c)
├── mainbibliography.bib      # Bibliografia (BibTeX consumido pelo biber) — 6 entradas de exemplo
├── Makefile                  # Build via latexmk -> build/ ; alvos: all, clean, clean-all
├── README.md                 # Lista de pacotes e instruções
├── frontmatter/
│   ├── frontmatter.tex       # Capa, declaração de integridade, dedicatória, resumo/abstract, agradecimentos,
│   │                         #   TOC, listas (figuras/tabelas/algoritmos/código), abreviaturas, símbolos, acrónimos
│   ├── glossary.tex          # Definição de acrónimos: \newacronym{KEY}{SHORT}{LONG}
│   └── assets/               # Logos: ISEP, MEIA, DEI
├── ch1/chapter1.tex          # Cap. exemplo: estrutura/recomendações (com tabela de checklist)
├── ch2/chapter2.tex          # Cap. exemplo: guia de uso (figuras, tabelas, citações, comandos) + ch2/assets/
├── ch3/chapter3.tex          # Cap. exemplo: algoritmos, código-fonte, PGF, acrónimos + ch3/assets/ (euclid.c/.java/.tex)
├── appendices/appendixA.tex  # Apêndice exemplo (\chapter dentro de \appendix)
└── build/                    # Saída de compilação (gitignored)
```

## Classe e opções (em `main.tex`)
- `\documentclass[...]{meia-style}` baseada em `book`. Opções **ativas**: `11pt`, `english`, `singlespacing`,
  `parskip`, `nohyperreflinkcolor`, `headsepline`. **Frente-e-verso por defeito** (`oneside` comentado, para draft).
- Opções da classe disponíveis: `nohyperref`, `nohyperreflinkcolor`, `nolistspacing`, `liststotoc`, `toctotoc`,
  `parskip`, `headsepline`. (Definidas no `.cls`.)
- **Língua:** já em `english` → coerente com a nossa decisão (tese em EN-GB; mudar de língua exige `make clean`).
- **Formato (regras ISEP):** 11pt; espaçamento simples; **mín. 60 / máx. 120 páginas** (sem anexos); cabeçalho
  com nº de página (exterior) + nome do capítulo (interior). TOC até 3 níveis (chapter/section/subsection).

## Pacotes (do README + main.tex)
`babel`, `scrbase`, `scrhack`, `setspace`, `longtable`, `siunitx`, `graphicx`, `xcolor`, `booktabs`, `inputenc`,
`fontenc`, `csquotes`, `cmbright` (fonte por defeito: CM Bright, sans-serif), `algorithm`, `algpseudocode`,
`listings`, `glossaries`, `caption`, `biblatex`. Em `main.tex` também: `tikz`, `pgfplots` (gráficos vetoriais),
`makecell`.

## Bibliografia e citações
- `\usepackage[style=authoryear-comp,backend=biber]{biblatex}` (estilo tipo Harvard) + `\addbibresource{mainbibliography.bib}`.
- Comandos: `\parencite{}` (entre parênteses), `\textcite{}` (no fluxo do texto), `\autocite{}` (alterna conforme contexto).
- Convenção: citação **antes** da pontuação; bibliografia ordenada alfabeticamente pelo 1.º autor.
- Formato `.bib`: BibTeX padrão (ex.: `@article{chave, author={...}, journal={...}, title={...}, volume, number, pages, year}`).
  Campos extra do BibDesk (`date-added`/`date-modified`) são inofensivos.
- **A nossa `thesis/references.bib`** segue este formato; nenhuma entrada sem verificação (§6.4 / `citation_log.md`).

## Figuras, tabelas, algoritmos, código (convenções a seguir)
- **Figuras:** `\begin{figure}\centering\includegraphics[width=\textwidth,keepaspectratio]{chN/assets/nome}\caption[título curto p/ Lista]{legenda longa \autocite{...}}\label{fig:nome}\end{figure}`.
  Assets em `chN/assets/`. Formatos: pdf/png/jpg (**preferir vetorial PDF** — §6.7). `\decoRule` opcional.
  **Regra ISEP:** todo o elemento gráfico tem texto descritivo associado e é referenciado no corpo (`\ref{}`).
- **Tabelas:** `booktabs` (`\toprule \midrule \bottomrule`), cabeçalhos com `\tabhead{}`, `\caption{}` + `\label{tab:}`.
- **Algoritmos:** ambiente `algorithm` + `algpseudocode` (`\begin{algorithmic}`), com `\caption`/`\label{alg:}`.
- **Código-fonte:** pacote `listings` (assets de código em `chN/assets/`, ex.: `euclid.c`, `euclid.java`).
- **Comandos utilitários da classe:** `\keyword{}`, `\tabhead{}`, `\code{}`, `\file{}`, `\option{}`.

## Glossário / acrónimos
- `\makenoidxglossaries` (compatível Overleaf, **não** requer ferramenta externa `makeglossaries`).
- Acrónimos definidos em `frontmatter/glossary.tex`: `\newacronym{AI}{AI}{Artificial Intelligence}`.
- No texto: `\acrlong{AI}`, `\acrshort{AI}`, `\gls{}`. Lista impressa via `\printnoidxglossary[...]` no frontmatter.

## Build
- **Makefile:** `make` → `latexmk -r latexmk.rc -outdir=build -auxdir=build -pdf ...`; `make clean`; `make clean-all`.
- Sequência manual: `pdflatex` → `biber` → (`makeglossaries`) → `pdflatex` ×2.
- ⚠️ **Achado importante:** o `Makefile` invoca `latexmk -r latexmk.rc`, mas **`latexmk.rc` NÃO existe** no template.
  Com `\makenoidxglossaries` o `makeglossaries` externo é dispensável, mas `make` tal como está pode falhar por
  falta do ficheiro. **Na Fase D:** ou criar um `latexmk.rc` mínimo, ou invocar `latexmk` sem `-r`. O **CI**
  (`xu-cheng/latex-action`) usa a sua própria invocação de `latexmk`+`biber`, por isso não depende deste ficheiro.

## Predefinido vs. a preencher/adaptar
| Predefinido (manter) | A preencher / adaptar |
|---|---|
| Classe `meia-style.cls`, layout, fontes, margens, cabeçalhos | Bloco **THESIS INFORMATION** em `main.tex` (título, autor, nº 1180934, orientador, coorientador, júri, keywords, universidade/departamento) |
| Frontmatter: declaração de integridade (já inclui menção a uso de IA), TOC/listas | Texto do Resumo (PT) + Abstract (EN); dedicatória/agradecimentos (opcionais); acrónimos em `glossary.tex` |
| Convenções de figuras/tabelas/algoritmos/código/citações | Os 7 capítulos (substituir ch1–ch3 de exemplo); `references.bib` real (verificado) |
| Estilo de citação `authoryear-comp` + biber | Escolher manter `authoryear-comp` (recomendado) — confirmar na Fase D |

## Implicações para a Fase D
1. Copiar o template para `thesis/`, **mantendo** `meia-style.cls` e a organização `chN/` + `frontmatter/` + `appendices/`.
2. Mapear o plano de 7 capítulos (§9) na estrutura `chN/` (decisão de mapeamento em `DECISIONS.md`).
3. Preencher THESIS INFORMATION (incl. nº de aluno 1180934, orientador Prof. Luís Gomes, coorientador Rafael Silva).
4. Resolver o `latexmk.rc` (criar mínimo ou ajustar invocação) para `make` local; CI já tratado.
5. Garantir EN-GB consistente; ativar/limpar listas conforme o que o documento realmente tiver (figuras/tabelas/algoritmos/código).
6. `thesis/references.bib` arranca vazio/estrutural; entradas só após verificação (§6.4).
