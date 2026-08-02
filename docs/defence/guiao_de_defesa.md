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
| **P@5 0.514 (±0.015)** | Recuperação SBERT-MiniLM, cross-ticker (corpus preliminar) | "~2,1× a base aleatória (0.240), acima da lexical (0.346). E **validado à escala: 0,595 em 80k**." |
| **+0.377 / +0.348 / +0.100** | Lift energia / saúde / consumo | "O motor vale mais onde o vocabulário é distintivo; menos no consumo, genérico." |
| **z = +7.61** | Tesla, 24 Out 2024, pós-resultados | "Exemplo real: μ=−0.92%, σ=2.73%, r=+19.8% → z=+7.61. A mesma regra que ignora ±2% apanha isto." |
| **0.542 / 0.538 / 0.496** | PR-AUC triagem: volatilidade / contexto / contexto+texto | "O TEXTO não ajuda; o sinal vive no contexto de mercado. 2.º teste justo — e **robusto** (re-teste justo com PCA/FinBERT nunca bate a volatilidade)." |
| **0.632 vs 0.163** | Precisão@orçamento (5 alertas/dia) vs alertar-sempre | "A triagem quase QUADRUPLICA a precisão dentro do orçamento — o valor de produto." |
| **p = 0.539 (54%)** | Decisão META real, 12 Jul 2026 | "u=+0.699 (vol + setor dominam) → σ → Platt → 54%, o número exato enviado ao canal." |
| **0.667 vs 0.455** | Pós-validação ao vivo (mantidas vs base rate) | "Fora da amostra, EM PRODUÇÃO: o mecanismo de triagem confirma-se." |
| **P@5 0.595 (80k)** | Recuperação à escala no FNSPID multi-ano *(reforço)* | "RQ2 validada à escala, acima do preliminar 0,514." |
| **dir. 0.708 vs chão 0.688** | Consistência de direção dos precedentes *(reforço)* | "Recupera o TEMA, não a DIREÇÃO — tema≠direção quantificado." |
| **FinBERT 0.420 · E5/BGE ~0.51** | Benchmark de embedders *(reforço)* | "MiniLM validado por medição: domínio pior, modernos empatam." |
| **texto justo 0.533 < 0.542** | RQ4 re-teste justo (C+PCA+FinBERT) *(reforço)* | "Negativo do texto robusto; PCA recupera de 0,499 mas nunca bate a volatilidade." |
| **AMI 0.358 vs 0.188** | Tipo de evento vs ticker, no espaço de embeddings *(Caso 5)* | "O espaço **sabe** o tipo de acontecimento, e sabe-o mais do que sabe a empresa. Mas a silhueta é 0,084: fraco demais para filtrar precedentes, por isso NÃO liguei." |
| **0.712 vs 0.444** | Pureza dos grupos vs aleatório do mesmo tamanho *(Caso 5)* | "O 0,712 sozinho engana: com um tipo a valer 44% dos rótulos, o acaso já dá 0,444. O ganho real é +0,269." |
| **0.951/0.902/0.803** | Cobertura conformal, divisão aleatória *(Caso 6)* | "Bate no nominal aos três níveis — prova que a implementação está certa." |
| **0.937 a 95%** | Cobertura conformal, divisão TEMPORAL *(Caso 6)* | "Parte-se só no nível mais exigente. Pedir 95% apoia-se na CAUDA, e é a cauda que se move primeiro. A 90% e 80% aguenta." |
| **39,5%** | Decisões definidas a 90% de cobertura garantida *(Caso 6)* | "**O número mais duro da tese.** Para prometer 90%, o modelo só decide em 39,5% das manchetes. Não contradiz a RQ4 — **explica-a** por um caminho independente, sem treinar nada." |
| **PSI 0.281** | Deriva da volatilidade, treino → teste *(Caso 7)* | "A limitação que a tese repetia passou a estar MEDIDA. Banda significativa, e dá um gatilho de re-treino verificável em vez de uma intuição." |
| **0.385 / 0.470 / 0.378** | Prevalência do rótulo nos três blocos *(Caso 7)* | "**Oscila, não tem tendência.** Comparar só as pontas esconderia uma excursão de 22%. Explica por que os congelados sobrevivem E por que a cobertura a 95% parte." |
| **ganha em 1 de 3** | Fusão multi-sinal vs melhor sinal isolado *(Caso 8)* | "Um ganho que depende do orçamento que se escolhe citar é um ganho que se **pode ter escolhido**. Não entra em produção." |
| **peso −0,283** | Intensidade de notícia na fusão *(Caso 8)* | "**Negativo**: mais manchetes = menos provável ser material, porque são dias de conteúdo automático. À mão eu teria posto positivo e estaria errado. É a justificação empírica de DERIVAR pesos." |
| **107 / 111 pp · 59 refs · 478 testes** | Tese EN/PT · referências verificadas · suíte | "Reprodutível de ponta a ponta; nenhum número digitado à mão. As 59 referências resolvem todas, e o título devolvido bate — verificado automaticamente." |

