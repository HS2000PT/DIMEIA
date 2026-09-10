# Plano de execução da reescrita final

> Escrito a 2026-09-10, em resposta ao §12 do
> [`PROMPT_REESCRITA_FINAL.md`](PROMPT_REESCRITA_FINAL.md), que exige um plano aprovado antes de
> se escrever uma linha.
>
> **Estado: à espera de aprovação do autor.** Nada do Capítulo 3 em diante foi tocado.

---

## 0. Três medições que mudam a premissa, e uma delas obriga a mexer numa porta primeiro

O prompt foi escrito sobre números que eu próprio produzi, e medi-os outra vez antes de planear.
Duas correções e um achado.

### 0.1 A extensão está 17% acima do alvo, não ao dobro

O prompt afirma **57 383 palavras** contra um alvo que soma **41 000**, o que se lê como um corte
de 29%. Reconciliei as três formas de contar:

| medida | total | o que inclui |
|---|---:|---|
| bruta | 57 736 | tudo: comandos LaTeX, coordenadas TikZ, corpo das figuras |
| **prosa + legendas** | **47 939** | **o que o leitor lê** |
| prosa nua | 43 152 | retira o flutuante inteiro, legendas incluídas |

A coluna «palavras hoje» do prompt soma **exatamente 57 383**, ou seja é a contagem **bruta**; e
foi comparada com o alvo de ~34 000 do plano anterior, que era uma contagem de **prosa**. Era uma
comparação entre duas réguas diferentes, e inflacionou o problema.

**A medida honesta é 47 939, ou seja 6 939 palavras acima do alvo (17%).** O corte é real e é
grande, mas é um corte e não uma reconstrução.

### 0.2 As legendas são 10% do documento, e o prompt não as nomeia

**4 787 palavras em 69 legendas**, média de 69 palavras. No Capítulo 4 são **96 palavras por
legenda**, que é um parágrafo dentro de um flutuante. É o manípulo mais barato do documento: não
toca em nenhum argumento e não altera um número.

| capítulo | legendas | palavras | média |
|---|---:|---:|---:|
| 4 | 16 | 1 534 | 96 |
| 5 | 25 | 1 737 | 69 |
| 3 | 9 | 489 | 54 |
| 2 | 6 | 255 | 43 |
| 6 | 6 | 426 | 71 |
| 1 | 3 | 154 | 51 |
| Apêndice A | 4 | 192 | 48 |

⚠️ **E o primeiro detetor que escrevi para isto encontrou zero legendas**, porque procurava
`\caption{` e as 65 do documento usam `\caption[curta]{longa}`. É a classe «não encontrar nada e
aprovar tudo têm o mesmo aspeto no ecrã», e apanhou-me hoje.

### 0.3 ⚠️ A porta «todo o número tem origem» não vê nenhum decimal da árvore canónica

Este é o achado que muda a ordem de execução.

O `scripts/auditar_numeros.py` extrai decimais com o padrão `\d+\.\d{2,}` — **com ponto**. A
árvore portuguesa escreve todos os resultados com **vírgula em modo matemático** (`$2{,}173$`),
que é a convenção PT-PT e é obrigatória por outra porta. O `prosa_e_tabelas` retira flutuantes e
comentários e **não normaliza `{,}`**.

Consequência: a porta declara «todos os números da prosa e das tabelas têm origem conhecida»
depois de examinar **60 números**, quando a prosa e as tabelas contêm **212 decimais com
vírgula** que ela nunca extrai. Entre os invisíveis está **a contribuição nova por inteiro**.

**É exatamente a classe que a sessão 63 corrigiu no `check_tese_numeros`** («a tese escreve os
decimais com vírgula e o verificador procurava `36.8`»). Foi corrigida lá e nunca aqui.

Simulei o que a porta diria se os visse, porque alargar um verificador sem medir o que ele passa a
gritar produz um verificador que ninguém lê:

| dos 212 decimais com vírgula | quantos | o que fazer |
|---|---:|---|
| já têm fonte nas pastas que a porta lê | 180 | nada; alargar não lhes custa |
| existem **só** em `docs/design/` | 19 | a QI4 (`0,205`, `0,782`, `2,157`, `2,185`, `2,259`, `0,720`…). A porta lê `docs/evaluation/`, `docs/decisions/` e `config/`, mas **não** `docs/design/`, que é onde o resultado da QI4 vive |
| **sem fonte nenhuma** | **13** | triagem à mão, uma a uma |

Os treze: `0,143` · `0,226` · `0,235` · `0,289` · `0,336` · `0,454` · `0,462` · `0,970` ·
`0,994` · `0,997` · `1,71` · `2,11` · `2,725`.

Reconheço alguns do registo — `0,994` e `0,970` são cossenos de degeneração da QI4, `2,725` é o σ
da Tesla que a sessão 66 corrigiu, `0,336` parece a margem do oráculo (`0,968 − 0,632`) — mas
**não os vou dar por justificados de memória**. Cada um recebe fonte no artefacto ou uma entrada
na lista dos justificados com a razão escrita, como as dez que já lá estão.

**Porque é que isto vem primeiro.** Vou reescrever cada número do documento. Se a porta que
distingue um valor com fonte de uma gralha estiver cega à forma em que os números são escritos, a
reescrita perde a única rede que a protege. Corrigi-la depois de escrever é descobrir os defeitos
com o documento já montado.

---

## 1. Orçamento revisto, sobre a medida honesta

O alvo de páginas mantém-se: **≤ 120 físicas**. O de palavras passa a ser medido em prosa +
legendas, que é o que o leitor lê.

| capítulo | hoje | alvo | delta | leitura |
|---|---:|---:|---:|---|
| 1 Introdução | 1 922 | 2 500 | **+578** | **cresce.** Tem 4 páginas contra 8, 8, 8 e 10 das quatro aprovadas: é curto de mais, e a primeira impressão forma-se aqui |
| 2 Estado da arte | 7 999 | 6 500 | −1 499 | corta |
| 3 Métodos e materiais | 6 062 | 6 500 | **+438** | **cresce** um pouco: recebe a §3.7 nova («onde entra a IA») |
| 4 Implementação | 8 279 | 7 000 | −1 279 | corta, e 1 534 das palavras estão em legendas |
| 5 Casos de estudo | 14 816 | 12 000 | −2 816 | corta |
| 6 Conclusões | 7 005 | 4 500 | **−2 505** | **o maior corte, e é onde está o problema**: «o Cap. 5 mede, o Cap. 6 interpreta» |
| Apêndice A | 1 856 | 2 000 | +144 | fica |
| **total** | **47 939** | **41 000** | **−6 939** | |

Somando: **8 099 palavras a sair** nos quatro capítulos que cortam, **1 160 a entrar** nos três que
crescem.

**Onde estão as 8 099, em concreto e já levantadas:**

| origem | palavras estimadas | base |
|---|---:|---|
| as 18 redundâncias da fase E | ~2 500 | levantadas uma a uma no `TASKS.md`, com a secção que fica e a que sai |
| legendas acima de 60 palavras | ~1 800 | 69 legendas, média 69; cortar a média para 40 dá isto |
| compressão do Cap. 6 (D5) | ~2 500 | o capítulo interpreta e não deve remedir |
| apêndice: fundir A.1+A.2, A.5 a meia página (D10) | ~400 | |
| prosa que relê os rótulos de um visual ao lado | ~900 | a regra da sessão 66: antes de acrescentar um visual, ver se ele já lá está — e o inverso |

---

## 2. Plano capítulo a capítulo

Para cada um: o argumento em uma frase, as secções, os visuais, os números com a origem, e o que
sai.

### Capítulo 1 · Introdução — 1 922 → 2 500 palavras

**Argumento:** um investidor particular precisa de saber se um movimento é invulgar e se já
aconteceu antes, e nenhuma ferramenta gratuita lhe responde às duas com evidência que ele possa
conferir; este trabalho constrói e mede um sistema que o faz sem nunca prever.

**Secções:** contextualização (dados de 2025–2026) · o problema · as três perguntas do investidor
e as quatro questões de investigação · contribuições · estrutura.

