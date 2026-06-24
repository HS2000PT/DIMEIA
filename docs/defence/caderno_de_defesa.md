# Caderno de Defesa — CLARION (PT-PT)

> Documento de estudo para a defesa. Reúne, em português, **o que foi feito e porquê**, para o aluno
> dominar todo o trabalho. Não é a tese (essa é em EN-GB); é o guião para a preparar e defender com calma.
> Atualizar à medida que a tese evolui. Fontes internas: `docs/decisions/learning.md`,
> `docs/decisions/glossary.md`, `progress/DECISIONS.md`, `progress/SESSIONS.md`.

---

## 1. O problema, o âmbito e a contribuição

**Problema.** O investidor de retalho (não profissional) vive sob *sobrecarga de informação*: milhares de
ações mexem-se em contínuo e as notícias financeiras chegam sem pausa. As ferramentas que ajudam a
interpretar estes sinais são institucionais, opacas, ou ambas. O comportamento deste investidor é guiado
pela **atenção** (compra o que está nas notícias / com movimentos extremos) — logo, faz sentido intervir
exatamente nesses momentos, com **contexto e explicação**, e não com mais ruído.

**O que o sistema faz (CLARION).** Vigia o mercado US (NYSE/NASDAQ) e dispara um alerta quando: (1) há um
**movimento abrupto** de preço (anomalia estatística), ou (2) chega uma **notícia relevante**. Cada alerta
traz a **cadeia de raciocínio completa**: o evento detetado, o raciocínio, as fontes e **precedentes
históricos** (notícias análogas do passado e o impacto que tiveram). Entrega via **Telegram**.

**Âmbito (o que NÃO faz).** Sem previsão de preços, sem trading algorítmico, sem APIs pagas. Mede impacto
**passado** como evidência; nunca prevê. Isto é uma escolha de honestidade e de defensibilidade.

**Contribuição (enquadramento permanente).** É uma tese de **Engenharia de IA**. A contribuição **não** é
inventar algoritmos — é **integrar, aplicar e avaliar criticamente** componentes existentes num sistema
funcional, explicável e reproduzível, com uma **metodologia documentada de correlação notícia–impacto**.
Usar modelos/ferramentas existentes **é** o trabalho de engenharia.

> **Defesa em 3 frases:** "Construí um sistema que avisa o investidor de retalho de movimentos de mercado
> e notícias relevantes, e — ao contrário das apps comuns — explica cada alerta de forma rastreável, com
> precedentes históricos reais. A contribuição é de engenharia de IA: integrei deteção estatística,
> recuperação semântica e estudo de evento num todo coerente, explicável e reproduzível. Não prevejo
> preços; mostro evidência do passado, com honestidade sobre as limitações."

---

## 2. Decisões e porquês (as que tenho de saber defender)

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

## 3. Componentes — o que faz, como funciona, e "como explico ao júri em 3 frases"

### 3.1 Detetor de anomalias (Gatilho 1)
- **O que faz:** assinala o retorno diário de hoje como anormal se o |z-score| ultrapassar um limiar *k*.
- **Como funciona:** z = (retorno − média móvel) / desvio-padrão móvel, calculados na janela de dias
  **estritamente anteriores** (sem lookahead). Devolve a decisão + todas as quantidades que a produziram.
- **Defesa em 3 frases:** "Normalizo o movimento de hoje pela volatilidade recente da própria ação. Assim,
  um detetor único é justo entre ações calmas e voláteis — algo que um limiar fixo em % não consegue.
  E como exponho o z-score, a janela e o limiar, o alerta é auto-explicativo."

### 3.2 Base de conhecimento histórica + motor de correlação (núcleo, Gatilho 2)
- **O que faz:** dada uma notícia nova, recupera as *k* notícias passadas mais semelhantes e mostra o
  impacto que tiveram.
- **Como funciona:** cada notícia → embedding SBERT; semelhança por cosseno; impacto por estudo de evento
  a partir do **fecho** do 1.º dia de negociação ≥ data da notícia (anti-lookahead).
- **Enquadramento académico (forte!):** isto é **Raciocínio Baseado em Casos** (CBR — Aamodt & Plaza 1994).
  Cada notícia histórica + o seu impacto é um *caso*; a notícia nova é a consulta; a semelhança faz o
  *retrieve*; o impacto dos precedentes é o *reuse*. Paro de propósito no retrieve+reuse (não faço *revise*
  → não há previsão). Saber dizer "o meu motor é o núcleo de um sistema CBR" mostra domínio do paradigma.
- **Defesa em 3 frases:** "Transformo cada notícia num vetor que capta o significado e procuro as mais
  parecidas no histórico — é raciocínio baseado em casos. Para cada precedente mostro o que aconteceu ao
  preço a seguir, medido sempre *depois* do evento. É recuperação de evidência, não previsão."

### 3.3 Motor de explicação (XAI)
- **O que faz:** monta o texto do alerta a partir dos objetos calculados a montante.
- **Como funciona:** para o gatilho de mercado, indica o movimento, z-score, limiar e janela; para o de
  notícias, lista os precedentes (data/ticker/semelhança/impacto/título) + impacto médio + aviso de
  não-previsão. Testado automaticamente: a explicação reproduz exatamente cada precedente recuperado.
