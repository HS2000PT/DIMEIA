# Auditoria de CONTEÚDO das citações — 2026-07-30

> **O que esta auditoria é.** O `citation_log.md` prova que cada referência **existe** (DOI/arXiv/fonte
> primária verificada). Esta auditoria prova algo diferente e nunca antes verificado: que cada citação
> **sustenta a frase a que está agarrada**. Uma referência pode ser perfeitamente real e mesmo assim
> estar mal aplicada.
>
> **Método.** Para cada `\autocite`/`\textcite` no corpo da tese: ler a frase, perguntar o que ela
> afirma, comparar com o que a obra citada realmente estabelece, e emitir um veredicto. Correções feitas
> **only** por enfraquecimento da afirmação — **nunca** inventando uma fonte nova (§6.4).
>
> **Âmbito.** 122 instâncias de citação, 52 chaves distintas, capítulos 1–6 + apêndice A. O Capítulo 2
> concentra 86 das 122 instâncias (70%), pelo que foi auditado primeiro e linha a linha.

## Resultado

| | |
|---|---|
| Instâncias auditadas | **122** (100%) |
| Chaves distintas | **52** (100% — todas as entradas do `.bib` são citadas) |
| Veredicto **sustenta** | **50 chaves** |
| Veredicto **precisa de enfraquecimento** | **2 chaves** → ambas corrigidas |
| Veredicto **citação errada / fabricada** | **0** |

Distribuição: ch1 7 instâncias / 5 chaves · **ch2 86 / 51** · ch3 19 / 14 · ch4 1 / 1 · ch5 8 / 8 ·
ch6 0 · apêndice A 1 / 1.

---

## Os 2 achados (ambos no Capítulo 2, ambos corrigidos EN+PT)

### F1 — `kearney2014textual`: anacronismo

**Onde:** `ch2/chapter2.tex` §2.5 (Financial NLP), abertura da secção.

**O que dizia:**
> "The financial-NLP literature moves through three generations \autocite{kearney2014textual}:
> lexicons, word embeddings, and **contextual neural models**."

**O que a fonte é:** Kearney & Liu, *Textual sentiment in finance: A survey of methods and models*
(International Review of Financial Analysis, **2014**).

**O problema:** um survey de 2014 **não pode** cobrir modelos neuronais contextuais. O BERT é de 2019 —
cinco anos DEPOIS. A frase, como estava, atribuía à fonte uma taxonomia de três gerações cuja terceira
geração é posterior à própria fonte. Isto é exatamente o tipo de erro que um arguente com literatura
apanha, e é indefensável quando apanhado.

**Correção (enfraquecimento, sem fonte nova):** a divisão em três gerações passa a ser assumida como
síntese **deste trabalho**; a citação passa a sustentar só o que consegue sustentar — as duas primeiras
gerações.
> "The financial-NLP literature falls into three generations: lexicons, word embeddings, and contextual
> neural models. Surveys of textual analysis in finance up to the mid-2010s \autocite{kearney2014textual}
> cover the first two; the third arrived afterwards, and is where this work takes its representation."

PT espelhado. As citações individuais de cada geração (`loughran2011liability`, `mikolov2013word2vec`,
`pennington2014glove`, `vaswani2017attention`, `devlin2019bert`) já sustentavam cada uma o seu troço —
nenhuma precisou de mexer.

### F2 — `doshivelez2017rigorous`: atribuição esticada

**Onde:** `ch2/chapter2.tex` §2.3 (XAI), parágrafo sobre avaliação de explicações.

**O que dizia:**
> "\textcite{doshivelez2017rigorous} **make \emph{fidelity} … a core criterion**"

**O que a fonte é:** Doshi-Velez & Kim, *Towards a Rigorous Science of Interpretable Machine Learning*
(2017). O contributo central é o argumento de que a interpretabilidade tem de ser **avaliada** em vez de
asserida, mais a taxonomia de avaliação (*application-grounded*, *human-grounded*, *functionally-grounded*).

**O problema:** o artigo **não** elege "fidelidade" como critério central — esse termo está mais associado
à *local fidelity* do LIME e à literatura de avaliação de XAI em geral. A primeira metade da frase
("explanations must be evaluated, not assumed") está certa e é literalmente a tese deles; a segunda metade
pedia emprestada autoridade que a fonte não dá.

**Correção (enfraquecimento):** a citação fica a sustentar o que a fonte de facto defende; a fidelidade
passa a ser declarada como o critério que **este trabalho** adota, o que além de honesto lê melhor —
a tese assume o critério em vez de o pedir emprestado.
> "\textcite{doshivelez2017rigorous} argue that interpretability claims need rigorous evaluation rather
> than assertion, and set out how such evaluation can be structured. The criterion this work adopts is
> \emph{fidelity} … because it is the property InvestiGator can guarantee."

