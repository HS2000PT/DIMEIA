# Diagnostico integral da tese canonica

**Data:** 2026-08-30  
**Fonte analisada:** `tese/main.pdf`  
**Estado da fonte:** 134 paginas fisicas; PDF gerado em 2026-08-28; SHA-256
`DC9BEAADFCA499458DB196883D34F6286FF39ED4D23D9D3C17B5C713AB7FC9A9`.

## Ambito e metodo

Este documento e um diagnostico, nao uma reescrita. A tese, o produto e os resultados congelados
nao foram alterados nesta passagem. O texto externo `REVISAO INTEGRAL E CRITICA DA TESE —
main.pdf.md` foi usado como especificacao do tipo de revisao pedido, e nao como autoridade sobre o
conteudo.

A verificacao combinou:

- leitura integral das 134 paginas do PDF canonico, com extracao em fluxo e com preservacao de
  composicao;
- inspecao visual de todas as paginas e ampliacao das paginas com figuras, tabelas de sintese e
  apendice;
- confronto com os capitulos LaTeX, geradores, artefactos de avaliacao e implementacao atual;
- execucao de `scripts/check_entrega.py`, que passou as 11 verificacoes e os oito verificadores
  especializados;
- duas reproducoes dirigidas contra o codigo: o caso `sigma=0` do detetor e a primeira posicao do
  piso escalonado com orcamento diario;
- uma analise de sensibilidade nova, apenas diagnostica, a titulos exatamente repetidos na QI2.

O resultado geral e importante: **nao ha uma falha sistemica escondida nem uma tese cientificamente
indefensavel**. A tese e rara na quantidade de resultados negativos, limites e correcoes que ja
declara. O risco que resta concentra-se em validade de construto, transferencia treino-producao e
algumas frases finais que prometem mais do que os proprios resultados. Ha tambem quatro correcoes
objetivas de alto retorno que devem anteceder a congelacao final.

---

## 1. A tese, em linguagem simples

O InvestiGator tenta resolver um problema concreto: quando o preco de uma empresa se move ou sai uma
noticia, um investidor particular recebe normalmente um numero ou uma manchete, mas nao uma
explicacao que consiga seguir e conferir.

O sistema combina quatro decisoes:

1. decide se o movimento do preco e invulgar para aquela empresa;
2. separa quanto do movimento veio do mercado, do setor e da propria empresa;
3. procura noticias historicas de outras empresas do mesmo setor com significado parecido e mostra
   o que aconteceu depois delas;
4. estima se uma nova noticia merece ocupar uma das poucas interrupcoes diarias.

A contribuicao nao e um algoritmo novo. E uma contribuicao de Engenharia de IA: construir o sistema,
obrigar cada componente a competir com uma alternativa simples, medir a cadeia em producao e manter
os resultados quando contrariam a hipotese inicial. O resultado cientifico central e misto:

- **QI1: sim.** O z-score produz uma cadencia muito mais comparavel entre empresas e bate duas
  alternativas aprendidas no protocolo usado.
- **QI2: sim, mas estreito.** A representacao semantica recupera melhor noticias de outra empresa do
  mesmo setor; isto mede tema/setor, nao relevancia factual nem direcao futura.
- **QI3: nao.** O modelo com texto nao bate a volatilidade; o texto acrescenta um sinal pequeno por
  cima de uma base por empresa, mas esse acrescimo desaparece na metrica de produto e nao distingue
  noticias da mesma empresa.

A promessa mais forte do produto e de **fidelidade**: o alerta e montado a partir dos objetos
calculados. A promessa que a tese deliberadamente nao fecha e a de **utilidade humana**, porque o
estudo com pessoas foi desenhado mas nao executado.

---

## 2. As dez fragilidades principais, por risco de defesa

### 1. A QI3 nao rotula a importancia de cada noticia

