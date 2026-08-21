# Revisão profunda da tese — notas, erros e plano (2026-08-21)

> **O que isto é.** Uma passagem à tese curta (`tese/`, 127 pp) do princípio ao fim, com seis
> lentes. Traz três coisas separadas de propósito: **o que estava errado e já está corrigido**,
> **o que ficou por decidir e é teu**, e **o que verifiquei e estava limpo** — esta última para
> ninguém voltar a gastar tempo lá.

---

## 0. Como foi feito, e o que correu mal no método

Lancei seis lentes independentes em paralelo, cada uma com um céptico obrigado a reproduzir o
achado antes de o confirmar.

⚠️ **Sete dos nove agentes morreram no limite de sessão**, e entre eles **os dois cépticos**.
Completaram-se duas lentes (coerência e afirmações) e nenhuma verificação. É a **11.ª vez** que
este padrão morde neste projecto, e a lição registada no `CLAUDE.md` voltou a valer: uma corrida
assim devolve achados de aparência limpa que **ninguém verificou**.

**Verifiquei os 18 achados eu próprio**, um a um, contra os ficheiros. Onze confirmaram-se, e as
severidades que os agentes deram estavam por vezes inflacionadas. As quatro lentes que não
correram (estrutura contra as teses aprovadas, escrita, figuras renderizadas, arguente hostil)
ficam por fazer — estão no plano, no ponto 3.

A isso juntei uma passagem mecânica minha, que os agentes fazem mal: contagens de página por
capítulo, avisos do compilador, distância entre cada figura e o texto que a invoca, páginas quase
vazias, acrónimos, e bibliografia.

---

## 1. Erros encontrados e **já corrigidos**

### 1.1 ⚠️ [ALTA] A tabela de consulta não é «o melhor preditor que existe» — e a afirmação era minha, de ontem

A medição nova da §5.6.10 soma o texto **por cima** da tabela de consulta por empresa, e eu
descrevi essa tabela como *«o melhor preditor conhecido»*. **Não é.** Na PR-AUC, que é a métrica
exacta onde o acréscimo de `+0.012` é medido, a tabela da própria §5.6.9 diz:

| modelo | PR-AUC |
|---|---|
| Só volatilidade | **0.542** |
| Tabela de consulta por empresa | 0.534 |

A volatilidade está **0.008 acima**. Um arguente que abra a tabela na página anterior encontra a
contradição.

**Porque é que a razão verdadeira é melhor do que a que eu tinha escrito:** a tabela de consulta
é a base certa para esta pergunta não por ser a melhor, mas porque **contém tudo o que o modelo
sabe sobre a empresa e nada sobre a notícia** — é isso que faz o acréscimo isolar a contribuição
do texto. Reescrito assim, e a tese passa a dizer em voz alta que a volatilidade fica acima dela,
que é exactamente a razão de existir a segunda linha da tabela dos intervalos.

Corrigido em **nove sítios**: Cap. 5 (×5), Cap. 6, apêndice, guia de estudo (×2).

### 1.2 ⚠️ [ALTA] «Dois modelos específicos de finanças» — foi medido um

O §4.9.1, que é onde o trabalho defende o que é contribuição própria, dizia ter comparado o
codificador *«contra quatro alternativas, incluindo dois modelos específicos de finanças que
perderam»*. A fonte (`evaluation_retrieval_embedders.md`) mede quatro alternativas — MPNet,
FinBERT, E5 e BGE — e **só o FinBERT é de domínio**. O próprio Cap. 4, 789 linhas antes, escreve
*«um modelo específico de finanças»*.

Passa a nomear a composição real: um modelo maior, dois codificadores mais recentes, e um
específico de finanças, que foi o pior de todos.

### 1.3 [MÉDIA] Três descrições erradas no §1.5, todas na mesma frase

O inventário dos estudos de caso, no fim da introdução, prometia:

| dizia | e é |
|---|---|
| «o funil de decisões de **um dia inteiro**» | a legenda da Tabela 4.5 diz explicitamente *«é parte de um dia e não o dia inteiro»* |
| «uma empresa cujo preço quase não se moveu enquanto **duas forças se anulavam**» | a figura foi recapturada ontem: agora é o **setor sozinho** a puxar (−0.56%), com mercado e empresa ambos em alta |
| «o Cap. 3 segue **uma mesma notícia** pelas três formas» | duas das três figuras são de 2020-03-09 e a do meio é de 2023-02-02 |

As três estavam a mandar o leitor conferir coisas que não estão lá. A segunda é staleness minha:
recapturei a figura ontem e não actualizei o ponteiro.

