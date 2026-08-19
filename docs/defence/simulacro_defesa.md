# Simulacro de defesa — cadeias de pressão para treinar (PT-PT)

> **Como usar:** lê a pergunta, tapa a resposta, responde **em voz alta** com as tuas palavras, só
> depois compara. O que treina de verdade não é a 1.ª pergunta — são os **follow-ups** (o júri não
> para na primeira). Cada bloco escala: Q1 → apertam → apertam mais. Todos os números são os
> congelados da tese. Complementa o [`guiao_de_defesa.md`](guiao_de_defesa.md) (§4 tem as versões
> curtas; aqui estão as cadeias completas).
>
> **Regras de ouro sob pressão:** (1) nunca concedas "fracasso" — diz "resultado". (2) Mantém a
> distinção **mecanismo vs hipótese**. (3) "Não medi isso; é trabalho futuro" é uma resposta forte.
> (4) Nunca inventes um número. (5) A honestidade desarma o arguente — fica calmo.

---

## 1. RQ4 — "o modelo perdeu, é um fracasso?" (a mais perigosa)

**🎓 Q1.** *"A RQ4 pergunta se o modelo prioriza 'para além da volatilidade'. Nenhum modelo com texto
bateu a volatilidade. Então a resposta à sua própria pergunta é 'não'. Como não é isto um fracasso da
contribuição central?"*

✅ *"A RQ4 tem duas partes e respondo às duas. Como **mecanismo de produto**, o modelo prioriza
claramente: dentro de um orçamento de 5 alertas/dia sobe a precisão de **0,379 para 0,632** — quase
4×, com probabilidades calibradas. A **hipótese científica** — 'o texto do título acrescenta sinal
sobre a volatilidade' — essa, pré-comprometida, deu não: PR-AUC **0,542 vs 0,496**. Não é um fracasso,
é um resultado, e reporto-o tal como caiu. É a segunda vez — a primeira foi a Isolation Forest — que a
escolha transparente vence um teste causal justo. Isso valida o desenho simplicidade-primeiro com
evidência, em vez de o assumir."*

**🎓 Q2 (aperta).** *"Se o texto não ajuda, para que serve o modelo? Podia ter usado só a volatilidade
— um número — e dispensado o machine learning."*

✅ *"Duas respostas. Primeira: eu não sabia o resultado à partida — a hipótese era plausível e
testável, e testá-la honestamente **é** a contribuição de engenharia de IA. Segunda: a volatilidade dá
um score; o modelo dá uma **probabilidade calibrada e decomponível** — digo '54%, e eis os termos que
lá chegaram'. O aparato não é para bater a volatilidade; é para a embrulhar de forma calibrada e
explicável."*

**🎓 Q3 (a mais dura).** *"Contexto-só deu 0,538; volatilidade-só 0,542. São iguais. Nem o contexto
ajuda — é tudo volatilidade. A sua 'triagem' é um nome pomposo para um limiar de volatilidade."*

✅ *"Concordo que o sinal vive esmagadoramente na volatilidade — digo-o na tese, sem rodeios. A
distinção real é: a volatilidade é uma feature; o modelo calibrado transforma-a numa probabilidade
honesta com um orçamento de alertas, o que um limiar cru não faz — o ganho 0,379→0,632 é esse valor
operacional. E o valor científico não é 'o meu modelo é sofisticado'; é 'testei se a sofisticação
valia a pena, e a resposta honesta foi: aqui, não'. Uma tese de engenharia honesta deve premiar isso."*

**🎓 Q4 (a pergunta técnica mais afiada).** *"Adicionar o texto BAIXA a PR-AUC (0,538→0,496). Um
modelo bem regularizado não piora ao ganhar features — isso não é um artefacto de sub-ajuste, e não
uma descoberta sobre o texto?"*

✅ *"Excelente pergunta, e testei-a exatamente. Um bootstrap por cluster (ticker,dia) confirma que a
degradação é robusta (P=1,00), não ruído de uma seed. E — concedo o seu ponto em parte — o texto cru
384-d ESTAVA deprimido por dimensionalidade: reduzi-o por PCA e recupera de 0,499 para **0,533**.
Reporto isso. MAS mesmo o melhor texto justo (0,533, com C afinado, PCA e o encoder de domínio FinBERT)
nunca supera a volatilidade (0,542) nem o contexto (0,538): recupera até ao nível do contexto, nunca
acima. Logo o negativo é robusto, não um artefacto — e testei a própria crítica em vez de a evitar."*

