# DEFENSE_QA — pergunta → resposta simples → resposta técnica → onde provar

> ⚠️ **Este documento foi escrito para a tese longa em inglês.** A que vais defender é a
> tese curta em português (`tese/`), que tem **três QI** e não quatro RQ, e onde alguns
> números foram corrigidos. Lê o [`LEIA-ME-PRIMEIRO.md`](LEIA-ME-PRIMEIRO.md) antes de
> estudares por aqui.

> **Como usar:** lê a coluna *simples* em voz alta até sair natural. A *técnica* só sai se
> insistirem. A coluna *onde provar* é para eu saber que existe — não é para recitar.
>
> **Regra da sala:** responde à pergunta que fizeram, não à que temias. E se não souberes,
> **"não medi isso"** é uma resposta completa e forte.

---

## A. As básicas (vão perguntar de certeza)

### A1. «Explique-me o seu trabalho em dois minutos.»
**Simples:** *"Construí um sistema de alertas para investidores de retalho. Quando uma das 12
empresas que vigio se mexe, ou sai uma notícia relevante, mando um alerta que responde a três
perguntas: isto é invulgar para esta acção? é a empresa ou é o mercado? já aconteceu antes, e o
que se seguiu? E nunca prevê preços — isso é uma restrição de desenho, não uma falha."*
**Técnica:** dois gatilhos independentes (z-score sobre retornos diários; notícia filtrada por
relevância), um motor de correlação que recupera casos semelhantes por embeddings e mede o
impacto ao estilo de estudo de evento, e um motor de explicação que renderiza o alerta a partir
dos objectos calculados.
**Provar:** tese §4.1, Figura 4.1 · demo: `python scripts/demo_defesa.py --offline`

### A2. «Qual é a contribuição, se todos os componentes já existiam?»
**Simples:** *"A integração avaliada. Nenhum algoritmo é novo. O que é novo é um sistema que
responde às três perguntas a custo zero, com cada afirmação rastreável ao procedimento que a
produziu, e com os resultados negativos reportados tal como caíram."*
**Técnica:** é uma dissertação de *Engenharia* de IA: integrar, aplicar e avaliar criticamente.
Duas comparações pré-comprometidas em que o método transparente venceu.
**Provar:** §1.4, §6.4 · Matriz de Evidência no Apêndice A

### A3. «Que dados usou?»
**Simples:** *"Duas camadas. A histórica é o FNSPID — 79.753 exemplos de notícia com preços
alinhados, de 2018 a 2023. A viva são notícias e preços de APIs gratuitas."*
**Técnica:** camada histórica com licença CC BY-SA 4.0, atribuída; camada viva Finnhub +
cadeia de 5 fontes de preços. Esquema comum às duas para serem directamente comparáveis.
**Provar:** §3.2, Tabela 3.1 (data card) · `THESIS_FACT_SHEET.md` §4

---

## B. As de método (as mais prováveis de um arguente técnico)

### B1. «Como garante que não há look-ahead?»
**Simples:** *"Há um teste que constrói duas séries de preços iguais até ao dia do evento e
depois divergentes de forma absurda, calcula as features nas duas, e exige que sejam idênticas.
E exige também que o rótulo MUDE — senão uma função que ignorasse os preços passava no teste."*
**Técnica:** a janela do z-score é `[-w-1:-1]`, exclui o dia julgado. As features são todas
computáveis ao fecho do dia `d`; o rótulo mede `(d, d+3]`. Divisão temporal por dia único com
embargo de 5 dias, que custa 820 linhas.
**Provar:** Excertos 3.1 e 3.2 na tese · `dataset.py:39,99,108` · `detector.py:28`

### B2. «Porque é que dividiu por tempo e não aleatoriamente?»
**Simples:** *"Porque com dados no tempo a divisão aleatória treina com o futuro para prever o
passado. E porque dias próximos parecem-se: se o dia 10 fosse treino e o 11 teste, o modelo já
tinha visto quase a mesma informação."*
**Técnica:** divisão por **dia único** (todos os títulos do mesmo dia no mesmo bloco) mais
embargo, porque o rótulo olha até 5 dias à frente e sem embargo um exemplo do fim do treino
seria rotulado por preços do bloco seguinte.
**Provar:** §3.3.4, Excerto 3.2 · `dataset.py:108`

