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

---

## Capítulo 5 — Case Studies

**Estado inicial:** capítulo de resultados (tabelas de números, figuras de avaliação, exemplo TSLA, alerta
CS3 literal, ameaças à validade). Passagem **muito cuidadosa**: só narrativa; **nenhum número, valor de
tabela, figura ou o bloco literal do alerta CS3** tocado.

**Problemas encontrados e correções:**
1. *Rótulos da tabela inconsistentes.* "SBERT --- MiniLM (default)" / "SBERT --- MPNet" → "SBERT (MiniLM,
   default)" / "SBERT (MPNet)", harmonizando com "Lexical (hashing)" / "Random (base rate)" na mesma tabela
   (remove travessões; valores inalterados).
2. *Números por extenso pesados.* "sixteen of the seven hundred and fifty trading days" → "16 of the 750
   trading days" (mesmos valores, leitura mais leve).
3. *Tique "precisely why".* Duas ocorrências → "why".
4. *Parágrafo longo (M1, tema vs direção).* Partido em dois (análise da recuperação | artefactos do corpus).

**Não alterado (de propósito):** todos os números e ±desvios, as 4 tabelas, as 5 figuras de avaliação, o
exemplo TSLA, o **bloco literal do alerta CS3** (5 precedentes), a nota da *lift* e as quatro categorias de
ameaças à validade.

**Verificação:** compila 78 pp, 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`.
**Resultado:** resultados e rigor idênticos; a narrativa à volta lê-se de forma mais limpa.

---

## Capítulo 6 — Conclusions

**Estado inicial:** capítulo curto (RQ1–RQ3, contribuições, limitações, trabalho futuro). Passagem leve.

**Problemas encontrados e correções:**
1. *Travessões conectores.* Dois pares em prosa → dois-pontos + frase nova (RQ2) e parênteses
   (contribuições). ch6: **2 → 0**.
2. *Frase longa (RQ2).* A frase dos números da recuperação partida em duas (números preservados exatamente).
3. *Pequenas asperezas.* "Three concrete contributions stand." → "stand out."; "addressing… risks…
   head on." → "directly addressing… risks…".

**Não alterado (de propósito):** todos os números (0,015/0,344; F1 0,516; 0,514±0,015; etc.), o mapeamento
RQ→resultado, as contribuições e os compostos en-dash ("clarity--completeness--actionability", "news--market").

**Verificação:** compila 78 pp, 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`.

---

## Balanço (Cap. 1–6)

Travessões conectores em prosa: **117 → 1** em todo o corpo (o que resta é uma célula "—" de
não-aplicável na tabela de posicionamento do Cap. 2). Todos os capítulos compilam sem erros, sem citações
indefinidas e sem overfull >15pt; nenhum número, citação, equação, algoritmo, tabela ou figura foi alterado.
Falta: front matter (abstract/resumo + declarações) e Apêndice A; depois, coerência global + sincronizar
paper/slides/caderno.

---

## Front matter (abstract + resumo) e Apêndice A

**Abstract (EN) e resumo (PT):**
- *Travessões conectores.* Dois pares em cada (a delimitar os dois gatilhos e a lista de componentes) →
  parênteses, em ambas as línguas. Prosa do abstract/resumo: **0** travessões.
- Abstract mantém-se com **192 palavras** (≤ 200); todos os números preservados (0,51 / 0,35 / 0,24).
- **Declarações (integridade + uso de IA) NÃO tocadas:** são texto formal; a redação da declaração de IA
  fica como está, a aguardar confirmação do aluno com o orientador (memória `honest-ai-declaration`).

**Apêndice A (Reproducibility):** revisto e **deixado como está** — já é uma secção de referência limpa,
sem travessões e com prosa clara (tabela de versões + 3 comandos de reprodução). Não se reescreve o que já
está bom.

