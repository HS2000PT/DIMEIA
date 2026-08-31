# Registo de cortes — noite de 30/08/2026

**Estado:** 141 → **136 páginas**, 56 281 → **52 539 palavras**, 34 → **28 tabelas**.
Compila a 0 erros, 0 referências indefinidas.

Cada corte está aqui com o texto original. **Nenhuma evidência, número, tabela de resultados ou
limitação foi removida.** Para reverter, procura o bloco `orig` e repõe-no.

---

## 1. Perguntas retóricas a abrir secção (34 removidas)

Nenhum dos quatro exemplos abre secções com uma pergunta em itálico. Era o traço estilístico mais
visível do documento.

- `\emph{Que problema é este, e porque é que vale a pena resolvê-lo?}` — `cap1`
- `\emph{Se tivesse de explicar o InvestiGator numa frase, qual seria?}` — `cap1`
- `\emph{Quem é esta pessoa, e o que é que a literatura já sabe sobre a forma como ela decide?}` — `cap2`
- `\emph{Ninguém resolveu isto antes?}` — `cap2`
- `\emph{E os produtos recentes que prometem explicar porque é que uma ação subiu?}` — `cap2`
- `\emph{Como é que se decide, de forma defensável, que um dia foi diferente dos outros?}` — `cap2`
- `\emph{Como é que um computador decide que duas notícias falam do mesmo?}` — `cap2`
- `\emph{Encontrada uma representação, como se recupera o que interessa, e como se avalia isso?}` — `cap2`
- `\emph{Encontrados casos análogos, como se mede honestamente o que aconteceu ao preço a seguir?}` — `cap2`
- `\emph{Mostrar casos anteriores em vez de uma regra: isso tem nome?}` — `cap2`
- `\emph{Se o sistema decide, como é que mostra em que se baseou?}` — `cap2`
- `\emph{Treinar um modelo é uma coisa. Mantê-lo a funcionar é outra. O que diz a literatura?}` — `cap2`
- `\emph{Antes de explicar o que se faz com os dados: com que é que eles se parecem, exatamente?}` — `cap3`
- `\emph{Como é que um computador decide que 4\% é muito?}` — `cap3`
- `\emph{Como é que o computador percebe que duas notícias falam da mesma coisa?}` — `cap3`
- `\emph{Já sei que algo é invulgar. Devo mesmo interromper alguém?}` — `cap3`
- `\emph{O que impede um resultado bonito de ser um resultado enganador?}` — `cap3`
- `\emph{Que riscos é que um sistema destes cria, e o que é que este faz em relação a eles?}` — `cap3`
- `\emph{Como é que as peças se ligam?}` — `cap4`
- `\emph{O que é que este sistema usa de fora, e porquê essas e não outras?}` — `cap4`
- `\emph{O que acontece, exatamente, entre uma notícia sair e um alerta chegar ao telemóvel?}` — `cap4`
- `\emph{E quando não há notícia nenhuma?}` — `cap4`
- `\emph{Porque é que o sistema não avisa de quase nada?}` — `cap4`
- `\emph{O que é que a pessoa recebe, e porque é que se pode fiar?}` — `cap4`
- `\emph{Como é que um sistema destes se mantém a funcionar sem servidor pago?}` — `cap4`
- `\emph{Onde é que está, concretamente, a engenharia de inteligência artificial deste trabalho?}` — `cap4`
- `\emph{O que é que vale como prova?}` — `cap5`
- `\emph{Antes de ver os resultados: o que é que cada medida quer dizer, e como é calculada?}` — `cap5`
- `\emph{dos dias que eram mesmo invulgares, quantos é que o sistema apanhou?}` — `cap5`
- `\emph{das cinco notícias que escolho mostrar, quantas eram mesmo importantes?}` — `cap5`
- `\emph{As escolhas foram comparadas com alternativas concretas?}` — `cap5`
- `\emph{Cada componente foi comparado com a sua alternativa. E o conjunto?}` — `cap5`
- `\emph{Onde é que este trabalho é fraco?}` — `cap6`
- `\emph{Se houvesse mais três meses, por onde começava?}` — `cap6`

---

## 2. seccao reescrita — `cap4`

**Razão:** descricao de infraestrutura e de repositorio; o juri nao avalia o alojamento. Preservadas a tabela de latencia, a figura do ciclo e as licoes citadas no Cap. 6

<details><summary>Texto original</summary>

```latex
§4.8 completa (2111 palavras): narrativa de GitHub Actions vs Heroku, figura da infraestrutura, historia do disco efemero, e subseccao inteira sobre custo de memoria com tabela de tres formatos
```

</details>

**Ficou:**

```latex
§4.8 nova (853 palavras): latencia, ciclo de maturacao, e o essencial do defeito e da memoria em prosa
```

---

## 3. compressao — `cap5/capitulo5.tex`  (377 → 229 palavras)

**Razão:** tres paragrafos a fazer o mesmo argumento por tres vias, com enquadramento confessional; consolidados em tres paragrafos curtos. Nenhum numero perdido.

<details><summary>Texto original</summary>