### 1.4 [MÉDIA] O resumo dizia «treinado em 79 753 exemplos»

79 753 é o conjunto **inteiro**. O treino são **28 574**; o resto é validação (17 710), teste
(32 649) e embargo (820) — números que o próprio Cap. 3 dá. Passa a «construído sobre um conjunto
de 79 753 exemplos», nas duas línguas.

### 1.5 [MÉDIA] «Uma página web onde **tudo** o que foi enviado pode ser consultado»

O `/api/alerts` serve `[-200:]`, ou seja os últimos 200 de 424. Corrigido para não dizer «tudo».

### 1.6 [MÉDIA] Um número não determinístico do lado determinístico da tabela

A tabela do apêndice divide-se em duas metades, e a de cima promete que *«correr outra vez sobre
os mesmos dados devolve exactamente os mesmos valores»*. A linha das **decisões maturadas em
produção** estava lá — e o Cap. 5 diz que ela mudou de 530 para 825 quando o registo foi relido.
Movida para a metade das medições sobre a operação, que é onde pertence.

### 1.7 [MÉDIA] Faltava um resultado à tabela que diz reunir todos

A recuperação sob a restrição da produção (§5.5.4, `0.513` com chão `0.259`) é um resultado
reportado e não estava na tabela do apêndice. Acrescentada.

### 1.8 [MÉDIA] O fecho do Cap. 6 contava só as vitórias

O último parágrafo — a última coisa que o júri lê — dizia *«acabo-o com três medições a dizer o
contrário»*, contando as três vezes em que a técnica simples ganhou. Omitia as **duas** em que a
alternativa mais sofisticada ganhou e o sistema ficou com a simples por explicabilidade (a janela
de 60 dias, `F₁ 0.678`, e o desvio-padrão com pesos que decaem, `0.664`). O Cap. 5 reporta-as com
todo o cuidado; a conclusão selecionava. Passa a dizer as duas, e a distinguir **escolha** de
**resultado** — que é a distinção que o resto do documento faz bem.

### 1.9 [MÉDIA] Sete tabelas do Cap. 4 saíam treze páginas depois do texto

Medido: as tabelas eram citadas nas páginas 44–47 e o LaTeX empurrava-as todas para 57–59. As
figuras saíam no sítio; a fila das tabelas entupia. O leitor do capítulo central — o que segue uma
notícia do princípio ao fim — tinha a tabela de cada etapa treze páginas à frente. Corrigido com
`[!htbp]`; agora saem na página onde são citadas.

### 1.10 [MÉDIA] Duas páginas com duas linhas cada, e uma promessa lógica que não se cumpria

O Cap. 2 e o Cap. 4 acabavam com duas linhas órfãs numa página só delas. A do Cap. 2 tinha causa
de conteúdo: o parágrafo final **repetia** o que a lista quatro linhas acima já dizia («em vez de
algo que se compra» / «uma capacidade comprada»). Cortada a repetição, a página desapareceu.

No Cap. 4, a subsecção abria com *«Duas coisas, e ambas são consequência de uma só causa»* — e o
primeiro item diz explicitamente que a sua causa é outra («o que impede não é a técnica»). A
promessa de causa comum não se cumpria. Corrigida.

### 1.11 [BAIXA] Duas legendas minhas que prometiam mais do que a tabela

Escritas ontem, as duas: a da Figura 4.1 prometia «as quatro técnicas» mostrando três, e a da
Tabela 4.5 prometia «as portas que têm uma constante associada» quando a primeira linha não tem
nenhuma. Ambas corrigidas.

### 1.12 [BAIXA] O guia ensinava um σ que a tese já tinha corrigido

O guia de estudo dava `σ = 2,73%` no exemplo da Tesla; a tese diz `2.72%` desde a sessão 60. Ele
estuda por ali.

### 1.13 [BAIXA] `Float too large for page by 41.6pt`

A figura das duas capturas da página empurrava a legenda para a linha do número de página. Não é
erro, é aviso, e só se vê a renderizar. Larguras apertadas; o aviso desapareceu.

---

## 2. Encontrado, **não corrigido** — precisa da tua decisão

### 2.1 A recomendação do coorientador não está citada na tese

O `worldmonitor2026` está no `.bib`, verificado, e **nunca é citado**. O `CLAUDE.md` regista que
foi o **Rafael Silva** quem recomendou aquele produto, e que a ideia adaptada foi a **convergência
multi-sinal** — que a tese implementou, mediu, e rejeitou honestamente (ganha em 1 de 3
orçamentos, e está na tabela das alternativas do Cap. 5).

