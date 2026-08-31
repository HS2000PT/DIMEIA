# Auditoria crítica de `tese/main.pdf` — diagnóstico pré-defesa

Documento auditado: `main.pdf`, 135 páginas, compilado em 2026-08-30 11:43.
Auditoria feita sobre o texto integral do PDF, com verificação aritmética independente
de todas as contas reproduzíveis a partir do documento, e verificação cruzada contra os
`.tex` de origem onde houve suspeita de contradição.
**Não foi lido o código nem os ficheiros de resultados.** Tudo o que exige esse acesso
está marcado `[VERIFICAR NO CÓDIGO]`.

---

## 0. Veredicto em três frases

A tese é sólida, está bem escrita e — coisa rara — está montada para poder dizer que não.
O risco principal na defesa **não é o resultado negativo da QI3**: é a QI1, cuja evidência
principal é uma métrica que um detetor trivial também satisfaz, e é o facto de todo o
Capítulo 5 assentar num único bloco de teste que já foi olhado dezenas de vezes.
Há ainda duas contradições numéricas concretas e uma afirmação do Resumo mais forte do
que a do Capítulo 5.

---

## 1. A tese em linguagem simples

**Problema.** Quando uma ação se mexe, as aplicações gratuitas mostram a percentagem e
mais nada. O investidor particular fica com três perguntas por responder: isto é invulgar?
foi a empresa ou o mercado? já aconteceu antes e o que se seguiu? Os terminais profissionais
respondem, a milhares de euros por ano.

**O que foi construído.** O InvestiGator: um sistema que corre continuamente sobre doze
empresas, só com fontes gratuitas, e que envia alertas ao Telegram com a evidência ao lado.
Dois gatilhos: movimento invulgar de preço, ou notícia relevante. Quatro técnicas:

1. **z-score deslizante** sobre 20 dias, com o dia julgado excluído da própria norma → "é invulgar?"
2. **Decomposição** do retorno em mercado + setor (ortogonalizado) + empresa, com beta
   encolhido pela precisão da estimativa (Vasicek) → "foi a empresa ou o mercado?"
3. **Recuperação semântica** (Sentence-BERT MiniLM, 384 dim, cosseno) sobre uma base de
   38 214 casos com impacto a 1/3/5 dias já medido → "já aconteceu antes?"
4. **Triagem supervisionada** (regressão logística de 9 entradas, calibrada por Platt),
   treinada sobre um conjunto próprio de 79 753 exemplos → "merece interromper alguém?"

**Contribuição real.** Não é um algoritmo. É (a) a integração destas quatro peças sob a
restrição de custo zero com a evidência entregue ao utilizador, e (b) — e isto é o que dá
valor científico — **uma avaliação montada para falhar, que falhou, e que foi reportada**.
A tese retira quatro afirmações suas com base nas suas próprias medições (Tabela A.3).

**Resultados.**
- QI1 (deteção): **sim**. Amplitude de taxa de disparo 0.015 contra 0.344 do limiar fixo;
  ganha ao Isolation Forest e ao LOF (F1 0.530 vs 0.269 / 0.280).
- QI2 (precedentes): **sim**, mas estreitado. Sob a restrição causal, precisão@5 = 0.513,
  chão 0.259, margem +0.254. Dentro de cada setor supera o chão nos cinco.
- QI3 (triagem): **não**. Nenhum modelo com texto bate a volatilidade sozinha
  (0.496 vs 0.542). Sobrevive a três testes de robustez. O texto acrescenta +0.012 por
  cima de uma tabela de consulta por empresa (IC [+0.004, +0.020]), abaixo do critério
  prático de 0.02 e sem ganho na precisão@5.
- Descoberta de produção: o modelo implantado **é, aritmeticamente, uma tabela de consulta
  por empresa** — a única entrada que distingue dois títulos da mesma empresa é o
  comprimento do título.

**O que se recusa fazer.** Prever preços. Única exceção declarada: probabilidade de
movimento invulgar *em qualquer direção*.

**Aritmética verificada.** Refiz, a partir do documento: z-score da Tesla (7.625 ✓),
conversão log↔simples (+19.82% → +21.92% ✓; +6.2944% → +6.50% ✓), soma das três parcelas
da AMD (✓ exata), calibração de Platt (3.700×0.507 − 2.313 = −0.437; σ(−0.437) = 0.392 ✓),
Brier do "alertar sempre" (1 − 0.378 = 0.622 ✓), F1 do z-score (0.516 ✓) e do limiar fixo
(0.217 ✓), soma dos blocos do split (28 574 + 17 710 + 32 649 + 820 = 79 753 ✓), soma da
Tabela 4.4 (5060 ✓), funil 944→42 (1 em 22.5 ✓), Tabela 4.2 (970 distintas = +124.5% ✓).
**Nenhum erro aritmético encontrado.** Isto é um ponto forte e deve ser dito na defesa.

---

## 2. As 10 maiores fragilidades, por risco na defesa

### F1 — CRÍTICO — A evidência principal da QI1 é satisfeita por um detetor trivial
**Onde:** §5.2.7 (Tabela 5.1, primeira linha), §5.3.1–5.3.2, §6.2.

**Problema.** O argumento "principal" da QI1 é a *amplitude da taxa de disparo* entre
empresas, escolhido precisamente por não depender de rótulos. Mas essa métrica mede
**consistência, não qualidade de deteção**. Um detetor que assinale 2% dos dias *ao acaso*
em cada empresa obtém amplitude ≈ 0, ou seja, bate o z-score na métrica que a tese elege
como decisiva. A métrica não tem chão declarado (a Tabela 5.1 diz "zero seria o ideal",
o que é exatamente o problema: o ideal é atingível por um método sem informação nenhuma).

