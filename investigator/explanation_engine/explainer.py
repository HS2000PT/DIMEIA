"""Motor de explicação (XAI) — regra transparente + precedentes históricos.

Produz texto rastreável: o utilizador vê exatamente porque é que o alerta disparou.
- Gatilho 1 (anomalia): `explain_anomaly` / `explain_normal` (z-score, janela, média/desvio).
- Gatilho 2 (notícia): `explain_news_impact` — a notícia + precedentes históricos semelhantes
  (recuperados por similaridade) e o impacto que tiveram.

Formato (revisão UX 2026-07-06): mensagens em CAMADAS — o facto que interessa primeiro, a
lista a seguir, o método numa nota final curta. O Telegram renderiza em HTML (parse_mode no
sender), por isso o conteúdo dinâmico é escapado e os títulos levam <b>…</b>. TODOS os números
calculados continuam presentes (fidelidade XAI testada em tests/test_explainer.py).
"""

from __future__ import annotations

import html
from typing import TYPE_CHECKING

from investigator.anomaly_detector.detector import AnomalyResult

if TYPE_CHECKING:
    from investigator.historical_kb.record import NewsRecord

_MAX_HEADLINE = 100  # truncagem SÓ de apresentação (os objetos calculados ficam intactos)


def _nome(ticker: str) -> str:
    """Sufixo ' (Apple)' quando há nome amigável ≠ ticker — leigos não sabem símbolos.

    Aditivo por desenho: os tokens de fidelidade XAI ('Anomaly detected for {T}', 'News
    alert for {T}') ficam intactos; tickers fora do mapa (ex.: testes) não ganham sufixo.
    """
    try:
        from investigator.news_fetcher.relevance import display_name

        nome = display_name(ticker)
        return f" ({nome})" if nome.upper() != ticker.upper() else ""
    except Exception:  # noqa: BLE001
        return ""


def plain_text(alert: str) -> str:
    """Versão sem tags para consola/app (o Telegram recebe o HTML canónico)."""
    out = alert.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", "")
    return html.unescape(out)


def direction_icon(value: float) -> str:
    """Ícone de direção — a FONTE ÚNICA (o bug das setas vinha de lógica duplicada em 3
    sítios: aqui, no resumo diário e no dashboard). Cor certa: 📈 sobe (verde), 📉 desce
    (vermelho) — o antigo 🔺/🔻 era vermelho nos dois sentidos e confundia."""
    return "📈" if value >= 0 else "📉"


def _clip(text: str, limit: int = _MAX_HEADLINE) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def severity_label(z_score: float) -> str:
    """Nível do movimento por |z| (produto, 2026-07-13): notable < strong < extreme.

    Com o limiar de implantação em 1,5 o canal ganha vida — mas nem todos os alertas pesam
    o mesmo, e um leigo não lê z-scores. Os degraus são os limiares clássicos: ≥3 desvios
    (o congelado da tese) = extreme; ≥2 = strong; o resto acima do limiar = notable.
    """
    az = abs(z_score)
    if az >= 3.0:
        return "extreme"
    if az >= 2.0:
        return "strong"
    return "notable"


def explain_anomaly(ticker: str, result: AnomalyResult) -> str:
    """Alerta de anomalia em CAMADAS, legível num relance (revisão UX 2026-07-22).

    Linha 1 (o facto, a negrito): direção + empresa + movimento de hoje.
    Linha 2: quão grande em palavras simples (severidade + múltiplo da oscilação típica).
    Linha final (nota curta): porque disparou (a estatística, para quem quiser).
    """
    icon = direction_icon(result.last_return)
    if result.zero_variance:
        return (
            f"{icon} <b>{html.escape(ticker, quote=False)}"
            f"{html.escape(_nome(ticker), quote=False)} · "
            f"{result.last_return * 100:+.2f}% today</b>\n"
            f"Move after a flat {result.window}-day baseline.\n"
            f"<i>Why flagged: the previous {result.window} daily returns had zero variation, "
            f"so a z-score is undefined; today's return differs from their "
            f"{result.mean * 100:+.2f}% mean. An observed move, not advice.</i>"
        )
    sev = severity_label(result.z_score).capitalize()
    return (
        f"{icon} <b>{html.escape(ticker, quote=False)}"
        f"{html.escape(_nome(ticker), quote=False)} · "
        f"{result.last_return * 100:+.2f}% today</b>\n"
        f"{sev} move · about {abs(result.z_score):.1f}× its typical daily swing "
        f"({result.window}-day norm).\n"
        f"<i>Why flagged: z-score {result.z_score:+.2f} vs threshold ±{result.threshold:g}, "
        f"i.e. {abs(result.z_score):.1f} standard deviations from the {result.window}-day mean "
        f"({result.mean * 100:+.2f}%, std {result.std * 100:.2f}%). "
        f"An observed move, not advice.</i>"
    )


