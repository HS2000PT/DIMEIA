# O que falta para submeter a 27/09, por ordem de retorno

Data: 2026-09-04. Restam **23 dias** até ao congelamento do documento.
Este plano decorre da [crítica de júri](CRITICA_JURI_2026-09-04.md) e da
[auditoria](AUDITORIA_2026-09-04.md), e obedece à mesma regra que o plano final:
**o que não melhora o documento que vai ser submetido não entra.**

O calendário tem um único item com relógio, e não é nenhum destes: a avaliação de
~17/09, cujo instrumento já está construído e testado. Tudo o que se segue cabe
à volta dela.

---

## Faixa 1 — as correcções de integridade (horas, não dias)

Fazer primeiro, porque são baratas e porque duas delas são das que um arguente
encontra sem esforço.

| # | O quê | Onde | Custo |
|---|---|---|---|
| 1 | O resumo mantém a afirmação absoluta que o Cap. 1 já retirou | `frontmatter`, duas línguas | minutos |
| 2 | O Cap. 6 diz que não houve avaliação com pessoas; o Cap. 5 reporta votos | `ch6`, `ch5/feedback_auto` | um parágrafo |
| 3 | Três subsecções com título em inglês, visíveis no Índice | `ch4` | minutos |
| 4 | As figuras estão em inglês e o documento não diz porquê | `ch3` ou `ch4` | duas frases |

O item 2 é o mais importante dos quatro e o que mais muda a exposição do
documento. Detalhe e citações exactas na crítica.

---

## Faixa 2 — o artigo científico

**Estado real, medido e não presumido: o artigo está desactualizado ao ponto de
afirmar o que a dissertação retirou.**

`paper/main.pdf` tem 4 páginas e foi tocado pela última vez a **13 de agosto**, ou
seja **antes da reescrita para `tese-v2`**, que é a árvore canónica. Comparando os
números um a um:

- **Tem** os valores antigos: `0,514`, `0,542`, `0,496`, `0,595`, `0,632`.
- **Não tem** nenhum dos achados posteriores: a estratégia trivial de `0,467` que
  leva a tese a **abandonar** o valor agregado da recuperação em favor da
  afirmação setor a setor; o `0,513` sob a restrição da produção; o `+0,012` como
  limite superior; o `0,534` da tabela de consulta.

A consequência não é de actualidade, é de integridade: **submetido como está, o
artigo faz a afirmação que a dissertação declara não sustentar.** É a mesma classe
do que a sessão 63 encontrou nos verificadores que apontavam para `tese/`.

Ordem de trabalho recomendada:

1. **Reancorar antes de escrever.** Correr a mesma verificação de números que a
   tese tem (`check_tese_numeros`) contra o `paper/`, para que a divergência deixe
   de depender de quem se lembra dela.
2. **Reescrever o resultado da QI2** na forma que a tese sustenta: a margem por
   setor, com a estratégia trivial nomeada. É a correcção que não é opcional.
3. **Acrescentar o `+0,012` como limite superior**, que é a única contribuição
   nova em texto e a que mais interessa a um revisor.
4. **Só depois** decidir o destino. Quatro páginas em formato IEEE dão para uma
   conferência; a decisão de destino é da Prof.ª Goreti e do orientador, e o prazo
   dela ainda não está no repositório.

**Recomendação de sequência:** fazer isto **depois** de 17/09. O artigo é
derivado da tese; reescrevê-lo antes de a tese estar congelada obriga a fazê-lo
duas vezes. A excepção é o ponto 2, que pode ser feito já porque não depende de
nenhuma medição pendente.

---

## Faixa 3 — o rigor da escrita, e uma ressalva de integridade

A Prof.ª Goreti pediu revisão de escrita. Há duas coisas diferentes debaixo desse
pedido e convém não as misturar.

### O que é legítimo e útil

**Paperpal** e **LanguageTool** corrigem gramática, concordância, pontuação e
registo. Isso é revisão linguística, é prática corrente em trabalho académico, e
não levanta questão nenhuma. O LanguageTool tem suporte de português europeu e
corre localmente ou no navegador; o Paperpal é orientado a texto académico mas o
seu suporte de PT-PT é fraco, pelo que rende mais no **artigo em inglês** do que
na dissertação em português.

O que já foi feito e não precisa de repetição: a passagem de escrita contra as
regras do `BRIEF_REESCRITA` mediu primeira pessoa, ênfase dramática,
coloquialismos, travessões, e a abertura de cada secção e capítulo. O
`check_escrita` corre como porta de entrega e apanha PT-PT e um termo por
conceito.

O que ainda rende, e é o único ponto onde uma ferramenta externa acrescenta:
**uma leitura de concordância e pontuação frase a frase**, que é precisamente o
que um verificador escrito por nós não faz bem e uma ferramenta comercial faz.

### A ressalva, e é importante

**O Evernote não faz o que se pretende.** É um bloco de notas; não reescreve nem
«humaniza» texto.

E se a intenção for passar o texto por uma ferramenta que **disfarce assistência
de inteligência artificial**, isso entra em conflito directo com a declaração de
uso de IA que a própria dissertação assina, e que descreve a extensão real dessa
assistência. Uma tese que declara o uso e depois o esconde no texto fica pior do
que uma que apenas declara. **A recomendação é não o fazer**, e manter a
declaração como está, que é honesta e é defensável.