**Risco: muito alto.** O rotulo e calculado por `(empresa, dia)` a partir do movimento futuro do
preco. Todas as manchetes da mesma empresa no mesmo dia recebem o mesmo desfecho. Assim, a experiencia
mede sobretudo se um **dia de uma empresa** antecedeu um movimento invulgar, nao se **aquela noticia**
merecia um alerta. A tese reconhece a multi-contagem nas pp. 37, 79 e 95, mas a formulacao da QI3
continua a dizer “que noticias merecem um alerta”.

**Defesa correta:** chamar-lhe explicitamente proxy de materialidade por empresa-dia; nao atribuir
causalidade a uma manchete; dizer que um alvo por noticia exigiria timestamps e anotacao/atribuicao
que este trabalho nao produziu.

### 2. A utilidade para pessoas nao foi medida

**Risco: muito alto.** O sistema e destinado a nao especialistas, mas nenhum utilizador concluiu a
travessia frase -> evidencia. A tese e honesta: o objetivo esta “cumprido por metade”, a matriz marca
utilidade como “nao afirmado” e o protocolo esta no Apendice A.5 (pp. 109-110). Ainda assim, esta e a
lacuna que melhor ataca o valor externo do artefacto.

**Defesa correta:** separar fidelidade mecanica de utilidade percebida. O estudo estar desenhado prova
que a pergunta foi pensada; nao substitui dados humanos.

### 3. A garantia anti-lookahead e diaria, nao relativa ao instante da noticia

**Risco: muito alto.** No treino, `ret_event` e o retorno completo entre os fechos de `d-1` e `d`
(Tabela 3.1, p. 24). Isso nao usa nada depois do fecho de `d`, mas pode usar horas posteriores a uma
noticia publicada de manha. Em producao, a noticia e pontuada quando chega e a ultima barra pode ser
o fecho anterior ou uma barra incompleta; a propria tese reconhece a incompatibilidade nas pp. 82-83.

**Defesa correta:** a garantia demonstrada e contra dados posteriores ao **fecho do dia do evento**;
nao e uma garantia timestamp-a-timestamp. A transferencia desta entrada para producao falhou e e uma
das explicacoes possiveis para o resultado ao vivo.

### 4. A QI2 mede o proxy de setor e e sensivel a historias sindicadas

**Risco: alto.** “Mesmo setor” nao e “noticia genuinamente relacionada”. Excluir o proprio ticker
torna o teste mais exigente, mas o modelo ainda pode ganhar por vocabulario setorial, nomes de
empresas e copias da mesma historia publicadas para varios tickers.

No corpus recente ha 3 714 linhas e apenas 2 879 manchetes normalizadas unicas; 1 413 linhas pertencem
a 578 grupos de manchete exatamente igual que atravessam tickers. Numa verificacao de sensibilidade
com o mesmo `k=5`, 500 consultas, cinco sementes e os embeddings existentes, proibir candidatos com
a mesma manchete normalizada fez a P@5 descer de **0.514 para 0.491**; o chao ficou em 0.240 e a
margem continuou forte, de +0.273 para +0.250. O resultado sobrevive, mas cerca de 0.023 da precisao
vem desta classe de repeticao. Este numero ainda nao tem gerador canonico e nao deve entrar na tese
sem o ganhar.

### 5. Ha tres inconsistencias finais diretamente visiveis

**Risco: alto porque sao perguntas de “abrir na pagina”.**

- A Tabela 4.5 (p. 52) diz que o primeiro alerta de uma empresa exige 0.49. Com
  `daily_budget: 5`, o codigo torna a primeira posicao livre de piso; um alerta com 0.10 passou na
  reproducao. O 0.64 aplica-se ao segundo alerta; o 0.49 deixa de atuar no primeiro.
- A QI2 pergunta por noticias **passadas** e a Secao 5.5.4 mede o protocolo causal correto:
  P@5 0.513, chao 0.259. A Tabela 5.12 e a Figura 6.1/fecho (pp. 90 e 92) voltam a destacar 0.595,
  que permite candidatos futuros. A conclusao mantem-se; o numero de sintese esta desalinhado.
