"""Receção de updates do Telegram por webhook — o bot deixa de precisar de uma máquina ligada.

## Porque deixou de ser long-polling

O `getUpdates` funciona atrás de qualquer NAT e sem servidor, e foi por isso a escolha certa
enquanto não havia um. Agora há: o `api/main.py` já corre num dyno web com endereço público e
HTTPS, servido pelo `Procfile`. Uma recolha de feedback com semanas não pode depender de o
portátil do aluno estar ligado, e o webhook remove essa dependência sem custo nem dyno novo.

⚠️ **O Telegram não permite os dois ao mesmo tempo.** Com um webhook registado, o `getUpdates`
passa a devolver 409. Por isso o `process_bot_commands` do runner tem de se calar quando o
webhook está ativo, e por isso este módulo trata **também** dos comandos — se tratasse só dos
votos, registar o webhook matava o `/watch` em silêncio.

## O que é durável e o que não é, dito sem rodeios

Os **votos** vão para um JSONL que é publicado na branch de dados, pelo mesmo mecanismo que já
serve o `gate_log`. Sobrevivem ao reinício do dyno, que na Heroku acontece pelo menos uma vez
por dia.

As **watchlists** dos subscritores continuam em SQLite num disco efémero, e continuam a
perder-se no reinício. Isso já era verdade antes desta alteração — o fan-out do runner já
imprimia «sem base de subscritores» — e esta alteração não piora nem melhora esse ponto. Fica
escrito para que ninguém conclua, ao ler o webhook, que passou a haver persistência que não há.

## Ordem das operações, e a razão

1. Gravar o voto. É uma escrita local, custa microssegundos.
2. Responder ao `callback_query`. **Sempre**, mesmo se o passo 1 falhou — sem resposta o
   relógio continua a girar no telemóvel e o Telegram reenvia o update, transformando um erro
   de escrita numa repetição sem fim.
3. Atualizar o teclado com a contagem. É o único passo que pode falhar sem consequência.
4. Publicar. Fora do caminho da resposta, e fail-open.

Testável sem rede: todas as saídas são injetadas em `Contexto`.
"""

from __future__ import annotations

import hmac
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from investigator import feedback_log as FL
from investigator.telegram_bot import feedback as F


@dataclass
class Contexto:
    """As dependências externas, injetadas. Nenhuma é chamada mais do que uma vez por update."""

    sal: str
    caminho_votos: Path
    enviar: Callable[..., Any]
    responder_callback: Callable[..., Any]
    editar_teclado: Callable[..., Any] | None = None
    publicar: Callable[[Path], Any] | None = None
    ligacao_db: Callable[[], Any] | None = None


def segredo_confere(cabecalho: str | None, esperado: str) -> bool:
    """Compara o cabeçalho `X-Telegram-Bot-Api-Secret-Token` em tempo constante.

    Sem segredo configurado a rota fica fechada, e não aberta: um webhook público sem
    verificação aceita qualquer voto de qualquer pessoa que descubra o endereço, e a amostra da
    tese deixaria de significar o que diz significar.
    """
    if not esperado:
        return False
    return hmac.compare_digest(str(cabecalho or ""), str(esperado))


def processar(update: dict[str, Any], ctx: Contexto) -> str:
    """Trata um update. Devolve uma linha de registo. Nunca levanta exceção."""
    try:
        voto = F.interpretar(update, ctx.sal)
    except Exception as exc:  # noqa: BLE001
        return f"[webhook] update ilegível (ignorado): {type(exc).__name__}"
    if voto is not None:
        return _tratar_voto(voto, ctx)
    return _tratar_comando(update, ctx)


def _tratar_voto(voto: F.Voto, ctx: Contexto) -> str:
    gravado = False
    try:
        FL.append_jsonl(
            FL.FeedbackRecord(
                chave_alerta=voto.chave_alerta, votante=voto.votante, acao=voto.acao,
                at=FL.agora(), chat_id=voto.chat_id, message_id=voto.message_id,
            ),
            ctx.caminho_votos,
        )
        gravado = True
    except Exception as exc:  # noqa: BLE001
        erro = f"{type(exc).__name__}: {exc}"
    else:
        erro = ""

    # 2 — a resposta ao Telegram acontece sempre, e é o passo que não pode falhar em silêncio.
    try:
        ctx.responder_callback(
            voto.callback_id,
            F.aviso_recebido(voto) if gravado
            else "Não consegui registar o voto. O problema é nosso, e não teu.",
        )
    except Exception as exc:  # noqa: BLE001
        return f"[webhook] voto {'gravado' if gravado else 'perdido'}, resposta falhou: {exc}"

    if not gravado:
        return f"[webhook] voto perdido: {erro}"

    _atualizar_teclado(voto, ctx)
    _publicar(ctx)
    return f"[webhook] voto {voto.acao} em {voto.chave_alerta} de {voto.votante[:8]}"


