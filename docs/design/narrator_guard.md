# narrator_guard.md — A guarda de fidelidade do narrador

> Documento de desenho. Acompanha `investigator/narrator/` e o arnês
> `scripts/evaluate_narrator.py`. Escrito para ser defensável numa arguição.

## A afirmação

> O texto entregue ao utilizador nunca contém um número que os motores não tenham calculado,
> nunca com a direção invertida, e nunca linguagem preditiva ou de aconselhamento —
> **independentemente do que o LLM devolva**.

Repare-se no que a afirmação **não** diz: não diz que o LLM é fiável. Diz que a fidelidade do
produto não depende disso. É uma propriedade do sistema, não do modelo.

## Porque um LLM, afinal

O sistema já produzia texto: um template determinístico. O LLM não acrescenta factos — os
factos vêm todos dos motores (z-score, decomposição, retrieval, triagem). Acrescenta apenas
*fluência*. Logo, o único risco que introduz é dizer algo que os motores não disseram, e é
exatamente esse risco que a guarda elimina.

Esta é também a razão de o narrador **não** ser um chatbot nem um sistema multi-agente. Um LLM
com ferramentas não é um sistema multi-agente, e reivindicá-lo entrega ao júri a superfície de
ataque mais fácil que existe. É uma função pura: `narrate(evidence) -> str`.

## A arquitetura, e porque a primeira estava errada

### v1 — blocklist (rejeitada)

Padrões proibidos (`will rise`, `recommend`, `bullish`) + correspondência numérica permissiva.

Um **red team de 3 adversários independentes**, cada um obrigado a reproduzir a sua alegação
com Python real antes de a poder afirmar, produziu **29 furos confirmados**. Os padrões:

| Família | Exemplo que passava | Causa |
|---|---|---|
| **Inversão de direção** | `"AMD gained 8.50%"` quando o motor calculou **−8,50%** | `lstrip("+-")` no conjunto permitido e extrator numérico sem sinal |
| **Apóstrofos como aspas** | `"It's … isn't"` criava um span "citado" falso que isentava tudo lá dentro | `_QUOTE_RE` aceitava `'…'`; qualquer frase com duas contrações abria buraco |
| **Paráfrase preditiva** | `poised to rally`, `likely to rebound`, `due for a bounce`, `Buy the dip`, `not bearish` | fora da lista finita de padrões |
| **Smuggling numérico** | separadores invisíveis (U+200B), numerais não-ASCII (٤٠٠, ½), fragmentos de data (`2026-07-28` legitimava "down 28%") | tokenização ingénua |
| **Atribuição errada** | `"mostly market-driven"` com `driver=company`; precedentes trocados | nada verificava semântica |

A lição é estrutural, não uma questão de melhorar a lista: **uma blocklist de linguagem
natural perde sempre.** O espaço de paráfrases é infinito; a lista é finita.

### v2 — allowlist (atual)

A assimetria inverte-se. O narrador não escreve prosa livre: reconta 6 a 10 factos. Um
**vocabulário fechado** de ~280 palavras neutras (`lexicon.py`) chega para isso, e tudo o que
não foi explicitamente permitido — incluindo a paráfrase que ninguém imaginou — é rejeitado
por omissão.

Quatro camadas, em `core.check_faithfulness`:

1. **Normalização** — NFKC, remoção de invisíveis (ZWSP, soft-hyphen, word-joiner), aspas
   tipográficas → retas, e rejeição de qualquer dígito não-ASCII.
2. **Números com sinal** — um valor **negativo** só vale escrito com `-`. Positivos aceitam-se
   com ou sem `+` (largar um `+` não muda o sentido; largar um `-` inverte-o). Datas da
   evidência são mascaradas antes da extração, para os seus dígitos não legitimarem nada.
3. **Vocabulário fechado** — palavras fora do léxico são violação. Ficam isentos: citações
   verbatim (só aspas duplas verdadeiras, conteúdo presente na evidência), disclaimers de uma
   lista fixa, e o nome comercial da empresa (identificador do nosso mapa, não texto livre).
4. **Atribuição** — a fonte dominante só pode ser afirmada pelas frases de `DRIVER_PHRASES`,
   validadas contra `evidence.driver`; contagens up/down validadas contra a evidência.

**Verbos direcionais estão deliberadamente fora do léxico.** `gained`, `fell`, `rose`,
`climbed` não constam: a direção é carregada pelo **sinal do número**, que é verificável
mecanicamente, e não por um verbo, que não é. Custo assumido: o texto fica mais clínico
("AMD moved -8.50%" em vez de "AMD fell 8.5%"). É o preço da verificabilidade, e o arnês
mede-o.

## Auto-consistência: o chão passa a própria guarda

O template determinístico é redigido **dentro** do vocabulário fechado e é verificado contra
a sua própria guarda em todos os casos do arnês. Se o chão violasse a guarda, uma falha do LLM
deixaria o utilizador sem texto nenhum. O arnês aborta se algum template falhar.

## As duas métricas, e porque são duas

- **Taxa de violação pré-guarda** — quantas respostas *cruas* do LLM violaram a evidência.
  Mede o **modelo**. É o número que justifica a guarda existir.
- **Taxa de violação entregue** — o mesmo verificador aplicado ao texto que o produto
  entregaria. Por construção deve ser **0**. Aqui o que está em julgamento é a **guarda**,
  não o modelo. Se alguma vez não for 0, a guarda tem um buraco e o arnês apanhou-o.

Um arguente pode objetar que a segunda métrica é circular — o mesmo verificador decide e
avalia. É verdade, e é por isso que **não é o único teste**: o corpus do red team (21 exploits
confirmados, em `tests/test_narrator_core.py::TestRedTeam`) é um conjunto de ataques
construídos por adversários que **não** tinham a guarda atual à frente, e cada um é executado
ponta a ponta contra `narrate()`. A honestidade está em reportar as duas coisas e nomear a
limitação.

## Limitações (declaradas, não escondidas)

- **Números por extenso** ("four hundred percent") escapam à extração numérica. Mitigado pelo
  vocabulário (as palavras de número não constam do léxico), não pela camada numérica.
- **Cobertura semântica parcial.** Verifica-se a atribuição do *driver* e as contagens
  direcionais; não se verifica todo o emparelhamento precedente↔impacto em prosa livre.
  O vocabulário fechado limita muito o que é dizível, mas não é uma prova de correção
  semântica.
- **A guarda é conservadora por desenho.** Prefere rejeitar prosa legítima a deixar passar
  prosa infiel. A consequência mensurável é a taxa de rejeição — reportada, não escondida.
- **O léxico cresce por medição.** Palavras entram quando o arnês ao vivo mostra que causam
  falsos positivos, e cada entrada é verificada como não-direcional e não-preditiva. Nunca
  entram verbos de direção ou juízo.

## Ficheiros

| Ficheiro | Papel |
|---|---|
| `investigator/narrator/providers.py` | transporte (Groq → Gemini → None), sem juízo de conteúdo |
| `investigator/narrator/evidence.py` | contrato de dados; grafias numéricas já formatadas |
| `investigator/narrator/lexicon.py` | vocabulário fechado, disclaimers e frases de atribuição |
| `investigator/narrator/core.py` | prompt, template-chão, verificador e `narrate()` |
| `scripts/evaluate_narrator.py` | arnês: 18 casos determinísticos, 2 fornecedores |
| `scripts/probe_llm.py` | saúde dos fornecedores (correr antes da defesa) |
| `tests/test_narrator_core.py` | propriedades + os 21 exploits do red team |
