# Simulacro de defesa — tese curta (PT)

> Escrito a 2026-08-23. **É este o simulacro a usar.** O `simulacro_defesa.md` foi escrito para a
> tese longa em inglês e usa a numeração RQ1–RQ4; este usa **QI1, QI2, QI3**, que é o que está no
> documento que vais entregar. Se te perguntarem pela "terceira pergunta de investigação", ela é a
> **triagem**, não as explicações.
>
> Todos os números aqui foram conferidos contra `tese/` a 2026-08-23. Se algum não bater com o PDF,
> **o PDF ganha**.

---

## Como usar isto

Lê uma pergunta, responde **em voz alta** antes de veres a resposta. O que te vai falhar no dia não
é o conhecimento, é a ordem das frases. Cada pergunta tem três partes:

- **O que estão mesmo a testar** — quase nunca é o que a pergunta diz.
- **A resposta** — a estrutura, não o guião para decorar.
- **⚠️ A armadilha** — a frase que soa bem e te afunda.

---

## Q1. A abertura: "onde está a contribuição?"

> *"Diga-me o que construiu e qual é a contribuição. Um detetor de anomalias, um modelo de
> embeddings pré-treinado e uma regressão logística é, à primeira vista, trabalho de integração."*

**O que estão mesmo a testar:** se sabes distinguir o que construíste do que descobriste. Um
candidato fraco lista componentes; um candidato forte nomeia um resultado.

**A resposta.** Três movimentos, por esta ordem:

1. **O problema, numa frase.** Um investidor particular vê o preço mexer e não sabe porquê. As
   ferramentas gratuitas dizem-lhe *quanto*, e nenhuma lhe diz *porquê* de forma que ele possa
   conferir.
2. **A restrição que define tudo o resto.** O sistema **nunca prevê**. Tudo o que ele escreve é
   sobre o que já aconteceu, e é isso que torna cada afirmação verificável no momento em que é
   lida. Não é modéstia: é a decisão de desenho de que decorre a explicabilidade.
3. **A contribuição, que é o método e não o código.** Cada componente foi comparado com a
   alternativa mais simples que responde à mesma pergunta, e **em três casos a simples ganhou** e
   ficou. O trabalho é uma avaliação honesta de onde a aprendizagem automática ajuda e onde não
   ajuda, feita num sistema real, em produção, com o resultado negativo publicado com o mesmo
   destaque dos positivos.

Se quiseres uma frase única: *"a contribuição não é ter juntado as peças, é ter medido quais delas
não eram precisas — e ter deixado isso escrito."*

**⚠️ A armadilha:** listar as quatro técnicas. Se a tua resposta for um inventário, confirmaste-lhes
a hipótese de que é integração. As técnicas entram na pergunta seguinte, não nesta.

---

## Q2. A mais perigosa: "o seu modelo perdeu"

> *"A QI3 pergunta se um modelo treinado prioriza melhor do que a volatilidade. Nenhum modelo com
> texto bateu essa linha de base. Isto não é um fracasso?"*

**O que estão mesmo a testar:** se sabes defender um resultado negativo sem o disfarçar. Esta é a
pergunta que separa uma tese honesta de uma tese defensiva.

**A resposta.**

- **Confirma primeiro, sem rodeios.** `0.496` contra `0.542` de PR-AUC. O texto não bateu a
  volatilidade.
- **Diz que o critério foi escrito antes.** A hipótese e a métrica estavam fixadas antes de correr
  a experiência. Reportá-la ao contrário do esperado era a única opção compatível com o resto.
- **Mostra que o resultado é robusto e não descuido.** Sobreviveu a um re-teste em condições
  favoráveis ao texto, a uma reamostragem por grupos, e a **nove definições diferentes do rótulo**.
  Não é um resultado que se desfaça se alguém mexer numa escolha.