**Visuais:** a figura de abertura (F6) — o mesmo dia da mesma empresa, à esquerda como uma cotação
o mostra e à direita como o sistema o entrega, com os valores **verbatim de um alerta real**.

**Números e origem:** os de contextualização (SIFMA, Gallup, CCAF) das fontes primárias já
verificadas; nenhum resultado próprio no Cap. 1 além das quatro respostas em uma linha.

**O que sai:** a afirmação de que as aplicações gratuitas «não respondem a nenhuma das três» — o
Cap. 2 nomeia duas que declaram responder, e a introdução prometia mais do que o corpo sustenta.
Sai também «não é método novo, é seleção e integração» (E3), que fica só no Cap. 2.

**O que entra:** as 578 palavras que faltam vão para o problema e para o público, que é a parte
que um júri lê primeiro e onde o documento está mais fino.

### Capítulo 2 · Estado da arte — 7 999 → 6 500

**Argumento:** as técnicas de que este sistema é feito existem e estão maduras; o que não existe é
a sua integração sob a restrição de não prever e de mostrar a evidência ao lado da afirmação.

**Secções:** mantém as nove, que estão bem ordenadas (o investidor e a atenção · ferramentas de
retalho · deteção de anomalias · representação de texto e recuperação · estudos de evento e
decomposição · raciocínio por casos · explicabilidade e confiança · aprendizagem em produção ·
síntese e posicionamento).

**Visuais:** as três atuais chegam. A matriz que pontua as ferramentas contra as três perguntas é
a peça que carrega o capítulo e fica.

**O que sai — 1 499 palavras:** o encolhimento de Vasicek explicado por extenso (E1: fica só na
§3.4); duas das três explicações do objetivo de treino do SBERT (E2); a fadiga de alertas (E4:
fica na §3.8.3); duas das quatro passagens sobre dívida técnica (E5: ficam §2.8 e §5.6.1); e a
compressão da prosa que repete a tabela comparativa.

**Ressalva:** o Cap. 2 é curto face às aprovadas (14 páginas contra 18, 20, 24 e 26) mas **não é
raso**. Cortar 1 499 palavras aproxima-o do limite inferior; se a leitura mostrar que perdeu
substância, o corte reduz-se e compensa-se no Cap. 6, que tem folga maior.

### Capítulo 3 · Métodos e materiais — 6 062 → 6 500

**Argumento:** cada técnica é apresentada pelo que serve, com o protocolo da sua avaliação fixado
**antes** de qualquer resultado, e com as garantias contra fuga do futuro no ponto onde são feitas.

**Secções:** as oito atuais **mais a §3.7 nova** («Onde entra a inteligência artificial neste
sistema», D1), que é a resposta à pergunta mais provável do júri e hoje está espalhada.

**Visuais:** a figura da §3.7 (F1, nova) · a janela deslizante · a linha do tempo do estudo de
evento · a curva do peso do encolhimento (F5, nova) · a Figura 3.4 tornada real com os pares já
citados, cosseno `+0,956` e `−0,086` (F8).

**Números e origem:** intervalos dos corpora dos manifestos `docs/design/*_manifest.json` com
`sha256`; `a=3,700` e `b=−2,313` do `.joblib` da calibração; os cinco eixos metodológicos.

**O que sai:** nada de substância. O crescimento é a §3.7 e a antecipação da nota que explica
`F1 0,516` contra `0,530` e amplitude `0,015` contra `0,017` (E15), que hoje aparece tarde e faz o
leitor pensar que há contradição.

### Capítulo 5 · Casos de estudo — 14 816 → 12 000

**Argumento:** quatro questões, quatro respostas, cada uma medida contra a alternativa mais forte
que existe e não contra a mais fraca.

**Secções:** desenho experimental e métricas · uma por questão · a decomposição · o sistema em
operação · síntese. **Renomear para «Avaliação»** (D9), que é o que o capítulo é.

**Visuais:** as 18 atuais são muitas para 12 000 palavras. Ficam as que carregam um veredicto;
entram as curvas de precisão-cobertura (F2, que existem nos artefactos e não no documento), os
histogramas do deslocamento da volatilidade (F4) e as figuras da QI4 (F9).