- O texto da p. 74 diz que a Figura 5.6 mostra resultados “por setor”. A figura mostra apenas
  resultados agregados por metodo em P@5 e P@10. A afirmacao mais defensavel, vitoria nos cinco
  setores, ficou sem a visualizacao que a devia sustentar.

### 6. O argumento de que o beta igual a um nao pode mudar a ordenacao e forte demais

**Risco: alto.** Na p. 36, a tese diz que usar o mesmo rotulo ruidoso para seis familias torna a
tarefa igualmente dificil e afeta o nivel das metricas, “nao a ordenacao”. A primeira metade e
verdadeira apenas como igualdade de protocolo. A segunda nao decorre dela: ruido correlacionado com
beta, volatilidade, empresa ou setor pode beneficiar familias com essas entradas de forma diferente.

**Defesa correta:** todas as familias foram comparadas internamente contra o mesmo alvo, mas a
robustez da ordenacao a um rotulo construido com betas estimados **nao foi testada**.

### 7. O modelo produz probabilidades no alerta, mas nao discriminou em producao

**Risco: alto.** A calibracao aplicada ao teste fica cerca de cinco pontos percentuais otimista
(p. 54). Nas 825 decisoes maturadas, reduzidas a 239 unidades empresa-dia, a ROC-AUC e 0.486 com IC
[0.403, 0.571] (p. 79): a amostra nao distingue o modelo do acaso. Duas das doze empresas nem
apareciam no treino. Mostrar “57%” e tecnicamente fiel ao calibrador, mas nao autoriza chamar ao
numero uma probabilidade transportada com sucesso para 2026.

**Defesa correta:** “calibrada no bloco de validacao, com erro de transferencia medido”; nunca
“probabilidade honesta” sem esta ressalva.

### 8. A decomposicao e interpretavel, mas fracamente validada

**Risco: alto.** Nao ha verdade de terreno para a parcela empresa/mercado/setor. Os priors 1.0, 0.0
e desvio 0.5 sao escolhas do autor sem analise de sensibilidade; a empresa pertence aos indices
contra os quais e regredida; o mapa setorial nao coincide integralmente com o ETF; e um dos 17
ajustes tem R2 negativo. A tese declara tudo isto, o que e uma forca, mas “nao ha linha de base
possivel” (p. 94) e excessivo. Mesmo sem verdade de terreno, eram possiveis comparacoes de
estabilidade, mercado-so vs mercado+setor, bruto vs encolhido, dados sinteticos ou validacao fora da
amostra.

### 9. A avaliacao ponta-a-ponta mede um proxy offline, nao valor para a pessoa

**Risco: medio-alto.** A p. 86 declara corretamente que escolher os cinco melhores depois de ver o
dia inteiro e um limite superior da politica online. Mas a p. 89 transforma 0.632 vs 0.489 em “valor
mensuravel sobre o que a pessoa ja tinha”. O numero mede precisao no rotulo proxy, sob politica
offline; nao mede utilidade, decisao, confianca nem beneficio economico para uma pessoa.

**Defesa correta:** “ganho mensuravel na ordenacao offline segundo o proxy de materialidade”.

### 10. A simplicidade escolhida tem dois custos que o juri pode explorar

**Risco: medio-alto.** O detetor implantado de 20 dias obtem F1 0.516, enquanto 60 dias obtem 0.678
e EWMA 0.664. A explicabilidade e a resposta mais rapida a mudanca justificam a opcao, mas o preco e
grande e deve ser assumido como decisao de produto, nao superioridade tecnica.

Ha ainda um defeito limite confirmado: depois de 20 retornos todos iguais, um salto de 5% produz
`sigma=0`, `z=0` e **nenhum alerta**. A frase da p. 27, “uma acao parada [...] nao tem nada de
especial”, so descreve o caso em que hoje tambem fica parada; nao descreve o salto que o codigo
silencia.

