# Caderno de Defesa — InvestiGator (PT-PT)

> Documento de estudo para a defesa. Reúne, em português, **o que foi feito e porquê**, para o aluno
> dominar todo o trabalho e **visualizar o fluxo de dados e passos** (§2). Não é a tese (essa é em EN-GB);
> é o guião para a preparar e defender com calma. Estudar a par com os `slides/` (apresentação) e com a
> própria tese. Fontes internas: `docs/decisions/learning.md`, `docs/decisions/glossary.md`,
> `progress/DECISIONS.md`, `progress/SESSIONS.md`.

---

## 1. O problema, o âmbito e a contribuição

**Problema.** O investidor de retalho (não profissional) vive sob *sobrecarga de informação*: milhares de
ações mexem-se em contínuo e as notícias financeiras chegam sem pausa. As ferramentas que ajudam a
interpretar estes sinais são institucionais, opacas, ou ambas. O comportamento deste investidor é guiado
pela **atenção** (compra o que está nas notícias / com movimentos extremos); logo, faz sentido intervir
exatamente nesses momentos, com **contexto e explicação**, e não com mais ruído.

**O que o sistema faz (InvestiGator).** Vigia o mercado US (NYSE/NASDAQ) e dispara um alerta quando: (1) há um
**movimento abrupto** de preço (anomalia estatística), ou (2) chega uma **notícia relevante**. Cada alerta
traz a **cadeia de raciocínio completa**: o evento detetado, o raciocínio, as fontes e **precedentes
históricos** (notícias análogas do passado e o impacto que tiveram). Entrega via **Telegram**.

**Âmbito (o que NÃO faz).** Sem previsão de preços, sem trading algorítmico, sem APIs pagas. Mede impacto
**passado** como evidência; nunca prevê. Isto é uma escolha de honestidade e de defensibilidade.

**Contribuição (enquadramento permanente).** É uma tese de **Engenharia de IA**. A contribuição **não** é
inventar algoritmos: é **integrar, aplicar e avaliar criticamente** componentes existentes num sistema
funcional, explicável e reproduzível, com uma **metodologia documentada de correlação notícia–impacto**.
Usar modelos/ferramentas existentes **é** o trabalho de engenharia.

> **Defesa em 3 frases:** "Construí um sistema que avisa o investidor de retalho de movimentos de mercado
> e notícias relevantes, e, ao contrário das apps comuns, explica cada alerta de forma rastreável, com
> precedentes históricos reais. A contribuição é de engenharia de IA: integrei deteção estatística,
> recuperação semântica e estudo de evento num todo coerente, explicável e reproduzível. Não prevejo
> preços; mostro evidência do passado, com honestidade sobre as limitações."

---

## 2. O workflow visual (dados e passos)

> O pedido central: **ver** todo o fluxo de dados e passos. Aqui está, em diagramas. As versões
> "bonitas" estão na tese (figura da arquitetura, do fluxo mestre e os **diagramas de sequência** dos dois
> gatilhos, Cap. 4) e nos `slides/`.

**(A) Construção offline da Base de Conhecimento (uma só vez):**
```
FNSPID: noticia + precos diarios
   |  alinhar ao 1.o dia de negociacao >= data da noticia  (evento e_i)
   v
 embedding SBERT do titulo   +   impacto do FECHO de e_i  (+1d, +3d, +5d)
   |
   v
 Base de Conhecimento  =  um "caso" por noticia
   caso = { data, ticker, titulo, vetor, impacto[+1/+3/+5] }
```

**(B) Gatilho 1 — movimento de mercado (a cada dia):**
```
precos live (yfinance) -> log-returns r_t
   |  janela de 20 dias ANTERIORES -> media (mu), desvio (sigma)
   v
 z = (r_t - mu) / sigma
   |
   v
 |z| > k (=3) ?  --nao-->  (sem alerta)
   | sim
   v
 explicacao { z, mu, sigma, janela, limiar }  ->  Telegram
```

**(C) Gatilho 2 — notícia nova (quando há notícia):**
```
noticia live (Finnhub/RSS)
   |  embedding SBERT do titulo
   v
 cosseno vs Base de Conhecimento  ->  top-k precedentes (mais semelhantes)
   |  impacto de cada um (+1/+3/+5d, do FECHO do evento)   [anti-lookahead]
   v
 explicacao { precedentes + impacto medio + aviso de nao-previsao }  ->  Telegram
```