**Números e origem** — e é aqui que a §0.3 morde:

| questão | valores | artefacto |
|---|---|---|
| QI1 | amplitude `0,015` vs `0,344`; `F1 0,530` vs `0,269` e `0,280` | `evaluation_anomaly.md`, `evaluation_anomaly_ext.md` |
| QI2 | precisão@5 `0,395` / `0,422` / `0,196` / `0,204` / `0,117` / `0,200`; por setor com o acaso ao lado; `0,595` e `0,513` à escala; BM25 `0,521`; direção `0,708` vs `0,688` | `evaluation_results_composicao.md`, `evaluation_per_sector.md`, `evaluation_retrieval_fnspid.md`, `evaluation_retrieval_causal.md`, `evaluation_retrieval_bm25.md` |
| QI3 | PR-AUC `0,542` > `0,538` > `0,496` > `0,469` > `0,439` > `0,378`; orçamento `0,632` vs `0,379` = `1,67×`; treze constantes `0,662`; oráculo `0,968`; produção `0,486` IC `[0,403; 0,571]` | `evaluation_triage.md`, `evaluation_budget_baselines.md`, `evaluation_triage_identity.md`, `evaluation_ranking_producao.md` |
| QI4 | os quatro braços nos dois protocolos; o diagnóstico de degeneração | **`docs/design/qi4_resultado_2026-09-09.md`** e **`porta_colapso_direcao_v2_2026-09-09.md`** — as duas fora do alcance da porta |
| utilidade | `90` votos, `51` efetivos, `50` de `51` (`98%`, Wilson `90%–100%`), votante dominante `73%` | `evaluation_feedback.md`, **e a secção é gerada**: escreve-se no `analyse_feedback.py`, nunca no `.tex` |

**O que sai — 2 816 palavras:** o parágrafo repetido da §5.6 (a reconciliação entre os 48% e os
60% aparece duas vezes) · as três passagens sobre o rótulo favorecer a volatilidade reduzidas a
duas (E8) · «três ocasiões» ×3 → a figura basta (E10) · a prosa que reenumera os intervalos que a
`fig:av_acrescimo` já desenha · as legendas acima de 60 palavras.

**Correções factuais desta fase, e uma está obsoleta:** E11 (a mediana de R² diz «lista vigiada» na
§4.5.2 e «17 do mapa de setores» na §5.5 — uma delas está errada) e E13 (a PR-AUC `0,469` das
árvores só existe na tabela e não no texto). **O E12 caiu:** manda corrigir a aritmética dos votos
para `81−10−29−5`, e o artefacto publica hoje **90 e 51**; a entrada refere números superados e é
retirada com a razão escrita, não silenciosamente.

### ⚠️ MEDIÇÃO DOS CORTES DO CAP. 5 — 2026-09-10: cinco manípulos, nenhum entrega

O plano orçamentou **−2 816 palavras** no Cap. 5 e nomeou cinco sítios de onde as tirar. Testados
um a um contra o ficheiro:

| manípulo do plano | veredicto |
|---|---|
| o parágrafo repetido da §5.6 (reconciliação 48% / 60%) | **já feito.** A sessão 66 corrigiu-o. `48\%` e `60\%` não aparecem no Cap. 5 **em forma nenhuma** |
| a prosa que reenumera os intervalos da `fig:av_acrescimo` | **já feito.** A prosa diz só «A Figura apresenta os três intervalos» |
| E12, aritmética dos votos | **obsoleto.** Refere 81 e 42; o artefacto publica 90 e 51 |
| E13, PR-AUC das árvores | **premissa falsa.** A figura da §5.4.2 já desenha as seis famílias |
| legendas acima de 60 palavras (~1 800 palavras) | **não disponível** — ver abaixo |

**As legendas são onde vivem as ressalvas, e não onde vive o enchimento.** Medidas as catorze
acima de 60 palavras, que somam 1 147: **47%** do comprimento é ressalva por palavra-chave
(«não é uma medição», «por construção», «limite superior», população, janela) e apenas **5%**,
ou seja **54 palavras**, é descrição do que a figura já mostra — o único corte que não perde
nada.