```latex
\paragraph{E esse $84\%$ precisa de uma ressalva, que aponta contra o próprio argumento.}
O número conta \textbf{decisões registadas}, e o sistema repontua os mesmos títulos a cada ciclo
de sessenta segundos: o mesmo título entra dezenas de vezes. Pior, a duplicação não é uniforme.
É maior nas empresas com \emph{menos} notícias, que são precisamente as que nunca passam o piso,
pelo que contar decisões empurra a fração para cima, ou seja na direção que favorece a conclusão
que estou a defender.

Contado uma vez por título distinto, sobre uma janela posterior e maior
($36\,925$ decisões até 20 de agosto de 2026), a fração cai para $48\%$. A conclusão estrutural
não muda, e é ela que sustenta a decisão que se seguiu: continua a haver empresas inteiramente
de um dos lados do piso, e a amplitude entre empresas continua a ser várias vezes a amplitude
dentro de cada uma. O que muda é a força do número isolado, e fica assim escrito.

\paragraph{E este é o mesmo defeito que este trabalho já tinha identificado, um nível acima.}
A Secção~\ref{sec:av_qi1} mostra que um limiar fixo sobre o \emph{retorno} mede a volatilidade da
empresa e não a raridade do dia, e é essa a razão de ser do \emph{z}-score. O limiar fixo sobre a
\emph{pontuação do modelo} tem exatamente a mesma forma: como a pontuação é quase uma constante por
empresa, cortá-la num valor fixo ordena empresas, não notícias. Encontrei o meu próprio erro
repetido numa camada diferente.

\paragraph{Porque é que nada disto disparou um alarme.}
Convém explicar como um defeito desta dimensão sobrevive meses num sistema com centenas de testes,
porque a resposta é genérica e não específica deste trabalho. O modelo foi avaliado sobre a
distribuição do conjunto de treino e implantado atrás de dois filtros que a alteram: só chegam à
sua entrada títulos que já passaram relevância e frescura. Nenhum teste podia detetar isto, porque
cada peça cumpria o seu contrato; o que estava errado era uma suposição sobre a ligação entre elas,
que ninguém tinha escrito em lado nenhum. É a classe de custo que \textcite{sculley2015debt}
arrumam sob dependências de dados e emaranhamento entre componentes, e o sintoma que eles apontam verificou-se aqui
por inteiro: o sistema continuou a produzir números de aparência perfeitamente normal.
```

</details>

**Ficou:**

```latex
As duas contagens medem coisas diferentes e ambas ficam. O sistema repontua os mesmos títulos a
cada ciclo de sessenta segundos, e a duplicação é maior nas empresas com menos notícias, que são
as que nunca passam o piso; contar decisões empurra portanto a fração para cima. Contado uma vez
por título distinto, sobre uma janela maior de $36\,925$ decisões, a fração é de $48\%$. A
conclusão estrutural não depende de qual se escolha: continua a haver empresas inteiramente de um
dos lados do piso, e a amplitude entre empresas continua a ser várias vezes a amplitude dentro de
cada uma.

O defeito tem a mesma forma que o da Secção~\ref{sec:av_qi1}, uma camada acima: aí, um limiar fixo
sobre o retorno mede a volatilidade da empresa em vez da raridade do dia; aqui, um limiar fixo
sobre uma pontuação quase constante por empresa ordena empresas em vez de notícias.

Nenhum teste o podia detetar. O modelo foi avaliado sobre a distribuição do conjunto de treino e
implantado atrás de dois filtros que a alteram, e cada peça cumpria o seu contrato: o que estava
errado era uma suposição sobre a ligação entre elas, não escrita em lado nenhum. É a classe de
custo que \textcite{sculley2015debt} arrumam sob dependências de dados e emaranhamento entre
componentes, com o sintoma que eles descrevem: o sistema continua a produzir números de aparência
normal.
```

---

## 4. compressao — `cap5/capitulo5.tex`  (83 → 45 palavras)

**Razão:** encurtado; retirado o comentario ao proprio raciocinio anterior.

<details><summary>Texto original</summary>

```latex
Não é a mesma coisa que a redundância descrita acima, e as duas produzem o mesmo sintoma. Com o
que ficou registado não consigo atribuir peso a cada uma: o registo de decisões guarda a
probabilidade e o resultado, e não guarda o valor das entradas no momento em que a pontuação foi
feita. Separá-las exigiria registar as entradas, que é uma linha de código e uma corrida de
semanas. Fica dito porque a explicação que eu tinha dado era completa de mais.
```

</details>

**Ficou:**

```latex
As duas causas produzem o mesmo sintoma e o registo não permite atribuir peso a cada uma, porque
guarda a probabilidade e o resultado mas não o valor das entradas no momento da pontuação.
Separá-las exigiria registar essas entradas e voltar a observar durante semanas.
```

---

## 5. compressao — `cap3/capitulo3.tex`  (156 → 46 palavras)

**Razão:** historia de operacao (um limite mal dimensionado, corrigido) sem valor para o juri; mantida a consequencia, que e a nao reprodutibilidade daquela linha.

<details><summary>Texto original</summary>

```latex
\paragraph{A ressalva da última linha, porque é um defeito que encontrei a escrever esta tabela.}
O registo do funil guarda apenas os últimos dias, e isso quase passou despercebido. O limite estava
escrito em \textbf{número de linhas} ($5000$) e foi dimensionado quando o sistema corria de meia em
meia hora, o que dava cerca de oito dias de história. Com o ciclo de 60 segundos passaram a existir
trinta vezes mais registos, e o mesmo limite guarda \textbf{menos de um dia}: quando fui ler o
ficheiro publicado, as $5000$ linhas eram todas do próprio dia.

Uma retenção contada em linhas muda de significado sempre que a cadência muda; contada em dias, não
muda. Passou a ser contada em dias. Fica em três, e não numa semana, porque o ficheiro é
republicado a cada ciclo e o custo é de publicação, não de armazenamento. A restrição que fixa o
número está escrita em vez de parecer arbitrária.
```

</details>

**Ficou:**

```latex
O registo do funil retém apenas três dias por desenho, porque é republicado a cada ciclo e o custo
é de publicação e não de armazenamento. A consequência para a leitura da tabela está no
Apêndice~\ref{ap:reprodutibilidade}: é a única medição deste documento que não se regenera.
```

---

## 6. compressao — `cap3/capitulo3.tex`  (237 → 118 palavras)

**Razão:** narrativa de incidente operacional reduzida ao controlo que ficou implementado; mantida a razao de ser da mascara.

<details><summary>Texto original</summary>

