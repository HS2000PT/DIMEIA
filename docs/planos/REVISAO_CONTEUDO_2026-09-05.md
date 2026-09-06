# Revisão de conteúdo, capítulo a capítulo — 2026-09-05

> Pedida pelo autor: *«reveres agora a tese do início ao fim, e focando-te desta vez no
> conteúdo mesmo»*, **antes** da tradução. Os achados são escritos **à medida que aparecem**,
> para a revisão sobreviver a um reinício de sessão e uma sessão nova pegar onde esta parar.

**Ordem de leitura:** Cap. 4 (sistema) → Cap. 5 (resultados) → Cap. 3 (métodos) → Cap. 6
(conclusões) → Cap. 2 → Cap. 1 → frontmatter. Os capítulos que descrevem o que o sistema
**faz hoje** vêm primeiro, porque é aí que uma afirmação desactualizada se esconde.

---

## Estado

| capítulo | lido | achados | corrigidos |
|---|---|---|---|
| 4 | integral | 4 | 4 |
| 5 | integral | 2 | 2 |
| 6 | integral | 3 | 3 |
| 3 | integral | 2 | 2 |
| 2 | integral | 1 | 1 |
| 1 | integral | 0 | — |

**Doze achados, doze corrigidos. Três eram meus, de ontem.** E três falsos alarmes meus,
todos apanhados antes de reportar.

**Os seis capítulos foram lidos por inteiro.** O que resta por fazer não é revisão de
conteúdo: é a tradução, e a decisão do título.

---

## Achados

### C4-1 — A figura do ciclo de vida estava metade em cada língua, e uma caixa a meio de uma tradução

`fig:sis_lifecycle`, `tese-pt/ch4/chapter4.tex`. Rótulos **desenhados**:
`labelled dataset`, `training`, `log of every decision` em inglês, ao lado de
`artefacto versionado`, `teste`, `retreino: ausente` em português — e uma caixa
**a meio de uma substituição**: `the `**`mesmo`**` model, in production`.

É a mesma classe do `declará-claradas` da sessão 61: **compila a zero erros**, porque é
texto válido, e só se vê a ler o que está desenhado.

⚠️ **E o `check_figuras_lingua.py` estava CALADO sobre ela**, tendo sido escrito ontem
exactamente para esta classe. A causa é estrutural e vale mais do que o defeito: o
verificador exige encontrar as **duas** línguas, e o lado português é uma **lista fechada**
de vocabulário. Nenhuma das palavras desta figura — `artefacto`, `versionado`, `teste`,
`mesmo`, `retreino`, `ausente` — estava na lista, logo a figura contava como
monolingue inglesa. **Um verificador cego e um corpus limpo são indistinguíveis no ecrã**,
que é a lição que a sessão 63 já tinha pago no `check_tese_numeros`.

**Corrigido nos dois sítios**, e a correcção do verificador foi verificada com a figura
original plantada.

**E a correcção do verificador encontrou logo uma segunda:** `fig:av_rotulos`, no Cap. 5,
tinha `célula usada` desenhada sobre um eixo rotulado `horizon (days)`. Só apareceu por
causa do sinal novo, que **não depende de vocabulário nenhum** — a ortografia portuguesa
(`ç`, `ã`, acentos) num rótulo desenhado. Uma lista fechada nunca a teria apanhado.

**Controlo:** com o rótulo original replantado, o verificador dispara e nomeia a figura.

### C5-1 — E a mesma classe tinha **três** cegueiras no verificador, não uma

Ao corrigir a lista fechada apareceu `fig:av_rotulos`. Ao ler a secção da deriva apareceu
`fig:av_deriva`, que o verificador continuava a não ver **por duas razões independentes**:

1. **`\gls{}` dentro de um rótulo de eixo.** O padrão era `\{([^{}]+)\}`, que para na
   primeira chaveta interior: `xlabel={\gls{PSI} entre o bloco de treino e o de teste}`
   **não casava de todo**, logo um eixo em português ao lado de escalas inglesas passava.
2. **Os rótulos de escala nunca eram olhados.** `xticklabels` e `yticklabels` são texto
   **desenhado** e não constavam do padrão. A figura da deriva tem
   `5-day momentum, Same-day return, Headline length` desenhados à esquerda, e era esse o
   lado inglês da mistura — invisível ao verificador.

**Três figuras corrigidas** (`fig:sis_lifecycle`, `fig:av_rotulos`, `fig:av_deriva`) e
três defeitos do verificador, cada um encontrado só depois de o anterior ser corrigido.
**A lição não é a lista: é que um verificador que só olha para parte do que é desenhado
dá a mesma saída de um corpus limpo.**

### C5-2 — Verificado e **não** é defeito: as três empresas fora do corpus de treino

`ch5:1385` afirma que a AMD, a Netflix e a Meta não figuram no corpus de treino. O registo
do projeto nomeava só duas (sessão 61). Conferido: são coisas diferentes — a sessão 61
tratava do mapa de setores (`SECTORS`), onde a Meta **está** e as outras duas não; o
corpus indexa a Meta como `FB`, pelo que sob o símbolo `META` está mesmo ausente
(`docs/evaluation/kb_fnspid_build.md`). **As duas afirmações são compatíveis.** Fica
registado para ninguém voltar a gastar tempo aqui.