- **E aqui vem a parte que ganha a pergunta: o "não" tem uma localização.** Feita a pergunta certa,
  que não é *qual é melhor* mas *o texto acrescenta ao que já se sabe*, a resposta é **sim**:
  `+0.012` de PR-AUC por cima da tabela de consulta por empresa, com intervalo `[+0.004, +0.020]`
  que exclui zero. É detetável neste protocolo, pequeno e abaixo do critério prático de `0.02`.
  Três medições impedem que reabra o veredicto: a
  diferença para a volatilidade continua a conter zero, a precisão dentro do orçamento não muda uma
  casa decimal, e a capacidade de separar dois dias da mesma empresa continua ao nível do acaso.

**A frase de fecho:** *"a informação que o texto traz distingue empresas e períodos, e o produto
precisava que distinguisse notícias. É essa a diferença entre um resultado negativo e um resultado
negativo compreendido."*

**⚠️ A armadilha:** dizer "mas o modelo é útil na precisão dentro do orçamento". É verdade e é
perigoso, porque a pergunta seguinte é a Q3 e tu acabaste de lhes dar a deixa.

---

## Q3. O seguimento: "o seu modelo é uma tabela de consulta"

> *"A sua própria ablação mostra que uma tabela com um número fixo por empresa iguala o modelo
> treinado, e na métrica mais próxima do produto **bate-o**. Não implantou um modelo cego ao
> conteúdo das notícias que estava a triar?"*

**O que estão mesmo a testar:** se descobriste isto sozinho ou se eles te apanharam.

**A resposta.** Descobriste-o tu, está na tese, e é das melhores coisas que lá estão.

- **Os números, ditos por ti antes de eles os lerem.** Tabela de consulta `0.534` contra `0.538` do
  modelo em PR-AUC; na precisão dentro do orçamento, `0.662` contra `0.632`, ou seja **fica à
  frente**. Sem nada de nível de empresa, o modelo cai para `0.378`, que é exatamente a prevalência,
  isto é, o chão. Só o comprimento do título dá o mesmo chão.
- **Porque é que isso acontece, e não é acidente.** É **aritmética**: das nove entradas do modelo
  implantado, uma só distingue dois títulos da mesma empresa no mesmo dia. Em produção, **48%** dos
  títulos distintos estavam determinados pela empresa antes de a notícia ser lida.
- **A lição de método, que é o que interessa.** A PR-AUC corre sobre o conjunto todo, onde a
  variação entre empresas domina. A métrica estava certa; a pergunta que ela faz não era a pergunta
  de que o produto precisava.
- **E o que se fez em consequência.** O modelo **deixou de ser porta e passou a ser critério de
  ordenação**, que é o uso que a medição sustenta, com o controlo de volume a passar para um
  orçamento diário. A justificação que resta para manter as nove entradas não é exatidão, é que é a
  única variante cujas contribuições o alerta consegue **mostrar** — e o preço disso, `0.005` de
  PR-AUC, está na tabela.

**⚠️ A armadilha:** defender a decisão original. Ela estava errada e a tese di-lo. O que se defende
é o processo que a apanhou: instrumentar o ciclo de vida depois de implantar, que é precisamente o
que a maior parte dos trabalhos não faz.

---

## Q4. QI2: "a sua margem é de 0.047, não de 0.274"

> *"Diz que a recuperação semântica obtém 0.514 contra 0.240 do acaso. Mas metade do seu corpus é
> tecnologia. Devolver sempre tecnologia, sem modelo nenhum e sem olhar para a pergunta, vale
> 0.467. A sua margem real é 0.047."*

**O que estão mesmo a testar:** se compreendes os teus próprios chãos de comparação. Se esta
pergunta te apanhar de surpresa, perdeste-a.

**A resposta.** Toma-lhes a pergunta da boca: **isso está na tese e fui eu que o medi.**

- Confirma: o chão que estava na tabela era o mais generoso dos disponíveis, a margem cai de
  `+0.274` para `+0.047`, e a linha lexical de `0.346` fica **abaixo** do chão.
- **Mas o que engana é o agregado, não o método.** A estratégia trivial obtém `1.000` em tecnologia
  e **`0.000`** em todos os outros quatro setores. Devolveria semicondutores a quem perguntasse por
  uma petrolífera: como produto não serve para nada.
