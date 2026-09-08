# Proposta: a tese do lado do leitor

Pedido do autor: a tese é exaustiva de ler, perde-se nela, falta elemento visual a acompanhar o
raciocínio, e há a suspeita de que se relatam erros que se poderiam simplesmente corrigir. Mais
três perguntas diretas: aplicamos RAG? faria sentido? um *chatbot* daria bom trabalho futuro?

Este documento responde às seis perguntas com medições, e não com opinião. Onde a intuição do
autor se confirma, está confirmada com números; onde não se confirma, está dito, porque agir sobre
um diagnóstico errado gasta o pouco tempo que resta.

---

## 0. O diagnóstico, em duas linhas

**A intuição está certa, e é mais estreita do que parece.** O problema não é a escrita: é a
**densidade visual**, e está concentrada em **dois capítulos**. Nos outros quatro, a tese já tem a
cadência que o autor diz querer.

**E a maior melhoria disponível não é de leitura: é de reivindicação.** Existe uma camada
completa de geração ancorada — 1 443 linhas testadas, com verificação de ancoragem própria e
resultado de *red team* — a que a dissertação dedica **um parágrafo**. É, de longe, o maior
subaproveitamento do documento, e resolve ao mesmo tempo a pergunta do RAG e a do *chatbot*.

---

## 1. «É exaustiva de ler» — medido, e localizado

Contadas as palavras de prosa com os ambientes flutuantes substituídos por marcador **antes** de
contar, porque o corpo de uma figura TikZ tem centenas de palavras e contaria como texto:

| capítulo | palavras | visuais | **palavras por visual** | pior corrida sem visual |
|---|---:|---:|---:|---:|
| Cap. 1 · Introdução | 1 432 | 2 | 716 | 1,6 pp |
| **Cap. 2 · Estado da arte** | 5 519 | 5 | **1 104** | **3,7 pp** |
| Cap. 3 · Métodos | 4 418 | 10 | 442 | 3,1 pp |
| Cap. 4 · Implementação | 5 944 | 15 | **396** | 2,8 pp |
| Cap. 5 · Casos de estudo | 11 267 | 22 | 512 | 2,1 pp |
| **Cap. 6 · Conclusões** | 5 703 | 4 | **1 426** | **5,3 pp** |
| Apêndice A | 1 652 | 4 | 413 | 1,7 pp |
| **total** | **35 935** | **62** | **580** | |

**O Capítulo 6 tem três vezes e meia a densidade de texto por visual do Capítulo 4**, e é o
capítulo que o júri lê por último. O Capítulo 2 tem quase três vezes.

**A pior passagem do documento inteiro:** entre a Figura 6.1 (fólio 83) e a Tabela 6.1 (fólio 87)
correm **cinco páginas sem um único elemento visual** — e é exatamente aí que as três questões de
investigação são respondidas. É o sítio onde o autor diz perder-se, e é o sítio onde não devia.

### ⚠️ O que NÃO é o problema, e fica dito para não se gastar tempo lá

| medida | Cap. 1 | Cap. 2 | Cap. 3 | Cap. 4 | Cap. 5 | Cap. 6 |
|---|---:|---:|---:|---:|---:|---:|
| mediana de palavras por frase | 24 | 22 | 23 | 21 | 23 | 22 |
| percentil 90 | 41 | 37 | 38 | 40 | 40 | 40 |
| mediana de palavras por parágrafo | 67 | 72 | 70 | 66 | 80 | 87 |

**Isto é prosa académica saudável.** Vinte e duas palavras por frase é o alvo, não o problema. De
1 388 frases, **28 passam das 48 palavras** — dois por cento. Encurtar frases não resolveria nada
e destruiria a densidade que o documento ganhou a construir.

**Conclusão operacional: não mexer na escrita para «simplificar». Acrescentar visuais.**

---

## 2. As figuras que faltam, por ordem de retorno

Cada proposta abaixo é um objeto **novo**, que não duplica nenhum existente, e que torna explícito
um raciocínio que hoje o leitor tem de reconstruir de cabeça.