### C4-2 — A prosa prometia **quatro** pontos de decisão e a figura desenha **cinco**

`ch4:220`, imediatamente antes da `fig:sis_caminho`. As caixas a tracejado são cinco —
*nomeia a empresa*, *é recente*, *evidência suficiente*, *triagem acima do piso*, *já
enviada hoje* — e o exemplo trabalhado que se segue atravessa as cinco, uma a uma.

É a classe que já mordeu duas vezes (a legenda das cinco portas na sessão 61, a contagem
das ocasiões na 63), e incide sobre **o núcleo do trabalho**: os pontos de decisão são o
que a dissertação tem de próprio. Corrigido para cinco.

**Verificadas e certas**, na mesma varredura: as cinco componentes do sistema, as nove
etapas, as sete entradas de nível de empresa em nove, as três causas do atraso, as três
leituras da ablação, as duas razões da janela, as duas precisões da predição conforme e
as duas propriedades da decomposição. O varrimento das promessas de contagem devolveu
**70 candidatas e um único defeito.**

### C6-1 — O Cap. 6 abria a citar a janela que o Cap. 5 declara **superseda**

`ch6:15`. O primeiro parágrafo que descreve o registo operacional do sistema dizia
«registadas $4\,366$ decisões de triagem», e o Cap. 5, para o qual remete, chama a essa
janela **«anterior e mais curta»** e reporta $36\,925$ como a medição principal. O
capítulo que resume estava a citar o número que o capítulo resumido substituiu — por um
fator de oito, e para baixo.

⚠️ **E as duas contagens da mesma frase são de janelas diferentes**, que é a forma exacta
do defeito da Figura 4.3: as $367$ mensagens são de 9 de julho a 13 de agosto e as
decisões de uma janela mais ampla. A frase passa a **datar as mensagens e a dizer que a
outra janela é mais ampla**, em vez de as apresentar como um par.

### C6-2 — «as seis peças» contra as **sete** que o Cap. 4 enumera

`ch6:30` remete para a `sec:sis_ciclo` e conta seis; a secção diz «sete componentes» e tem
sete `\item`. A que faltava é **a declaração do rótulo como decisão** — a peça que sustenta
a terceira verificação da QI3, e das mais defensáveis do conjunto. Acrescentada.

### Método — dois falsos alarmes meus, os dois apanhados antes de reportar

1. A legenda da figura dos rótulos promete «faixa verde» e eu vi só uma anotação de texto.
   **Existe**: `\path[fill=igGreenLight] rectangle`, no mesmo bloco.
2. Julguei uma frase da QI3 partida a meio e sem citação. **O meu próprio filtro de
   leitura** (`grep -v` de linhas começadas por barra) apagava a linha do `\autocite`, que
   levava as duas citações e metade da frase. **Ler a prosa em bruto, não filtrada.**

### C6-3 — O parágrafo da latência contradizia-se a si próprio em duas linhas

`ch6:432` afirmava a negrito que **«a sua causa não está identificada»** e a frase seguinte
diz **«Restam três causas que o histórico não separa»**. A tabela de limitações repetia a
primeira versão. O Cap. 4 identifica as três, nomeia-as e mede uma delas com um exemplo.

O que é verdade é que estão **identificadas e não separadas**, e a diferença não é de
estilo: «não identificada» convida à pergunta *então investigaram?*, e a resposta é que
sim. Corrigido nos dois sítios.

**Cap. 6 verificado e certo no resto:** os quatro objetivos batem um a um com os quatro do
Cap. 1 (e as três QI também); o item 1 do trabalho futuro remete para o «terceiro item
desta lista» e o terceiro é mesmo o do julgamento humano; a distinção entre utilidade
percebida e decisão melhor está feita nos dois sítios.

### C4-3 — ⚠️ O achado maior desta passagem é **meu**: os números da figura das razões vinham de um registo que rola

A figura que acrescentei ontem imprimia `98,0%` para o orçamento, `0,1%` para o limiar de
semelhança e `1,1%` para a repetição. **Três defeitos, e o terceiro é o pior:**

1. **Vinham de uma leitura única de um registo que guarda três dias.** Medido em seis dias
   — 19 a 21 de agosto e 3 a 5 de setembro — o que o orçamento elimina vai de **77,7% a
   99,8%**, e a repetição de **0% a 14,0%**. Imprimir `98,0%` como se fosse uma propriedade
   do sistema é o mesmo erro que a própria Figura 4.3 existia para corrigir, cometido por
   mim no dia seguinte.
2. **Não tinham fonte em `docs/evaluation/`**, contra a regra do projeto, e por isso o
   `check_tese_numeros` deixava-os passar **sem os ver** — 55/55 batia certo enquanto quatro
   números sem origem estavam impressos.
3. **Escrevi que o piso escalonado «deixou de vetar». É falso.** O código aplica-o ao
   segundo alerta da mesma empresa no mesmo dia (`run_alerts.py:457`), e o comentário do
   `config/alerts.yaml` di-lo. O que é verdade é que **nunca atuou** nos seis dias, porque o
   orçamento se esgota antes de uma empresa alcançar um segundo alerta. São afirmações
   diferentes: uma diz que o mecanismo foi desligado, a outra que não chega a ser alcançado.

