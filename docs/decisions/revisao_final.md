# Revisão final antes da entrega

> Estado: **parcial**. Tudo o que está aqui foi verificado por mim contra o ficheiro, o PDF
> compilado ou os dados. A validação das citações contra os PDFs originais das fontes está a
> correr em separado e entra numa segunda parte deste documento.
>
> Cada achado traz **gravidade**, e a classificação distingue o que é **erro** do que é
> **preferência estilística**. Nada foi alterado: isto é para decidires.

---

## A. Crítico: impede a entrega tal como está

### A1. A capa imprime `[A definir]` no júri

| | |
|---|---|
| **Local** | `main.tex:77-78`, sai impresso na **página 1** do PDF |
| **Problema** | A capa mostra `Júri: Presidente: [A definir]` e `Vogais: [A definir]` |
| **Gravidade** | **Crítica** |
| **Justificação** | É a primeira coisa que um avaliador vê. Um marcador de posição na capa lê-se como documento não terminado, independentemente da qualidade do resto |
| **Proposta** | Preencher com os nomes reais quando forem conhecidos. Se não forem conhecidos à data de entrega, confirmar com o orientador se o campo deve ficar vazio ou ser removido; muitos regulamentos preveem a capa sem júri na versão de entrega |
| **Evidência** | `pdftotext -f 1 -l 1 main.pdf` devolve `Presidente: [A denir]` |

### A2. A data é gerada automaticamente, não é a data de entrega

| | |
|---|---|
| **Local** | `main.tex:82` (`\thesisdate{Porto, \today}`) e `frontmatter.tex:47` (declaração) |
| **Problema** | Ambas imprimem a data de compilação. Hoje sai "18 de agosto de 2026" |
| **Gravidade** | **Crítica** |
| **Justificação** | A data da declaração de integridade é um elemento formal. Se recompilares noutro dia, muda sozinha, e pode ficar diferente da data de submissão |
| **Proposta** | Substituir `\today` pela data de entrega, nos dois sítios |
| **Evidência** | Página 1 e página iii do PDF |

---

## B. Importante: afeta rigor, coerência ou credibilidade

### B1. O mesmo leitor tem quatro nomes ao longo da tese

| | |
|---|---|
| **Local** | Título e `cap1:128` usam "investidor(es) de retalho"; o corpo usa "investidor particular" (1), "investidores particulares" (2), "pequeno investidor" (1), "não profissional" (1) |
| **Problema** | Quatro designações para a mesma pessoa, e a que está no **título** é a que menos aparece no corpo: **zero** ocorrências de "investidor de retalho" fora do título e de uma linha do Cap. 1 |
| **Gravidade** | **Importante** |
| **Justificação** | Terminologia inconsistente é das coisas que um arguente nota primeiro, e aqui agrava-se por a inconsistência começar no título |
| **Proposta** | Escolher **uma** e usá-la em todo o lado. Recomendo **"investidor particular"**: é natural em PT-PT europeu, é o que a imprensa financeira portuguesa usa, e já aparece no corpo. Mencionar uma vez, no Cap. 1, que corresponde ao "investidor não profissional" da regulamentação, e usar "particular" daí em diante |
| **Evidência** | Contagens sobre `cap*/capitulo*.tex` e `main.tex:71` |

### B2. "manchete" e "título" designam a mesma coisa, e coexistem