PT espelhado.

---

## Verificações que passaram e que valia a pena confirmar

Registadas porque são as que um arguente testaria, e porque um "está tudo bem" sem provas não vale nada.

| Chave | Afirmação na tese | O que a fonte estabelece | ✓ |
|---|---|---|---|
| `barber2008glitters` | Compradores líquidos de ações que "chamam a atenção": notícias, volume invulgar, retornos extremos a um dia | Usa **exatamente** esses três proxies de atenção | ✓ |
| `tetlock2007media` | Índice diário de pessimismo a partir de uma coluna de jornal, ligado a pressão nos preços e volume | É precisamente a construção do artigo (coluna do WSJ) | ✓ |
| `welch2022robinhood` | Investidores de retalho **acrescentaram** posições durante o crash de março de 2020 | É o achado central | ✓ |
| `kahneman1979prospect` | Aversão à perda: perdas pesam mais que ganhos iguais | Prospect Theory | ✓ |
| `da2011attention` | A atenção pode medir-se por volume de pesquisa | "In Search of Attention" usa o Google SVI | ✓ |
| `chandola2009anomaly` | Taxonomia ponto / contextual / coletiva + famílias estatística, distância-densidade, ML | É a estrutura do survey | ✓ |
| `engle1982arch`, `bollerslev1986garch` | Volatility clustering (períodos calmos e turbulentos em séries) | ARCH/GARCH modelam exatamente isso | ✓ |
| `ahmed2016financial` | Em finanças a deteção é dominada por métodos **não supervisionados**, por escassez de rótulos | Survey de deteção de anomalias no domínio financeiro, com essa ênfase | ✓ |
| `breunig2000lof` | Pontua o quão isolado um ponto está na sua vizinhança | Local Outlier Factor, densidade local | ✓ |
| `rudin2019stop` | Defende **abandonar** o pós-hoc a favor de modelos interpretáveis de raiz | É o argumento do título | ✓ |
| `miller2019explanation` | As pessoas querem razões **contrastivas** e seletivas | Insights das ciências sociais: contrastivo, seletivo, social | ✓ |
| `lee2004trust` | *Calibrated trust*; modos de falha *disuse* e *misuse* | Usa e desenvolve exatamente esses termos | ✓ |
| `bansal2021whole` | Explicações podem causar **excesso** de confiança, incl. em respostas erradas | Achado central do estudo CHI | ✓ |
| `loughran2011liability` | Dicionários gerais leem mal palavras financeiras comuns ("liability", "tax") | Achado central; ~75% das palavras negativas do Harvard-IV não são negativas em finanças | ✓ |
| `reimers2019sbert` | Um vetor por frase, comparável por cosseno barato | É a motivação declarada do SBERT | ✓ |
| `fama1969adjustment`, `brown1985daily` | Event study introduzido / normalizado para retornos diários | Correto e na ordem histórica certa | ✓ |
| `aamodt1994cbr` | CBR: *retrieve*, *reuse*, *revise*, *retain* | Os 4 R's, literalmente | ✓ |
| `niculescu2005calibration` | Scores brutos são mal calibrados; sigmoide em validação (Platt) corrige | É a comparação do artigo (Platt vs isotónica) | ✓ |
| `dacunto2019robo` | Robo-advisors melhoram diversificação e atenuam vieses | Achado do artigo para investidores antes sub-diversificados | ✓ |
| `salton1975vsm`, `robertson2009bm25`, `manning2008ir` | Modelo vetorial / TF-IDF→BM25 / medidas rank-aware | Cada uma na sua função canónica | ✓ |

## O que esta auditoria NÃO cobre

- **Não re-verifica a existência** das fontes — isso é o `citation_log.md` (52/52, re-verificado na
  Fase E e novamente nesta ronda).
- **Não julga se a literatura escolhida é a melhor possível** — julga se o que está citado sustenta o
  que está escrito.
- Números, tabelas e figuras têm o seu próprio rasto de proveniência (apêndice A e `docs/evaluation/`).

## Resposta pronta, se o júri perguntar

> *"Verificaram que as citações sustentam o que afirmam, ou só que existem?"*
>
> Ambas, e separadamente. A existência está no registo de citações: 52 entradas, cada uma com
> identificador verificado contra a fonte, incluindo uma **rejeição** documentada (MacKinlay 1997, DOI
> irresolúvel). O conteúdo está nesta auditoria: as 122 instâncias foram lidas contra o que a obra citada
> estabelece. Encontrei duas afirmações esticadas — um survey de 2014 a que se atribuía uma geração de
> modelos de 2019, e um critério atribuído a autores que não o elegem — e corrigi ambas **enfraquecendo a
> afirmação**, nunca acrescentando uma fonte que dissesse o que me convinha.