**⚠️ E corrigi-lo destapou o mesmo defeito no gerador.** O `snapshot_funil.py` **reescrevia
o ficheiro inteiro**: corrê-lo hoje apagava os três dias de agosto e a amplitude deixaria de
existir. É a classe que a sessão 57 documentou **duas vezes** — um artefacto regenerável
regenerado noutro dia é indistinguível de um correcto. Passa a **acumular**: cada dia entra
quando o comando corre e nunca é retirado, e o ficheiro diz quantos dias tem.

**Corrigido:** a coluna passa a amplitude com a janela nomeada; a legenda diz que a unidade
é a **avaliação** e não a notícia; os quatro números entraram no manifesto (55 → 59); e a
legenda curta dizia «As sete regras» com nove filas.

**Controlo:** os três defeitos de figura replantados um a um, e o verificador dispara nos três.

---

## Segunda passagem — Cap. 3 e Cap. 2

### C3-1 — A tabela de conjuntos declarava o registo de decisões pela janela curta

`ch3:120`. A linha dizia «2026-07-22 a 2026-08-15, $4\,366$ decisões». É a mesma janela que
o Cap. 5 chama **«anterior e mais curta»**, e a medição que o capítulo usa cobre
**2026-07-22 a 2026-08-20 com $36\,925$**. O inventário dos dados declarava menos dados do
que a análise consome, e é a mesma incoerência de C6-1, uma camada atrás. Corrigido contra
`evaluation_gate_selectivity_unicos.md`, que é a fonte que dá a janela.

### C3-2 — «questões» onde o Cap. 2 diz «perguntas», e o termo colide

`ch3:36` dizia que as três primeiras decisões correspondem «às questões enunciadas no
Capítulo 1». No documento, **«questões» é o termo técnico das questões de investigação** e
as do investidor chamam-se «perguntas» — é assim no Cap. 2 e na Figura 2.1. Lido como
questões de investigação, a frase fica errada, porque a decomposição **não** dá origem a
uma. Passa a nomear as três perguntas do investidor.

### C2-1 — A tabela afirmava um preço que a síntese do mesmo capítulo declara não citável

`ch2:88` dava «milhares por ano» para o terminal profissional, e `ch2:626` diz que **«o seu
preço não é publicado de forma citável, e é a indisponibilidade, e não um valor concreto,
que sustenta o argumento»**. Uma célula com um valor sem fonte, contradita 538 linhas
adiante pelo próprio capítulo. Passa a «não publicado», que é o que se sabe.

### C4-4 — ⚠️ O artigo afirma uma camada generativa que a tese não menciona em lado nenhum

O artigo diz que o sistema *«does implement a grounded generation layer»*, **«implemented and
evaluated but not exposed»**, e reporta quantidades sobre ela. A tese só diz que o sistema
**não** integra um modelo de linguagem no texto entregue — verdadeiro e insuficiente: um
arguente que leia os dois documentos encontra no artigo trabalho medido que a dissertação
não reivindica.

Verificado antes de escrever: a camada existe (`investigator/intelligence/`, cinco módulos),
tem testes próprios, tem artefacto de avaliação, e **não está exposta** — o próprio
`api/main.py` regista que as rotas foram retiradas e o código não.

**A correcção é na tese e não no artigo**, pela razão já decidida: remover do artigo apagaria
trabalho medido, e descrever a camada como entregue descreveria um produto que não existe.
A tese ganha um parágrafo na mesma formulação estreita — implementada, avaliada, não
exposta — com a razão que decide, que é a **natureza da garantia** e não o desempenho da
verificação: o texto entregue parte de um vocabulário fechado, a camada gerada enumera o que
proíbe, e enumerar o proibido é mais fraco do que enumerar o permitido. Mais uma remissão do
Cap. 2 e uma linha na tabela de origem dos resultados do apêndice.

**Verificado e certo no Cap. 3:** as seis versões de biblioteca batem uma a uma com os
ficheiros de dependências; a conversão de retorno logarítmico (`exp(0,1982) − 1 = 21,92\%`);
a repartição da AMD soma exacto e o seu retorno simples confere; o decaimento de meia-vida
(`2^{-365/120} = 0,12`). **No Cap. 2:** os produtos que o Cap. 1 promete nomeados estão
nomeados; a atribuição a Engle e Bollerslev é correcta, incluindo a ressalva de que ambos
formalizam sobre séries de inflação.

---

## Terceira passagem — o que faltava do Cap. 5 e do Cap. 2

Nenhum achado novo. Fica registado o que foi **conferido a valer**, para ninguém repetir:

- **A aritmética que a tese mostra fecha toda.** $F_1$ do *z*-score
  ($2 \times 0{,}381 \times 0{,}800 / 1{,}181 = 0{,}516$) e da regra fixa ($0{,}218$); o Brier
  de anunciar sempre a unidade ($1 - 0{,}378 = 0{,}622$); a conversão de retorno logarítmico
  ($\exp(0{,}1982) - 1 = 21{,}92\%$); a repartição da AMD, que soma exacto e cujo retorno
  simples confere; o decaimento de meia-vida ($2^{-365/120} = 0{,}12$).