---

## 2. RQ2 — validada à escala (era "o corpus é fino")

**🎓 Q1.** *"O seu corpus de recuperação são 3.714 títulos de uns meses. Como sabe que a P@5 de 0,51
se aguenta noutro período?"*

✅ *"Boa pergunta — e a resposta mudou desde a versão preliminar. O resultado inicial (P@5 **0,514** em
~3.700 títulos) era preliminar por desenho: estabelecia o mecanismo. Mas validei-o depois **à
escala**: no corpus FNSPID multi-ano, ~80 mil títulos de 6 anos, o mesmo protocolo cross-ticker deu
**P@5 0,595** — acima do preliminar. A recuperação não só se aguenta noutro período, melhora."*

**🎓 Q2 (aperta).** *"E a direção dos precedentes? Recuperar o tema não diz o que o preço faz."*

✅ *"Exato, e quantifiquei-o: a consistência de direção dos clusters recuperados é **0,708**, quase no
chão do acaso de **0,688** — a recuperação capta o TEMA (P@5 bem acima do acaso) mas quase nada sobre a
DIREÇÃO. Confirma quantitativamente o meu ponto do CS3: o impacto médio é evidência sobre um tema,
nunca uma previsão direcional — e é por isso que mostro sempre os precedentes individuais."*

**🎓 Q3 (a mais dura).** *"Então ainda há uma parte por fazer."*

✅ *"Sim, e digo-o: o que fica é o estudo das MAGNITUDES de impacto ajustadas ao mercado sobre os
precedentes multi-ano. Mas a recuperação — o componente — está **validada à escala**, e a propriedade
tema≠direção está **medida**, não assumida. Reporto o que está feito e o que falta, sem sobre-afirmar."*

---

## 3. RQ3 — "a utilidade nunca foi medida"

**🎓 Q1.** *"Dizem 'explicável e útil', mas nunca mediram a utilidade com pessoas. Não é uma alegação
vazia?"*

✅ *"Separo as duas metades. A **fidelidade** não é uma alegação — é uma propriedade construída e
testada: cada alerta é composto diretamente dos objetos calculados, e um teste unitário verifica que
reproduz exatamente a data, o ticker e o impacto de cada precedente. A **utilidade** para um humano não
a afirmo como resolvida — reporto-a como ponto **em aberto**, uma limitação explícita, não uma
conclusão."*

**🎓 Q2 (aperta).** *"Uma limitação confessada não deixa de ser um buraco na RQ3."*

✅ *"Deixa, e assumo-o. Mas é um buraco **desenhado**: tenho o protocolo do estudo pronto (rubrica de
clareza/completude/acionabilidade, desenho within-subject, análise). O que falta é correr com pessoas —
trabalho de dias, não de método. 'Construí a explicação fiel e desenhei como medir a utilidade' é mais
honesto do que alegar utilidade sem prova."*

**🎓 Q3 (a mais dura).** *"Então a sua contribuição de XAI é só metade."*

✅ *"A contribuição de XAI é a explicação **fiel por construção** ponta a ponta — isso está inteiro e é
o difícil. A utilidade percebida é uma questão empírica separada que **qualquer** sistema XAI enfrenta,
e que reporto honestamente como o próximo passo. Não confundo 'não medido' com 'inexistente'."*

---

## 4. "Onde está a contribuição? Isto é só integrar ferramentas"

**🎓 Q1.** *"Não vejo um algoritmo novo. Usou o SBERT dos outros, a regressão logística dos manuais.
Onde está a sua contribuição?"*

✅ *"É uma tese de Engenharia de IA, e a contribuição é essa: **integrar, aplicar e avaliar
criticamente** componentes existentes num sistema funcional, explicável e reproduzível — não inventar
um algoritmo. Usar modelos existentes é o trabalho de engenharia. Concretamente: uma metodologia
documentada de correlação notícia–impacto (retrieval + event-study, sem lookahead), um sistema
XAI-first com toda a cadeia rastreável, um modelo de triagem calibrado, e uma avaliação crítica contra
baselines — incluindo dois testes pré-comprometidos que os métodos transparentes venceram."*

