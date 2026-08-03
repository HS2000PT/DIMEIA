"""As frases do painel, separadas do Streamlit para poderem ser testadas a sério.

**Porque é que isto é um módulo próprio.** A lei de desenho da v3
(`docs/design/dashboard_acceptance.md` §6.2) é:

> Todo o cartão e toda a secção abrem com uma frase que um não-especialista consegue usar.
> Nenhum número aparece antes da frase que ele sustenta.

Uma lei que só se verifica abrindo um browser não é uma lei, é uma intenção — e este
projecto já perdeu seis redesenhos a verificar coisas a olho. Com as frases aqui, puras e
sem estado, os critérios de escrita passam a testes de milissegundos que falham com um
diff legível, e o teste de proibição de vocabulário (H2: zero previsões) pode varrer
centenas de combinações sintéticas em vez de uma captura de ecrã.

**O que estas funções nunca fazem:** não vão buscar dados, não formatam HTML e não sabem
o que é o Streamlit. Recebem números e devolvem texto.
"""

from __future__ import annotations

from investigator.anomaly_detector.frequency import Exceedance
from investigator.correlation_engine.decomposition import VERDICT_SHORT

# Vocabulário proibido em qualquer frase de produto (H2). Não é uma lista de estilo: cada
# uma destas palavras transformaria uma descrição do passado numa afirmação sobre o futuro,
# que é a restrição fundadora do trabalho. O teste varre isto sobre frases geradas.
PROIBIDO = (
    "expected", "forecast", "predict", "chance of", "probability", "likely",
    "will rise", "will fall", "target", "recommend", "should buy", "should sell",
    "bullish", "bearish", "outlook", "projected",
)


# A resposta a "o que é isto?", em linguagem comum. Vive aqui, e não solta no HTML do
# cabeçalho, por duas razões: é texto de produto, logo tem de passar pelo mesmo varrimento
# de vocabulário proibido (H2) que todas as outras frases; e muda-se num sítio só.
#
# O que ela deliberadamente NÃO diz: "1,5 desvios-padrão numa janela de 20 dias". Era essa
# a versão anterior, e explicava o MECANISMO a quem tinha perguntado pela CONSEQUÊNCIA.
# Quem carrega em "o que é isto?" não está a pedir a fórmula — está a perguntar se tem de
# se importar. A segunda frase é a que faz o trabalho todo: sem ela, um leitor compara os
# 3% da Apple com os 3% da Tesla e conclui que o sistema se enganou num dos dois.
FLAG_EXPLAINER = (
    "Flagged means today's move is unusually large for this company, measured against its "
    "own recent behaviour. Each company is judged against itself, so a 3% day can be "
    "flagged for a calm stock and ordinary for a volatile one."
)


def rarity_sentence(exc: Exceedance | None, name: str = "") -> str:
    """Quão invulgar foi o dia, em palavras e sem estatística.

    O `n` vem sempre do objecto, nunca de uma constante: uma série curta tem de dizer
    "58 dias". Escrever a janela à mão seria afirmar um facto que não se mediu.
    """
    if exc is None:
        return ""
    quem = name or "It"
    n, c = exc.n, exc.count
    if c == 0:
        direccao = "fall" if exc.move < 0 else "move"
        return f"Its biggest {direccao} in {n} trading days."
    if c <= 5:
        return f"Only {c} of the last {n} trading days moved this much or more."
    if c <= 25:
        return f"{c} of the last {n} trading days moved this much or more."
    return f"An ordinary day for {quem}: most of the last {n} days moved as much or more."


def driver_sentence(decomp: dict | None) -> str:
    """O motor do movimento, **só quando surpreende**.

    Devolve "" quando o motor é a própria empresa: nesse caso o cartão já disse o nome e o
    número, e acrescentar "foi específico da empresa" é repetir o que se acabou de ler. A
    frase existe para o caso contrário — quando afinal *não* é uma história sobre esta
    empresa —, que é a informação que o detentor de longo prazo veio buscar.
    """
    if not decomp:
        return ""
    frase = VERDICT_SHORT.get(decomp.get("driver", ""), "")
    if frase and decomp.get("fallback"):
        frase += " (Beta not estimated; the split is indicative.)"
    return frase


def verdict(
    name: str,
    exc: Exceedance | None,
    decomp: dict | None,
    flagged: bool,
    market_open: bool = False,
) -> str:
    """O veredicto do cartão: uma ou duas frases, sem um único número técnico.

    É a primeira coisa que se lê e a única obrigatória. Um dia calmo tem direito a uma
    frase curta — o silêncio legível também é informação, e é literalmente o produto para
    quem só quer permissão para não fazer nada.
    """
    if not flagged:
        # Um dia calmo tem de **mostrar** que é calmo, não afirmá-lo. Um utilizador que vê
        # +3,23% ao lado da palavra "Quiet" não tem razão nenhuma para acreditar; o mesmo
        # utilizador a ver "203 dos últimos 249 dias moveram-se tanto ou mais" acredita
        # sem precisar de confiar em nós. É a diferença entre um rótulo e uma prova.
        if exc is None:
            base = f"Quiet — an ordinary day for {name}."
        elif exc.count > 25:
            base = (f"Quiet — {exc.count} of the last {exc.n} trading days "
                    f"moved as much or more.")
        else:
            # AS DUAS RÉGUAS DISCORDAM, e esconder isso seria mentir pela palavra mais
            # simpática. O detector mede contra os **20 dias anteriores**; a contagem mede
            # contra o **ano**. Uma acção num período calmo pode não ser sinalizada (z
            # abaixo do limiar) e ainda assim estar no topo do ano.
            #
            # Medido ao vivo a 2026-08-03: MSFT +4,82%, z +1,11 (não sinalizada) e apenas
            # **5 dos 249 dias** se moveram tanto. A versão anterior escrevia "an ordinary
            # day for Microsoft" — sobre um movimento no top 2% do ano. Dizer as duas
            # coisas é mais comprido e é a verdade: o dia é normal *para as últimas
            # semanas* e raro *para o ano*, e é o leitor que decide o que fazer com isso.
            quantos = ("Only 1 of the last" if exc.count == 1
                       else f"only {exc.count} of the last")
            base = (f"Quiet by its recent norm — but {quantos} {exc.n} trading days "
                    f"moved this much.")
            if exc.count == 0:
                base = ("Quiet by its recent norm — but no other day in the last "
                        f"{exc.n} trading days moved this much.")
        return f"{base} So far today." if market_open else base

    partes = [rarity_sentence(exc, name) or f"{name} stood out today."]
    motor = driver_sentence(decomp)
    if motor:
        partes.append(motor)
    if market_open:
        partes.append("The session is not over.")
    return " ".join(partes)


