# Auditoria final — relatório estruturado

Iniciada a 2026-09-04, em resposta à directiva de 40 secções.
**Estado: em curso.** Este documento cresce à medida que cada secção da directiva é
tratada, e diz sempre o que está fechado e o que não está.

---

## A. Pendências anteriores concluídas

Antes de abrir a auditoria nova, fechei o que estava a meio.

| O quê | Estado |
|---|---|
| Apêndice A.5 — infraestrutura com logótipos por etapa, e o custo real | fechado |
| Crítica de júri à tese canónica | fechado, em [`CRITICA_JURI_2026-09-04.md`](CRITICA_JURI_2026-09-04.md) |
| Plano de submissão até 27/09 | fechado, em [`PLANO_SUBMISSAO_2026-09-04.md`](PLANO_SUBMISSAO_2026-09-04.md) |
| Faixa 1 do plano — quatro correcções de integridade | fechado |

Detalhe da Faixa 1 na secção C.

---

## B. Problemas encontrados

### B1. O resumo mantinha a afirmação que o Cap. 1 já tinha retirado — ALTA

O resumo, nas duas línguas, dizia que as aplicações gratuitas «não respondem a estas
questões». O Cap. 1 já dizia, três páginas adiante, que «existem produtos recentes que
declaram ir além disso». A correcção de uma sessão anterior tinha sido aplicada ao
capítulo e não ao resumo, que é a primeira coisa que o júri lê.

### B2. O Cap. 5 media utilidade com pessoas e o Cap. 6 dizia que isso não foi feito — ALTA

A Secção 5.6.5 reporta votos reais do canal. A Secção 6.4 abre a lista de limitações com
«não foi realizada qualquer avaliação com utilizadores». **As duas secções não se referiam
uma à outra**, em nenhum sentido. A reconciliação estava escrita, mas toda dentro da 5.6.5.

### B3. Três subsecções com título em inglês num documento em português — MÉDIA

`Prices`, `News`, `Web application`, visíveis no Índice. Restos da árvore anterior.

### B4. As 40 figuras em inglês sem explicação no documento — MÉDIA

O Cap. 4 explicava por que razão as mensagens do produto são em inglês; sobre as figuras,
nada. Um leitor que não encontre a razão assume descuido.

### B5. A Figura 4.3 publicava um teto como se fosse uma medição — ALTA

Levantada pelo autor. Tratada na secção E, porque é uma anomalia de dados e não de texto.

### B6. O `check_references` era cego a `\input{}` — MÉDIA (defeito de instrumento)

Um `\label` definido num fragmento gerado era invisível ao extractor, e uma referência
legítima para ele aparecia como defeito da tese. O verificador acusaria o documento de um
problema que era dele.

### B7. O artigo científico afirmava o que a dissertação retirou — ALTA, **corrigido**

Quatro divergências, todas verificadas contra os ficheiros:

1. afirmava que a recuperação «clearly outperforms every baseline», com o agregado que a
   tese abandona por causa da estratégia trivial de `0,467`;
2. descrevia a **camada generativa como entregue**, quando as rotas que a expunham foram
   retiradas da API e a tese justifica explicitamente a ausência de um modelo de
   linguagem na composição das mensagens;
3. citava `0,271` para o *Isolation Forest* e a tese cita `0,269` — os dois certos, em
   artefactos diferentes;
4. o `graphicspath` apontava para `thesis/`, árvore superseda.

Correção na secção C. A camada generativa foi **estreitada e não removida**: o código
existe e as medições são reais, pelo que removê-la apagaria trabalho medido, e
descrevê-la como entregue seria descrever um produto que não existe.

### B8. A introdução e o estado da arte são os mais curtos das cinco dissertações — INFORMATIVO

Cap. 1 com 4 páginas contra 8, 8, 8 e 10 das quatro aprovadas; Cap. 2 com 14 contra 18,
20, 24 e 26. Decisão do autor, com as duas leituras escritas no plano de submissão.

---

## C. Correções realizadas

| # | Correcção | Onde |
|---|---|---|
| C1 | O resumo passa a «as poucas que vão além disso não expõem a evidência que as sustenta», nas duas línguas. 198 de 200 palavras | `frontmatter` |
| C2 | Parágrafo novo no Cap. 6 a dizer por que razão os votos não constituem exceção à lacuna, e remissão no sentido inverso | `ch6`, gerador |
| C3 | `Prices`, `News`, `Web application` → `Cotações`, `Notícias`, `Aplicação web` | `ch4` |
| C4 | Nota no fim do Cap. 1 sobre a língua das figuras, ancorada na razão que o Cap. 4 já dá | `ch1` |
| C5 | Figura 4.3 refeita sobre uma janela única, com gerador novo e quatro testes | `ch4`, `scripts/` |
| C6 | `check_references` passa a seguir `\input{}` e `\include{}` | `scripts/` |
| C7 | Artigo alinhado com a dissertação nos quatro pontos de B7 | `paper/` |
| C8 | Porta nova `check_artigo_numeros.py`, no `check_entrega` | `scripts/` |

