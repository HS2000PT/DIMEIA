"""Vistas da v4 — a lógica pura, separada do Streamlit.

Está num módulo próprio pela mesma razão que a v3 tem o `verdict.py`: uma lei que só se
verifica abrindo um browser é uma intenção, não um critério. Aqui é tudo função pura sobre
dicionários, e os testes verificam-na sem levantar servidor nenhum.

O que **não** vive aqui: nada que toque em Streamlit, rede ou disco.
"""

from __future__ import annotations

# Vocabulário proibido pela regra H2 (zero previsão). Varrido por teste sobre TODAS as frases
# que estas funções sabem produzir, e não só sobre um exemplo — foi assim que a v3 apanhou
# "price target" dentro de "No price targets".
PROIBIDO = (
    "will rise", "will fall", "will go", "expected to", "expect ", "forecast", "predict",
    "price target", "should buy", "should sell", "recommend", "guaranteed", "projection",
    "outlook for", "set to ", "poised to",
)

NOMES_FACTOR = {
    "market": "the market as a whole",
    "sector": "its sector",
    "company": "the company itself",
}


def rotulo_raridade(count: int | None, n: int | None) -> str:
    """A raridade em palavras. Contagem empírica, nunca probabilidade.

    Converter um z-score numa probabilidade exigiria normalidade, e os retornos têm caudas
    pesadas — o valor estaria errado exactamente nos dias que interessam.
    """
    if not n or count is None:
        return "Not enough history to say."
    if count == 0:
        return f"No other day in the last {n} trading days moved this much."
    if count == 1:
        return f"Only 1 of the last {n} trading days moved this much or more."
    return f"{count} of the last {n} trading days moved this much or more."


def rotulo_atribuicao(decomp: dict | None, move: float) -> str:
    """Quem moveu a acção, em palavras.

    O motor é a maior componente **com o mesmo sinal** do total, nunca a maior em módulo:
    medido, a NVDA subiu +0,25% com o sector a −1,54%, e dizer "foi o sector" seria falso.
    As componentes que puxaram ao contrário são ditas, não descartadas — uma acção que subiu
    enquanto o sector caía é precisamente o caso que o leitor deve conhecer.
    """
    if not decomp:
        return "Attribution unavailable for this name today."
    motor = decomp.get("driver")
    frase = f"Mostly {NOMES_FACTOR.get(motor, motor)}."
    # Ordenar por magnitude: com duas componentes a puxar ao contrário, nomear a primeira da
    # lista fixa dava a MENOR. Medido na NVDA: setor +0,03% e empresa +0,09% opunham-se ambos
    # a um total de −0,10%, e o texto anunciava só o setor.
    contra = sorted(
        (k for k in ("market", "sector", "company")
         if decomp.get(k) is not None and decomp[k] * move < 0),
        key=lambda k: -abs(decomp[k]),
    )
    if len(contra) == 1:
        frase += f" {NOMES_FACTOR[contra[0]].capitalize()} pulled the other way."
    elif len(contra) > 1:
        nomes = " and ".join(NOMES_FACTOR[k] for k in contra)
        frase += f" {nomes.capitalize()} pulled the other way."
    return frase


def linhas_decomposicao(decomp: dict | None, move: float) -> list[tuple[str, float, bool]]:
    """(rótulo, contribuição, é-o-motor) — as três parcelas que somam ao movimento observado.

    Somam por construção, e é isso que permite mostrá-las sem risco de uma linha que não fecha.
    """
    if not decomp:
        return []
    motor = decomp.get("driver")
    return [
        (NOMES_FACTOR[k].capitalize(), float(decomp.get(k) or 0.0), k == motor)
        for k in ("market", "sector", "company")
    ]


