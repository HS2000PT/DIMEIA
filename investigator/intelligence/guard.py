"""Guarda de ancoragem para texto generativo de forma livre.

## Dois níveis de garantia, e a diferença está declarada de propósito

Este projecto já tem uma guarda de geração: `investigator/narrator/core.py`. Essa é uma
**allowlist de vocabulário fechado** (~250 palavras), e a razão está registada: um red team de
três adversários abriu 29 furos numa blocklist, e a lição foi estrutural — *o espaço de
paráfrases é infinito e a lista é finita*.

Um relatório de seis secções e um analista conversacional **não cabem** em 250 palavras. Se
aplicasse aqui a mesma allowlist, ou o produto não escrevia nada, ou eu alargava o léxico até
deixar de ser allowlist e passar a ser blocklist com outro nome. Nenhuma é honesta.

Há portanto dois níveis, e o produto usa-os em sítios diferentes por **risco**, não por
conveniência:

| | Alerta (`narrator/`) | Relatório e analista (aqui) |
|---|---|---|
| Como chega | **empurrado** (Telegram, sem pedir) | **puxado** (o utilizador clica) |
| Evidência ao lado | não | sim, na mesma página |
| Números | conjunto fechado global | **conjunto fechado POR FRASE** |
| Direcção | obrigatória | obrigatória |
| Vocabulário | allowlist fechada | blocklist + disclaimers em allowlist |
| Ancoragem | n/a | **cada frase com número cita o facto** |
| Garantia linguística | absoluta | **mais fraca, e medida** |

## O que o red team mudou nesta guarda

Seis lentes adversárias correram **114 ataques** contra a primeira versão e reproduziram 21.
Três eram críticos e partilhavam **uma só causa**: o conjunto numérico era **global**. Qualquer
número do pacote podia ser colado a qualquer afirmação, o que permitia:

- citar `[f5]` e usar o número de `f9`;
- restituir um retorno como se fosse um z-score (tipos não modelados);
- inverter a direcção usando o número de sinal oposto de outro facto;
- apresentar o desfecho passado de um precedente como o movimento de hoje.

A correcção não é mais uma regra: é **ligar cada número ao facto que a frase cita**. Uma
frase que cita `[f5]` só pode usar números de `f5`. É a diferença entre "este número existe
algures" e "este número é deste facto" — e era a segunda que o produto sempre prometeu.

Fecharam-se ainda, do mesmo relatório: a padding de precisão que **cunhava** números (2.65
arredondado a zero casas metia "3" no vocabulário), os números por extenso, a janela de
negação explorável, a máscara de horas que apagava qualquer `dd:dd`, e a inversão de pares
ordenados (`8 up, 4 down` reescrito como `4 up, 8 down`, com ambos os números legítimos).

**O que continua em aberto está escrito em `RESIDUAL`, no fim deste ficheiro.** Uma garantia
mais fraca que foi medida vale mais numa tese do que uma garantia forte que foi afirmada.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from investigator.intelligence.context import Bundle

_INVISIBLE = dict.fromkeys(
    [0x200B, 0x200C, 0x200D, 0x00AD, 0x2060, 0xFEFF, 0x180E, 0x200E, 0x200F], None)

_NUM_RE = re.compile(r"[+-]?\d+(?:[.,]\d+)?")
_ANCHOR_RE = re.compile(r"\[(f\d+)\]")
_DQUOTE_RE = re.compile(r'"[^"]*"')

# ── Linguagem proibida ────────────────────────────────────────────────────────
# É uma blocklist e, ao contrário do narrador, aqui ela É a defesa linguística — daí ser
# deliberadamente larga, daí ser MEDIDA, e daí o residual estar declarado no fim.
_FORBIDDEN: tuple[tuple[str, str], ...] = (
    # previsão
    (r"\bwill\s+\w*\s*(?:rise|fall|climb|drop|jump|surge|plunge|rally|recover|reach|hit|"
     r"continue|remain|keep|go)\b", "prevê o preço"),
    (r"\b(?:expect|anticipate|forecast|predict|project|foresee)(?:s|ed|ing|ation|ations)?\b",
     "prevê"),
    (r"\b(?:likely|unlikely|probably|possibly|poised|set|primed|positioned|due|on\s+track|"
     r"ready)\s+to\b", "prevê"),
    (r"\b(?:should|could|may|might|would)\s+\w*\s*(?:rise|fall|climb|drop|rebound|recover|"
     r"continue|outperform|underperform|extend|resume|reverse)\b", "prevê"),
    (r"\b(?:going|expected|likely)\s+to\s+\w+\b", "prevê"),
    (r"\bdue\s+for\s+a\b", "prevê"),
    (r"\b(?:upside|downside)\b", "prevê"),
    (r"\bprice\s+targets?\b", "prevê"),
    (r"\b(?:bullish|bearish|overbought|oversold|undervalued|overvalued)\b",
     "toma posição direccional"),
    (r"\b(?:suggests?|implies|indicates?|points?\s+to|signals?|hints?)\s+(?:that\s+)?"
     r"(?:further|more|continued|additional|a\s+further)\b", "prevê"),
    (r"\bmomentum\b", "prevê"),
    (r"\bnext\s+(?:week|month|session|day|quarter)\b", "prevê"),
    (r"\bin\s+the\s+(?:coming|next)\s+\w+\b", "prevê"),
    (r"\btend(?:s|ed)?\s+to\s+\w+\b", "generaliza para o futuro"),
    (r"\bhistorically\s+(?:leads?|precedes?|results?|followed\s+by)\b", "prevê por analogia"),
    (r"\bevery\s+(?:previous\s+)?time\b", "prevê por analogia"),
    # conselho
    (r"\b(?:buy|sell|hold|short|accumulate|trim|add|exit|enter|avoid)\b", "aconselha"),
    (r"\b(?:recommend|advise|suggest)(?:s|ed|ing)?\s+(?:that\s+)?(?:you|investors|buying|"
     r"selling|holding|caution)\b", "aconselha"),
    (r"\b(?:entry|exit)\s+point\b", "aconselha"),
    (r"\bworth\s+(?:buying|selling|holding|considering|watching|a\s+look)\b", "aconselha"),
    (r"\b(?:opportunit|attractive|cheap|expensive|compelling)\w*\b", "aconselha"),
    (r"\btake\s+profits?\b", "aconselha"),
    (r"\bstop[-\s]loss\b", "aconselha"),
    (r"\b(?:investors|holders|traders|you)\s+(?:may|might|should|will)\s+(?:wish|want|need)\b",
     "aconselha"),
    (r"\bdeserves?\s+(?:attention|a\s+look|consideration)\b", "aconselha"),
    (r"\bkeep\s+an\s+eye\b", "aconselha"),
    (r"\brisk(?:y|ier)?\s+(?:for|to)\s+(?:investors|holders|you)\b", "aconselha"),
    # causa afirmada (o sistema mede coincidência temporal, nunca causa)
    (r"\b(?:caused|causing|causes)\b", "afirma causa"),
    (r"\b(?:because\s+of|due\s+to|as\s+a\s+result\s+of|thanks\s+to|owing\s+to|on\s+the\s+back"
     r"\s+of|amid|amidst|following\s+the\s+news)\b", "afirma causa"),
    (r"\b(?:drove|driven\s+by\s+(?:the\s+)?(?:news|headline|report|announcement)|drives?)\b",
     "afirma causa"),
    (r"\b(?:triggered|sparked|prompted|fuell?ed|spurred|ignited|set\s+off)\b", "afirma causa"),
    (r"\b(?:sent|pushed|lifted|dragged|weighed\s+on|boosted|hurt|hit)\s+(?:the\s+)?"
     r"(?:shares?|stock|price)\b", "afirma causa"),
    (r"\bin\s+(?:response|reaction)\s+to\b", "afirma causa"),
    (r"\b(?:led\s+to|resulted\s+in|explains?\s+the\s+move|responsible\s+for)\b",
     "afirma causa"),
    (r"\breact(?:ed|ing|ion)\s+to\b", "afirma causa"),
    (r"\bafter\s+(?:the\s+)?(?:news|announcement|report|headline)\b", "afirma causa"),
)
_FORBIDDEN_C = tuple((re.compile(p, re.I), why) for p, why in _FORBIDDEN)

# ── Ressalvas honestas: ALLOWLIST, não detecção de negação ────────────────────
#
# ⚠️ A primeira versão usava uma janela de negação de 40 caracteres. O red team mostrou que
# isso **desliga a blocklist**: basta pôr um "no" perto para qualquer previsão passar. Uma
# heurística de negação é uma superfície de ataque, não uma defesa.
#
# A substituição é o padrão que o narrador já tinha provado: as frases honestas que o produto
# precisa de escrever são POUCAS e CONHECIDAS. Ficam numa lista fechada, retiram-se do texto
# antes da verificação, e tudo o resto é julgado sem excepções.
ALLOWED_DISCLAIMERS = (
    "observed history, not a forecast",
    "measured history and computed statistics only",
    "this report states measured history and computed statistics only",
    "it contains no forecast",
    "contains no forecast",
    "this is not a forecast",
    "not a forecast",
    "this is not advice",
    "not investment advice",
    "no measured causal link",
    "temporal proximity only",
    "the system does not measure causation between news and price",
    "does not measure causation",
    "this estimates whether the market reacts, never which way",
    "never which way",
    "retrieval matches theme, not direction",
    "measured outcomes, not a forecast",
    "with no forecast",
    "and no forecast",
)

# Frases que o gerador PODE usar para ligar acontecimentos no tempo. Existem para haver
# alternativa: proibir sem oferecer substituto produz texto que a guarda rejeita sempre.
TEMPORAL_PHRASES = (
    "coincided with", "was published shortly before", "was published shortly after",
    "appeared around the same time as", "preceded", "followed",
    "temporal proximity only", "no measured causal link",
)

# ── Números por extenso ───────────────────────────────────────────────────────
# O red team escreveu "up four percent" e passou: `_NUM_RE` só vê dígitos. Só se verificam
# quando seguidos de UNIDADE — "one of the names" é prosa legítima, "four percent" é uma
# quantidade e tem de estar na evidência.
_WORD_NUM = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
}
_UNITS = r"(?:percent|per\s+cent|percentage\s+points?|points?|times|dollars?|basis\s+points?)"
_WORDNUM_RE = re.compile(
    r"\b(" + "|".join(_WORD_NUM) + r")\s+(?:and\s+a\s+half\s+)?" + _UNITS + r"\b", re.I)

# Pares ordenados: `8 up, 4 down` reescrito como `4 up, 8 down` usa dois números legítimos e
# inverte o veredicto do dia inteiro. Números soltos não sabem de que lado são.
_PAIR_RE = re.compile(
    r"(\d+)\s+(?:names?\s+)?(?:were\s+|that\s+)?(up|down|advanced|declined|higher|lower|"
     r"gainers?|losers?|rose|fell)\b", re.I)
_UPWORDS = {"up", "advanced", "higher", "gainer", "gainers", "rose"}


@dataclass(frozen=True)
class GroundingReport:
    ok: bool
    ungrounded_numbers: list[str] = field(default_factory=list)
    forbidden: list[str] = field(default_factory=list)
    unknown_anchors: list[str] = field(default_factory=list)
    unanchored_sections: list[str] = field(default_factory=list)
    bad_pairs: list[str] = field(default_factory=list)
    anchors_used: list[str] = field(default_factory=list)

    @property
    def violations(self) -> list[str]:
        out = [f"número não ligado ao facto citado: {n}" for n in self.ungrounded_numbers]
        for v in self.forbidden:
            expr, _, why = v.partition("|")
            out.append(f"linguagem proibida ({why}): {expr}")
        out += [f"âncora inexistente: {a}" for a in self.unknown_anchors]
        out += [f"afirmação sem âncora: {s}" for s in self.unanchored_sections]
        out += [f"par ordenado invertido: {p}" for p in self.bad_pairs]
        return out


def normalize(text: str) -> str:
    out = unicodedata.normalize("NFKC", text).translate(_INVISIBLE)
    return out.replace("“", '"').replace("”", '"')


def _numbers_of(value, out: set[str]) -> None:
    """Formas em que UM valor pode aparecer.

    ⚠️ **Sem padding de precisão.** A primeira versão gerava o valor a 0, 1, 2 e 3 casas para
    tolerar formatações diferentes. O red team mostrou que isso **cunha números**: 2.65 a zero
    casas produz "3", e "3" passava a ser citável como se um motor o tivesse calculado.
    Tolerar formatação não pode custar inventar quantidades.
    """
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int | float):
        v = float(value)
        if v != v:  # NaN
            return
        forms = {f"{v:g}", f"{v:.1f}", f"{v:.2f}", f"{v:.3f}".rstrip("0").rstrip(".")}
        if v.is_integer():
            forms.add(str(int(v)))
        for f in forms:
            out.add(f)
            out.add(f.lstrip("+"))
            if not f.startswith("-"):
                out.add(f"+{f}")
        return
    if isinstance(value, str):
        for tok in _NUM_RE.findall(value):
            out.add(tok)
            out.add(tok.lstrip("+"))
            if not tok.startswith(("-", "+")):
                out.add(f"+{tok}")
        return
    if isinstance(value, list | tuple):
        for v in value:
            _numbers_of(v, out)
    elif isinstance(value, dict):
        for v in value.values():
            _numbers_of(v, out)


def _fact_numbers(bundle: Bundle, fid: str) -> set[str]:
    """Os números que UM facto autoriza — o seu valor e o seu detalhe, mais nada."""
    f = bundle.by_id(fid)
    if f is None:
        return set()
    out: set[str] = set()
    _numbers_of(f.value, out)
    for v in f.detail.values():
        _numbers_of(v, out)
    return out


def _split_sentences(text: str) -> list[str]:
    """Frases, para o âmbito numérico ser por frase e não pelo documento inteiro.

    Divide em `.`/`?`/`!` seguidos de espaço e maiúscula, e em quebras de linha. Não parte em
    `+4.47%` nem em `U.S.` porque a casa decimal e a sigla não são seguidas de maiúscula com
    espaço. Um divisor imperfeito só junta duas frases — e juntar é o lado seguro, porque
    alarga o âmbito de quem cita, nunca o de quem não cita.
    """
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"])|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def _mask_exempt(text: str, bundle: Bundle) -> str:
    """Retira do âmbito o que contém dígitos e não é uma afirmação nossa.

    Três classes, cada uma por um falso positivo real:
    - **âncoras** `[f12]` — identificador, não quantidade;
    - **datas ISO e horas COM fuso** — "down 28%" passava por causa de "2026-07-28";
    - **citações verbatim** de manchetes — o número é da fonte, não nosso.

    ⚠️ A máscara de horas era `\\d{1,2}:\\d{2}` sem contexto, e o red team escreveu
    `"changed hands at 92:50 per share"` — um preço fabricado invisível à verificação. Agora
    só isenta o que tem marca horária a seguir.
    """
    out = _ANCHOR_RE.sub(" ANCHOR ", text)
    out = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", " DATE ", out)
    out = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:UTC|GMT|ET|EST|EDT|am|pm|AM|PM)\b",
                 " TIME ", out)

    quotable: list[str] = []
    for f in bundle.facts:
        if f.kind in {"headline", "precedent"}:
            raw_h = str(f.detail.get("headline") or "")
            if raw_h:
                quotable.append(raw_h)
                quotable.append(raw_h.replace('"', "'").replace("“", "'").replace("”", "'"))
            quotable.append(str(f.value))
    for m in _DQUOTE_RE.finditer(out):
        inner = m.group(0)[1:-1].strip()
        if inner and any(inner in q for q in quotable):
            out = out.replace(m.group(0), " QUOTE ")
    return out


def _strip_disclaimers(low: str) -> str:
    for d in sorted(ALLOWED_DISCLAIMERS, key=len, reverse=True):
        low = low.replace(d, " ")
    return low


def _claims_something(para: str, tickers: set[str]) -> bool:
    """O parágrafo afirma algo verificável sobre o mercado?

    A âncora existe para que nenhuma afirmação factual chegue ao ecrã sem a evidência ao lado.
    Um parágrafo que não afirma nada verificável não tem o que citar, e exigir-lhe uma âncora
    produziria citações decorativas — que ensinam o leitor a não clicar nelas.

    ⚠️ Sem limite mínimo de comprimento: o red team passou afirmações curtas ("XOM: +4.47%.")
    por baixo do corte de 40 caracteres que a primeira versão tinha.
    """
    if re.search(r"\d", para) or _WORDNUM_RE.search(para):
        return True
    upper = para.upper()
    if any(re.search(rf"\b{re.escape(t)}\b", upper) for t in tickers):
        return True
    # Afirmações sem número nem ticker, mas com verbo de mercado, continuam a ser afirmações.
    return bool(re.search(r"\b(moved|rose|fell|declined|advanced|stood out|flagged|"
                          r"outperformed|underperformed)\b", para, re.I))


def check_grounding(text: str, bundle: Bundle,
                    require_anchors: bool = True) -> GroundingReport:
    """Decide se `text` está ancorado em `bundle`. Puro, determinístico, conservador.

    Conservador quer dizer: em dúvida, rejeita. Rejeitar texto fiel custa cair no resumo
    determinístico; aceitar texto infiel custa uma afirmação falsa no ecrã com a nossa
    assinatura. Não são comparáveis.
    """
    raw = normalize(text)

    used = _ANCHOR_RE.findall(raw)
    known = {f.fid for f in bundle.facts}
    unknown = sorted({a for a in used if a not in known})

    tickers = {str(f.detail.get("ticker") or "").upper() for f in bundle.facts}
    tickers |= {bundle.subject.upper()}
    tickers.discard("")

    ungrounded: list[str] = []
    unanchored: list[str] = []

    for sent in _split_sentences(raw):
        anchors = _ANCHOR_RE.findall(sent)
        scope = _mask_exempt(sent, bundle)
        low_scope = _strip_disclaimers(scope.lower())

        nums = _NUM_RE.findall(low_scope)
        words = [_WORD_NUM[m.group(1).lower()] for m in _WORDNUM_RE.finditer(low_scope)]

        if not nums and not words:
            if require_anchors and not anchors and _claims_something(sent, tickers):
                unanchored.append(sent[:60])
            continue

        if not anchors:
            # Uma quantidade sem âncora não é verificável, e é exactamente o que o produto
            # promete que não acontece.
            unanchored.append(sent[:60])
            continue

        # ⚠️ O CONJUNTO É A UNIÃO DOS FACTOS QUE ESTA FRASE CITA — não o pacote inteiro.
        # É a correcção dos três achados críticos do red team de uma só vez.
        allowed: set[str] = set()
        for a in anchors:
            allowed |= _fact_numbers(bundle, a)

        for tok in nums:
            norm = tok.replace(",", ".")
            if norm in allowed or norm.lstrip("+") in allowed:
                continue
            ungrounded.append(tok)
        for w in words:
            if str(w) not in allowed:
                ungrounded.append(f"(por extenso) {w}")

    # Linguagem proibida — sobre o texto inteiro, com as ressalvas honestas retiradas.
    scope_all = _strip_disclaimers(_mask_exempt(raw, bundle).lower())
    forbidden: list[str] = []
    for rx, why in _FORBIDDEN_C:
        m = rx.search(scope_all)
        if m:
            forbidden.append(f"{m.group(0).strip()}|{why}")

    # Pares ordenados: os dois números são legítimos; a ORDEM é que pode estar invertida.
    bad_pairs: list[str] = []
    pairs = [(int(n), w.lower()) for n, w in _PAIR_RE.findall(_mask_exempt(raw, bundle))]
    if pairs:
        for f in bundle.facts:
            up, down = f.detail.get("up"), f.detail.get("down")
            if up is None or down is None:
                continue
            for n, w in pairs:
                side_up = w in _UPWORDS
                if side_up and n != int(up):
                    bad_pairs.append(f"{n} {w} (evidência: {up} up)")
                if not side_up and n != int(down):
                    bad_pairs.append(f"{n} {w} (evidência: {down} down)")

    return GroundingReport(
        ok=not (ungrounded or forbidden or unknown or unanchored or bad_pairs),
        ungrounded_numbers=sorted(set(ungrounded)),
        forbidden=sorted(set(forbidden)),
        unknown_anchors=unknown,
        unanchored_sections=unanchored,
        bad_pairs=sorted(set(bad_pairs)),
        anchors_used=sorted(set(used)),
    )


def strip_anchors(text: str) -> str:
    """O texto sem marcas, para canais sem interface (Telegram, registos, testes)."""
    return re.sub(r"\s*\[f\d+\]", "", text).strip()


# ── O que esta guarda NÃO garante ─────────────────────────────────────────────
RESIDUAL = """\
Risco residual desta guarda, depois do red team de seis lentes (114 ataques, 21 reproduzidos):

1. RELEVÂNCIA DA ÂNCORA. Verifica-se que o facto citado EXISTE e que os números da frase são
   dele. Não se verifica que o facto SUSTENTA a afirmação em linguagem natural. Uma frase
   pode citar um facto verdadeiro e caracterizá-lo mal sem usar números.
2. PARÁFRASE. A defesa linguística é uma blocklist, e uma blocklist de linguagem natural
   perde sempre no limite. É por isso que o alerta empurrado usa a allowlist do narrador e
   este caminho não: aqui o texto aparece ao lado da evidência e o utilizador pode abri-la.
3. QUALIFICADORES. "unusually large", "relatively rare" são juízos sem número. Ficam
   permitidos porque proibi-los tornaria o texto ilegível; são verificáveis pelo leitor
   contra o facto citado ao lado.
4. OMISSÃO. Nada obriga o gerador a mencionar um facto desfavorável. A composição
   determinística cobre isto por construção; o texto gerado não.
"""