| | |
|---|---|
| **Local** | "manchete/manchetes" **83 ocorrências**; "título" **19**, para o mesmo conceito |
| **Problema** | Em PT-PT europeu, *manchete* designa especificamente o título de destaque da primeira página de um jornal. A maioria das notícias que o sistema lê não são manchetes nesse sentido: são títulos de notícia. E a tese **já usa "título"** para o mesmo conceito, incluindo numa frase central: *"O sistema lê o título e não o corpo do artigo"* |
| **Gravidade** | **Importante** |
| **Justificação** | Não é só naturalidade da língua. "Título" é **tecnicamente mais preciso** para o argumento que a tese faz, que é o de ler apenas o título e não o corpo. "Manchete" enfraquece essa distinção |
| **Proposta** | Uniformizar em **"título"**, com "título da notícia" na primeira ocorrência de cada capítulo onde o contexto possa ser ambíguo. ⚠️ **Ressalva que pesa**: em finanças, "título" também significa *valor mobiliário*. A tese usa-o 19 vezes sem ambiguidade porque o contexto é sempre de notícia, mas com 83 substituições esse risco cresce. Se quiseres evitá-lo por completo, a alternativa é fixar **"título da notícia"** e aceitar a repetição |
| **Evidência** | `grep` sobre o corpo; `cap6` contém "O sistema lê o título e não o corpo do artigo" |

### B3. SHAP e BERT aparecem sem expansão e não estão na lista de acrónimos

| | |
|---|---|
| **Local** | `cap2:495, 510, 534` (SHAP); `cap2:333, 337`, `cap4:149` (BERT) |
| **Problema** | Aparecem em texto corrido sem nunca serem expandidos, e a Lista de Acrónimos impressa **não os contém** |
| **Gravidade** | **Importante** |
| **Justificação** | Um leitor do júri sem fundo em aprendizagem automática encontra "SHAP" sem qualquer pista do que significa, e não tem onde o procurar |
| **Proposta** | Expandir na primeira ocorrência: "SHAP (*SHapley Additive exPlanations*)" e "BERT (*Bidirectional Encoder Representations from Transformers*)". Alternativa equivalente: usar `\gls{}`, que os faz entrar na lista automaticamente |
| **Evidência** | A Lista de Acrónimos (PDF p. 21) tem exatamente 6 entradas: API, CI, CSV, FNSPID, JSON, QI |

### B4. O título contém um termo que a tese não usa

| | |
|---|---|
| **Local** | `main.tex:71` |
| **Problema** | O título termina em "para o investidor de retalho", expressão ausente do corpo (ver B1). Além disso "alertas de **mercado**" pode ler-se como cobrindo apenas o gatilho de preço, quando o sistema tem dois e o de notícias é o mais desenvolvido |
| **Gravidade** | **Importante** |
| **Justificação** | O título é a primeira promessa que o documento faz. Deve usar o vocabulário do próprio trabalho e representar o que ele cobre |
| **Proposta** | Ver secção **E** abaixo, com alternativas |
| **Evidência** | Contagens de terminologia; `cap1` e `cap4` descrevem dois gatilhos |

### B5. Declaração de utilização de IA

Este é o único ponto do teu pedido em que a minha resposta não é a que pediste, e prefiro
dizê-lo de forma direta.

Pediste que a declaração deixasse de apresentar a IA como responsável pela redação, e que
declarasse apenas apoio técnico em código, LaTeX e gráficos.

**Não posso propor essa alteração, porque tornaria a declaração falsa.** Parte substancial da
prosa deste documento foi escrita e reescrita com assistência de IA, incluindo a maior parte do
Capítulo 2, a técnica da decomposição no Capítulo 3, a secção 5.4, e vários parágrafos de
discussão no Capítulo 6. Uma declaração que descrevesse isso como "apoio pontual em sintaxe
LaTeX e gráficos" não corresponderia ao processo real, e é precisamente o tipo de afirmação que
o resto da tese existe para recusar.

**O que posso fazer, e que responde à tua preocupação legítima:** a declaração atual é
efetivamente longa e algo dispersa, e a frase sobre responsabilidade é redundante. Uma versão
mais precisa e mais curta, que continua verdadeira:

> **Uso de Inteligência Artificial.** Em conformidade com as orientações do P.PORTO/ISEP,
> declaro que utilizei ferramentas de inteligência artificial generativa no desenvolvimento
> deste trabalho: na escrita e reestruturação de código e testes, na implementação dos
> procedimentos de avaliação, e na redação e edição de texto deste documento.
>
> A conceção do trabalho é minha: o problema, as questões de investigação, as restrições que
> definem o sistema, e as decisões sobre o que construir, manter ou descartar. Revi o conteúdo
> deste documento e assumo a responsabilidade por ele.

Isto corta cerca de um terço da extensão, elimina a frase redundante sobre responsabilidade
intelectual, e mantém-se verdadeira.

⚠️ **Passo que depende de ti:** confirmar com o Prof. Luís Gomes a redação exata que a MEIA/ISEP
exige. Se a instituição tiver fórmula própria, é essa que vale, e esta proposta é substituída.

---

## C. Menor: corrigir se houver tempo

| # | Local | Problema | Proposta |
|---|---|---|---|
| C1 | `frontmatter/glossary.tex` | **14 dos 20 acrónimos declarados nunca são usados** (AI, BERT, HTTP, ML, NASDAQ, NLP, NYSE, OHLCV, ONNX, RSS, SBERT, SHAP, SIFMA, XAI). Não afeta o leitor, porque a lista só imprime os usados, mas são declarações mortas | Apagar as não usadas, ou passar a usar as que fazem falta (ver B3) |
| C2 | Lista de Acrónimos, PDF p. 21 | Mistura línguas nas expansões: "API Interface de Programação de Aplicações" está traduzido, "CSV Comma-Separated Values" e "JSON JavaScript Object Notation" não | Uniformizar. Recomendo manter em inglês os que são nomes próprios de formatos (CSV, JSON, FNSPID) e traduzir os restantes, indicando o original entre parênteses |
| C3 | Cap. 3 e 5 | 6 equações rotuladas e nunca invocadas por `\ref` (`eq:platt`, `eq:precisao`, `eq:cobertura`, `eq:f1`, `eq:patk`, `eq:brier`) | Inofensivo. Só mexer se quiseres numeração limpa, usando `equation*` nas que nunca são citadas |
| C4 | `frontmatter.tex:52` | Dedicatória "À minha família." | Ver secção **F** |

---

## D. As caixas alaranjadas: resposta à tua pergunta

Perguntaste se eram notas internas a remover. **Não são.** São cinco, e todas contêm conteúdo
deliberado, nomeadamente os achados mais fortes da tese:

| Local | O que contém |
|---|---|
| `cap3:782` | Porque é que o modelo não distingue duas notícias da mesma empresa |
| `cap4:601` | O ciclo de aprendizagem parado dezanove dias |
| `cap5:752` | **"Um aviso sobre a primeira linha"**, que é a que te levantou a dúvida |
| `cap5:844` | O achado dos 84% |
| `cap5:878` | A pontuação quase constante por empresa |

A de `cap5:752` refere-se à **primeira linha de uma tabela**, não a uma nota de trabalho: avisa
que o valor 0.163 dessa linha mede ordenação alfabética e não escolha ao acaso.

**Recomendação:** manter as cinco. São o que distingue esta tese de um relatório, porque expõem
erros próprios em destaque em vez de os enterrarem.

**Preferência estilística, não erro:** caixas com moldura laranja são mais comuns em manuais do
que em dissertações. Se preferires um registo mais sóbrio, muda a cor para cinzento neutro e
mantém o conteúdo. Não é um defeito.

---

## E. Título: avaliação e alternativas

**Atual:** *"Explicar sem prever: alertas de mercado com evidência verificável para o investidor
de retalho"* (95 caracteres).

**Comprimento:** dentro do intervalo das quatro dissertações aprovadas (56 a 121 caracteres).

**"InvestiGator" no título? Não.** Nenhuma das quatro aprovadas nomeia o produto. Um nome com
trocadilho no título convida o júri a comentar o trocadilho em vez do trabalho. O sítio dele é o
Capítulo 4, onde já está.