```latex
Um sistema que corre sozinho e fala com serviços externos tem credenciais, e credenciais fogem.

As chaves nunca estão no repositório: vivem em variáveis de ambiente e no cofre de segredos da
plataforma. Isso é o mínimo e não chega, e a razão pela qual sei que não chega é que \textbf{falhou}.
As mensagens de erro de uma biblioteca de HTTP incluem o endereço do pedido, e o endereço de
algumas destas \glspl{API} leva a chave lá dentro. Bastou um dia em que uma fonte respondeu com
erro a todos os pedidos para a chave ficar escrita centenas de vezes no registo do serviço. O
código nunca imprimiu a chave: imprimiu a exceção.

A correção tem duas partes, e só a primeira é técnica. A primeira é uma função que mascara
qualquer parâmetro com nome de credencial em todo o texto que vai para o registo, e um teste que
usa a cadeia real que apareceu. A segunda é que \textbf{uma máscara não desfaz uma fuga}: a chave
exposta tem de ser substituída, e isso é uma operação humana que fica na lista de tarefas por
fazer.

Há ainda uma decisão de segurança do lado dos modelos. O codificador de frases é descarregado sob
pedido e verificado contra uma soma de controlo fixada no código. Sem essa verificação, um
descarregamento corrompido ou substituído mudaria em silêncio aquilo que o sistema entende por
``semelhante''; com ela, falha fechado.
```

</details>

**Ficou:**

```latex
Um sistema autónomo que consome serviços externos detém credenciais. As chaves vivem em variáveis
de ambiente e no cofre de segredos da plataforma, nunca no repositório, e todo o texto enviado para
os registos passa por uma função que mascara parâmetros com nome de credencial. Esta segunda
salvaguarda foi acrescentada depois de se observar que as mensagens de erro de bibliotecas de HTTP
reproduzem o endereço do pedido, e que algumas destas \glspl{API} transportam a chave nesse
endereço.

Do lado dos modelos, o codificador de frases é descarregado sob pedido e verificado contra uma soma
de controlo fixada no código. Sem essa verificação, um descarregamento corrompido ou substituído
alteraria em silêncio o que o sistema entende por ``semelhante''.
```

---

## 7. compressao — `apendices/apendiceA.tex`  (86 → 20 palavras)

**Razão:** descricao da organizacao de pastas e pacotes do repositorio: o juri avalia o documento e nao tem acesso ao codigo. Mantida a contagem de testes, que e evidencia.

<details><summary>Texto original</summary>

```latex
O código está organizado por componente, com um pacote para cada peça da
Figura~\ref{fig:arquitetura}: dados de mercado, recolha de notícias, deteção, motor de correlação,
base de casos, triagem, motor de explicação e entrega. A
lógica pura está separada da entrada e saída, e as dependências pesadas são carregadas só quando
precisas, e por isso o núcleo é testado sem rede e sem carregar modelos. A suite tem
\textbf{763 testes} automáticos.

Os segredos (chaves de API, credenciais) são lidos de um ficheiro local que nunca é versionado.
```

</details>

**Ficou:**

```latex
A verificação automática do sistema tem \textbf{763 testes}, entre os quais os que impõem a
separação temporal descrita na Secção~\ref{sec:met_avaliacao}.
```

---

## 8. compressao — `cap6/capitulo6.tex`  (520 → 291 palavras)

**Razão:** reflexao em primeira pessoa, com enquadramento de diario; mantidas as tres licoes e a discussao de Rudin, em registo descritivo.

<details><summary>Texto original</summary>

```latex
Termino com aquilo que mudou na minha cabeça ao longo destes meses, porque é a parte que não estava
no plano.

A primeira foi perceber que \textbf{a linha de base é tão importante como o modelo}. Passei semanas
a melhorar modelos e o resultado mais útil de todo o trabalho veio de olhar com atenção para aquilo
contra o qual os estava a comparar. Numa das medições, o valor que eu usava como ``escolher às
cegas'' não escolhia às cegas de todo: escolhia por ordem alfabética. Corrigir isso reduziu
para menos de metade um ganho que eu já tinha escrito.

A segunda foi perceber que \textbf{o sítio onde se põe um modelo importa tanto como o modelo}. O meu
funcionava razoavelmente quando avaliado sozinho e deixou de servir para nada quando colocado atrás
de dois filtros simples, que já faziam grande parte do trabalho. Isso não estava em nenhum sítio do
plano inicial, e é provavelmente a lição mais transferível que levo daqui.

E a terceira foi mais simples do que as outras: \textbf{a técnica mais simples ganhou três vezes}.
Ganhou ao Isolation Forest, ganhou ao modelo que lê o texto, e uma tabela de treze constantes ganhou
ao modelo que está implantado. Convém dizer também as duas vezes em que
foi ao contrário: uma janela mais longa e um desvio-padrão com pesos que decaem obtêm ambos um
$F_1$ melhor do que o que o sistema usa, e mantive o simples por ser explicável. Essas duas são
uma \emph{escolha}, e não um resultado, e é assim que estão escritas no Capítulo \ref{cap:avaliacao}.
Comecei este trabalho a assumir que o caminho para um bom resultado era acrescentar
sofisticação. Acabo-o com medições a dizer o contrário, e com a convicção de
que a parte difícil da engenharia de inteligência artificial não é escolher a técnica mais avançada,
é montar a avaliação que consegue dizer que ela não era precisa.

Esta conclusão não é minha nem é original, e é por isso que me deixa mais descansado do que se
fosse. \textcite{rudin2019stop} defende que, em decisões de consequência séria, se deve usar
modelos interpretáveis à partida em vez de explicar modelos opacos depois, e um dos argumentos é
que a diferença de desempenho que justificaria a opacidade muitas vezes não existe quando se
verifica. A primeira das minhas três comparações é uma instância disso, o \emph{z}-score contra dois
detetores cuja decisão não se lê, e há ainda uma quarta comparação, fora dessa lista e com a mesma
lição, que é a regressão logística contra as árvores com reforço do gradiente.

A das treze constantes não é, e convém não a arrumar na mesma prateleira só porque a conclusão
rima. A tabela de
treze constantes não venceu um modelo opaco: venceu uma regressão logística calibrada, que é
interpretável e cujas contribuições esta tese exibe uma a uma. Aquilo não é um argumento sobre
opacidade, é um argumento sobre \emph{informação}: o modelo perdeu para uma tabela porque as suas
entradas quase não variavam dentro de cada empresa, e não porque fosse complexo demais. São lições
diferentes, e juntá-las tornaria a mais interessante das duas invisível.
```

