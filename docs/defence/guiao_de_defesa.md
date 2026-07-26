# Guião de Defesa — recall rápido para a arguição (PT-PT)

> Complementa o guia de estudo (`slides/guia_estudo/`, que ENSINA). Isto é para **recall e
> ensaio**: os números que tens de saber de cor, o guião por RQ, e as perguntas mais duras do
> júri com respostas-modelo. Feito para uma defesa CALMA. Todos os números são os congelados da
> tese (reprodutíveis). **Regra de ouro na defesa: honestidade > brilho.** Um "sim" honesto e um
> "isso é trabalho futuro" defendem-se sempre; um exagero rebenta.

---

## 1. Pitch de 30 segundos (decorar)

> "Construí o **InvestiGator**: um sistema de alertas financeiros **explicável** para investidores
> de retalho nos EUA. Dois gatilhos — um movimento de preço anómalo, ou uma notícia relevante.
> Cada alerta traz a explicação completa: *o que* detetou, *como*, as *fontes*, e *precedentes*
> históricos com o que aconteceu aos preços depois. **Nunca prevê** — mede e explica. A
> contribuição é de **engenharia de IA**: integrar, aplicar e avaliar criticamente componentes
> existentes num sistema funcional, honesto e reprodutível, com uma metodologia documentada de
> correlação notícia–impacto."

**O argumento central (se só disseres uma coisa):** a **simplicidade defensável** venceu. Em
**dois testes justos e pré-comprometidos**, o método transparente bateu o aprendido (z-score vs
Isolation Forest; volatilidade vs texto). Reporto isto tal como caiu — é integridade, não
fraqueza.

---

## 2. Mapa dos números congelados (número → o que é → defesa numa frase)

| Número | O que é | Defesa numa frase |
|---|---|---|
| **0.015 vs 0.344** | Amplitude da taxa de disparo entre 15 tickers: z-score vs limiar fixo | "O argumento mais forte, e **não precisa de rótulo**: o z-score dispara de forma consistente em ações de volatilidade muito diferente; o limiar fixo não." |
| **F1 0.516 vs 0.218** | z-score vs limiar fixo, contra proxy de movimentos extremos | "Mais do dobro; mas é evidência de APOIO, porque o rótulo é relativo à volatilidade." |
| **F1 0.271 vs 0.530** | Isolation Forest vs z-score, mesma informação causal | "Dei ao modelo aprendido a MESMA informação e perdeu. 1.º teste justo." |
| **F1 0.664 vs 0.516** | EWMA vs volatilidade deslizante | "A EWMA melhora — reporto-o. Mantenho a deslizante por ser explicável numa frase; o ganho fica como futuro VALIDADO." |
| **P@5 0.514 (±0.015)** | Recuperação SBERT-MiniLM, cross-ticker | "~2,1× a base aleatória (0.240), acima da lexical (0.346). Robusto (5 sementes, 2 modelos)." |
| **+0.377 / +0.348 / +0.100** | Lift energia / saúde / consumo | "O motor vale mais onde o vocabulário é distintivo; menos no consumo, genérico." |
| **z = +7.61** | Tesla, 24 Out 2024, pós-resultados | "Exemplo real: μ=−0.92%, σ=2.73%, r=+19.8% → z=+7.61. A mesma regra que ignora ±2% apanha isto." |
| **0.542 / 0.538 / 0.496** | PR-AUC triagem: volatilidade / contexto / contexto+texto | "O TEXTO não ajuda; o sinal vive no contexto de mercado. 2.º teste justo." |
| **0.632 vs 0.163** | Precisão@orçamento (5 alertas/dia) vs alertar-sempre | "A triagem quase QUADRUPLICA a precisão dentro do orçamento — o valor de produto." |
| **p = 0.539 (54%)** | Decisão META real, 12 Jul 2026 | "u=+0.699 (vol + setor dominam) → σ → Platt → 54%, o número exato enviado ao canal." |
| **0.667 vs 0.455** | Pós-validação ao vivo (mantidas vs base rate) | "Fora da amostra, EM PRODUÇÃO: o mecanismo de triagem confirma-se." |
| **90 / 92 pp · 50 refs · 224 testes** | Tese EN/PT · referências verificadas · suíte | "Reprodutível de ponta a ponta; nenhum número digitado à mão." |