- **As seis versões de biblioteca** do Cap. 3 batem uma a uma com os ficheiros de dependências.
- **Cap. 2 sem mais achados:** a atribuição a Engle e Bollerslev é correcta e traz a ressalva
  de que ambos formalizam sobre séries de inflação; a secção da calibração **declara que a
  fonte citada não favorece a opção tomada** e remete para a medição; os produtos que o
  Cap. 1 promete nomeados estão nomeados.

### Terceiro falso alarme meu, apanhado a tempo

A figura da decomposição diz «mediana $0{,}487$» e o apêndice diz $0{,}460$. **São
quantidades diferentes** e a fonte tem as duas: $0{,}487$ é a mediana da quota do movimento
atribuída à empresa, $0{,}460$ é a mediana do $R^2$ do ajuste. A tese distingue-as no
parágrafo seguinte, e chega a dizer que o segundo «não é o coeficiente do ajuste por mínimos
quadrados». **Ler o parágrafo seguinte antes de reportar** — é a mesma lição da sessão 64.

---

## `tese-eng/` — árvore inglesa completa

Os seis capítulos, o *front matter*, o glossário e os dois apêndices estão traduzidos. A
árvore compila a **130 páginas, 0 erros**.

**Quatro conversões mecânicas antes de traduzir**, e a ordem entre duas delas decide: `babel`
para `main=english`, a opção da classe, **441 decimais** de vírgula para ponto e **34
milhares** de espaço fino para vírgula — nesta ordem, porque a inversa faria `79 753` sair
como `79.753`, que em inglês se lê como setenta e nove vírgula sete.

### Três adaptações que não são tradução, cada uma com a razão escrita no ficheiro

1. **O parágrafo da convenção linguística do Cap. 1 foi retirado.** Explica porque é que o
   interior das figuras está em inglês e a prosa em português; aqui as duas estão na mesma
   língua. ⚠️ Terá de sair também da árvore PT quando as figuras lá forem convertidas.
2. **O parágrafo equivalente no Cap. 4**, que justifica a mensagem do sistema estar em
   inglês. A decisão de desenho que ele defende — citar os títulos sem traduzir — fica, e
   passa a ser dita directamente.
3. **`\gls{QI}` mantém a chave e imprime `RQ`**; `\gls{IA}` foi remapeado para `\gls{AI}`,
   senão a lista de acrónimos imprimia a mesma sigla duas vezes. E os dois resumos trocaram
   de lugar.

### C5-3 — Sete rótulos **desenhados** escaparam à conversão numérica

A conversão só apanhou a forma de modo matemático, `{,}`. Ficaram sete rótulos com vírgula
simples — `0,381`, `0,516` — e um deles, **`0,800 nos dois`**, era ao mesmo tempo vírgula
decimal e português. Num documento inglês a vírgula lê-se como separador de milhares.

### O ficheiro gerado saiu do gerador, e não de uma edição à mão

O `ch5/feedback_auto.tex` é **gerado** e diz na primeira linha para não ser editado.
Traduzi-lo no destino faria a tradução desaparecer na corrida seguinte — a mesma disciplina
que a sessão 63 aplicou à remissão para o Cap. 6. O `analyse_feedback.py` ganhou
`--lingua {pt,en}`; **toda a lógica fica intacta** (mínimo de vinte votos, salvaguarda do
votante dominante, intervalo de Wilson, recusa de reportar proporção abaixo do mínimo).

⚠️ E correr o gerador reescreveu o relatório `.md` com o carimbo de hoje sobre dados
idênticos. **Reposto:** um artefacto que muda só na data sugere uma medição nova que não
houve.

### O que fica por fazer

As **figuras da `tese-pt` continuam em inglês**, e é a pendência que o autor nomeou como
imperativa. A ordem que ele fixou é esta: primeiro a `tese-eng` completa, depois converter as
figuras da PT. As figuras inline em TikZ já estão traduzidas nos rótulos desenhados da árvore
inglesa; o que falta são as **34 figuras em PDF/PNG** de `figures/`, que são geradas por
`scripts/figures/` e por capturas, e que hoje as duas árvores partilham.

---

## As figuras da `tese-pt` em português

Feita a conversão que o autor tinha fixado como imperativa. **172 rótulos desenhados** em 38
figuras inline, mais o único gráfico gerado, que passou a sair nas duas línguas do mesmo
gerador. As armadilhas de tradução (o *bilião* que vale mil vezes mais em português, o
trocadilho da figura dos *embeddings*, os títulos de notícia citados que ficam em inglês
porque o corpus é inglês) estão registadas acima.

### O que a inspeção visual encontrou, e que nenhum verificador via

O log do LaTeX ficou limpo do princípio ao fim — máximo de 5,68 pt de *overfull* — e mesmo
assim havia cinco defeitos nas figuras. **Nenhum deles produz aviso**, porque dois nós
sobrepostos são composição válida.

1. **Os números 5 e 9 da Figura 4.2 estavam desenhados por cima das setas.** As duas caixas
   alcançadas por uma seta vertical recebiam o número `above`, que é exatamente onde a seta
   entra: os dois algarismos saíam riscados a meio. Pré-existente e nas duas árvores.