> **Explicar o fluxo ao júri (1 frase):** "Offline construo uma memória de casos (notícia→impacto); em
> produção, cada gatilho transforma dados *live* em evidência e converge num único passo de explicação
> antes de enviar, e nada usa informação do futuro."

---

## 3. Decisões e porquês (as que tenho de saber defender)

| Decisão | Porquê (defesa curta) |
|---|---|
| **Estrutura de 6 capítulos (MEIA)** | É a estrutura canónica das dissertações de referência do ISEP/GECAD; o júri reconhece-a. |
| **Deteção por z-score** (e não Isolation Forest/deep) | Transparência: consigo explicar *porque* disparou (nº de desvios-padrão). Para uma única série de retornos, a capacidade extra de modelos opacos não compensa a perda de explicabilidade (Rudin 2019). |
| **SBERT (embeddings de frase) + cosseno** | Capta significado contextual (melhor que léxicos/word2vec), mas dá vetores diretamente comparáveis e baratos (ao contrário do BERT cru ou de LLMs). Reprodutível e gratuito. |
| **Estudo de evento (+1/+3/+5 dias)** | Forma padrão e reprodutível de medir impacto (Fama 1969; Brown & Warner 1985). Medido **depois** do evento → caracteriza um resultado, não uma previsão. |
| **Explicação por desenho transparente** (não só LIME/SHAP) | O alerta é renderizado a partir dos próprios objetos calculados → é **fiel por construção**, não uma aproximação de uma caixa preta. |
| **Duas camadas de dados (histórica FNSPID + live)** | Esquema partilhado → live e histórico comparáveis. FNSPID dá notícias alinhadas a preços sem scraping. |
| **Avaliação com argumento sem-rótulo (consistência da taxa de disparo)** | Rótulos de "anomalia verdadeira" são escassos/circulares; a consistência da taxa entre ações não depende de rótulo → evidência mais forte. |
| **Janela de avaliação FIXA (2023-06 a 2026-06)** | Reprodutibilidade: `period=3y` mudava com a data de execução; janela fixa dá sempre os mesmos números. |
| **Só APIs gratuitas / Telegram** | Restrição não negociável do projeto; e Telegram é gratuito e ubíquo. |

---

## 4. Componentes — o que faz, como funciona, e "como explico ao júri em 3 frases"

### 4.1 Detetor de anomalias (Gatilho 1)
- **O que faz:** assinala o retorno diário de hoje como anormal se o |z-score| ultrapassar um limiar *k*.
- **Como funciona:** z = (retorno − média móvel) / desvio-padrão móvel, calculados na janela de dias
  **estritamente anteriores** (sem lookahead). Devolve a decisão + todas as quantidades que a produziram.
- **Defesa em 3 frases:** "Normalizo o movimento de hoje pela volatilidade recente da própria ação. Assim,
  um detetor único é justo entre ações calmas e voláteis, algo que um limiar fixo em % não consegue.
  E como exponho o z-score, a janela e o limiar, o alerta é auto-explicativo."

### 4.2 Base de conhecimento histórica + motor de correlação (núcleo, Gatilho 2)
- **O que faz:** dada uma notícia nova, recupera as *k* notícias passadas mais semelhantes e mostra o
  impacto que tiveram.
- **Como funciona:** cada notícia → embedding SBERT; semelhança por cosseno; impacto por estudo de evento
  a partir do **fecho** do 1.º dia de negociação ≥ data da notícia (anti-lookahead).
- **Enquadramento académico (forte!):** isto é **Raciocínio Baseado em Casos** (CBR, Aamodt & Plaza 1994).
  Cada notícia histórica + o seu impacto é um *caso*; a notícia nova é a consulta; a semelhança faz o
  *retrieve*; o impacto dos precedentes é o *reuse*. Paro de propósito no retrieve+reuse (não faço *revise*
  → não há previsão). Saber dizer "o meu motor é o núcleo de um sistema CBR" mostra domínio do paradigma.
- **Defesa em 3 frases:** "Transformo cada notícia num vetor que capta o significado e procuro as mais
  parecidas no histórico; é raciocínio baseado em casos. Para cada precedente mostro o que aconteceu ao
  preço a seguir, medido sempre *depois* do evento. É recuperação de evidência, não previsão."

