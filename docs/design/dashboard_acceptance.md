# dashboard_acceptance.md — critérios da reconstrução densa (escritos ANTES do código)

> **Estatuto: proposta com a premissa REVISTA.** Este documento existe porque a mesma disciplina
> que travou o ciclo de redesenhos da app atual ([`app_acceptance.md`](app_acceptance.md)) tem de
> valer para a reconstrução. Mas escrevê-lo obrigou a reler o plano contra o que foi **medido
> entretanto**, e duas das cinco ideias que davam identidade à reconstrução **já não se sustentam**.
> Isso está na §1, antes de qualquer critério, porque muda o que vale a pena construir.

---

## 1. O que a medição desta sessão fez ao plano

O plano da reconstrução (estilo worldmonitor, adaptado e não copiado) assentava em cinco
elementos. Depois dos Estudos de Caso 5–8, o estado deles é este:

| Elemento previsto | Estado | Porquê |
|---|---|---|
| **Score de convergência** na matriz | ❌ **cai** | Mede-se: ganha em 1 de 3 orçamentos (`evaluation_convergence.md`). Mostrar um score fundido que a medição não sustenta seria exatamente o que esta tese recusa. |
| **Badges de tipo de evento** | ❌ **cai** | Mede-se: os grupos não supervisionados são fracos demais (silhueta 0,084) e a rubrica só cobre 15,1% do corpus (`evaluation_event_taxonomy.md`). Um badge errado é pior do que badge nenhum. |
| **Densidade sem scroll** | ✅ mantém | Não depende de sinal novo. É desenho. |
| **Faixa de contexto de mercado** | ✅ mantém | Os dados já existem (`market_hours`, decomposição). |
| **Paleta de comandos** | ✅ mantém | Navegação, não sinal. |

**Consequência honesta:** a reconstrução perdeu as duas capacidades que a distinguiriam da app
atual em **conteúdo**. O que sobra é uma reconstrução de **forma**: mais densa, mais rápida de
navegar. Isso pode valer a pena, mas é um argumento diferente e mais fraco do que o inicial, e
quem decidir avançar deve decidi-lo sabendo isso.

**Uma capacidade nova sobreviveu e não precisa de reconstrução nenhuma:** o **detetor de volume**
(`anomaly_detector/volume.py`) responde a "e com quanta gente a negociar?" e encaixa numa coluna da
app **atual**, com o rácio legível ("3,2× o habitual") que já vem pronto.

---

## 2. A condição de paragem

A reconstrução vive em `app/dashboard.py`. A app atual (`app/streamlit_app.py`) **fica no ar,
intocada**, até que a nova passe **todos** os critérios abaixo **mais** todos os de
`app_acceptance.md`. Se não passar até à data de corte, **a app atual entrega-se** e a
reconstrução vira Trabalho Futuro. Nos dois casos não se perde nada, e é isso que torna o risco
gerível por construção e não por otimismo.

Alterar este documento é uma decisão consciente do aluno, não um efeito secundário de estar a
olhar para o ecrã.

---

## 3. Critérios (executáveis)

Cada critério tem de ser verificável por um teste ou por uma medição, não por opinião.

### 3.1 Densidade

| # | Critério | Como se verifica |
|---|---|---|
| D1 | Toda a watchlist (10 tickers) visível **sem scroll** a 1366×768 | captura Playwright a essa dimensão; contar linhas visíveis |
| D2 | Cada linha mostra movimento, \|z\|, e a decomposição mercado/setor/empresa **sem clique** | teste que afirma a presença dos três por linha |
| D3 | A decomposição é codificada em **forma** (barra assinada) e não só em número | inspeção da captura; a barra existe no DOM |
| D4 | **Volume** aparece como coluna, com o rácio legível | teste que afirma a coluna e o formato "N,N×" |

### 3.2 Rastreabilidade

| # | Critério | Como se verifica |
|---|---|---|
| R1 | Todo o número no ecrã chega ao motor que o produziu em **um clique** | teste que percorre cada número e afirma o destino |
| R2 | Nenhum número é recalculado na app: os alertas são espelho do canal | já garantido; teste de regressão mantém-se |
| R3 | A latência só aparece quando foi **medida** | critério herdado de `app_acceptance.md` |

### 3.3 Desempenho

| # | Critério | Como se verifica |
|---|---|---|
| P1 | Carrega a frio em **< 5 s** | cronometrar o arranque headless, 3 corridas, mediana |
| P2 | Trocar de ticker **não** re-renderiza os outros | o teste de `len(metric)==1` já existente |

### 3.4 Honestidade (herdados, não negociáveis)

| # | Critério |
|---|---|
| H1 | A promessa aparece **uma** vez, como identidade da página |
| H2 | Zero números previstos; zero recomendações; zero price targets |
| H3 | Precedentes sempre com a moldura tema ≠ direção |
| H4 | **Nenhum score que a medição não sustente** — inclui, hoje, o score de convergência fundido e os badges de tipo de evento |

> H4 é o critério que este documento acrescenta ao conjunto anterior, e é o que faz a ligação
> entre a avaliação e o produto. Sem ele, a reconstrução poderia mostrar um número bonito que os
> Estudos de Caso 5 e 8 dizem não valer.

### 3.5 O que a convergência PODE mostrar

O score fundido cai, mas a leitura **humana** sobrevive e é melhor: `agreement_count` diz quantos
dos sinais ultrapassaram o seu próprio limiar.

| # | Critério |
|---|---|
| C1 | Se a concordância for mostrada, é como **contagem verificável** ("3 de 4 sinais"), nunca como score fundido |
| C2 | Os componentes que contam ficam visíveis, para o utilizador poder conferir a contagem |

---

## 4. Fora de âmbito, explicitamente

Mapa; 56 camadas; 65 fornecedores de dados; mercados de previsão; sockets ao vivo. É a escala do
worldmonitor, não a deste projeto, e listá-la aqui evita que reapareça a meio.

---

## 5. Recomendação de quem escreveu isto

Com a premissa revista, **a reconstrução deixou de ser o passo de maior valor**. A app atual foi
construída contra critérios escritos, passa 15 testes, e as duas capacidades que justificariam
substituí-la foram medidas e não se sustentam. O caminho com melhor retorno passa a ser
**aditivo**:

1. **Acrescentar a coluna de volume** à app atual (dados prontos, rácio legível pronto, custo
   baixo, valor imediato para a persona do trader).
2. **Acrescentar a contagem de concordância** como número verificável, sem score fundido.
3. Manter a reconstrução densa como Trabalho Futuro, com estes critérios já escritos, para que
   quem lhe pegue comece com a condição de paragem definida.

Isto **não** é reduzir o âmbito por falta de tempo. É a mesma regra que os Estudos de Caso 5–8
aplicaram ao sistema: construir, medir, e deixar a medição decidir, incluindo quando ela diz que
não. Uma reconstrução feita depois de a sua premissa cair seria trabalho a fingir que a medição
não aconteceu.