2. **As contagens de alerta da Figura 4.3 caíam sobre a linha do eixo, e um zero riscado
   lê-se como nove** — nas quatro empresas que não alertam, que são precisamente aquelas
   cuja leitura a figura existe para sustentar. A causa não era a posição do rótulo: era a
   margem esquerda, que não deixava espaço entre o eixo e o marcador do zero. ⚠️ Duas
   tentativas de correção falharam antes desta e as duas só se viram a renderizar — por
   baixo do marcador o rótulo assentava no eixo horizontal; por cima ficava a meio caminho
   entre duas linhas, e o leitor atribuía-o à empresa errada, que é **pior** do que o
   defeito original.

3. **A Figura 5.16 nomeava uma só das suas duas séries.** `ytick={1.2}` desenha uma marca a
   meio caminho entre as duas linhas e deixa a outra sem nome, num painel cuja leitura
   inteira depende de distinguir as mantidas das suprimidas. Um caráter — `{1,2}` é a lista
   de duas marcas que o painel precisa. Pré-existente e nas duas árvores.

4. **Os eixos usavam ponto decimal e os valores anotados vírgula, na mesma figura.** 49
   rótulos de eixo e 34 valores desenhados. Nenhuma das duas convenções está errada
   isoladamente, e é essa a razão pela qual estiveram lado a lado sem ninguém dar por isso.
   ⚠️ Só se tocou em `xticklabels`/`yticklabels`: uma vírgula dentro de `xtick=` ou de
   `coordinates` separa argumentos e parte a figura.

5. **`metric value` num eixo português e `somam` dentro da tese inglesa** — uma fuga em cada
   sentido.

⚠️ **Dois falsos alarmes meus, e os dois vinham de olhar em baixa resolução.** A 100 dpi o
rótulo rodado do eixo da Figura 1.1 aparece com traços por cima que se leem como colisão, e
a Figura 4.12 parecia ter texto sobreposto. A 400 dpi as duas estão limpas: era
rasterização. Ampliar antes de corrigir o que está certo.

### O verificador de línguas tinha a cegueira simétrica da que já tinha sido corrigida

A 2026-09-04 o lado português da deteção passou a ter um sinal independente de vocabulário —
a ortografia acentuada — porque uma lista fechada tinha deixado passar `artefacto
versionado`. **O lado inglês ficou como estava**, e a Figura 4.12 atravessou o verificador
com `promotion gate` e `does not win: log and discard` ao lado de doze rótulos portugueses:
nenhuma dessas palavras constava da lista, e o lado português disparava pela ortografia.

Duas correções, de naturezas diferentes:

- **No verificador existente**, dois sinais que não dependem de saber vocabulário: palavras
  funcionais inglesas inequívocas e terminações que o inglês tem e o português não (`-tion`,
  `-ment`, `-ing`, `-ness`, `-ity`, `-ly`, `-ed`). ⚠️ Três falsos positivos apareceram de
  imediato e **todos eram do verificador**: `no` é palavra portuguesa e entrou na lista de
  palavras funcionais inglesas ao lado de `not`; `Isolation Forest` disparava o sufixo
  `-tion` sendo nome próprio de um método; e o material entre aspas — títulos de notícia de
  um corpus inglês, que a política manda manter — disparava `-ed` em `gained`. Um
  verificador que acusa figuras corretas gasta-se, porque se deixa de olhar para ele.

- **Um verificador novo, `check_figuras_paridade.py`**, que não sabe vocabulário nenhum.
  Existem duas árvores que são traduções uma da outra: se o mesmo texto desenhado aparece
  nas duas, ou é nome próprio, ou é número, ou é material citado — ou escapou à tradução.
  ⚠️ **A direção da lista é o que distingue os dois.** A lista do verificador de línguas é
  de *acusação*, e fechá-la cega-o; a deste é de *isenção*, logo um rótulo que ninguém
  previu faz a verificação **falhar** em vez de passar. Foi ele que encontrou o `metric
  value` e o `somam`, que os dois verificadores de vocabulário não viam.

⚠️ **Um `git checkout` meu apagou trabalho por commitar.** Corri-o para desfazer um defeito
plantado num teste de controlo, e ele devolveu o `ch4` ao último commit — levando com ele a
tradução das figuras do capítulo e as três correções desta passagem. A tradução recuperou-se
por o script que a produziu estar guardado; o resto foi refeito. **A regra é guardar o
ficheiro antes de plantar o defeito e restaurar dessa cópia**, que foi o que fiz nos dois
controlos anteriores e não neste.

---

## O título, decidido a 2026-09-06

> **Explicar sem prever: deteção de anomalias e recuperação de precedentes em alertas
> financeiros verificáveis**

Em inglês, na capa interior: *Explaining without predicting: anomaly detection and precedent
retrieval for verifiable financial alerts.*

⚠️ **A decisão mudou porque a premissa em que a anterior assentava é falsa.** O registo da
sessão 61 afirma que «as quatro dissertações aprovadas nomeiam todas a sua máquina», e foi
isso que pôs «InvestiGator» na capa. Medido nas quatro capas: **nenhuma usa nome de
produto** — Bruno é técnica + domínio + restrição, Helder é tipo de arquitetura + finalidade
+ domínio, Joana é metáfora, dois pontos, substância, e Rafael é descrição simples. E
**nenhuma usa subtítulo**: todas imprimem um título único, que é também o formato que a
submissão ao ISEP recebe.