**🎓 Q2 (aperta).** *"Mas qualquer engenheiro podia ligar essas peças."*

✅ *"Ligar as peças é fácil; ligá-las de forma **honesta e avaliada** não é. A contribuição está nas
decisões defensáveis e na avaliação que as testa: porquê cosseno (a identidade em vetores unitários),
porquê z-score e não um detetor aprendido (testei — a Isolation Forest perdeu, F1 0,271 vs 0,530),
porquê Platt e não isotónica, e a disciplina anti-lookahead testada por mutação. E o resultado mais
valioso é negativo e pré-comprometido — o texto não bate a volatilidade — que só tem valor porque a
avaliação foi montada para o poder revelar. Isso é engenharia de IA, não montagem."*

**🎓 Q3 (profundidade).** *"A sua 'IA' de recuperação é um encoder de 2021 off-the-shelf. Nem testou
um encoder de domínio nem um moderno."*

✅ *"Testei ambos, no mesmo protocolo. O FinBERT de domínio dá **0,420** — pior, coerente com ser
afinado para sentimento e não para similaridade de frases. Os modernos E5 e BGE **empatam** com o
MiniLM (~0,51), não o superam. Ou seja, a escolha do MiniLM está validada por **medição**, não por
conveniência: um modelo pequeno, gratuito e de 2021 continua no sweet spot para esta tarefa — e agora
tenho o número para o dizer, em vez de o argumentar."*

---

## 5. Proxy de setor — "relevância a fingir"

**🎓 Q1.** *"'Mesmo setor = relevante' é um proxy fraco para relevância."*

✅ *"É um substituto automático e imperfeito, e digo-o. Torno-o **exigente** de duas formas: proíbo
precedentes do mesmo ticker (mede cross-ticker, o caso difícil) e uso k pequeno. A inspeção
qualitativa mostra onde falha — o setor 'consumo' é demasiado amplo, e é por isso que o seu lift é o
mais baixo (**+0,100** vs **+0,377** na energia)."*

**🎓 Q2 (aperta).** *"Se sabe que falha no consumo, porque não usou um rótulo de relevância melhor?"*

✅ *"Porque um rótulo humano de relevância exigiria anotação manual em escala, que não tenho — e um
proxy **transparente e reprodutível** é preferível a um rótulo subjetivo não-reproduzível. O proxy de
setor é a escolha defensável dado o orçamento; um estudo humano de relevância é o trabalho futuro que o
substituiria."*

---

## 6. Impacto bruto vs ajustado ao mercado

**🎓 Q1.** *"O impacto que mostra ao utilizador é o retorno bruto. Não devia ser ajustado ao mercado?"*

✅ *"Uso o **bruto** no que **mostro** porque é o que o investidor experienciou e pode verificar num
gráfico público — transparência. Mas o **rótulo** do modelo de triagem usa o retorno **ajustado ao
mercado**, para isolar a ação do índice. É a mesma maquinaria a responder a duas perguntas diferentes,
e digo o custo do bruto — confundimento com o movimento do mercado — que limito com janelas curtas
(+1/+3/+5 dias)."*

**🎓 Q2 (aperta).** *"Mas então o número que o utilizador vê pode ser sobretudo o mercado, não a
notícia."*

✅ *"Pode, em dias de grande movimento de mercado, e é uma limitação que enuncio. A mitigação é dupla:
as janelas curtas reduzem a deriva do mercado, e mostro sempre os precedentes **individuais**, não só a
média — o utilizador vê a dispersão. Para uma alegação causal usaria o ajustado; para uma evidência
transparente e verificável, o bruto é a escolha honesta."*

---

## 7. Lookahead — "como garante que não usa o futuro?"

**🎓 Q1.** *"Como garante que não há lookahead?"*

✅ *"Por construção **e** por teste. Cada feature usa só informação até ao fecho do dia do evento; o
impacto acumula-se **estritamente para a frente** a partir desse fecho. E há um teste unitário que
**muta os preços futuros** e verifica que nenhuma feature muda enquanto o rótulo muda — se houvesse
fuga, esse teste falhava."*

**🎓 Q2 (aperta).** *"E na avaliação? O split temporal não podia deixar uma janela de rótulo cavalgar
dois blocos?"*