- **Dentro de cada setor**, onde ela não se pode agarrar a nada, o método obtém `0.712` na
  tecnologia (chão `0.429`), `0.448` na energia e `0.419` na saúde (chãos de `0.072` e `0.071`).
  Onde o corpus é fino, ganha **seis vezes o chão**.
- **A afirmação que faço é a mais estreita:** a recuperação supera a taxa-base **nos cinco
  setores**, e o número agregado não é a forma certa de o dizer, porque subestima o método e
  sobrestima a alternativa pela mesma razão.

**Se apertarem com a direção:** a semelhança capta o **tema**, não a **direção**. Concordância de
direção `0.708` contra um chão de acaso de `0.688`. É por isso que o produto apresenta os
precedentes como observações passadas e nunca como indicação do que vem a seguir.

**⚠️ A armadilha:** dizer **"2,1 vezes o acaso"**. Esse número está retirado. Se o disseres, dás-lhes
a refutação já feita.

---

## Q5. "Nunca testou com uma pessoa"

> *"A tese é sobre explicações para investidores particulares e não foi testada com um único
> utilizador. Como sustenta a alegação de utilidade?"*

**O que estão mesmo a testar:** se admites o buraco sem te desfazeres, e se ele é falta de tempo ou
falta de pensamento.

**A resposta.**

- **Não sustento, e a tese não a faz.** O terceiro objetivo está declarado como **cumprido por
  metade**. A fidelidade está garantida por construção, porque o texto é montado a partir dos
  objetos calculados e não pode divergir deles. A **utilidade** não foi medida e não se afirma nada
  sobre ela.
- **Onde não há evidência, não há afirmação.** A Matriz de Evidência do apêndice tem uma linha
  marcada "não afirmado" precisamente para isto.
- **E o estudo não é uma ideia solta: está desenhado, congelado, e descrito na Secção A.5.** Duas
  condições sobre seis alertas reais, contrabalanço cruzado em dois fatores, e duas salvaguardas
  contra mim próprio — o limiar de oito participantes está fixado no código **antes de existirem
  dados**, e o procedimento de análise, corrido sobre a folha vazia, responde que está vazia em vez
  de produzir um resultado.
- **A pergunta que ele responderia**, e que é a mais interessante: a garantia de que cada frase se
  abre no facto que a sustenta está verificada por máquina e **nunca por uma pessoa**. Se ninguém
  conseguir fazer essa travessia, a contribuição é verdadeira e inútil.

**✅ E aqui podes invocar o enquadramento, porque ele está no documento.** A **§3.1** declara que
este trabalho pertence à investigação por desenho, citando \[Hevner 2004\] e \[Peffers 2007\], e
diz que a avaliação de um artefacto tem de ser rigorosa e é atividade central do processo. Podes
dizer: *"o meu enquadramento é o da investigação por desenho, e ele exige avaliação rigorosa do
artefacto; cumpri-a na parte técnica e declaro por medir a parte de utilidade."* Não uses isto para
sugerir que a avaliação humana é opcional — o próprio enquadramento pede demonstração de utilidade,
e é por isso que o objetivo está dito como cumprido **por metade**.

---

## Q6. "O seu rótulo de relevância é a fingir"

> *"'Mesmo setor' é um substituto muito fraco para 'relevante'. Duas notícias de tecnologia podem
> não ter nada a ver uma com a outra."*

**A resposta.** Concorda com a premissa e mostra o que fizeste para a tornar exigente.

- É um substituto automático e imperfeito, e está dito como tal.
- Torno-o **mais difícil**, não mais fácil: a própria empresa está **excluída** dos vizinhos, logo
  não posso ganhar a acertar em mim mesmo; e o resultado é reportado com os chãos ao lado.
- A alternativa honesta seria anotação humana, e é a mesma coisa que falta ao estudo de utilidade:
  cerca de duzentos itens anotados desbloqueariam os dois ao mesmo tempo. Está no trabalho futuro.