A distinção prática: **corrigir gramática e estilo é legítimo e declarável;
disfarçar a origem do texto não é.** Paperpal e LanguageTool ficam do lado
legítimo. Sugiro tratar a revisão linguística como o que ela é e registá-la, se
for feita, junto da declaração.

---

## Faixa 4 — a estrutura, e a decisão que ela pede ao autor

A comparação com as quatro dissertações aprovadas dá um quadro que não é opinião:

- Cap. 1: **4 páginas**, contra 8, 8, 8 e 10 das aprovadas.
- Cap. 2: **14 páginas**, contra 18, 20, 24 e 26.

E há espaço: 96 de 120 páginas.

**Esta é uma decisão do autor e não minha**, porque a alternativa também é
defensável. As duas leituras:

- **A favor de crescer:** a primeira impressão do júri forma-se na parte mais
  leve do documento, e cada área do estado da arte tem hoje página e meia. Um
  arguente especialista numa delas encontra a sua área em três parágrafos.
  Crescer é **aditivo**, não toca em números, e não tem risco de regressão.
- **Contra:** o Cap. 2 é curto mas denso, com cinco flutuantes legendados, uma
  tabela de posicionamento e 70 referências todas citadas. Acrescentar por
  contagem de páginas produz enchimento, que é pior do que a brevidade.

**Se for para crescer, o sítio que rende é o Cap. 1**, e por uma razão específica:
é o capítulo mais curto, é o primeiro, e falta-lhe o que as quatro aprovadas têm
todas — uma secção que descreva o **contexto institucional e o âmbito do
trabalho** antes de saltar para as três perguntas. Duas a três páginas, aditivas,
sem tocar em resultado nenhum.

**A minha recomendação:** crescer o Cap. 1 em duas a três páginas e deixar o
Cap. 2 como está. Um estado da arte breve e denso defende-se; uma introdução de
quatro páginas num documento de 130 é a única métrica em que ficamos abaixo de
todas as aprovadas.

---

## Faixa 5 — o painel, e por que razão recomendo não lhe tocar

A pergunta era se faz sentido rever o painel «a pensar já num nível profissional
de qualidade e desempenho».

**Estado medido hoje:** produção viva, `/api/health` a 200 em 0,72 s, instantâneo
fresco a 66 segundos, doze empresas na lista.

O que a tese afirma sobre a interface é deliberadamente pouco: o Cap. 4 diz que
ela serve para ver o que foi enviado e o que não foi, e que **a interface não é
uma contribuição deste trabalho**. As capturas v7 estão sincronizadas entre a
tese, os slides e o guia, e o `check_materiais` passa.

**Recomendação: não mexer antes de 27/09.** Três razões, por ordem de peso:

1. **Não compra nada no documento.** A tese não reivindica a interface, portanto
   melhorá-la não altera uma única afirmação avaliável.
2. **Cria dívida imediata.** Qualquer alteração visual invalida as capturas v7 em
   três artefactos, e a sessão anterior mostrou que trocar só a imagem **muda o
   defeito de sítio**, porque o texto ao lado descreve o ecrã número a número.
3. **Gasta o recurso escasso.** Faltam 23 dias e o único item com relógio é a
   avaliação de 17/09.

Sobre **Vercel**: alojar a página lá seria mais rápido e mais barato do que o
Heroku para a parte estática, mas **o worker teria de ficar onde está**, porque é
ele que faz a recolha para o retreino. Dividir o alojamento a três semanas do
prazo é risco puro. Fica registado como trabalho pós-submissão, e é uma boa ideia
para depois.

Sobre referências de desenho: o critério que rende mais aqui não é estético. Se
houver tempo depois de 27/09, o que falta ao painel é o que a auditoria já
identificou — a camada generativa em `investigator/intelligence/` está completa,
testada e **não exposta**.

---

## Faixa 6 — o que fica de fora, com a razão escrita

Itens da auditoria que **não** entram neste plano, e porquê:

- **Arrumar a raiz do repositório** (4 árvores de tese, 11 planos versionados). O
  repositório fica privado e não é avaliado. Mexer nele a 23 dias troca risco por
  arrumação.
- **Glossário.** Os quinze acrónimos definidos e nunca usados **não são impressos**
  — verificado na Lista de Acrónimos, que mostra apenas os doze utilizados. É
  código morto invisível ao leitor.
- **Dados de contextualização de 2026.** O Cap. 1 já cita Gallup 2025, SIFMA 2025,
  Cahill 2025 e Ernst 2026. A cobertura é adequada.
- **Reestruturar a dissertação.** Decidido e não a reabrir.
- **Reduzir a tese.** Decidido e não a reabrir.

---

## Sequência recomendada

1. **Agora:** Faixa 1 inteira (quatro correcções, horas).
2. **Agora:** ponto 2 da Faixa 2 (o artigo deixa de afirmar o que a tese retirou).
3. **Esta semana:** decisão do autor sobre a Faixa 4, e execução se for sim.
4. **Contínuo:** a recolha corre sozinha; o relatório de projecção diz a cada
   corrida se o mínimo de 80 pares chega a tempo.
5. **~17/09:** correr `scripts/evaluate_ranking_producao.py`. Integrar o que ele
   devolver, seja qual for o sinal.
6. **Depois de 17/09:** revisão linguística com ferramenta externa, e o artigo.
7. **Até 27/09:** as pendências humanas, que nenhuma delas se resolve com trabalho
   no repositório — leitura final, declaração de IA, licença, agradecimentos,
   rotação de credenciais.
8. **Depois da submissão:** painel, Vercel, camada generativa, arrumação do
   repositório.