</details>

**Ficou:**

```latex
Três lições atravessam este trabalho, e nenhuma delas estava no plano inicial.

\textbf{A linha de base vale tanto como o modelo.} O resultado mais útil desta dissertação não veio
de melhorar modelos, veio de examinar aquilo contra o qual estavam a ser comparados: um chão de
comparação que aparentava escolher ao acaso ordenava por ordem alfabética, e corrigi-lo reduziu a
menos de metade um ganho já escrito.

\textbf{O lugar onde um modelo é colocado importa tanto como o modelo.} O componente aprendido
comportava-se razoavelmente avaliado isoladamente e deixou de acrescentar valor quando colocado
atrás de dois filtros que já faziam grande parte do trabalho. É a lição mais transferível do
trabalho, e generaliza-se: um componente é avaliado onde é treinado e é útil onde é colocado.

\textbf{A técnica mais simples venceu três comparações.} Venceu dois detetores de anomalias
aprendidos, venceu o modelo que lê o texto, e uma tabela de treze constantes venceu o modelo
implantado. Duas comparações correram em sentido contrário, e ficam registadas como escolhas e não
como resultados: uma janela mais longa e um desvio-padrão com pesos decrescentes obtêm ambos um
$F_1$ superior ao da regra usada, mantida por ser explicável.

As duas primeiras convergem com \textcite{rudin2019stop}, que defende o uso de modelos
interpretáveis à partida em decisões de consequência séria, com o argumento de que a diferença de
desempenho que justificaria a opacidade frequentemente não resiste à verificação. A terceira é de
outra natureza e não deve ser arrumada com elas: a tabela de treze constantes não venceu um modelo
opaco, venceu uma regressão logística calibrada cujas contribuições este documento exibe uma a uma.
Não é um argumento sobre opacidade, é um argumento sobre informação, porque as entradas do modelo
quase não variavam dentro de cada empresa.
```

---

## 9. titulo reescrito — `cap3/capitulo3.tex`

**Razão:** titulo em registo confessional; substituido por descritivo. O conteudo do paragrafo mantem-se.

<details><summary>Texto original</summary>

```latex
\paragraph{E há aqui um número que surpreende, por isso convém explicá-lo antes que espante.}
```

</details>

**Ficou:**

```latex
\paragraph{Porque é que o bloco de teste é maior do que o de treino.}
```

---

## 10. titulo reescrito — `cap4/capitulo4.tex`

**Razão:** titulo em registo confessional; substituido por descritivo. O conteudo do paragrafo mantem-se.

<details><summary>Texto original</summary>

```latex
\paragraph{E a ressalva é um defeito que encontrei ao construir esta tabela.}
```

</details>

**Ficou:**

```latex
\paragraph{Uma etapa que não estava instrumentada.}
```

---

## 11. titulo reescrito — `cap4/capitulo4.tex`

**Razão:** titulo em registo confessional; substituido por descritivo. O conteudo do paragrafo mantem-se.

<details><summary>Texto original</summary>

```latex
\paragraph{E este exemplo mostra um defeito que eu não tinha visto até o pôr aqui.}
```

</details>

**Ficou:**

```latex
\paragraph{O que o alerta afirma, e o que a medição sustenta.}
```

---

## 12. titulo reescrito — `cap5/capitulo5.tex`

**Razão:** titulo em registo confessional; substituido por descritivo. O conteudo do paragrafo mantem-se.

<details><summary>Texto original</summary>

```latex
\paragraph{Uma nota sobre o padrão de evidência desta secção, e é uma nota contra mim.}
```

</details>

**Ficou:**

```latex
\paragraph{Uma assimetria no padrão de evidência.}
```

---

## 13. titulo reescrito — `cap5/capitulo5.tex`

**Razão:** titulo em registo confessional; substituido por descritivo. O conteudo do paragrafo mantem-se.

<details><summary>Texto original</summary>

```latex
\paragraph{E há uma alternativa trivial que faltava a esta tabela, que é a que mais incomoda.}
```

</details>

**Ficou:**

```latex
\paragraph{Uma alternativa trivial que a tabela não continha.}
```

---

## 14. titulo reescrito — `cap5/capitulo5.tex`

**Razão:** titulo em registo confessional; substituido por descritivo. O conteudo do paragrafo mantem-se.

<details><summary>Texto original</summary>

```latex
\paragraph{O oráculo diz onde está o problema, e não é onde eu julgava.}
```

</details>

**Ficou:**

```latex
\paragraph{O oráculo localiza a limitação.}
```

---

## 15. titulo reescrito — `cap6/capitulo6.tex`

**Razão:** titulo em registo confessional; substituido por descritivo. O conteudo do paragrafo mantem-se.

<details><summary>Texto original</summary>

```latex
\paragraph{Escolhi para o produto um modelo que não podia fazer o que eu lhe estava a pedir.}
```

</details>

**Ficou:**

```latex
\paragraph{O modelo implantado não podia executar a função que lhe foi atribuída.}
```

---

## 16. tabela removida — `cap4/capitulo4.tex`  (669 → 142 palavras)

**Razão:** Tabela 4.1, duas paginas a listar dependencias externas com custos e limites de utilizacao: e descricao de infraestrutura, nao de metodo. Substituida por um paragrafo que retem o que e defensavel (a cadeia de precos, as tres fontes, as duas rejeicoes por medicao).

<details><summary>Texto original</summary>

