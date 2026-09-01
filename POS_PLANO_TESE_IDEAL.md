# Pós-plano — a tese que o autor quer escrever

> **Isto não é para agora.** O `PLANO_FINAL_2026-09-01.md` manda até à defesa. Este ficheiro
> regista a visão que o Henrique descreveu a 2026-09-01, para não se perder, e separa três
> coisas: o que dela cabe nos dias que faltam, o que é uma tese diferente, e **duas correções
> sem as quais a visão não sobrevive a uma defesa**.
>
> As correções vão primeiro, de propósito. Não são discordância com o objetivo — são o que
> falta para o objetivo aguentar a primeira pergunta do júri.

---

## Correção 1 — o valor de negócio não pode ser a velocidade

**O que foi descrito.** Quem obtém a informação primeiro tem vantagem competitiva: vende antes
e perde menos, compra antes e ganha mais. O tempo é dinheiro, sobretudo em mercados.

**Porque não pode ser esse o argumento desta dissertação**, e o problema é interno ao próprio
documento:

1. **A medição contradi-lo.** O Capítulo 4 reporta 353 minutos de mediana entre a publicação de
   uma notícia e a sua deteção pelas fontes gratuitas. Este sistema nunca é o primeiro, e não
   pode ser: a restrição fundadora é usar apenas fontes gratuitas. Uma introdução que promete
   vantagem por velocidade prepara uma contradição que o júri encontra vinte páginas à frente.
2. **A conclusão contradi-lo.** A resposta à QI3 é negativa. Se o valor prometido fosse
   antecipação, a dissertação teria de concluir que falhou.
3. **A posição ética contradi-lo.** «Vender cedo para perder menos» é aconselhamento de
   investimento. A Secção 3.8.3 constrói, com cuidado, a recusa de prever e de aconselhar, e é
   essa recusa que torna tudo o resto verificável. Pôr o oposto na introdução desfaz o trabalho
   de um capítulo inteiro.

**O argumento que funciona, e é mais forte.** O valor não está em chegar primeiro; está em
**compreender**, num mercado onde compreender está reservado a quem paga. O investidor
particular olha para uma variação percentual e não sabe se é invulgar para aquela ação, se veio
da empresa ou do mercado inteiro, nem se já aconteceu antes. As três perguntas têm resposta —
os terminais profissionais respondem-lhes — e essa resposta não está disponível em regime
gratuito. **A lacuna é de acesso, não de método**, e é exatamente isso que a dissertação já
diz. A introdução deve dizê-lo também.

E há valor de negócio real nesse enquadramento, mensurável e citável em 2026: a dimensão do
mercado retalhista, a fração da população exposta a ações, o custo de atenção mal gasta
(alertas que não são lidos deixam de proteger seja quem for — a fadiga de alertas está medida
noutros domínios e citada no Capítulo 3), e o custo concreto de ler mal um movimento de mercado
inteiro como se fosse da empresa. Nada disto exige prometer antecipação.

**O que a introdução ganha:** números de 2026, uma oportunidade nomeada, e uma promessa que o
resto do documento cumpre.

---

## Correção 2 — testar todas as combinações não é o método mais rigoroso; é o menos

**O que foi descrito.** Construir cada técnica como um componente que comunica com qualquer
outro, e depois testar todas as combinações e todas as ordens, ficando com a melhor. A escolha
fica justificada porque foi medida.

**A intuição está certa e o desenho está certo.** Componentes intermutáveis, com interfaces
explícitas, é boa engenharia — e é, aliás, o que o sistema já tem. O problema não é a
arquitetura. É o que se conclui do varrimento.

**Dois problemas, e o segundo é fatal:**

1. **Tamanho.** Com $k$ componentes há $2^k-1$ subconjuntos; com ordem, $\sum_k k!$. Cinco
   componentes dão 31 subconjuntos e 325 sequências. Dez dão 1023 e mais de nove milhões.
   Somando hiperparâmetros, pré-processamento e features — que a descrição inclui, e bem — o
   espaço deixa de ser percorrível, e percorrer só uma parte dele reintroduz a escolha
   arbitrária que o varrimento existia para eliminar.

2. **Comparações múltiplas.** Este é o que desfaz o argumento. Escolher a melhor de $N$
   configurações sobre o mesmo conjunto de teste **enviesa o vencedor para cima**: parte da
   margem que ele mostra é sorte, não mérito, e a magnitude do enviesamento cresce com $N$.
   Com 31 configurações e um conjunto de teste da dimensão do que existe aqui, o «vencedor»
   pode ser inteiramente ruído de seleção. A pergunta *«sobre que conjunto escolheu a melhor?»*
   é das primeiras que um júri de engenharia faz, e a resposta «sobre o teste» encerra a
   discussão.