### Porque é o menos arriscado

Cada termo tem onde se sustentar, e o que não está lá conta tanto como o que está:

| no título | onde se sustenta |
|---|---|
| deteção de anomalias | QI1, respondida **sim** — amplitude de $0{,}015$ contra $0{,}344$ |
| recuperação de precedentes | QI2, respondida **sim** — acima da taxa-base nos cinco setores |
| verificáveis | a contribuição estabelecida, o lado esquerdo da Figura 6.3 |
| sem prever | a restrição fundadora do Capítulo 1 |

**Nada no título toca a triagem**, que é o resultado negativo. Um título com «modelo
treinado» ou «priorização» prometeria exatamente a única coisa que a dissertação reporta
como não tendo funcionado, e é aí que uma defesa cai. «Sem prever» desarma ainda a pergunta
mais perigosa que existe contra este trabalho, antes de ela ser feita.

**106 caracteres**, dentro do intervalo das três longas aprovadas (115, 116 e 123); o
anterior tinha **74**, abaixo do intervalo. A forma — metade evocativa, dois pontos, metade
substantiva — é a da Joana, que passou, e a dela é bastante mais decorativa.

O nome do sistema **não desaparece**: continua no resumo, no Capítulo 4 e no produto. Sai
apenas da capa, que é onde nenhuma das aprovadas o põe.

### O risco que esta escolha tem, dito em voz alta

Um título que declara o que o trabalho **não** faz pode ser lido como defensivo. Aqui não é
uma desculpa — é a decisão de desenho de que tudo o resto decorre — mas quem lê a capa ainda
não sabe isso. A alternativa que o evitava trocava «verificáveis» por «para o investidor
particular», e perdia a contribuição para ganhar o público, que já está na primeira frase do
resumo.

### Propagação

Capa PT e EN, capa dos slides (que passa a ser o título partido nos dois pontos, palavra por
palavra), a citação da dissertação no `CITATION.cff` — que ainda trazia o título de junho,
duas gerações atrás — e a abertura do guião de defesa, que mandava dizer uma frase que agora
**é** o título.

⚠️ **E o subtítulo foi retirado, não esvaziado:** o `meia-style.cls` decide com
`\ifdefined\tsubtitle`, pelo que um subtítulo vazio continuaria definido e imprimiria uma
linha em branco com a quebra.

### Um defeito de porta apanhado a propagar

O `check_tese_pt` acusava «PDF anterior a slides/main.pdf». Os materiais de estudo vivem
dentro de `tese-pt/` desde a reorganização, e o `.pdf` conta como extensão de fonte porque as
figuras são PDF — logo o PDF **dos slides** era lido como figura da dissertação. ⚠️ E não era
cosmético: recompilar os slides passava a exigir recompilar a tese, e o `latexmk` **não
recompila um documento que não mudou**, pelo que a porta acusava algo que compilar não
resolvia. A regra nova não conhece nomes de pastas: **uma subpasta com o seu próprio
`main.tex` é outro documento**. Verificada nos dois sentidos — uma fonte verdadeira continua
a invalidar o PDF.

---

## O artigo lido contra a dissertação revista (2026-09-06)

O artigo foi escrito **antes** da revisão de conteúdo que corrigiu doze defeitos na tese, e
herdou dois deles. A porta de números passava, porque nenhum dos dois é um número inventado.

### (1) Duas janelas fundidas numa frase

O artigo dizia: «over the documented period it delivered $367$ messages and recorded
$4{,}366$ triage decisions». A frase paralela da tese (`ch6:15`) diz o contrário com
cuidado: $367$ mensagens **entre 9 de julho e 13 de agosto**, e $36\,925$ decisões **sobre
uma janela mais ampla**.

⚠️ **E o que primeiro pareceu ser o defeito não era.** Julguei que o artigo citava um número
que a tese já não tem — e a tese **tem** o $4\,366$, duas vezes, na §5.6.1, declarado como
«uma janela anterior e mais curta». O defeito não é o valor: é o «over the documented
period», que junta ao mesmo período uma contagem que pertence a outro. Nenhuma verificação
numérica apanha isto, e foi por isso que ler o artigo contra a tese valeu a pena.

### (2) O número mais favorável de duas subpopulações

O artigo dizia que entre a deteção e a entrega a mediana é de **um segundo**. O
`evaluation_latency.md` traz esse valor numa linha só — a do agendador do GitHub Actions,
com $n=28$. A mediana sobre os $278$ alertas é de **cinco segundos**, percentil noventa de
$16$, e é isso que a tese reporta.

⚠️ É o que mais incomoda dos dois. Não é um número velho: é o número do lado que nos convém,
ainda que sem intenção, num trabalho cuja tese central é que cada valor apresentado tem de
ser confrontável com o registo.

### A porta cobria menos do que parecia

O `check_artigo_numeros` só olhava para **decimais** — «os inteiros são anos, contagens e
coordenadas». A isenção é certa para anos e coordenadas e errada para contagens: uma
contagem é uma afirmação sobre o sistema implantado, tão verificável como uma PR-AUC.

