# learning.md — Explicações de conceitos (PT-PT, para o aluno)

> Registo de aprendizagem. **Regra de ouro:** nenhum conceito, técnica, métrica ou biblioteca é usado sem
> antes ter aqui um parágrafo claro em PT-PT — o que é e porque o usamos. Cada componente fecha com a nota
> "como explico isto ao júri em 3 frases".
>
> Conceitos introduzidos pela arquitetura (`docs/arquitectura_sistema.md`, Fase C). A justificação académica
> aprofundada e as citações verificadas entram com a tarefa de metodologias (Fase C).

---

## 1. Retorno e log-return
**O que é:** o *retorno* de um ativo é a variação percentual do preço entre dois instantes. Em finanças usa-se
muitas vezes o *log-return* = ln(preço_hoje / preço_ontem), porque é mais estável estatisticamente e soma-se
bem ao longo do tempo. **Porque o usamos:** trabalhamos sobre retornos (não preços), pois é nos retornos que se
mede um "movimento abrupto". **Nota:** não prevemos preços — só medimos o que já aconteceu.

## 2. Volatilidade
**O que é:** o desvio-padrão dos retornos num período — mede o "quanto o preço costuma oscilar". **Porque o
usamos:** um mesmo movimento de 3% é normal num ativo muito volátil e anormal num ativo calmo; precisamos da
volatilidade para julgar se um movimento é mesmo anómalo.

## 3. Média e desvio móveis (rolling) e z-score — *detetor de anomalias*
**O que é:** "móvel/rolling" significa calcular a média e o desvio-padrão dos retornos numa **janela
deslizante** (ex.: últimos 20 dias), em vez de usar todo o histórico. O **z-score** de um retorno é
(retorno − média_móvel) / desvio_móvel: diz a quantos desvios-padrão o movimento de hoje está da norma recente.
Um |z| grande (ex.: > 3) = movimento abrupto. **Porque o usamos:** é simples, transparente e fácil de explicar
— exatamente o que o XAI exige; só subiríamos a métodos mais complexos (ex.: Isolation Forest) se houvesse
justificação académica (§5.5).
- **Como explico ao júri em 3 frases:** "Para detetar movimentos abruptos calculo o z-score do retorno diário
  em relação à média e desvio-padrão dos últimos N dias. Se o movimento ultrapassar um limiar (ex.: 3 desvios),
  é assinalado como anomalia. Escolhi este método por ser estatisticamente transparente: o utilizador consegue
  ver e perceber exatamente porque é que o alerta disparou."

## 4. Embeddings de texto (sentence embeddings)
**O que é:** um *embedding* é uma representação de um texto como um vetor de números, construída por um modelo
de forma a que textos com significado parecido fiquem "perto" no espaço vetorial. **Porque o usamos:** permite
medir semelhança entre notícias de forma semântica (não só por palavras iguais), para encontrar precedentes
históricos análogos. Usamos um modelo *open-source* já treinado (inferência apenas) — integrá-lo é o trabalho
de engenharia, não o treino.

## 5. Similaridade do cosseno
**O que é:** uma medida de quão "alinhados" estão dois vetores (ângulo entre eles); 1 = idênticos, 0 = sem
relação. **Porque a usamos:** é a forma padrão de comparar embeddings — comparamos o embedding da notícia nova
com os das notícias históricas e escolhemos as mais semelhantes (top-k).

## 6. Event study e janela de impacto — *motor de correlação (núcleo)*
**O que é:** um *event study* mede o efeito de um evento (aqui, uma notícia) observando os retornos do ativo
numa **janela após** o evento (ex.: +1 dia, +3 dias). **Porque o usamos:** é assim que quantificamos, de forma
objetiva e reproduzível, o "impacto observado" de cada notícia histórica — e é essa evidência que apresentamos
como precedente. A escolha da janela e da métrica é **decisão nossa documentada** e parte da contribuição.
- **Como explico ao júri em 3 frases:** "Para cada notícia histórica meço o retorno do ativo nos dias seguintes
  (+1, +3) como 'impacto observado'. Quando chega uma notícia nova, recupero por similaridade as notícias
  históricas análogas e mostro o impacto que tiveram, como precedentes. Tudo usa apenas informação posterior ao
  evento, sem olhar para o futuro além da janela definida."

## 7. Explicabilidade (XAI) — *motor de explicação*
**O que é:** XAI (*eXplainable AI*) é IA cuja lógica é compreensível para o utilizador. No nosso caso, a
explicação combina (i) regras transparentes, (ii) os precedentes históricos como evidência e (iii)
opcionalmente atribuição de importância (ex.: SHAP) sobre o detetor. **Porque a usamos:** é o requisito central
da tese — o utilizador tem de saber 100% como se chegou ao alerta; nada de caixas negras.
- **Como explico ao júri em 3 frases:** "Cada alerta é acompanhado de uma explicação passo a passo: o que foi
  detetado, com que regra/medida, e que precedentes históricos o sustentam, com as fontes. Não há modelo opaco
  a decidir sozinho. Assim o investidor pode verificar e confiar — ou discordar — com base na evidência."

## 8. Lookahead / fuga de informação futura
**O que é:** *lookahead* (ou *data leakage* temporal) é usar, sem querer, informação do futuro para calcular
algo do presente — um erro grave que inflaciona resultados. **Porque importa:** ao medir impacto histórico ou
avaliar qualquer modelo, as features num instante só podem usar dados desse instante ou anteriores. Garantimos
e documentamos isto explicitamente (§6.5); é uma das perguntas prováveis do júri.

## 9. (Opcional) FinBERT / análise de sentimento
**O que é:** o FinBERT (`ProsusAI/finbert`) é um modelo de linguagem afinado para texto financeiro que
classifica o *sentimento* (positivo/negativo/neutro). **Porque (talvez) o usamos:** apenas em **inferência**
(sem treino), como sinal adicional na explicação. É padrão e citável. **Cortável** se não acrescentar valor
defensável (§5.3) — decidir na tarefa de metodologias. *(Ref. verificada: Araci 2019 — `araci2019finbert`.)*

## 10. (Opcional) SHAP — atribuição de importância
**O que é:** SHAP (*SHapley Additive exPlanations*) é um método que atribui a cada variável de entrada um valor
de "quanto contribuiu" para uma decisão do modelo, com base nos valores de Shapley da teoria de jogos. **Porque
(talvez) o usamos:** para, no detetor de anomalias, mostrar **que fatores** mais pesaram num alerta — reforça a
explicação local. Usado só se acrescentar clareza defensável. *(Ref. verificada: Lundberg & Lee 2017 — `lundberg2017shap`.)*

> Referências de enquadramento XAI (verificadas): Arrieta et al. 2020 (`arrieta2020xai`), Adadi & Berrada 2018
> (`adadi2018peeking`). Todas em `docs/citation_log.md`.