---

## 3. Dez melhorias de maior retorno antes da defesa

| Prioridade | Melhoria | Trabalho | Retorno |
|---|---|---:|---|
| 1 | Corrigir a Tabela 4.5: com orcamento, o primeiro alerta nao tem piso; o segundo usa 0.64. Sincronizar guia e simulacro. | baixo | elimina uma contradicao direta com codigo e configuracao |
| 2 | Fazer a sintese da QI2 usar o numero causal: 0.513, chao 0.259, margem +0.254. Manter 0.595 apenas como teste simetrico de escala, claramente rotulado. | baixo | alinha pergunta, protocolo, tabela final e conclusao |
| 3 | Substituir a Figura 5.6 por um grafico realmente por setor, com os cinco chãos; acrescentar um pequeno painel causal 0.595/0.333 vs 0.513/0.259. | medio | torna visivel a melhor defesa da QI2 sem treinar nada |
| 4 | Reescrever a frase do beta=1: protocolo igual, ordenacao nao garantida; declarar que a sensibilidade a outro rotulo nao foi corrida. | baixo | remove uma inferencia estatistica indefensavel |
| 5 | Delimitar “anti-lookahead” como garantia ao fecho diario e trazer o desfasamento de `ret_event` para a primeira explicacao da QI3. | baixo | fecha a pergunta tecnica mais perigosa sem esconder o negativo |
| 6 | Corrigir o caso `sigma=0` no detetor, nos tres caminhos, com teste de regressao e semantica definida para salto apos janela constante; sincronizar tese e guia de construcao. | medio | corrige um defeito real e demonstravel |
| 7 | Trocar “valor para a pessoa” por “ganho no proxy sob politica offline”; trocar “fontes gratuitas nao dao precos ao minuto” por falta de historico intradiario fiavel, timestamp exato e atribuicao causal em escala. | baixo | impede duas sobre-afirmacoes no Capitulo 6 |
| 8 | Canonizar a sensibilidade a manchetes repetidas com script, artefacto e verificador; se o numero reproduzir, acrescentar 0.491 como robustez, nao como novo resultado principal. | medio | antecipa uma objecao forte e mostra que a QI2 sobrevive |
| 9 | Trocar “nao ha linha de base possivel” por “nao ha verdade de terreno para exatidao”; listar as comparacoes que ficaram por fazer e evitar nova experiencia apressada. | baixo | torna a defesa da decomposicao precisa |
| 10 | Uniformizar rotulos dos graficos para portugues, verificar os Type 3/ausencia de tagging contra as regras de deposito e manter o apendice legivel; nao mudar a fonte se a instituicao nao o exigir. | medio | melhora acabamento sem reabrir a ciencia |

**O que nao fazer em tres dias:** retreinar toda a QI3, inventar participantes, acrescentar um LLM,
migrar o repositorio antes de testar a dependencia da base historica, ou compactar capitulos antes de
fechar estas correcoes. O risco supera o retorno.

---

## 4. Figuras essenciais e o que falta desenhar

### Conjunto essencial para a defesa

1. **Figura 1.2, p. 3 — promessa do sistema.** Abre o problema, os dois gatilhos e o que o
   investidor recebe. Deve ser a primeira figura conceptual da apresentacao.
2. **Figura 3.1, p. 22 — as quatro decisoes.** E o mapa mais economico entre pergunta, tecnica e
   componente.
3. **Figura 3.6, p. 29 — decomposicao num caso real.** Ja faz o trabalho visual certo: parcela,
   sinal e soma, com a ressalva de que somar nao valida.
4. **Figura 4.1, p. 45 — arquitetura.** Mostra entradas, motores e entregas; deve acompanhar a
   explicacao de ponta a ponta, nao uma lista de modulos.