- **Defesa em 3 frases:** "A explicação não é gerada à parte — é renderizada dos mesmos números que o
  sistema calculou, por isso não pode divergir da lógica. Chamo a isto *fidelidade por construção*.
  Um teste automático confirma que nenhum precedente é inventado nem omitido."

### 3.4 Entrega (Telegram)
- **O que faz:** envia o alerta completo numa única mensagem.
- **Defesa em 1 frase:** "Escolhi o Telegram por ser gratuito, ubíquo e com API de bot simples; um alerta
  real foi entregue com sucesso nos testes."

---

## 4. Resultados e limitações (honestos)

**Recuperação de precedentes (RQ2).** Precision@5 *cross-ticker* por setor, média de 5 seeds:
- SBERT-MiniLM **0,549 ± 0,014**; SBERT-MPNet **0,569 ± 0,009**; lexical 0,359; aleatório 0,241; recência 0,105.
- **Leitura:** ~2,3× acima do acaso e bem acima do lexical; a vantagem é do *embedding semântico* (robusta
  ao modelo). É uma avaliação **preliminar** (notícias recentes do Finnhub, não o FNSPID multi-ano).

**Detetor de anomalias (RQ1).** Janela fixa 2023-06 a 2026-06, 15 tickers:
- Amplitude da taxa de disparo entre ações: **z-score 0,015** vs **limiar fixo 0,344** (>20× mais consistente).
- F1 vs proxy de movimento extremo: **z-score 0,516** vs fixo 0,218. Ablação de janela: 0,385 / 0,516 / 0,678
  (10/20/60 dias). **Argumento principal = a consistência (sem rótulo);** o F1 é suporte (rótulo é proxy).

**Explicação (RQ3).** Fidelidade **conseguida** (por construção + teste automático). Utilidade para o
investidor: **ainda não medida** com estudo humano → reportada como limitação, não como resultado.

**Limitações (dizer antes que o júri pergunte):** proxy de setor (não julgamento humano); corpus recente
(não FNSPID multi-ano); títulos curtos limitam a semântica; rótulo de anomalia é volatilidade-relativo;
sem estudo humano de utilidade; **por desenho, sem previsão/trading**.

---

## 5. Mapa do repositório (para navegar e mostrar)
```
thesis/    a dissertação (LaTeX, EN-GB) — 6 capítulos + front matter + apêndice
src/       o sistema, um pacote por componente
scripts/   dados, figuras, build/verify/sessão
docs/      design/ · evaluation/ · decisions/ · defence/ (este ficheiro) · _archive/
progress/  TRACKER (checklist) + SESSIONS (registo)
```
- Resultados reprodutíveis: `scripts/evaluate.py` (recuperação) e `scripts/evaluate_anomaly.py` (anomalia)
  escrevem `docs/evaluation/*` e as figuras em `thesis/figures/`.
- Análise extra pronta: `scripts/evaluate_per_sector.py` dá a recuperação **por setor** (precision@k +
  *lift* por setor) — basta o corpus Finnhub (re-obter com a `FINNHUB_API_KEY` na `.env`).
- Tudo o que é número na tese sai de um script com seed fixa.

---

## 6. Perguntas difíceis do júri (e respostas preparadas)

**P: Isto não é só usar bibliotecas existentes?**
R: Sim — e numa tese de *Engenharia* de IA é isso que se pede: a contribuição é a integração, a metodologia
de correlação notícia–impacto, as escolhas justificadas e a avaliação crítica honesta. O valor está no
*sistema coerente e explicável*, não num algoritmo novo. Além disso, o núcleo assenta num paradigma
reconhecido — **Raciocínio Baseado em Casos** (Aamodt & Plaza 1994): recuperar casos análogos e reusar o
seu resultado como evidência. Não é ad hoc; é CBR aplicado a notícias–mercado, com explicação por exemplos.

**P: Porque não usaram um LLM / deep learning, que dá melhores resultados?**
R: Por defensibilidade. O objetivo é explicabilidade para um não-especialista; um modelo opaco contraria
isso (Rudin 2019). Para o sinal em causa (uma série de retornos; títulos curtos), o ganho não justifica a
perda de transparência e o custo. Deixo LLMs como trabalho futuro, com a infraestrutura pronta (FAISS para
escala).

**P: A precision@5 de 0,55 é boa?**
R: É ~2,3× o acaso (0,24) e bem acima do baseline lexical (0,36), com desvio pequeno (5 seeds). É uma
medida *honesta* do valor acrescentado, e **preliminar** — assumo que o corpus é recente; o FNSPID
multi-ano é o passo seguinte.

**P: O proxy de setor não é fraco?**
R: É um proxy automático, sim — por isso é uma limitação explícita e por isso dou primazia ao argumento
*sem rótulo* (consistência da taxa de disparo). Um estudo humano de relevância é trabalho futuro.

**P: Como garantem que não há lookahead?**
R: O z-score usa só dias *anteriores*; o impacto é medido só *depois* do evento, a partir do fecho do 1.º
dia de negociação ≥ data da notícia. Está em código e testado.

**P: Como sei que a explicação é verdadeira?**
R: É renderizada dos mesmos objetos calculados → fiel por construção; e há um teste automático que verifica
que reproduz exatamente os precedentes recuperados, sem inventar.

**P: Usaram IA para escrever a tese?**
R: Sim, declarado honestamente no front matter (assistência do Claude Code); dirigi o trabalho, revi e
validei tudo, e as ideias, decisões e conteúdo final são da minha responsabilidade.