**⚠️ A armadilha:** defender que o proxy é bom. Não é. É o melhor que se consegue **sem rótulos
humanos**, que é uma afirmação diferente e verdadeira.

---

## Q7. "Como garante que não usa o futuro?"

> *"Todo este trabalho depende de não haver fuga de informação do futuro. Como o garante?"*

**O que estão mesmo a testar:** se a garantia é uma intenção ou um mecanismo.

**A resposta.** Quatro camadas, e a última é a que interessa.

1. **No detetor:** a janela do *z*-score termina no dia **anterior**. O dia que está a ser julgado
   nunca entra na sua própria norma.
2. **Na base de casos:** o impacto de uma notícia é medido a partir do primeiro dia de negociação
   **igual ou posterior** à data dela, e só é escrito quando a janela fecha, oito dias depois.
3. **Na divisão dos dados:** o corte é cronológico, `70/15/15` **em dias de negociação**, com um
   **embargo de cinco dias** entre blocos, porque o rótulo olha três dias para a frente e sem
   embargo o fim do treino tocaria no princípio do teste. Custou `820` linhas, `1.03%`.
4. **E a garantia a sério:** existe um **teste que muta o futuro** e exige que as entradas fiquem
   iguais e o rótulo mude. Se alguém introduzir uma fuga, esse teste parte. Uma garantia que não
   falha quando é violada não é uma garantia.

**Se apertarem com a divisão por dias:** o bloco de teste tem **mais** exemplos do que o de treino,
`32 649` contra `28 574`, e isso está explicado na tese: o corte é por dias (`1050` contra `221`) e
a densidade de notícias cresce muito ao longo do período. Cortar por número de exemplos partiria
dias ao meio e deixaria entrar no treino notícias do mesmo dia que está a ser testado.

---

## Q8. "Porque não prevê o preço?"

> *"Um sistema que previsse o preço não seria muito mais útil? E a QI3 treina um modelo: isso não é
> prever?"*

**A resposta.**

- **A recusa é de desenho e não de capacidade.** Uma previsão não se pode conferir no momento em
  que é lida; uma afirmação sobre o passado pode. É isso que torna todo o resto verificável.
- **O modelo da QI3 não prevê direção.** O rótulo é em **valor absoluto**: aprende sobre
  *materialidade*, não sobre subir ou descer. A fronteira está no rótulo, não numa promessa.
- **A única probabilidade que o sistema mostra** é a de o mercado reagir de forma invulgar, em
  qualquer direção, e vai declarada como tal no fim do alerta.

**⚠️ A armadilha:** dizer que prever seria impossível. Não é o teu argumento, e obriga-te a
defender uma afirmação sobre eficiência de mercados que a tese não faz.

---

## Q9. "Chama a isto alertas, com 353 minutos de atraso?"

> *"A latência mediana entre a publicação e a captação é de quase três horas. O mercado já reagiu."*

**A resposta.**

- **Confirma e decompõe**, porque a decomposição é a defesa: `158` minutos da publicação até o
  sistema ver a notícia, e **um segundo** dali até à entrega. O atraso está **todo na descoberta**,
  e não na engenharia do sistema.
- **A causa é a fonte gratuita**, e há uma razão que só se vê a medir: a manchete mais recente do
  feed não é a mais recente **relevante**.
- **Comprar um serviço em tempo real resolveria e violaria a restrição fundadora**, que é usar
  apenas fontes gratuitas. É uma limitação medida, declarada, e com o custo conhecido.
- **E o Capítulo 1 nunca promete velocidade.** Promete um alerta que a pessoa consegue seguir e
  conferir. O valor não está em chegar primeiro.

---

## Q10. "Onde está a Inteligência Artificial?"

> *"Um encoder de 2021 tirado da prateleira e uma regressão logística. Onde está a IA num mestrado
> de Engenharia de IA?"*

**A resposta.** Esta é a pergunta que mais parece um insulto e é a mais fácil, se não fores
defensivo.

