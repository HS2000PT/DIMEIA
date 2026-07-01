#!/bin/bash
# Cria o ambiente virtual (Python 3.12), instala dependências fixadas e verifica imports-chave.
# Ver docs/design/setup.md e decisões D-003 / D-005 em progress/DECISIONS.md.
#
# Uso:
#   bash scripts/setup_env.sh          # stack LEVE (demo + testes + avaliações + figuras)
#   bash scripts/setup_env.sh --ml     # + stack PESADA (torch CPU + SBERT) para a recuperação real
set -euo pipefail

# 0) Argumentos.
WITH_ML=0
for arg in "$@"; do
  case "$arg" in
    --ml) WITH_ML=1 ;;
    *) echo "❌ Argumento desconhecido: $arg (usa --ml para a stack pesada de SBERT/torch)."; exit 2 ;;
  esac
done

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
  echo "   (Ver docs/design/setup.md e CLAUDE.md → Questões em Aberto.)"
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

# 4) Instala dependências fixadas (stack leve por defeito).
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4b) Stack pesada opcional (torch CPU + SBERT). O requirements-ml.txt já traz o --extra-index-url
#     da PyTorch, por isso o torch "+cpu" resolve corretamente (não está no PyPI).
if [ "$WITH_ML" -eq 1 ]; then
  echo "ℹ️ A instalar a stack pesada de ML (torch CPU + SBERT) — pode demorar alguns minutos."
  pip install -r requirements-ml.txt
fi

# 5) Verificação mínima de imports.
python -c "import pandas, dotenv; print('Ambiente OK (imports base verificados).')"
if [ "$WITH_ML" -eq 1 ]; then
  python -c "import torch, sentence_transformers; print('Stack ML OK (torch + sentence-transformers).')"
fi
echo "✅ Ambiente preparado (Python 3.12$([ "$WITH_ML" -eq 1 ] && echo ' + ML' || echo ' — leve'))."