**Nota:** os `---` que restam no `frontmatter.tex` são comentários `%----` (não renderizados) e as células
"—" da lista de símbolos (grandezas adimensionais = sem unidade), ambos usos corretos.

**Verificação:** compila 78 pp, 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`.

---

## Gate final — coerência global + artefactos

**Coerência global (tese):** verificado de ponta a ponta —
- **0 espaços duplos** e **0 artefactos** de pontuação introduzidos pelas conversões (vírgulas/parênteses).
- **Terminologia consistente:** "Sentence-BERT" (14×, sempre capitalizado), "cross-ticker" sempre
  hifenizado, "precision@$k$", "no-lookahead" (adjetivo) vs "no lookahead" (rótulo) usados corretamente.
- **Referências cruzadas:** 0 indefinidas, 0 `??` (build limpo).
- **Travessões conectores em prosa: 117 → 1** (1 célula de tabela "não-aplicável" no Cap. 2).
- Abstract EN: **192 palavras** (≤ 200).

**Artefactos derivados:** o copy-edit mudou só a prosa da tese; o `paper/` (IEEE, 3 pp) e os `slides/`
(14 pp) **compilam sem erros** e continuam **factualmente alinhados** (mesmos números e a mesma mensagem
"tema, não direção", já sincronizada antes). Não foram reescritos: o registo do artigo IEEE aceita
travessões e a sincronização exigida aqui é de coerência, não de estilo. (Opcional, a pedido: aplicar a
mesma passagem de naturalidade ao caderno de defesa PT-PT e aos slides.)

**Conclusão:** corpo da tese 100% revisto; mesmo rigor, conteúdo e números; leitura mais natural, simples e
humana. `verify.sh` verde (43 testes + ruff). Faltam só as tarefas humanas (declaração ISEP + leitura do aluno).

---

## Artefactos — slides + caderno de defesa (a pedido do aluno)

Aplicada a mesma passagem de naturalidade aos artefactos derivados (o `paper/` IEEE ficou como está: o
registo de artigo aceita travessões).

**`slides/main.tex` (Beamer, EN-GB):** travessões conectores 16 → 1 (resta só o "News alert --- NVDA" do
mock de UI). Títulos de frame/bloco passaram a dois-pontos ("Result 1: ..."); bullets com travessão
conector passaram a vírgula/dois-pontos. Compila 14 pp, 0 erros. Nenhum número alterado.

**`docs/defence/caderno_de_defesa.md` (PT-PT):** travessões em prosa `—` 28 → 7; os 7 que restam são
separadores de título/cabeçalho (ex.: "Gatilho 1 — movimento de mercado") e uma linha de bloco de código,
usos estruturais legítimos. Os 7 divisores de secção `---` (regra horizontal markdown) e os diagramas ASCII
foram preservados. Nenhum número, citação ou facto alterado.

**Resultado:** tese, slides e caderno partilham agora a mesma voz natural; o paper IEEE mantém-se alinhado
em conteúdo.

---

## Revisão de figuras/diagramas (a pedido: "tornar claro, transparente, ligado, conectado")

Revistas **todas** as figuras visualmente (render). As figuras de dados (matplotlib) já estavam limpas; o
problema era os **diagramas TikZ** (sobreposições/bugs) e a **fragmentação do Cap. 4** (6 diagramas para o
mesmo sistema). Decisão do aluno: **consolidar num mapa único**.

**Bugs de renderização corrigidos (Cap. 3):**
- *Espaço de embeddings* (era o pior): os rótulos do cluster sobrepunham-se. Redesenhado com **linhas-guia**
  para rótulos à direita, pontos bem separados, "não-relacionados" à esquerda. Legível.
- *Janela de evento*: as setas de retorno cumulativo e o rótulo colidiam com "news (non-trading)".
  Redesenhado com setas bem separadas, rótulo único por cima, data da notícia à esquerda sem colisão.
- *Camadas de dados*: rótulo "common schema" afastado da seta (sem sobreposição).

**Cap. 4 consolidado (6 → 2 diagramas + mockup):**
- **Mantido:** mapa de arquitetura (componentes) e o mockup do Telegram.
- **Redesenhado:** o diagrama end-to-end passou a ser **um único mapa conectado** com 3 faixas rotuladas
  (offline · news · market) que convergem na explicação → Telegram; seta vertical "precedents" da base de
  conhecimento para o passo de cosseno; corrigida a sobreposição do rótulo "align, embed".
- **Removidos:** os 4 diagramas redundantes (fluxo + sequência de cada gatilho). A prosa do Cap. 4 passou a
  remeter para as faixas (middle/bottom) do mapa único, ficando "mais conectada".

**Resultado:** tese **76 pp** (era 78; menos 4 figuras redundantes), 0 erros, 0 refs indefinidas,
0 overfull >15pt, 0 `??`. Figuras totais 19 → 15; Cap. 4 de 7 → 3. Nenhum número/dado alterado.

---

# REESCRITA PROFUNDA (clareza, capítulo a capítulo) — Sessão 24

> Pedido do aluno: a tese ainda lê densa/cansativa e o núcleo não fica claro. Reescrita de raiz para
> **clareza progressiva**, dentro dos 6 capítulos canónicos; cada secção responde a UMA pergunta; conceito
> antes de implementação; parágrafos curtos; **sem inventar nada**, números/citações preservados.

## Capítulo 1 — Introduction (reescrito)
- Cada secção passa a responder a uma pergunta clara; parágrafos curtos.
- **Objetivos** convertidos de frase corrida para **lista**; contribuições mais nítidas.
- **"Document Structure" → mapa do leitor:** lista com a pergunta que cada capítulo responde (prepara a
  leitura progressiva). Ex.: Cap. 4 (CLARION) = "o que é o sistema, e como encaixam os seus dados, partes,
  fluxo e decisões?".
- Figuras (market cap, conceito), números (62,2T; 87/28; 81/71) e citações preservados; 0 travessões.

**Verificação:** compila 76 pp, 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`.