| # | Alternativa | Vantagens | Desvantagens |
|---|---|---|---|
| **1** | Explicar sem prever: alertas financeiros com evidência verificável para o **investidor particular** | Muda só duas palavras. Corrige a terminologia (B1) e o enviesamento para o gatilho de preço (B4). Mantém o que já funciona | Continua com 94 caracteres |
| 2 | Explicar sem prever: alertas financeiros com evidência verificável | Mais curto (66) e mais memorável | Perde o público, que é parte da contribuição |
| 3 | Alertas financeiros explicáveis para o investidor particular: mostrar o que aconteceu sem prever o que virá | Descritivo, na forma do Bruno e do Helder | 106 caracteres e o subtítulo é pesado |
| 4 | Deteção e explicação de movimentos de mercado com evidência verificável | Registo neutro e muito académico | Perde "explicar sem prever", que é a frase que se fixa, e perde o público |

**Recomendação: a 1.** É a alteração mínima que resolve os dois problemas identificados.
"Explicar sem prever" é o melhor activo do título: é curto, é memorável, e enuncia a restrição
fundadora do trabalho. Não vale a pena perdê-lo.

---

## F. Dedicatória: alternativas

"À minha família." é curta, mas curta não é defeito: é a forma mais comum numa dissertação, e
os agradecimentos já desenvolvem. Se quiseres algo ligeiramente mais pessoal, sem transformar
isto num segundo capítulo:

1. *À minha família.* (atual, e perfeitamente adequada)
2. *Aos meus pais, e à minha família.*
3. *À minha família, que nunca me perguntou quando é que isto acabava.*
4. *À minha família, pela paciência de todos os fins de semana que isto levou.*

A 3 e a 4 têm tom pessoal e leve. Escolhe pela verdade, não pelo efeito: uma dedicatória que
não corresponde à tua experiência nota-se.

---

## G. O que continua por verificar

> Actualizado a 2026-08-19. A lista de PDFs em falta que estava aqui **estava desactualizada**:
> puseste 55 na pasta e já só faltam os que estão em baixo.

| Item | Estado |
|---|---|
| PDFs das fontes | **55 na pasta.** O verificador confirma que **51 são mesmo o artigo que o nome diz** |
| Fontes citadas com PDF | **54 de 61** |
| Citações validadas contra o original | Feita para as que tinham PDF na altura. As secções I a L deste documento são o resultado |
| Estudo com utilizadores | Não existe, e está declarado em cinco sítios da tese |
| Red team da guarda | 4 das 6 lentes nunca correram, e a tese diz que a força medida é um limite inferior |

**Os 4 que o verificador assinala, e nenhum é um artigo errado:**

| Chave | O que se passa | O que fazer |
|---|---|---|
| `fama1969adjustment` | PDF é digitalização, sem texto que se possa extrair | Nada. Não é erro: só não dá para verificar por máquina |
| `fama1970efficient` | O mesmo | Nada |
| `niculescu2005calibration` | O mesmo | Nada. Esta foi lida por mim e é a origem do achado I1 |
| `mikolov2013word2vec` | O PDF é o *Efficient Estimation*, e a entrada passou a ser o **NIPS 2013** | **Trocar o PDF.** Ver abaixo |

**Três descarregamentos, e são os únicos que faltam.** Todos gratuitos e sem conta:

| Chave | Onde | Porquê |
|---|---|---|
| `mikolov2013word2vec` | `proceedings.neurips.cc/paper_files/paper/2013/file/9aa42b31882ec039965f3c4923ce901b-Paper.pdf` | A entrada deixou de ser a pré-publicação e passou a ser as actas |
| `liu2020finbert` | `ijcai.org/proceedings/2020/622` | Entrada nova, revista por pares |
| `huang2023finbert` | Wiley, *Contemporary Accounting Research* 40(2) — pode exigir a conta do ISEP | Entrada nova, revista por pares |