### 4.3 Motor de explicação (XAI)
- **O que faz:** monta o texto do alerta a partir dos objetos calculados a montante.
- **Como funciona:** para o gatilho de mercado, indica o movimento, z-score, limiar e janela; para o de
  notícias, lista os precedentes (data/ticker/semelhança/impacto/título) + impacto médio + aviso de
  não-previsão. Testado automaticamente: a explicação reproduz exatamente cada precedente recuperado.
- **Defesa em 3 frases:** "A explicação não é gerada à parte: é renderizada dos mesmos números que o
  sistema calculou, por isso não pode divergir da lógica. Chamo a isto *fidelidade por construção*.
  Um teste automático confirma que nenhum precedente é inventado nem omitido."

### 4.4 Entrega (Telegram)
- **O que faz:** envia o alerta completo numa única mensagem.
- **Defesa em 1 frase:** "Escolhi o Telegram por ser gratuito, ubíquo e com API de bot simples; um alerta
  real foi entregue com sucesso nos testes."

### 4.5 Exemplos reais, traçados passo a passo (saber recitar!)

**Gatilho 1 (anomalia) — TSLA, 24-10-2024 (reação a resultados):**
1. Preços live → log-return do dia: **r = +19,82%** (≈ +22% em preço).
2. Janela dos 20 dias **anteriores** → **μ = −0,92%**, **σ = 2,73%**.
3. z = (19,82 − (−0,92)) / 2,73 = **+7,61**.
4. |7,61| > 3 → **anomalia**; o alerta expõe r, μ, σ, janela e limiar.
   *Reprodutível:* `scripts/evaluate_anomaly.py` (janela fixa).

**Gatilho 2 (notícia) — consulta "Nvidia demand surges on AI chip orders":**
1. Embedding do título → cosseno vs Base de Conhecimento → top-3:
   - NVDA "Nvidia guidance surges…" (sem. 0,60) → +5d **+3,5%**
   - MSFT "Microsoft cloud growth… AI demand" (sem. 0,38) → +5d **+10,9%**  ← **cross-ticker!**
   - NVDA "Nvidia unveils new AI accelerator…" (sem. 0,38) → +5d **+4,9%**
2. Impacto médio +5d ≈ **+6,5%**; o alerta lista os precedentes + média + aviso "resultado passado, não
   previsão". *Reprodutível:* sobre `data/samples/kb_sample.jsonl` (encoder transparente); em produção, SBERT.

> **Porque é que o MSFT aparece numa consulta sobre a NVIDIA?** Porque a recuperação é por **significado**
> (tema "procura de IA / data-center"), não por nome de empresa; é a generalização *cross-ticker* que a
> avaliação mede. Saber explicar isto mostra que domino o núcleo do sistema.

---

## 5. Resultados e limitações (honestos)

**Recuperação de precedentes (RQ2).** Precision@5 *cross-ticker* por setor, média de 5 seeds (3.714 notícias):
- SBERT-MiniLM **0,514 ± 0,015**; SBERT-MPNet **0,538 ± 0,011**; lexical 0,346; aleatório 0,240; recência 0,126.
- **Leitura:** ~2,1× acima do acaso e bem acima do lexical; a vantagem é do *embedding semântico* (robusta
  ao modelo). É uma avaliação **preliminar** (notícias recentes do Finnhub, não o FNSPID multi-ano).
- **Por setor:** o *lift* é maior na energia (+0,377) e saúde (+0,348), de vocabulário distintivo, e menor no
  consumo (+0,100). A tecnologia tem a P@5 bruta mais alta (0,712) mas porque domina o corpus (taxa-base 0,429).

**Detetor de anomalias (RQ1).** Janela fixa 2023-06 a 2026-06, 15 tickers:
- Amplitude da taxa de disparo entre ações: **z-score 0,015** vs **limiar fixo 0,344** (>20× mais consistente).
- F1 vs proxy de movimento extremo: **z-score 0,516** vs fixo 0,218. Ablação de janela: 0,385 / 0,516 / 0,678
  (10/20/60 dias). **Argumento principal = a consistência (sem rótulo);** o F1 é suporte (rótulo é proxy).

**Explicação (RQ3).** Fidelidade **conseguida** (por construção + teste automático). Utilidade para o
investidor: **ainda não medida** com estudo humano → reportada como limitação, não como resultado.