**Porque importa.** A QI1 é uma das duas respostas afirmativas. Se o júri desmontar a
métrica principal, resta o F1 = 0.516 contra um rótulo que a própria tese admite ser
circular (percentil 99 dos retornos da própria empresa, ou seja, já normalizado pela
volatilidade — §5.3.1, §5.7).

**Impacto.** Alto: transforma "sim, e com margem grande" em "sim, sob um rótulo circular".

**Correção (30 min, texto apenas).** Acrescentar uma linha à Tabela 5.2 e um parágrafo:
uma linha de base *aleatória calibrada para a mesma taxa média de disparo*. Ela terá
amplitude ≈ 0 e F1 ≈ ao acaso. Isso **fortalece** o argumento em vez de o enfraquecer,
porque mostra que as duas métricas têm de ser lidas em conjunto: consistência **e** F1.
Escrever explicitamente: *"nenhuma das duas métricas basta sozinha; a amplitude exclui o
limiar fixo, o F1 exclui o disparo aleatório, e só o z-score passa nas duas."*
Se não houver tempo de correr nada, esse parágrafo pode ser escrito por argumento — a
amplitude do detetor aleatório é ≈0 por construção e não precisa de ser medida.

---

### F2 — CRÍTICO — Um único bloco de teste, olhado dezenas de vezes
**Onde:** §5.6.3 (a tese declara-o), §5.6.10 (declara-o outra vez), §5.7, §5.8.

**Problema.** Todo o Capítulo 5 quantitativo — as seis famílias, as nove definições de
rótulo, sete ablações, a soma do texto por cima da tabela de consulta, a comparação ponta
a ponta — corre sobre **o mesmo bloco de teste de 221 dias**. A reamostragem por grupos
mede ruído *dentro* desse bloco e não diz nada sobre estabilidade entre períodos. E há
evidência direta de que a variância entre períodos é grande: PSI de 0.281 na volatilidade
e prevalência a passar de 47.0% (validação) para 37.8% (teste).

**Porque importa.** O efeito de +0.012 com IC [+0.004, +0.020] é, na melhor das hipóteses,
frágil: é o resultado de uma comparação entre muitas feitas no mesmo conjunto. A tese
declara-o, o que a protege parcialmente — mas o júri vai perguntar porque é que declarar
chega.

**Correção (texto, 20 min).** Reforçar em §5.6.10 e no Capítulo 6 que **o +0.012 não é uma
descoberta, é um limite superior de um efeito que uma origem rolante poderia não confirmar.**
Preferir a formulação: *"não conseguimos rejeitar que o texto acrescenta algo; o efeito, se
existe, é menor do que o critério prático."* Não vale a pena tentar correr origem rolante
em 3 dias.

---

### F3 — CRÍTICO — `ret_event` não está disponível no referencial em que o modelo é usado
**Onde:** Tabela 3.1, §3.3.2, §5.6.1, §5.6.7 (segunda causa possível).

**Problema.** Uma das nove entradas é o retorno fecho-a-fecho do dia da notícia. No
protocolo offline é o dia completo; em produção a notícia é pontuada em média 158 minutos
depois da publicação, com o dia ainda aberto. **Todas as métricas do Capítulo 5 para os
modelos com contexto são portanto medidas com uma entrada que o sistema implantado nunca
tem.** A tese declara isto em três sítios, mas em nenhum deles diz o que muda no número.

**Porque importa.** É a definição-livro de *lookahead* parcial. O teste anti-lookahead do
Excerto 3.2 protege contra informação de d+1 em diante, e **não** contra esta fronteira
intradiária — a tese diz isso explicitamente, o que é honesto, mas deixa em aberto quanto
vale.

**Impacto.** Não inverte a QI3 (a linha de base "só volatilidade" não usa `ret_event`, e
mesmo assim ganha; se algo, o *leak* favorece os modelos que perderam). **Este é o
argumento de defesa e deve estar escrito.**

**Correção (texto, 15 min).** Uma frase em §5.6.1: *"a assimetria de referencial favorece
os modelos com contexto, que são os que perdem; corrigi-la só poderia tornar o resultado
negativo mais forte, nunca mais fraco."* Isto neutraliza a pergunta.
`[VERIFICAR NO CÓDIGO]` se `ret_event` entra também na linha de base "só volatilidade" —
se entrar, o argumento acima cai e a fragilidade sobe para bloqueante.

---

### F4 — IMPORTANTE — O Resumo afirma mais do que o Capítulo 5 sustenta (QI2)
**Onde:** Resumo/Abstract (p. vii/ix) contra §5.5.2 e §6.2.

**Problema.** O Resumo diz: *"A recuperação semântica supera as linhas de base lexical e
triviais."* O Capítulo 5 **retirou** essa afirmação: a alternativa trivial "devolver sempre
notícias do setor maior" obtém 0.467, contra 0.514 do método (margem +0.047), e a linha
lexical (0.346) fica **abaixo** desse chão trivial. A Tabela A.3 regista a afirmação como
"Estreitada". O Resumo não foi atualizado.

**Porque importa.** É uma inconsistência Resumo↔Capítulo que a Tabela A.3 do próprio
documento denuncia. Um júri que leia o apêndice antes do resumo apanha-a de imediato, e é
o tipo de achado que contamina a leitura do resto.

**Correção (10 min, prioridade máxima pelo rácio custo/benefício).** Substituir por:
> "A recuperação semântica supera a taxa-base em cada um dos cinco setores, e mantém a
> margem quando restringida a olhar apenas para o passado."

Fazer o mesmo no Abstract.

---