```latex
\begin{table}[!htbp]
\caption[Tudo o que o sistema usa de fora]{As dependências externas, nomeadas. A coluna da direita
é a que interessa: uma escolha só se defende contra a alternativa que não foi tomada.}
\label{tab:sis_pecas}
\centering
\scriptsize
\begin{tabular}{L{0.15\textwidth} L{0.20\textwidth} L{0.16\textwidth} L{0.35\textwidth}}
\toprule
\tabhead{Peça} & \tabhead{Para quê} & \tabhead{Cus [...tabela completa de 64 linhas...]
```

</details>

**Ficou:**

```latex
O sistema assenta em serviços de terceiros, todos gratuitos, e cada um é uma dependência e um
limite. As notícias vêm de três fontes complementares, comparadas na Secção~\ref{sec:sis_fontes};
os preços vêm de uma cadeia de quatro alternativas tentadas por ordem fixa, porque nenhuma fonte
gratuita de preços é fiável sozinha e sem a cadeia um dia de bloqueio seria indistinguível de um
dia em que o mercado não abriu; o registo guarda sempre qual delas serviu, porque a origem de um
número faz parte de o poder explicar. A representação de frases usa um codificador pré-treinado,
escolhido por medição contra quatro alternativas (Secção~\ref{sec:av_alternativas}), e a entrega
usa a interface de robô do Telegram. Duas candidaturas foram rejeitadas por medição e não por
argumento: uma fonte de preços que responde com verificação anti-robô, e uma de notícias que não
permite consulta por empresa.
```

---

## 17. compressao — `cap5/capitulo5.tex`  (23 → 17 palavras)

**Razão:** a tabela-resumo das tres QI e a mesma informacao da Figura 6.1 no capitulo seguinte; mantida so a figura.

<details><summary>Texto original</summary>

```latex
A Tabela~\ref{tab:av_resumo} junta as três. Duas das respostas são afirmativas e uma é negativa. A negativa é a que eu mais aprendi a
```

</details>

**Ficou:**

```latex
Duas das respostas são afirmativas e uma é negativa. A negativa é a que mais custou a
```

---

## 18. tabela removida — `cap5/capitulo5.tex`  (154 → 0 palavras)

**Razão:** duplicava a Figura 6.1 (As tres perguntas e as suas respostas), que apresenta a mesma informacao no capitulo das conclusoes.

<details><summary>Texto original</summary>

```latex
\begin{table}[ht]
\caption[As três perguntas e as suas respostas]{O veredicto de cada questão de investigação.}
\label{tab:av_resumo}
\centering
\small
\begin{tabular}{L{0.16\textwidth} L{0.14\textwidth} L{0.56\textwidth}}
\toprule
\tabhead{Pergunta} & \tabhead{Resposta} & \tabhead{Com base em quê} \\
\midrule
\textbf{QI1} deteção & \textbf{Sim} & Amplitude de disparo $0.015$ contra $0.344$; e ganha a dois
métodos aprendidos ($F_1$ $0.530$ contra $0.269$ e $0.280$) \\
\textbf{QI2} precedentes & \textbf{Sim} & Sob a restrição causal da produção, precisão@5 de
$0.513$, chão $0.259$ e margem $+0.
[...]
```

</details>

**Ficou:**

```latex
(removido por completo)
```

---

## 19. compressao — `cap4/capitulo4.tex`  (22 → 6 palavras)

**Razão:** remissao para a tabela removida

<details><summary>Texto original</summary>

```latex
A Figura~\ref{fig:caminho} mostra as etapas. A Tabela~\ref{tab:sis_caminho} mostra o que aconteceu
em cada uma, com os valores que o sistema realmente calculou.
```

</details>

**Ficou:**

```latex
A Figura~\ref{fig:caminho} mostra as nove etapas.
```

---

## 20. tabela removida — `cap4/capitulo4.tex`  (282 → 0 palavras)

**Razão:** uma pagina a repetir, linha a linha, as nove etapas que a Figura 4.2 ja apresenta. Os valores do caso real passaram para prosa a seguir a figura, sem perder nenhum numero.

<details><summary>Texto original</summary>

```latex
\begin{table}[!htbp]
\caption[Uma notícia real, etapa a etapa]{O que aconteceu em cada etapa para o alerta da Meta de 12
de julho de 2026. Todos os valores são os que o sistema calculou nesse dia.}
\label{tab:sis_caminho}
\centering
\small
\begin{tabular}{L{0.24\textwidth} p{0.66\textwidth}}
\toprule
\tabhead{Etapa} & \tabhead{O que aconteceu} \\
\midrule
1. Recolher & A varredura foi buscar as notícias da semana para cada empresa da lista. \\
2. Nomeia a empresa? & O título diz ``Meta'' e ``Mark Zuckerberg'', que estão na lista de nomes da
empresa, e não corresponde a nenhum padrão de texto a
[...]
```

</details>

**Ficou:**

```latex
(removido por completo)
```

---

## 21. compressao — `cap3/capitulo3.tex`  (26 → 72 palavras)

**Razão:** remissao para a tabela removida; os dois valores e a verificacao da normalizacao passaram para prosa.

<details><summary>Texto original</summary>

```latex
A Tabela~\ref{tab:met_cosseno} segue a conta para dois pares de títulos retirados da base de
casos. São reais, e os valores são os que o sistema calcula.
```

</details>

**Ficou:**

```latex
Dois pares reais, retirados da base de casos, situam a escala. No primeiro, dois títulos sobre a
descida de empresas de tecnologia e semicondutores dão $\cos = +0.956$. No segundo, um título sobre
a Peloton e outro sobre o impacto da pandemia na indústria automóvel dão $\cos = -0.086$. Nos
quatro vetores o comprimento vale exatamente $1$, o que confirma a normalização e faz o cosseno
coincidir com a soma dos produtos.
```

---

## 22. tabela removida — `cap3/capitulo3.tex`  (166 → 0 palavras)

**Razão:** os dois valores desta tabela ($+0.956$ e $-0.086$) ja aparecem desenhados na Figura 3.8, e os titulos completos ocupavam meia pagina sem acrescentar ao argumento.

<details><summary>Texto original</summary>

