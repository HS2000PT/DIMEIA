# SESSIONS — Registo de sessões (continuidade)

Registo curto de cada sessão para garantir continuidade entre dispositivos.
A entrada mais recente fica no topo.

---

## Sessão 5 — 2026-06-21 — Escrita: Capítulo 1 (Introduction)
**Objetivo:** redigir a Introduction, fundacional e apoiada no Cap. 2.

**Feito:**
- **Cap. 1 redigido** (rascunho EN-GB): motivação (com stats do Cap.2 citadas), enunciado do problema (explicação,
  não previsão), **3 research questions (RQ1 deteção transparente; RQ2 correlação/precedentes sem lookahead vs.
  baselines; RQ3 explicações fiéis e úteis)**, contribuições (enquadramento de Engenharia de IA: integrar/aplicar/
  avaliar; metodologia documentada de correlação notícia–impacto; pipeline XAI-first), e estrutura do documento.
- Referências cruzadas (`\ref` aos capítulos) e citações verificadas (Gallup, SIFMA, CCAF, Arrieta, Adadi).
- Compila: **43 páginas, 0 erros, 11 referências**.

**Próxima ação:** Cap. 3 (Literature Review) — tabelas comparativas + ampliar citações verificadas.

---

## Sessão 4 — 2026-06-21 — Escrita: Capítulo 2 (Contextualization)
**Objetivo:** redigir o capítulo de contextualização com dados US 2025–2026 reais e verificados.

**Feito:**
- Investigação web + **verificação em fonte primária** de 3 fontes: SIFMA 2025 Fact Book (cap. ações US =
  $62,2T, 49,1% do global, 5,3× a China; valor extraído do PDF), Gallup 2025 (62% dos americanos detêm ações),
  CCAF 2026 (81% adoção de IA, 40% avançada, 71% GenAI). Registadas em `citation_log.md` + `references.bib`.
- **Cap. 2 redigido** (rascunho EN-GB): mercado US (NYSE/NASDAQ), panorama do retalho, IA em finanças +
  necessidade de XAI, e o problema de sobrecarga de informação. Cada afirmação citada.
- **1.ª figura reprodutível** (§6.7): `scripts/figures/fig_us_market_cap.py` (matplotlib) gera
  `thesis/figures/us_equity_market_cap.pdf` (capitalização US 2015–2024). Pipeline de figuras estabelecido.
- Adicionado acrónimo SIFMA; termos no `glossary.md`. Compila: **43 páginas, 0 erros, 11 referências**.

**Próxima ação:** Cap. 1 (Introduction) e Cap. 3 (Literature Review). Rever Cap. 2 (fonte da quota de retalho).

---

## Sessão 3 — 2026-06-21 — Fase D (Setup LaTeX)
**Objetivo:** integrar o template ISEP em `thesis/` e garantir compilação.

**Feito:**
- Template ISEP copiado para `thesis/` (classe `meia-style.cls`, `frontmatter/`, `appendices/`, assets) e criados
  `ch1..ch7/`. `main.tex` adaptado: título **T1**, autor, nº 1180934, orientador Luís Gomes, coorientador Rafael
  Silva, keywords; `\addbibresource{references.bib}`; `authoryear-comp` + biber; `makenoidxglossaries`.
- **7 capítulos** com estrutura de secções (Introduction · Contextualization · Literature Review · Methodology ·
  Implementation · Evaluation · Conclusion).
- `references.bib` com as **8 referências verificadas**; `latexmk.rc` criado (resolve o achado da Fase A);
  acrónimos próprios em `glossary.tex`; abstract (EN) + resumo (PT) em rascunho (exemplos do template removidos).
- **Compila localmente: 41 páginas, 0 erros**, biber OK, 8 refs no `.bbl` (só aviso cosmético de fonte).
- Correção: removido `\thesissubtitle{}` vazio (causava "There's no line here to end"). `\nocite{*}` temporário.

**Próxima ação:** gate da Fase D; confirmar compilação no CI após push; depois escrita (Sessão 4+).

---

## Sessão 2 — 2026-06-21 — Fase C (Planeamento e decisões técnicas)
**Objetivo:** planear o sistema e fechar decisões técnicas antes da Fase D.

**Feito:**
- **Título:** escolhido **T1** pelo aluno — *Explainable Financial Alerts for Retail Investors: Integrating
  Statistical Anomaly Detection and News–Market Impact Correlation* (D-008).
- **Arquitetura:** `docs/arquitectura_sistema.md` — diagrama de componentes, 2 camadas (histórica FNSPID vs.
  live), fluxos dos 2 gatilhos, thin slice, garantias XAI/anti-lookahead; **confirmada pelo aluno**.
- **Metodologias por componente** com **8 citações verificadas** (Crossref/arXiv, 2026-06-21) em
  `citation_log.md` + secção 9 da arquitetura: Chandola 2009, Brown & Warner 1985, Reimers & Gurevych 2019,
  Araci 2019, Lundberg & Lee 2017, Arrieta 2020, Adadi & Berrada 2018, Dong 2024. (MacKinlay 1997 rejeitada —
  sem DOI resolúvel.)
- **APIs gratuitas:** `docs/free_apis.md` (verificado 2026-06-21): yfinance+Finnhub (preços), Finnhub news+RSS
  (notícias), FNSPID (histórico), Telegram (alertas); Alpha Vantage só ocasional (25/dia).
- **Avaliação:** `docs/evaluation_design.md` detalhado (métricas, baselines, ablções, rubrica XAI).
- **Plano:** `progress/PLANO_SESSOES.md` detalhado (~30 sessões + buffer, marcos M1–M5).
- **Aprendizagem:** `learning.md` + `glossary.md` com os conceitos (z-score, embeddings, cosseno, event-study,
  XAI, lookahead, FinBERT, SHAP), cada um com nota de defesa.

**Próxima ação:** pausar no gate da Fase C; depois Fase D (integrar template ISEP em `thesis/`).

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
