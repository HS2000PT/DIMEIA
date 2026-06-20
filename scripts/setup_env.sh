#!/bin/bash
# Cria o ambiente virtual (Python 3.12), instala dependências fixadas e verifica imports-chave.
# Ver docs/setup.md e decisões D-003 / D-005 em progress/DECISIONS.md.
set -euo pipefail

# 1) Localiza um interpretador Python 3.12.
PYTHON=""
for cand in "python3.12" "py -3.12" "python3" "python"; do
  if $cand --version >/dev/null 2>&1; then
    ver=$($cand -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null || echo "")
    if [ "$ver" = "3.12" ]; then PYTHON="$cand"; break; fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "❌ Python 3.12 não encontrado. Instala o Python 3.12 e corre de novo."
  echo "   (Ver docs/setup.md e CLAUDE.md → Questões em Aberto.)"
  exit 1
fi
echo "ℹ️ A usar interpretador: $PYTHON"

# 2) (Re)cria o venv para garantir Python 3.12 + dependências fixadas.
if [ -d ".venv" ]; then
  echo "ℹ️ .venv já existe — a recriar."
  rm -rf .venv
fi
$PYTHON -m venv .venv

# 3) Ativa (Windows: Scripts; Unix: bin).
if [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
else
  source .venv/bin/activate
fi

# 4) Instala dependências fixadas.
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5) Verificação mínima de imports (cresce com os componentes — D-005).
python -c "import pandas, dotenv; print('Ambiente OK (imports mínimos verificados).')"
echo "✅ Ambiente preparado (Python 3.12)."