def explain_intraday(ticker: str, result: AnomalyResult) -> str:
    """Anomalia INTRADIÁRIA (movimento em curso, sem esperar o fecho) — mesmas camadas do
    alerta diário, com "so far today" e a fonte (cotação ao vivo vs fecho anterior)."""
    icon = direction_icon(result.last_return)
    if result.zero_variance:
        return (
            f"{icon} <b>{html.escape(ticker, quote=False)}"
            f"{html.escape(_nome(ticker), quote=False)} · "
            f"{result.last_return * 100:+.2f}% so far today</b>\n"
            f"Move in progress after a flat {result.window}-day baseline · "
            f"the session is not over.\n"
            f"<i>Why flagged: the previous {result.window} complete daily returns had zero "
            f"variation, so a z-score is undefined; the live return differs from their "
            f"{result.mean * 100:+.2f}% mean. An observed move in progress, not advice.</i>"
        )
    sev = severity_label(result.z_score).capitalize()
    return (
        f"{icon} <b>{html.escape(ticker, quote=False)}"
        f"{html.escape(_nome(ticker), quote=False)} · "
        f"{result.last_return * 100:+.2f}% so far today</b>\n"
        f"{sev} move in progress · about {abs(result.z_score):.1f}× its typical daily swing "
        f"({result.window}-day norm) · the session is not over.\n"
        f"<i>Why flagged: live quote vs yesterday's close · z-score {result.z_score:+.2f} vs "
        f"threshold ±{result.threshold:g} against the {result.window}-day daily norm "
        f"({result.mean * 100:+.2f}%, std {result.std * 100:.2f}%). "
        f"An observed move in progress, not advice.</i>"
    )


def attach_news_context(alert_text: str, headline: str | None,
                        news_date: str = "", today: str = "") -> str:
    """Investigação cruzada (anomalia → notícia): anexa a explicação candidata ao alerta.

    O comportamento do "trader profissional": vê o movimento, procura a causa. Com notícia
    relevante recente, o alerta ganha a linha "Possible explanation"; SEM notícia, diz que
    não há explicação pública conhecida — a ausência também é informação útil (e honesta).
    A hipótese nunca é afirmada como causa provada — é a manchete mais recente relevante.
    """
    if headline:
        quando = ""
        if news_date and today:
            idade = _age_label(news_date, today)
            quando = f" ({idade})" if idade else ""
        return (alert_text +
                f'\nPossible explanation{quando}: '
                f'"{html.escape(_clip(headline), quote=False)}"')
    return (alert_text +
            "\nNo relevant news found in the last 48h. No public explanation yet.")


# Quantas vezes o movimento do título tem de exceder a mediana dos pares para deixar de se
# poder chamar "setorial". Em 2× a diferença já é visível a olho e o modelo de dois fatores
# atribui a maior parte à empresa; abaixo disso, chamar-lhe setorial é defensável.
_SECTOR_DISPROPORTION = 2.0