**Nota de método sobre C2, que vale para o futuro:** o `ch5/feedback_auto.tex` é
**gerado**. A remissão foi escrita no `analyse_feedback.py` e não no `.tex` — uma frase
escrita à mão no destino desapareceria na corrida seguinte sem um único aviso. É a mesma
classe de defeito que este projecto já pagou duas vezes com artefactos regeneráveis.

Duas correcções foram apanhadas pelas próprias portas do projecto, e não por mim:
o `check_floats` acusou a figura nova do apêndice por não ser invocada por frase nenhuma,
e o `check_escrita` acusou quatro «tecto», que é pré-Acordo, no meu texto novo.

---

## D. Dados e resultados atualizados

| Antes | Depois | Razão |
|---|---|---|
| Funil de seletividade: 944 → 42, janela 4–13 de julho | 743 → 15, janela 1–3 de setembro | Quatro defeitos no instantâneo anterior, secção E |

**Nenhum outro número foi substituído.** Os 55 números que a porta confere continuam a
bater com a fonte que os produz.

---

## E. Anomalias encontradas nos dados

### E1. Figura 4.3 — três empresas com exatamente 14 alertas e sete a zero

**Sintoma.** Levantado pelo autor: `AMD 14`, `META 14`, `TSLA 14`, todas as restantes a
zero, com `42 = 3 × 14`. A distribuição não tinha a forma de uma medição.

**Investigação.** Percorrido o percurso completo, contra os ficheiros de dados reais da
branch `alerts-history`, e não contra o que o gerador afirmava.

**Causa — e são quatro, não uma.**

1. **`14` é o teto e não uma medição.** A política de julho impunha duas mensagens por
   empresa por dia. Contados os primeiros 42 alertas de notícia do canal: estão datados de
   13 a 20 de julho, a **seis por dia**, que é exatamente três empresas × duas. As três
   empresas estavam saturadas **todos os dias**. A legenda atribuía essa forma ao limiar
   de semelhança e à composição da base de casos, ou seja explicava por um mecanismo
   aquilo que um limite produzia.
2. **A razão 22:1 comparava populações diferentes.** O numerador vinha de
   `live_pending.jsonl`, que é uma **janela deslizante** — um caso sai quando matura, ao
   fim de oito dias. O denominador vinha de `alerts_history.jsonl`, que é **cumulativo**.
   Verificado hoje: o ficheiro de pendentes cobre apenas 23 de agosto a 4 de setembro.
3. **A janela anunciada não era a janela contada.** O rótulo saía da união das datas das
   duas fontes e dizia 4 a 13 de julho; os alertas contados estão datados de 13 a 20.
4. **A política descrita foi substituída a 2026-08-15**, quando o teto por empresa deu
   lugar ao orçamento global de cinco por dia. O resto do Capítulo 4 já descreve a
   política nova, pelo que a figura contradizia o próprio capítulo.

**Correção.** Primeiro a causa, depois a figura, como o pedido manda.
`scripts/evaluate_funil_seletividade.py` impõe três coisas que o instrumento anterior não
tinha:

- a **janela é um argumento** e aplica-se aos dois lados do funil;
- a unidade é o **título distinto**, deduplicado por `(data, empresa, título)`, porque o
  sistema reavalia os mesmos títulos a cada ciclo de 60 s — no registo da janela nova são
  1 321 linhas para 743 títulos;
- e o relatório **diz quando um número é um teto**, verificando a saturação do orçamento
  diário e a igualdade suspeita entre empresas. Foi a ausência desta terceira verificação
  que deixou passar o 14.

**Resultado.** Janela de 1 a 3 de setembro: **743 títulos distintos de doze empresas → 15
alertas a oito delas**, razão de 50:1. E o relatório declara sozinho que 15 é o teto,
porque o orçamento de cinco foi integralmente utilizado nos três dias.

**Ressalva que fica escrita, porque é a regra §37 da directiva.** A janela nova não foi
escolhida por dar um número melhor. Qualquer um dos quatro defeitos acima obrigava a
refazer a figura. Que o resultado seja mais favorável ao sistema é consequência, e o texto
da tese di-lo: o total de quinze é o teto que a política impõe, e o que a figura mede é a
repartição desse teto.