- **Está em escolher, medir e saber rejeitar.** Testei o encoder de domínio e dois modernos, no
  mesmo protocolo: o FinBERT financeiro dá `0.420` contra `0.514` do genérico pequeno; o E5 e o BGE
  **empatam**. A escolha está validada por medição, não por conveniência.
- **E sei explicar porque o de domínio perdeu**, que é a parte que vale: medi-o com a média dos seus
  vetores a servir de vetor de frase, e ele é afinado para **classificação de sentimento**, não
  para pôr frases num espaço onde a distância signifique semelhança. É precisamente esse objetivo de
  treino que o Sentence-BERT acrescenta. Logo o que mostro é que *este* modelo de domínio, usado
  *desta* forma, perde — não que conhecimento de domínio não sirva.
- **Está em treinar um modelo e publicar que ele perdeu**, com a ablação que explica porquê.
- **Está na engenharia de produção:** exportar o mesmo modelo para correr num contentor de 512 MB e
  **provar** que continua a ser o mesmo (top-3 idênticos em 20 de 23 consultas), instrumentar as
  decisões depois de implantar, e apanhar por medição que o modelo estava a mais.

**⚠️ A armadilha:** pedir desculpa por não haver *deep learning* novo. A tese é de **Engenharia** de
IA: a contribuição é integrar, aplicar e avaliar criticamente. Dizer isso com naturalidade vale mais
do que qualquer arquitetura.

---

## Antes de entrares na sala

**Os números que tens de saber de cor** (e mais nenhum):

| Número | O que é |
|---|---|
| `0.015` vs `0.344` | amplitude de disparo: *z*-score vs limiar fixo (QI1) |
| `0.530` vs `0.269` / `0.280` | F1: *z*-score vs Isolation Forest vs LOF |
| `0.514` vs `0.467` | precisão@5 vs o chão trivial *sempre tecnologia* (QI2) |
| `0.513` vs `0.259` | precisão@5 causal vs chão; margem `+0.254` |
| `0.595` vs `0.333` | teste simétrico de escala; permite candidatos futuros |
| `0.708` vs `0.688` | concordância de direção vs acaso: **tema ≠ direção** |
| `0.496` vs `0.542` | PR-AUC: contexto+texto vs só volatilidade (QI3) |
| `0.534` vs `0.538` | tabela de consulta vs modelo implantado |
| `+0.012` `[+0.004, +0.020]` | o que o texto acrescenta por cima da tabela |
| `353 min` / `5 s` | descoberta / entrega |
| `48%` | títulos distintos determinados pela empresa antes de ler a notícia |

**O que NÃO dizer, em nenhuma circunstância:**

- ❌ **"quase quadruplica"** ou **"2,1 vezes o acaso"** — números retirados.
- ❌ **"0,667 contra 0,455"** — eram doze decisões, o intervalo continha a taxa-base.
- ❌ **"a minha RQ3 é sobre as explicações"** — na tese curta a QI3 é a **triagem**.
- ❌ **"era computacionalmente inviável"** sobre os betas de Vasicek — não era. A razão verdadeira é
  que obrigaria a retreinar as seis famílias para chegar à mesma conclusão com outro número.
- ✅ **Hevner / Design Science Research** — **podes** usá-los: a §3.1 cita os dois. (Correcção a 2026-08-26: eu tinha dito o contrário, e estava enganado.)

**As três frases com que abres, se te esqueceres de tudo o resto:**

> *"Construí um sistema que explica movimentos de mercado a quem não é especialista, e que nunca
> prevê. Avaliei cada componente contra a alternativa mais simples que responde à mesma pergunta.
> Em três casos a simples ganhou, e foi ela que ficou."*

**E a última coisa.** Duas críticas hostis geradas por ferramentas externas produziram vinte
acusações a este trabalho, e **dezanove já estavam escritas na tese**, em parágrafos que existem
para as antecipar. Se te fizerem uma pergunta difícil, a probabilidade mais alta é que a resposta
já esteja no documento. Respira e diz onde.