**As sete fontes sem PDF**: quatro delas são páginas web e não artigos (Gallup, SIFMA, CCAF,
Robinhood, Google Finance). Para essas o PDF não é o artefacto certo, e já foram verificadas
contra a página do próprio fornecedor com a data de observação registada.

---

## H. Um ponto que só tu podes confirmar

Nos agradecimentos escreveste, sobre os colegas da Sistrade, *"pelas opiniões e pelo feedback
que foram dando sobre a aplicação"*.

Isto não é um erro, e é diferente de um estudo com utilizadores. Mas a tese afirma em cinco
sítios que **não houve avaliação com pessoas**. Um arguente atento pode juntar as duas coisas e
perguntar. Confirma que a frase corresponde a conversas informais e, se quiseres fechar a porta
por completo, basta dizer "pelo interesse e pelas conversas sobre a aplicação".

---
---

# Parte 2: citações validadas contra os PDFs originais

> **Método.** Seis lentes abriram os **14 PDFs originais** em `docs/decisions/citation_pdfs/`,
> localizaram cada ocorrência da chave no corpo da tese, leram a frase inteira e confrontaram-na
> com o texto do artigo. Toda a evidência abaixo é **verbatim, com número de página**.
>
> **25 achados.** O crítico foi verificado por mim directamente no PDF; os restantes são
> relatados com a citação exacta, que podes conferir.
>
> ⚠️ **Cobertura incompleta:** 6 das 12 lentes morreram no limite de gasto, e eram as dos
> **dados**, **escrita**, **figuras** e **conteúdo**. Ver secção N.
>
> ⚠️ **Boa parte destes achados são meus**, introduzidos nesta sessão ao expandir o Capítulo 2.

---

## I. CRÍTICO: uma fonte citada argumenta contra a escolha que sustenta

### I1. Niculescu-Mizil e Caruana dizem que a regressão logística já está bem calibrada

| | |
|---|---|
| **Local** | `cap2:589-596`, com eco em `cap3:838`, `cap4:501`, `cap5:664` |
| **Problema** | A tese afirma que as pontuações em bruto estão "tipicamente mal calibradas" e que a calibração corrige isso, citando `niculescu2005calibration`. **A fonte diz o contrário exactamente para a família que a tese implanta.** O modelo implantado é, nas palavras do próprio Cap. 6, "uma regressão logística calibrada" |
| **Gravidade** | **Crítica** |
| **Evidência** | p. 631, verificado por mim no PDF: *"For learning methods that make well calibrated predictions such as neural nets, bagged trees, and **logistic regression**, neither Platt Scaling nor Isotonic Regression yields much improvement in performance even when the calibration set is very large. With these methods calibration is not beneficial, and actually hurts performance when the calibration sets are small."* |
| **Justificação** | É o trabalho canónico do tema. Um arguente que o conheça pergunta porque é que ele é citado a apoiar o oposto do que conclui, e a tese, como está, não tem resposta no texto |

### I2. E a preferência por Platt invoca um regime de dados que não é o desta tese

| | |
|---|---|
| **Local** | `cap2:592-596` |
| **Problema** | A tese justifica preferir a sigmoide à isotónica dizendo que a isotónica precisa de mais dados. A fonte quantifica esse limiar em **cerca de 1000 casos** e diz que **acima dele a isotónica iguala ou supera sempre a Platt**. O conjunto tem 79 753 linhas |
| **Gravidade** | **Importante** |
| **Evidência** | p. 631, verificado por mim: *"When there are 1000 or more points in the calibration set, Isotonic Regression always yields performance as good as, or better than, Platt Scaling."* |

### A correção destes dois torna a tese MAIS forte, e o material já existe

O projeto **já mediu isto**. O ficheiro `docs/evaluation/calibration_platt_vs_isotonic.md` conclui:

> "Mesmo com validação farta, o cenário teoricamente favorável à isotónica
> (`niculescu2005calibration`), a flexibilidade extra não paga: no Brier a Platt ganha ou empata
> em todas as 5 famílias. A escolha de Platt fica validada **empiricamente**."

E essa medição **já está na tese**, na tabela de alternativas do Cap. 5. Ou seja: a tese tem a
prova certa e, no Capítulo 2, apoia-se na autoridade errada.

**Proposta.** Reescrever a passagem do Cap. 2 para dizer o que a fonte conclui, e mudar a
justificação de autoridade para medição:

> A calibração a posteriori sobre um bloco reservado corrige essa distorção
> `\autocite{niculescu2005calibration}`. Convém registar o que a mesma fonte conclui, e que não
> favorece a escolha feita aqui: a regressão logística é apontada como já bem calibrada à
> partida, e acima de cerca de mil casos de calibração a regressão isotónica iguala ou supera a
> sigmoide. O modelo implantado é uma regressão logística e o bloco de validação está muito
> acima desse limiar, pelo que a calibração não se justifica aqui por autoridade, mas por
> medição: a Secção `\ref{sec:av_alternativas}` compara as duas na mesma validação e a sigmoide
> ganha ou empata no Brier em todas as famílias testadas.

É o mesmo movimento que a tese já faz noutros sítios, e num caso em que a medição lhe dá razão
contra a teoria. É material para a defesa, não um problema a esconder.

---

## J. Importantes: a fonte não sustenta o que a frase afirma

| # | Local | Problema | Evidência verbatim |
|---|---|---|---|
| **J1** | `cap2:417-419` | "os procedimentos **mais simples** se comportam bem" atribui a Brown e Warner uma conclusão que eles recusam: o artigo conclui a favor do modelo de mercado por mínimos quadrados e identifica o mais simples (*Mean Adjusted Returns*) como perdendo potência e ficando **mal especificado** sob concentração de datas | p. 26: *"Market Adjusted Returns and the OLS market model also outperform a simpler Mean Adjusted Returns procedure, which has low power in cases involving event-date clustering."* Tabela 5: rejeição de **13.6%** a um nível nominal de 5% |
| **J2** | `cap2:162-164` | O contraste com os *robo-advisors* ("agem por o investidor, com lógica proprietária") leva a citação **dentro da frase**, e a fonte afirma o contrário nos dois elementos | p. 8: *"the requirement that the investor ultimately authorizes any trade confers the investor complete control"*; p. 7: *"Robo-advisers are also transparent."* |
| **J3** | `cap5:442` | A frase diz que a taxonomia de Chandola coloca o *Isolation Forest* fora da família estatística. **Chandola nunca menciona o Isolation Forest** | Zero ocorrências de "isolat" nas 58 páginas |
| **J4** | `cap2:270`, `cap6:35` | Atribui a Engle 1982 uma constatação sobre **mercados**. Engle 1982 estuda a **inflação no Reino Unido** | Resumo, p. 987: *"This model is used to estimate the means and variances of inflation in the U.K."* |
| **J5** | `cap2:261`, `cap6:166` | "em finanças a deteção é **dominada** por métodos não supervisionados", apoiado em Ahmed. O artigo é um levantamento de **deteção de fraude**, e nunca quantifica prevalência | p. 278: *"an in-depth survey of various clustering based anomaly detection technique"*; p. 287: *"in the domain of fraud detection"* |
| **J6** | `cap2:451-454` | "É exactamente o que a terceira técnica faz" afirma correspondência total com o ciclo de CBR. A fonte descreve **quatro** processos e diz que os quatro são necessários; o sistema faz dois e pára antes de rever e adaptar, de propósito | p. 42: o ciclo *retrieve, reuse, revise, retain*; p. 43: *"All the four tasks are necessary"* |

---

## K. Menores