5. **Figura 4.2, p. 49 — caminho de uma noticia.** E a melhor figura para explicar portas, silencio
   e por que nove em dez varreduras nao chegam ao utilizador.
6. **Figura 4.3, p. 54 — alerta real.** Mostra exatamente o produto, incluindo a previsao citada de
   terceiros e a probabilidade de materialidade.
7. **Figura 5.4, p. 69 — QI1.** Deve sustentar o “sim” da detecao; manter a comparacao com a regra
   fixa e os metodos aprendidos na fala.
8. **Figura 5.7, p. 77 — QI3.** E a figura do resultado negativo. Deve ser mostrada antes da
   ablação, para nao parecer que o veredicto foi reconstruido depois.
9. **Figura 5.8, p. 81 — a porta separa empresas.** E a visualizacao que transforma o negativo em
   explicacao: a maioria das decisoes estava tomada antes do titulo.
10. **Figura 6.1, p. 92 — veredictos.** E uma boa figura final, mas so depois de corrigir a linha da
    QI2 para o protocolo causal.

### Figuras a criar ou corrigir

- **QI2 por setor, obrigatoria.** Cinco grupos, cada um com P@5 do metodo e o seu chao; os dados ja
  existem em `docs/evaluation/evaluation_per_sector.md`. A figura atual nao e por setor.
- **QI2 causal vs simetrica.** Dois pares de barras com precisao e chao, destacando as margens
  +0.262 e +0.254. E uma explicacao visual muito melhor do que defender 0.595 em prosa.
- **Treino -> producao de `ret_event`.** Um eixo temporal simples: fecho `d-1`, publicacao,
  pontuacao, fecho `d`, rotulo futuro. Isto torna imediatamente visivel o que o teste garante e o
  que nao garante.
- **Escada de evidencia da QI3.** Quatro linhas: volatilidade 0.542; modelo implantado 0.538;
  contexto+texto 0.496; texto sobre a tabela +0.012, mas precisao@5 sem mudanca. Serve para impedir
  que numeros de perguntas diferentes sejam comparados como se fossem a mesma experiencia.

### Diagnostico de composicao

As 134 paginas foram inspecionadas. Nao ha figuras cortadas, texto sobreposto, referencias visuais
partidas nem paginas densas de forma incoerente. As Tabelas A.2 e A.3 (pp. 107-108) sao densas, mas
legiveis ampliadas; dividir a A.3 so vale a pena se nao aumentar o documento de forma desnecessaria.
Os graficos de avaliacao usam rotulos em ingles num documento portugues: e polimento, nao risco
cientifico.

Tecnicamente, todas as fontes estao incorporadas, mas o PDF usa sobretudo fontes Type 3, nao esta
marcado como documento acessivel e o `pdfinfo` emite um aviso de destino de anotacao curto. Uma
segunda leitura com `pypdf` encontrou 724 anotacoes, 551 destinos nomeados e zero arrays de destino
invalidos; nao ha evidencia de link partido. Deve confirmar-se apenas se o regulamento de deposito
exige PDF/A, fontes escalaveis ou tagging antes de mexer na compilacao.

---

## 5. Quinze perguntas perigosas do juri

### 1. “Como pode dizer que decide que noticias merecem alerta se todas as noticias da mesma empresa e dia recebem o mesmo rotulo?”

**Resposta-nucleo:** nao pode inferir causalidade por noticia. A QI3 usa um proxy por empresa-dia;
foi suficiente para comparar familias no protocolo, mas nao para atribuir o movimento a uma
manchete. E a primeira linha de trabalho futuro.

### 2. “A noticia sai de manha. Como e que o retorno ate ao fecho nao e futuro?”

**Resposta-nucleo:** e conhecido no fecho, nao no instante da publicacao. O teste impede dados depois
do fecho de `d`; nao prova disponibilidade intradiaria. A incompatibilidade treino-producao esta
medida e declarada.