## Capítulo 2 — State of the Art (reescrito para clareza)
- **Cada secção abre com a sua pergunta** (ex.: "Como distinguir um movimento anormal de ruído normal?") e
  **fecha com uma linha "For CLARION:"** (o que o sistema retira daquele campo). Parágrafos muito mais curtos.
- Densidade cortada: prosa reduzida de forma substancial; **−4 páginas** (76 → 72).
- **Integridade de citações preservada: 50 citadas = 50 no .bib, 0 órfãs, 0 indefinidas.** Nenhuma citação,
  tabela ou figura removida (o corte é em palavras, não em referências).
- Conclusões do capítulo encurtadas (os takeaways por secção já resumem), reduzindo redundância.
- 0 travessões em prosa (resta 1 célula de tabela "—" não-aplicável).

**Verificação:** compila 72 pp, 0 erros, 0 citações/refs indefinidas, 0 overfull >15pt, 0 `??`.

## Capítulo 3 — Methods and Materials (reescrito, concept-first)
- **Cada técnica abre por "What it is for:"** (propósito em linguagem simples) **antes** da equação/algoritmo
  (deteção, recuperação+impacto, explicação). Secções abrem com a pergunta ("How is a news item turned into
  a historical case?", "How is the system judged?").
- **Parágrafo denso das "três escolhas" (horizontes/baseline/agregação) → lista** scannable.
- Prosa encurtada em todo o capítulo; conclusões crisp.
- **Intocado:** as 3 equações, os 3 algoritmos, a data card, as tabelas trabalhadas, as 3 figuras, e TODOS
  os números (3,2%; z −8,1/−2,2; 3 714; +6,5%; 0,60/0,38; k=5; etc.). Citações 50/50 (0 órfãs/indefinidas).

**Verificação:** compila 72 pp, 0 erros, 0 indefinidas, 0 overfull >15pt, 0 `??`.
