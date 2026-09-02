#!/usr/bin/env python3
"""Registar, inspecionar e remover o webhook do Telegram.

    python scripts/telegram_webhook.py estado
    python scripts/telegram_webhook.py registar https://investigator-....herokuapp.com
    python scripts/telegram_webhook.py remover

⚠️ **Registar um webhook desliga o `getUpdates`.** O Telegram não permite os dois: a partir do
registo, qualquer chamada a `getUpdates` devolve 409. É por isso que `TELEGRAM_WEBHOOK_ENABLED`
existe — cala o processamento de comandos no runner — e é por isso que o webhook trata também
dos comandos. Registar sem pôr essa variável a 1 deixa o `/watch` sem resposta.

O segredo do cabeçalho é gerado aqui se não existir no `.env`, e é impresso **uma vez** para
poder ser copiado para a configuração da plataforma. Não é gravado em lado nenhum por este
script: um segredo que um script escreve num ficheiro é um segredo que acaba num repositório.
"""

from __future__ import annotations

import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests  # noqa: E402

from investigator import config  # noqa: E402

CAMINHO = "/telegram/webhook"
# Só estes chegam ao servidor. Pedir menos do que o Telegram oferece é a forma mais barata de
# reduzir superfície: `message` traz os comandos, `callback_query` traz os votos, e mais nada é
# usado por este sistema.
ATUALIZACOES = ["message", "callback_query"]


def _api(metodo: str) -> str:
    token = config.TELEGRAM_BOT_TOKEN
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN não está definido (vê o .env).")
    return f"https://api.telegram.org/bot{token}/{metodo}"


def estado() -> int:
    r = requests.get(_api("getWebhookInfo"), timeout=10).json()
    info = r.get("result", {})
    if not info.get("url"):
        print("Sem webhook registado. O bot está (ou pode estar) em long-polling.")
        return 0
    print(f"URL                 : {info['url']}")
    print(f"Updates pendentes   : {info.get('pending_update_count', 0)}")
    print(f"Tipos subscritos    : {', '.join(info.get('allowed_updates') or ['(todos)'])}")
    segredo = "sim" if info.get("has_custom_certificate") is not None else "?"
    print(f"Segredo configurado : {segredo}")
    if info.get("last_error_message"):
        # É aqui que se vê um webhook que responde 500 ou que não responde de todo, e é a
        # primeira coisa a olhar quando os votos param de chegar.
        print(f"⚠️ Último erro      : {info['last_error_message']} ({info.get('last_error_date')})")
    return 0


def registar(base: str) -> int:
    base = base.rstrip("/")
    if not base.startswith("https://"):
        raise SystemExit("O Telegram só aceita webhooks em HTTPS.")
    segredo = config.TELEGRAM_WEBHOOK_SECRET
    gerado = False
    if not segredo:
        segredo = secrets.token_urlsafe(32)
        gerado = True
    r = requests.post(_api("setWebhook"), data={
        "url": base + CAMINHO,
        "secret_token": segredo,
        "allowed_updates": '["' + '","'.join(ATUALIZACOES) + '"]',
        # Updates acumulados de antes do registo não interessam e podem ser muitos: descartá-los
        # evita que o primeiro minuto do webhook seja gasto a responder a comandos de ontem.
        "drop_pending_updates": "true",
    }, timeout=10).json()
    if not r.get("ok"):
        raise SystemExit(f"setWebhook falhou: {r}")
    print(f"Webhook registado em {base + CAMINHO}")
    if gerado:
        print("\nO segredo foi GERADO agora e não está guardado em lado nenhum. Define estas")
        print("duas variáveis na plataforma (e no .env local) antes de esperar votos:\n")
        print(f"  TELEGRAM_WEBHOOK_SECRET={segredo}")
        print("  TELEGRAM_WEBHOOK_ENABLED=1")
        print("\nSem a primeira, a rota responde 403 a tudo — inclusive ao Telegram.")
        print("Sem a segunda, o runner continua a chamar getUpdates e recebe 409 em cada ciclo.")
    else:
        print("Usado o TELEGRAM_WEBHOOK_SECRET que já existia.")
        print("Confirma que TELEGRAM_WEBHOOK_ENABLED=1 está definido na plataforma.")
    return 0


def remover() -> int:
    r = requests.post(_api("deleteWebhook"), data={"drop_pending_updates": "false"},
                      timeout=10).json()
    if not r.get("ok"):
        raise SystemExit(f"deleteWebhook falhou: {r}")
    print("Webhook removido. O `getUpdates` volta a funcionar —")
    print("põe TELEGRAM_WEBHOOK_ENABLED a vazio para o runner voltar a tratar dos comandos.")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in {"estado", "registar", "remover"}:
        print(__doc__)
        return 2
    if argv[1] == "estado":
        return estado()
    if argv[1] == "remover":
        return remover()
    if len(argv) < 3:
        raise SystemExit("Falta o endereço base, ex.: https://investigator-xxxx.herokuapp.com")
    return registar(argv[2])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