### F1 · A cadeia de evidência das três questões — Cap. 6, §6.2 🔴 maior retorno

**Onde:** logo a seguir à Figura 6.1, no fólio 83. Parte a corrida de cinco páginas ao meio.

**O quê:** três linhas, uma por questão, com cinco caixas cada:
`pergunta → o que se mediu → contra o quê → resultado → o que daqui NÃO decorre`.

**Porque funciona:** é o mapa de que o leitor precisa nesse ponto exato. A Figura 6.1 dá o
veredicto (SIM/SIM/NÃO); esta dá o **percurso** até ele. E a quinta coluna é a coluna que
distingue esta tese de um relatório — hoje está em prosa, dispersa por cinco páginas.

**Risco:** baixo. Nenhum número novo; tudo já está escrito no capítulo.

### F2 · O ciclo dos quatro processos do raciocínio baseado em casos — Cap. 2, §2.6 🔴

**Onde:** dentro da §2.6, que hoje é prosa pura.

**O quê:** o ciclo de Aamodt e Plaza — **recuperar → reutilizar → rever → reter** — com os dois
primeiros a cheio e os dois últimos a tracejado, e uma legenda a dizer que a interrupção é
consequência da restrição fundadora e não uma insuficiência.

**Porque funciona:** a tese faz aqui uma afirmação forte — *implementamos metade de um ciclo
estabelecido, de propósito* — e pede ao leitor que a segure só com palavras. Num diagrama
percebe-se num segundo. É também a figura que melhor explica a **recusa de prever** a quem não é
da área.

**Risco:** baixo. É literatura citada, não resultado.

### F3 · A janela do estudo de evento — Cap. 2 §2.5 ou Cap. 3 §3.5 🟠

**O quê:** uma linha temporal com o dia da notícia, o alinhamento de uma notícia de sábado ao
primeiro dia de negociação seguinte, e as três janelas de medição (+1, +3, +5), com a marca de
que a medição começa **no fecho** do dia da notícia e não na abertura.

**Porque funciona:** são três decisões de detalhe que condicionam todos os resultados da QI2 e da
QI3, e hoje vivem em três frases seguidas. É o género de coisa que um arguente pergunta e que uma
figura responde antes de a pergunta existir.

**Risco:** baixo. A Figura 3.2 já faz o equivalente para a janela do z-score; esta é a irmã que
falta.

### F4 · As três simples que ganharam e as três que não foram adotadas — Cap. 6, §6.1 🟠

**O quê:** duas colunas, três linhas cada, com a técnica, o valor e a razão da decisão.

**Porque funciona:** o §6.1 enuncia isto duas vezes em prosa e é a **segunda conclusão** do
trabalho. A Tabela 5.4 tem a informação, mas está no capítulo anterior e tem treze linhas. Uma
versão de seis linhas no sítio onde a conclusão é feita.

**Risco:** baixo, mas ⚠️ **é o mais próximo de duplicar** um objeto existente. Só vale a pena se
ficar visivelmente mais compacto do que a Tabela 5.4.

### F5 · O que o sistema entrega, lado a lado com o que uma aplicação gratuita entrega — Cap. 1 🟡

**O quê:** dois painéis a par, o mesmo acontecimento: à esquerda «−0,30%», à direita o alerta
completo com repartição, precedentes e ressalva.

**Porque funciona:** o Capítulo 1 argumenta a lacuna em palavras durante duas páginas. Esta figura
fá-lo em três segundos, e é a primeira coisa que o júri veria. **É a figura de abertura que a tese
não tem.**

**Risco:** médio. Exige uma captura nova ou uma composição; e há o risco de parecer promocional.
Mitiga-se usando um caso real já publicado no canal.

---

## 3. «Porque é que não corrigimos os erros?» — a resposta é por linha, não geral

A pergunta é legítima e a Tabela 6.1 já a antecipa: cada limitação traz **o que a encerra** e o
**custo**. Cinco estão marcadas `reduzido`. Vale a pena olhar para essas cinco uma a uma, porque
**duas são mesmo corrigíveis em vinte dias e três não são, e a razão não é a mesma.**