### B3. «Porquê PR-AUC e não accuracy?»
**Simples:** *"Porque com classes desequilibradas a accuracy engana: um modelo que diz sempre
'não' pode ter 62% e ser inútil. O PR-AUC tem como chão a prevalência, por isso não me deixa
enganar-me a mim próprio."*
**Técnica:** prevalência do teste 0,378, que é exactamente o valor do "alertar sempre". Reporto
também ROC-AUC e Brier, e uma métrica com forma de produto — precisão dentro de um orçamento de
5 alertas/dia — porque é essa que corresponde ao custo real, a fadiga de alertas.
**Provar:** §3.6.4 · `model.py:68,82`

### B4. «Como criou os rótulos? Quem decidiu o que é positivo?»
**Simples:** *"Nenhuma pessoa. O rótulo é derivado dos preços: é positivo se, nos três dias
seguintes, a acção se moveu pelo menos 2% mais do que o mercado."*
**Técnica:** `|r_ticker − r_SPY|` acumulado em (d, d+3] ≥ 0,02. Direcção-livre por construção:
mede se houve reacção, nunca para que lado. Grelha de sensibilidade sobre τ ∈ {1,5%, 2%, 3%} e
h ∈ {1, 3, 5}.
**Provar:** §3.3.4 · `dataset.py:99`
**⚠️ A ressalva a dar antes que perguntem:** *"é um proxy — mede reacção do mercado, não
importância jornalística. Uma notícia importante que o mercado ignorou conta como não-material."*

### B5. «Qual é o baseline, e o que o ML acrescentou?»
**Simples:** *"O baseline é uma regressão só com a volatilidade recente. E ganhou. PR-AUC 0,542
contra 0,496 do modelo que também lê o texto."*
**Técnica:** comparação **pré-comprometida** — escolhi o baseline antes de correr. O negativo
sobreviveu a três testes: bootstrap por cluster (ticker, dia), re-teste justo com C afinado,
PCA e um encoder de domínio, e uma troca de métrica para orçamentos de alerta.
**Provar:** §5.5 · `evaluation_triage.md`, `evaluation_triage_fairtext.md`

---

## C. As que doem (ensaiar estas em voz alta)

### C1. «Os vossos "precedentes" são anteriores à consulta?»
**Simples:** *"Na experiência de avaliação, a maior parte não é — só 31%. Por isso não lhe
chamo recuperação de precedentes, chamo-lhe recuperação semântica de itens do mesmo setor. Em
produção são anteriores por construção."*
**Técnica:** o corpus tem 27 dias e a avaliação não restringe candidatos por data — só a linha
de base de recência usa datas. A métrica não é afectada, porque pontua concordância de **setor**
e o setor não muda com o tempo. Na implantação a base termina em 2023 e as consultas são de
2026. A medição de impacto olha sempre só para a frente.
**Provar:** §3.2.3, §6.5 · `evaluation_relevance_filter.md` §3

### C2. «Deita fora dois terços das notícias. Com que critério?»
**Simples:** *"O título tem de nomear a empresa e não pode ser um resumo genérico de mercado.
Medi o efeito: mantenho 811 de 2.478. E só 3% dos descartes são a regra de boilerplate — os
outros 64% falham por o título nunca nomear a empresa."*
**Técnica:** `relevante = não-vazia ∧ ¬boilerplate ∧ menciona(ticker ∨ alias)`, comparação por
palavra inteira. É código determinístico: duas pessoas obtêm o mesmo resultado.
**Provar:** §4.5 · `relevance.py:114` · `evaluation_relevance_filter.md`
**⚠️ Assumir sem esperar:** *"a regra foi escrita depois de ler os primeiros 27 alertas, e as
listas de aliases são feitas à mão. É reprodutível, mas não é um critério a priori."*