**A forma que sobrevive, e que continua a ser exaustiva onde importa:**

| | |
|---|---|
| **Componentes** | Poucos e pré-registados. Três ou quatro, escolhidos antes de correr nada. |
| **Onde se escolhe** | Sobre a **validação**, nunca sobre o teste. |
| **O teste** | Tocado **uma vez**, no fim, só com a configuração escolhida. |
| **O que se reporta** | Não só o vencedor: a dispersão entre todas as configurações. É ela que mostra ao leitor quanto da margem do vencedor é seleção. |
| **Ordem dos componentes** | Só se a ordem tiver significado; caso contrário é espaço de busca gasto sem hipótese. |

**E uma observação que talvez surpreenda: a dissertação atual já faz algo mais forte do que o
varrimento.** Ela tem comparações emparelhadas, fixadas antes de correr, com as alternativas
derrotadas reportadas — incluindo três casos em que a opção implantada **não** ganhou. Isso é
evidência que não pode ser acusada de escolha a posteriori, e é precisamente o que um
varrimento sobre o teste não consegue oferecer. O caminho a seguir é **acrescentar** ablações
pré-registadas a essa base, e não substituí-la por um varrimento.

---

## Correção 3 — «não descartar nada» precisa de critérios escritos antes

Na revisão da literatura, o objetivo de considerar tudo e explicar porque é que cada coisa
serve ou não é o objetivo certo, e distingue uma revisão real de uma lista de referências.

A forma prática: **fixar os critérios de exclusão antes do levantamento** e aplicá-los a
todas as famílias, para que «considerámos X e excluímos por Y» seja uma decisão documentada e
não uma omissão. Sem isso, «não descartar nada» transforma-se em cinquenta páginas de
enumeração que o limite de 120 não comporta e que ninguém lê.

Critérios que este trabalho já pode declarar, porque decorrem das suas restrições fundadoras:
custo de execução compatível com fontes gratuitas; explicabilidade da saída; ausência de
previsão de preço; e reprodutibilidade sem credenciais pagas. Uma família excluída por um
destes é uma linha na tabela, com a razão — não uma ausência.

---

## O que da visão cabe nos dias que faltam

| Peça | Cabe? | Custo | Nota |
|---|---|---|---|
| Introdução reescrita: valor, oportunidade e números de 2026 | **Sim** | 2 dias | Com o enquadramento da Correção 1. As fontes têm de ser recentes e não do arXiv. |
| Tabela comparativa do estado da arte: produtos e trabalhos, o que cada um tem, o que este tem | **Sim** | 2 dias | É a peça que mais valor acrescenta por página. |
| Famílias de IA consideradas, com critério de exclusão declarado | **Sim, reduzido** | 1 dia | Tabela de famílias, não uma secção por família. |
| Diagramas do fluxo de dados de ponta a ponta, do dataset à decisão | **Sim** | dentro da frente 05 | Já está no plano. |
| Ablações pré-registadas sobre 3–4 componentes, com seleção em validação | **Sim, reduzido** | 3 dias | Substitui o varrimento exaustivo. Requer a campanha de re-execução. |
| Varrimento de todas as combinações e ordens | **Não** | — | Pelas Correções 2. Não é falta de tempo: é que o resultado não seria defensável. |
| Estudo de cada família de IA com implementação própria | **Não** | — | É uma tese diferente, e provavelmente boa. Fica como trabalho futuro. |

---

## O que já está feito da visão, e convém saber antes de reescrever

- **Declaração de uso de IA** — feita, e no sítio que o modelo oficial manda (Secção 3.8.4).
  O autor tem razão: não há vergonha nenhuma, e declarar protege.
- **Apêndices** — existem dois. Figuras largas em página rodada e evidências de execução são
  usos legítimos e cabem lá, porque **os anexos não contam para o limite de 120 páginas**.
- **Conclusões com o que ficou e porquê** — o Capítulo 6 já distingue resultado de escolha, que
  é a distinção que a visão pede.
- **Trabalho futuro** — a Secção 6.4 tem seis itens, três acrescentados a 2026-09-01.

---

## Registo

| Data | O quê |
|---|---|
| 2026-09-01 | Criado a partir da descrição do autor. Três correções registadas antes de qualquer execução. |