Passa a cobrir inteiros a partir de mil (que a essa escala não são coordenadas nem corpos de
letra), com os anos de fora salvo quando trazem separador de milhares — ninguém escreve
`2{,}026`. E as **contagens exigem a dissertação como fonte**, não bastando um artefacto de
avaliação: um resultado decimal pode existir só num artefacto, porque o artigo pode reportar
uma medição que a tese comprime, mas se os dois documentos derem contagens diferentes o
leitor vê dois sistemas. Verificado com uma contagem plantada que a tese não tem.

⚠️ **E fica dito o que a porta continua a não apanhar:** nem a fusão de janelas de (1) nem o
«um segundo» de (2), que é uma palavra. A porta cobre agora uma classe a mais; a leitura
contra a tese continua a ser o que apanha as afirmações.

**Dois falsos positivos do próprio verificador, fechados antes de reportarem nada:** os
intervalos de página da bibliografia — que no artigo vive **dentro** do `main.tex`, por ser
LNCS, ao passo que a da tese está num `.bib` à parte — e o número de aluno no endereço de
correio. Mais uma cegueira real: **o separador de milhares em PT-PT é o espaço fino `\,` e
não o `{,}`**, que fica reservado à vírgula decimal, e o analisador só conhecia o segundo —
lia `38\,214` como dois números.

⚠️ **E usei `git checkout` sobre trabalho por commitar pela segunda vez no mesmo dia**, desta
vez no `paper/main.tex`. Recuperado da cópia `cp` que tinha feito antes de plantar o
controlo. A regra já estava escrita depois da primeira vez; o que faltou foi segui-la.

---

## Os materiais de estudo lidos contra a tese revista (2026-09-06)

Mesma leitura que se fez ao artigo, pela mesma razão: os slides, o guia e o quizz também são
anteriores à revisão de conteúdo. Três achados, e o primeiro é o mesmo defeito do artigo.

### A latência antiga, outra vez, e outra vez a nosso favor

O slide das limitações dizia «$\approx$2,5 h até detetar, 1 s até entregar». A dissertação
mede **353 minutos** entre a publicação e a deteção, e **5 segundos** entre a deteção e a
entrega. O `2,5 h` é a medição antiga do processo permanente e o `1 s` é a linha do
agendador, com $n=28$ — a mesma subpopulação que o artigo citava. Passam a ser os valores
publicados, e o contraste fica **mais** forte, não mais fraco.

### O segundo slide afirmava o que a tese se recusa a afirmar

O quadro «O que existe hoje» dava traço a toda a gente nas três perguntas, salvo o terminal
profissional. O Capítulo 2 nomeia **dois produtos que declaram responder à mesma pergunta** —
Robinhood Cortex e os momentos-chave do Google Finance — e trata-os com cuidado: a diferença
reivindicada não é de fluência mas de **verificabilidade**, e a tese diz em voz alta que os
produtos não foram testados. ⚠️ É o segundo slide do *deck*: um arguente que conheça o Cortex
via a apresentação a afirmar o que a dissertação declina afirmar, e a posição mais fraca era
a do slide. Nenhuma porta apanha isto — é uma afirmação, não um número.

### Duas convenções decimais no mesmo dia

Medido: a dissertação imprime **307 decimais com vírgula e zero com ponto**; os slides tinham
**48 com ponto contra 7 com vírgula** e o guia **13 contra 21**, internamente misturado.
Convertidos 53, 39 e 14. Ficam com ponto os excertos de **código real** do guia de
construção, porque o Python usa ponto e os excertos são cortados dos ficheiros por script.

⚠️ **E a primeira conversão mexeu em 195 sítios onde havia 48 a converter**: apanhou as
coordenadas TikZ, `(6.1,-\xn*0.92)` → `(6{,}1,...)`, o que parte a figura. Restaurado das
cópias e refeito com o ambiente de fora.

### E converter cegou a porta, que é pior do que o defeito

O `check_materiais` procura decimais com **ponto**, e o seu próprio comentário dizia «a tese
usa ponto, incluindo em modo matemático» — deixou de ser verdade na reescrita. No instante em
que os materiais foram convertidos, a porta passou a ver **1 decimal nos slides** em vez de
dezenas e a declarar «0 sem par na tese». **Não encontrar nada e aprovar tudo têm o mesmo
aspeto no ecrã**, e esta é justamente a porta que existe porque um documento de defesa já
mandou decorar um valor retirado.

Corrigida em quatro pontos, e cada um veio de um achado:

1. reconhece as **duas convenções** e compara por **valor**, não por cadeia;
2. passa de decimais de duas casas para **duas ou três** — a forma da esmagadora maioria dos
   valores deste trabalho. Via 23 números nos três materiais; vê 133;
3. aceita **`docs/evaluation/` como segunda fonte**, pelo mesmo critério da porta do artigo:
   os slides mostram o mínimo e o máximo da taxa de disparo e a tese só a amplitude que deles
   resulta;
4. no quizz compara apenas a **opção certa**. ⚠️ Um banco de escolha múltipla *tem* de conter
   números errados — são os distractores —, e exigir que todas as opções existam na tese é
   pedir um quizz que não pergunta nada.

