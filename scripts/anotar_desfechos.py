#!/usr/bin/env python3
"""Acrescenta a cada alerta já entregue o que a ação veio a fazer a +1, +3 e +5 sessões.

## O que isto faz, e porque é a parte que interessa do alerta em dois tempos

O sistema guarda, desde 2026-09-01, o `message_id` de cada alerta que envia. Isso torna a
mensagem alcançável para sempre, e permite voltar a ela dias depois para lhe anexar o desfecho
observado — no sítio onde a afirmação foi feita, e para as mesmas pessoas que a leram.

É a diferença entre um sistema que explica e um sistema que se deixa verificar. Nenhum dos
produtos comparados no Capítulo 2 volta atrás para dizer como correu.

## As guardas, e o que cada uma impede

- **Só edita quando há informação nova** (`precisa_de_edicao`). Cada edição é uma notificação;
  uma edição que não acrescenta nada é a única forma de esta funcionalidade incomodar.
- **Acrescenta, nunca reescreve.** O texto original fica intacto por baixo do bloco novo.
- **Uma mensagem apagada não é um erro.** O `sender` trata `message to edit not found` como
  sucesso: quem recebe tem o direito de apagar.
- **Fail-open por alerta.** Um ticker sem preços não impede os restantes.
- **Só toca em mensagens de que temos o HTML exato** (`text_html`). O `text` do histórico é a
  versão sem tags, para a consola e para o painel: reenviá-lo perderia o negrito e, numa
  manchete com «<» ou «&», produziria HTML inválido. Uma entrada sem `text_html` é saltada.
- **Nada de horizontes por medir.** Um horizonte sem barra fica de fora do bloco em vez de
  aparecer como espaço reservado — ver a razão em `desfecho.anotacao`.

Uso:
    python scripts/anotar_desfechos.py --dry-run     # mostra o que faria, não toca em nada
    python scripts/anotar_desfechos.py
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from investigator.alerts_history import HistoryEntry, load_jsonl, save_jsonl  # noqa: E402
from investigator.explanation_engine.desfecho import (  # noqa: E402
    HORIZONTES,
    Desfecho,
    anotar,
    precisa_de_edicao,
)

DEFAULT_HISTORICO = REPO / "data" / "alerts_history.jsonl"
# Depois de doze dias de calendário, as cinco sessões já passaram com folga mesmo com feriados
# e fins de semana pelo meio. Além disso a mensagem já não está no ecrã de ninguém, e editá-la
# seria acordar uma conversa antiga sem retorno.
JANELA_DIAS = 12


def desfechos_de(ticker: str, dia_alerta: str,
                 horizontes: tuple[int, ...] = HORIZONTES) -> list[Desfecho]:
    """Retornos observados desde o fecho do dia do alerta até N sessões depois.

    Conta **sessões** e não dias de calendário: um alerta de sexta-feira mede o +1d contra a
    segunda seguinte, e não contra o sábado, que não existe. É por isso que a série é lida da
    fonte em vez de as datas serem somadas.
    """
    from investigator.market_data.prices import fallback_daily

    inicio = (date.fromisoformat(dia_alerta) - timedelta(days=5)).isoformat()
    fim = (date.fromisoformat(dia_alerta) + timedelta(days=max(horizontes) + 12)).isoformat()
    df, _fonte = fallback_daily(ticker, inicio, fim)
    fechos = df["Close"] if "Close" in df.columns else df.iloc[:, 0]

    # A barra do próprio dia do alerta é a referência. Se a fonte não a tiver — o alerta pode
    # ter saído antes do fecho, ou o dia pode não ser sessão —, usa-se a última barra ANTERIOR
    # ou igual, e não a seguinte: medir contra uma barra futura seria olhar para o futuro a
    # partir do momento do alerta, exatamente o defeito que a avaliação da tese passou o
    # trabalho todo a evitar.
    ate_ao_dia = fechos[fechos.index.date <= date.fromisoformat(dia_alerta)]
    if ate_ao_dia.empty:
        return [Desfecho(h, None) for h in horizontes]
    base = float(ate_ao_dia.iloc[-1])
    posteriores = fechos[fechos.index.date > date.fromisoformat(dia_alerta)]

    saida = []
    for h in horizontes:
        if len(posteriores) >= h and base:
            saida.append(Desfecho(h, float(posteriores.iloc[h - 1]) / base - 1.0))
        else:
            saida.append(Desfecho(h, None))
    return saida


def entradas_a_anotar(entradas: list[HistoryEntry], hoje: date,
                      janela: int = JANELA_DIAS) -> list[HistoryEntry]:
    """Alertas de notícia, com mensagem alcançável, dentro da janela e não anteriores a hoje."""
    saida = []
    for e in entradas:
        if e.kind != "news" or not e.message_id or not e.date or not e.text_html:
            continue
        try:
            dia = date.fromisoformat(e.date)
        except ValueError:
            continue
        if dia > hoje or (hoje - dia).days > janela:
            continue
        saida.append(e)
    return saida


def anotar_tudo(historico: str | Path = DEFAULT_HISTORICO, *, dry_run: bool = False,
                hoje: date | None = None) -> int:
    """Percorre o histórico e anota o que houver a anotar. Devolve quantas mensagens editou.

    Separada do `main` para poder ser chamada de dentro do `run_alerts.py` sem passar por
    `sys.argv` — o worker já é um processo permanente e não precisa de lançar um subprocesso
    para fazer isto uma vez por dia.
    """
    caminho = Path(historico)
    entradas = load_jsonl(caminho)
    hoje = hoje or datetime.now(UTC).date()
    candidatas = entradas_a_anotar(entradas, hoje)
    alcancaveis = sum(1 for e in entradas if e.kind == "news" and e.message_id)
    print(f"[desfechos] {len(entradas)} entrada(s) no histórico, {alcancaveis} alcançável(eis), "
          f"{len(candidatas)} candidata(s) na janela de {JANELA_DIAS} dias.")

    editadas = 0
    for i, e in enumerate(entradas):
        if e not in candidatas:
            continue
        try:
            ds = desfechos_de(e.ticker, e.date)
        except Exception as exc:  # noqa: BLE001  (um ticker sem preços não pára os outros)
            print(f"[desfechos] {e.ticker} {e.date}: sem preços ({type(exc).__name__}) — segue")
            continue
        if not precisa_de_edicao(e.text_html, ds):
            continue
        novo_html = anotar(e.text_html, ds)
        medidos = ", ".join(f"+{d.dias}d {d.retorno * 100:+.2f}%"
                            for d in ds if d.retorno is not None)
        if dry_run:
            print(f"[dry-run] editaria {e.ticker} {e.date} (msg {e.message_id}): {medidos}")
            continue
        try:
            from investigator.telegram_bot.sender import edit_message_text

            edit_message_text(novo_html, e.message_id, chat_id=e.chat_id or None)
        except Exception as exc:  # noqa: BLE001
            print(f"[desfechos] {e.ticker} {e.date}: edição falhou ({type(exc).__name__}) — segue")
            continue
        # O histórico partilhado tem de refletir EXATAMENTE o que está no Telegram. Se
        # divergissem, o painel — que lê daqui — passaria a mostrar uma versão que já não
        # existe, e a promessa de «isto é o que foi enviado, palavra por palavra» cairia.
        from investigator.explanation_engine.explainer import plain_text

        entradas[i] = HistoryEntry(**{**e.__dict__, "text_html": novo_html,
                                      "text": plain_text(novo_html), "estado": "anotado"})
        editadas += 1
        print(f"[desfechos] {e.ticker} {e.date} anotado: {medidos}")

    if editadas and not dry_run:
        save_jsonl(entradas, caminho)
        print(f"[desfechos] {editadas} mensagem(ns) anotada(s); histórico atualizado.")
        try:
            from investigator.history_publish import publish_safe

            publish_safe(caminho)
        except Exception as exc:  # noqa: BLE001
            print(f"[desfechos] publicação indisponível (ignorado): {type(exc).__name__}")
    elif not editadas:
        print("[desfechos] nada de novo a acrescentar.")
    return editadas


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--historico", default=str(DEFAULT_HISTORICO))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--hoje", default="", help="ISO, para testes")
    args = ap.parse_args()
    anotar_tudo(args.historico, dry_run=args.dry_run,
                hoje=date.fromisoformat(args.hoje) if args.hoje else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