⚠️ **E o meu próprio classificador subcontou as ressalvas.** Deu 0% à
`fig:av_pontaaponta`, cujas 85 palavras são **todas** ressalva quando lidas: reconcilia `0,375`
contra `0,379` («duas execuções do mesmo sorteio por procedimentos distintos», sem o que o leitor
encontra dois valores para a mesma coisa e nenhuma explicação), declara o oráculo «não
utilizável» e fixa o protocolo («todas escolhem conhecendo o dia completo»). Nenhuma dessas
frases casou com a lista de padrões. **A percentagem real de ressalva é superior a 47%, e o corte
seguro é próximo de zero.**

**Conclusão, e é sobre o plano e não sobre o capítulo:** o Cap. 5 **já foi comprimido** pelas
sessões 63 a 67, e o alvo de −2 816 assenta numa contagem de um documento que já não existe nessa
forma. Reduzi-lo a partir daqui exige decisão **estrutural** — menos figuras, ou fundir
subsecções — que é outra ordem de risco e é decisão do autor, não minha.

**O que fica medido para essa decisão:** o Cap. 5 tem 25 flutuantes e 14 862 palavras contando
legendas. Cortar figuras liberta as legendas com elas, mas cada legenda retirada leva as suas
ressalvas, e existe uma porta (`tradução: nenhuma ressalva perdida`) que o apanha — por desenho.

### Capítulo 4 · Implementação — 8 279 → 7 000

**Argumento:** o sistema que existe, o percurso de uma notícia da recolha à entrega, e as nove
decisões que ele toma antes de interromper alguém.

**Secções:** as oito atuais. **Decidir o destino da §4.8** (a camada de inteligência): promover ou
ligar à §3.7 nova (D9).

**Visuais:** entram a linha do tempo `353 min / 5 s / 8 dias` (F3) e o crescimento da base de casos
(F7); **sai a Figura 4.4** e alivia-se a Tabela 4.2 (D4).

**O que sai — 1 279 palavras:** **1 534 estão em 16 legendas** com média de 96 palavras, e é aí que
o corte é mais barato · as três causas do atraso ficam só na §4.6 (E7) · o defeito dos 36,8% fica
na §4.5.1 (E9) · o argumento RAG reduzido a dois sítios (E6).

**O que entra, e são frases:** o enquadramento na abertura sobre o estatuto das medições deste
capítulo (D3) · «57% calibrado + modelo sem discriminação demonstrada» (D2) · a justificação de o
modelo continuar implantado (D8) · a frase sobre o canal público não constituir prestação de
serviço (D11).

### Capítulo 6 · Conclusões — 7 005 → 4 500

**Argumento:** as quatro respostas, o que as delimita, e o que ficaria por fazer — e nada mais.

**Secções:** as seis atuais, comprimidas de 14 para ~10 páginas (D5).

**Visuais:** as duas que valem — `fig:con_futuro` (as dez linhas futuras agrupadas pelo que cada
uma exige) e `fig:con_fronteira` (o que o trabalho estabelece contra a hipótese fundadora que não
testou). As outras três saem.

**O que sai — 2 505 palavras, e a regra é uma só:** **o Cap. 5 mede, o Cap. 6 interpreta.** Sai
toda a remedição. Em concreto: «não é método novo» (E3) · a dívida técnica (E5) · as três causas do
atraso (E7) · o defeito dos 36,8% (E9) · «três ocasiões» (E10) · e as onze limitações passam de
prosa a tabela com uma linha cada.

⚠️ **O que NÃO sai:** as **onze** limitações continuam onze, e o número está prometido no texto.
A tabela 6.1 nomeia o remédio de cada uma; comprimir não é apagar.

### Apêndice A · Reprodutibilidade — 1 856 → 2 000

Fundir A.1+A.2, cortar A.5 a meia página, e **promover as linhas «Retirada» da matriz de evidência
para o corpo** (D10) — uma afirmação retirada tem mais valor no capítulo onde esteve do que num
apêndice.

---

## 3. As figuras: nove novas e todas as outras regeneradas