**Guarda permanente.** Quatro testes. O central planta a forma exacta de julho — três
empresas com o mesmo valor e as restantes a zero — e exige que o relatório a assinale.
**Verificado a falhar** com o guarda desligado. Mais o controlo no sentido oposto: uma
distribuição desigual não dispara o aviso.

### E2. A mesma classe noutras figuras e tabelas — nenhuma

Varridas todas as figuras com coordenadas embutidas e todas as tabelas, à procura de
valores idênticos repetidos entre categorias, zeros que possam ser dados em falta, e
múltiplos exactos de um limite conhecido. **Um único resultado, e é a figura nova**: quatro
empresas a zero alertas e três com dois, o que é uma distribuição legítima e bem abaixo do
limite por empresa. As repetições nas tabelas são anos, o tamanho da lista vigiada e
números de secção.

Verificada também a §23 da directiva, percentagens sem tamanho de amostra: os `n` estão
declarados onde importa, incluindo a sub-população («dos 120 alertas que afirmam
unanimidade»).

---

## E3. A estrutura pré-textual e os acrónimos

**As listas no Índice.** Só a Lista de Acrónimos constava; as de Figuras, Tabelas e
Símbolos não. Decidido contra as dissertações aprovadas e não por gosto: o Índice do Bruno
Ribeiro lista todas com página. As três entram, e as páginas conferem.

**A Lista de Excertos era defendida por um comentário e não existia.** O frontmatter
argumentava por que valia a pena mantê-la, e a reescrita deixou o documento com zero
excertos de código. A garantia anti-lookahead, que era o excerto que valia a pena mostrar,
passou a ser a figura da janela deslizante. Nada se perdeu; o que ficou era código morto.

**Acrónimos.** Dos 27 declarados, quinze nunca são usados — e a lista imprime apenas os
usados, pelo que são invisíveis ao leitor. Três decisões diferentes para os que apareciam
por expandir: `HTTP` passa a `\gls`; `ONNX` entra na prosa do apêndice porque só aparecia
dentro de uma figura; e `AI` e `SIFMA` **ficam**, o primeiro por estar dentro de um título
de notícia citado e o segundo por ser parte do nome de uma publicação. A lista passa de 12
para 14, com espaçamento uniforme.

**A pergunta sobre o FinBERT, respondida:** não está na lista porque **não é um acrónimo**.
A tese nomeia-o pelo ponto de controlo público `ProsusAI/finbert`, que é o artefacto exacto
sobre o qual a medição incide, e reporta o resultado (`0,420`, o mais baixo de todos) com o
enquadramento certo. O mesmo critério vale para MiniLM, MPNet, Platt, Vasicek e Telegram.

---

## E4. Cor e uniformidade visual (§7)

**Medido em vez de suposto.** A tese canónica usa **sete cores não-cinzentas em todo o
documento**, todas `orange!60!black` e todas com o mesmo papel: marcar o critério prático
ou o limiar. **Não há verde nenhum no corpo.** O verde que o autor viu está nos slides e no
guia, que são materiais de marca, e nas capturas da aplicação.

Registado e não corrigido: seis capturas superseda (v3, v5, v6) e três logótipos estão em
`tese-v2/figures/` sem serem usados. Não entram no PDF, mas são uma armadilha para quem
reutilize a errada.

---

## E5. A cadeia das questões de investigação (§17)

A matriz de evidência **já existia** no apêndice, com 24 linhas e estados *retirada*,
*estreitada* e *nova*, e a Secção 4.7.1 já separa o que foi desenvolvido do que é consumido
do exterior. Nenhuma das duas foi duplicada.

O que faltava era a cadeia, e foi feita como **verificação e não como tabela**: uma tabela
escrita por mim afirmaria a cadeia; o verificador testa-a. E encontrou um defeito: **o
Cap. 6, ao responder à QI2, cita o chão de acaso sob a restrição da produção () e
nenhum capítulo anterior o enuncia.** O Cap. 5 dava a margem e o valor do método, pelo que
o  só se obtinha por subtracção a partir de uma legenda. Confirmado contra o
artefacto e enunciado no Cap. 5, que é onde o resultado vive.

 impõe: cada questão tem resultados e resposta; o Cap. 6 não cita
decimais que os capítulos anteriores não estabeleçam; e cada questão delimita o que o
resultado não permite concluir. Verificado com uma afirmação inventada plantada.

---

## E6. Auditoria visual (§38)

Feita por medição sobre as 130 páginas, e não por leitura de todas — o que permite dirigir
a inspecção visual às candidatas em vez de a diluir.