E quatro valores ficam **isentos por lista, com a razão ao lado**: o par `0,667` contra
`0,455` e o seu intervalo `[0,391;\,0,862]`, que o guia cita para ensinar a **não** os dizer.
⚠️ É o inverso exato do defeito que a porta existe para apanhar: um valor retirado
apresentado como afirmação é o defeito; apresentado **com** a retratação é o antídoto.
Verificada nos dois sentidos com um valor fabricado.

---

## O pacote de defesa (2026-09-06)

Os onze documentos de `docs/defence/` são o que o autor **decora**, e estavam fora de
qualquer porta. O `check_materiais` cobria os slides, o guia, o quizz e o guião de gravação,
e não estes — apesar de ser exatamente aqui que esta classe de defeito já aconteceu: a
sessão 55 encontrou o guião de defesa a listar, na tabela dos números a saber, um par que
tinha sido **retirado**, e o simulacro a mandar decorá-lo.

**Os números estavam limpos** — 110 valores, todos com par na tese ou nos artefactos. O que
não estava foi uma afirmação, e é a terceira aparição da mesma.

### A latência antiga, em três documentos, e num deles com a conclusão invertida

O `gravar_demo.md` foi reescrito a 2026-08-07 **precisamente para o autor deixar de dizer uma
coisa falsa**, e avisa: «Se disseres a frase antiga, um arguente que abra o documento
apanha-te.» ⚠️ **O aviso passou a aplicar-se ao próprio documento.** Ensinava que, separando
as eras, a mediana «desce de ~196 min para ~143 min e fica lá». A dissertação mede hoje
**196 minutos no agendador e 402 no processo permanente**, e conclui o contrário: *o ciclo
mais curto não reduziu a latência observada.*

⚠️ **E havia uma segunda coisa a corrigir, mais subtil.** A tese não diz que o ciclo piorou:
diz que a comparação **não é interpretável como efeito do ciclo**, porque as configurações
não operaram em paralelo, entre elas mudaram as fontes e o período, e as amostras são de 28
contra 250. A resposta ensaiada não podia trocar uma afirmação causal por outra — tinha de
**retirar** a afirmação causal.

Mais o par de números do sistema, errado nos três ficheiros: **353 minutos** até detetar e
**5 segundos** até entregar. Somando o artigo e os slides, **uma só atualização de medição
deixou cinco documentos a dizer o valor antigo**, e em todos ele era o mais favorável.

### A porta passa a cobri-los

⚠️ **E um separador de milhares à portuguesa parece um decimal:** em prosa PT-PT escreve-se
`2.478` para dois mil quatrocentos e setenta e oito, e `0.542` para o decimal. A regra que os
separa sem ambiguidade neste corpus é que **um valor deste trabalho tem parte inteira zero** —
são precisões, PR-AUC e taxas —, e um separador de milhares nunca a tem. Mais as remissões de
secção, que não são números afirmados. Com isso, **zero ruído** sobre os onze documentos, e o
controlo dispara com um valor fabricado.

---

## A recolha para a avaliação de setembro (2026-09-06)

Verificada porque é a única coisa nesta lista que **não se recupera**: um dia em que o
mecanismo não esteja no ar é um dia de dados que não existe na defesa, e a sessão 63 já
encontrou exatamente esse modo de falha — o código existia só na árvore de trabalho, nunca
implantado.

**Está viva.** O registo tem notícias até 05/09 e cresceu de 39 595 para **41 747 linhas**;
os *snapshots* de classe A passaram de 977 para **1 272**. Os utilizáveis mantêm-se em 243
porque só houve **um dia de bolsa** desde que a recolha começou (04/09 foi sexta-feira).

### O relatório estava certo e lia-se ao contrário

Dizia: «com 9 dias de bolsa até 2026-09-17, a projeção é de 120 pares». Isso lê-se como *«a
17/09 tens 120 pares maturados»*. **Não tens.** O 17/09 é a última **data de notícia**
rotulável, não a data de correr a avaliação: o rótulo mede `(d, d+3]` dias de bolsa, e os
pares dos últimos três dias só maturam depois. O protocolo fixa o congelamento em ~22/09,
mas isso está noutro documento — e o que alguém lê no dia é o relatório gerado.

⚠️ **A consequência é exatamente o beco que este script existe para evitar.** O seu próprio
comentário diz que a recusa não pode ser um beco. Corrido a 17/09, encontraria cerca de 72 a
84 pares maturados, recusaria, e quem o lesse concluiria que a recolha falhou — quando ela só
não maturou ainda. **Uma recusa indistinguível de uma avaria é o defeito que o script foi
escrito para não ter.**

A aritmética fica como está, porque está certa. O que muda é o relatório dizer **quando** é
que esses pares existem, e quantos há hoje.

⚠️ **E a primeira versão da minha correção pôs o relatório a contradizer a sua própria
tabela:** escrevi «hoje há 12 pares maturados» três linhas abaixo de «pares maturados: 0».
O `por_dia` é construído sobre as linhas **utilizáveis**, antes de rotular — conta pares
**recolhidos**. São 12 recolhidos e 0 maturados, e é isso que passa a dizer.
