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
        base = f"Quiet — an ordinary day for {name}."
        return f"{base} So far today." if market_open else base

    partes = [rarity_sentence(exc, name) or f"{name} stood out today."]
    motor = driver_sentence(decomp)
    if motor:
        partes.append(motor)
    if market_open:
        partes.append("The session is not over.")
    return " ".join(partes)


def gloss_z(z: float) -> str:
    """O z-score com a glosa que o torna legível (critério V4).

    Nunca devolve o número nu. O z é a estatística com que o detector dispara e por isso
    tem de continuar visível e rastreável, mas sozinho não diz nada a quem não o conhece.
    """
    return f"z {z:+.2f} vs 20-day norm"
