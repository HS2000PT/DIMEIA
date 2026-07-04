# learning.md — Explicações de conceitos (PT-PT, para o aluno)

> Registo de aprendizagem. **Regra de ouro:** nenhum conceito, técnica, métrica ou biblioteca é usado sem
> antes ter aqui um parágrafo claro em PT-PT — o que é e porque o usamos. Cada componente fecha com a nota
> "como explico isto ao júri em 3 frases".
>
> Conceitos introduzidos pela arquitetura (`docs/design/arquitectura_sistema.md`, Fase C). A justificação académica
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
> (`adadi2018peeking`). Todas em `docs/decisions/citation_log.md`.

---

## 11. Base de conhecimento histórica e recuperação de precedentes (implementação)
Esta secção explica o que foi efetivamente **implementado** em `src/historical_kb/` e
`src/correlation_engine/similarity.py` (Sessão 9).

**O que é a KB:** uma coleção de notícias históricas, cada uma com (i) data e ticker, (ii) o
título, (iii) o **impacto pós-evento** medido (+1/+3/+5d, via `event_study`) e (iv) o
**embedding** do título. Guarda-se em JSONL (uma notícia por linha — legível e versionável).
**Para que serve:** quando chega uma notícia nova, calculamos o seu embedding, comparamos por
**similaridade do cosseno** com todas as da KB e devolvemos as mais parecidas (`top-k`) com o
impacto que tiveram. São esses os **precedentes** que a explicação XAI mostra ao investidor.

**Interface `Embedder` (padrão de engenharia):** definimos uma interface mínima
(`dim` + `encode(textos) -> matriz`) e duas implementações intermutáveis:
- **`HashingEmbedder`** — *baseline* lexical sem dependências (cada palavra cai numa posição do
  vetor por *hash*; conta-se e normaliza-se). Não capta significado, mas é **determinístico,
  reprodutível e rápido**. Permite testar todo o pipeline **sem instalar torch** e serve de
  **baseline para a ablação** na avaliação (SBERT *vs.* sobreposição de palavras).
- **`SbertEmbedder`** — SBERT real (`sentence-transformers`), a abordagem metodológica. O import
  é **tardio** (só quando se cria o objeto), pelo que o núcleo e os testes não dependem da stack
  pesada de ML. Trocar de embedder não muda mais nada — é a vantagem de programar contra uma
  interface.
- **Como explico ao júri em 3 frases:** "Comparo o SBERT com um *baseline* simples de
  sobreposição de palavras. Programei ambos contra a mesma interface, por isso a troca é
  transparente e a avaliação é justa. Assim mostro, com números, que o ganho do SBERT vem da
  semântica e não da implementação."
