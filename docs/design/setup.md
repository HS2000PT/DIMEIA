# setup.md — Ambiente e build (multi-dispositivo)

Objetivo: reconstruir o ambiente com um comando, em qualquer dispositivo.

> Para **correr** o sistema (gatilhos, KB, avaliações, testes, compilar a tese), ver
> [`how_to_run.md`](how_to_run.md). Este ficheiro trata só do **ambiente**.

## Python
- **Versão fixada: 3.12** (ver `.python-version`). Decisão D-003 (`progress/DECISIONS.md`).
- **Ambiente virtual:** `.venv/` (gitignored). Nunca instalar no Python do sistema.
- **Criar/instalar:** `bash scripts/setup_env.sh` — cria o venv com Python 3.12, instala dependências fixadas e verifica imports-chave.
- **Dependências:** `requirements.txt` (versões fixadas). Lockfile `requirements.lock.txt` gerado com `pip freeze` assim que o venv 3.12 existir.
- **Estratégia faseada (D-005):** a stack pesada (`torch`, `transformers`, `sentence-transformers`, `datasets`, `huggingface-hub`, `yfinance`) é adicionada nas fases que a usam; o `import check` do `setup_env.sh` cresce em conformidade.

> **Pendente (humano-only):** instalar Python 3.12. Até lá, `verify.sh` corre no Python disponível (3.14).

## LaTeX
- **Fonte de verdade do PDF: GitHub Action** (`.github/workflows/compile-thesis.yml`) — compila em cada push (após a Fase D) e publica o PDF como artefacto.
- **Instalação local (opcional):** já disponível neste dispositivo — MiKTeX (pdflatex), `latexmk` 4.88, `biber` 2.21. Permite compilar localmente além do CI.
- **Template:** ISEP MEIA (`meia-style.cls`, biblatex `authoryear-comp` + `biber`, glossaries via `makenoidxglossaries`). Build via `Makefile`/`latexmk` para `build/`.

## Reprodutibilidade
- Seeds aleatórias fixas onde houver aleatoriedade (registadas no código e na metodologia).
- Dados grandes nunca versionados; recriados por `scripts/download_data.py`.

## Git / continuidade
- Início de sessão: `bash scripts/start_session.sh` (pull-rebase + estado).
- Fim de sessão: `bash scripts/end_session.sh "descrição"` (verify → commit → pull-rebase → push, sem force-push).
