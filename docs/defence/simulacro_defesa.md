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
claramente: dentro de um orçamento de 5 alertas/dia sobe a precisão de **0,163 para 0,632** — quase
4×, com probabilidades calibradas. A **hipótese científica** — 'o texto da manchete acrescenta sinal
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
honesta com um orçamento de alertas, o que um limiar cru não faz — o ganho 0,163→0,632 é esse valor
operacional. E o valor científico não é 'o meu modelo é sofisticado'; é 'testei se a sofisticação
valia a pena, e a resposta honesta foi: aqui, não'. Uma tese de engenharia honesta deve premiar isso."*

---

## 2. RQ2 — "o corpus é fino e recente"

**🎓 Q1.** *"O seu corpus de recuperação são 3.714 manchetes de uns meses. Como sabe que a P@5 de 0,51
se aguenta noutro período?"*

✅ *"É a limitação que assinalo, e o resultado é preliminar **por desenho**. Estabelece o **mecanismo**,
não a magnitude: os embeddings batem todas as baselines — **0,514 vs 0,346** lexical e **0,240** do
acaso — em 5 sementes e 2 modelos (MiniLM e MPNet), com restrição cross-ticker exigente (proíbo o
mesmo ticker). A robustez a sementes e modelos é o que me diz que é sinal, não sorte do corpus."*

**🎓 Q2 (aperta).** *"'Mecanismo' é uma palavra confortável. Mas os impactos que mostra — o '−2%'
médio — são medidos nesse corpus fino. Não são de confiança."*

✅ *"Correto, e por isso a validação de **magnitudes** sobre o FNSPID multi-ano (2018–2023) é o passo
seguinte explícito — a base de conhecimento já foi reconstruída para isso (79.753 casos). O que
reporto hoje sobre impacto é a maquinaria a funcionar (event-study sem lookahead) a dar clusters
coerentes; a distribuição de magnitudes em escala é trabalho futuro, não uma alegação fechada."*

**🎓 Q3 (a mais dura).** *"Então metade da RQ2 — 'quantificar o impacto' — não está respondida."*

✅ *"Está respondida ao nível do **método** e de um estudo de caso reproduzível; não está **validada em
escala**. Faço essa distinção na tese e no scorecard, onde a RQ2 é 'sim, para a recuperação'. Prefiro
dizer exatamente o que está e o que não está do que sobre-afirmar — é a postura de toda a tese."*

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

## 10. Antes de entrares na sala
- Sabe de cor: **0,015 vs 0,344** · **P@5 0,514** · **0,542 vs 0,496** · **0,163→0,632** · **0,667 vs
  0,455** · **90/92 pp** (mapa completo no `guiao_de_defesa.md` §2).
- Ensaia estas 8 cadeias em voz alta até a Q3 sair sem hesitar.
- Se travares numa pergunta nova: respira, reformula a pergunta em voz alta, e responde pela evidência
  que tens — nunca por um número inventado.
