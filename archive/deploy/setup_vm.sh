#!/usr/bin/env bash
# Setup do vigia InvestiGator numa VM Linux acabada de criar (Ubuntu/Debian; Oracle Free serve).
# Correr como o utilizador normal (não root): bash deploy/setup_vm.sh
# Passos manuais ANTES: criar a VM + criar o PAT — ver docs/design/vm_watch.md.
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/HS2000PT/DIMEIA.git}"
BASE="$HOME"

echo "== 1/5 Dependências do sistema =="
sudo apt-get update -y && sudo apt-get install -y python3.12 python3.12-venv git || {
  echo "python3.12 indisponível no APT? Em Ubuntu 24.04 já vem; noutros, usar deadsnakes."; exit 1; }

echo "== 2/5 Clonar o código =="
if [ ! -d "$BASE/DIMEIA" ]; then git clone "$REPO_URL" "$BASE/DIMEIA"; fi
cd "$BASE/DIMEIA"
python3.12 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo "== 3/5 Checkout da branch de dados (histórico partilhado) =="
if [ ! -d "$BASE/alerts-history" ]; then
  # O PAT (fine-grained, só contents:read/write neste repo) entra no URL do remote — fica
  # APENAS na VM, nunca no repositório. Cria-o em GitHub → Settings → Developer settings.
  read -r -p "Cola o PAT do GitHub (fine-grained, contents RW): " PAT
  git clone --branch alerts-history "https://x-access-token:${PAT}@github.com/HS2000PT/DIMEIA.git" \
    "$BASE/alerts-history"
  git -C "$BASE/alerts-history" config user.name "investigator-vm"
  git -C "$BASE/alerts-history" config user.email "investigator-vm@users.noreply.github.com"
fi

echo "== 4/5 Segredos (.env) =="
if [ ! -f "$BASE/DIMEIA/.env" ]; then
  cp .env.example .env
  echo ">>> Edita $BASE/DIMEIA/.env com TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, FINNHUB_API_KEY <<<"
fi

echo "== 5/5 Serviço systemd =="
sudo cp deploy/investigator-watch.service /etc/systemd/system/
# Ajustar o utilizador do serviço ao utilizador real desta VM:
sudo sed -i "s|/home/investigator|$HOME|g; s|^User=investigator|User=$(whoami)|" \
  /etc/systemd/system/investigator-watch.service
sudo systemctl daemon-reload
echo
echo "Pronto. Depois de preencheres o .env:"
echo "  sudo systemctl enable --now investigator-watch"
echo "  journalctl -u investigator-watch -f     # ver os ciclos ao vivo"
