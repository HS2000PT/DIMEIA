# Plano até à entrega

> Escrito a 2026-08-20, a pedido do aluno: *"forja um plano para revermos isto"*.
> Cada fase diz **o que se faz**, **como se sabe que ficou feito**, e **o que pode correr mal**.
> As fases estão por ordem de risco: primeiro o que pode invalidar afirmações, depois o produto,
> depois a escrita, depois os materiais.

---

## Onde estamos, medido hoje

| | Estado |
|---|---|
| `python scripts/check_entrega.py` | **sai a zero** |
| Tese curta | 114 pp · 0 erros · 0 referências indefinidas · overfull máx 5 pt |
| Slides · guia · quizz | 20 · 22 · quizz 37, verificados por porta |
| Suite | 737 testes, 0 falhas |
| Ligações da bibliografia | **0 partidas** (ver F1) |
| Achados de citação por consumir | **122** (ver F1) |

---

## F1 — Citações: fechar o que ficou por consumir

**O problema, e é real.** Dois workflows correram a **17** e a **19 de agosto** e produziram
**134 achados** sobre se cada citação sustenta a frase a que está agarrada. Os resultados ficaram
no `journal.jsonl` e **nunca foram lidos**. Encontrei-os hoje ao procurar trabalho pendente.

**O que já está confirmado:** os **5 críticos** estão todos corrigidos, e verifiquei um a um:

| # | Achado | Estado |
|---|---|---|
| 92, 110 | O `\textbf` partido por um TAB, impresso no PDF | corrigido hoje |
| 57 | A tabela da ablação divergia da fonte em 5 de 7 linhas | corrigido hoje, bate 7/7 |
| 52 | O Niculescu-Mizil diz que a regressão logística **já** está bem calibrada | Cap. 2 diz isso, com as palavras da fonte |
| 70 | O viés da calibração (val 0.470, teste 0.378) | declarado no Cap. 3, com os números |

**O que falta:** **122 achados** por conferir — 5 altos, 28 importantes, 19 médios, 55 menores,
15 sugestões. Muitos estarão corrigidos pelas rondas de 19 e 20 de agosto; outros não.
Estão extraídos em texto integral, com a evidência de cada um.

**Como se faz:** um a um, contra a tese de hoje. Para cada achado: abrir a frase, ver se ainda
diz o que o achado diz, e — quando disser — abrir a fonte e confrontar. **Não aceitar o achado
sem o verificar:** já aconteceu nesta revisão um revisor "apanhar" números errados por ter lido
o corpo de um artigo e não o resumo, e a correcção teria estragado texto correcto.

**Ordem:** os 5 altos e os 28 importantes primeiro; os 55 menores por último, e alguns serão
preferência e não erro.

**Como se sabe que ficou feito:** cada achado fica marcado como *corrigido*, *já estava certo*,
ou *rejeitado com razão*, num documento com a evidência. Zero por decidir.

### F1b — As ligações, verificadas ao vivo

Já feito e versionado em `scripts/check_links_vivos.py`. **Resposta à tua pergunta:** sim, cada
DOI e cada URL foi seguido até ao destino final, hoje, com redireccionamentos.

- **37 respondem 200** e aterram na página certa
- **28 respondem 202 ou 403** — o desafio anti-robô do IEEE, da ACM, da Wiley e da Oxford. **O
  DOI já redireccionou para a página certa**; o que falha é o robô entrar, não a ligação existir.
  Confirmei o destino de cada uma à mão
- **0 partidas**

Isto é diferente do `verify_dois.py`, que pergunta ao Crossref se o registo existe e compara os
metadados campo a campo. Os dois juntos cobrem as duas perguntas: *o identificador está certo?* e
*a ligação abre?*

### F1c — Os PDF que faltam

**Três, e são os únicos.** Todos gratuitos:

| Chave | Onde | Porquê |
|---|---|---|
| `mikolov2013word2vec` | `proceedings.neurips.cc/paper_files/paper/2013/file/9aa42b31882ec039965f3c4923ce901b-Paper.pdf` | A entrada deixou de ser a pré-publicação e passou a ser as actas |
| `liu2020finbert` | `ijcai.org/proceedings/2020/622` | Entrada nova, revista por pares |
| `huang2023finbert` | Wiley, *Contemporary Accounting Research* 40(2) — pode exigir a conta do ISEP | Entrada nova, revista por pares |

E **um por substituir**: o ficheiro guardado como `bollerslev1986garch` é uma **tese de mestrado
de 2003** com o título parecido, não o artigo de 1986.

---

## F2 — O painel: retirar a v5, construir a v6

**O que está no ar:** a `/` serve a **v5** (`web/index.html` + 48 KB de `app.js`), e a
`/simple.html` serve a versão simplificada. Duas páginas a competir, e o aluno já disse que a v5
não serve.

**O que a v6 tem de ter**, e nada mais:

1. **O gráfico, que é a parte boa da v5.** Preços com os acontecimentos assinalados na curva, e
   **clicar num marcador abre o detalhe** desse acontecimento ou alerta. É a única coisa da v5
   que vale a pena salvar.
2. **O espelho do Telegram, que é a parte boa da simples.** O que foi enviado, e — a seguir — o
   que **não** foi, com a porta que travou e a margem que faltou. Nenhum produto comercial mostra
   o que descartou, e é isso que este mostra.
3. **As hiperligações a funcionar.** O `simple.html` já converte o `<a href>` do alerta; é preciso
   confirmar que a fonte da notícia abre mesmo, e que nenhum bocado de marcação sai como texto.
4. **Nada mais.** Sem probabilidade de triagem à vista (o critério H2 proíbe-a nas vistas de
   produto), sem relatório generativo, sem analista.

**Como se faz:** a v6 nasce do `simple.html` (que é honesto e tem 9 KB) e recebe o gráfico. Não
o contrário: reduzir a v5 seria arrastar 48 KB de coisas que se decidiu não mostrar.

**Como se sabe que ficou feito:**
- a `/` serve a v6, e a v5 sai do `Procfile` e da raiz
- clicar num marcador abre o detalhe, verificado no browser e não no código
- a ligação da fonte abre o artigo, verificada com um alerta real
- os testes de `api/` e `web/` continuam verdes, e ganham os da v6
- capturado um ecrã da v6 para a tese, se a tese a mostrar

**O que pode correr mal:** a tese descreve a interface em algum sítio. Antes de mexer, procurar o
que ela afirma sobre o painel, e ou a v6 cumpre, ou a tese muda no mesmo *commit*. Foi assim que a
promoção da v4 abriu dívida de tese que ficou meses por pagar.

---

## F3 — A escrita da tese: registo académico  ✅ FEITO (2026-08-20)

**O que se procura**, por esta ordem de gravidade:

1. **Brasileirismos.** Varridos com lista fechada, não com impressão. O último varrimento deu
   zero, mas foi antes de ~40 páginas novas.
2. **Registo demasiado coloquial.** Já apanhei três nesta ronda (*"a porta que mais mata"*,
   *"dispararia a torto e a direito"*, *"o ponto todo"*). Ficam candidatos como *"fazer batota
   com o tempo"*, que aparece **no índice**, e *"não me deu razão"*.
3. **Anglicismos onde há palavra portuguesa corrente.** *features* → entradas (feito), *proxy*,
   *lookahead*, *baseline*.
4. **Concordância.** Já corrigi 15 partidas pela substituição manchete→título; convém uma última
   passagem depois de todas as edições desta fase.
5. **Frases sem verbo, pontuação que muda o sentido, termos com dois nomes.**

**Método:** capítulo a capítulo, sobre o **PDF composto** e não sobre o `.tex` — várias coisas
desta revisão só apareceram a olhar para a página. Cada alteração é de forma, nunca de conteúdo:
**nenhum número, nenhuma citação e nenhuma afirmação muda nesta fase.**