**Triagem de materialidade (RQ4) — o modelo que EU treinei.** Corpus FNSPID 2018–2023: **79.753**
exemplos (título, ticker, dia do evento), 1.501 dias únicos, 14/15 tickers (a Meta é "FB" no corpus);
split temporal por dias únicos + embargo 5; calibração de Platt só na validação; teste com prevalência
0,378.
- PR-AUC (teste): **só-volatilidade 0,542** > só-contexto 0,538 > contexto+texto 0,496 > GBM 0,469 >
  só-texto 0,439 > alertar-sempre 0,378.
- **Precisão@5 alertas/dia: 0,632 vs 0,163** do alertar-sempre (quase 4×); Brier 0,218 vs 0,622.
- **Veredicto (pré-comprometido, na tese):** *"No on the text hypothesis; yes on the mechanism"* — a
  triagem vale como mecanismo de produto, mas nenhum modelo que lê o texto bateu a baseline de
  volatilidade ⇒ o sinal está no contexto de mercado. É a **2.ª** comparação justa "aprendido vs
  simples" que a escolha transparente vence (a 1.ª: Isolation Forest causal perde para o z-score,
  F1 0,271 vs 0,530 na mesma região).
- **Em produção:** a variante só-contexto (1,8 KB, stack leve) pontua no runner/app, off por defeito
  (`news.min_materiality`); cada decisão é registada e **pós-validada** dias depois com o resultado
  real (`scripts/post_validate.py` → `live_monitoring.md`) — aprendizagem contínua com rótulos
  atrasados, não RL clássico.
- **Como explico ao júri em 3 frases:** "Treinei um classificador que estima a probabilidade de uma
  notícia ser seguida por um movimento anormal — materialidade, não direção; os rótulos vêm do meu
  próprio event study contra o SPY. O protocolo é temporal com embargo, a calibração é só na validação,
  e um teste unitário muta o futuro para provar que não há lookahead. Dentro de 5 alertas/dia quase
  quadruplica a precisão, mas nenhum modelo com texto bateu a volatilidade — e reporto isso tal como caiu."

**Limitações (dizer antes que o júri pergunte):** proxy de setor (não julgamento humano); corpus de
recuperação recente (a **triagem** já usa o FNSPID multi-ano; a KB de recuperação multi-ano é futuro);
títulos curtos limitam a semântica; rótulo de anomalia é volatilidade-relativo;
a semelhança capta **tema, não direção** (um *cluster* pode misturar subidas e descidas → a média é
evidência sobre um tema, não previsão); sem estudo humano de utilidade; **por desenho, sem previsão/trading**.

### 5.5 Mapa dos números validados (de onde vem cada um)

> **Re-corridos na Fase E (2026-06-27):** os scripts reproduzem **exatamente** estes números (a única
> diferença ao re-correr é o carimbo temporal). É a resposta mais forte a "isto é reprodutível?".

| Número | Valor | Script | Output / local na tese |
|---|---|---|---|
| P@5 SBERT-MiniLM | 0,514 ± 0,015 | `evaluate.py` | `evaluation_results.md` · Cap. 5 (CS2) |
| P@5 SBERT-MPNet | 0,538 ± 0,011 | `evaluate.py` | idem |
| P@5 lexical / aleatório / recência | 0,346 / 0,240 / 0,126 | `evaluate.py` | idem |
| Lift por setor: energia / saúde / consumo | +0,377 / +0,348 / +0,100 | `evaluate_per_sector.py` | `evaluation_per_sector.md` · Cap. 5 |
| Amplitude de disparo: z-score vs fixo | 0,015 vs 0,344 | `evaluate_anomaly.py` | `evaluation_anomaly.md` · Cap. 5 (CS1) |
| F1: z-score vs fixo | 0,516 vs 0,218 | `evaluate_anomaly.py` | idem |
| Ablação de janela (10/20/60 d) | 0,385 / 0,516 / 0,678 | `evaluate_anomaly.py` | idem |
| Anomalia real TSLA (24-10-2024) | z = +7,61 | (yfinance, janela fixa) | Cap. 5 (CS1), tabela trabalhada |
| IF causal vs z-score (mesma região) | F1 0,271 vs 0,530 | `evaluate_anomaly.py` | `evaluation_anomaly.md` §4 · Cap. 5 (CS1) |
| Triagem: PR-AUC das 6 famílias | 0,542/0,538/0,496/0,469/0,439/0,378 | `train_triage.py` | `evaluation_triage.md` · Cap. 5 (CS4) |
| Triagem: precisão@5/dia · Brier | 0,632 vs 0,163 · 0,218 vs 0,622 | `train_triage.py` | idem |
| Dataset de triagem | 79.753 exemplos, 0 descartes | `build_dataset.py` | `data/triage_dataset.csv` · Cap. 5 (CS4) |
| Contexto: mercado US / posse de ações / IA | US\$62,2T · 62/87/28% · 81/71% | fontes primárias (Fase E) | Cap. 1 |

