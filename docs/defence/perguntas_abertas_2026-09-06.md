# As duas perguntas de júri que ficaram abertas

> Saem da simulação de júri da [auditoria forense de 2026-09-06](../planos/AUDITORIA_FORENSE_2026-09-06.md),
> secção J. Das vinte perguntas prováveis, dezoito têm resposta escrita em parágrafos que a
> dissertação tem precisamente para as antecipar. Estas duas não tinham, e é por isso que existem
> aqui.
>
> ⚠️ **Nenhum dos materiais de defesa em `docs/defence/` menciona os votos do canal**, porque a
> Secção 5.6.5 é posterior a todos eles. A pergunta 1 deste documento não tem resposta preparada
> em lado nenhum, e é a mais perigosa das duas.

---

## 1 · «Quem votou nos 42 votos? O senhor está entre os três?»

### Por que razão esta é a pergunta perigosa

A Secção 5.6.5 reporta que **41 de 42 votos efetivos** classificaram o alerta como útil, ou seja
98%, e diz na frase seguinte que **uma só pessoa forneceu 67% deles**. São três pessoas. Um
arguente que faça a subtração chega imediatamente à pergunta: quem são, e é o autor uma delas?

Se a resposta for «sim, e sou eu o votante dominante», o número deixa de medir utilidade percebida
por terceiros e passa a ser o autor a classificar o seu próprio trabalho — numa dissertação cuja
virtude central é não fabricar. **Ser apanhado nisso vale muito mais caro do que declará-lo.**

### O que a secção já faz bem, e é bastante

Convém abrir a resposta por aqui, porque é verdade e desarma metade da pergunta:

- **As regras foram fixadas antes do primeiro voto** e não foram alteradas depois: mínimo de vinte
  votos efetivos, um voto por pessoa e por alerta, e a salvaguarda do votante dominante acima dos
  40%.
- **A salvaguarda disparou, e está reportada.** A secção não a esconde: diz que uma pessoa
  representa 67%.
- **A proporção sem o votante dominante NÃO é reportada**, porque os 14 votos restantes ficam
  abaixo do mínimo pré-registado. O protocolo recusou-se a publicar o número que teria sido
  conveniente — os 14 são todos «útil», e reportá-los daria 100%.
- **A Secção 6.4 e a matriz de evidência do Apêndice A classificam isto como «Não afirmado»**:
  mede utilidade percebida, não decisão melhor, e não substitui o estudo controlado.

### O que o sistema não consegue responder, por construção

O identificador do votante **nunca é armazenado**. O que fica no registo é um resumo BLAKE2b com
sal secreto (`investigator/telegram_bot/feedback.py::resumir_votante`), e o próprio docstring
explica porquê: o espaço de identificadores do Telegram é pequeno o suficiente para que um resumo
**sem** sal fosse percorrível por força bruta em minutos.

> «O sistema não sabe quem votou, e não pode saber: o que guarda é um resumo criptográfico com
> sal. É a mesma decisão de minimização que a Secção 3.8.1 declara para o resto do sistema.»

Isto responde a «quem são as três pessoas» — não responde, e não deve fingir responder, à pergunta
sobre o autor.

### O que tem de ser apurado ANTES da defesa

**Esta é a única parte deste documento que depende de si.** O sal está no `.env` e nas variáveis de
configuração do Heroku, e o seu identificador do Telegram é seu: com os dois, o resumo é
reconstruível e a pergunta fica respondida em segundos.

```bash
python scripts/quem_votou.py
```

O procedimento pede o identificador por entrada interativa e **não o escreve em ficheiro nenhum**:
imprime apenas se o resumo correspondente aparece no registo e com que peso. Um identificador
colado num script versionado seria exactamente o dado pessoal que o resto do sistema evita.

### As três respostas possíveis, e o que fazer com cada uma

| se o apuramento der | a resposta na defesa | e antes disso |
|---|---|---|
| **não votei** | «Não. Verifiquei-o contra o registo, e nenhum dos três resumos é o meu.» | nada a alterar; vale a pena a frase constar da Secção 5.6.5 |
| **votei, mas não sou o dominante** | «Votei em N alertas, o que é uma parte pequena dos 42. O votante dominante, que representa 67%, não sou eu.» | acrescentar a declaração à Secção 5.6.5 |
| **sou o votante dominante** | «Sim, e é por isso que a proporção sem ele não é reportada: o protocolo recusa-a por ficar abaixo do mínimo. Os 98% incluem-me e não devem ser lidos como retorno de terceiros.» | **declarar isto na Secção 5.6.5 antes da entrega.** Não é aceitável que a primeira vez que se diga seja em resposta a uma pergunta |