| # | Limitação | O que a encerra | Veredicto honesto |
|---|---|---|---|
| 8 | A repartição nem sempre está bem estimada | Exibir o ajuste junto de cada repartição | ✅ **Faz-se.** É produto, não ciência: mostrar o R² ao lado da repartição e uma nota abaixo de um limiar. Converte uma limitação declarada numa propriedade observável. Custa uma alteração na aplicação e uma captura nova. |
| 2 | A pontuação é quase constante dentro de cada empresa | Entradas que variem com a notícia | ⚠️ **Não.** Exige treinar de novo. Todos os valores da QI3 mudam, e propagam-se por seis capítulos, artigo, slides, guia e quizz. É a correção certa e o momento errado. |
| 3 | O rótulo pode favorecer a linha de base vencedora | Reconstruir o alvo com sensibilidades estimadas | ⚠️ **Não, e é a que mais dói.** Fecharia a maior ameaça à QI3. Mas são seis famílias re-treinadas e um resultado que pode inverter uma conclusão a vinte dias do congelamento. |
| 6 | A composição por empresa varia entre blocos | Uma divisão de composição constante | ⚠️ **Não.** Re-executa a avaliação inteira. |
| 9 | A deriva é medida e não corrigida | Re-treinar com o registo de produção | ⚠️ **Não**, e a tese já diz porquê: alteraria os valores reportados e exigiria tempo de observação próprio. |

**A resposta curta a dar ao júri**, se perguntarem: *três das cinco exigem re-treinar, e re-treinar
a esta distância trocaria um resultado verificado por um resultado por verificar. A quarta é de
produto e foi feita. A quinta está declarada com a arquitetura que a resolveria já desenhada.*

⚠️ **E há uma correção de enquadramento que não custa nada e vale muito.** Hoje a Tabela 6.1 diz
`custo: reduzido` em cinco linhas, e um leitor atento pergunta exatamente o que o autor perguntou.
A coluna devia distinguir **«reduzido em esforço»** de **«reduzido em risco»** — porque o que
trava três destas cinco não é o trabalho, é a propagação. Uma palavra por linha.

---

## 4. RAG: sim, aplicamos metade — e a outra metade está construída e escondida

### O que a tese diz hoje

A §2.4.1 descreve a arquitetura de geração aumentada por recuperação e explica que o sistema
executa a primeira metade e **se detém antes da segunda**, com a razão certa: a recuperação
devolve objetos verificáveis; a geração converte-os numa afirmação em prosa cuja fidelidade é ela
própria uma propriedade por avaliar.

Depois, no fólio 49, um parágrafo de onze linhas diz que a camada gerada **existe, foi avaliada, e
não é exposta**.

### O que existe mesmo no repositório

| ficheiro | linhas | o que faz |
|---|---:|---|
| `intelligence/context.py` | 325 | monta o **pacote de evidência**: cada facto com identificador citável e origem declarada (`measured` / `computed` / `model`). Nenhum facto é `generated`. |
| `intelligence/guard.py` | 455 | a **verificação de ancoragem**: cada número de uma frase tem de pertencer ao facto que essa frase cita |
| `intelligence/report.py` | 280 | relatório de situação, com **rejeição por secção** e recuo para o chão determinístico |
| `intelligence/analyst.py` | 327 | **o analista conversacional**: pergunta → plano → evidência → resposta ancorada, com um encaminhador determinístico que funciona **sem chaves de API** |
| | **1 443** | |

Medido: **23 de 23 tentativas de contornar a verificação recusadas, 8 de 8 textos fiéis aceites,
0 violações entregues.**

### Isto muda as duas respostas que o autor pediu

**«Aplicamos RAG?»** — Aplicamos a metade de recuperação em produção, e temos a arquitetura
completa construída e avaliada. **A tese pode dizer isto muito melhor do que diz.**

**«Um chatbot como trabalho futuro?»** — ⚠️ **Não. Seria subestimar o trabalho.** O `analyst.py`
**é** esse chatbot, e com uma propriedade que um chatbot colado ao lado não tem: cada frase da
resposta traz os identificadores dos factos que a sustentam, e o leitor abre-os. Anunciá-lo como
futuro seria a repetição exata do defeito que a sessão 65 encontrou no Apêndice B, onde a linha
de Linguagem Natural dizia que o sistema «recusa produzir texto» e **subestimava a dissertação**.