def sector_context_line(ticker: str, moves: dict[str, float],
                        min_move: float = 0.01, top_n: int = 3) -> str:
    """Puro: 1 linha descritiva sobre o setor no MESMO dia — nunca causa nem previsão.

    O pedido real do investidor: "a NVIDIA está correlacionada com o setor; uma notícia
    noutra empresa pode afetá-la". Se outros nomes do mesmo setor (taxonomia da tese,
    relevance.SECTOR_OF) também mexeram ≥1% na MESMA direção, o movimento parece setorial;
    se estiveram parados, parece específico da empresa. `moves` = retornos do dia por ticker
    (só os já buscados na varredura — zero chamadas extra). '' quando não há o que dizer.
    """
    from investigator.news_fetcher.relevance import SECTOR_LABEL, SECTOR_OF

    tkr = ticker.upper()
    sec = SECTOR_OF.get(tkr)
    my_move = moves.get(tkr)
    if sec is None or my_move is None or my_move == 0:
        return ""
    peers = {t: m for t, m in moves.items()
             if t != tkr and m is not None and SECTOR_OF.get(t) == sec}
    if not peers:
        return ""
    label = SECTOR_LABEL.get(sec, sec)
    same_dir = {t: m for t, m in peers.items()
                if abs(m) >= min_move and (m > 0) == (my_move > 0)}
    if same_dir:
        tops = sorted(same_dir.items(), key=lambda kv: -abs(kv[1]))[:top_n]
        listagem = ", ".join(f"{t} {m * 100:+.1f}%" for t, m in tops)
        # A MAGNITUDE decide, não só a direção.
        #
        # Isto era um defeito real, medido no histórico: em 9 de 30 alertas esta linha dizia
        # "looks sector-wide" e a linha SEGUINTE, da decomposição de dois fatores, dizia "most
        # of this move was specific to the company". O caso mais gritante foi a AMD a cair
        # 13,23% com os pares a cair 2,0%, 1,9% e 1,4%: a direção coincide, a dimensão não.
        # Um alerta que se contradiz a si próprio duas linhas depois destrói a confiança que
        # todo o resto do sistema tenta construir.
        mediana = sorted(abs(m) for m in same_dir.values())[len(same_dir) // 2]
        desproporcionado = mediana > 0 and abs(my_move) > _SECTOR_DISPROPORTION * mediana
        if desproporcionado:
            return (f"Sector check: other {label} names moved the same way today ({listagem}), "
                    f"but by far less than {tkr} did. The direction is shared; the size is not.")
        return (f"Sector check: other {label} names moved the same way, and by a similar "
                f"amount, today ({listagem}).")
    return (f"Sector check: other {label} names were quiet today. "
            f"This move looks specific to {tkr}.")


def explain_normal(ticker: str, result: AnomalyResult) -> str:
    """Mensagem quando não há anomalia (útil para testes/diagnóstico)."""
    if result.zero_variance:
        return (
            f"No anomaly for {html.escape(ticker, quote=False)} today "
            f"(the return stayed at the flat {result.window}-day mean)."
        )
    return (
        f"No anomaly for {html.escape(ticker, quote=False)} today "
        f"(z-score {result.z_score:+.2f}, within ±{result.threshold:g})."
    )


def _age_label(rec_date: str, today: str) -> str:
    """Idade legível de um precedente ('18d ago', '7mo ago', '2y ago'); '' se indisponível.

    "Timeline matters" (feedback real do aluno): o utilizador tem de VER a idade de cada
    precedente sem fazer contas de datas.
    """
    from datetime import date as _date

    try:
        dias = (_date.fromisoformat(today) - _date.fromisoformat(rec_date)).days
    except ValueError:
        return ""
    if dias < 0:
        return ""
    if dias < 60:
        return f"{dias}d ago"
    if dias < 540:
        return f"{round(dias / 30)}mo ago"
    return f"{round(dias / 365)}y ago"


def _impacts(precedents: list[tuple[NewsRecord, float]], horizon: int) -> list[float]:
    """Impactos não-NaN dos precedentes no horizonte, pela ordem recebida."""
    key = str(horizon)
    return [
        rec.impacts[key]
        for rec, _ in precedents
        if key in rec.impacts and rec.impacts[key] == rec.impacts[key]  # exclui NaN
    ]


def _mean_precedent_impact(precedents: list[tuple[NewsRecord, float]], horizon: int) -> float:
    """Impacto médio dos precedentes no horizonte (ignora NaN). NaN se não houver dados."""
    vals = _impacts(precedents, horizon)
    return sum(vals) / len(vals) if vals else float("nan")


# ── Alerta em dois tempos: o esboço, e depois a análise ───────────────────────────────────
#
# **Porque existe.** A recuperação semântica é o passo caro do percurso: o codificador de
# frases custa cerca de sete segundos a carregar a frio, medidos, e é essa a razão declarada
# para a recuperação estar fora do painel. Enquanto ela corre, o leitor não tem nada — e o
# facto que o alerta comunica (esta empresa, esta manchete, este movimento) já está todo
# apurado.
#
# **O que isto NÃO resolve, e é preciso dizê-lo antes que alguém o assuma.** A mediana entre a
# publicação de uma notícia e a sua deteção pelas fontes gratuitas é de 353 minutos. Entre a
# deteção e a chegada da mensagem são 5 segundos. Enviar o esboço primeiro poupa segundos, não
# minutos, e não toca nos 353. O ganho está noutro sítio: o leitor vê o sistema a trabalhar, a
# recuperação deixa de estar no caminho crítico, e a mesma mensagem passa a poder ser anotada
# dias depois com o desfecho observado — que é a parte que nenhum produto comparável faz.
#
# **A regra que mantém isto honesto:** o esboço traz a advertência desde o primeiro segundo. Uma
# mensagem que sai sem ela, mesmo por oito segundos, é uma mensagem que saiu sem ela.

# ⚠️ «checking WHETHER there are», e não «looking for». A primeira redação dizia «looking for
# similar past headlines», e um teste apanhou o problema: lida depressa, afirma que existem
# casos semelhantes antes de o sistema ter procurado. É a mesma distinção entre «não há» e
# «não vimos» que a própria página do painel recusa esbater.
ESTADO_A_INVESTIGAR = ("🔍 <i>Investigating: checking whether there are comparable past cases, "
                       "and what happened after them.</i>")
AVISO_CURTO = "<i>Never a price prediction and never advice.</i>"


def esboco_news_impact(
    ticker: str,
    headline: str,
    date: str = "",
    move: float | None = None,
    move_note: str | None = None,
    source: str = "",
    url: str = "",
) -> str:
    """O alerta como sai no primeiro instante: o facto, e o aviso de que a análise vem a seguir.

    Assinatura deliberadamente igual à de `explain_news_impact` menos `precedents`, `horizon`,
    `materiality` e `today` — ou seja, menos exatamente aquilo que ainda não se sabe. Quem
    chamar isto e depois `explain_news_impact` com os mesmos argumentos obtém um cabeçalho
    byte a byte idêntico, e o leitor vê a mensagem crescer em vez de mudar.
    """
    return "\n".join([
        _cabecalho_noticia(ticker, headline, date, move, move_note, source, url),
        "",
        ESTADO_A_INVESTIGAR,
        AVISO_CURTO,
    ])


def _cabecalho_noticia(ticker: str, headline: str, date: str = "",
                       move: float | None = None, move_note: str | None = None,
                       source: str = "", url: str = "") -> str:
    """O cabeçalho do alerta de notícia — tudo o que se sabe ANTES da recuperação semântica.

    Extraído de `explain_news_impact` para poder ser enviado sozinho, de imediato, enquanto os
    precedentes ainda estão a ser recuperados. O texto produzido é byte a byte o mesmo de
    antes: quem lê o alerta completo não vê diferença nenhuma, e é isso que permite editar a
    mensagem sem que o cabeçalho mude debaixo dos olhos de quem já o leu.
    """
    header = (f"📰 <b>News alert for {html.escape(ticker, quote=False)}"
              f"{html.escape(_nome(ticker), quote=False)}</b>")
    if date:
        header += f" ({html.escape(date, quote=False)})"
    header += f'\n"{html.escape(_clip(headline), quote=False)}"'
    # ⚠️ DE ONDE VEIO, E COMO IR LÊ-LA. O `NewsItem` já trazia `source` e `url` da fonte, e o
    # alerta deitava-os fora: citava uma manchete sem dizer quem a publicou nem deixar
    # verificá-la. Num sistema cujo argumento é entregar a afirmação COM a evidência anexada,
    # a fonte da própria manchete é a evidência mais básica de todas.
    if source or url:
        quem = html.escape(source, quote=False) if source else "source"
        header += f'\n<a href="{html.escape(url, quote=True)}">{quem}</a>' if url else f"\n{quem}"
    # ⚠️ O QUE O PREÇO ESTÁ A FAZER, que é o facto que faltava. Até 2026-08-15 um alerta de
    # notícia falava de manchetes passadas e nunca dizia o que a acção fazia AGORA — o
    # utilizador tinha de ir ver a outro lado a única coisa que lhe permitia julgar se a
    # notícia interessava. Opcional: sem valor, o texto fica byte-igual ao de sempre.
    if move is not None and move == move:
        linha = f"Right now: <b>{move * 100:+.2f}%</b> today"
        if move_note:
            linha += f" · {html.escape(move_note, quote=False)}"
        header += f"\n{linha}"
    return header


def explain_news_impact(
    ticker: str,
    headline: str,
    precedents: list[tuple[NewsRecord, float]],
    horizon: int = 3,
    date: str = "",
    materiality: str | None = None,
    today: str = "",
    move: float | None = None,
    move_note: str | None = None,
    source: str = "",
    url: str = "",
) -> str:
    """Explicação XAI para o Gatilho 2: notícia nova + precedentes históricos semelhantes.

    Camadas: a notícia; o resumo honesto dos precedentes (INTERVALO primeiro — a média sozinha
    esconde direções mistas — com a média entre parênteses); a lista, um por linha, com o
    resultado à cabeça; nota final curta. NÃO é uma previsão (restrição §5.2).

    `materiality` (opcional, off por defeito): linha da triagem aprendida (RQ4), já composta
    por `investigator.triage.explain.materiality_line`. None ⇒ sem essa linha.
    `today` (opcional): quando dado (produção/app), cada precedente mostra a idade
    ("2y ago") — sem ele (demo/tese), o output histórico fica byte-igual.
    """
    header = _cabecalho_noticia(ticker, headline, date, move, move_note, source, url)
    if not precedents:
        out = header + "\nNo similar historical precedents found in the knowledge base."
        return f"{out}\n{materiality}" if materiality else out

    vals = _impacts(precedents, horizon)
    avg = _mean_precedent_impact(precedents, horizon)
    if vals:
        resumo = (
            f"<b>{len(precedents)} similar past headlines.</b> Their {horizon}-day move ranged "
            f"{min(vals) * 100:+.2f}% to {max(vals) * 100:+.2f}% (average {avg * 100:+.2f}%):"
        )
    else:
        resumo = (f"<b>{len(precedents)} similar past headlines.</b> "
                  f"Average {horizon}-day move: n/a:")
    lines = [header, "", resumo]
    key = str(horizon)
    for rec, score in precedents:
        imp = rec.impacts.get(key)
        imp_txt = f"{imp * 100:+.2f}%" if imp is not None and imp == imp else "n/a"
        quem = f"{html.escape(rec.ticker, quote=False)} {html.escape(rec.date, quote=False)}"
        idade = _age_label(rec.date, today) if today else ""
        if idade:
            quem += f" ({idade})"
        lines.append(
            f"▸ {imp_txt} in {horizon}d · {quem} · "
            f'"{html.escape(_clip(rec.headline), quote=False)}" (sim {score:.2f})'
        )
    # Direção dos precedentes — SEMPRE descritiva (frequência observada nos casos mostrados),
    # NUNCA preditiva: a lição do CS3 (tema ≠ direção) aplicada ao produto. Com sinal misto,
    # o aviso explícito; com sinal unânime, a contagem simples ("3 of 3 moved down").
    subiram = sum(1 for v in vals if v > 0)
    desceram = sum(1 for v in vals if v < 0)
    if subiram and desceram:
        # Direções mistas: mostrar o SPLIT (não uma média enganadora) e enquadrar como TEMA.
        lines.append(
            f"⚠ These cases moved in BOTH directions ({subiram} up, {desceram} down) — "
            "similar in TOPIC, not in direction. Context, never a forecast."
        )
    elif vals and (subiram == len(vals) or desceram == len(vals)):
        # Unânime (inclui o caso confuso: notícia positiva mas casos passados caíram) — deixar
        # explícito que estes são casos do mesmo TEMA, não uma previsão para esta notícia.
        #
        # ⚠️ E CONTAR OS DIAS, não só os casos. O impacto é medido por (empresa, dia), portanto
        # duas manchetes da mesma empresa no mesmo dia partilham o MESMO valor por construção.
        # Dizer "3 de 3 casos desceram" quando os três são o mesmo dia apresenta como
        # concordância aquilo que é uma repetição. Medido sobre os 247 alertas já entregues
        # com precedentes: em 36,8% os casos assentavam em menos dias distintos do que casos
        # exibidos, e em 11,3% eram todos do mesmo dia.
        rumo = "up" if subiram else "down"
        dias = {(rec.ticker, rec.date) for rec, _ in precedents
                if rec.impacts.get(key) is not None}
        if len(dias) < len(vals):
            plural = "s" if len(dias) != 1 else ""
            lines.append(
                f"{len(vals)} of {len(vals)} shown cases moved {rumo}, but they come from only "
                f"{len(dias)} observed day{plural} — impact is measured per company-day, so "
                "cases sharing a day share the same number. Topic-similar past cases, not a "
                "prediction for this news."
            )
        else:
            lines.append(
                f"{len(vals)} of {len(vals)} shown cases moved {rumo} — topic-similar past "
                "cases, not a prediction for this news (an observed pattern, not a forecast)."
            )
    if materiality:
        lines.append(materiality)
    lines.append(
        "<i>Observed past outcomes after similar news, not a price prediction and not advice.</i>"
    )
    return "\n".join(lines)