---

## 6. Mapa do repositório (para navegar e mostrar)
```
thesis/    a dissertação (LaTeX, EN-GB) — 6 capítulos + front matter + apêndice
paper/     artigo IEEE (IEEEtran) destilado da tese validada
slides/    slides de defesa (Beamer, 14 frames)
src/       o sistema, um pacote por componente
scripts/   dados, figuras, build/verify/sessão
docs/      design/ (how_to_run, arquitetura, data_card, APIs) ·
           evaluation/ (resultados reprodutíveis) ·
           decisions/ (citation_log, learning, glossary, review_log,
                       implementation_review, page_audit) ·
           defence/ (este ficheiro) · _archive/
progress/  TRACKER (checklist) + SESSIONS (registo)
```
- **Como correr o sistema:** `docs/design/how_to_run.md` (guia do operador, testado).
- **Provas de rigor (Fases C/D/E):** `review_log.md` (revisão crítica), `implementation_review.md`
  (estatística re-validada), `page_audit.md` (50 citações re-verificadas).
- Resultados reprodutíveis: `scripts/evaluate.py` (recuperação) e `scripts/evaluate_anomaly.py` (anomalia)
  escrevem `docs/evaluation/*` e as figuras em `thesis/figures/`.
- Análise extra pronta: `scripts/evaluate_per_sector.py` dá a recuperação **por setor** (precision@k +
  *lift* por setor); basta o corpus Finnhub (re-obter com a `FINNHUB_API_KEY` na `.env`).
- Tudo o que é número na tese sai de um script com seed fixa.

---

## 7. Perguntas difíceis do júri (e respostas preparadas)

**P: Isto não é só usar bibliotecas existentes?**
R: Sim, e numa tese de *Engenharia* de IA é isso que se pede: a contribuição é a integração, a metodologia
de correlação notícia–impacto, as escolhas justificadas e a avaliação crítica honesta. O valor está no
*sistema coerente e explicável*, não num algoritmo novo. Além disso, o núcleo assenta num paradigma
reconhecido, o **Raciocínio Baseado em Casos** (Aamodt & Plaza 1994): recuperar casos análogos e reusar o
seu resultado como evidência. Não é ad hoc; é CBR aplicado a notícias–mercado, com explicação por exemplos.
E não fico só pela integração: **treinei um modelo** (triagem de materialidade, RQ4) com ciclo de ML
completo — rótulos do meu event study, protocolo temporal, calibração, avaliação contra baselines e
pós-validação em produção.

**P: O vosso modelo treinado perdeu para a baseline de volatilidade. Isso não é um fracasso?**
R: Não — é o resultado de uma comparação **pré-comprometida** no protocolo (Cap. 3): eu escrevi, antes de
treinar, que se o modelo não batesse a volatilidade isso seria reportado tal como é. A RQ4 fica respondida
com evidência: o sinal de materialidade está no contexto de mercado, não no texto do título (com esta
representação). E a triagem vale na mesma como mecanismo: quase 4× a precisão dentro do orçamento diário
(0,632 vs 0,163), com probabilidades calibradas. Uma tese que só mostra vitórias é menos credível do que
uma que mostra o teste justo e o desfecho real.

**P: Como garantem que o modelo de triagem não vê o futuro (lookahead)?**
R: Três camadas: (1) convenção de features fixada — tudo calculável no fecho do dia do evento (vol20 e
momentum terminam no dia ANTERIOR; a janela do rótulo começa no fecho do próprio dia); (2) split temporal
por dias únicos com embargo de 5 dias (nenhuma janela de rótulo atravessa blocos); (3) um **teste unitário
que muta os preços do futuro** e verifica que nenhuma feature muda (e que o rótulo muda). É verificação
executável, não uma promessa.