```latex
\begin{table}[ht]
\caption[O cosseno entre dois títulos reais]{Dois pares do lado oposto da escala. Repare-se na
linha do comprimento: vale exatamente $1$ nos quatro vetores, o que confirma a normalização e faz o
cosseno coincidir com a soma dos produtos.}
\label{tab:met_cosseno}
\centering
\small
\begin{tabular}{L{0.26\textwidth} L{0.30\textwidth} L{0.30\textwidth}}
\toprule
 & \tabhead{Par A: mesmo assunto} & \tabhead{Par B: assuntos diferentes} \\
\midrule
Primeiro título & ``Shares of several companies in the technology, software and semiconductor
space are trading lower\ldots'' & ``Peloto
[...]
```

</details>

**Ficou:**

```latex
(removido por completo)
```

---

## 23. compressao — `cap3/capitulo3.tex`  (10 → 13 palavras)

**Razão:** remissao para a tabela removida, na legenda da Figura 3.8

<details><summary>Texto original</summary>

```latex
Os dois valores são os do par real da
Tabela~\ref{tab:met_cosseno}.}
```

</details>

**Ficou:**

```latex
Os dois valores são os de um par real da base de casos.}
```

---

## 24. compressao — `cap3/capitulo3.tex`  (37 → 85 palavras)

**Razão:** tabela de doze linhas a documentar colunas de um ficheiro CSV: e documentacao de dados, nao metodo. A distincao que importava, que colunas veem o futuro, ficou em prosa.

<details><summary>Texto original</summary>

```latex
A Tabela~\ref{tab:met_colunas} diz o que cada coluna é, de onde vem, e a pergunta que mais importa:
\textbf{consegue esta coluna ver o futuro?} É a pergunta que separa uma avaliação honesta de uma
avaliação impossível de acreditar.
```

</details>

**Ficou:**

```latex
A pergunta que separa uma avaliação honesta de uma avaliação impossível de acreditar é, para cada
coluna, \textbf{se ela consegue ver o futuro}. Só as colunas de rótulo o fazem, porque é isso que
um rótulo é. A \texttt{ret\_event} exige uma precisão adicional: no protocolo \emph{offline} não vê
nada posterior ao fecho de $d$, que é o referencial em que a linha é construída, mas no instante em
que uma notícia chega durante a sessão esse fecho ainda é futuro. As restantes descrevem o passado.
```

---

## 25. tabela removida — `cap3/capitulo3.tex`  (216 → 0 palavras)

**Razão:** dicionario de colunas do conjunto de treino. Documentacao de dados sem valor para a avaliacao do trabalho.

<details><summary>Texto original</summary>

```latex
\begin{table}[ht]
\caption[O dicionário de colunas]{Cada coluna do conjunto de treino, a sua origem, e se pode ou não
conter informação posterior ao momento da decisão.}
\label{tab:met_colunas}
\centering
\small
\begin{tabular}{L{0.20\textwidth} L{0.40\textwidth} C{0.13\textwidth} L{0.15\textwidth}}
\toprule
\tabhead{Coluna} & \tabhead{O que é} & \tabhead{Vê o futuro?} & \tabhead{Origem} \\
\midrule
\texttt{date} & dia de negociação a que a notícia foi alinhada & não & calculado \\
\texttt{news\_date} & data que a fonte declara para a notícia & não & \gls{FNSPID} \\
\texttt{ticker} & empresa &
[...]
```

</details>

**Ficou:**

```latex
(removido por completo)
```

---

## 26. compressao — `cap3/capitulo3.tex`  (10 → 10 palavras)

**Razão:** remissao para a tabela removida

<details><summary>Texto original</summary>

```latex
Essa fronteira intradiária é a ressalva já declarada na
Tabela~\ref{tab:met_colunas}.
```

</details>

**Ficou:**

```latex
Essa fronteira intradiária é a ressalva já declarada na
Secção~\ref{sec:met_dados}.
```

---

## 27. compressao — `cap3/capitulo3.tex`  (15 → 15 palavras)

**Razão:** designacao que dependia da tabela removida

<details><summary>Texto original</summary>

```latex
Para tornar a soma concreta, eis as quatro primeiras das $384$ parcelas do par A:
```

</details>

**Ficou:**

```latex
Para tornar a soma concreta, eis as quatro primeiras das $384$ parcelas do primeiro par:
```

---

## 28. compressao — `cap3/capitulo3.tex`  (20 → 20 palavras)

**Razão:** idem

<details><summary>Texto original</summary>

```latex
que conta é os dois vetores concordarem naquela dimensão, e não o sinal em si. E note-se, no par B,
```

</details>

**Ficou:**

```latex
que conta é os dois vetores concordarem naquela dimensão, e não o sinal em si. E note-se, no segundo par,
```

---

## 29. compressao — `cap3/capitulo3.tex`  (21 → 20 palavras)

**Razão:** idem

<details><summary>Texto original</summary>

```latex
O chão de semelhança usado em produção é $0.45$. O par A passaria com folga; o par B nem se aproxima.
```

</details>

**Ficou:**

```latex
O chão de semelhança usado em produção é $0.45$: o primeiro par passaria com folga, o segundo nem se aproxima.
```

---

## 30. compressao — `apendices/apendiceA.tex`  (6 → 43 palavras)

**Razão:** tabela de dez versoes de biblioteca convertida em prosa: a informacao e a mesma e ocupa cinco linhas em vez de meia pagina.

<details><summary>Texto original</summary>

```latex
nada. A Tabela~\ref{tab:ap_versoes} lista as principais.
```

</details>

**Ficou:**

```latex
nada. As versões com que todos os números deste documento foram produzidos são
\texttt{numpy}~2.1.3, \texttt{pandas}~2.2.3, \texttt{scikit-learn}~1.9.0,
\texttt{matplotlib}~3.11.0, \texttt{yfinance}~1.4.1, \texttt{sentence-transformers}~5.6.0,
\texttt{transformers}~5.12.1 e \texttt{torch}~2.12.1 na variante para CPU. Estão fixadas, e não em
intervalos, porque uma biblioteca que muda sozinha muda os resultados sem aviso.
```

