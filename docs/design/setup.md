# setup.md — Ambiente e build (multi-dispositivo)

Objetivo: reconstruir o ambiente com um comando, em qualquer dispositivo.

> Para **correr** o sistema (gatilhos, KB, avaliações, testes, compilar a tese), ver
> [`how_to_run.md`](how_to_run.md). Este ficheiro trata só do **ambiente**.

## Python
- **Versão fixada: 3.12** (ver `.python-version`). Decisão D-003 (`progress/DECISIONS.md`).
- **Ambiente virtual:** `.venv/` (gitignored). Nunca instalar no Python do sistema.
- **Criar/instalar (stack leve):** `bash scripts/setup_env.sh` — cria o venv com Python 3.12, instala a
  stack **leve** (`requirements.txt`) e verifica imports-chave. Chega para a demo, os testes (`verify.sh`),
  as avaliações sobre dados guardados e as figuras.
- **Stack pesada de ML (opcional):** `bash scripts/setup_env.sh --ml` — acrescenta `requirements-ml.txt`
  (torch CPU + sentence-transformers + transformers + huggingface-hub + scikit-learn). Só é precisa para a
  recuperação semântica real (`SbertEmbedder`) e os testes `@sbert`.
- **⚠️ torch CPU:** o `torch==2.12.1+cpu` **não está no PyPI** — vem do índice dedicado da PyTorch. O
  `requirements-ml.txt` já inclui a linha `--extra-index-url https://download.pytorch.org/whl/cpu`, por isso
  o `--ml` resolve-o sozinho. (Instalação manual: `pip install -r requirements-ml.txt`.)
- **Dependências:** `requirements.txt` (leve) + `requirements-ml.txt` (pesada), versões fixadas. Lockfile
  completo do ambiente com ML em `requirements.lock.txt` (`pip freeze`).

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
