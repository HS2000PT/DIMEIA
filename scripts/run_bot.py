"""Bot interativo do InvestiGator (Fase B) — onboarding self-service por utilizador.

Corre um loop de *long-polling* (getUpdates): qualquer pessoa que fale com o bot pode
gerir a SUA watchlist (/start, /watch TSLA, /unwatch, /list, /stop). As subscrições
ficam em data/bot_users.db (SQLite, gitignored). O runner agendado
(`scripts/run_alerts.py`) distribui os alertas por subscritor quando `bot.enabled: true`
no config/alerts.yaml.

Requisitos: TELEGRAM_BOT_TOKEN no .env. Não precisa de servidor nem webhook — funciona
em qualquer máquina (o webhook/host fica documentado como evolução em going_live.md).

Uso:
    python scripts/run_bot.py           # Ctrl+C para parar
"""

from __future__ import annotations

import argparse

from investigator.console import force_utf8_stdout
from investigator.telegram_bot.interactive import run_polling
from investigator.telegram_bot.store import DEFAULT_DB


def main() -> int:
    force_utf8_stdout()
    parser = argparse.ArgumentParser(description="InvestiGator — bot interativo (long-polling)")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="base SQLite de subscritores")
    args = parser.parse_args()
    try:
        run_polling(db_path=args.db)
    except KeyboardInterrupt:
        print("\n[bot] parado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