### C3. «Então o vosso machine learning funciona ou não?»
**Simples:** *"Em dados retidos, sim. Em produção, não — e medi-o. ROC-AUC 0,486, com o
intervalo a conter o acaso."*
**Técnica:** duas falhas produzem o mesmo sintoma e pedem correcções opostas. Se o score ordena
e só a escala está errada, recalibra-se. Se não ordena, recalibrar não serve, porque a sigmóide
é **monótona** e preserva a ordem exactamente. Medi a discriminação: não há ordem para preservar.
A explicação é que o modelo é **redundante**, não avariado — a materialidade ao vivo corre a
0,602 contra 0,378 no treino, porque só se registam títulos que já passaram os filtros.
**A lição:** *um modelo avaliado isolado e implantado atrás de filtros nunca foi avaliado na
distribuição que ia ver.*
**Provar:** §6.5 · `evaluation_live_transfer.md` · `recalibrate_live.py` (recusa-se a correr)

### C4. «"Mesmo setor" não é "análogo".»
**Simples:** *"Concordo, é um proxy, e está declarado como limitação."*
**Técnica:** três defesas. Excluo a própria empresa, o que torna a métrica mais difícil e não
mais fácil. O ganho é maior onde o vocabulário é distintivo (energia +0,377) e menor no consumo,
que é genérico — que é o padrão que se esperaria se estivesse mesmo a captar significado. E a
alternativa honesta seria um estudo humano de relevância, que não fiz.
**Provar:** §3.6.1, §5.10 · `evaluation_per_sector.md`

### C5. «Prevêem ou não prevêem?»
**Simples:** *"Prevejo uma coisa, de forma estreita: se o mercado vai reagir de forma
anormalmente grande. Nunca a direcção, nunca o preço."*
**Técnica:** o rótulo é o valor absoluto do retorno anormal — direcção-livre por construção.
Uma versão anterior do alerta terminava em *"not a forecast"* e isso era **falso**: uma
probabilidade sobre os próximos dias é uma afirmação sobre o futuro. Está corrigido, e a
distinção verdadeira — materialidade vs direcção — está agora no texto.
**Provar:** §2.9, §4.6 · `explain.py:45`

### C6. «É só uma regressão logística com 9 números.»
**Simples:** *"É. E testei modelos com mais capacidade: o gradient boosting saiu-se pior, 0,469
contra 0,542. Se o problema fosse falta de capacidade, teria ganho."*
**Técnica:** o que é modesto aqui é o **sinal**, não a solução. A contribuição está no método:
divisão temporal com embargo, teste de fuga, calibração só na validação, PR-AUC com chão
explícito, e um negativo que sobreviveu a três tentativas de o derrubar. Uso deep learning
onde ele se justifica — o SBERT — e a engenharia aí foi pô-lo a correr em 512 MB sem framework.
**Provar:** §5.5 · §4.9 (ONNX)

### C7. «Porque tantos resultados negativos?»
**Simples:** *"Porque as comparações foram pré-comprometidas, e porque um trabalho que só
reporta o que correu bem é um trabalho em que não se pode confiar."*
**Técnica:** todas as retiradas caíram por medições minhas, não por revisão externa. O apêndice
tem uma matriz que marca cada afirmação como mantida, estreitada ou retirada — e as retiradas
ficam lá de propósito: uma matriz que só listasse as sobreviventes não seria uma auditoria.
**Provar:** Apêndice A, Matriz de Evidência

---

## D. Sobre IA, aprendizagem e arquitectura

### D1. «O sistema aprende sozinho?»
**Simples:** *"Não. Faz inferência com pesos fixos. O que corre continuamente é recolha de
rótulos e monitorização — nenhum peso muda."*
**Técnica:** quatro coisas diferentes. **Inferência** (a cada 60 s), **treino** (uma vez,
offline), **re-treino** (possível, documentado, nunca executado), **aprendizagem contínua** (não
existe). Chamar aprendizagem contínua à recolha de rótulos seria exagero.
**Provar:** §3.3.4 · `postval.py`

### D2. «Onde está o modelo? Como sabe que o avaliado é o que corre?»
**Simples:** *"É um ficheiro de 1,8 KB no repositório, com um JSON ao lado que guarda a
semente, os blocos e as métricas. É literalmente o mesmo ficheiro."*
**Técnica:** e não é preciso acreditar em mim — há um teste que carrega o ficheiro implantado,
recalcula as quatro métricas que a tese cita e exige igualdade **exacta**. Para o SBERT a
garantia é outra: verificação contra um SHA256 fixo, para um download corrompido falhar fechado.
**Provar:** `tests/test_frozen_reproducibility.py` · §4.9

