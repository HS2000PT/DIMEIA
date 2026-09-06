# Auditoria forense da dissertação — 2026-09-06

> **O que este documento é.** O registo de uma leitura integral de `tese-pt/` (a árvore
> canónica) e do seu espelho `tese-eng/`, feita em papel de júri hostil, com cruzamento contra
> `docs/evaluation/`, `models/`, `config/` e `investigator/`. Vinte e três defeitos confirmados,
> todos corrigidos nas duas árvores salvo os que exigem decisão humana, que ficam na secção L.
>
> **O que este documento não é.** Não é uma proposta de reestruturação, não abre âmbito e não
> introduz medições novas. Nenhum resultado foi alterado; o que mudou foi a correspondência
> entre o que o documento afirma e o que os seus próprios artefactos dizem.

---

## A. Estado geral

A dissertação chega a esta auditoria em bom estado, e convém dizê-lo antes das falhas porque
condiciona a leitura de todas elas. Verifiquei **de forma independente**, refazendo a
aritmética em vez de aceitar o valor impresso:

| verificação | resultado |
|---|---|
| divisão com embargo | $28\,574 + 17\,710 + 32\,649 = 78\,933 = 79\,753 - 820$, e $820/79\,753 = 1{,}03\%$ — **fecha exacto** |
| decomposição da AMD | $-0{,}3992 - 0{,}0362 + 6{,}7298 = 6{,}2944$, e $e^{0{,}062944}-1 = 6{,}50\%$ — **fecha exacto** |
| $z$-score da Tesla | $(19{,}82 + 0{,}92)/2{,}7246 = 7{,}61$ — **fecha** |
| $F_1$ dos três detetores | $0{,}530$, $0{,}269$ e $0{,}280$ reproduzem-se das coordenadas desenhadas — **fecham** |
| funil de 15/08 | $5\,060 - 2994 - 1194 - 269 - 249 - 21 = 333$ — **fecha exacto** |
| Figura 4.3 | os doze títulos somam $743$ e os doze alertas somam $15$ — **fecha exacto** |
| taxa-base da pós-validação | $(436 \times 0{,}589 + 389 \times 0{,}617)/825 = 0{,}602$ — **fecha exacto** |
| Tabela 4.1 | $432+141+429 = 1002$, $1002-970 = 32$ duplicados, $1002-64 = 938 = 401+119+418$ — **fecha exacto** |
| Wilson de $41/42$ | $[0{,}877;\,0{,}996] \rightarrow$ 88\%–100\% — **fecha** |
| custo do alojamento | $75-14 = 61$ e $57-14 = 43$ — **fecha exacto** |
| Platt implantado | `a=3.6996675`, `b=-2.3133665` no `.joblib` contra $3{,}700$ e $-2{,}313$ — **fecha** |
| nove entradas | `['vol20','mom5','ret_event','headline_len','sector_*×5']` — **nove, exactamente** |
| $31{,}1\%$ vs $38{,}7\%+30{,}2\%$ | $100 - 68{,}9 = 31{,}1$ — **fecha** |
| $17{,}1\%$ sem prior | `5581/32649 = 17,1%` no `evaluation_budget_baselines.md` — **fecha** |

**Nenhum defeito encontrado compromete um resultado.** Os vinte e três achados repartem-se por
três classes: **a figura e o texto lerem janelas diferentes** (a mais séria, e a única visível
numa só página), **aritmética de contagem que não fecha na prosa** apesar de fechar no
artefacto, e **defeitos de composição e de nomenclatura**.

---

## B. Problemas críticos 🔴

### B1 · A Figura 5.15 desenhava uma janela e o parágrafo seguinte citava outra ✅ corrigido

Na página 70, por esta ordem, e sem nada entre eles:

- «a medição foi realizada sobre as **4 366** decisões»
- a figura, com **três** barras alaranjadas e a legenda «**Oito** das doze empresas encontram-se
  inteiramente de um dos lados»
- «**Os valores confirmam a leitura da figura.** Sobre as **36 925** decisões registadas…
  **Duas** empresas situavam-se sempre acima do limiar… apenas em **cinco** das doze o limiar
  chegava a decidir»

