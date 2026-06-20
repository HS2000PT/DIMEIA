# SESSIONS — Registo de sessões (continuidade)

Registo curto de cada sessão para garantir continuidade entre dispositivos.
A entrada mais recente fica no topo.

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
