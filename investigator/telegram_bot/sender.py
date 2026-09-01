"""Envio e edição de mensagens via Telegram Bot API (gratuito). Segredos só do .env
(investigator/config).

Este ficheiro é o único sítio do pacote que fala com a rede do Telegram. A construção do texto
vive no `explanation_engine`, a dos teclados em `feedback.py`, e a interpretação dos comandos em
`commands.py` — todos puros, e todos testáveis sem rede.
"""

from __future__ import annotations

import json
from typing import Any

import requests

from investigator import config

_API = "https://api.telegram.org/bot{token}/{metodo}"


def _credenciais(token: str | None, chat_id: str | None) -> tuple[str, str]:
    token = token or config.TELEGRAM_BOT_TOKEN
    chat_id = chat_id or config.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        raise RuntimeError(
            "Telegram não configurado: define TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env."
        )
    return token, chat_id


def send_message(text: str, token: str | None = None, chat_id: str | None = None,
                 timeout: int = 10, parse_mode: str | None = "HTML",
                 reply_markup: dict[str, Any] | None = None) -> dict:
    """Envia uma mensagem via Telegram Bot API. Devolve a resposta JSON.

    `parse_mode="HTML"` por defeito (revisão UX): os alertas usam <b>/<i> para hierarquia
    visual; todo o conteúdo dinâmico é escapado nos construtores (explainer/commands).
    Se o Telegram rejeitar o HTML (400), reenvia UMA vez em texto puro — entregar vale mais
    do que formatar.

    `reply_markup` leva o teclado em linha do feedback quando existe. ⚠️ Vai na REPETIÇÃO em
    texto puro também: sem isso, um alerta que caísse no caminho de recurso perdia os botões
    em silêncio, e a amostra ficava enviesada precisamente pelos alertas com formatação mais
    difícil — que são os mais compridos, ou seja os mais informativos.
    """
    token, chat_id = _credenciais(token, chat_id)
    url = _API.format(token=token, metodo="sendMessage")
    payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup is not None:
        payload["reply_markup"] = json.dumps(reply_markup)
    resp = requests.post(url, data=payload, timeout=timeout)
    if resp.status_code == 400 and parse_mode:
        recurso: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if reply_markup is not None:
            recurso["reply_markup"] = json.dumps(reply_markup)
        resp = requests.post(url, data=recurso, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def message_id_de(resposta: dict) -> int | None:
    """O `message_id` que o `sendMessage` devolveu, ou `None`.

    É a identidade da mensagem no Telegram e é o que permite editá-la mais tarde — para
    acrescentar a análise, a contagem de votos, ou o desfecho observado ao fim de alguns dias.
    Sem o guardar no momento do envio, a mensagem torna-se inalcançável.
    """
    try:
        return int((resposta or {}).get("result", {}).get("message_id"))
    except (TypeError, ValueError):
        return None


def edit_message_text(text: str, message_id: int, token: str | None = None,
                      chat_id: str | None = None, timeout: int = 10,
                      parse_mode: str | None = "HTML",
                      reply_markup: dict[str, Any] | None = None) -> dict:
    """Substitui o texto de uma mensagem já entregue.

    Dois erros do Telegram não são falhas e são tratados como sucesso:

    - `message is not modified` — o texto novo é igual ao antigo. Aconteceu, é inofensivo, e
      levantar exceção aqui faria um ciclo de reedição periódica falhar em todos os dias
      calmos, que são a maioria.
    - `message to edit not found` — quem recebeu apagou a mensagem, ou o canal apagou-a. É um
      direito de quem lê, não um defeito nosso.
    """
    token, chat_id = _credenciais(token, chat_id)
    payload: dict[str, Any] = {"chat_id": chat_id, "message_id": int(message_id), "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup is not None:
        payload["reply_markup"] = json.dumps(reply_markup)
    resp = requests.post(_API.format(token=token, metodo="editMessageText"),
                         data=payload, timeout=timeout)
    dados = _json_seguro(resp)
    if _benigno(resp, dados):
        return dados
    if resp.status_code == 400 and parse_mode:
        payload.pop("parse_mode")
        resp = requests.post(_API.format(token=token, metodo="editMessageText"),
                             data=payload, timeout=timeout)
        dados = _json_seguro(resp)
        if _benigno(resp, dados):
            return dados
    resp.raise_for_status()
    return dados


def edit_message_reply_markup(message_id: int, reply_markup: dict[str, Any],
                              token: str | None = None, chat_id: str | None = None,
                              timeout: int = 10) -> dict:
    """Troca só o teclado — usado para atualizar a contagem de votos sem retocar o texto.

    Editar apenas o teclado, e não o texto, evita que o alerta apareça como «editado» aos
    olhos de quem o leu: a promessa da secção «What was sent» do painel é que o texto entregue
    não é reescrito, e essa promessa tem de valer também no Telegram.
    """
    token, chat_id = _credenciais(token, chat_id)
    resp = requests.post(
        _API.format(token=token, metodo="editMessageReplyMarkup"),
        data={"chat_id": chat_id, "message_id": int(message_id),
              "reply_markup": json.dumps(reply_markup)},
        timeout=timeout,
    )
    dados = _json_seguro(resp)
    if _benigno(resp, dados):
        return dados
    resp.raise_for_status()
    return dados


def answer_callback_query(callback_id: str, text: str = "", token: str | None = None,
                          timeout: int = 5) -> dict:
    """Fecha o `callback_query` — o balão de confirmação no telemóvel de quem votou.

    ⚠️ Tem de acontecer em menos de um segundo e **sempre**, mesmo quando o voto não pôde ser
    gravado. Sem resposta, o relógio continua a girar no cliente e o Telegram reenvia o update
    — um defeito de gravação passaria a produzir uma repetição sem fim de tentativas.
    """
    token = token or config.TELEGRAM_BOT_TOKEN
    if not token:
        raise RuntimeError("Telegram não configurado: define TELEGRAM_BOT_TOKEN no .env.")
    resp = requests.post(
        _API.format(token=token, metodo="answerCallbackQuery"),
        data={"callback_query_id": str(callback_id), "text": text[:200]},
        timeout=timeout,
    )
    return _json_seguro(resp)


def _json_seguro(resp) -> dict:
    try:
        return resp.json()
    except ValueError:
        return {}


def _benigno(resp, dados: dict) -> bool:
    """True quando a resposta é sucesso, ou um dos dois erros que não são falhas."""
    if resp.status_code < 400:
        return True
    descricao = str(dados.get("description", "")).lower()
    return ("not modified" in descricao) or ("message to edit not found" in descricao)