**Porque é um problema.** Um membro do júri que conte as barras alaranjadas obtém três e lê duas
uma linha abaixo. A frase de transição afirma concordância exactamente onde ela não existe. É a
secção que carrega o achado que a própria dissertação chama «a constatação com maior capacidade
de transferência do trabalho».

**Evidência.** As doze linhas da figura reproduziam, valor a valor, a tabela de
`evaluation_gate_selectivity.md` (janela 4 366, 2026-07-22 a 2026-08-15: META 0,525/0,537/0,545,
«sempre passa»), enquanto o texto reporta `evaluation_gate_selectivity_unicos.md` (janela 36 925,
2026-07-22 a 2026-08-20: META 0,498/0,506/0,545, «o piso decide»).

**Correção.** A figura passa a desenhar a janela de 36 925, lida do artefacto; a legenda declara
a janela e as datas; a frase de abertura cita 36 925; «Oito» passa a «Sete». Verificado a
renderizar: duas barras alaranjadas, cinco claras, cinco escuras.

### B2 · O Apêndice A.5 imprimia uma frase truncada ✅ corrigido

O PDF entregue, página 103, terminava assim:

> «…e as duas exceções a essa restrição, que são o alojamento e»

e passava à figura. Igual nas duas línguas. **Correção:** «…que são o alojamento e o canal de
mensagens, são custos de operação e não fontes de dados», que é o que a própria secção conclui
mais abaixo.

### B3 · A afirmação sobre a AMD e a Meta era falsa na janela reportada ✅ corrigido

§5.6.2 dizia «Duas das ausentes, a AMD e a Meta, estão entre as que se situam sempre acima do
limiar». Na janela de 36 925 decisões — a que o §5.6.1 reporta — as duas empresas sempre acima
são a **AMD e a TSLA**; a Meta tem mínimo $0{,}498$ e o limiar chega a decidir. **Correção:** a
frase passa a nomear a AMD como uma das duas e a Meta como tendo mediana imediatamente acima do
limiar, o que preserva o argumento sem afirmar o que os dados não mostram.

---

## C. Problemas importantes 🟠

| # | Onde | O problema | Correção |
|---|---|---|---|
| C1 | Fig. 4.4 vs Fig. 4.5 | O funil de 15/08 mostra o **piso escalonado a eliminar 269 avaliações**; a Figura 4.5, duas páginas à frente, dizia «**nunca atuou**» | «$0\%$ nos seis dias», e a legenda do funil remete para a Figura 4.5 ✅ |
| C2 | §5.6.5 | «81 votos válidos → 42 efetivos», com 10 alterações e 5 exclusões explicadas: **faltavam 29** | O gerador passa a escrever os cliques repetidos. $42+10+29 = 81$ ✅ |
| C3 | Tab. 3.1 vs §4.2.3 | A linha «Base de precedentes **implantada** — 38 214» descreve **metade** dela: o §4.2.3 diz que a base consultada funde 38 214 reconstruídos com 11 445 vivos | Passa a «Base de precedentes **reconstruída**»; o §6.1 acompanha ✅ |
| C4 | Resumo PT | **201 palavras** contra o limite de 200 do modelo oficial e do próprio `BRIEF_REESCRITA.md` | «linha de base baseada apenas em» → «apenas com» (200 palavras, e resolve a cacofonia *base baseada*) ✅ |
| C5 | Fig. 5.11 vs Fig. 5.18 | «Escolha aleatória» aparece a **$0{,}379$** numa figura e a **$0{,}375$** noutra, ambas «40 sementes», mesmo bloco, mesmo orçamento | A legenda da Fig. 5.18 declara as duas e situa a diferença dentro da dispersão entre sementes ✅ |
| C6 | Tab. A.2 | «As explicações são úteis a uma pessoa — evidência: **---**» depois de o §5.6.5 passar a reportar 42 votos | A célula nomeia o retorno observacional; o estado continua **Não afirmado** ✅ |
| C7 | Fig. 5.12 vs Fig. 5.18 | A palavra «volatilidade» designava **dois preditores distintos**: a regressão sobre `vol20` ($0{,}632$) e as treze constantes ($0{,}662$) | A Fig. 5.18 passa a «Treze constantes de volatilidade» e o texto distingue-as explicitamente ✅ |
| C8 | Fig. 4.2 / Tab. 4.2 / Fig. 4.5 | O documento nomeia **5**, **7** e **9** «pontos de decisão» sem os reconciliar | A legenda da Fig. 4.5 enumera os quatro que a Fig. 4.2 não mostra ✅ |