**Como se sabe que ficou feito:** o `check_materiais.py` continua limpo, os 42 números continuam
a bater, e o diff desta fase não toca em nenhum `$...$` nem em nenhum `\cite`.

---

## F4 — Slides  ✅ FEITO (2026-08-20)

**Estado:** **20** *slides*, 0 erros, todos os números batem com a tese.

**Feito:** um *slide* novo, "Então quanto vale o modelo?", com as duas medições lado a
lado — a ablação da identidade ($0.534$ contra $0.538$, e $0.378$ sem nada da empresa) e as
linhas de base ponta a ponta ($0.375$ · $0.489$ · $0.632$ · $0.662$ · oráculo $0.968$). A
**deriva** saiu do rodapé e passou a linha própria na tabela das limitações. O *slide* de
fecho já existia. O `GRAVACAO.md` passou a apontar para o *slide* 19 de 20.

**O que fazer:** o aluno tem 20 minutos, o que dá menos de um minuto por *slide* e é apertado.
**Expandir só se cada *slide* novo ensinar alguma coisa que o júri vá perguntar.** Candidatos, e
os três primeiros são os que a tese ganhou depois de os *slides* estarem feitos:

- a **deriva** (PSI 0.281 com o rótulo parado) — é uma limitação medida, e um arguente pergunta
- a **ablação da identidade** tem *slide*? É o achado mais forte da tese
- as **linhas de base ponta a ponta** (0.489 · 0.632 · 0.662 · 0.968) — o oráculo é a informação
  nova, e diz onde está o problema
- um *slide* de **fecho** com as três lições, que é o que fica no ecrã durante as perguntas

**Como se sabe que ficou feito:** compila a 0 erros, o `check_materiais.py` continua limpo, e o
guião da gravação continua a apontar para o *slide* certo (é o 18 de 19 hoje).

---

## F5 — Guia de estudo e quizz  ✅ FEITO (2026-08-20)

**Estado:** guia com **22** *slides*, quizz com **37** perguntas.

**Feito:** o guia ganhou o *slide* da **decomposição** (técnica 2, com o encolhimento de
Vasicek e as duas coisas que se mediram nela), e a numeração das quatro técnicas passou a
bater com a do Nível 0. Ganhou também um segundo *slide* de avisos: o **$0.667$ contra
$0.455$** que foi retirado, e a tradução **RQ$	o$QI**. O quizz ganhou quatro perguntas: a
ablação da identidade (duas), o **oráculo** das linhas de base, e a **deriva**.

**O que falta:**
- o guia **não ensina** a decomposição com a profundidade das outras três, e ela é uma das quatro
  técnicas e responde a uma das três perguntas fundadoras
- o quizz não tem perguntas sobre o que a tese ganhou depois: a deriva, a ablação da identidade,
  as linhas de base ponta a ponta, o oráculo
- o guia tem os avisos do que **não** dizer? O *"quase 4×"* está lá; faltam o *"0,667 vs 0,455"*
  e a numeração RQ/QI

**Como se sabe que ficou feito:** o quizz tem uma pergunta por cada resultado que a tese reporta,
e o guia tem um *slide* por técnica com a mesma profundidade.

---

## F6 — Revisão de produto do painel  ✅ FEITO (2026-08-20)

Pedida como revisão de pré-lançamento e não como inspecção de interface: questionar a estrutura,
não preservar o que já lá está. Cinco achados, todos corrigidos.

**1. Duas representações, dois estados, no mesmo ecrã.** O gráfico era de uma empresa e as duas
listas por baixo eram de todas. Agora a empresa escolhida governa a página inteira — gráfico,
acontecimentos, detalhe do dia e mensagens — com um botão explícito para o canal todo. A URL
guarda a escolha.