### 3. “Porque afirma que o beta igual a um nao pode mudar a ordenacao dos modelos?”

**Resposta-nucleo:** essa formulacao deve ser estreitada. O alvo e igual para todos, garantindo
comparacao interna; nao se demonstrou que outro alvo preservaria a ordenacao.

### 4. “Mesmo setor e a sua definicao de relevancia?”

**Resposta-nucleo:** e o proxy automatico, nao relevancia semantica julgada por humanos. A empresa da
consulta e excluida e os chãos sao medidos; a conclusao e apenas “recupera o mesmo setor melhor”.

### 5. “Quanto do resultado da recuperacao vem de copiar a mesma historia entre tickers?”

**Resposta-nucleo:** na verificacao diagnostica do corpus recente, proibir a mesma manchete fez a
P@5 passar de 0.514 para 0.491. O ganho sobre o chao continua forte; a sensibilidade deve ser
canonizada antes de ser citada como resultado da tese.

### 6. “Porque resume a QI2 com 0.595 se o recuperador real so pode ver o passado e ai obtem 0.513?”

**Resposta-nucleo:** 0.595 mede o protocolo simetrico de escala; 0.513 mede a tarefa causal do
produto. A conclusao mantem-se porque a margem sobre o respetivo chao quase nao muda; a sintese deve
usar 0.513.

### 7. “Porque manteve 20 dias se 60 dias e EWMA ganham por uma margem tao grande?”

**Resposta-nucleo:** foi uma troca de produto: 20 dias reage mais depressa e a estatistica explica-se
diretamente. A medicao favorece as alternativas em F1; nao se deve chamar a escolha implantada a
melhor tecnica.

### 8. “O que acontece se os vinte dias anteriores tiverem variancia zero?”

**Resposta-nucleo:** o codigo atual devolve zero para evitar divisao, o que tambem silencia um salto
posterior. E um caso limite real a corrigir com politica explicita e teste; nao deve ser defendido
como comportamento correto.

### 9. “Porque mostra 57% se em producao o modelo e indistinguivel do acaso?”

**Resposta-nucleo:** 57% e a saida do calibrador ajustado na validacao, nao uma garantia transportada
para 2026. A tese mede cerca de cinco pontos de otimismo e uma ROC-AUC de 0.486 em producao; por isso
o modelo deixou de vetar e passou apenas a ordenar dentro do que ainda consegue.

### 10. “Uma tabela de treze constantes bate o modelo. Para que serve a aprendizagem automatica?”

**Resposta-nucleo:** serviu para testar e localizar o limite. A experiencia mostrou que a variacao
entre empresas dominava e levou a retirar o modelo da porta. O valor cientifico e ter instrumentado
o produto de modo a descobrir isso, nao insistir no modelo.

### 11. “Como valida a decomposicao se a parcela empresa e definida como resto?”

**Resposta-nucleo:** a soma e apenas uma garantia de implementacao. O R2 da janela informa qualidade
do ajuste, mas nao verdade da atribuicao; sem ground truth, as parcelas sao indicativas e os priors e
o mapa setorial limitam-nas.

### 12. “O sistema escolhe os cinco melhores do dia ou os cinco primeiros que chegam?”

**Resposta-nucleo:** a metrica escolhe offline os cinco melhores; a producao decide online e gasta
quota por chegada, ordenando apenas dentro de cada ciclo. A precisao reportada e um limite superior,
nao desempenho observado da politica implantada.

### 13. “Onde esta a prova de que a explicacao ajuda uma pessoa?”

**Resposta-nucleo:** nao existe e a tese nao a reivindica. Existe prova de fidelidade por construcao
e um estudo humano congelado; utilidade permanece nao medida.

### 14. “Chama valor para o utilizador a uma melhoria num rotulo proxy?”

**Resposta-nucleo:** essa frase deve ser estreitada. O resultado e valor na metrica offline de
materialidade; beneficio para a pessoa exigiria o estudo que nao foi corrido.

