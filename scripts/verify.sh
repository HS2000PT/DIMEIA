#!/bin/bash
# Verificação única: testes + lint + (nota de) build LaTeX. Resumo pass/fail.
set -uo pipefail

# Ativa o venv se existir (Windows: Scripts; Unix: bin); caso contrário usa o Python disponível.
if [ -f ".venv/Scripts/activate" ]; then
  source .venv/Scripts/activate
elif [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

PY="python"
command -v python >/dev/null 2>&1 || PY="python3"

echo "—— Testes ——"
$PY -m pytest -q || { echo "❌ Testes falharam"; exit 1; }

echo "—— Lint ——"
if command -v ruff >/dev/null 2>&1; then
  ruff check src tests app || echo "⚠️ Avisos de lint (não bloqueante)."
elif $PY -m ruff --version >/dev/null 2>&1; then
  $PY -m ruff check src tests app || echo "⚠️ Avisos de lint (não bloqueante)."
else
  echo "ℹ️ ruff não instalado — lint ignorado nesta fase."
fi

echo "ℹ️ O PDF é compilado pela GitHub Action em cada push (fonte de verdade)."
echo "✅ Verificação concluída."