### D3. «A arquitectura do diagrama é a que está implementada?»
**Simples:** *"Sim, e é deliberadamente modesta: um script treina e grava um ficheiro; o worker
carrega esse ficheiro. Não há pipeline de treino automático nem registo de modelos a sério."*
**Técnica:** dois processos num alojamento pago — um worker com ciclo de 60 s e um servidor web.
O par `.joblib`/`.json` **funciona** como registo de modelos, e digo-o nesses termos, sem
desenhar uma arquitectura aspiracional.
**Provar:** §4.9 · Apêndice A

### D4. «Usam um LLM. Isso não faz o sistema aprender?»
**Simples:** *"Não. O LLM só escreve a linguagem — nunca fornece factos. E há uma guarda que
valida a saída dele contra a evidência calculada antes de a entregar."*
**Técnica:** qualquer número ausente da evidência, qualquer sinal invertido, qualquer redacção
preditiva, faz descartar a resposta inteira a favor do texto determinístico. O primeiro desenho
era uma blocklist e falhou contra um red team; foi reconstruído como vocabulário fechado.
**Provar:** §6.1 (RQ3) · `narrator_guard.md`

---

### D5. «Onde é que está a inteligência artificial neste trabalho?» ⭐

> Esta é **a pergunta**. Ensaia-a até saíres sem hesitar.

**Simples:** *"Em quatro camadas, e cada uma faz uma coisa diferente. Estatística determinística
para detectar. **Modelos treinados** para recuperar casos análogos e para pontuar materialidade —
um transformer de frases e uma regressão logística calibrada, treinada por mim em 79 mil
exemplos. E **geração** para sintetizar tudo isso em prosa. A quarta é a que se vê no ecrã; as
outras três é que produzem os factos que ela usa."*

**Técnica:** a distinção que interessa não é de fluência, é de **ancoragem**. Um LLM genérico
responde "porque é que a XOM subiu?" com o que leu na Internet até à data de corte. Este responde
com: o retorno medido da sessão, o z-score contra a norma de 20 dias *daquele* nome, a
decomposição mercado/setor/empresa com betas encolhidos por Vasicek, os títulos captadas com
carimbo temporal, e — o que nenhum modelo sabe de cor — **casos passados semanticamente parecidos
com o desfecho medido a cinco dias**, recuperados de um arquivo de mais de 80 mil títulos.

**A frase que fecha:** *"O modelo não sabe o que aconteceu. É-lhe dito. E cada número que ele
escreve é verificado contra a evidência que o produziu, antes de chegar ao ecrã."*

**Provar:** §4.8 · §3.4 · `evaluation_intelligence_guard.md` · **e mostra no ecrã**: clica numa
âncora `[f1]` e abre o facto.

---

### D6. «Isso não é só um wrapper de ChatGPT com um prompt bonito?»
**Simples:** *"Não, e a diferença é verificável em três segundos: clique num identificador do
texto e ele abre o facto que o gerou, com a origem declarada. Um wrapper não consegue fazer isso
porque não tem factos próprios."*
**Técnica:** o gerador recebe um **pacote de evidência** onde cada registo tem `id`, valor e
origem (`medido` / `calculado` / `modelo`). **Nenhum registo tem origem `gerado`** — há um teste
que o exige. A guarda liga cada número à frase que o cita: citar um facto e usar o número de
outro é rejeitado.
**Provar:** §4.8.1 · `investigator/intelligence/context.py`

---

### D7. «A vossa guarda é uma blocklist. Não me disse na tese que blocklists perdem sempre?» ⚠️
> **Armadilha, e é justa. Não te defendas — concorda e explica a diferença de risco.**

**Simples:** *"Disse, e continua a ser verdade. Por isso o alerta — que é **empurrado** para o
telemóvel sem evidência ao lado — usa uma allowlist de vocabulário fechado. O relatório é
**pedido** pelo utilizador, na página, com a evidência a um clique. São dois perfis de risco
diferentes, e por isso duas garantias diferentes. Está declarado numa tabela, não escondido."*
**Técnica:** o que se mantém **idêntico** nos dois caminhos é a parte verificável: números do
conjunto fechado, sinal obrigatório, e aqui ainda mais estrito — ligados à frase que os cita. O
que é mais fraco é só a defesa **linguística**, e os quatro riscos residuais estão em
`guard.RESIDUAL` e no §6.5.
**Provar:** §4.8.2 (a tabela dos dois níveis) · §6.5

