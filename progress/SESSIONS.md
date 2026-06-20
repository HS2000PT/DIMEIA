# SESSIONS — Registo de sessões (continuidade)

Registo curto de cada sessão para garantir continuidade entre dispositivos.
A entrada mais recente fica no topo.

---

## Sessão 1 — 2026-06-20 — Fase A (Análise de ficheiros de referência)
**Objetivo:** analisar a dissertação de referência e o template ISEP (benchmark + regras LaTeX).

**Feito:**
- `docs/analise_referencia.md` — *Distributed Intelligent Management of Citizen Communities* (Rafael Silva, EN,
  feito em Word): **109 páginas**, 6 capítulos (Intro / State of the art / Methods & Materials / Implementation /
  Case Studies / Conclusion), front matter i–xv, **~170 referências** (autor-ano), **34 figuras + 6 tabelas**
  (concentradas em implementação e casos de estudo). Estilo claro/direto, estatísticas concretas, citações inline.
  Definidos alvos de benchmark para a nossa tese (dimensão, nº refs, ≥30 figuras, tabelas comparativas).
- `docs/analise_template_latex.md` — classe `meia-style.cls` (book, 11pt, EN, frente-e-verso), pacotes,
  `biblatex authoryear-comp` + `biber`, convenções de figuras/tabelas/algoritmos/código, glossário
  `makenoidxglossaries`, build via Makefile/latexmk. **Achado:** `Makefile` refere `latexmk.rc` inexistente
  (tratar na Fase D; CI não depende dele).

- **Benchmark alargado** (secção comparativa em `docs/analise_referencia.md`): analisadas as outras 3
  dissertações — Bruno Ribeiro (139pp, 40 fig, 13 tab, ~210 refs), Helder Pereira (133pp, 41 fig, 14 tab,
  ~200 refs, citação numérica), Joana Figueiredo (104pp, 20 fig, 5 tab, ~60 refs). Todas EN. Estrutura comum
  (Intro→Estado da arte/Literatura→…→Conclusão) valida o plano de 7 capítulos. Alvos refinados: ~110–120 pp.,
  ~30–40 figuras, ~8–14 tabelas, ~150–200 refs, `authoryear-comp`.

**Notas técnicas:** instalado `pypdf` no venv (gitignored) para extrair estrutura dos PDFs.

**Próxima ação:** pausar no gate da Fase A; depois Fase C (planeamento). Fase B já coberta pela Fase 0.

---

## Sessão 0 — 2026-06-20 — Setup & Authorization (Fase 0)
**Objetivo:** preparar o repositório 100% scaffolded e seguro antes de qualquer trabalho real.

**Feito:**
- Verificado o ambiente: Git 2.54, Node 24, Python 3.14.6 (sistema), MiKTeX (pdflatex, latexmk 4.88, biber 2.21);
  remote HTTPS `github.com/HS2000PT/DIMEIA.git`; Git Credential Manager configurado; repo sem commits.
- Decisões bloqueadas com o aluno: **EN-GB**, **Python 3.12**, **docs de aprendizagem em PT-PT**.
- Criados: permissões (`.claude/settings.json`), ignore/segredos (`.gitignore`, `.gitattributes`, `.env.example`),
  esqueleto §9, `CLAUDE.md`, `README.md`, ficheiros `progress/` e `docs/`, scripts de automação, `requirements.txt`,
  `.python-version`, workflow de CI, e teste placeholder.

**Decisões:** ver `DECISIONS.md` (EN-GB; Python 3.12; docs PT-PT; layout LaTeX nativo do template ISEP;
dependências ML faseadas; PDFs de referência gitignored).

**A precisar do aluno:** instalar Python 3.12; aprovar auth do GitHub no primeiro push; (mais tarde) bot Telegram,
chaves de APIs, política ISEP de uso de IA.

**Próxima ação:** pausar no gate da Fase 0 e confirmar com o aluno antes de iniciar a Fase A (análise de
referência + template).