def precedent_framing(up: int, down: int) -> str:
    """A moldura tema ≠ direcção, que o critério H3 torna **obrigatória** e nunca opcional.

    É a lição do Estudo de Caso 3 aplicada ao produto: a recuperação semântica capta o
    **tema**, não a direcção. Uma manchete positiva recupera com toda a naturalidade um
    grupo de casos cujo desfecho médio foi negativo — não porque o método falhou, mas
    porque "concorrência em chips de IA" é o mesmo assunto quer a notícia seja boa ou má.

    Por isso não se mostra a média como número de destaque: uma média de −1,97% sobre casos
    que foram a +4% e a −8% descreve um número que nunca aconteceu, e lê-se como se fosse
    o que vem aí. A repartição observada não tem esse problema.
    """
    if up and down:
        return (f"These moved in both directions ({up} up, {down} down) — "
                f"similar in topic, not in direction.")
    if up or down:
        n, rumo = (up, "up") if up else (down, "down")
        return (f"All {n} of these moved {rumo} — topic-similar past cases, "
                f"and not a statement about this one.")
    return "None of these cases has a measured outcome yet."


def gloss_z(z: float) -> str:
    """O z-score com a glosa que o torna legível (critério V4).

    Nunca devolve o número nu. O z é a estatística com que o detector dispara e por isso
    tem de continuar visível e rastreável, mas sozinho não diz nada a quem não o conhece.
    """
    return f"z {z:+.2f} vs 20-day norm"


def sparkline_svg(closes, colour: str, width: int = 96, height: int = 22) -> str:
    """Uma linha de preço minúscula, em SVG inline.

    SVG e não plotly: dez figuras plotly numa grelha seriam de longe a coisa mais lenta da
    página, e o critério P1 dá cinco segundos ao arranque a frio. Isto é uma string.
    """
    valores = [float(v) for v in closes if v == v]
    if len(valores) < 2:
        return ""
    baixo, alto = min(valores), max(valores)
    span = (alto - baixo) or 1.0  # série plana não pode dividir por zero
    passo = width / (len(valores) - 1)
    pontos = " ".join(
        f"{i * passo:.1f},{height - (v - baixo) / span * (height - 2) - 1:.1f}"
        for i, v in enumerate(valores))
    return (f'<svg class="spark" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" aria-hidden="true">'
            f'<polyline points="{pontos}" fill="none" stroke="{colour}" '
            f'stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round"/></svg>')


def card_html(
    ticker: str,
    name: str,
    move: float,
    icone: str,
    cor: str,
    frase: str,
    flagged: bool,
    chips: list[str],
    logo: str = "",
    spark: str = "",
) -> str:
    """Um cartão. **O veredicto vem sempre antes de qualquer número** (critério V2).

    A ordem no HTML não é um detalhe de implementação: é a lei de desenho, e por isso é
    verificada por um teste que compara as posições no texto emitido. Um cartão calmo não
    leva sparkline nem chips — o vazio é o sinal.
    """
    classe = "card--flagged" if flagged else "card--quiet"
    # A pílula sai da linha do topo. Estava entre o ticker e o número grande, a disputar
    # uma linha que já levava logótipo, nome e percentagem — e o nome, único elemento sem
    # largura própria, era o que cedia: "JPMorgan Chase" truncava para dar espaço à
    # palavra `UNUSUAL`. Numa linha só dela ninguém compete, e o nome da empresa nunca
    # abrevia. A palavra continua lá, que é o que o critério V3 exige (quatro canais
    # redundantes, nunca só cor) — mudou de sítio, não de existência.
    pilula = ('<div class="card-state"><span class="pill">UNUSUAL</span></div>'
              if flagged else "")
    chips_html = ("".join(f"<span>{c}</span>" for c in chips)
                  if flagged and chips else "")
    return (
        f'<a class="card {classe}" href="?t={ticker}" target="_self">'
        f'<div class="card-top">{logo}'
        f'<span class="card-name">{name}</span>'
        f'<span class="card-tick num">{ticker}</span>'
        f'<span class="card-move num" style="color:{cor}">{icone} {move * 100:+.2f}%</span>'
        f"</div>"
        f"{pilula}"
        f'<div class="verdict">{frase}</div>'
        f"{spark}"
        f'{f"<div class=chips>{chips_html}</div>" if chips_html else ""}'
        f"</a>"
    )
