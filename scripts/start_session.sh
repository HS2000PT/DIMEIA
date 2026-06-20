#!/bin/bash
# Início de sessão: sincroniza e mostra o estado.
set -euo pipefail
git pull --rebase origin main
echo "—— CLAUDE.md (topo) ——"; head -n 40 CLAUDE.md || true
echo "—— Última sessão ——"; head -n 25 progress/SESSIONS.md || true
echo "✅ Pronto. Lê o CLAUDE.md na íntegra antes de agir."