### Se perguntarem pela bibliografia

> "59 entradas, 59 no registo de verificação, 59 chaves citadas. Zero órfãs, zero indefinidas, e
> **todas** com identificador resolúvel. Cada uma foi verificada contra o Crossref, a arXiv ou a
> fonte primária, com a data registada."

**A pergunta difícil, e a resposta:** *"Rejeitou o MacKinlay por não ter DOI resolúvel, mas aceita
quatro DOIs da JSTOR. Não é incoerente?"*
> "O critério é o identificador **resolver**, não o prefixo. Os quatro `10.2307` que aceitei
> resolvem; o do MacKinlay dá 404 no Crossref e não aparece no OpenAlex. Substituí-o pelo Brown e
> Warner (1985), que cobre a mesma metodologia de estudo de evento. A rejeição está registada —
> é evidência de que o protocolo foi aplicado, não contornado."

---

## 3. As quatro RQ — veredicto + guião de ~60 s (decorar o veredicto e a 1.ª frase)

**RQ1 (deteção transparente) — SIM.**
> "Um z-score deslizante deteta movimentos abruptos de forma consistente em todo o mercado
> (amplitude 0.015 vs 0.344), e cada alerta é explicável a um não-especialista. Testei-o contra
> uma Isolation Forest com a mesma informação — a transparente ganhou."

**RQ2 (precedentes análogos, sem lookahead) — SIM, validada à escala.**
> "A recuperação semântica bate todas as linhas de base (P@5 0.514 vs 0.346 lexical, 0.240
> aleatório), e **validei-a à escala** no FNSPID multi-ano: **P@5 0,595 em ~80k manchetes**, acima do
> preliminar. O impacto é medido ESTRITAMENTE após o evento — evidência observada, nunca previsão.
> Fica só o estudo das MAGNITUDES ajustadas ao mercado como trabalho futuro."

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
> "A resposta mudou desde a versão preliminar. O inicial (P@5 0,514 em ~3.700 manchetes) era
> preliminar por desenho — estabelecia o mecanismo. Mas validei-o **à escala**: no FNSPID multi-ano,
> ~80k manchetes de 6 anos, o mesmo protocolo cross-ticker deu **P@5 0,595** — acima do preliminar.
> E quantifiquei o tema≠direção (consistência 0,71 vs chão do acaso 0,69). Fica só o estudo das
> magnitudes ajustadas ao mercado."

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
2. ✅ **Avaliação de recuperação no FNSPID multi-ano (RQ2): FEITO** — P@5 **0,595** em 80k, já
   integrado na tese; a RQ2 subiu de "preliminar" a "validada à escala". Resta apenas o estudo das
   magnitudes de impacto ajustadas ao mercado.

---

## 8. As fórmulas — intuição, porquê, e como as dizes em voz alta

> Não decorar matemática. Perceber o que cada uma FAZ e dizê-la numa frase. São 7, na notação da tese.

### 8.1 z-score — `z_t = (r_t − μ_t) / σ_t`, anomalia se `|z_t| > k`
- **O que faz:** diz quantos desvios-padrão o retorno de hoje está fora do retorno médio recente **daquela** ação.
- **Intuição:** "grande" é relativo. +3% numa ação calma é enorme; numa volátil é rotina. Divido pela volatilidade de cada ação para ser justo.
- **Porque existe:** um limiar fixo em % dispara demais nas voláteis e de menos nas calmas. O z-score normaliza isso — e não precisa de rótulos.
- **Oral:** *"Pego no retorno de hoje, tiro a média recente e divido pelo desvio-padrão recente. Dá quantos desvios-padrão o movimento está fora do normal daquela ação. Acima de 3, é anomalia. Assim +3% conta como enorme numa ação calma e normal numa volátil."*

