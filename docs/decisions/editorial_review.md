# Revisão Editorial / Copy-edit — registo por capítulo

> Revisão **editorial** (não de autoria) da dissertação: tornar o texto natural, simples, fluido e credível
> em **EN-GB**, sem tiques de IA, mantendo todo o rigor e **sem inventar nada**. Trabalho capítulo a capítulo,
> com pausa no fim de cada um. Plano em `.claude/plans/…squishy-yeti.md`. Início: 2026-06-27.
>
> Guarda-rios: sem conteúdo novo; preservar todos os números, citações, labels, equações e cross-refs;
> encurtar só onde não se perde rigor; nunca PT no corpo (o *resumo* fica PT).

---

## Capítulo 1 — Introduction

**Estado inicial:** já era dos capítulos mais limpos (claro, bem fundamentado). Passagem **leve**, sem
reescrever; foco em naturalidade e simplicidade.

**Problemas encontrados e correções:**
1. *Tique de IA — travessões na legenda da Figura 1.2 (conceito).* "two triggers --- … --- feed CLARION,
   which replies **not with** a bare notification **but with** an explained alert". → Reescrita sem
   travessões e com a antítese aligeirada: "The two triggers, a sudden market move or a relevant news item,
   feed CLARION, which answers with an explained alert the investor can follow and check, not just a bare
   notification." (ch1: 2 → **0** travessões.)
2. *Construções "cleft" (indiretas).* "Letting the investor see why an alert was raised is what this
   dissertation sets out to do." → ativa e direta: "This dissertation sets out to let the investor see why
   an alert was raised."
3. *Advérbio mal colocado.* "Artificial intelligence has, meanwhile, spread quickly…" → "Meanwhile,
   artificial intelligence has spread quickly…".
4. *Eco de palavra / frase vaga.* "What they share is a hard position." + "knowledge of how … in the past,
   knowledge most people do not have to hand." → "Whatever their income, they face the same difficulty." e
   "which takes knowing how similar events played out before, and most people have no easy way to do that."
5. *Pequenas asperezas.* "rather than from professional institutions" → "not from…"; "two distinct
   challenges" → "two challenges"; "telling … apart from" → "telling … from"; "provide alerts" → "send
   alerts"; última frase dos objetivos reescrita de forma mais simples ("built incrementally, in its
   simplest defensible form first; that is a deliberate methodological choice").

**Não alterado (de propósito):** números (62,2T; 87/28%; 81/71%), citações, RQ1–RQ3, contribuições,
estrutura do documento — todos preservados.

**Verificação:** compila 78 pp, 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`.
**Resultado:** capítulo mais direto e humano, mesmo conteúdo e rigor.

---

## Capítulo 2 — State of the Art

**Estado inicial:** o capítulo mais denso e "académico-pesado", com 23 travessões e várias frases/parágrafos
longos. Passagem **profunda** (continua a ser copy-edit, não reescrita de conteúdo).

**Problemas encontrados e correções:**
1. *Travessões como conectores (tique de IA).* Convertidos **todos** os 23 em prosa para vírgulas,
   parênteses ou dois-pontos (ch2: **23 → 0** em prosa; resta 1 célula de tabela com "—" = não-aplicável).
2. *Parágrafos demasiado longos.* Dividido o bloco enorme da deteção de anomalias em dois (estatística
   transparente/GARCH | detetores mais expressivos) e separado o parágrafo dos *embeddings* (estáticos |
   Transformer/BERT). Frase-taxonomia de \textcite{chandola2009anomaly} partida em duas.
3. *Jargão evitável.* "desiderata" → "different goals"; "impounded into prices rapidly" → "absorbed into
   prices quickly"; "the asymmetric weighting of losses against equivalent gains" → "we weigh losses more
   heavily than equivalent gains".
4. *Advérbios/tiques de sinalização.* Removidos "Crucially", "moreover", "in effect", "and durable", "And"
   (início de frase), "precisely why" → "why".
5. *Construção invertida nas conclusões.* "What the literature offers… it largely lacks…" → duas frases
   simples: "The literature thus provides mature individual components but not an integrated… system. That
   gap is what this dissertation addresses…".
6. *Pequenas asperezas.* "has likewise been quantified" → "has also been measured"; "intervenes exactly
   where" → "arrives exactly where"; "a contested claim of total interpretability" → "claiming full
   interpretability"; "response pursued here is not… but…" → "response here is not… but…".

**Não alterado (de propósito):** todas as citações (mesmo conjunto), tabelas e figuras (taxonomias),
compostos com en-dash ("capacity--interpretability", "news--market", "word--word", "human--AI") e a célula
"—" de não-aplicável na tabela de posicionamento.

**Verificação:** compila 78 pp, 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`.
**Resultado:** mesmo rigor e mesma literatura, leitura bastante mais leve e humana.

---

## Capítulo 3 — Methods and Materials

**Estado inicial:** capítulo técnico (3 equações, 3 algoritmos, data card, exemplos trabalhados). Passagem
**deliberadamente leve e cuidadosa**: só prosa à volta; **nada** de equações, pseudocódigo, valores de
tabela ou números tocado.

**Problemas encontrados e correções:**
1. *Travessões conectores.* Os 5 em prosa convertidos para vírgula, dois-pontos, ponto ou parênteses
   (ch3: **5 → 0**). Inclui partir uma frase longa do protocolo cross-ticker em duas.
2. *Frase longa (fidelidade).* O parágrafo sobre fidelidade/utilidade, antes uma única frase com par de
   travessões, foi partido em três frases curtas e claras.
3. *Palavras desnecessariamente sofisticadas.* "bespoke scraping" → "custom scraping"; "stated plainly
   rather than obscured" → "rather than hidden".

**Não alterado (de propósito):** equações (\ref{eq:zscore}, \ref{eq:precatk}), os 3 algoritmos, a data card,
a tabela do z-score, a tabela de recuperação e respetiva nota, todas as figuras, e todos os números.

**Verificação:** compila 78 pp, 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`.
**Resultado:** mesma técnica e rigor; a prosa de ligação ficou mais simples e direta.

---

## Capítulo 4 — CLARION

**Estado inicial:** capítulo de desenho do sistema, com 7 figuras (arquitetura, fluxo end-to-end, fluxo e
sequência de cada gatilho, mockup do Telegram). Passagem de prosa + legendas; **lógica dos diagramas
intocada**.

**Problemas encontrados e correções:**
1. *Travessões conectores.* Par numa legenda (sequência da notícia) → dois-pontos + vírgula (ch4: prosa
   **0**; o mockup mantém `\textemdash` como separador de UI, que é correto).
2. *Enumeração mecânica.* A frase com cadeia de 5 pontos-e-vírgula na introdução da arquitetura partida em
   duas frases mais naturais.
3. *Repetição.* "A real alert was delivered to a Telegram account during testing" aparecia em duas secções;
   a segunda foi reescrita para referir o mesmo facto sem repetir ("works end to end, not just on paper").
4. *Pequenas asperezas.* Legenda da sequência do gatilho de mercado: "dashed arrows returns" → "dashed
   arrows are returns" (paralelismo); "recorded here for honesty rather than hidden" → "recorded here
   openly rather than hidden".

**Não alterado (de propósito):** todos os diagramas TikZ e a sua lógica, a tabela de decisões, o mockup do
Telegram (números já consistentes), e a cláusula de linguagem simples do motor de explicação.

**Verificação:** compila 78 pp, 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`.
**Resultado:** prosa e legendas mais limpas; o desenho do sistema lê-se de forma mais fluida.