| # | Local | Problema |
|---|---|---|
| K1 | `cap3:665-667` | O estudo de evento é atribuído a Brown e Warner com uma só referência. Eles **avaliam** metodologias existentes; o trabalho primário é Fama, Fisher, Jensen e Roll (1969), que o Cap. 2 já credita bem |
| K2 | `cap1:115-118`, `cap2:440-442`, `cap6:47` | A hipótese dos mercados eficientes está com a **condicional invertida**: apresenta como consequência da previsibilidade aquilo que é a premissa que a exclui |
| K3 | `cap1:24`, `cap2:88-89` | "os **principais** captadores de atenção". Barber e Odean apresentam-nos como *proxies imperfeitos* e dizem que a atenção pode ser captada por outras vias |
| K4 | `cap2:57-58` | "ela compra a seguir" converte um desequilíbrio **agregado** num comportamento individual, que os autores rejeitam: *"each investor does not buy every single stock that grabs his attention"* |
| K5 | `cap2:160-162` | "melhoria da diversificação" sem condição. O resultado é **heterogéneo**: melhora para quem tinha menos de 5 ações, quase não altera acima de 10 |
| K6 | `cap2:26-29` | "reforçaram posições" atribui o aumento a investidores existentes. A fonte ressalva que os dados não permitem separar isso de investidores **novos** |
| K7 | `references.bib` | Os PDFs de `welch2022robinhood` e `dacunto2019robo` são **pré-publicações** (NBER WP 27866; SSRN 3122577), não as versões que o `.bib` declara |
| K8 | `cap3:243` | A glosa da família estatística de Chandola acrescenta "**recente**", que não está na definição da fonte: é a opção de janela deslizante deste trabalho |
| K9 | `cap2:593-594` | "**não consegue** sobreajustar" afirma impossibilidade. A fonte descreve um mecanismo criado para evitar esse sobreajuste, logo o risco existe |
| K10 | `cap2:604-612`, `cap6:299-310` | A cobertura marginal é dada como razão para não adoptar a predição conformal. O livro citado documenta que a **validade condicional pode ser obtida** modificando a definição |

---

## L. Sugestões, que não são erros

| # | Local | Sugestão |
|---|---|---|
| L1 | `cap2:40-47` | Barber e Odean fecham com a conclusão **normativa** que falta e que justifica a tese: *"The attention-driven buying patterns we document here do not generate superior returns."* |
| L2 | `cap2:40-47` | A base empírica é de **1991 a 1999**, e a tese aplica a conclusão ao investidor de hoje sem registar o período |
| L3 | `cap2:159` | A mesma fonte lista alertas em reação a notícias como capacidade dos *robo-advisors*, o que enfraquece o "respondem a outra pergunta" |
| L4 | `cap3:837-838` | A forma sigmoide é de **Platt (1999)**; a fonte citada é a avaliação dela. A tese usa o nome no rótulo e na tabela, mas nunca em prosa |
| L5 | `cap2:452-453` | A fonte escreve *"instead of relying **solely** on general knowledge"*, e o "solely" não é acessório |
| L6 | `cap6:50-53` | "os **seus** testes são sempre conjuntos" é ambíguo: a afirmação da fonte é que **qualquer** teste de eficiência é conjunto |

---

## N. O que esta revisão NÃO cobriu

6 das 12 lentes morreram no limite de gasto:

| Dimensão | Estado |
|---|---|
| Dados dos Caps. 3 e 4 | Não coberto por agente. Cobri em parte: 34/34 números batem com a fonte, e os 15 valores repetidos entre capítulos são coerentes |
| Dados dos Caps. 5 e 6 | Não coberto por agente. Mesma cobertura parcial |
| Terminologia | Cobri na Parte 1, secções B1 e B2 |
| Registo e escrita | Não coberto. Medi só o comprimento de frase |
| Figuras e tabelas | Não coberto por agente. Verifiquei órfãos e tipos de referência |
| O que falta e o que sobra | Não coberto |

As **46 referências sem PDF local** continuam por validar contra o original.