- **Validação empírica (S9):** com o SBERT real (`all-MiniLM-L6-v2`, 384 dim.), uma consulta
  *sem nenhuma palavra em comum* com a notícia ("Graphics processor maker lifts outlook on AI
  accelerator sales") recupera na mesma a notícia da NVIDIA sobre chips de IA como precedente nº 1.
  O baseline lexical não conseguiria (não há sobreposição de palavras) — é a prova concreta de que
  o SBERT capta **significado**, não apenas vocabulário. (Teste `tests/test_sbert_embedder.py`.)

**Alinhamento evento↔preço (anti-lookahead na prática):** o "dia do evento" é o **primeiro dia
de negociação >= data da notícia** (`searchsorted`). O impacto mede-se a partir do **fecho desse
dia**. Consequência importante e defensável: se a notícia já estava refletida na abertura (ex.: a
subida da NVIDIA em 2023-05-25), o nosso +1d **não** captura o salto já ocorrido — medimos só o
que um investidor ainda poderia ter apanhado. Isto evita inflacionar o impacto com informação já
"dentro" do preço.

## 12. Gatilho 2 — notícia → precedentes → explicação (implementação)
**O que é:** o segundo gatilho do sistema. Quando surge uma notícia financeira, o sistema
recupera notícias históricas semelhantes (da KB) e mostra o **impacto que tiveram** como
precedentes — não prevê preços, apenas apresenta evidência passada análoga (restrição §5.2).

**`news_fetcher`** (`src/news_fetcher/fetcher.py`): obtém notícias da camada live (Finnhub
`/company-news` e feeds RSS) e **normaliza-as para o mesmo esquema da KB** (`date, ticker,
headline`), para poderem ser comparadas por similaridade com o histórico. Tal como nos outros
componentes, separámos o **parsing** (puro, testado sem rede) do **HTTP** (invólucro fino, tardio).
Validado ao vivo (247 notícias AAPL via Finnhub).

**Explicação com precedentes** (`explain_news_impact`): produz um alerta rastreável — a notícia,
o **impacto médio** observado em eventos passados análogos (no horizonte escolhido) e a lista de
precedentes (data, ticker, similaridade, impacto e título), terminando sempre com a nota de que
**o impacto é o resultado observado no passado, não uma previsão**.

**Orquestração** (`src/main.py::run_news_trigger`): notícia → *embedding* → `KB.find_precedents`
→ `explain_news_impact` → (opcional) Telegram. O embedder usado tem de coincidir com o que
construiu a KB (a amostra usa `HashingEmbedder`; com `SbertEmbedder` usa-se a KB SBERT).
- **Como explico ao júri em 3 frases:** "Quando chega uma notícia, represento-a como vetor e
  procuro na base histórica as mais semelhantes. Mostro ao investidor o que aconteceu ao mercado
  a seguir a essas notícias passadas, com as fontes. É uma explicação por analogia e evidência —
  nunca uma previsão de preço."

## 13. *Streaming* de dados grandes (FNSPID)
**O que é:** o ficheiro de notícias do FNSPID tem dezenas de GB. Em vez de o descarregar inteiro,
lemo-lo em **blocos (*chunks*)** diretamente do URL e filtramos à medida (só os 15 tickers e a
janela 2018–2023 do `data_card.md`); só o subconjunto fica em disco. **Porque importa:** torna o
projeto tratável num portátil (R2 no `risk_register.md`) e mantém a reprodutibilidade — qualquer
pessoa recria o subconjunto com `scripts/download_data.py`. Os dados grandes ficam *gitignored*;
só **amostras pequenas** vão para `data/samples/` (e, de notícias de terceiros, só títulos — §5.4).

## 14. Avaliação da recuperação — precision@k, baselines e *lift*
**O que é:** para medir se os precedentes recuperados são mesmo análogos, usamos **precision@k**:
de entre os k mais semelhantes a uma notícia, que fração é relevante. Como "relevante" é caro de
julgar à mão, usamos um *proxy* automático: **mesmo setor** (data_card.md). Para não ser trivial
(o nome da empresa apareceria no título), fazemos recuperação **cross-ticker** (excluímos a própria
empresa) — isto testa analogia **temática**, não o nome.

**Baselines (essenciais para honestidade):** comparamos sempre com alternativas triviais —
**aleatório** (taxa-base = fração de candidatos do mesmo setor; o que se obteria por acaso) e
**recência** (os mais recentes). O *lift* = precisão do método − taxa-base mostra o valor
**acrescentado** pelos embeddings.

**Resultado real (`docs/evaluation/evaluation_results.md`, média±desvio de 5 seeds):** em 3.692 notícias reais
(Finnhub, 5 setores), **P@5: SBERT-MiniLM 0,549±0,014 e SBERT-MPNet 0,569±0,009 vs lexical 0,359 vs
aleatório 0,241 vs recência 0,105**. A **ablação de modelo** (MiniLM vs MPNet) mostra que a vantagem
não depende de um modelo específico — ambos batem largamente os baselines.
- **Como explico ao júri em 3 frases:** "Para avaliar a recuperação, pergunto se os precedentes
  vêm do mesmo setor, em modo cross-empresa para não ser trivial. O SBERT acerta ~57% no top-5,
  contra ~25% do acaso e ~36% de um baseline de palavras — ou seja, capta analogia temática real.
  Comparo sempre com baselines triviais para o ganho ser honesto e não um número solto."
- **Caveats (assumidos):** o setor é um *proxy* (não relevância humana); dados recentes do Finnhub
  (não o histórico multi-ano do FNSPID); títulos curtos limitam a semântica. Avaliação preliminar,
  reprodutível por `scripts/evaluate.py` (seed fixa).

## 15. Avaliação do detetor de anomalias — consistência da taxa de disparo
**O que é:** como mostrar, sem circularidade, que o z-score é melhor que um limiar fixo em %?
O argumento mais limpo é a **taxa de disparo entre tickers**: um limiar fixo (ex.: |retorno|≥3%)
dispara ~1% das vezes numa ação calma (KO) e ~35% numa volátil (TSLA/NVDA) — não é um detetor
universal. O z-score normaliza pela volatilidade recente, pelo que dispara a uma taxa quase
constante (~2%) em todos. Medimos a **amplitude** (máx−mín) da taxa entre tickers.

**Resultado real (`docs/evaluation/evaluation_anomaly.md`, yfinance 3 anos, 15 tickers):** amplitude da taxa
de disparo **z-score 0,015 vs limiar fixo 0,344** (>20× mais consistente). Como suporte, contra um
rótulo-proxy (movimento no percentil 99 por ticker): **F1 z-score 0,516 vs fixo 0,218**; ablação à
janela: F1 sobe com a janela (10d 0,385 → 20d 0,516 → 60d 0,678). *(Números congelados da corrida
final — a mesma da tese.)*
- **Como explico ao júri em 3 frases:** "Um limiar fixo em percentagem é injusto entre ações: numa
  volátil dispara a toda a hora, numa calma quase nunca. O meu z-score normaliza pela volatilidade
  recente, por isso deteta movimentos *invulgares para aquela ação*, com taxa de disparo estável.
  Mostro isto pela amplitude da taxa entre tickers (0,015 vs 0,344) — não depende de nenhum rótulo."
- **Caveat:** o rótulo-proxy é volatilidade-relativo como o z-score (alguma circularidade), por isso
  o argumento principal é a consistência da taxa, que **não** depende do rótulo.

## 16. Triagem de materialidade — o modelo TREINADO (RQ4)
**O que é:** um classificador supervisionado que responde a "esta notícia merece alerta?". Para cada
(título, ticker, dia do evento) estima **P(segue-se um movimento anormal)** — anormal = |retorno do
ticker − retorno do SPY| ≥ τ na janela (d, d+h] (primário: τ=2%, h=3). O rótulo vem do NOSSO event
study (não há anotação manual). **Nunca prevê direção nem preço** — só se o mercado reagiu com
tamanho invulgar, em qualquer direção.

**Anti-lookahead (a pergunta nº 1 do júri):** todas as features usam só dados ≤ fecho do dia d:
vol20 (desvio dos 20 retornos que TERMINAM em d−1), momentum 5d até d−1, retorno d−1→d (conhecido no
fecho de d; a janela do rótulo só começa aí), comprimento do título, setor, embedding SBERT. Um teste
unitário **muta os preços do futuro** e verifica que as features não mudam (e o rótulo sim).

**Protocolo honesto:** split TEMPORAL por dias únicos (70/15/15) + embargo (nenhuma janela de rótulo
atravessa blocos); **calibração de Platt** ajustada só na validação (sigmóide que transforma scores em
probabilidades honestas — cito Niculescu-Mizil & Caruana 2005); métricas PR-AUC (principal; o chão é a
prevalência = "alertar sempre"), ROC-AUC, Brier e **precisão@orçamento** (5 alertas/dia — mede a fadiga
de alertas). A comparação decisiva é contra a **LR só-volatilidade**: o modelo só é útil onde a bate.
6 famílias: alertar-sempre, LR-vol, LR-contexto, LR-texto, LR-completa (principal, interpretável),
gradient boosting (Friedman 2001; teto de capacidade).
- **Como explico ao júri em 3 frases:** "Treinei um classificador que estima a probabilidade de uma
  notícia ser seguida por um movimento anormal — materialidade, não direção; os rótulos vêm do meu
  próprio event study contra o SPY. O protocolo é temporal com embargo e calibração na validação, e um
  teste unitário prova que nenhuma feature vê o futuro. Só confio no modelo onde ele bate a baseline
  de só-volatilidade — e reporto o resultado seja ele qual for."
- **XAI:** na LR, o logit é uma soma EXATA de contribuições por feature (as dimensões do embedding
  agregadas em "conteúdo do título") — cada score vem com os fatores principais e a frase fixa
  "Triage evidence, not a forecast."

**Resultado FINAL (FNSPID 2018–2023, 79.753 exemplos, teste com prevalência 37,8% —
`docs/evaluation/evaluation_triage.md`):** PR-AUC — só-volatilidade **0,542** > só-contexto 0,538 >
contexto+texto 0,496 > GBM 0,469 > só-texto 0,439 > alertar-sempre 0,378. **Nenhum modelo com texto
bateu a baseline de volatilidade** (o resultado honesto pré-comprometido). MAS a triagem vale como
mecanismo de produto: **precisão@5 alertas/dia 0,632 vs 0,163** do alertar-sempre (quase 4×), com
probabilidades calibradas (Brier 0,218 vs 0,622).
- **Como explico ao júri em 3 frases (o resultado):** "Com 6 anos de dados, todos os modelos treinados
  ficam muito acima do chão alertar-sempre — dentro de um orçamento de 5 alertas/dia, a triagem quase
  quadruplica a precisão. Mas nenhum modelo que lê o texto do título bateu a baseline de
  só-volatilidade, portanto o sinal está no contexto de mercado, não nas palavras. Reporto isso tal
  como caiu — foi a segunda comparação justa 'aprendido vs simples' que a escolha transparente venceu."

## 17. Estatístico vs APRENDIDO — Isolation Forest perde para o z-score (M4)
**O que é:** desafiámos a nossa regra transparente com um detetor aprendido em igualdade: Isolation
Forest causal (features = retorno do dia + vol20 anterior; treina nos primeiros 250 dias; nunca vê o
futuro), avaliado na MESMA região que o z-score.

**Resultado real:** o IF perde claramente — **F1 0,271 (P 0,159 / R 0,913) vs z-score 0,530 na mesma
região**; e a taxa de disparo do IF varia entre tickers com amplitude **0,135 vs 0,015** do z-score
(falha o requisito de consistência que motivou o desenho).
- **Como explico ao júri em 3 frases:** "Não assumi que a regra estatística era melhor — testei-a
  contra um Isolation Forest com a mesma informação e sem lookahead. O modelo aprendido teve F1 de
  0,27 contra 0,53 do z-score e disparou de forma muito menos consistente entre ações. A comparação
  é que valida a escolha: com informação idêntica, o detetor interpretável foi não só mais simples
  como melhor."

## 18. Loop de pós-validação — a forma defensável do "reinforcement learning"
**O que é:** o runner regista cada decisão de triagem (probabilidade, gate, mantida/suprimida) em
`data/predictions_log.jsonl`; dias depois, `scripts/post_validate.py` rotula cada decisão **maturada**
(a janela (d, d+3] já fechou) com o que REALMENTE aconteceu — a mesma regra do treino — e escreve
métricas ao vivo (precisão das mantidas vs base rate, Brier, calibração) + a receita de retreino.
É **aprendizagem contínua com rótulos atrasados + monitorização (MLOps)** — não é RL clássico.
- **Como explico ao júri em 3 frases:** "As decisões de hoje são validadas com a realidade de daqui a
  três dias: registo cada decisão e, quando a janela fecha, comparo com o que aconteceu de facto.
  Isso dá-me precisão e calibração ao vivo e dados novos para retreinar. Não é reinforcement learning
  clássico porque não há ciclo ação-ambiente — os meus alertas não movem o mercado; é aprendizagem
  contínua com rótulos atrasados."
