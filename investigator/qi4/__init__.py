"""QI4 — ajuste contrastivo do codificador por materialidade comparável.

A tese estabelece, na §5.3, que a recuperação semântica capta **tema** e não direção, e na
§5.3.5 que a direção quase não se aprende do texto. A QI4 pergunta o passo seguinte: se o
codificador for ajustado para que a proximidade signifique **grandeza comparável do movimento
subsequente**, os precedentes recuperados ficam mais comparáveis ao caso em mãos?

Três braços, no mesmo arnês:

- **principal** — ajuste sobre `|retorno anormal|` (materialidade, nunca direção);
- **replicação** — o mesmo, sobre o retorno **com sinal**, reproduzindo [Jeong26] aqui dentro.
  A comparação magnitude-vs-direção é o resultado da QI4;
- **controlo** — codificador de domínio (FinBERT) com o objetivo principal. Despromovido de
  contribuição a controlo depois de o FinBERT2 (KDD 2025) mostrar que a ideia resulta.
"""
