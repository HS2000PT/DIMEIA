#!/bin/bash
# Fim de sessão: verifica, faz commit, sincroniza e publica — sem force-push.
# Uso: bash scripts/end_session.sh "Descrição breve da sessão"
set -euo pipefail
SESSION_MSG=${1:-"Progresso da sessão"}
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

# 1) Verificação antes de guardar (testes, lint, build).
bash scripts/verify.sh

# 2) Stage de tudo.
git add .

# 3) Aviso de segredos: aborta se algo parecer um segredo COM VALOR no diff em stage.
#    Exclui o .env.example (só nomes de variáveis, sem valores).
#    Exige >=8 caracteres de valor para evitar falsos positivos em templates vazios.
SECRET_REGEX='(api[_-]?key|secret|token|password|bearer)["'"'"' ]*[:=]["'"'"' ]*[A-Za-z0-9_./+=-]{8,}'
if git diff --cached -- . ':(exclude).env.example' | grep -E -i "$SECRET_REGEX" ; then
  echo "❌ Possível segredo detetado no commit. A abortar. Verifica e remove."
  git reset
  exit 1
fi

# 4) Commit.
git commit -m "Sessão — $TIMESTAMP: $SESSION_MSG" || echo "Nada para fazer commit."

# 5) Sincroniza ANTES de publicar (evita rejeição por non-fast-forward).
if ! git pull --rebase origin main ; then
  echo "❌ Conflito de rebase. NÃO faço force-push. Resolve manualmente e corre de novo."
  exit 1
fi

# 6) Publica.
git push origin main
echo "✅ Sessão verificada, guardada e sincronizada com o GitHub."