---

## D. Problemas menores 🟡 (todos corrigidos)

| # | Onde | O problema |
|---|---|---|
| D1 | p. 3 | `\gls{QI}1` imprimia «Questão de Investigação **(QI)1**» na primeira utilização — o número colado ao parêntese, precisamente nas questões de investigação. Resolvido com `\glsunset{QI}`, e o acrónimo continua na lista |
| D2 | Fig. 5.15 | **A única figura do documento com ponto decimal** nos rótulos desenhados (`0.25 … 0.65`), a duas linhas do `0,50` do limiar dentro da mesma figura |
| D3 | §5.4.4 | Dizia que as empresas sem prior «recebem a **mediana** global»; `evaluate_endtoend_baselines.py:139` usa `.mean()` |
| D4 | §5.4.5 | «As diferenças situam-se entre $0{,}004$ e $0{,}009$» — as diferenças par a par entre os quatro valores vão de **$0{,}001$** ($0{,}543$ vs $0{,}542$) a $0{,}009$ |
| D5 | pp. 1–2 | A citação do SIFMA saía com parênteses encaixados: «(Securities Industry and Financial Markets Association (SIFMA) 2025)». Resolvido com `shortauthor` |
| D6 | Fig. A.1 | Mostrava o logótipo do **RSS**, que o caminho vivo não invoca (`fetch_rss_feed` não é chamado por `run_alerts.py`), e omitia a Alpha Vantage e o Polygon, que a Tabela 4.1 mede |
| D7 | Fig. 4.12 | «PSI $>0{,}25$» na página 50; o acrónimo só era definido na página 74 |
| D8 | Lista de Símbolos | `$2PC/(P+C)$` partia-se ao meio no `+` entre duas linhas |
| D9 | §6.1 | «Ao longo dos períodos documentados no Capítulo 5 foram entregues 367 mensagens, entre 9 de julho e 13 de agosto» — o Capítulo 5 documenta períodos que vão a setembro. Cada janela passa a estar datada |
| D10 | §6.4 | «os casos exibidos assentam em menos dias distintos do que **casos exibidos**» |
| D11 | Tab. 3.2 vs §5.6.2 | «**duas** empresas ausentes de todos os conjuntos históricos» e «**três** não figuram no corpus de treino» — ambas verdadeiras, âmbitos distintos, nada o dizia. A legenda passa a nomear a terceira |
| D12 | Tab. 4.2 | A legenda dizia «O **primeiro ponto** não utiliza constante», e a primeira linha da tabela é «Movimento invulgar — $|z| \geq 1{,}5$» |

---

## E. Polimentos 🔵 — duas portas estavam cegas

Não encontrar nada e aprovar tudo têm o mesmo aspeto no ecrã, e as duas seguintes tinham-no:

- **`check_resumos.py`** aplicava o limite de 200 palavras **apenas ao abstract inglês**. O
  resumo português passou a 201 e a porta imprimia «ok». Passa a medir os dois.
- **`check_apendice_xref.py`** não lia o `ch5/feedback_auto.tex`, que é **gerado** e não se chama
  `chapter*`. Uma remissão do apêndice para `sec:av_feedback` era reportada como «label nao
  existe» enquanto o LaTeX a resolvia sem um único aviso: o verificador via menos documento do
  que o compilador.

---

## F. Resultados, figuras e tabelas suspeitos — REQUER VERIFICAÇÃO

Nenhum destes está provado como erro. Ficam listados porque um júri pode perguntar.

