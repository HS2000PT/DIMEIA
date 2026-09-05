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
