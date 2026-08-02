# autoteste.md — perguntas para responderes EM VOZ ALTA antes de ver a resposta

> **Como usar, e isto importa.** Ler uma resposta cria a ilusão de a saber. Dizê-la em voz alta
> antes de a ver é o que a fixa. Por isso: **lê a pergunta, responde alto, só depois abres.**
>
> Se falhares, não passes à frente: volta ao guia de estudo nessa parte e tenta outra vez no dia
> seguinte. Falhar aqui é barato; falhar na sala não é.
>
> **Legenda.** 🔴 saber de cor, sem hesitar · 🟡 saber explicar por palavras tuas · 🟢 saber que
> existe e onde encontrar.

---

## Bloco 1 — O que isto é (5 min, faz sempre primeiro)

**🔴 1. Em três frases, o que é o InvestiGator?**
<details><summary>resposta</summary>

Um sistema de alertas financeiros explicáveis para investidores de retalho. Responde a três
perguntas quando uma ação se mexe: *é invulgar para esta ação?*, *é a empresa ou o mercado?*, e
*já aconteceu antes, e o que se seguiu?*. Nunca prevê preços, e isso é uma restrição de desenho.
</details>

**🔴 2. Qual é a contribuição, se todos os modelos já existiam?**
<details><summary>resposta</summary>

A integração **avaliada**. Nenhum algoritmo é novo. O que é novo é um sistema que responde às três
perguntas a custo zero, com cada afirmação rastreável ao procedimento que a produziu, e com os
resultados negativos reportados tal como caíram. É engenharia de IA: integrar, aplicar e avaliar
criticamente.
</details>

**🟡 3. Porque é que recusar prever é uma força e não uma desculpa?**
<details><summary>resposta</summary>

Porque a hipótese de mercado eficiente diz que a informação pública é absorvida quase de imediato,
logo prever retornos a partir de notícia pública é muito difícil por construção. Em vez de competir
com isso e falhar, o sistema mede e explica o que **já** aconteceu depois de notícias comparáveis.
É mais honesto e mais defensável para um não-especialista.
</details>

---

## Bloco 2 — Os conceitos de IA (15 min)

**🔴 4. O que é um embedding, e porque é preciso?**
<details><summary>resposta</summary>

Um vetor de números que representa o significado de uma frase. É preciso porque um computador não
compara texto por significado, só por caracteres. Com vetores, "escassez de chips" fica perto de
"problemas no fornecimento de semicondutores" mesmo sem uma palavra em comum.
</details>

**🔴 5. Porquê cosseno e não distância euclidiana?**
<details><summary>resposta</summary>

Porque interessa a **direção** do vetor (o tema), não o seu comprimento. E como os embeddings são
normalizados a norma 1, o cosseno é simplesmente o produto interno, e a ordenação por cosseno e por
distância euclidiana passa a ser a mesma. É a escolha barata e correta.
</details>

**🔴 6. Escreve o z-score e explica porque se normaliza.**
<details><summary>resposta</summary>

$z_t = (r_t - \mu_t) / \sigma_t$, anomalia se $|z_t| > k$.

Normaliza-se pela volatilidade **da própria ação** porque a mesma queda de 3% é dramática numa ação
calma e banal numa volátil. Um limiar fixo em percentagem trataria as duas de igual maneira.
</details>

**🟡 7. O que significa "sem lookahead" e como se garante?**
<details><summary>resposta</summary>

Que nenhum número usado para decidir hoje vem do futuro. A janela do z-score usa só dias
**anteriores**; o impacto é medido estritamente **depois** do fecho do dia do evento. Há um teste
que **muta os preços futuros**: as features não podem mudar, o rótulo tem de mudar.
</details>

**🟡 8. O que é precision@k e porquê essa métrica?**
<details><summary>resposta</summary>

A fração dos $k$ primeiros resultados que são relevantes. É a métrica certa porque um alerta só
mostra três ou cinco precedentes: o que interessa é se os do **topo** prestam, não a lista toda.
</details>

**🟢 9. O que é um event study?**
<details><summary>resposta</summary>

Medir o retorno numa janela curta **depois** de um acontecimento. Aqui, +1, +3 e +5 dias a contar
do fecho do dia do evento. Descreve um resultado observado, nunca um efeito causal nem uma previsão.
</details>

---

## Bloco 3 — Os números que tens de saber de cor (20 min, repete até saírem)

**🔴 10. Deteção de anomalias: o argumento mais forte, com número.**
<details><summary>resposta</summary>

Amplitude da taxa de disparo entre os 15 tickers: **0,015** no z-score contra **0,344** no limiar
fixo. É o mais forte porque **não precisa de rótulo**: mostra consistência em ações de volatilidade
muito diferente.
</details>