**P: A ideia de "reinforcement learning" que refere no trabalho futuro — porquê não RL a sério?**
R: Porque não há MDP: os meus alertas não afetam o mercado, logo não existe o ciclo ação→ambiente→recompensa
do RL clássico. A forma defensável da ideia está implementada: o **loop de pós-validação** — cada decisão é
registada e, quando a janela fecha, rotulada com o que realmente aconteceu, dando métricas ao vivo e dados
para retreino (aprendizagem contínua com rótulos atrasados). *Contextual bandits* para afinar o limiar de
alerta ficam documentados como a extensão aprendida natural.

**P: Porque não usaram um LLM / deep learning, que dá melhores resultados?**
R: Por defensibilidade. O objetivo é explicabilidade para um não-especialista; um modelo opaco contraria
isso (Rudin 2019). Para o sinal em causa (uma série de retornos; títulos curtos), o ganho não justifica a
perda de transparência e o custo. Deixo LLMs como trabalho futuro, com a infraestrutura pronta (FAISS para
escala).

**P: A precision@5 de ~0,51 é boa?**
R: É ~2,1× o acaso (0,240) e bem acima do baseline lexical (0,346), com desvio pequeno (~0,01, 5 seeds).
É uma medida *honesta* do valor acrescentado, e **preliminar**: assumo que o corpus é recente; o FNSPID
multi-ano é o passo seguinte. (O MPNet chega a 0,538, o que mostra que a vantagem é dos *embeddings*
semânticos, não de um modelo específico.)

**P: O proxy de setor não é fraco?**
R: É um proxy automático, sim, por isso é uma limitação explícita e por isso dou primazia ao argumento
*sem rótulo* (consistência da taxa de disparo). Um estudo humano de relevância é trabalho futuro.

**P: Como garantem que não há lookahead?**
R: O z-score usa só dias *anteriores*; o impacto é medido só *depois* do evento, a partir do fecho do 1.º
dia de negociação ≥ data da notícia. Está em código e testado.

**P: Como sei que a explicação é verdadeira?**
R: É renderizada dos mesmos objetos calculados → fiel por construção; e há um teste automático que verifica
que reproduz exatamente os precedentes recuperados, sem inventar.

**P: Porque excluem o próprio ticker na avaliação (cross-ticker)?**
R: É uma escolha de **avaliação**, não do sistema. Se deixasse a NVIDIA recuperar as suas próprias
notícias, ganhava por correspondência trivial de nome; ao excluir o próprio ticker, obrigo o motor a
**generalizar entre empresas** (analogia temática), que é o que interessa. Em produção, o alerta mostra os
precedentes mais semelhantes, incluindo do mesmo ticker, que são legítimos para o utilizador.

**P: No exemplo real, um título *positivo* da NVIDIA recuperou notícias de ameaça competitiva e mostrou impacto médio −1,97%. Isso não engana o utilizador?**
R: É a pergunta certa, e respondê-la mostra que percebo o método. A semelhança por *embeddings* capta o
**tema** ("chips de IA para data-center"), não a **direção** (o sentimento): por isso um título positivo
pode recuperar um *cluster* de ameaça competitiva cujos desfechos foram negativos. A média é evidência sobre
*como um tema se moveu*, **não uma previsão** para este caso; por isso mostro sempre os precedentes um a um
e termino com o aviso de não-previsão. É também a razão para explicar com **evidência verificável** e não com
narrativa persuasiva (Lee & See 2004; Bansal 2021, sobre *over-reliance*). Melhorias de produto já
identificadas: de-duplicar precedentes quase iguais e **sinalizar quando o cluster discorda na direção**,
para o utilizador ver incerteza em vez de falso consenso. (Nota: o +6,5% do exemplo do Cap. 3 e o −1,97%
aqui não se contradizem: são bases de conhecimento, horizontes e *encoders* diferentes, e nenhum é previsão.)

**P: Isto é mesmo reprodutível?**
R: Sim. Seeds fixas, dependências fixadas e cada número sai de um script versionado. Na validação final
(Fase E) **voltei a correr os três scripts e obtive exatamente os mesmos números**; a única diferença foi
o carimbo temporal. Está em `docs/decisions/implementation_review.md` e `page_audit.md`.

**P: Usaram IA para escrever a tese?**
R: Sim, declarado honestamente no front matter (assistência do Claude Code); dirigi o trabalho, revi e
validei tudo, e as ideias, decisões e conteúdo final são da minha responsabilidade.