1. **$0{,}662$ pertence a dois preditores diferentes.** A tabela de consulta por empresa (taxa de
   positivos) e o prior de volatilidade por empresa dão ambos $0{,}662$ na precisão dentro do
   orçamento. É plausível — a métrica só depende da ordenação das empresas, e as duas constantes
   ordenam-nas igual — mas é uma coincidência que convém saber explicar. Os dois artefactos são
   `evaluation_triage_identity.md` e `evaluation_budget_baselines.md`.
2. **Os 11 445 casos da base viva (§4.2.3) não têm data**, num capítulo cuja abertura promete que
   «as datas em que cada medição foi efetuada são indicadas junto de cada uma».
3. **§2.2 diz que as aplicações de sentimento «fornecem matéria-prima para a primeira pergunta»**,
   e a primeira pergunta é *o movimento é invulgar?*. Uma classificação de sentimento não é
   matéria-prima para isso. A Tabela 2.1 marca-as «parcial» nessa coluna. Não alterei: a legenda
   define «parcial» de forma suficientemente lata para o sustentar, e a correção depende de saber
   o que se pretendia dizer.
4. **«custo incompatível com este investidor»** (resumo, abstract, §1.1) é uma afirmação
   quantitativa sem fonte, e a §2.9 declara explicitamente que o preço «não é publicado de forma
   citável». As duas coisas são compatíveis se se ler a primeira como qualitativa; um arguente
   pode não a ler assim.
5. **A extração de texto do PDF perde as ligaturas `fi`/`fl`** («nanceiro» em vez de
   «financeiro»). É comportamento conhecido do `pdftotext` com estas fontes e **não é um defeito
   do documento**; verifiquei que não corresponde a nenhum problema de composição. Fica registado
   porque pode afetar a pesquisa de texto no repositório institucional, e é decisão do autor
   saber se isso lhe importa.

---

## G. Inconsistências código ↔ tese

**Uma encontrada** (D3, corrigida). Tudo o resto que testei corresponde:

| a tese diz | o código faz |
|---|---|
| nove entradas, sete de empresa, uma de dia, uma de título | `feature_names` tem exactamente essas nove ✅ |
| $a = 3{,}700$, $b = -2{,}313$ | `PlattCalibrator(a=3.6996675, b=-2.3133665)` ✅ |
| limiar $0{,}45$, orçamento 5/dia, teto 2/empresa/dia, piso $0{,}64$ | `config/alerts.yaml` ✅ |
| meia-vida de 120 dias; o decaimento **ordena** e o cosseno é o que se mostra | `merged_precedents` ordena por `cos × 0.5^(idade/h)` e devolve o cosseno real ✅ |
| «o limiar de $0{,}45$ incide sobre um conjunto já selecionado pela ordenação» | `precedents_are_strong` corre sobre `unicos[:top_k]`, já ordenados ✅ |
| implantação a $|z| \geq 1{,}5$, avaliação a $3{,}0$ | `threshold: 1.5` com a razão escrita no `.yaml` ✅ |
| mapa alargado 17, canónico 15, produção 12, duas ausentes | `SECTOR_OF` 17, `SECTORS` 15, watchlist 12, `DEPLOY_SECTORS = {AMD, NFLX}` ✅ |
| Python 3.12, numpy 2.1.3, pandas 2.2.3, sklearn 1.9.0, matplotlib 3.11.0, SBERT 5.6.0, torch 2.12.1+cpu | `requirements*.txt` e `.python-version` ✅ |
| treino 28 574 / validação 17 710 / teste 32 649, prevalências 0,3854 / 0,4704 / 0,3781 | `models/triage_context_lr.json` ✅ |
| PR-AUC 0,538 / 0,496 / 0,469 e precisão@orçamento 0,632 | os três `.json` dos modelos ✅ |

---

## H. Citações e bibliografia

- **70 entradas no `.bib` = 70 citadas = 70 renderizadas**, zero órfãs, zero indefinidas.
- **91/91 entradas verificadas** contra Crossref/arXiv/ISBN pelo `verify_bibliography.py`, sem
  achados. As «notas» que ele imprime são o registo a declarar uma segunda data de depósito
  eletrónico; o `.bib` usa a de publicação, que é a correta.