**🔴 11. Recuperação: o número principal e as suas linhas de base.**
<details><summary>resposta</summary>

P@5 = **0,514** (MiniLM), contra **0,346** lexical, **0,240** aleatório e **0,126** recência. E
**validado à escala: 0,595** em 80 mil manchetes do FNSPID.
</details>

**🔴 12. RQ4: o número que diz que o texto não ajuda.**
<details><summary>resposta</summary>

PR-AUC: **volatilidade 0,542** > contexto 0,538 > **contexto+texto 0,496**. Acrescentar o texto da
manchete **piora**. O sinal vive no contexto de mercado.
</details>

**🔴 13. RQ4: o número que diz que a triagem vale a pena na mesma.**
<details><summary>resposta</summary>

Precisão dentro de um orçamento de 5 alertas/dia: **0,632** contra **0,163** de alertar às cegas.
Quase quadruplica. É o valor de produto, mesmo com o negativo do texto.
</details>

**🟡 14. Estatístico contra aprendido: os dois testes justos.**
<details><summary>resposta</summary>

1. Anomalia: z-score **F1 0,530** contra Isolation Forest **0,271** e LOF **0,280**, com a mesma
   informação causal.
2. Triagem: nenhum modelo com texto bate a volatilidade.

Duas comparações pré-comprometidas, ganhas pela opção transparente.
</details>

**🟡 15. O achado honesto que vai CONTRA a escolha feita.**
<details><summary>resposta</summary>

A volatilidade EWMA bate a deslizante: **F1 0,664 contra 0,516**, com o mesmo recall e quase metade
dos falsos positivos. Reportei-o. Mantenho a deslizante por ser explicável numa frase, e a EWMA
fica como futuro **já validado**.
</details>

---

## Bloco 4 — Os quatro estudos que terminam em "não" (20 min, os mais prováveis)

**🔴 16. Taxonomia de eventos: o número, e porque NÃO a ligaste.**
<details><summary>resposta</summary>

AMI **0,358** com tipo de evento contra **0,188** com ticker: o espaço sabe o acontecimento, e
sabe-o mais do que sabe a empresa. Mas a silhueta é **0,084**, os grupos sobrepõem-se, e a rubrica
só cobre **15,1%** do corpus. Filtrar por um tipo errado **remove evidência válida em silêncio**.
</details>

**🔴 17. Porque é que a pureza de 0,712 sozinha engana?**
<details><summary>resposta</summary>

Porque com um tipo a valer 44% dos rótulos e 18 grupos, uma atribuição **aleatória com os mesmos
tamanhos** já dá **0,444**. O ganho real é **+0,269**, não 0,712.
</details>

**🔴 18. Predição conformal: o que acrescenta a uma probabilidade calibrada?**
<details><summary>resposta</summary>

Uma garantia **livre de distribuição** e de amostra finita: escolhido um α, o conjunto contém a
classe verdadeira em pelo menos 1−α dos casos. A calibração é uma afirmação agregada sobre o
passado; isto é uma garantia. E num problema binário o conjunto pode dizer **"não sei"**.
</details>

**🔴 19. O número mais duro da tese.**
<details><summary>resposta</summary>

Para garantir **90% de cobertura**, o modelo só consegue uma decisão definida em **39,5%** das
manchetes. Não contradiz a RQ4: **explica-a** por um caminho independente, sem treinar nada.
</details>

**🟡 20. A cobertura conformal parte-se onde, e porquê?**
<details><summary>resposta</summary>

Aguenta a 90% e 80%; parte-se a **95%** sob divisão temporal (**0,937** contra 0,95). Pedir 95%
obriga o limiar a apoiar-se na **cauda** da calibração, e é a cauda que se move primeiro quando o
regime muda.
</details>

**🔴 21. Deriva: o que está medido e o que isso muda.**
<details><summary>resposta</summary>

Volatilidade pré-evento **PSI 0,281** (banda significativa); features de retorno 0,020 e 0,014
(estáveis). A limitação que a tese repetia passou de **afirmada a medida**, e dá um gatilho de
re-treino verificável em vez de uma intuição.
</details>

**🟡 22. Porque é que os números congelados sobrevivem à deriva?**
<details><summary>resposta</summary>

Porque a prevalência do rótulo **oscila** em vez de ter tendência: 0,385 → **0,470** → 0,378. O
protocolo já atravessa uma dessas oscilações, logo os números são medidos **sob** deriva.
</details>

**🔴 23. Convergência: o resultado, e o achado que vale mais.**
<details><summary>resposta</summary>

A fusão ganha em **1 de 3** orçamentos. Um ganho que depende do orçamento que se cita é um ganho
que se **pode ter escolhido** ⇒ não entra em produção.