### 8.2 Embedding da frase — `e = (1/n) Σ tᵢ`, depois `ê = e / ‖e‖`
- **O que faz:** transforma uma notícia num vetor de números (a média dos vetores dos seus tokens), escalado para comprimento 1.
- **Intuição:** o SBERT dá um vetor por palavra (o sentido no contexto); a média resume a frase toda num só vetor. Normalizar põe todas as frases "à mesma escala" para as comparar por direção.
- **Porque existe:** preciso de UM vetor por notícia; a média (mean pooling) é a forma simples e padrão; a normalização L2 faz "comparar por cosseno" = "ordenar por distância".
- **Oral:** *"Cada notícia vira um vetor: o modelo lê a frase, dá um vetor por palavra, e eu faço a média — um vetor que resume o significado. Escalo-o a comprimento 1 para comparar notícias pelo ângulo."*

### 8.3 Cosseno — `cos(q,e) = (q·e) / (‖q‖‖e‖)`
- **O que faz:** mede o ângulo entre dois vetores. Perto de 1 = mesma direção (muito parecidos); 0 = nada a ver.
- **Intuição:** duas notícias do mesmo tema apontam na mesma direção no espaço de significado, mesmo que uma seja "maior". O cosseno ignora o tamanho, foca o tema.
- **Porque existe (a resposta ao "porquê cosseno?"):** quero similaridade de TEMA. E em vetores de comprimento 1, `‖q̂−ê‖² = 2 − 2·cos` — ordenar por cosseno é o mesmo que ordenar por distância. A escolha é **canónica, não arbitrária**.
- **Oral:** *"Comparo pelo cosseno — o ângulo entre os vetores. Perto de 1, mesmo tema. Como normalizei, é equivalente a medir a distância entre eles, por isso a escolha do cosseno é a natural, não uma preferência."*

### 8.4 Regressão logística — `p_raw = σ(u) = 1/(1+e^−u)`, com `u = w·x + b`
- **O que faz:** combina as features numa pontuação linear `u` e a sigmoide esmaga-a para um número entre 0 e 1.
- **Intuição:** `u` pode ser qualquer número; a sigmoide comprime-o em forma de S para [0,1]. Features que aumentam a materialidade puxam `u` para cima, `p` para perto de 1.
- **Porque existe:** quero uma probabilidade **interpretável** — cada peso `w` diz quanto cada feature contribui (é XAI). Simples de propósito, ao contrário de uma rede opaca.
- **Oral:** *"Somo as features com pesos — cada peso diz o quanto essa feature importa — e a sigmoide transforma a soma num número entre 0 e 1. Consigo decompor a decisão termo a termo."*

### 8.5 Calibração de Platt — `p = σ(a·p_raw + c)`
- **O que faz:** uma segunda sigmoide, com 2 parâmetros (a, c) ajustados em validação, que corrige as probabilidades cruas para serem honestas.
- **Intuição:** o score cru pode dizer "0.67" quando a frequência real é outra. O Platt estica/desloca a curva para que "p=0.6" signifique mesmo ~60% das vezes.
- **Porque existe:** um score discriminativo não é automaticamente uma probabilidade fiável. 2 parâmetros = não sobre-ajusta (mais seguro que a isotónica num bloco pequeno).
- **Oral (com o exemplo real):** *"O modelo deu logit u = +0,699 → sigmoide → 0,668. Mas 0,668 cru não é fiável, por isso aplico o Platt: σ(3,700·0,668 − 2,313) = **0,539** — os 54% que o canal recebeu. É o passo que torna a probabilidade honesta."*