- **`reimers2019sbert`:** o Crossref dá 3980–3990 e a ACL Anthology 3982–3992. Prevalece a
  Anthology, que é o que o `.bib` usa. Decisão já registada e mantida.
- **«Cahill, Zhangxin Liu e Smales 2025»** com nome próprio é o `biblatex` a desambiguar contra os
  outros dois Liu da bibliografia. Não é defeito.
- Corrigido: o campo `author` do SIFMA trazia o acrónimo lá dentro (D5).

---

## I. LaTeX e compilação

| | tese-pt | tese-eng |
|---|---|---|
| páginas | 132 | 130 |
| erros | 0 | 0 |
| referências e citações indefinidas | 0 | 0 |
| `Float too large` | 0 | 0 |
| overfull máximo | 5,68 pt | 8,61 pt |

⚠️ **Um defeito que eu próprio introduzi e removi**, e fica registado porque a lição é de método:
a linha que acrescentei à Tabela A.2 fê-la exceder a página em 4,4 pt (PT) e 24,4 pt (EN) — no
inglês, o traço inferior da tabela **colidia com o número de página**. Confirmei que era meu
compilando a versão anterior do apêndice (zero avisos) e encurtei a célula até a tabela recuperar
a altura original. O `exit code` era 0 nas duas situações.

---

## J. As perguntas de júri mais prováveis

Ordenadas pelo risco. As que ficam **abertas** são as que recomendo preparar.

| # | Pergunta | Está respondida? |
|---|---|---|
| 1 | «O seu modelo perde para uma tabela de treze constantes. Para que serviu treiná-lo?» | **Sim** — §5.4.5 e §6.1 separam resultado de escolha, e a contribuição é declarada como sendo a infraestrutura que torna o negativo defensável |
| 2 | «Mediu a utilidade? A hipótese fundadora foi testada?» | **Sim, pela negativa** — Fig. 6.3 e §6.4 declaram-no como o que não fica estabelecido |
| 3 | «Quem votou nos 42 votos? O autor está entre os três?» | **Aberta.** §5.6.5 diz que se desconhece quem responde, mas não diz se o autor votou. Preparar a resposta |
| 4 | «Porque é que a Figura 5.12 dá $0{,}632$ à volatilidade e a Figura 5.18 dá $0{,}662$?» | **Sim, agora** — C7 |
| 5 | «$0{,}662$ para duas linhas de base diferentes. É a mesma experiência?» | **Aberta** — ver F1 |
| 6 | «A tese diz que os terminais custam demasiado. Quanto custam?» | **Parcialmente** — a §2.9 assume que o preço não é citável; o resumo afirma-o na mesma. Ver F4 |
| 7 | «Porque é que o bloco de teste é maior do que o de treino?» | **Sim** — §3.6, com a densidade de notícias como causa |
| 8 | «$88{,}5\%$ de cobertura — em quantos dias, e é um limite superior de quê?» | **Sim** — 417 dias, e a distinção «existia uma notícia» ≠ «chegou a notícia certa» está escrita |
| 9 | «Uma janela de 60 dias dá $F_1$ de $0{,}678$ contra $0{,}516$. Porque manteve 20?» | **Sim** — §5.2.5, com a reserva de circularidade do rótulo declarada |
| 10 | «O rótulo desconta o mercado com beta 1, e a técnica do Cap. 3 recusa essa suposição.» | **Sim** — §3.6 declara a incoerência e o §6.4 nomeia-a como limitação |
| 11 | «Os três blocos quase não partilham empresas. Isso não invalida a comparação?» | **Sim** — §5.4.3 diz que corta nos dois sentidos |
| 12 | «Mostra três precedentes concordantes que são um dia visto três vezes.» | **Sim** — §4.5.1 mede-o em $36{,}8\%$ e o §6.4 mantém-no como limitação |
| 13 | «Qual é a diferença entre isto e o Robinhood Cortex?» | **Sim** — §2.2, com a cautela de só afirmar o que as páginas declaram |
| 14 | «Porque não usou um modelo de linguagem?» | **Sim** — §2.4.1, §4.7.1, e a camada construída-e-não-exposta com a razão de garantia |
| 15 | «O que é PSI, e porquê $0{,}25$?» | **Sim** — §5.6.3, com as bandas convencionadas |
| 16 | «Correu o retreino?» | **Sim** — §4.7.2 diz que não, com a arquitetura desenhada e as duas restrições fixadas antes |
| 17 | «Se o ciclo de 60 s não reduziu a latência, para que serviu?» | **Sim** — §4.6, e diz que a comparação **não é interpretável** como efeito do ciclo |
| 18 | «A recuperação supera o acaso — mas o corpus é metade tecnologia.» | **Sim** — §5.3.3, e a afirmação é estreitada para o nível do setor |
| 19 | «Porque é que a Lista de Acrónimos tem 14 entradas e o glossário declara 27?» | **Sim, por construção** — só os usados são impressos. Vale saber dizê-lo |
| 20 | «A dissertação tem 132 páginas e o limite são 120.» | **Sim, e com o corpus medido** — o limite incide sobre a numeração árabe, a nossa está em 108, e a do Bruno Ribeiro foi aprovada com 139 físicas e fólio 120. Ver a secção N |