# Porque é que cada gate silenciou um ticker, em linguagem de quem lê e não de quem programou.
# É a peça que nenhum produto comercial mostra: o que foi DESCARTADO e porquê.
RAZOES_GATE = {
    "no_news": ("No news today", "The source returned nothing for this company."),
    "none_relevant": ("Nothing about the company",
                      "Headlines arrived, but none actually mentioned this company."),
    "stale": ("Old news", "The most recent story is outside the freshness window."),
    "weak_precedent": ("No close precedent",
                       "Nothing similar enough in the case base to be worth showing."),
    "triage_suppressed": ("Judged immaterial",
                          "The triage model scored it below the bar for an alert."),
    "error": ("Could not check", "A data source failed. Nothing is being hidden."),
    "alerted": ("Alert sent", "Cleared every gate and went to the channel."),
}


def explicar_silencio(gate: str, detalhe: str = "") -> tuple[str, str]:
    """(título, explicação) para um ticker que não gerou alerta.

    O detalhe técnico (a margem que faltou) vai por inteiro, porque é o que torna isto
    verificável em vez de tranquilizador: "melhor semelhança 0,42 < chão 0,45" diz ao leitor
    exactamente **por quanto** o sistema se calou.
    """
    titulo, texto = RAZOES_GATE.get(gate, ("Not alerted", "No alert was sent for this name."))
    if detalhe:
        texto = f"{texto} ({detalhe})"
    return titulo, texto


# Negações que INVERTEM o sentido do termo proibido. Sem isto, a frase "not a forecast" —
# que é exactamente a moldura de honestidade que este produto usa — seria acusada de prever.
_NEGACOES = (
    "not a ", "not an ", "never ", "no ", "isn't a ", "is not a ", "rather than a ",
    "rather than ", "without ", "cannot ", "does not ", "doesn't ",
)


def contem_previsao(texto: str) -> bool:
    """H2, em forma executável: nenhuma frase do produto pode prever.

    ⚠️ **Reconhece negações, e a razão é histórica.** Este projecto já foi mordido três vezes
    pela mesma classe de defeito: uma lista de palavras proibidas que não olha para o contexto
    acusa a própria frase que existe para ser honesta.

    1. No *red team* do narrador (sessão 42), uma blocklist perdeu contra paráfrases e o desenho
       foi invertido para **allowlist**.
    2. No portão de promoção da v3, a verificação de H2 acusou *"price target"* dentro de
       **"No price targets"**.
    3. Aqui: a moldura *"an observed pattern, not a forecast"* — que é a defesa do H2 — seria
       marcada como violação por conter "forecast".

    Por isso um termo proibido só conta quando **não** vem precedido de negação. Continua a ser
    uma blocklist, e continua a ser frágil contra paráfrases livres; aguenta porque o conjunto
    de frases que este módulo produz é **fechado e varrido por teste**, ao contrário do texto
    gerado por um modelo, onde a lição foi ter de usar allowlist.
    """
    b = " " + " ".join(texto.lower().split()) + " "
    for termo in PROIBIDO:
        inicio = 0
        while (i := b.find(termo, inicio)) != -1:
            antes = b[:i]
            if not any(antes.endswith(neg) for neg in _NEGACOES):
                return True
            inicio = i + 1
    return False


def moldura_precedentes(subiram: int, desceram: int) -> str:
    """H3: tema ≠ direcção, sempre, e nunca como uma frase que se pode saltar.

    É o ponto que o próprio autor leu como incoerência nos seus alertas: notícia negativa,
    precedentes a subir. Não é defeito — é o resultado medido do CS3 (consistência de direcção
    0,708 contra um chão de acaso de 0,688). Se a moldura não chega a quem escreveu a tese,
    não chega a ninguém, portanto tem de ser dita em números e não em adjectivos.
    """
    total = subiram + desceram
    if total == 0:
        return "No comparable past cases with a measured outcome yet."
    if subiram and desceram:
        return (f"Of {total} similar past cases, {subiram} went up and {desceram} went down. "
                "Similar in topic is not similar in direction.")
    lado = "up" if subiram else "down"
    return (f"All {total} similar past cases moved {lado} — an observed pattern in this small "
            "set, not a forecast. Similar in topic is not similar in direction.")
