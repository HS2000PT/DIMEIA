# Mensagem ao orientador e ao coorientador (PT-PT, pronta a copiar)

> **Reescrita a 2026-09-11.** A versão anterior era de 7 de agosto, dirigida só ao orientador, e
> apresentava o trabalho pela primeira vez. Esta é diferente: envia o **documento completo e o
> sistema a funcionar**, e pede uma coisa concreta — leitura crítica do documento.
>
> ⚠️ **E a versão anterior tinha uma afirmação que a tese retirou.** Dizia que um terminal
> profissional responde às três perguntas «por cerca de 2.000 dólares por mês». A §2.9 declara que
> esse preço **não é publicado de forma citável**, e é a indisponibilidade — não um valor — que
> sustenta o argumento. Escapou às duas portas: o `check_materiais` compara decimais e `2.000` é
> um separador de milhares, e o `check_numeros_retirados` procura os números da sua lista. Uma
> afirmação de preço numa mensagem ao orientador é exactamente onde ela custa caro: se ele
> perguntar de onde vem, não há fonte.
>
> **Anexar:** `tese-eng/main.pdf` (ou a PT, conforme o que se decidir entregar) e
> `tese-pt/slides/main.pdf`.
>
> **Destinatários:** Prof. Luís Gomes (orientador) e Rafael Silva (coorientador).

---

**Assunto:** Dissertação MEIA (nº 1180934) — documento completo e sistema no ar

Bom dia a ambos,

Envio em anexo a dissertação para vossa apreciação, e os slides da defesa.

Só apresento agora porque quis chegar-vos com uma versão fechada e com o sistema a funcionar ao
vivo. Até há pouco tempo o documento ainda mudava com as medições, e preferi não vos pedir tempo
para rever algo que ia mudar por baixo. Daqui para a frente as alterações serão menores e sobretudo
de escrita.

**O que é.** Um sistema de alertas financeiros para quem investe sem ser profissional. Quando uma
ação se mexe, responde a três perguntas — *isto é invulgar para esta ação?*, *foi a empresa ou foi o
mercado?*, e *já aconteceu antes, e o que se seguiu?* — sempre com a evidência ao lado, e **nunca
prevê preços**. Essa recusa é uma restrição de desenho e atravessa o trabalho todo.

**As técnicas, e para que serve cada uma.**

- **z-score sobre janela deslizante** — decide se o movimento do dia é invulgar *para aquela
  empresa*. Sem parâmetros aprendidos.
- **Regressão de dois fatores com encolhimento** — reparte o movimento entre mercado, setor e
  empresa. Coeficientes estimados dos preços, sem rótulos.
- **Embeddings de frase (SBERT) e semelhança do cosseno** — recupera notícias passadas parecidas e
  mostra o que o preço fez a seguir. Modelo pré-treinado, usado sem ajuste.
- **Modelo calibrado sobre exemplos rotulados** — ordena as notícias por materialidade, para decidir
  o que vale interromper alguém. É a única componente treinada neste trabalho, e o **resultado é
  negativo**: não bate uma linha de base de uma só variável. Está reportado como tal.
- **Ajuste contrastivo do codificador** — tentativa de tornar a materialidade comparável entre
  notícias. Também **negativo**, e também reportado.

Dois dos quatro resultados são negativos, e é essa a parte que considero mais sólida do trabalho:
as alternativas simples foram escolhidas e declaradas antes de medir, o que é a condição para o
resultado poder correr mal.

**O que os leitores dizem, e o que isso não é.** Cada alerta leva dois botões. Estão registados
91 votos sobre 62 alertas, e 86 deles classificam o alerta como útil — 95%, ou 89% se retirar o
leitor que deu 58% dos votos. As regras de análise ficaram fixadas antes do primeiro voto. Mas
são **três pessoas**, ninguém recebeu o movimento sem explicação, e utilidade percebida não é
decisão melhor: é um piloto observacional, e o estudo controlado está desenhado e não foi
corrido. Digo-o assim no documento, e é a primeira limitação das conclusões.

**Para verem a funcionar:**
aplicação — <https://investigator-ddc9d8618935.herokuapp.com> ·
canal — <https://t.me/InvestiGatorMEIA>

**O que vos peço, e é sobretudo isto:** leitura crítica do **documento**. Em concreto, se a
estrutura faz sentido, se a escrita está ao nível, **se está demasiado extensa**, e o que
acham que se deve cortar, acrescentar ou rever. É aí que o vosso tempo me vale mais.

Duas perguntas práticas:

1. Posso responder ao inquérito da Professora Goreti para ir a defesa?
2. Concordam com o título? Neste momento é *«Explicar sem prever: deteção de anomalias e
   recuperação de precedentes em alertas financeiros verificáveis»*.
3. Sobre o **artigo publicável** que a unidade curricular pede: tenho uma versão escrita em
   formato de conferência IEEE, destilada da dissertação e com todos os números conferidos
   contra ela. Queria confirmar três coisas — se esse formato é o que é aceite, se deve ser
   submetido a algum sítio concreto ou se basta entregá-lo, e, caso deva ser submetido, se têm
   sugestão de destino. Pelo que o trabalho é, parece-me caber melhor numa conferência de
   sistemas inteligentes ou de IA aplicada a finanças do que numa revista, mas prefiro seguir o
   que recomendarem.

Obrigado pela disponibilidade,
Henrique Santos