O critério de aceitação é o do §6 do prompt, e verifica-se **renderizando**, nunca pelo `exit
code`.

**A causa dos defeitos que reportaste é conhecida e é sistemática:** `minimum width` é um **piso e
não um tecto**, logo uma caixa com texto mais largo cresce e come o intervalo entre colunas. Foi
assim que os rótulos das setas se imprimiram por cima dos títulos na `fig:sis_inteligencia` e que
o TikZ desenhou uma seta ao contrário na `fig:con_cadeia`. **Todas as caixas com texto de
comprimento variável passam a `text width`**, e isso é uma regra e não um remendo.

As nove novas: F1 (onde entra a IA) · F2 (precisão-cobertura) · F3 (linha do tempo da latência) ·
F4 (deslocamento da volatilidade) · F5 (peso do encolhimento) · F6 (figura de abertura) · F7
(crescimento da base de casos) · F8 (Figura 3.4 real) · F9 (as da QI4).

**Nenhum valor escrito à mão num gráfico:** o gerador lê o artefacto, para que a figura e o texto
não possam divergir.

---

## 4. Ordem de execução, com paragem em cada passo

| passo | o que | porta |
|---|---|---|
| **0** | **corrigir o `auditar_numeros.py`** (ver vírgula, ler `docs/design/`) e triar os 13 sem fonte | a porta dispara sobre um defeito plantado **e** cala-se num corpus limpo |
| 1 | Cap. 3 · Métodos e materiais | compila, `check_escrita`, números |
| 2 | Cap. 5 · Avaliação | idem + `check_tese_numeros` |
| 3 | Cap. 4 · Implementação | idem |
| 4 | Cap. 2 · Estado da arte | idem + `check_references` |
| 5 | Cap. 1 e 6 | idem + as promessas de contagem |
| 6 | Apêndice e matriz de evidência | `check_apendice_xref` |
| 7 | figuras, uma a uma, renderizadas | inspeção visual + `check_figuras_lingua`, `check_figuras_paridade` |
| 8 | tradução inglesa, capítulo a capítulo | `check_bilingual_parity`, paridade dos resumos |
| 9 | slides e guia | `check_materiais`, `check_numeros_retirados` |
| 10 | releitura integral: orientador, depois arguente hostil | relatório de cada uma |

**No fim de cada passo:** `python scripts/check_entrega.py`, `python -m pytest`,
`python -m ruff check .`, `python scripts/_compilar.py`. Nenhuma tolerância afrouxada para passar.

---

## 5. O que não vou fazer, e porquê

- **Não corro medições novas.** As quatro lacunas B3–B6 continuam declaradas como não feitas, com
  a redação que a tese já usa. Está na §11.1 do prompt e é a armadilha mais perigosa dele.
- **Não escrevo os agradecimentos nem a dedicatória** como texto final. É voz tua; faço rascunho
  se pedires e digo que é rascunho.
- **Não preencho os nomes do júri** nem afirmo que a redação da declaração de IA foi confirmada
  com o orientador.
- **Não invento participantes.** A secção de utilidade é gerada do `evaluation_feedback.md`; o
  estudo moderado continua a ser a lacuna declarada de maior peso.
- **Não reescrevo as 98 construções «X, e não Y» que restam.** A sessão 66 mediu que não formam
  aglomerados e que cada frase reescrita num documento verificado é uma oportunidade de introduzir
  um defeito — duas em treze introduziram-no.

---

## 6. O risco, dito antes de começar

Faltam **17 dias** para 27/09. O documento atual tem 1 174 testes, 23 verificadores e ~120 números
conferidos contra artefactos. Uma reescrita repõe a superfície de risco: cada parágrafo novo é um
parágrafo por verificar.

As três mitigações que este plano tem: **a ordem** (métodos primeiro, porque fixa o vocabulário; os
capítulos que prometem no fim); **a paragem em cada passo**, para o erro não se propagar por seis
capítulos; e **o passo 0**, que devolve a rede antes de eu começar a escrever.

O que **não** mitigo: uma porta verde prova que nada partiu, não que a formulação nova é a certa.
Isso é a releitura, e o passo 10 existe para ela.