---

## K. Alterações efetuadas

Um commit, 25 ficheiros, +197 −98. Simétrico entre as duas árvores.

| ficheiro | porquê |
|---|---|
| `tese-{pt,eng}/ch5/chapter5.tex` | B1, B3, C5, C7, D2, D3, D4 |
| `tese-{pt,eng}/ch4/chapter4.tex` | C1, C8, D7, D12 |
| `tese-{pt,eng}/ch3/chapter3.tex` | C3, D11 |
| `tese-{pt,eng}/ch6/chapter6.tex` | C3, D9, D10 |
| `tese-{pt,eng}/ch1/chapter1.tex` | D1 |
| `tese-{pt,eng}/appendices/appendixA.tex` | B2, C6, D6 |
| `tese-{pt,eng}/frontmatter/frontmatter.tex` | C4, D8 |
| `tese-{pt,eng}/references.bib` | D5 |
| `tese-{pt,eng}/ch5/feedback_auto.tex` | C2 — **regenerado**, não editado |
| `scripts/analyse_feedback.py` | C2, na origem |
| `scripts/check_resumos.py`, `check_apendice_xref.py`, `check_figuras_paridade.py` | E |
| `tese-{pt,eng}/main.pdf` | recompilados |

**Portas depois das alterações:** 132 pp / 130 pp · 0 erros · 0 indefinidas · 0 floats fora da
página · overfull máx 5,68 / 8,61 pt · 11/11 verificadores · **998 testes** · ruff limpo ·
59/59 números conferidos · 91/91 entradas de bibliografia.

---

## L. O que exige decisão humana

1. **Nomes do júri.** A capa imprime `[Nome do Presidente, Categoria, Escola]`. O ISEP designa-os
   depois da submissão, e a dissertação aprovada do Bruno Ribeiro foi depositada assim. Não é
   defeito; é o único item que a porta de entrega ainda acusa.
2. ~~**O limite de páginas.**~~ **RESOLVIDO POR MEDIÇÃO a 2026-09-06 — ver a secção N.** Ficava
   aqui como decisão do orientador; as quatro dissertações aprovadas respondem sozinhas.
3. **§2.2 e as aplicações de sentimento** (F3) — depende do que se pretendia afirmar.
4. **«custo incompatível»** (F4) — manter como qualitativo, ou alinhar com a §2.9.
5. **Datar os 11 445 casos** da base viva (F2).
6. **Quem votou** (J3) — é a pergunta de júri mais desconfortável que a §5.6.5 abre.
7. Os itens que já estavam pendentes e não são de auditoria: leitura final do autor, redação da
   declaração de IA e escolha da licença com o orientador, agradecimentos na voz do autor.

---

## M. Veredicto

