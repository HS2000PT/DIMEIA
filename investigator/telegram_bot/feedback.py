"""Feedback do leitor sobre um alerta — o lado que faltava para a comunicação ser nos dois
sentidos.

## Porque existe

A tese declara, como limitação, que a hipótese fundadora — a de que uma explicação
verificável conduz a uma decisão melhor — não foi testada, por não ter havido estudo com
utilizadores. Isto não testa essa hipótese. Testa uma coisa mais estreita e mensurável: se
os alertas que o sistema **decide** enviar são considerados úteis por quem os recebe, e se
essa utilidade percebida acompanha a pontuação de triagem que o modelo lhes atribuiu. É a
primeira vez que uma medida interna do sistema é confrontada com um juízo externo.

## As decisões de desenho, e a razão de cada uma

**Dois botões e não cinco.** Uma escala de Likert num telemóvel tem taxa de resposta pior, e
com o N que uma janela de três semanas num canal pequeno permite, cinco níveis não sustentam
melhor análise do que dois — sustentam pior, porque dividem a amostra.

**O `callback_data` leva a chave do alerta, não o texto.** O Telegram impõe 64 bytes. A chave
é a mesma que o histórico partilhado usa para deduplicar entre produtores, sha1 truncado a
doze caracteres, o que deixa o campo em dezassete bytes e permite correlacionar o voto com o
alerta sem depender de o processo que recebe o voto ser o mesmo que o enviou. Na Heroku não é:
o `web` e o `worker` são dynos distintos, com discos distintos.

**Quem vota é `from.id` e não o chat.** Num canal o chat é o canal, igual para toda a gente; o
votante é o utilizador. Confundir os dois daria um voto por canal em vez de um voto por pessoa.

**O identificador do votante é guardado em resumo criptográfico e nunca em claro.** A análise
precisa de distinguir pessoas — para não contar dez votos de uma como dez pessoas —, e não
precisa de as identificar. O resumo permite a primeira coisa e impede a segunda. É a mesma
posição de minimização que a Secção de privacidade da tese assume para as carteiras.

**Um voto repetido substitui, nunca acumula.** Mudar de opinião é dado, não ruído; e sem esta
regra qualquer pessoa podia carregar cem vezes no mesmo botão.

**A resposta ao Telegram é imediata e incondicional.** Um `callback_query` sem
`answerCallbackQuery` fica com o relógio a girar no telemóvel de quem carregou, e o Telegram
reenvia o update. Responder mesmo em erro é o que impede um defeito de se transformar numa
tempestade de repetições.

Puro: este módulo não faz rede nem toca em disco. O envio vive em `sender.py`, a persistência
em `store.py` e a receção em `api/main.py`.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

PREFIXO = "fb"
UTIL = "u"
INUTIL = "n"
_ACOES = {UTIL, INUTIL}

# O Telegram corta o `callback_data` aos 64 bytes e não avisa: o botão simplesmente deixa de
# funcionar, em silêncio. Doze caracteres de chave deixam a carga em dezassete bytes.
MAX_CALLBACK_DATA = 64
TAM_CHAVE = 12

ROTULO_UTIL = "👍 Útil"
ROTULO_INUTIL = "👎 Não ajudou"


@dataclass(frozen=True)
class Voto:
    """Um voto recebido, já interpretado. `votante` é o resumo, nunca o identificador."""

    chave_alerta: str
    votante: str
    acao: str
    callback_id: str
    chat_id: str
    message_id: int

    @property
    def util(self) -> bool:
        return self.acao == UTIL


def resumir_votante(user_id: str | int, sal: str) -> str:
    """Resumo estável e não reversível do identificador do votante.

    `blake2b` com sal: o mesmo utilizador dá sempre o mesmo resumo, o que permite contar
    pessoas; sem o sal ninguém reconstrói o identificador a partir do resumo, e o espaço de
    identificadores do Telegram é pequeno o suficiente para que um resumo sem sal fosse
    percorrível por força bruta em minutos.
    """
    if not sal:
        raise ValueError("resumir_votante exige um sal; sem ele o resumo é reversível.")
    h = hashlib.blake2b(str(user_id).encode("utf-8"), key=sal.encode("utf-8"), digest_size=12)
    return h.hexdigest()


def encurtar_chave(chave: str) -> str:
    """Chave do alerta reduzida ao que cabe no `callback_data`.

    Aceita a chave do histórico (já truncada a doze) e qualquer outra forma — por exemplo
    `2026-09-01:TSLA` nos alertas de mercado, que não têm chave de notícia. Nesse caso resume,
    porque um `date:ticker` longo estouraria o limite e o botão morreria calado.
    """
    chave = (chave or "").strip()
    if not chave:
        return ""
    if len(chave) <= TAM_CHAVE and chave.isalnum():
        return chave
    return hashlib.sha1(chave.encode("utf-8")).hexdigest()[:TAM_CHAVE]


def dados_callback(chave: str, acao: str) -> str:
    if acao not in _ACOES:
        raise ValueError(f"ação desconhecida: {acao!r}")
    dados = f"{PREFIXO}|{acao}|{encurtar_chave(chave)}"
    if len(dados.encode("utf-8")) > MAX_CALLBACK_DATA:
        raise ValueError(f"callback_data com {len(dados)} bytes excede o limite do Telegram")
    return dados


def teclado(chave: str) -> dict[str, Any]:
    """O teclado em linha que acompanha um alerta. Uma linha, dois botões."""
    return {
        "inline_keyboard": [[
            {"text": ROTULO_UTIL, "callback_data": dados_callback(chave, UTIL)},
            {"text": ROTULO_INUTIL, "callback_data": dados_callback(chave, INUTIL)},
        ]]
    }


def teclado_com_contagem(chave: str, uteis: int, inuteis: int) -> dict[str, Any]:
    """O mesmo teclado, com as contagens no rótulo.

    Um botão que não muda nada depois de premido lê-se como avariado, e deixa de ser premido.
    A contagem é a confirmação mais barata de que o voto chegou, e não exige uma mensagem nova.
    """
    return {
        "inline_keyboard": [[
            {"text": f"{ROTULO_UTIL} {uteis}" if uteis else ROTULO_UTIL,
             "callback_data": dados_callback(chave, UTIL)},
            {"text": f"{ROTULO_INUTIL} {inuteis}" if inuteis else ROTULO_INUTIL,
             "callback_data": dados_callback(chave, INUTIL)},
        ]]
    }


def interpretar(update: dict[str, Any], sal: str) -> Voto | None:
    """Extrai um `Voto` de um update do Telegram, ou `None` se não for um voto nosso.

    Puro e tolerante: aceita o JSON tal como a API o entrega, e devolve `None` — nunca uma
    exceção — perante qualquer coisa que não reconheça. Um update malformado não é um erro do
    sistema; é tráfego.
    """
    if not isinstance(update, dict):
        return None
    cq = update.get("callback_query")
    if not isinstance(cq, dict):
        return None
    dados = cq.get("data")
    if not isinstance(dados, str):
        return None
    partes = dados.split("|")
    if len(partes) != 3 or partes[0] != PREFIXO or partes[1] not in _ACOES:
        return None
    quem = cq.get("from") or {}
    msg = cq.get("message") or {}
    chat = msg.get("chat") or {}
    if "id" not in quem:
        return None
    try:
        message_id = int(msg.get("message_id"))
    except (TypeError, ValueError):
        return None
    return Voto(
        chave_alerta=partes[2],
        votante=resumir_votante(quem["id"], sal),
        acao=partes[1],
        callback_id=str(cq.get("id") or ""),
        chat_id=str(chat.get("id") or ""),
        message_id=message_id,
    )


def aviso_recebido(voto: Voto) -> str:
    """O balão que aparece no telemóvel de quem votou. O Telegram corta aos 200 caracteres."""
    if voto.util:
        return "Registado. Obrigado — é isto que nos diz quais alertas valem a pena."
    return "Registado. Um alerta que não ajuda é a informação mais útil que podemos receber."