Ou seja: a experiência está lá, o resultado negativo está lá, e **não há indicação de onde veio a
ideia**. Isso não é só uma lacuna de atribuição — subestima o teu envolvimento com a supervisão.
Uma oração na linha da tabela resolve.

⚠️ **Não o fiz porque é uma decisão tua**: creditar uma sugestão do coorientador no corpo do
documento é uma escolha que te pertence, não a mim.

### 2.2 O resumo diz que o sistema «explica o que já aconteceu», e o alerta traz um número para a frente

O alerta termina em *«57% chance of an unusually large move over the next few days»*. A tese
**sabe** e trata disto muito bem no Cap. 4 (*«é o único número da mensagem que olha para a
frente»*) e o código tem a distinção materialidade/direção escrita no `docstring`. Mas os resumos
comprimem para «explica o que já aconteceu», e a figura do alerta real, cinquenta páginas depois,
mostra a percentagem.

**Não é desonestidade** — é compressão. Mas é a pergunta que um arguente faz, e a resposta que já
tens é excelente. **Proposta:** ~15 palavras no resumo a nomear esse número e a sua moldura. Custo
nulo, e transforma uma armadilha em prova de cuidado.

Deixei por fazer porque mexer no resumo é decisão de autor.

### 2.3 Achados que ficaram por verificar

Três, todos de severidade média ou baixa, que não confirmei por falta de tempo de sessão:

- o Cap. 6 afirma correspondência **linha a linha** entre as cinco primeiras linhas do trabalho
  futuro e as limitações — exige contar contra a Figura 6.2;
- o resumo diz que as decisões foram avaliadas uma segunda vez e **não diz o resultado**;
- o veredicto da QI2 cita só os números do protocolo que podia ver o futuro, sem a ressalva
  causal que a §5.5.4 acrescentou.

---

## 3. O que **não foi verificado** e vale a pena fazer a seguir

As quatro lentes que morreram. Por ordem de valor:

| # | lente | porque vale | custo |
|---|---|---|---|
| 1 | **Arguente hostil** | é a única que produz as perguntas da defesa a partir de frases concretas | 1 sessão |
| 2 | **Figuras renderizadas** | ~30 figuras, e três dos defeitos de ontem só apareceram a olhar | 1 sessão |
| 3 | **Estrutura contra as 4 teses aprovadas** | responde a «falta-nos alguma secção que elas têm?» | meia sessão |
| 4 | **Escrita e registo** | o `check_escrita` cobre parte; frases-comboio e repetições não | meia sessão |

⚠️ **Correr isto de madrugada ou com o limite reposto** (repõe às 2h, hora de Lisboa). E manter os
cépticos: sem eles, a corrida devolve achados por confirmar, que é pior do que não a correr.

---

## 4. O que verifiquei e **estava limpo** — não repetir

- **Bibliografia:** 63 chaves citadas, 0 sem entrada, 0 órfãs no output. As 4 entradas não citadas
  são do `.bib` partilhado com as teses longas e não são impressas.
- **Acrónimos:** 0 usados sem definição. Os 13 definidos e nunca usados **não são impressos**; o
  `BERT` e o `AI` que aparecem em texto simples são, respectivamente, nome de modelo com citação e
  texto dentro de um título citado em inglês. Nenhum defeito.
- **Referências cruzadas:** 0 labels duplicados, 0 indefinidas, 0 avisos do LaTeX além do que já
  foi corrigido.
- **Composição:** overfull máximo **5.19 pt** (o limite do projecto é 15), 2 underfull, 0 floats
  grandes demais.
- **Números:** extraí os 341 decimais distintos do corpo. Os 94 «sem fonte» são coordenadas TikZ,
  amostras de curva e valores intermédios cuja aritmética a tese mostra. **Não é achado**, e
  reportá-lo seria gritar de mais.
- **Resumo ↔ Abstract:** os mesmos dois números nos dois (`79 753`, `825`), sem divergência de
  conteúdo.
- **Proporção dos capítulos:** 1: 6 pp · 2: 14 · 3: 22 · 4: 18 · 5: 26 · 6: 14 · Apêndice: ~10.
  Corpo de **100 pp** em 127 físicas.
- **Distância figura ↔ texto:** depois da correcção do Cap. 4, o que sobra acima de 3 páginas são
  referências **para trás** (o texto manda relembrar) e citações entre capítulos. Nada a fazer.

---

## 5. Estado

**Tese 127 pp · 0 erros · 52/52 números conferidos · `check_entrega.py` a zero · 750 testes ·
ruff limpo.**