O achado: o peso da intensidade de notícia saiu **negativo (−0,283)**. Mais manchetes = menos
provável ser material, porque são dias de conteúdo automático. À mão eu teria posto positivo e
estaria errado.
</details>

---

## Bloco 5 — Método e integridade (10 min)

**🔴 24. Como sabes que as tuas citações não são inventadas?**
<details><summary>resposta</summary>

**59 de 59** verificadas. 43 DOIs resolvem no Crossref **e o título devolvido bate com o da
bibliografia**, 8 arXiv, 6 URLs, 1 ISBN conferido na página de rosto, 1 sem identificador **e está
correto assim**. A comparação de títulos apanha o DOI que resolve para **outro** artigo.

E há uma **rejeição** documentada: o MacKinlay 1997 saiu porque o DOI não resolve.
</details>

**🟡 25. E que as citações sustentam o que dizes?**
<details><summary>resposta</summary>

Auditoria separada: li as **122 instâncias** contra o que a obra estabelece. Encontrei duas
afirmações esticadas e corrigi-as **enfraquecendo a afirmação**, nunca inventando fonte: um survey
de 2014 a que atribuía modelos de 2019, e um critério atribuído a autores que não o elegem.
</details>

**🟡 26. Como é que a explicação não pode divergir do cálculo?**
<details><summary>resposta</summary>

Porque o texto é **composto a partir dos mesmos objetos** que o sistema calcula. Não há um segundo
caminho que possa desalinhar. Um teste verifica que cada precedente mostrado aparece com a data,
ticker e similaridade exatos, e que não aparece nenhum que não foi recuperado.
</details>

**🟢 27. Tens base de dados?**
<details><summary>resposta</summary>

Três camadas: SQLite para as subscrições do bot, JSONL versionado para o histórico partilhado, e os
modelos com metadados. Não há **servidor** de base de dados porque o acesso é
acrescentar-e-ler-tudo sobre 24 MB, e versionar dá rasto de auditoria e leitura pública. A
limitação é a escrita concorrente, tratada com controlo otimista.
</details>

---

## Bloco 6 — As perguntas que doem (15 min, ensaia em voz alta)

**🔴 28. "O vosso modelo perdeu. É um fracasso?"**
<details><summary>resposta</summary>

Não, é o resultado. A comparação foi **pré-comprometida**: decidi antes de correr que a
volatilidade era a linha de base a bater. Não bateu, e reporto-o. Como mecanismo de produto a
triagem quadruplica a precisão dentro do orçamento. E um trabalho que só reporta o que correu bem é
um trabalho em que não se pode confiar.
</details>

**🔴 29. "Construiu quatro coisas e não usou nenhuma."**
<details><summary>resposta</summary>

É a parte de que tenho mais orgulho. Construir é fácil; o difícil é ter um critério que consiga
dizer não. E quando a medição **sustentou**, liguei: o detetor de volume saiu do mesmo estudo e
está em produção. O critério foi registado **antes**, não depois de ver o resultado.
</details>

**🟡 30. "Isto é só integrar ferramentas existentes."**
<details><summary>resposta</summary>

Sim, e é isso que engenharia de IA é. A contribuição é a integração **avaliada**: linhas de base
pré-comprometidas, ablações, resultados negativos publicados, e cada número regenerável por um
procedimento versionado. Inventar um algoritmo novo não era o objetivo nem seria defensável em
quatro meses.
</details>

**🟡 31. "A relevância é medida por setor. Não é batota?"**
<details><summary>resposta</summary>

É um indicador aproximado, e digo-o. Um precedente do mesmo setor sobre outro assunto conta como
acerto, o que **inflaciona** todas as linhas comparadas por igual, incluindo as baselines. E o
argumento principal da anomalia é **sem rótulo** precisamente para não depender de proxies.
</details>

---

## Como distribuir isto pelos dias

| Sessão | O que fazes | Tempo |
|---|---|---|
| Dia 1 | Blocos 1 e 2. Não avances sem os 🔴 a sair sem hesitar. | 30 min |
| Dia 2 | Bloco 3 (números). Escreve-os à mão, não só leias. | 30 min |
| Dia 3 | Bloco 4 (os quatro "não"). São os mais prováveis. | 30 min |
| Dia 4 | Blocos 5 e 6. Em voz alta, de pé. | 30 min |
| Dia 5 | **Tudo outra vez, sem abrir as respostas.** Marca os que falhaste. | 45 min |
| Dia 6 | Só os que falhaste $+$ as cadeias do `simulacro_defesa.md`. | 45 min |
| Dia 7 | Descansa. A consolidação acontece longe do material. | — |

Repete o ciclo. À terceira volta os 🔴 saem sozinhos, e é aí que a confiança aparece: não por
acreditares que sabes, mas por te teres testado e teres acertado.