⚠️ **Em nenhum dos três casos se retira a secção.** O retorno é observacional, está declarado como
tal em três sítios, e a lacuna que ele não fecha — o estudo controlado — é a primeira limitação do
Capítulo 6 e o primeiro item do trabalho futuro. Uma secção com uma reserva declarada defende-se;
uma secção retirada na véspera não.

---

## 2 · «$0{,}662$ aparece para linhas de base diferentes. É a mesma experiência?»

### O que um arguente atento vê

O valor $0{,}662$ aparece no capítulo dos resultados atribuído a mais do que um objeto. São, de
facto, **três constantes por empresa distintas**, produzidas por três procedimentos:

| procedimento | a constante é | precisão@5 |
|---|---|---|
| `evaluate_triage_identity.py` | a **taxa de positivos** de cada empresa no bloco de treino | $0{,}662$ |
| `evaluate_budget_baselines.py` | a **mediana** da volatilidade de 20 dias de cada empresa, no treino | $0{,}6624$ |
| `evaluate_endtoend_baselines.py` | a **média** da volatilidade de 20 dias de cada empresa, no treino | $0{,}662$ |

### A resposta, e ela reforça a tese em vez de a fragilizar

> «São três constantes por empresa diferentes, e coincidem por uma razão que é o próprio achado do
> capítulo. A precisão dentro do orçamento escolhe, em cada dia, as cinco notícias mais bem
> pontuadas. Com uma pontuação que só depende da empresa, essa escolha depende **apenas da
> ordenação que a constante induz sobre as empresas presentes nesse dia** — não do valor. Três
> maneiras diferentes de resumir uma empresa que a ordenem da mesma forma selecionam as mesmas
> notícias e obtêm, por construção, a mesma precisão.
>
> E que a ordenação por taxa de materialidade coincida com a ordenação por volatilidade é o
> resultado da Secção 5.4.5 dito uma segunda vez: o modelo implantado reconhece a empresa e não a
> notícia. Se ordenar por volatilidade e ordenar por taxa de positivos dá o mesmo, é porque, ao
> nível da empresa, as duas quantidades dizem a mesma coisa.»

### O que não afirmar

⚠️ **Não dizer que são o mesmo número.** Concordam às três casas decimais, e o ficheiro do
orçamento reporta $0{,}6624$ com quatro. Não foi verificado que sejam idênticos, e verificá-lo
exige re-correr sobre a máquina que tem o conjunto congelado. Se o arguente insistir:

> «Concordam às três casas. Não verifiquei que sejam o mesmo número, e uma diferença na quarta casa
> não alteraria a leitura: nenhuma delas se distingue do modelo pelo critério prático de $0{,}02$
> que o capítulo fixou antes das medições.»

### Onde a dissertação já o diz

A Secção 5.6.4 passou a distinguir explicitamente as duas que aparecem em figuras diferentes:

> «Não é a mesma quantidade que a Figura 5.12 designa por *só volatilidade*, que é uma regressão
> sobre a volatilidade diária e obtém $0{,}632$ nesta métrica; aqui a volatilidade entra como uma
> constante por empresa.»

E a Figura 5.18 deixou de rotular a linha «Volatilidade da empresa» para passar a **«Treze
constantes de volatilidade»**, que é o que ela é.

---

## O que mudou na dissertação a 2026-09-06 e convém não dizer à antiga

Correções da auditoria que alteram formulações que os materiais de defesa mais antigos podem
ensinar:

| não dizer | dizer |
|---|---|
| «os terminais custam demasiado» | «os terminais **não estão acessíveis** a este investidor» — o preço não é publicado de forma citável, e é a indisponibilidade que sustenta o argumento (Secção 2.9) |
| «a AMD e a Meta estão sempre acima do limiar» | «a AMD e a **TSLA**; a Meta tem mediana imediatamente acima dele» |
| «oito das doze empresas estão inteiramente de um dos lados» | «**sete** das doze» — a figura passou a desenhar a janela de 36 925 decisões, que é a que o texto reporta |
| «o piso escalonado nunca atuou» | «**não eliminou nada nos seis dias medidos**» — no funil de 15 de agosto eliminou 269 avaliações |
| «a tese tem 132 páginas contra um limite de 120» | «**108** em numeração árabe contra 120; a dissertação aprovada do Bruno Ribeiro tem 139 páginas físicas e termina no fólio 120» |