---

### D8. «Como sabe que a guarda funciona?»
**Simples:** *"23 de 23 ataques bloqueados, e — o número que importa mais — 8 de 8 frases fiéis
aceites. Sem o segundo, uma guarda que rejeitasse tudo pontuava 100% e parecia perfeita."*
**Técnica:** e o que a guarda **rejeita** é informativo: nos relatórios gerados as rejeições foram
de causa afirmada, conselho e previsão — os três registos que o sistema recusa. Ou seja está a
trabalhar continuamente, não a decorar um caminho que já era seguro.
**⚠️ E digo antes que perguntem:** o red team tinha seis lentes, **duas completaram** e **nenhum
verificador correu** — bateram no limite de gasto. O workflow devolveu "nenhum exploit
sobreviveu", e isso é a *ausência* de verificação, não um resultado limpo. A força medida é um
**limite inferior**.
**Provar:** `evaluation_intelligence_guard.md` · §6.5

---

### D9. «Porque é que reescreveu a interface? Isso é engenharia de software, não de IA.»
**Simples:** *"Porque a arquitectura antiga obrigava-me a **retirar uma capacidade da tese**: a
recuperação de precedentes custava sete segundos a carregar e foi removida da página. Separar o
cliente do servidor não a acelera — elimina a escolha."*
**Técnica:** o custo medido: carga de 5,5–6,2 s para 1,0 s, 12 pedidos para 1, e mudar de
intervalo de ~750 ms para 2,5–7,3 ms **com zero chamadas de rede**. O zero é a afirmação
estrutural: passou a ser uma fatia de um vector que o browser já tem.
**Provar:** §4.7.1 (tabela) · medido no browser, em produção

---

## E. Produto

### E1. «O sistema funciona?»
**Simples:** *"Depende do que 'funciona' quer dizer, e vale a pena separar."*
**Técnica:** a API responde, a app abre, o alerta é gerado, e a mediana entre a deteção e a
chegada da mensagem é de **5 segundos** — isso está medido, sobre 278 alertas. Se o alerta é
**útil** ao investidor não está medido, e é a única lacuna real da tese.

⚠️ **Não digas «1 segundo».** Era a medição antiga, sobre 101 alertas; e não digas «chega em
segundos» sem dizer o resto, porque a mediana **até detetar** é de 353 minutos e é aí que o
arguente vai. A frase que aguenta é: *o sistema entrega em segundos aquilo que a fonte lhe dá*.
**Provar:** §6.5 (limitações) · Apêndice A (332 alertas com carimbos)

### E2. «Porque é que a demo é uma gravação e não ao vivo?»
**Simples:** *"Porque nove em cada dez varreduras não mandam nada. O silêncio é o comportamento
correcto. Uma demo ao vivo mostrava um ecrã parado, e forçar um alerta seria fabricar
exactamente o que esta tese recusa fabricar."*
**Técnica:** o replay corre sobre três registos versionados que o sistema escreveu enquanto
decidia. É determinístico e funciona sem rede.
**Provar:** `demonstracao.md` · `python scripts/demo_defesa.py --offline`

### E3. «O alerta chega a tempo?»
**Simples:** *"Do nosso lado, ~5 segundos. O tempo todo está na descoberta: ~353 minutos até a
fonte gratuita publicar a notícia."*
**Técnica:** reporto as duas componentes separadas de propósito, porque um número agregado não
distingue "somos lentos" de "a fonte é lenta", e as duas afirmações pedem coisas opostas — a
primeira pede engenharia, a segunda pede honestidade sobre a limitação.
**Provar:** §6.2 · `evaluation_latency.md`

---

## F. As três respostas que valem mais do que qualquer número

1. **«Não medi isso.»** — Completa. Não a enfeites.
2. **«Isso está declarado como limitação, na secção X.»** — Transforma um ataque numa
   confirmação de que li o meu próprio trabalho.
3. **«Isso foi uma afirmação que retirei, e está na matriz como retirada.»** — Não há resposta
   a isto, porque já concordei antes de perguntarem.