### 8.6 precision@k — `precision@k = (1/|Q|) Σ_q (1/k) Σ_{d∈R_k(q)} rel(q,d)`
- **O que faz:** das k notícias recuperadas para cada consulta, que fração é relevante? Média sobre todas as consultas.
- **Intuição:** mostro 5 precedentes, 3 são do mesmo tema → precision@5 = 0,6. Mede a qualidade do **topo** da lista (o que o utilizador vê).
- **Porque existe:** numa recuperação, importa o topo, não a lista toda.
- **Oral:** *"Para cada notícia recupero as 5 mais parecidas e vejo quantas são mesmo do mesmo tema. A média é a precision@5: o meu SBERT dá 0,51 vs 0,24 do acaso — mais do dobro."*

### 8.7 PR-AUC (área sob a curva precisão–recall)
- **O que faz:** varro o limiar de decisão de 0 a 1; para cada um marco (recall, precisão); a área sob essa curva é a PR-AUC.
- **Intuição:** um número que resume o compromisso precisão↔recall em TODOS os limiares. Maior = melhor. O "chão" (alertar sempre) = a prevalência.
- **Porque existe:** com poucos casos materiais (classes desequilibradas), a ROC-AUC engana; a PR-AUC foca a classe rara.
- **Oral:** *"Como há poucos casos materiais, uso a PR-AUC — resume precisão vs recall em todos os limiares, e o chão é a própria prevalência. A volatilidade deu 0,542; nenhum modelo com texto passou disso — e reporto-o tal como é."*

---

## 9. O guião dos 15 minutos

> ~13 slides, ~1 min cada. Ensaia para **13–14 min** (buffer). Um facto por slide; fala, não leias.

| # | Slide | Tempo | O essencial a dizer |
|---|-------|-------|---------------------|
| 1 | Título + 1 frase | 0:30 | Quem sou, o título, e "alertas financeiros explicáveis; nunca prevejo". |
| 2 | O problema | 1:30 | Sobrecarga de informação; o investidor de retalho; **porque NÃO prever** (eficiência de mercado). |
| 3 | A ideia central | 1:00 | 2 gatilhos (movimento / notícia), XAI-first, engenharia de IA (integrar+avaliar, não inventar). |
| 4 | Arquitetura | 1:30 | O diagrama: sensores → motor único → explicação → Telegram/painel. |
| 5 | Deteção (RQ1) | 2:00 | z-score (8.1, em 1 frase) → **firing rate 0,015 vs 0,344**; bateu a Isolation Forest (teste justo nº1). |
| 6 | Recuperação (RQ2) | 2:30 | embeddings+cosseno → **P@5 0,514 vs 0,346/0,240**; + o **CS3 (tema≠direção)** como honestidade. |
| 7 | Triagem (RQ4) | 2:00 | o veredicto confiante: **mecanismo sim (0,163→0,632), texto não (0,542 vs 0,496)** — teste justo nº2. |
| 8 | Demo ao vivo | 1:30 | a app **sóbria**: um alerta real no canal + o painel. **Plano B: screenshot** se falhar o wifi. |
| 9 | Contribuições | 1:00 | as 4; o fio condutor: **"a simplicidade defensável venceu dois testes justos e pré-comprometidos"**. |
| 10 | Limitações + futuro | 1:00 | corpus fino, utilidade por medir, tema≠direção — ditas com naturalidade (mostra domínio). |
| 11 | Conclusão | 0:30 | "um sistema que corre, honesto e reprodutível; mede e explica, nunca prevê." |
| — | **Backup** | — | scorecard das RQ; exemplo trabalhado META (p=0,539); ablação RQ4-ext; EWMA. |

**Ordem — porquê:** problema → ideia → arquitetura → os 3 componentes pela ordem das RQ → prova ao vivo → síntese. O júri segue a mesma lógica da tese, sem saltos.

**Estratégia de comunicação:**
- **Lidera com o argumento, não com a app.** A mascote/temas ficam de fora; mostra a app sóbria como prova de que corre (1 slide).
- **Na RQ4, diz o veredicto com confiança** — é um resultado honesto, não um fracasso (ver §4).
- **Se não sabes:** *"Não medi isso; seria trabalho futuro"* é uma resposta forte. Nunca inventes um número.
- **Gestão do tempo:** se atrasares, corta a demo (o slide 8 tem o screenshot). Nunca cortes as limitações — é onde ganhas credibilidade.