| O que se mediu | Resultado |
|---|---|
| Caixas rebentadas | 5, **todas abaixo de 5,7 pt** |
| Páginas de conteúdo com 8 linhas ou menos | **2**, e ambas legítimas: a dedicatória e o fim da Lista de Figuras |
| Versos em branco | 14, normal em impressão frente e verso |
| Flutuantes a mais de 2 páginas da invocação mais próxima | **1**, a 3 páginas |
| Flutuantes sem invocação | **0** |

Inspeccionadas visualmente as páginas das duas figuras refeitas, a da lista de acrónimos, a
do apêndice novo, e duas páginas densas do Cap. 6. Nenhuma com defeito de composição.

**⚠️ Três falsos positivos do meu próprio varrimento, resolvidos antes de reportar:** uma
figura invocada numa frase que **termina em dois pontos** foi lida como legenda; uma
**remissão para a frente** do capítulo dos métodos para os resultados foi contada como má
colocação, quando é legítima; e três figuras apareceram como não invocadas porque a
referência estava **quebrada entre linhas** no PDF — todas têm referência na fonte.

---

## F. Afirmações reformuladas ou removidas

| Afirmação | Estado |
|---|---|
| «As aplicações gratuitas não respondem a estas questões» (resumo, 2 línguas) | estreitada |
| «A concentração dos alertas em três empresas decorre da interação entre o limiar de semelhança e a composição da base de casos» | **retirada**: a igualdade era o teto da política |
| «Das 944 notícias relevantes resultaram 42 alertas, razão de um para vinte e dois» | **retirada**: populações e janelas diferentes |
| «Não foi realizada qualquer avaliação com utilizadores» | mantida, com a razão explicitada e ligada aos votos do canal |

---

## G. Nova evidência adicionada

- `docs/evaluation/evaluation_funil_seletividade.md` — instantâneo datado, com a secção
  «é medição ou é teto?».
- Apêndice A.5 — as peças externas por etapa, com logótipos, e a tabela de custo com a
  razão do escalão escolhido.

---

## H. Figuras PT/EN

Ainda não tratado. Ver secção K.

---

## I. Estado das questões de investigação

Verificado por leitura do Cap. 6: as três estão respondidas, com o alcance delimitado em
cada uma, e a resposta negativa da QI3 aparece na figura de síntese com o mesmo destaque
das outras duas. Nenhuma fica implicitamente sem resposta.

---

## J. Limitações ainda existentes

As onze da tabela do Cap. 6 mantêm-se, e nenhuma foi encerrada por esta auditoria.

---

## K. Pendente

Por ordem do plano de submissão:

1. ~~O artigo científico~~ — **fechado**, ver B7 e C7. Fica por decidir o destino de
   publicação, que depende do prazo que a Prof.ª Goreti indicar.
2. **Política linguística e figuras PT/EN** (§5, §6, §7 da directiva).
3. **Agradecimentos** (§2) — voz do autor; o repositório tem um rascunho por reescrever.
4. **Estrutura pré-textual e listas** (§3).
5. **Glossário e símbolos** (§4).
6. **Painel e screenshots** (§11, §12) — o plano recomenda depois de 27/09, com a razão.
7. **Auditoria factual frase a frase e matriz de evidência** (§15, §16).
8. **Auditoria visual página a página** (§38).

---

## L. Recomendações adicionais

### L1. Três pontos da directiva não se aplicam a este sistema, e convém dizê-lo

A §19 pede para uniformizar a terminologia entre «Investigator», «FinXAI-Agents»,
«multi-agent system», «agente» e «arquitetura multiagente». **Este sistema não tem
agentes**, e a dissertação não os reivindica em lado nenhum. O nome «FinXAI-Agents» não
existe no repositório. Introduzir essa terminologia seria descrever um sistema que não
existe, o que a §37 proíbe.

Pela mesma razão, a §31 pede para tratar «limitações do FinBERT» e «possíveis
hallucinations». O FinBERT aparece **apenas como alternativa medida numa comparação** e não
é usado pelo sistema; e o sistema não tem camada generativa exposta, pelo que não há
alucinações a discutir no produto entregue.

### L2. A ressalva sobre «humanizar o texto»

O Evernote é um bloco de notas e não reescreve texto. Se a intenção for passar o texto por
uma ferramenta que **disfarce assistência de inteligência artificial**, isso entra em
conflito directo com a declaração de uso de IA que a dissertação assina. Paperpal e
LanguageTool são outra coisa — corrigem gramática e estilo, o que é legítimo e declarável
— e ficam recomendados, com o LanguageTool a render mais em PT-PT e o Paperpal no artigo
em inglês.
