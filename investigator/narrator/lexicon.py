"""Vocabulário fechado do narrador — a lista do que PODE ser dito.

**Porque é uma allowlist e não uma blocklist.** A primeira versão desta guarda proibia
padrões ("will rise", "recommend", "bullish"). Um red team de 3 adversários independentes
produziu 29 furos REPRODUZIDOS, quase todos da mesma família: linguagem preditiva fora da
lista. `poised to rally`, `likely to rebound`, `due for a bounce`, `attractive entry point`,
`Buy the dip`, `will climb`, `not bearish` — todos passavam. Uma blocklist de linguagem
natural é uma corrida que se perde sempre: o espaço de paráfrases é infinito, a lista é finita.

A inversão resolve a assimetria. O narrador não precisa de escrever prosa livre: precisa de
recontar 6 a 10 factos. Um vocabulário fechado de ~250 palavras neutras basta para isso, e
qualquer palavra fora dele — incluindo toda a paráfrase preditiva que ainda não imaginámos —
é rejeitada por omissão. Deixa de ser preciso adivinhar como se diz "vai subir".

**Verbos direcionais estão FORA de propósito.** `gained`, `fell`, `rose`, `climbed`, `dropped`
não constam. O red team mostrou porquê: com números sem sinal, "AMD gained 8.50%" passava a
guarda quando o motor calculou −8,50% — a inversão de direção mais consequente possível.
A direção passa a ser carregada pelo SINAL do número ("-8.50%"), que é verificável
mecanicamente, e não por um verbo, que não é.

Custo assumido e medido: o texto fica mais clínico ("AMD moved -8.50%" em vez de "AMD fell
8.5%"). É o preço da verificabilidade, e o arnês reporta a taxa de rejeição que ele provoca.
"""

from __future__ import annotations

# ── Palavras funcionais e de ligação ─────────────────────────────────────────
_FUNCTION = """
a an and as at be been by for from had has have in into is it its of on or over than that
the their there these this those to was were with within after before during between
also both each no not only other same so some such then when which while who whose
"""

# ── Substantivos e adjetivos neutros do domínio ──────────────────────────────
# Descrevem o que os motores calculam. Nada avaliativo ("cheap", "strong", "attractive"),
# nada temporal-futuro ("outlook", "upside", "momentum" como promessa).
_DOMAIN = """
alert alerts case cases company companys company-specific close context data date dates day
days detection deviation deviations evidence event events fact facts headline headlines
history horizon impact impacts information level levels market markets mean measure measured
move moved movement movements news norm number numbers observation observations outcome
outcomes past pattern patterns percent percentage period point points precedent precedents
price prices range ratio record records reference report reported result results score scores
sector sectors session sessions share shares similar similarity size split splits standard
statistic statistics stock stocks summary system threshold thresholds ticker time times today
trading typical value values volatility window windows year years z-score
beta estimate estimated estimates indicative triage learned model chance
"""

# ── Verbos neutros (relato, nunca juízo nem direção) ─────────────────────────
_VERBS = """
appear appeared appears are be been being came come contain contained contains cover covered
covers describe described describes detect detected detects differ differed differs
flag flagged flags give gives given include included includes involve involved involves
is list listed lists mark marked marks match matched matches
measure measured measures move moved moves note noted notes observe observed observes
occur occurred occurs read reads record recorded records refer referred refers
relate related relates remain remained remains report reported reports
represent represented represents return returned returns say said says see seen shift shifted
show showed shown shows sit sits stand stood stands state stated states
was were
"""

# ── Quantificadores e comparadores neutros ───────────────────────────────────
_QUANTIFIERS = """
above all almost approximately about around at-least below beyond compared different equal
exactly fewer first following four here how however identical individual last less lower
many more most much nine one previous rest second several seven six ten third three total
two under up-to versus vs whereas whole
mostly largely mainly primarily
"""

# Palavras neutras que o arnês ao vivo mostrou serem usadas legitimamente e estavam a causar
# FALSOS positivos (2026-07-29). Cada uma verificada como não-direcional e não-preditiva —
# o léxico cresce por medição, não por antecipação, e nunca com verbos de direção ou juízo.
_MEASURED_NEUTRAL = """
activity along another available based conditions distinct featuring given
label labels line lines named note notes present recent relative
analysis dominant scale set showing shown side single source specific type types
using where whether
"""

# ── Rótulos que a evidência usa e que o texto pode nomear ────────────────────
_LABELS = """
january february march april may june july august september october november december
monday tuesday wednesday thursday friday
"""

VOCABULARY: frozenset[str] = frozenset(
    w for chunk in (_FUNCTION, _DOMAIN, _VERBS, _QUANTIFIERS, _MEASURED_NEUTRAL, _LABELS)
    for w in chunk.split()
)

# ── Frases de isenção (disclaimers) permitidas VERBATIM ──────────────────────
# Contêm palavras fora do vocabulário ("forecast", "prediction", "advice") de propósito: é a
# linguagem honesta do produto. São retiradas do texto ANTES da verificação de vocabulário,
# por isso essas palavras nunca podem ser usadas fora destas frases exatas. Resolve também os
# falsos-negativos que o red team encontrou ("isn't a forecast" era rejeitado).
ALLOWED_DISCLAIMERS: tuple[str, ...] = (
    "observed history, not a forecast",
    "observed history and not a forecast",
    "this is not a forecast",
    "this is not a prediction",
    "not a forecast",
    "not a prediction",
    "not investment advice",
    "not advice",
    "evidence, not a forecast",
    "evidence and not a forecast",
    "an observed move, not advice",
    "past outcomes, not a forecast",
    "no forecast is implied",
    "no prediction is implied",
)

# ── Frases de atribuição permitidas, validadas CONTRA a evidência ────────────
# O red team mostrou que o texto podia dizer "mostly market-driven" quando o motor concluiu
# driver="company". Estas são as únicas formas de afirmar a fonte dominante, e cada uma é
# verificada contra `evidence.driver` — ver core._check_attribution.
DRIVER_PHRASES: dict[str, tuple[str, ...]] = {
    "market": ("mostly market", "largely market", "mainly market", "primarily market"),
    "sector": ("mostly sector", "largely sector", "mainly sector", "primarily sector"),
    "company": ("mostly company-specific", "largely company-specific",
                "mainly company-specific", "primarily company-specific"),
}