---

## 3. As quatro RQ — veredicto + guião de ~60 s (decorar o veredicto e a 1.ª frase)

**RQ1 (deteção transparente) — SIM.**
> "Um z-score deslizante deteta movimentos abruptos de forma consistente em todo o mercado
> (amplitude 0.015 vs 0.344), e cada alerta é explicável a um não-especialista. Testei-o contra
> uma Isolation Forest com a mesma informação — a transparente ganhou."

**RQ2 (precedentes análogos, sem lookahead) — SIM, para a recuperação.**
> "A recuperação semântica bate todas as linhas de base (P@5 0.514 vs 0.346 lexical, 0.240
> aleatório), independentemente do modelo. O impacto é medido ESTRITAMENTE após o evento — é um
> resultado observado, nunca uma previsão. A validação em larga escala sobre o FNSPID multi-ano é
> trabalho futuro; a MAQUINARIA está montada e comporta-se de forma coerente."

**RQ3 (explicações fiéis e úteis) — FIEL sim; ÚTIL em aberto.**
> "As explicações são fiéis POR CONSTRUÇÃO: o texto é composto diretamente dos objetos calculados,
> e um teste automático verifica-o. A utilidade para um humano precisa de um estudo com pessoas —
> reporto-a como limitação em aberto, não como afirmação."

**RQ4 (triagem para além da volatilidade) — NÃO no texto; SIM no mecanismo.** *(o mais sensível)*
> "Pré-comprometi-me com a comparação decisiva: nenhum modelo que lê o TEXTO da manchete bateu a
> volatilidade (PR-AUC 0.496 vs 0.542). **Mas isto é um resultado, não um fracasso** — como
> MECANISMO, a triagem quase quadruplica a precisão dentro do orçamento (0.632 vs 0.163). O sinal
> vive no contexto de mercado, e a variante em produção usa exatamente essas features. É a 2.ª vez
> que a escolha transparente venceu num teste justo. Reporto-o tal como caiu."

---

## 4. Perguntas MAIS DIFÍCEIS do júri — respostas-modelo (ensaiar em voz alta)

**P: O corpus de recuperação é fino e recente. Como sabes que a P@5 se aguenta?**
> "Boa pergunta — é a limitação que assinalo explicitamente. O resultado é **preliminar** por
> desenho: usei ~3.714 manchetes reais dos meses recentes. O que ele estabelece é o MECANISMO — os
> embeddings batem consistentemente as linhas de base, em 5 sementes e 2 modelos, com uma
> restrição cross-ticker exigente. A validação de MAGNITUDES sobre o FNSPID multi-ano (2018–23) é o
> passo seguinte natural, e a base de conhecimento já foi reconstruída para isso."

**P: O teu modelo treinado PERDEU para a volatilidade. Não é um fracasso?**
> "Não — e é importante porque foi **pré-comprometido**. A pergunta da RQ4 era 'o texto ajuda?', e
> a resposta honesta é 'neste corpus, não'. Isso é ciência: reporto o que caiu. E como PRODUTO a
> triagem é claramente valiosa (0.632 vs 0.163). Juntando a Isolation Forest, é a segunda vez que a
> escolha transparente venceu um teste causal justo — isso VALIDA o desenho simplicidade-primeiro
> com evidência, em vez de o assumir."