✅ *"É exatamente o risco que fecho: o split é por dia único com **embargo**, para nenhuma janela de
rótulo (+1/+3/+5) atravessar a fronteira treino/teste. A tese descreve esse cuidado precisamente porque
é onde estes estudos costumam falhar sem dar por isso."*

---

## 8. "Porquê não prever o preço?"

**🎓 Q1.** *"Um sistema que previsse o preço não seria muito mais útil?"*

✅ *"Seria, se fosse possível fazê-lo com honestidade — e não é. Pela eficiência de mercado (Fama,
1970), as notícias públicas são absorvidas quase de imediato, por isso prever a partir delas é, por
construção, muito difícil. Escolhi um problema **honesto** — medir e explicar o que já aconteceu em
casos análogos — defensável e genuinamente útil, em vez de um que não resolveria com integridade e que
produziria um número falsamente confiante."*

**🎓 Q2 (aperta).** *"Mas o seu RQ4 treina um modelo. Isso não é prever?"*

✅ *"Não. O modelo estima a probabilidade de uma notícia ser **material** — merecer atenção — não a
**direção** nem o retorno. Nunca digo 'vai subir'; digo 'isto parece material, e eis os casos análogos
e o que lhes aconteceu'. A fronteira é deliberada e está em todo o produto: evidência do passado, nunca
previsão do futuro."*

---

## 9. Bónus — perguntas de método mais curtas (resposta única)

- **"Porquê o cosseno e não a distância euclidiana?"** → *"Em vetores de comprimento 1 são
  equivalentes: `‖q̂−ê‖² = 2 − 2·cos`, logo dão a mesma ordenação. A escolha é canónica, não
  arbitrária."*
- **"O z-score assume normalidade dos retornos?"** → *"Uso-o como medida de dispersão relativa, não
  como teste estatístico — não preciso de assumir normalidade para dizer 'quantos desvios-padrão fora
  do normal'. E o argumento primário é o da taxa de disparo, que é label-free."*
- **"Porquê Platt e não calibração isotónica?"** → *"Dois parâmetros não sobre-ajustam um bloco de
  validação modesto; a isotónica, mais flexível, arriscava-o. Testei as duas e o Platt não perde —
  documentado."*
- **"O formato do alerta evoluiu — os exemplos da tese ainda valem?"** → *"O layout foi compactado para
  legibilidade, mas os **campos** são os mesmos (evento, precedentes com data/ticker/similaridade/
  impacto, cláusula de não-previsão), por isso o argumento de fidelidade não muda."*

---

## 11. "Construiu quatro coisas e não usou nenhuma" (a NOVA mais perigosa)

Esta é agora a pergunta mais provável, porque os Casos 5 a 8 terminam todos em "não". Trata-a como
uma oportunidade, não como uma acusação.

**Q1.** *"Fez uma taxonomia de eventos, predição conformal, deteção de deriva e um score de
convergência, e não ligou nenhum deles ao produto. Não foi trabalho desperdiçado?"*

> *"Foi o contrário: é a parte do trabalho de que tenho mais orgulho. Construir é fácil; o difícil
> é ter um critério que consiga dizer não. Cada um dos quatro foi construído, medido, e recusado
> **pela medição**, não por falta de tempo. Se eu tivesse ligado os quatro, teria um produto mais
> vistoso e uma tese mais fraca."*

**Q2.** *"Mas o AMI de 0,358 mostra que a taxonomia funciona. Porque não a usa?"*

> *"Porque 'funciona melhor do que o acaso' não é o mesmo que 'é boa o suficiente para decidir'. A
> silhueta é 0,084, ou seja os grupos sobrepõem-se muito, e a rotulagem depende de uma rubrica que
> só cobre 15,1% do corpus. Filtrar precedentes por um tipo de evento errado **remove evidência
> válida em silêncio**, e o utilizador nunca saberia. Prefiro não filtrar a filtrar mal."*

**Q3.** *"Isso não é conveniente? Recusar sempre que o resultado não agrada?"*

> *"Seria, se o critério tivesse aparecido depois do resultado. Não apareceu: a rubrica foi escrita
> e registada **antes** de qualquer agrupamento correr, e a ordem está no histórico do projeto. E
> quando a medição sustentou uma capacidade nova, eu liguei-a: o detetor de volume saiu deste mesmo
> estudo e está em produção."*