**⚠️ 2. O produto respondia a duas das três perguntas fundadoras.** A repartição do movimento
(*foi a empresa, ou foi o mercado?*) vinha na API em cada linha, no campo `decomp`, e o cliente
**deitava-a fora**. O mesmo com o veredicto em palavras, que `app/verdict.py` calcula com 29
testes e a página ignorava. Uma camada testada, servida e invisível é pior do que não existir:
paga-se o custo e não se recebe o valor. Ambas voltaram ao ecrã, com testes que falham sem elas.

**⚠️ 3. A legenda dizia "0 sent" e a lista ao lado mostrava alertas enviados.** Um alerta mais
recente do que o último fecho desenhado não tem barra onde pousar, e era deitado fora em
silêncio. Passa a ser contado à parte e dito: *"2 more sent after the last close shown"*.

**4. O muro de texto.** Vinte e cinco mensagens de quinze linhas em monoespaçado. Cada uma passa
a mostrar o título e o movimento do momento, e abre para o texto **exacto** que saiu. E o canal
deixou de ser cortado em silêncio: quantas mensagens ficaram por mostrar é dito, com botão.

**5. O ecrã.** Uma coluna de 860 px num monitor de 1920. Duas colunas a partir dos 1100 px, o
gráfico a acompanhar a janela (`autoSize`), e no telemóvel a barra fixa deixou de comer 12% do
ecrã. Trinta e oito botões de data soltos viraram uma lista que diz o que aconteceu em cada dia.

**Verificado no browser, não no código:** contraste ≥ 4.5:1 nos dois temas em dez pares de
cores, zero rolagem horizontal a 375, 1200 e 1600 px, zero erros de consola, a ligação da fonte
a resolver para o artigo real (302 do Finnhub → Benzinga), e a página em produção com o
instantâneo fresco. **+3 testes** (744), verificados a falhar contra a página anterior.

**Também apanhado:** a porta dizia *ruff limpo* e havia **11 erros** em cinco verificadores;
corrigidos. E o `deploy_heroku.py` morria com um rasto de excepção quando a **consulta** ao
build expirava — com o build **bem sucedido** e a página já no ar. Um rasto que se lê como falha
leva alguém a implantar outra vez.

---

## O que NÃO está neste plano, e porquê

| | Porquê |
|---|---|
| Estudo com utilizadores | É o único item com relógio de calendário, e depende de recrutar pessoas. O pacote está pronto (`build_usefulness_pack.py`). Se não houver tempo, fica como limitação declarada, que é o que a tese já faz |
| Reescrever os documentos de defesa | São a voz do aluno e o raciocínio continua útil. Levam aviso no topo e o `LEIA-ME-PRIMEIRO.md` com o mapa |
| Tocar nas teses longas | Foram superadas. Compilam, e ficam como registo |
| Red team da guarda | 4 das 6 lentes nunca correram. A tese já diz que a força medida é um **limite inferior**, portanto é melhoria e não correcção |

---

## O que só o aluno pode fazer

1. **A leitura final da tese.** É pré-requisito da declaração de IA, que afirma *"Revi o conteúdo
   deste documento"*.
2. **Com o orientador:** a redacção exacta da declaração de IA, e a **licença do código** — que
   **não é uma escolha livre**: o repositório distribui derivados do FNSPID (**CC BY-SA**,
   partilha nos mesmos termos) e o `meia-style.cls` é **CC BY-NC-SA** (partilha nos mesmos termos
   *e* não comercial).
3. **A data de entrega**, hoje fixada em *setembro de 2026* na capa e na declaração.
4. **Rodar as 4 credenciais**, o PAT do GitHub primeiro, que tem `admin`.
5. **Descarregar os 3 PDF** de F1c e substituir o do Bollerslev.
6. **Gravar a demonstração** (`Win`+`G`), com o `tese/GRAVACAO.md` à frente.

---

## Ordem sugerida

**F1 primeiro**, porque é o único que pode invalidar afirmações da tese. **F2 a seguir**, porque
é o que tem mais código e mais risco de partir alguma coisa. **F3, F4 e F5 no fim**, porque são
de forma e não de conteúdo, e porque F4 e F5 só se fecham depois de F3 estabilizar o texto.