---

## 31. tabela removida — `apendices/apendiceA.tex`  (101 → 0 palavras)

**Razão:** lista de versoes de dependencias, passada para prosa no paragrafo anterior.

<details><summary>Texto original</summary>

```latex
\begin{table}[H]
\caption[Versões fixadas das dependências]{As versões com que todos os números deste
documento foram produzidos, lidas do ficheiro de dependências do repositório. Estão fixadas, e
não em intervalos, porque uma biblioteca que muda sozinha muda os resultados sem aviso.}
\label{tab:ap_versoes}
\centering
\small
\begin{tabular}{l l l l}
\toprule
\tabhead{Biblioteca} & \tabhead{Versão} & \tabhead{Biblioteca} & \tabhead{Versão} \\
\midrule
numpy & 2.1.3 & sentence-transformers & 5.6.0 \\
pandas & 2.2.3 & transformers & 5.12.1 \\
scikit-learn & 1.9.0 & torch (versão CPU) & 2.12.1 \\

[...]
```

</details>

**Ficou:**

```latex
(removido por completo)
```

---

## 32. seccao comprimida — `cap5/capitulo5.tex`  (2103 → 723 palavras)

**Razão:** §5.2 ocupava 5 paginas a explicar precisao, cobertura, F1, precisao@k, PR-AUC e Brier com tres figuras didaticas. Um juri de mestrado em IA conhece estas medidas. Mantidas as definicoes, todas as formulas em linha, todos os numeros, a tabela-resumo e — sobretudo — os chaos de cada medida, que e a parte que este capitulo usa. Removidas as Figuras 5.1, 5.2 e 5.3.

<details><summary>Texto original</summary>

```latex
\section{Como se lê cada número deste capítulo}
\label{sec:av_metricas}

Esta secção existe porque um resultado só vale o que vale a medida que o produziu. Um número como
``$F_1 = 0.530$'' não diz nada a quem não sabe o que é o $F_1$, e um leitor que aceite esse número
sem o compreender não está a avaliar o trabalho: está a confiar nele. Percorro por isso cada medida
usada, com a fórmula, com o que ela premeia, e com a conta feita até ao valor que aparece mais à
frente.

\subsection{As quatro maneiras de acertar e de errar}
\label{sec:av_matriz}

Todas as medidas deste capítulo, à exceção de uma, assentam na mesma ideia de partida. O sistema faz
uma afirmação sobre um dia, a realidade tem um
[... 5 paginas ...]
```

</details>

**Ficou:**

```latex
\section{Como se lê cada número deste capítulo}
\label{sec:av_metricas}

Um resultado vale o que vale a medida que o produziu, e este capítulo usa cinco. Esta secção define
cada uma e, sobretudo, fixa o seu \textbf{chão} --- o valor que um método sem informação nenhuma
obtém --- porque uma medida lida sem o seu chão dá a conclusão errada, e este capítulo documenta
três ocasiões em que isso aconteceu.

Todas assentam nas quatro combinações entre o que o sistema afirma e o que a realidade tem:
verdadeiros e falsos positivos, verdadeiros e falsos negativos. Os dois erros não são simétricos e
custam coisas diferentes: um falso positivo gasta a atenção de quem lê, um falso negativo deixa
passar o
[...]
```

---


# Parte 2 — segunda volta de cortes

**Estado final desta noite:** 141 → **118 páginas**, 56 281 → **51 447 palavras**, 34 → **27 tabelas**.
Compila a 0 erros. Os seis verificadores do projeto passam todos (53/53 números).

---

## P2.1 — seccao comprimida — `apendices/apendiceA.tex`  (444 → 284 palavras)

**Razão:** A.5 descrevia em tres paginas um estudo que nao foi corrido, com o registo das decisoes de desenho contado em primeira pessoa. Mantido o desenho completo (duas condicoes, contrabalanco cruzado, pergunta, salvaguardas, bloco retirado), em registo descritivo.

<details><summary>Texto original</summary>

```latex
\section{O estudo com pessoas: desenhado, congelado, por correr}
\label{sec:ap_estudo}

A limitação mais séria deste trabalho é não ter sido testado com um único utilizador. O
Capítulo~\ref{cap:conclusoes} refere um protocolo ``já montado'', e uma afirmação dessas não vale
nada se o leitor não a puder conferir. Fica aqui o desenho, para que a diferença entre \emph{não
foi feito} e \emph{não foi pensado} seja visível.

\textbf{As duas condições.} Seis alertas reais, tirados do canal, nunca inventados. A condição A
mostra o facto nu, a condição B mostra o alerta completo com a explicação. Dois dos seis são casos
em que o tema e a direção discordam, que é onde a Secção~\ref{sec:av_qi2} mostra q
[...]
```

</details>

**Ficou:**

```latex
\section{O estudo com utilizadores: desenho}
\label{sec:ap_estudo}

A limitação mais séria deste trabalho é não ter sido testado com utilizadores. O
Capítulo~\ref{cap:conclusoes} refere um protocolo já preparado, e o seu desenho fica aqui para que
essa afirmação possa ser conferida.

O estudo compara duas condições sobre seis alertas reais retirados do canal: a condição~A apresenta
o facto sem explicação, a condição~B apresenta o alerta completo. Dois dos seis são casos em que o
tema e a direção do movimento discordam, que é onde a Secção~\ref{sec:av_qi2} mostra o sistema ser
mais fácil de interpretar mal. O contrabalanço cruza dois fatores: a ordem das condições e qual das
metades dos estím
[...]
```

---

## P2.2 — seccao comprimida — `cap3/capitulo3.tex`  (864 → 526 palavras)

**Razão:** §3.9.3 mantinha os quatro temas eticos mas com enquadramento narrativo e repeticoes. Comprimida sem perder nenhuma das quatro questoes nem nenhuma limitacao assumida.

<details><summary>Texto original</summary>