### 15. “Qual e afinal a contribuicao original se nao inventou um algoritmo e a QI3 deu nao?”

**Resposta-nucleo:** a contribuicao e o metodo de engenharia verificavel: construir o dataset e a
cadeia, comparar cada decisao com uma alternativa simples, instrumentar a producao, publicar os
negativos e alterar o produto quando a medicao o contradiz. O “nao” da QI3 e evidência desse metodo,
nao ausencia de trabalho.

---

## 6. Alegacoes, numeros e formulas que exigem verificacao ou estreitamento

| Local | Alegacao atual | Diagnostico | Acao |
|---|---|---|---|
| Resumo, p. vii | “Cada componente foi avaliado contra linhas de base” | contradiz a p. 94, que exclui a decomposicao | dizer “sempre que existia um referente adequado” |
| Secao 3.4.4, p. 27 | com `sigma=0`, `z=0` descreve corretamente uma acao parada | falso se hoje houver salto; reproduzido com +5% | corrigir codigo, teste e frase |
| Secao 3.7.2, p. 36 | ruido do beta=1 afeta nivel, nao ordenacao | nao demonstrado | substituir por comparabilidade interna, sem invariancia |
| Tabela 3.1, p. 24 | `ret_event` “nao ve futuro” | verdadeiro ao fecho diario, ambiguo ao instante da noticia | nomear explicitamente o referencial temporal |
| Tabela 4.5, p. 52 | primeiro alerta exige 0.49 | falso com `daily_budget`; reproducao passou a 0.10 | corrigir tabela e materiais derivados |
| Figura 5.6, p. 74 | mostra por setor | falso: grafico agregado P@5/P@10 | substituir a figura ou a frase; melhor substituir |
| Secao 5.5.4 vs pp. 90/92 | QI2 sobre passado resumida com 0.595 | protocolo causal e 0.513 com chao 0.259 | usar 0.513 na sintese; rotular 0.595 como simetrico |
| QI2, pp. 72-75 | ganho sem deduplicacao de historias | sensibilidade nova: 0.514 -> 0.491 | canonizar antes de citar; conclusao sobrevive |
| Secao 5.6.10, pp. 84-85 | `+0.012` e positivo | estatisticamente acima de zero, mas abaixo do criterio pratico 0.02 e sem ganho no orcamento | dizer sempre “pequeno, detetavel e sem efeito de produto” |
| Secao 5.8, p. 89 | “valor mensuravel sobre o que a pessoa ja tinha” | mede proxy offline, nao utilidade | estreitar a “ganho na metrica ponta-a-ponta” |
| Secao 6.3, p. 94 | “nao ha linha de base possivel” na decomposicao | nao ha ground truth, mas ha comparacoes possiveis | corrigir o absoluto |
| Secao 6.4, p. 95 | fontes gratuitas nao dao precos ao minuto | demasiado amplo; o proprio sistema usa intradiario gratuito | dizer “historico intradiario fiavel + timestamp + atribuicao em escala” |
| Alerta/p. 54 | probabilidade calibrada | calibrada na validacao, ~5 pp otimista no teste e sem transferencia ao vivo | qualificar sempre a calibracao |
| QI3, p. 79 | 825 decisoes | apenas 239 unidades empresa-dia independentes | usar 239 ao discutir incerteza; a tese ja o faz |
| Capa e ficheiro tecnico | campos do juri; Type 3; PDF nao tagged | decisao pre-defesa e possivel requisito administrativo, nao falha cientifica | confirmar apenas com secretaria/regulamento antes do deposito |

### O que foi confirmado como limpo

- O PDF tem 134 paginas, metadados corretos, tamanho A4 e fontes incorporadas.
- Nao ha referencias indefinidas, figuras ausentes, sobreposicoes ou paginas visualmente quebradas.
- `check_entrega.py` passa todas as 11 verificacoes; os oito verificadores especializados passam.
- A auditoria existente encontra origem para todos os 246 numeros que reconhece e os 53 valores
  congelados conferem.