def _atualizar_teclado(voto: F.Voto, ctx: Contexto) -> None:
    """Põe as contagens nos botões. Falhar aqui não perde nada: o voto já está gravado."""
    if ctx.editar_teclado is None or not voto.chat_id:
        return
    try:
        uteis, inuteis = FL.contagem(FL.load_jsonl(ctx.caminho_votos), voto.chave_alerta)
        ctx.editar_teclado(
            voto.message_id,
            F.teclado_com_contagem(voto.chave_alerta, uteis, inuteis),
            chat_id=voto.chat_id,
        )
    except Exception:  # noqa: BLE001
        pass


def _publicar(ctx: Contexto) -> None:
    """Publica o ficheiro de votos na branch de dados. Fora do caminho da resposta, fail-open.

    O disco do dyno é efémero: sem este passo, os votos de um dia desaparecem no reinício
    seguinte, e a recolha inteira seria uma sucessão de amostras de algumas horas.
    """
    if ctx.publicar is None:
        return
    try:
        ctx.publicar(ctx.caminho_votos)
    except Exception:  # noqa: BLE001
        pass


def _tratar_comando(update: dict[str, Any], ctx: Contexto) -> str:
    """`/watch`, `/list`, `/stop` — o que o poller fazia, agora aqui.

    ⚠️ Tem de existir. Registar o webhook desliga o `getUpdates`, e sem este ramo os comandos
    deixariam de ter resposta sem que nada o assinalasse.
    """
    try:
        from investigator.telegram_bot.commands import handle_command
        from investigator.telegram_bot.interactive import extract_command

        par = extract_command(update)
        if par is None:
            return "[webhook] update sem comando nem voto (ignorado)"
        chat_id, texto = par
        comando = texto.split()[0].split("@")[0].lower()
        if comando in {"/apagar", "/deletefeedback"}:
            return _retirar_feedback(update, chat_id, ctx)
        if ctx.ligacao_db is None:
            ctx.enviar("O bot está a arrancar. Tenta outra vez daqui a um minuto.",
                       chat_id=chat_id)
            return "[webhook] comando sem base disponível"
        conn = ctx.ligacao_db()
        ctx.enviar(handle_command(texto, chat_id, conn), chat_id=chat_id)
        return f"[webhook] comando {texto.split()[0]!r} de {chat_id}"
    except Exception as exc:  # noqa: BLE001
        return f"[webhook] comando falhou (ignorado): {type(exc).__name__}: {exc}"


def _retirar_feedback(update: dict[str, Any], chat_id: str, ctx: Contexto) -> str:
    """Regista a retirada sem reescrever o histórico acrescentável.

    A linha ``d`` funciona como marca de retirada: a análise apaga logicamente todos os votos
    anteriores desse resumo. As linhas pseudonimizadas permanecem no histórico Git, o que é
    explicado na resposta e no consentimento; prometer eliminação física seria falso.
    """
    mensagem = update.get("message") or {}
    autor = mensagem.get("from") or {}
    if "id" not in autor:
        ctx.enviar("I could not identify which feedback to withdraw.", chat_id=chat_id)
        return "[webhook] retirada sem identificador"

    try:
        votante = F.resumir_votante(autor["id"], ctx.sal)
        FL.append_jsonl(
            FL.FeedbackRecord(
                chave_alerta="*",
                votante=votante,
                acao=FL.RETIRAR,
                at=FL.agora(),
            ),
            ctx.caminho_votos,
        )
        _publicar(ctx)
    except Exception as exc:  # noqa: BLE001
        ctx.enviar("I could not withdraw the feedback. Please try again later.", chat_id=chat_id)
        return f"[webhook] retirada falhou: {type(exc).__name__}"

    ctx.enviar(
        "Your previous feedback has been withdrawn from the analysis. The versioned log keeps "
        "pseudonymised audit lines, but they no longer count. A future vote starts new "
        "participation.",
        chat_id=chat_id,
    )
    return f"[webhook] feedback retirado por {votante[:8]}"