### A proposta: §4.8 nova, «A camada de inteligência», com uma figura 🔴 maior retorno do documento

**O quê:** promover o parágrafo do fólio 49 a secção própria, com:
- o **contrato**: o pacote de evidência, e a regra de que a linguagem nunca produz factos;
- os **dois níveis de garantia** em tabela — vocabulário fechado no alerta empurrado, enumeração
  do proibido no texto puxado — e porque é que o segundo é mais fraco;
- a **figura da travessia**: `pergunta → plano → evidência → resposta → âncora aberta`;
- os **números do red team** que já existem;
- e a razão declarada de **não estar exposta**, que já está escrita e é boa.

**Porque é a maior melhoria disponível:** num mestrado de Engenharia de IA, esta é a componente
que um júri procura primeiro. Hoje está a valer onze linhas. E responde antecipadamente à pergunta
mais provável de todas — *onde está a IA neste trabalho?*

**Risco:** baixo em conteúdo — nada de novo se afirma, tudo já foi medido. Médio em espaço: são
duas a três páginas e uma figura.

⚠️ **E há uma decisão do autor embutida aqui**, que não é minha: expor ou não a camada. A tese
está coerente hoje porque não a expõe e explica porquê. **Recomendo manter fechada e descrevê-la
melhor** — expô-la a vinte dias obrigaria a avaliar em produção o que hoje só está avaliado em
banco de ensaio.

---

## 5. Outras metodologias: a recomendação é não acrescentar nenhuma

Percorrida a área, a tese já cobre: deteção de anomalias estatística e aprendida, três gerações de
representação de texto, estudo de evento, encolhimento de beta, aprendizagem supervisionada,
calibração a posteriori, predição conformal (considerada e **rejeitada com razão escrita**), deriva
de conceito, geração aumentada por recuperação e geração ancorada.

**Acrescentar uma técnica nova a vinte dias produziria uma secção sem avaliação, que é exatamente
o que esta tese recusa fazer.** O que falta não é método: é **reivindicar o que já existe**.

O que **sim** vale a pena, e custa apenas prosa, é afiar três linhas de trabalho futuro que hoje
estão implícitas ou ausentes, cada uma ancorada em peças que já temos:

1. **Reordenação por *cross-encoder***. A §2.4 já explica a diferença entre bi- e cross-encoder e
   porque é que o segundo não é praticável sobre dezenas de milhares de casos. O passo natural é
   recuperar com o bi-encoder e **reordenar os vinte primeiros** com um cross-encoder. Fica dito
   que a base de avaliação já existe e o que faltaria medir.
2. **Aprendizagem de ordenação sob orçamento**. O problema real do produto não é classificar, é
   escolher cinco por dia. Isso é *learning to rank* com restrição, e a tese mede-o hoje com uma
   métrica de classificação. Nomear a família certa é honesto e mostra domínio.
3. **Índice aproximado de vizinhos.** Já mencionado na §2.4 como caminho de crescimento. Basta
   ligá-lo explicitamente ao número de casos que a base tem hoje.

---

## 6. «Estar mais perto do leitor» — quatro dispositivos, nenhum deles cosmético

O autor pediu prosa mais próxima, genuína e fluida. A medição diz que a prosa **já é** boa. O que
falta são **pontos de apoio**, e há quatro que este documento não usa:

**6.1 · Uma frase de orientação no início de cada capítulo, a dizer o que o leitor vai levar dali.**
Os capítulos abrem a dizer o que fazem («Este capítulo apresenta…»). Não dizem o que o leitor
**ganha**. Uma frase por capítulo, seis ao todo.

**6.2 · O caso real como fio condutor — ⚠️ MEDIDO, E NÃO É VIÁVEL NA FORMA FORTE.** A ideia era
escolher uma empresa e segui-la do princípio ao fim, dando ao leitor uma personagem. Contadas as
ocorrências de cada *ticker* por capítulo, **nenhum aparece em mais de três dos seis**:

| empresa | capítulos onde aparece |
|---|---|
| **AMD** | 3, 4, 5 |
| TSLA · AMZN · NFLX · META · NVDA · AAPL | 4 e 5 apenas |

Nenhuma empresa tem valores nas duas pontas do documento, e forçá-la exigiria medições novas —
ou seja, exatamente a classe de trabalho que a secção 7 recomenda não fazer. **A versão forte
está fora.**

**A versão fraca está dentro e vale quase o mesmo:** a **AMD** já atravessa os Capítulos 3, 4 e 5,
que são o núcleo técnico. Basta **nomeá-la como fio** — uma frase no fim do §1.5 a dizer que o
mesmo caso é seguido pelas três técnicas, e uma remissão explícita em cada um dos três sítios onde
ela reaparece. Custa três frases e nenhuma medição.

**6.3 · Repetir o número-chave ao lado da figura que o sustenta.** O leitor que vira a página perde
o valor. Custa nada e é o que torna uma figura autónoma.

**6.4 · Uma página de «como ler esta tese», antes do Capítulo 1.** Um mapa: os quatro percursos
possíveis (quem quer o resultado, quem quer o método, quem quer o sistema, quem quer verificar), e
onde cada um deve entrar e sair. As dissertações longas que se leem bem quase todas têm isto.

---

## 7. Ordem proposta, por retorno sobre risco

| # | O quê | Retorno | Risco | Esforço |
|---|---|---|---|---|
| 1 | **§4.8 · a camada de inteligência**, com figura da travessia | 🔴 muito alto | baixo | 2–3 pp |
| 2 | **F1 · cadeia de evidência das três QI** (Cap. 6) | 🔴 alto | baixo | 1 figura |
| 3 | **F2 · ciclo dos quatro processos** (Cap. 2) | 🔴 alto | baixo | 1 figura |
| 4 | **§6.5 · três linhas de trabalho futuro afiadas** | 🟠 alto | nenhum | prosa |
| 5 | **Tabela 6.1 · separar esforço de risco** na coluna de custo | 🟠 médio | nenhum | 5 palavras |
| 6 | **F3 · janela do estudo de evento** | 🟠 médio | baixo | 1 figura |
| 7 | **6.4 · página «como ler esta tese»** | 🟠 médio | baixo | 1 página |
| 8 | **6.1 · frase de orientação por capítulo** | 🟡 médio | nenhum | 6 frases |
| 9 | **Item 8 · exibir o ajuste na aplicação** + captura nova | 🟡 médio | **médio** | software |
| 10 | **F4 · as três e três** (Cap. 6) | 🟡 baixo | baixo | 1 figura |
| 11 | **F5 · figura de abertura** (Cap. 1) | 🟡 alto | **médio** | composição |
| 12 | **6.2 · a AMD nomeada como fio dos Cap. 3–5** | 🟡 médio | baixo | 3 frases |

⚠️ **O item 12 mudou de forma depois de medido.** A versão que eu ia propor — um caso a atravessar
os seis capítulos — **não é viável**: nenhuma empresa aparece em mais de três. Fica a versão
fraca, que é barata e honesta.

**Os itens 1 a 8 não tocam num único número** e podem correr todos sem risco de resultado. São o
grosso do ganho.

**Os itens 9 a 12 mexem em produto, em composição ou na estrutura narrativa.** Valem a pena, e
merecem decisão explícita antes de começar.

⚠️ **O que continuo a não recomendar, mesmo com «custe o que custar»:** re-treinar o modelo, refazer
o rótulo, ou re-executar a avaliação. Não é falta de tempo, é a natureza do que se troca — um
resultado verificado por um resultado por verificar, a vinte dias, com propagação por seis
capítulos e cinco materiais. Se houver tempo depois de 27/09 e antes da defesa em outubro, o
item 3 da Tabela 6.1 (reconstruir o rótulo com sensibilidades estimadas) é o que mais acrescentaria
— e pode ser dito na defesa como acréscimo oral sobre um resultado fechado.