- A bibliografia e internamente consistente. As quatro pre-publicacoes ja identificadas sao um risco
  localizado, nao uma bibliografia dominada por fontes fracas.
- Estes controlos provam proveniencia e consistencia mecanica; **nao provam necessidade, validade do
  proxy ou correca interpretacao**, que e onde se concentram os achados deste relatorio.

---

## 7. Plano realista de tres dias

### Dia 1 — fechar a verdade cientifica e tecnica

**Manha**

1. Corrigir Tabela 4.5 e sincronizar a politica da primeira/segunda posicao.
2. Corrigir a frase do beta=1 e a fronteira temporal de `ret_event`.
3. Corrigir `sigma=0` nos tres caminhos do detetor e acrescentar testes de regressao.

**Tarde**

4. Corrigir as sinteses da QI2 para o protocolo causal.
5. Estreitar “valor para a pessoa”, “sem linha de base possivel” e “fontes gratuitas nao dao”.
6. Recompilar do zero e correr suite, ruff, verificadores numericos, referencias, `diff --check` e
   inspecao das paginas afetadas.

**Saida do dia:** nenhuma contradicao direta entre tese, codigo e configuracao; PDF mecanicamente
limpo.

### Dia 2 — tornar a evidencia visivel e sincronizar a defesa

**Manha**

1. Gerar a Figura 5.6 por setor a partir do artefacto existente.
2. Gerar o painel causal vs simetrico e, se a implementacao ficar pequena, canonizar a sensibilidade
   a manchetes repetidas.
3. Traduzir apenas os rotulos dos graficos que vao aparecer na defesa.

**Tarde**

4. Atualizar Figura 6.1, slides, guia e simulacro com os mesmos numeros.
5. Ensaiar as 15 perguntas deste documento, em voz alta, com respostas de 30-60 segundos.
6. Fazer uma passagem visual nas novas paginas e congelar o PDF.

**Saida do dia:** cada conclusao principal tem uma figura que mostra exatamente a afirmacao feita;
nenhum material de estudo ensina um numero antigo.

### Dia 3 — produto, administracao e ensaio final

**Manha**

1. Executar a demonstracao gravada e a verificacao da aplicacao; confirmar que a pagina e os alertas
   correspondem ao que o PDF mostra.
2. Resolver apenas tarefas humanas reais: declaracao de IA, licenca, rotacao de credenciais, campos
   administrativos e regras de deposito.
3. Se e somente se ja existirem oito participantes reais, consentimento e tempo para recolha sem
   pressa, correr o estudo A/B congelado. Caso contrario, nao o simular nem o apresentar como feito.

**Tarde**

4. Fazer dois simulacros completos: um de 15 minutos e outro so de perguntas hostis.
5. Verificar a copia final por hash, abrir o PDF noutro leitor e confirmar links, figuras e fontes.
6. Congelar: nenhuma nova experiencia, refatoracao ou migracao depois desta porta.

**Saida do dia:** um PDF final, uma demonstracao que nao depende da rede, respostas coerentes com o
documento e nenhuma alegacao acrescentada na vespera.

---

## Veredicto final

A tese ja possui a virtude mais dificil de fabricar a tres dias da defesa: mostra onde os metodos
perderam e onde o produto teve de mudar. O trabalho restante nao e “tornar os resultados melhores”.
E fazer com que **cada frase de sintese diga exatamente aquilo que as experiencias mediram**.

As correcoes prioritarias sao poucas e concretas: politica do piso, numero causal da QI2, figura por
setor, fronteira temporal de `ret_event`, inferencia sobre o beta=1 e caso `sigma=0`. Feitas estas, o
risco dominante deixa de ser uma contradicao apanhavel no documento e passa a ser o conjunto de
limitacoes que a propria tese ja sabe defender.