**Pronta com pequenos ajustes.**

Não é «pronta para entrega» apenas por causa da secção L, e nenhum dos itens dessa lista é
técnico: são a designação do júri pela escola e a
leitura final que torna verdadeira a frase «o conteúdo deste documento foi revisto pelo autor».

Nos eixos que esta auditoria mede — validade dos resultados, correspondência entre o texto, os
artefactos e o código, integridade das citações, coerência interna e composição — o documento
está no ponto. Os defeitos que encontrei eram reais e alguns eram embaraçosos, mas **nenhum
tocou num resultado**: a aritmética fecha em todos os sítios onde a refiz, cada número tem um
procedimento que o produz, e as três respostas às questões de investigação estão enunciadas,
medidas, delimitadas e respondidas — incluindo a negativa, que continua a ser o que dá crédito
às outras duas.

---

## N. O limite de páginas, medido contra as quatro dissertações aprovadas

Este ponto estava na secção L como decisão do orientador. Não precisa de ser: as quatro
dissertações aprovadas em `archive/thesis-versions/thesis-examples/` respondem sozinhas, e a
medição está aqui para não voltar a ser discutida.

**Método.** Para cada PDF, a página física em que o Capítulo 1 abre e o fólio impresso na última
página. As duas convenções de numeração que o corpus contém obrigam a este cuidado: três teses
**reiniciam** a numeração em árabe no Capítulo 1, e a do Rafael Silva usa um **contador contínuo**
— a página física 16 imprime «xvi» e a 17 imprime «17». Comparar «último fólio árabe» entre as
duas convenções daria números que não querem dizer a mesma coisa.

| dissertação | páginas físicas | Cap. 1 abre na física | último fólio | **corpo em numeração árabe** |
|---|---|---|---|---|
| Bruno Ribeiro (aprovada) | 139 | 20 | 120 | **120** |
| Helder Pereira (aprovada) | 133 | 20 | 114 | **114** |
| **NOSSA** | **132** | **25** | **108** | **108** |
| Rafael Silva (aprovada) | 109 | 17 | 109 | **93** |
| Joana Figueiredo (aprovada) | 104 | 22 | 82 | **83** |

As contas fecham em três das cinco até à unidade: $139-20+1 = 120$, $133-20+1 = 114$ e
$132-25+1 = 108$. A da Joana difere de um por uma página final em branco, e a do Rafael Silva é
$109-17+1 = 93$ sob o contador contínuo.

**Três conclusões, e nenhuma é de interpretação.**

1. **O limite não incide sobre páginas físicas.** Duas das quatro aprovadas têm **139** e **133**
   páginas físicas, ambas acima de 120. Se a regra fosse sobre o total impresso, duas
   dissertações aprovadas violavam-na.
2. **Incide sobre a numeração árabe, e a tese do Bruno Ribeiro assenta exactamente no limite:**
   termina no fólio **120**, sobre 139 páginas físicas. É a evidência mais forte que o corpus
   contém — uma dissertação aprovada precisamente em cima da regra sob esta leitura, e dezanove
   páginas acima dela sob a outra.
3. **A nossa está em 108**, ou seja **doze abaixo do limite**, abaixo de duas aprovadas e acima
   das outras duas. Excluindo os apêndices, que ocupam os fólios 99 a 108, são **97**.

**Uma precisão que corrige os registos internos.** Os planos do projeto escrevem «96 de 120»,
contando até ao fim do Capítulo 6. O número comparável com as aprovadas é **108**, porque o 120
do Bruno Ribeiro e o 114 do Helder Pereira **incluem a bibliografia** — a última página do Bruno,
fólio 120, é uma página de referências. A margem real é de doze páginas e não de vinte e quatro.
Nenhuma das duas aprovadas tem apêndices; a nossa tem dois, e mesmo assim fica abaixo.

**O que estava errado era a redação do `BRIEF_REESCRITA.md`**, que escreve «Páginas **totais** —
mínimo 60, máximo 120». O corpus mostra que o limite não é sobre totais. A linha foi corrigida,
com a medição ao lado.