**P: 'Mesmo setor = relevante' não é um proxy fraco?**
> "É um substituto automático, imperfeito, e digo-o. Torno-o EXIGENTE de duas formas: proíbo
> precedentes do mesmo ticker (cross-ticker), e uso k pequeno. A inspeção qualitativa mostra onde
> falha (o setor 'consumo' é demasiado amplo). Um estudo humano de relevância é trabalho futuro."

**P: O impacto mostrado é bruto — não devia ser ajustado ao mercado?**
> "Uso o retorno BRUTO no que MOSTRO ao investidor, porque é o que ele teria experienciado e pode
> verificar num gráfico público. Mas o RÓTULO do modelo de triagem usa o retorno ajustado ao
> mercado, para isolar o movimento da ação do índice. É a mesma maquinaria a responder a duas
> perguntas diferentes — assumo o custo do bruto (confundimento) e limito-o com janelas curtas."

**P: Como garantes que não há lookahead?**
> "Por construção e por teste. Cada feature usa só informação até ao instante; o impacto acumula-se
> ESTRITAMENTE para a frente a partir do fecho do dia do evento. E há um teste unitário que MUTA os
> preços FUTUROS e verifica que nenhuma feature muda enquanto o rótulo muda. O split temporal é por
> dia único com embargo, para nenhuma janela de rótulo cavalgar dois blocos."

**P: Porquê não previr o preço? Não seria mais útil?**
> "Pela eficiência de mercado (Fama 1970): as notícias públicas são absorvidas quase de imediato,
> por isso prever a partir delas é, por construção, muito difícil. Escolhi um problema HONESTO —
> medir e explicar o que já aconteceu em casos análogos — que é defensável e genuinamente útil a um
> não-especialista, em vez de um que não conseguiria resolver com integridade."

---

## 5. Armadilhas — o que NÃO fazer

- **NÃO lideres com a app "gira"** (mascote, temas, painel admin). São ótimos como produto, mas na
  defesa mostra a app SÓBRIA (o dashboard, 1 slide) como prova de que o sistema CORRE. Senão o júri
  pergunta "isto é investigação ou um brinquedo?".
- **NÃO sobre-afirmes.** Nunca digas "prevê" ou "recomenda". Diz "mede", "explica", "mostra
  evidência".
- **NÃO tentes defender extensões que não dominas.** Domina os 4 estudos de caso à exaustão; as
  extensões (EWMA, LOF, RQ4-ext) só as mencionas se aguentas 3 perguntas de profundidade.
- **NÃO fiques na defensiva na RQ4.** Diz o veredicto com CONFIANÇA — é um resultado honesto.
- **Se não sabes:** "Não medi isso; seria trabalho futuro" é uma resposta forte. Nunca inventes um
  número.

---

## 6. Checklist final (só HUMANO — sem isto não há submissão)

- [ ] **Declaração institucional** — confirmar com o Prof. Luís Gomes a redação e o formato exatos
      exigidos pela MEIA/ISEP para o front matter.
- [ ] **Licença do código** (MIT/Apache; política de IP do ISEP) + ficheiro `LICENSE`.
- [ ] **Data e formato de entrega** confirmados.
- [ ] **Leitura final** das DUAS teses (EN + PT) — o texto é teu para defender; a tradução PT
      precisa da tua aprovação de voz/terminologia.
- [ ] **Ensaio em voz alta:** o pitch de 30 s, o veredicto de cada RQ, e as 6 perguntas duras do §4.

---

## 7. (Opcional, se houver tempo antes da defesa) — reforços de alto valor

1. **Pequeno estudo humano de utilidade (RQ3):** 6–8 pessoas, uma rubrica (clareza/completude/
   acionabilidade) sobre alguns alertas reais. Fecha a maior lacuna "em aberto" de forma barata.
2. **Avaliação de recuperação no FNSPID multi-ano (RQ2):** sobe a RQ2 de "preliminar" a "validada em
   escala" — mas é uma experiência NOVA numa tese perto da defesa; só com o teu 'ok' (muda o que
   tens de defender, e pode não mudar a história).