---

## 12. "O seu modelo só decide em 39,5% dos casos"

**Q1.** *"A predição conformal mostra que, para garantir 90% de cobertura, o modelo só consegue uma
decisão definida em 39,5% dos títulos. O modelo não serve para nada?"*

> *"Serve para o que a tese diz que serve, e esse número **confirma-o** em vez de o contradizer. A
> RQ4 já reportava que o texto não bate a volatilidade. A conformal chega à mesma conclusão por um
> caminho completamente independente, sem treinar nada de novo: o sinal disponível não separa a
> maioria dos itens. Dois métodos que não partilham suposições a dizer o mesmo é mais forte do que
> um."*

**Q2.** *"Então porque é que o produto continua a decidir em 100% dos casos?"*

> *"Porque o produto promete uma cadência legível, e um fluxo que dissesse 'não sei' a 60% dos itens
> quebrava essa promessa sem ninguém ter decidido quebrá-la. Mas o número está na tese, e é ele que
> diz ao leitor o quanto pesar cada alerta. É a diferença entre um sistema que esconde a sua
> incerteza e um que a mede e a publica."*

**Q3.** *"Não devia então baixar a exigência para 80%?"*

> *"A 80% a decisão definida sobe para 68%. Escolher o nível **depois** de ver qual dá melhor
> aparência seria exatamente o erro que evito no resto do trabalho. Reporto os três níveis e deixo
> o leitor escolher o que corresponde ao seu custo de errar."*

---

## 13. "Treinou em 2018-2023 e corre em 2026"

**Q1.** *"O modelo está obsoleto?"*

> *"A distância existe e está **medida**, não afirmada. A volatilidade pré-evento tem um PSI de
> 0,281, banda significativa; as features de retorno ficam em 0,020 e 0,014, estáveis. Portanto a
> deriva é real mas concentrada numa entrada, e não generalizada."*

**Q2.** *"Vi um PSI de 2,866 no instantâneo ao vivo. Isso é enorme."*

> *"É, e o relatório diz porque é que esse número **exagera**. A média só se desloca 0,18 desvios-
> padrão. Um PSI perto de três com uma deslocação de média tão pequena não descreve um mercado
> irreconhecível; descreve uma amostra com poucas observações independentes: dez tickers, cerca de
> cem dias, e a volatilidade a 20 dias é uma janela deslizante, por isso dois dias seguidos
> partilham 95% da informação. Escrevi que os dois PSI **não são comparáveis em magnitude**, em vez
> de citar o maior."*

**Q3.** *"E porque é que os seus números congelados ainda valem?"*

> *"Porque a prevalência do rótulo **oscila em vez de ter tendência**: 0,385, depois 0,470, depois
> 0,378. O protocolo de avaliação já atravessa uma dessas oscilações, portanto os números
> reportados são medidos **sob** deriva, não apesar dela. E a mesma oscilação explica por que a
> cobertura conformal mais apertada se parte: uma cauda que oscila é o que uma garantia a 95% tem
> menos folga para absorver."*

---

## 10. Antes de entrares na sala
- Sabe de cor: **0,015 vs 0,344** · **P@5 0,514** · **0,542 vs 0,496** · **0,379→0,632 (em dados
  retidos)** · **ROC-AUC ao vivo 0,494** · **39,5%** · **PSI 0,281** · **130/139 pp** (mapa completo
  no `guiao_de_defesa.md` §2).
- ⚠️ **Não digas 0,667 vs 0,455.** Foi retirado: valia sobre 12 decisões e o intervalo continha a
  taxa-base. Com 530 decisões o sinal inverte-se (0,592 mantidas vs 0,647 suprimidas). Se disseres o
  número antigo e te pedirem o intervalo, não tens resposta.
- Ensaia estas **11** cadeias em voz alta até a Q3 sair sem hesitar. As três últimas (§11–13) são as
  mais prováveis agora, porque cobrem os estudos que terminam em "não" — que são **cinco**, e o
  quinto (o gate medido em produção) é o mais recente e o mais provável de ser perguntado.
- Se travares numa pergunta nova: respira, reformula a pergunta em voz alta, e responde pela evidência
  que tens — nunca por um número inventado.
