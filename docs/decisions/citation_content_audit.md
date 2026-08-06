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

---

# 2.ª ronda — 2026-08-05: as 7 chaves que faltavam, e a paridade EN↔PT

A 1.ª ronda cobriu **122 instâncias / 52 chaves**. Entretanto a tese cresceu para **129 / 59**, e
sete chaves nunca tinham tido o conteúdo verificado: `angelopoulos2023conformal`,
`vovk2005algorithmic`, `gama2014survey`, `vinh2010ami`, `rousseeuw1987silhouettes`,
`sculley2015debt` e `worldmonitor2026`. **Cobertura agora: 129/129 instâncias, 59/59 chaves.**

Desta vez a leitura foi do **texto integral**, não só do resumo, para as fontes acessíveis.

## Os 2 achados, ambos corrigidos por enfraquecimento

### F3 — `angelopoulos2023conformal`: a garantia é **marginal**, não individual

**Onde:** `ch2/chapter2.tex`, secção sobre incerteza (e o eco em `ch5/chapter5.tex`).

**O que dizia:**
> "Calibration […] is an *aggregate* property. **It says nothing about any individual item** […]
> *Conformal prediction* **addresses exactly this gap**."

**O problema.** A frase apresenta a predição conformal como a resposta ao facto de a calibração
nada dizer sobre um item individual. Mas a garantia conformal é **igualmente agregada**: é
*marginal*, em média sobre os casos. Dizer que "responde exactamente" a essa lacuna sugere
**cobertura condicional**, que o método split não dá — e que, no caso geral, é impossível.

**Verificado na fonte** (texto integral, arXiv:2107.07511, confirmado a 2026-08-05):
> *"we call this property **marginal coverage**, since the probability is marginal (averaged) over
> the randomness in the calibration and test points"*
>
> *"in the most general case, **conditional coverage is impossible to achieve**"*

A obra dedica a este ponto uma secção, uma figura e duas métricas de diagnóstico, e chama-lhe
*"subtle but of great practical importance"*. É exactamente o mal-entendido mais comum sobre o
método, portanto é o que um arguente de ML testa primeiro.

**Correcção (enfraquecimento, sem fonte nova — a precisão vem da mesma obra já citada):**
> "*Conformal prediction* **narrows this gap**. It returns a set for each item rather than a point
> estimate, although its guarantee remains *marginal*, averaged over cases, rather than conditional
> on any one of them."

PT espelhado. O eco no Cap. 5 (*"backed by a guarantee"*) passou a *"produced by a procedure whose
coverage guarantee holds on average over cases"*.

**Nota de justiça para com o texto original:** a frase seguinte já enunciava correctamente
*"in at least $1-\alpha$ of cases"*. O defeito era de **moldura**, não uma atribuição falsa.

### F4 — `vinh2010ami`: a correcção é da **linha de base**, não da escala

**Onde:** `ch3/chapter3.tex`, protocolo de avaliação do agrupamento.

**O que dizia:**
> "whereas the adjusted measure **corrects for both chance and cardinality**."

**O problema.** Vinh, Epps & Bailey estabelecem a *constant baseline property* — o **ponto zero**
deixa de depender do número de classes. Não estabelecem comensurabilidade plena de **escala** entre
referências de cardinalidades diferentes; o próprio artigo levanta ressalvas sobre efeitos
secundários da normalização. Além disso não são duas correcções: é **uma só**, porque a esperança
que se subtrai já é calculada sobre as marginais.

**Verificado na fonte** (JMLR 11:2837–2854, PDF integral, p. 2844):
> *"A corrected-for-chance measure, such as the ARI, on the other hand, has a **baseline value
> always close to zero**, and appears **not to be biased in favor of any particular value of K**."*

**Correcção (enfraquecimento):**
> "whereas the adjusted measure has a **chance baseline close to zero that is not biased towards any
> particular number of classes**."

PT espelhado. **A conclusão do Caso 5 mantém-se intacta**: o argumento precisava apenas de que o
artefacto de cardinalidade que corrompia a pureza desaparecesse, e desaparece.

### F5 — `tetlock2007media`: "proof" onde a fonte dá evidência

Apanhado pelo verificador de paridade e presente **nas duas línguas** por igual, portanto não era
um defeito de tradução. O Cap. 2 dizia *"an early **proof** that textual signals relate to market
outcomes"*. Tetlock estabelece uma relação estatística, não uma prova. Passou a *"early
**evidence**"* / *"uma das primeiras **evidências**"*.

## As 5 chaves que passaram, e porquê

| chave | o que a tese lhe atribui | veredicto |
|---|---|---|
| `vovk2005algorithmic` | um preditor pode ser embrulhado para devolver um **conjunto**, com garantia livre de distribuição e válida em amostra finita, exigindo permutabilidade | ✓ sustenta, e a hipótese (permutabilidade) **está declarada** no texto, não escondida |
| `gama2014survey` | a taxonomia da deriva: súbita, gradual, incremental e recorrente | ✓ são esses os quatro nomes do survey |
| `rousseeuw1987silhouettes` | coesão contra separação; e a leitura de um valor **baixo** (0,084) como grupos **sobrepostos** | ✓ sustenta, incluindo a interpretação do valor baixo |
| `sculley2015debt` | custo de manutenção escondido: entanglement, dependências de dados instáveis/não declaradas, dívida de configuração | ✓ são os próprios factores de risco do artigo, escritos a partir de sistemas em produção |
| `worldmonitor2026` | inspiração de **produto**, creditada ao coorientador | ✓ e — o que importa — a tese **não** lhe atribui autoridade académica |

## Paridade EN↔PT: verificada, e com controlo negativo

Nunca tinha sido feita. O risco não era a citação mudar de sítio (as contagens já batiam certo):
era a **tradução endurecer o verbo** e a citação passar a sustentar mais do que aguenta, na versão
que o júri português lê.

`scripts/check_bilingual_parity.py` compara a frase de cada lado e assinala perda de *hedges* ou
ganho de verbos fortes. **Resultado: 0 assimetrias em 86 chaves comparadas.**

⚠️ **O zero só vale porque o detector traz controlo negativo.** A primeira versão apanhava `causa`
dentro de *causal*, *causalmente* e *causar*, e acusou cinco frases fiéis — uma delas dizia
*"podem causar"*, que é o **hedge oposto**. Com fronteira de palavra, os cinco desapareceram. Por
isso o script planta agora um endurecimento e um *hedge* perdido e **exige** que dispare nos dois,
recusando-se a reportar "0 achados" se o autoteste falhar: um detector partido e um corpus limpo
são indistinguíveis no ecrã.

## Resposta pronta, se o júri perguntar

> *"Verificaram que as citações sustentam o que afirmam, ou só que existem?"*
>
> Ambas, e separadamente. A existência está no registo de citações: 61 entradas, cada uma com
> identificador verificado contra a fonte, incluindo uma **rejeição** documentada (MacKinlay 1997, DOI
> irresolúvel). O conteúdo está nesta auditoria: as 129 instâncias foram lidas contra o que a obra citada
> estabelece. Encontrei duas afirmações esticadas — um survey de 2014 a que se atribuía uma geração de
> modelos de 2019, e um critério atribuído a autores que não o elegem — e corrigi ambas **enfraquecendo a
> afirmação**, nunca acrescentando uma fonte que dissesse o que me convinha.