```latex
\subsection{Questões éticas e sociais}
\label{sec:met_etica}

Quatro, por ordem de importância. As três primeiras são decisões de desenho; a última é uma
restrição que se descobriu tarde e que não se escolheu.

\paragraph{Não aconselhar, e não prever.} A restrição fundadora deste trabalho é também a sua
principal salvaguarda ética. Um sistema que dissesse a alguém o que vai acontecer ao preço estaria
a emitir uma previsão que ninguém pode conferir no momento em que é lida; um que dissesse o que
comprar estaria dentro de uma atividade regulada, no sentido corrente de recomendar um
instrumento financeiro a uma pessoa concreta. Convém dizer com que estatuto esta frase aparece:
é uma fronteira d
[...]
```

</details>

**Ficou:**

```latex
\subsection{Questões éticas e sociais}
\label{sec:met_etica}

\paragraph{Não aconselhar, e não prever.} A restrição fundadora do trabalho é também a sua
principal salvaguarda ética. Um sistema que anunciasse o que vai acontecer ao preço emitiria uma
previsão que ninguém pode conferir no momento em que a lê; um que indicasse o que comprar entraria
numa atividade regulada. Importa o estatuto desta fronteira: é de \textbf{desenho}, traçada por
prudência e não a partir de uma análise do direito aplicável. Não houve parecer jurídico, a
bibliografia não tem fontes legais, e operar isto como serviço exigiria obtê-lo antes.

A garantia aplica-se ao que o sistema \textbf{escreve} e não ao que ele \te
[...]
```

---

## P2.3 — seccao comprimida — `cap2/capitulo2.tex`  (808 → 431 palavras)

**Razão:** §2.11 dedicava tres paragrafos a explicar a validade condicional da predicao conformal, materia que o Capitulo 6 volta a tratar por inteiro. Mantidas as tres questoes, as duas precisoes que decidem a nao adocao, e todas as citacoes.

<details><summary>Texto original</summary>

```latex
\section{Um modelo que continua a funcionar depois de implantado}
\label{sec:ctx_producao}

Este trabalho inclui um componente aprendido, cuja função é ordenar notícias por materialidade
esperada, e esse componente levanta três questões que a literatura trata separadamente.

A primeira é a de saber contra que teto comparar um modelo simples. Conjuntos de árvores treinados
por reforço do gradiente \autocite{friedman2001gbm} são uma família de modelos não lineares forte e amplamente
usada em dados tabulares, capaz de captar interações e efeitos não lineares que uma regressão
logística não capta, e servem por isso de referência superior contra a qual o modelo interpretável é
medido no Capítulo~
[...]
```

</details>

**Ficou:**

```latex
\section{Um modelo que continua a funcionar depois de implantado}
\label{sec:ctx_producao}

O componente aprendido deste trabalho levanta três questões que a literatura trata separadamente.

A primeira é contra que teto comparar um modelo simples. Conjuntos de árvores treinados por reforço
do gradiente \autocite{friedman2001gbm} captam interações e efeitos não lineares que uma regressão
logística não capta, e servem por isso de referência superior no Capítulo~\ref{cap:avaliacao}. Não
se afirma que sejam o melhor método existente, porque essa seria uma afirmação sobre um campo
inteiro.

A segunda é a honestidade do número produzido. Uma pontuação só é honesta para quem a lê se for uma
probabi
[...]
```

---

## P2.4 — compressao — `cap2/capitulo2.tex`  (9 → 5 palavras)

**Razão:** remissao para a tabela removida

<details><summary>Texto original</summary>

```latex
vias, ilustradas na Figura~\ref{fig:ctx_xai} e comparadas na Tabela~\ref{tab:ctx_xai}: modelos
```

</details>

**Ficou:**

```latex
vias, ilustradas na Figura~\ref{fig:ctx_xai}: modelos
```

---

## P2.5 — tabela removida — `cap2/capitulo2.tex`  (108 → 0 palavras)

**Razão:** a tabela comparava LIME, SHAP e modelos transparentes com as mesmas forcas e limitacoes que os tres paragrafos anteriores ja enunciam, e que a Figura 2.3 ja divide nas duas vias.

<details><summary>Texto original</summary>

```latex
\begin{table}[ht]
\caption[Abordagens de explicabilidade consideradas]{As opções ponderadas, e a razão da escolha feita
neste trabalho.}
\label{tab:ctx_xai}
\centering
\small
\begin{tabular}{L{0.20\textwidth} L{0.24\textwidth} L{0.42\textwidth}}
\toprule
\tabhead{Método} & \tabhead{Tipo} & \tabhead{Forças e limitações} \\
\midrule
LIME \autocite{ribeiro2016lime}
  & Substituto local, a posteriori
  & Intuitivo e agnóstico ao modelo; as explicações podem ser instáveis e só valem localmente \\
\addlinespace
SHAP \autocite{lundberg2017shap}
  & Atribuição por valores de Shapley
  & Fundamentação
```

</details>

**Ficou:**

```latex
(removido por completo)
```

---

## P2.6 — opcao de formato — `main.tex`  (3 → 88 palavras)

**Razão:** opcao `oneside` acrescentada: remove as 18 paginas em branco impostas pelo formato frente-e-verso. Nenhum conteudo alterado. Reversivel apagando uma linha.

<details><summary>Texto original</summary>

```latex
\documentclass[
11pt,
singlespacing,
```

</details>

**Ficou:**

```latex
\documentclass[
11pt,
% ⚠️ DECISAO A CONFIRMAR COM O ORIENTADOR. A classe base e `book`, que e twoside por
% omissao: cada seccao do inicio e cada capitulo abriam em pagina impar, o que produzia
% 18 paginas em branco (11 no inicio, 7 entre capitulos). Com `oneside` o documento passa
% de 136 para 118 paginas sem perder uma unica linha de conteudo. Se a entrega final tiver
% de ser impressa em frente e verso, basta apagar esta linha para voltar ao formato anterior.
oneside,
singlespacing,
```

---