### F5 — IMPORTANTE — Contradição: 13 ou 14 empresas no treino?
**Onde:** Tabela 3.2 ("79 753 exemplos, **14 empresas**"), §5.6.5 ("o treino cobre
**catorze**"), Tabela 5.8 / Tabela 5.11 / §5.6.9 / §6.6 ("**treze** constantes, uma por
cada empresa que aparece no treino").

**Problema.** Verificado no `.tex`: `cap5/capitulo5.tex:888`, `:906`, `:927`, `:1463` e
`cap6/capitulo6.tex:468,486`. Se o treino cobre catorze empresas, a tabela de consulta por
empresa deve ter catorze constantes, não treze. Uma das duas está errada, ou falta uma
frase a explicar porque é que uma das catorze foi excluída (p.ex. contagem insuficiente).

**Impacto.** Pequeno em substância, **grande em credibilidade**: é a linha que sustenta o
resultado mais espetacular da tese ("uma tabela de treze constantes bate o modelo").

**Correção.** `[VERIFICAR NO CÓDIGO]` o número de chaves da tabela de consulta. Depois
uniformizar e, se forem mesmo 13 contra 14, acrescentar meia frase a dizer porquê.

---

### F6 — IMPORTANTE — O universo de empresas muda cinco vezes ao longo do documento
**Onde:** 12 (produção, §6.1), 13 (constantes, §5.8), 14 (treino, Tabela 3.2), 15 (deteção,
Tabela 3.2 e §5.3.1), 17 (mapa de setores, §3.5.3 e §5.4).

**Problema.** Cada número está justificado no sítio onde aparece, mas nunca em conjunto.
O leitor que salte entre capítulos não consegue saber se está a ver a mesma população.

**Correção (45 min, alto retorno).** Uma tabela nova de cinco linhas no Capítulo 3
(a seguir à Tabela 3.2): *conjunto | quantas empresas | para que serve | porque é diferente
das outras*. Além de fechar a lacuna, dá um slide pronto para a defesa.

---

### F7 — IMPORTANTE — O rótulo usa β = 1, e a incoerência não tem análise de sensibilidade
**Onde:** §3.7.2 (declarada), §5.6 (todas as famílias avaliadas contra o mesmo rótulo).

**Problema.** O rótulo subtrai o movimento do mercado supondo β = 1, exatamente a suposição
que §3.5 recusa uma página antes, mostrando um β bruto estimado de 4.43. A tese declara a
incoerência e diz que a comparação é internamente consistente — o que é verdade — mas
reconhece que não correu a análise de sensibilidade.

**Porque importa.** O erro introduzido por β = 1 está correlacionado com a empresa e com a
volatilidade, que é **precisamente** a variável da linha de base vencedora. Não é
implausível que parte da vitória da volatilidade seja um artefacto do rótulo.

**Impacto.** Este é o ataque mais forte que existe contra a QI3, e é o que eu faria no lugar
do júri.

**Correção realista em 3 dias:** não recorrer nada. Preparar a **resposta oral** (ver §5,
pergunta Q7) e acrescentar duas linhas em §5.6.12 a nomear este mecanismo explicitamente
como a hipótese alternativa que não foi excluída. Assumir é mais forte do que ser apanhado.

---

### F8 — IMPORTANTE — A sobreposição entre as três fontes de notícias é implausível
**Onde:** Tabela 4.2 e §4.3.1.

**Problema.** 432 + 141 + 429 = 1002 títulos relevantes; 970 distintos; 401 + 119 + 418 =
938 exclusivos. Isto implica que só **32 títulos (3%)** aparecem em mais do que uma fonte,
sobre as mesmas 12 empresas e os mesmos 3 dias. Três agregadores de notícias financeiras
sobre a Apple e a Nvidia não têm 97% de conteúdo disjunto.

**Diagnóstico provável:** a deduplicação é feita por **igualdade exata de string** do título.
Fontes diferentes reescrevem títulos, logo quase nada casa, e a coluna "exclusivas" — que é
a coluna que justifica a decisão de somar três fontes — está inflacionada.

**Impacto.** Não afeta nenhuma questão de investigação. Afeta a justificação de uma decisão
de arquitetura, e é uma pergunta fácil de fazer e desconfortável de responder.

**Correção (10 min, texto).** `[VERIFICAR NO CÓDIGO]` a regra de deduplicação. Se for
igualdade exata, acrescentar uma frase à legenda da Tabela 4.2: *"a deduplicação é por
título exato, pelo que a coluna de exclusivas é um limite superior: reescritas do mesmo
acontecimento contam como títulos distintos."* Nota: o sistema **tem** a técnica para fazer
isto por significado — é o item 5 do trabalho futuro. Ligar as duas coisas é uma boa
resposta oral.

---

### F9 — MENOR/IMPORTANTE — "53 minutos" é uma comparação não controlada de n=28 vs n=73
**Onde:** Tabela 4.7 e §4.8.

**Problema.** As duas eras diferem no agendador, mas também no número de fontes, na lista de
empresas vigiadas e no período de calendário. As medianas não têm intervalo. E o próprio
texto mostra que o ganho é quase todo irrelevante, porque 158 dos ~196 minutos estão na
descoberta.

**Correção (5 min).** Trocar "o ciclo comprou 53 minutos" por "as duas eras diferem em 53
minutos de mediana, sem controlo de outras alterações no mesmo período; o que a decomposição
mostra com segurança é que quase todo o tempo está na descoberta e não na entrega."
Esta reformulação é mais fraca na aparência e mais forte na defesa.

---

### F10 — MENOR — O produto mostra uma probabilidade que se sabe enviesada em ~5 pp
**Onde:** §3.7.5, §4.7, Figura 4.3 ("57%").

**Problema.** A calibração é ajustada num bloco com 47.0% de positivos e aplicada a um
mundo com 37.8%. A tese mede o enviesamento (média prevista 0.428 contra 0.378 observado)
e mantém o número no alerta.

**Correção.** Não mexer no sistema a três dias da defesa. Preparar a resposta: *"a ordenação
é o que o produto usa e é preservada por ser monótona; o valor absoluto está declarado como
otimista em cerca de cinco pontos, e recalibrar exigia a distribuição de produção, que é
trabalho declarado."* Se sobrar tempo no Dia 2, acrescentar essa ressalva **no texto do
próprio alerta**, o que é uma linha de código e fecha a pergunta por inteiro.

---

### Menções honrosas (não entram no top 10, mas anote-as)

- **Tabelas 5.6 e 5.9 dão números diferentes para linhas com o mesmo nome**
  ("Contexto + texto": 0.496 vs 0.533; "Só texto": 0.439 vs 0.457). A causa está no texto
  (representação reduzida a 32 dimensões na segunda), mas **não está na legenda da
  Tabela 5.9**. Um júri que compare as duas tabelas vê uma contradição. *Correção: uma
  frase na legenda. 5 minutos, retorno alto.*
- **Amplitude 0.015 (Tabela 5.2) vs 0.017 (Tabela 5.3)** sem nota. Mesma solução que acima —
  a Tabela 5.3 corre na região comum aos três detetores, e isso está dito para o F1 mas não
  para a amplitude.
- **"Fadiga de alertas" não tem citação nenhuma** (§3.7.1, §3.9.3, §4.6). É um conceito
  estabelecido (literatura de alarmes clínicos) e sustenta uma decisão de desenho inteira
  — o orçamento de cinco. `[REFERÊNCIA A VERIFICAR]`: procurar uma revisão sobre *alarm
  fatigue* ou *notification fatigue*. **É a única lacuna de referência que considero séria
  numa bibliografia que, no resto, é boa e está bem usada.**
- **A caixa destacada de §5.6.7 diz 84%**, e o número honesto (por título distinto, janela
  maior) é **48%**. A correção está no parágrafo seguinte. Numa leitura em diagonal — que é
  o que um júri faz — fica o 84%. *Trocar o número dentro da caixa e deixar o 84% no corpo.*
- **A prevalência da validação (47.0%) é maior do que a do treino (38.5%) e a do teste
  (37.8%)** num split cronológico. Não é um erro, mas é estranho e não está explicado.
  `[VERIFICAR NO CÓDIGO]`.
- **Contribuição 2** ("método reprodutível para ligar notícias a impacto de mercado")
  está mais forte do que a medição: a concordância de direção é 0.708 contra um chão de
  0.688. O método liga notícias a *desfechos observados*, não a *impacto atribuível*.
  Sugiro trocar "ligar notícias a impacto de mercado" por "medir, sem informação do futuro,
  o que se seguiu a notícias semanticamente próximas".

---

## 3. As 10 melhorias de maior retorno, realistas em 3 dias

Ordenadas por (impacto na defesa) ÷ (tempo).

| # | O quê | Onde | Tempo | Porquê |
|---|---|---|---|---|
| 1 | Corrigir a frase da QI2 no Resumo e no Abstract | p. vii, ix | 10 min | Fecha a única inconsistência Resumo↔Capítulo (F4) |
| 2 | Resolver 13 vs 14 empresas | Tab. 3.2 / 5.8 / 5.11 | 20 min | Contradição numérica direta (F5) |
| 3 | Nota na legenda da Tabela 5.9 a explicar porque difere da 5.6 | §5.6.10 | 5 min | Evita uma contradição aparente entre duas tabelas |
| 4 | Trocar 84% por 48% dentro da caixa destacada | §5.6.7 | 5 min | O número honesto passa a ser o que se lê |
| 5 | Parágrafo sobre o chão da amplitude de disparo | §5.3.2 | 30 min | Fecha o buraco crítico da QI1 (F1) |
| 6 | Frase a dizer que a assimetria do `ret_event` favorece os modelos que perderam | §5.6.1 | 15 min | Neutraliza a pergunta mais técnica (F3) |
| 7 | Tabela nova: os cinco conjuntos de empresas | Cap. 3 | 45 min | Fecha F6 e dá um slide |
| 8 | Legenda da Tabela 4.2: deduplicação por título exato | §4.3.1 | 10 min | Fecha F8 |
| 9 | Reformular o "comprou 53 minutos" | §4.8 | 5 min | Fecha F9 |
| 10 | Citação para fadiga de alertas | §3.7.1 | 30 min | Única lacuna séria de referência |

Total: **menos de 3 horas de trabalho de texto**, e fecha oito das dez fragilidades.
Nada nesta lista exige correr uma experiência.

---

## 4. Figuras — plano visual

A tese **já é muito visual** (25 figuras, 21 tabelas, e as figuras explicam mecanismo em
vez de decorar). Não recomendo acrescentar quase nada. Três excepções.

### P0 — Figura "os cinco conjuntos de empresas"
- **Local:** Capítulo 3, a seguir à Tabela 3.2.
- **Objetivo:** que o leitor perceba de uma vez que 12/13/14/15/17 não são erros.
- **Conteúdo:** cinco barras horizontais aninhadas ou um diagrama de conjuntos:
  17 (mapa de setores) ⊃ 15 (deteção) ⊃ 14 (treino) ⊃ 13 (constantes) e, ao lado e
  parcialmente disjunto, 12 (produção) — com as duas empresas de produção fora do treino
  marcadas, porque isso é um resultado da §5.6.5.
- **Layout:** barras à esquerda, uma coluna de texto à direita com "serve para".
- **Legenda:** "Os cinco conjuntos de empresas usados. A lista de produção não é um
  subconjunto do treino: duas das doze nunca apareceram em nenhum exemplo de treino."
- **Substitui:** nada; acrescenta ~15 linhas de dispersão que hoje estão espalhadas.
- **Defesa:** slide de resposta pronta à pergunta "afinal quantas empresas?"

### P0 — Figura "o que cada métrica da QI1 exclui"
- **Local:** §5.3.2, ao lado da Tabela 5.2.
- **Objetivo:** mostrar que só o z-score passa nas **duas** métricas.
- **Conteúdo:** um plano 2D. Eixo x = amplitude de disparo (menor melhor), eixo y = F1
  (maior melhor). Quatro pontos: limiar fixo (amplitude alta, F1 baixo), disparo aleatório
  calibrado (amplitude ≈0, F1 ≈ acaso), Isolation Forest / LOF, z-score (canto bom).
  Duas linhas tracejadas a marcar as regiões excluídas por cada métrica.
- **Legenda:** "Nenhuma das duas medidas basta sozinha: a amplitude exclui o limiar fixo,
  o F1 exclui o disparo aleatório, e apenas a regra deslizante passa nas duas."
- **Substitui:** dois parágrafos de justificação metodológica em §5.3.1.
- **Defesa:** é a figura que responde à pergunta mais perigosa da tese. Vale por si.

### P1 — Figura "onde o modelo foi avaliado e onde foi usado"
- **Local:** §5.6.5, a acompanhar a explicação "o modelo está a mais".
- **Objetivo:** tornar visível a lição mais transferível do trabalho.
- **Conteúdo:** duas distribuições sobrepostas. À esquerda: o funil de treino (todas as
  notícias do corpus) com o modelo a avaliar sobre tudo. À direita: o funil de produção,
  com relevância e frescura a cortar antes, e o modelo a receber só a cauda. Uma seta a
  ligar "avaliado aqui" a "usado aqui".
- **Legenda:** "Um modelo avaliado isolado e implantado atrás de filtros nunca foi avaliado
  na distribuição que vai ver."
- **Defesa:** é a frase que fecha a apresentação. Convém ter desenho.

### O que **não** acrescentar
Nada no Capítulo 2 (já tem 3 figuras e 5 tabelas para 13 páginas — é suficiente),
nada no Capítulo 6 (as três figuras existentes já ligam limitações a trabalho futuro),
e nenhuma figura decorativa. A tese não sofre de falta de visual.

### O que cortar / mover
| Secção | Recomendação |
|---|---|
| §5.2 inteira (as métricas explicadas) | **MANTER.** É invulgar e é boa: torna o capítulo auditável por um leitor não especialista. Não ceder se alguém sugerir cortar. |
| §4.3, Tabela 4.1 (dependências) | **SIMPLIFICAR**: manter, mas mover a coluna "porquê esta e não a outra" para as três linhas onde houve medição, e resumir as restantes. Ocupa duas páginas. |
| §4.8.2 (memória dos 38 mil vetores) | **MANTER.** É engenharia real e mede-se. Um júri gosta disto. |
| §3.9 (desafios sociais) | **MANTER**, mas é o candidato natural se for preciso ganhar páginas. |
| Apêndice A.3 (matriz de evidência) | **MANTER e destacar no Capítulo 6.** É a melhor página do documento e está escondida. Uma frase em §6.3 a apontar para ela. |

---

## 5. As 15 perguntas mais perigosas do júri

Legenda: 🔴 fragilidade real · 🟡 preparar · 🟢 seguro

**Q1 🔴 — "A vossa métrica principal da QI1 é a amplitude da taxa de disparo. Um detetor que
dispare 2% dos dias ao acaso em cada empresa tem amplitude zero. Então é melhor que o vosso?"**
*Porque é perigosa:* é a métrica que a tese elege como decisiva, e um método sem informação
nenhuma atinge o seu ótimo. *Correção na tese:* melhoria #5.
*Resposta oral:* "Tem amplitude melhor e F1 ao nível do acaso. É por isso que a secção usa
duas medidas: a amplitude exclui o limiar fixo, que mede a volatilidade em vez da raridade,
e o F1 exclui o disparo aleatório. Nenhuma basta sozinha, e só a regra deslizante passa nas
duas. Se me perguntar qual é o argumento mais fraco da tese, é este, e é por isso que a
resposta à QI1 vale sob um rótulo que é ele próprio relativo à volatilidade."

**Q2 🔴 — "O rótulo da triagem subtrai o mercado com beta igual a um, o que a secção 3.5
recusa. Como é que sabe que a vitória da volatilidade não é um artefacto do rótulo?"**
*Porque é perigosa:* é o ataque mais forte que existe à QI3 e não há análise de
sensibilidade. *Resposta oral:* "Não sei, e está declarado na secção 3.7.2. O que posso
afirmar é mais estreito: sob esta definição de alvo, e ela é a mesma para as seis famílias,
a ordenação é internamente consistente. O erro que o beta unitário introduz está
correlacionado com a empresa e com a volatilidade, portanto pode favorecer a linha de base
vencedora. Reconstruir o alvo com betas encolhidos é a experiência que falta, e é meia
página de código sobre um pipeline que já existe. Não a corri, e por isso a conclusão está
escrita como condicionada ao rótulo efetivamente usado."
**Não improvise aqui. Decore o mecanismo e assuma.**

**Q3 🔴 — "Todas as comparações do Capítulo 5 correm no mesmo bloco de teste. Quantas vezes
olhou para ele antes de encontrar o +0.012?"**
*Resposta oral:* "Muitas, e é por isso que esse efeito está escrito com três ressalvas e
declarado abaixo do critério prático que fixei antes de medir. As duas defesas que usei —
não afinar a configuração e escrever o critério antes — reduzem o risco sem o eliminarem.
A resposta certa era uma origem rolante com três ou quatro cortes; não a corri, e a
secção 5.6.3 diz isso. O veredicto da QI3 não depende desse número: depende do 0.496 contra
0.542, que sobrevive a nove definições de rótulo."

**Q4 🔴 — "O `ret_event` é o retorno completo do dia. Em produção o dia ainda não fechou.
Todos os vossos números offline são inválidos?"**
*Resposta oral:* "São válidos para a pergunta offline e não demonstram paridade com
produção — está na Tabela 3.1 e na secção 5.6.7. E a direção do problema é favorável à
conclusão: quem beneficia dessa entrada são os modelos de contexto, que são os que perdem
para uma linha de base que não a usa. Corrigir a assimetria só poderia tornar o resultado
negativo mais forte."
*[Antes da defesa: `[VERIFICAR NO CÓDIGO]` que a linha de base "só volatilidade" não usa
`ret_event`. Se usar, esta resposta não serve.]*

**Q5 🔴 — "Diz que uma tabela de treze constantes bate o modelo, mas a tabela 3.2 diz que o
treino tem catorze empresas. Qual é?"**
*Correção na tese antes da defesa (melhoria #2).* Se não der tempo: "Catorze empresas
aparecem no treino; a tabela de consulta tem treze entradas porque [razão]. Vou confirmar."
**É a pergunta mais fácil de evitar e a mais barata de corrigir. Corrija-a.**

**Q6 🔴 — "O Resumo diz que a recuperação supera a linha de base lexical. A secção 5.5 diz
que a lexical fica abaixo do melhor chão trivial. Qual das duas frases é a tese?"**
*Correção: melhoria #1.* Se for apanhado: "A do Capítulo 5. O Resumo ficou por atualizar
depois de eu estreitar a afirmação, e a Tabela A.3 regista essa afirmação como estreitada."

**Q7 🟡 — "O que é que o vosso sistema faz que o Robinhood Cortex ou os momentos-chave do
Google Finance não façam?"**
*Resposta:* "Provavelmente menos, em fluência e em cobertura. A diferença não é essa: um
resumo gerado é uma afirmação, e o que aqui se entrega é uma afirmação com os casos anexados
— datas, semelhanças e o que o preço fez a seguir a cada um. Não testei esses produtos, e
por isso só afirmo o que as páginas dos fornecedores declaram."

**Q8 🟡 — "Se a recuperação capta tema e não direção, e a concordância é 0.708 contra um
chão de 0.688, para que serve mostrar precedentes?"**
*Resposta:* "Não serve para prever, e é exatamente por isso que os casos são mostrados um a
um, com datas e desfechos, e nunca resumidos a uma média. O que eles dão é uma distribuição
de desfechos observados em situações do mesmo tema, que é contexto verificável. Se
resumisse à média estaria a produzir a previsão que o trabalho recusa. Que isso torne a
confiança do utilizador *apropriada* é uma hipótese por verificar, e é a primeira linha de
trabalho futuro."

**Q9 🟡 — "Porque é que uma das quatro técnicas não tem pergunta de investigação?"**
*Resposta:* "Porque não existe resposta certa contra a qual a comparar. A parcela verdadeira
de mercado num movimento não é observável: só existe relativamente a um modelo. Dados os
betas, a repartição é uma identidade contabilística. Inventar aí uma métrica de exatidão
produziria um número sem referente. O que é falsificável nela mede-se e está medido: se
discrimina entre empresas, e o R² do modelo efetivamente usado — mediana 0.460, negativo
numa das dezassete."

**Q10 🟡 — "As três parcelas somam sempre ao movimento. Isso não valida a decomposição?"**
*Resposta:* "Não valida nada. Soma por construção, porque a parcela da empresa é definida
como o resto — uma repartição inteiramente sem sentido somaria igualmente bem. É uma
verificação de implementação. Está dito na secção 5.4."
🟢 na substância; 🟡 só porque tem de sair fluida.

**Q11 🟡 — "A empresa que está a explicar faz parte do índice contra o qual a regride."**
*Resposta:* "Faz, e está declarado na secção 3.5. O enviesamento tem direção conhecida:
empurra a parcela específica para baixo, e é maior nas maiores empresas, que são
precisamente as de que o sistema mais fala. Corrigi-lo exigia índices construídos sem a
ação, que nenhuma fonte gratuita publica."

**Q12 🟡 — "Escolheu quinze empresas grandes em 2026 e avaliou até 2018. Isso é
survivorship bias."**
*Resposta:* "É, e está escrito na secção 5.3.5. O que se mede é o comportamento do método
em empresas que duraram, e não na população de que foram tiradas. Nenhuma saiu de bolsa nem
foi absorvida. Para a QI1 isso importa menos do que pareceria, porque o argumento principal
é de consistência entre empresas e não de acerto absoluto, mas continua a ser uma limitação
de âmbito e não a resolvo."

**Q13 🟡 — "O sistema mostra 57% e a tese diz que essa probabilidade é cinco pontos
otimista. Porque é que continua a mostrar?"**
*Resposta:* "Porque a ordenação, que é o que o produto usa para escolher, é preservada por a
sigmoide ser monótona, e corrigir o valor absoluto exigia recalibrar sobre a distribuição de
produção, que é trabalho declarado. Concordo que o mínimo era o alerta dizer isso, e é uma
linha de texto." *(Se fizer a alteração no Dia 2, mude para o pretérito.)*

**Q14 🟡 — "Onde está a engenharia de inteligência artificial? Treinou uma regressão
logística com nove entradas que perdeu a uma linha de base."**
*Resposta:* "Está na secção 4.9, e a resposta é que não está no modelo. Está no que foi
preciso construir para que esse número, e a conclusão negativa que ele sustenta, sejam de
confiança: o conjunto de dados rotulado a partir de duas fontes desalinhadas, a separação
temporal imposta por um teste que altera o futuro e exige que as entradas não mudem e o
rótulo mude, a calibração com o enviesamento declarado, a garantia de que o modelo
implantado é o modelo avaliado — que custou exportar o codificador em vez de o trocar — e o
ciclo que voltou a avaliar o sistema depois de implantado. Foi esse ciclo que produziu o
resultado mais útil da tese, que é o modelo não servir para o que eu lhe estava a pedir.
Sem ele, esta dissertação afirmaria uma falsidade com números verdadeiros."
**Esta é a pergunta mais provável de todas. Decore-a.**

**Q15 🟢 — "Qual foi o erro que mais lhe custou?"**
*Resposta:* "Escolhi para o produto um modelo por uma métrica que fazia a pergunta errada.
A PR-AUC pergunta 'ordena bem o conjunto todo?' e o produto precisava de 'distingue duas
notícias da mesma empresa?'. A variante que implantei tinha uma única entrada capaz de
distinguir dois títulos — o comprimento — e por isso a pontuação era quase constante dentro
de cada empresa, por aritmética e não por acidente do treino. Em quase metade das decisões
o resultado estava determinado antes de a notícia ser lida. O modelo deixou de decidir e
passou a ordenar, que é o uso para o qual tem informação."

---

## 6. Afirmações, números e fórmulas que exigem verificação adicional

| # | O quê | Onde | O que verificar | Como |
|---|---|---|---|---|
| 1 | 13 vs 14 empresas | Tab. 3.2 / 5.8 / 5.11 | número de chaves da tabela de consulta e de tickers distintos no bloco de treino | `[VERIFICAR NO CÓDIGO]` — contagem direta |
| 2 | `ret_event` na linha de base "só volatilidade" | §5.6.1–5.6.2 | se a baseline vencedora usa ou não a entrada com fronteira intradiária | `[VERIFICAR NO CÓDIGO]` — **prioritário**, muda a resposta a Q4 |
| 3 | Deduplicação de notícias | Tab. 4.2 | igualdade exata de título vs normalização | `[VERIFICAR NO CÓDIGO]` |
| 4 | Prevalência 47.0% na validação vs 38.5% treino / 37.8% teste | §3.7.5, §5.6.6 | se é real ou artefacto do corte | `[VERIFICAR NO CÓDIGO]` |
| 5 | Tab. 5.6 vs Tab. 5.9 | §5.6.2 vs §5.6.10 | confirmar que a diferença 0.496→0.533 é só a redução a 32 dimensões e não outra corrida | `[VERIFICAR NO CÓDIGO]` — ficheiros de resultados |
| 6 | Amplitude 0.015 vs 0.017 | Tab. 5.2 vs 5.3 | confirmar que é a região comum de pontuação | ficheiro de resultados |
| 7 | Fórmula 3.1 | p. 25 | **verificar visualmente no PDF** que a fração renderiza (a camada de texto sai truncada: `z_t = r_t`) | abrir o PDF |
| 8 | Tabela 3.4 | p. 31 | idem: as linhas de β_m, β_s e R² saem desalinhadas na extração; confirmar que R²=0.6577 está na linha certa | abrir o PDF |
| 9 | Referência de fadiga de alertas | §3.7.1 | não existe | `[REFERÊNCIA A VERIFICAR]` — procurar revisão de *alarm fatigue* |
| 10 | "World Monitor 2026" | §2.1, Tab. 5.10 | é uma aplicação web citada como origem de uma ideia técnica; verificar que o texto deixa claro que é atribuição de ideia e não fonte científica | leitura |
| 11 | Nomes do júri | folha de rosto | continuam como `[Nome do Presidente, Categoria, Escola]` | **preencher antes de entregar** |
| 12 | Licença do código | §3.9.3, A.4 | fica declarada como decisão em aberto; confirmar que é aceitável entregar assim | orientador |

**Nenhum destes pontos me leva a duvidar de um resultado central.** O documento é
internamente muito mais consistente do que a média, e a matriz de evidência do Apêndice A.3
é a prova disso.

---

## 7. Plano para 3 dias

### DIA 1 — científico e crítico (~4 h)
1. `[VERIFICAR NO CÓDIGO]` os pontos 1, 2 e 3 da tabela acima (45 min). O ponto 2 é o único
   que pode mudar uma resposta oral.
2. Melhorias #1 e #2 (Resumo/Abstract; 13 vs 14). 30 min.
3. Melhoria #5: o parágrafo do chão da amplitude na §5.3.2. 45 min. **É o que fecha a
   fragilidade crítica.**
4. Melhoria #6: a frase sobre a direção do enviesamento do `ret_event`. 15 min.
5. Duas linhas em §5.6.12 a nomear o β=1 como hipótese alternativa não excluída. 20 min.
6. Reforçar em §5.6.10 que o +0.012 é frágil por ser um efeito entre muitos no mesmo bloco.
   20 min.
7. Recompilar e confirmar que nada partiu. 20 min.

### DIA 2 — clareza, figuras e produto (~5 h)
1. Melhorias #3, #4, #8, #9, #10 (legendas, caixa dos 48%, deduplicação, latência, citação).
   1 h 30.
2. Figura P0 "os cinco conjuntos de empresas" + tabela nova no Capítulo 3. 1 h 30.
3. Figura P0 "o que cada métrica da QI1 exclui". 1 h. *(Se o tempo apertar, corte esta e
   deixe o parágrafo do Dia 1 — o argumento sobrevive sem desenho.)*
4. Opcional, 20 min de código: acrescentar ao alerta a ressalva de que a probabilidade é
   ~5 pp otimista. Fecha a Q13 por inteiro.
5. Preencher os nomes do júri na folha de rosto. Recompilar. Ler o PDF de fio a pavio uma
   vez, só a olhar para figuras e legendas.

### DIA 3 — defesa (dia inteiro, sem tocar no documento)
1. **Manhã.** Escrever as respostas a Q1, Q2, Q3, Q4 e Q14 **por extenso**, e depois
   reduzi-las a três frases cada. São as cinco que decidem a defesa. Q14 é a mais provável;
   Q2 é a mais difícil.
2. **Meio-dia.** O mapa de domínio (abaixo). Verificar que consegue explicar cada item da
   coluna "TENHO DE SABER" começando por *"A ideia é muito simples:"*.
3. **Tarde.** Duas passagens completas da apresentação em voz alta, com relógio. A segunda
   com alguém a interromper.
4. **Fim do dia.** Parar. Não abrir o LaTeX.

**Regra para os três dias:** não corra nenhuma experiência nova. Nada nesta lista precisa
de uma. Uma medição nova a 48 h da defesa cria uma inconsistência que já não há tempo de
propagar por seis capítulos.

---

## 8. Mapa de domínio — o que tem mesmo de saber

### TENHO DE SABER (explicar sem consultar, começando por "a ideia é muito simples")
- **z-score deslizante e porque é que a janela exclui o próprio dia.** Ideia simples:
  comparo o dia de hoje com os vinte anteriores da mesma ação e conto a distância em
  desvios-padrão. Se o dia entrasse na sua própria norma, puxava-a e parecia menos invulgar.
- **Porque é que um limiar fixo é uma má ideia.** Mede a volatilidade da empresa, não a
  raridade do dia. É a mesma forma de erro que voltou a aparecer no limiar sobre a
  pontuação do modelo — saber ligar as duas vale muito.
- **A decomposição, e porque é que a soma fechar não prova nada.** A parcela da empresa é
  definida como o resto.
- **Encolhimento de Vasicek:** peso = σ²_ref / (σ²_ref + SE²(β̂)). Ideia simples: uma
  estimativa limpa fica quase intacta, uma estimativa ruidosa é puxada para a referência.
  Saber porque é que um peso fixo (Blume) é pior: encolhe com a mesma força uma boa e uma má.
- **Cosseno e porque é ângulo e não distância.** E o atalho: os vetores vêm com norma 1,
  logo o cosseno é só a soma dos produtos.
- **A cadeia PR-AUC → chão = prevalência.** E o Brier do "alertar sempre" = 1 − prevalência.
  Saber refazer as duas contas de cabeça: 0.378 e 0.622.
- **Porque é que o modelo implantado é uma tabela de consulta.** Sete entradas de nível de
  empresa, uma de nível de dia, uma de nível de notícia — e essa é o comprimento do título,
  que sozinho dá PR-AUC igual ao chão.
- **A lição: um modelo avaliado isolado e implantado atrás de filtros nunca foi avaliado na
  distribuição que vai ver.**

### DEVO SABER (podem perguntar, prepare mas não decore)
- Calibração de Platt: dois parâmetros, ajustada na validação, e porque é que o b negativo
  vem em parte da reponderação de classes no treino.
- Embargo de 5 dias e porquê 5 (o rótulo olha 3 dias para a frente).
- Porque é que o bloco de teste tem mais exemplos do que o de treino (densidade de notícias
  cresce; 2018 vale 5.1% das linhas e 2023 vale 43.8%).
- Porque é que o FinBERT perdeu (é um codificador afinado para sentimento, não para colocar
  frases num espaço de distâncias; o Sentence-BERT acrescenta esse objetivo de treino).
- PSI e as bandas 0.10 / 0.25.
- Porque é que a predição conformal foi considerada e não adotada (cobertura marginal;
  exige permutabilidade, que é a hipótese que o split cronológico recusa).
- As duas escolhas que a medição não favorece: janela de 20 dias (60 dá F1 0.678) e desvio
  de pesos iguais (EWMA dá 0.664). Saber dizer que são **escolhas e não resultados**.

### POSSO CONSULTAR (não decore)
- Valores exatos das tabelas 4.1, 4.5, A.1, A.2.
- As nove combinações de limiar × horizonte.
- Os números do funil de um dia concreto.
- Versões de bibliotecas, dimensões de ficheiros, custos de memória.

---

## 9. Onde a tese está acima da média, e deve dizê-lo

Não é elogio: é material de defesa que está subaproveitado.

1. **A matriz de evidência (Apêndice A.3) com quatro afirmações retiradas.** Quase nenhuma
   dissertação tem isto. Está escondida no apêndice — aponte para ela no Capítulo 6 e leve-a
   como slide.
2. **O aviso da Tabela 5.7** ("o chão de 0.163 ordenava alfabeticamente") é o melhor
   parágrafo da tese. Mostra uma avaliação a apanhar-se a si própria.
3. **A dupla avaliação** — histórico retido e depois as próprias decisões em produção
   maturadas contra o mercado — é o que separa isto de um projeto.
4. **A aritmética está toda certa.** Verifiquei tudo o que era verificável a partir do PDF.
   É raro e vale a pena saber, porque dá confiança para responder com números de cabeça.
5. **A declaração de uso de IA** é exemplar em precisão e em tom.

---

*Auditoria produzida sem acesso ao código, aos dados ou aos ficheiros de resultados.
Tudo o que dependia deles está marcado `[VERIFICAR NO CÓDIGO]`.*
