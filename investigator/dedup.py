"""A mesma história noutras palavras — uma só implementação, para dois caminhos.

## Porque é que isto saiu de dentro de um script

O detector de quase-repetição nasceu em `scripts/run_alerts.py` para impedir que a mesma história,
publicada por dois meios com títulos diferentes, chegasse ao canal duas vezes. Ficou lá — e o
**caminho dos precedentes nunca o usou**, apesar de o problema ser o mesmo e de aí ser **pior**.

A deduplicação de precedentes era de **texto exacto** (`" ".join(headline.lower().split())`).
O comentário que a acompanha explica melhor do que qualquer justificação minha porque é que isso
importa: mostrar a mesma história como precedentes independentes *"não é uma imprecisão de
apresentação, é uma afirmação falsa sobre a evidência: três observações independentes pesam muito
mais do que uma vista três vezes"*. A correcção de 2026-08-02 fechou o caso do texto **idêntico**
entre tickers; a mesma história escrita por dois meios continuava a contar como duas observações —
e o alerta afirma, em voz alta, *"3 of 3 shown cases moved down"*.

Uma biblioteca não deve importar de um script, e duas cópias da mesma regra divergem. Vive aqui, e
o runner passa a importá-la.

## Porque é que continua a ser léxico, e não embeddings

Porque a medição que justificaria a mudança **não existe** (não há corpus anotado de pares
quase-duplicados neste projecto), e trocar uma heurística por um modelo sem medir seria exactamente
o que o resto do trabalho recusa fazer. O limiar de 0,6 é **escolhido, não derivado**, e está dito.
Medi-lo — e comparar léxico contra embeddings sobre pares anotados — é a linha de trabalho que a
directiva de raiz identifica como a mais forte deste domínio.
"""

from __future__ import annotations

import re

# Palavras que não distinguem histórias. Curta de propósito: uma lista longa começa a apagar
# diferenças reais entre manchetes ("beats" vs "misses" não podem cair aqui).
STOPWORDS: frozenset[str] = frozenset({
    "the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "as", "at", "by", "is",
    "its", "it", "with", "from", "after", "over", "amid", "says", "said", "will", "be",
    "que", "de", "do", "da", "dos", "das", "e", "o", "os", "um", "uma", "no", "na",
})

MIN_CONTENT_WORDS = 4
DEFAULT_THRESHOLD = 0.6


def content_words(text: str) -> set[str]:
    """Palavras de conteúdo de uma manchete, para comparar histórias entre si."""
    palavras = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {p for p in palavras if len(p) > 2 and p not in STOPWORDS}


def is_near_duplicate(headline: str, seen: list[set[str]] | list[list[str]],
                      threshold: float = DEFAULT_THRESHOLD) -> bool:
    """A mesma história que alguma das já vistas?

    Jaccard sobre palavras de conteúdo. O limiar é 0,6 e não 0,9 porque duas redacções da mesma
    história partilham os nomes próprios e os números mas trocam metade dos verbos; 0,9 só
    apanharia o que uma comparação de texto exacto já apanha.

    ⚠️ **Falha ABERTA com manchetes curtas** (menos de `MIN_CONTENT_WORDS` palavras de conteúdo):
    com uma ou duas palavras qualquer par bate e a medida não significa nada. Mais vale um
    precedente repetido do que um precedente a menos — o custo é assimétrico.
    """
    novo = content_words(headline)
    if len(novo) < MIN_CONTENT_WORDS:
        return False
    for anterior in seen:
        velho = set(anterior)
        if len(velho) < MIN_CONTENT_WORDS:
            continue
        if len(novo & velho) / len(novo | velho) >= threshold:
            return True
    return False
