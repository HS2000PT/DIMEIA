# PLANO_V2.md — Programa de redesenho (produto + tese + marca)

> Documento-mestre da reformulação pedida na Sessão 42. Multi-sessão, multi-dispositivo.
> Ler com o `CLAUDE.md`. Substitui `PLANO_MELHORIAS.md` como plano ativo.
> **Data:** 2026-07-29 · **Entrega:** 2026-09-13 (≈6,5 semanas)

---

## 0. Veredicto em três frases

O produto tem um problema de **posicionamento e de cadência**, não de motores: os motores (deteção,
retrieval, triagem, XAI) estão validados e são bons. O que falta é (a) dizer em UMA frase o que o
sistema promete, (b) responder à pergunta que o utilizador faz mesmo — *"é a minha empresa ou é o
mercado?"* — e (c) uma camada de linguagem que torne tudo isto legível. Tudo o resto que apeteça
construir é **Track B**: excelente para o produto e para o LinkedIn, perigoso para 13 de setembro.

---

## 1. Correções honestas (erros meus, corrigidos por revisão adversária)

1. **`abnormal_returns` NÃO está adormecido.** É chamado em `investigator/triage/dataset.py:102`
   para construir o rótulo da RQ4 — os números congelados da triagem assentam nele. O que falta é
   uma decomposição **contemporânea** (o movimento de HOJE), que é coisa diferente e exige beta
   rolante. Eu tinha dito "existe mas não é usado": errado.
2. **`beta = 1.0` é atacável.** `event_study.py` usa retorno-do-ticker menos retorno-do-mercado com
   beta implícito de 1,0. O beta da NVDA face ao SMH não é 1,0 → um "company-specific −0,6%" sem
   beta estimado está simplesmente errado. Qualquer arguente com formação em finanças ataca isto
   primeiro.
3. **`CLAUDE.md` tem uma entrada obsoleta:** diz que `thesis-pt` ch2–ch6 são "scaffolds vazios".
   Medido no disco hoje: ch2 32k, ch3 55k, ch4 30k, ch5 46k, ch6 15k caracteres. A tese PT **está
   traduzida**. A entrada antiga tem de ser riscada ou continua a enganar todas as sessões futuras.

---

## 2. As duas pistas (a decisão estruturante)

O aluno quer um produto grande ("worldmonitor adaptado", redes sociais, muitos dados) **e** uma tese
entregue a 13/09. As duas coisas cabem — em pistas separadas.

| | **Track A — a tese** | **Track B — o produto** |
|---|---|---|
| Prazo | 13 setembro, inegociável | sem prazo; continua depois |
| Regra | **aditivo**; congelados byte-iguais | liberdade total |
| Critério | cada item é **avaliável** e defensável | cada item traz valor ao utilizador |
| Risco | churn bilingue mata o prazo | nenhum |
| Destino | dissertação + defesa | LinkedIn, repo público, portfólio |

**Regra de ouro:** nada do Track B entra na tese como *facto novo*; entra como **Trabalho Futuro**
(que pontua) ou como secção de produto claramente datada — exatamente o padrão já usado no projeto
para o threshold 3,0→1,5 e para a ablação RQ4-ext.

**O maior risco identificado (citação da revisão académica):** *"trocar uma tese defensável por uma
indefensável"* — prosa que descreve um sistema que já não corresponde à sua própria avaliação
congelada, com três avaliações a meio que o aluno não consegue explicar sob interrogatório.

---

## 3. Posicionamento (a camada de "marketing" pedida)

### A ideia central

Quando uma ação se mexe, o investidor de retalho faz sempre as mesmas três perguntas:

1. **Isto é invulgar — ou é normal para esta ação?**
2. **É a *minha empresa* ou é o mercado todo?**
3. **Já aconteceu algo assim — e o que se seguiu?**

As ferramentas gratuitas não respondem a nenhuma. A Robinhood e o Yahoo dão uma percentagem. O
ChatGPT escreve uma narrativa plausível sem números nem base histórica. O Seeking Alpha e o
StockTwits dão opiniões. Um terminal Bloomberg responde às três — por ~2.000 USD/mês.

> **Frase de posicionamento.** *O InvestiGator responde às três perguntas que qualquer investidor faz
> quando uma ação se mexe — é invulgar, é a empresa ou o mercado, e já aconteceu antes — com números
> reais e precedentes históricos reais, de graça, e mostrando as contas.*

### Porque é que isto é defensável

- **Contra as gratuitas:** relatam, não contextualizam. Nenhuma decompõe um movimento em mercado vs
  empresa. Nenhuma devolve precedente histórico quantificado.
- **Contra os LLM genéricos:** um LLM não sabe que −5,2% são 2,5σ *para esta ação*, não calcula um
  resíduo ajustado ao beta, e não ancora nada em 79.000 casos indexados com desfechos medidos. O
  nosso narrador usa o LLM **só para a língua, nunca para os factos**.
- **Contra os terminais pagos:** mesma classe de pergunta, custo zero, raciocínio todo à vista.

### O mapa que dá elegância à tese

| Pergunta do investidor | Motor | Estado |
|---|---|---|
| É invulgar? | z-score rolante + perfil de normalidade | existe (RQ1) |
| Empresa ou mercado? | **decomposição contemporânea com beta rolante** | **a construir** |
| Já aconteceu? | retrieval SBERT + event study | existe (RQ2) |
| Merece a minha atenção? | triagem calibrada | existe (RQ4) |
| Posso simplesmente perguntar? | narrador ancorado | **a construir** (RQ3) |

---

## 4. Personas e casos de uso (para o Cap. 1 e para os slides)

- **P1 — o detentor de longo prazo ansioso.** ~10 ações, vê 2×/semana, fica em pânico com vermelho,
  não distingue "ignora isto" de "presta atenção". Valor entregue: **permissão para ignorar ruído**.
- **P2 — o investidor de retalho ativo.** 8–15 nomes, vê várias vezes ao dia, afoga-se em alertas que
  só dizem "TSLA −4%". Valor entregue: **contexto já dentro do alerta**.

| ID | Cenário | Motores |
|---|---|---|
| UC1 | Triagem matinal: o que merece atenção hoje? | anomalia, triagem, decomposição |
| UC2 | Queda súbita: porque caiu a NVDA, é ela ou o setor? | decomposição, ligação a notícia |
| UC3 | Notícia nova: este tipo de manchete já importou? | retrieval, event study |
| UC4 | Catalisador agendado: resultados daqui a 2 dias | calendário + perfil histórico |
| UC5 | Pergunta livre em linguagem natural | narrador sobre todos os motores |

**"Os alertas chegam tarde" — a resposta honesta.** Um alerta reativo é, por definição, posterior ao
facto. Duas soluções legítimas, nenhuma exige previsão: (a) baixar a latência de deteção; (b) expor
eventos **agendados e conhecidos de antemão** (resultados) — informação genuinamente antecipada que
não viola nenhuma restrição ética.

---

## 5. Track A — o que construir para a tese (4 coisas avaliadas, não 9 por avaliar)

Ordenado. Cada item é **aditivo**, **avaliável** e defensável numa arguição.

### A1. Contrato de cadência + instrumentação de tempo `[~12h] — SEMANA 1, bloqueante`
Hoje a cadência **emerge** de quatro gates independentes (`threshold 1.5`, `min_similarity 0.45`,
`max_per_ticker_per_day 2`, `min_materiality 0.5`) e ninguém — nem o autor — consegue dizer numa frase
o que chega e o que não chega. Todas as queixas de "o conteúdo é mau" são sintoma disto.
- Escrever **uma página** que declara o que o sistema promete enviar e o que promete nunca enviar.
- **`detected_at` / `sent_at` no `HistoryEntry`** (campos opcionais, retrocompatíveis, ~1h).
  **Verificado: o sistema hoje NÃO consegue produzir um número de latência** — só guarda a data ao dia.
  Sem isto, nenhuma afirmação sobre latência na tese tem prova.
- Registar **qual das 5 fontes de preço serviu cada pedido** (`fallback_daily` já devolve a fonte e
  o código deita-a fora) → tabela real de disponibilidade do free tier.

### A2. Decomposição contemporânea mercado / setor / idiossincrática `[~16h]`
A linha que muda comportamento: *"−4,0% hoje = −0,3% mercado, −3,1% setor, −0,6% específico da empresa."*
Converte a maioria dos alertas vermelhos de "a tua ação afundou" em "o mercado caiu, a tua ação não
fez nada de invulgar".
- Beta rolante estimado contra SPY + um ETF de setor, na **mesma janela de 20 dias** do detetor.
- `beta = 1` só como fallback **explicitamente rotulado** quando a regressão é instável.
- **Entra como linha de explicação, não como gatilho** → a RQ1 congelada fica intacta.
- Avaliação: ablação aditiva (quantos alertas mudariam de leitura), documento `evaluation_*.md` novo.

### A3. Varrimento de política sobre dados congelados `[~10h]` ← *melhor relação nota/hora*
`min_materiality: 0.5` é uma constante posta à mão em cima de um modelo **calibrado por Platt** — e a
calibração existe precisamente para escolher um limiar, coisa que o projeto nunca faz.
- Varrer o limiar sobre a validação congelada → curva de custo esperado sob um rácio explícito
  falso-alarme:falha → derivar o ponto de operação.
- Converte *"o nosso modelo de texto perdeu para a volatilidade"* em *"caracterizámos o regime de
  política em que o score aprendido ganha"*.
- Mesma técnica para as outras constantes mágicas (`0.45`, `2/dia`, `120d`, `1.5`, `2 dias`) → fecha
  a crítica "porquê 0,45?" que é a pergunta de júri mais provável.
- **Zero dados novos, zero retreino.** É um script de análise sobre artefactos congelados.

### A4. Estudo de utilidade — **já está desenhado, falta correr** `[~8h]`
`docs/design/usefulness_study.md` (172 linhas) já tem protocolo completo: H1–H3, desenho
intra-sujeito contrabalançado, condição A (facto nu) vs B (alerta completo), 6 alertas reais
incluindo o caso difícil tema≠direção, rubrica, consentimento, 6–10 participantes não-especialistas,
15 min cada.
- A RQ3 é a **única** linha "ainda em aberto" no Cap. 6. Correr isto fecha-a.
- Uma tarde a recrutar + um dia a analisar. **Zero código novo, zero API nova, não parte nada.**

### A5. Narrador ancorado — UMA função pura ✅ **FEITO (2026-07-29)**
`narrate(evidence) -> str`. Recebe o dicionário de evidência que os motores já produzem, devolve
prosa. **Proibido introduzir qualquer número ausente do input.**
- **Não é um chatbot multi-turno. Não é um sistema multi-agente.** Rotular quatro chamadas de função
  como "agentes" é pior do que omitir a cadeira — os arguentes reconhecem isso de imediato.
- Avaliação de fidelidade **offline**: conjunto de casos com output de motor conhecido → medir a taxa
  a que a geração afirma um número ausente. Mais recusa em perguntas de previsão ("vai subir?").
- Fallback determinístico obrigatório: se o LLM falhar, sai o texto atual. **A demo não pode morrer
  em frente ao júri.**

**Como correu, e a lição que vale para a tese.** A v1 da guarda era uma **blocklist** de padrões
proibidos. Um red team de 3 adversários independentes — cada um obrigado a REPRODUZIR a sua
alegação com Python antes de a poder afirmar — encontrou **29 furos confirmados**. Os dois piores:
`"AMD gained 8.50%"` passava quando o motor calculou **−8,50%** (o conjunto permitido fazia
`lstrip("+-")`), e apóstrofos de contrações (`it's`, `isn't`) eram lidos como aspas, criando
"citações" falsas que isentavam números injetados e previsões.

A conclusão é estrutural: **uma blocklist de linguagem natural perde sempre** (paráfrases
infinitas vs lista finita). A v2 inverte para **allowlist**: vocabulário fechado de ~360 palavras
neutras, números negativos só válidos com sinal, aspas só duplas verdadeiras, atribuição validada
contra a evidência. Os 21 exploits ficaram como testes de regressão permanentes
(`tests/test_narrator_core.py::TestRedTeam`).

Detalhe completo em [`docs/design/narrator_guard.md`](../docs/design/narrator_guard.md).

### A6. Minerar o funil que já foi recolhido `[~6h]`
`docs/evaluation/alert_funnel.md`: **AAPL 135 manchetes relevantes → 0 alertas.** AMZN 91 → 0.
NFLX 83 → 0. MSFT 75 → 0. GOOGL 71 → 0. JPM 60 → 0. NVDA 56 → 0.
**Que gate os matou?** Similaridade, triagem, ou frescura? Análise de atrito por gate sobre dados que
já estão na branch `alerts-history`. É avaliação operacional genuína de um sistema implantado.

### A7. Escrita (o que já está feito e só precisa de ser posto em evidência) `[~8h]`
- **ONNX int8**: cosseno médio 0,992 vs sentence-transformers, top-3 idêntico em 20/23 consultas
  reais, SHA256 fixado, ~23 MB, CPU-only, sem torch. É o artefacto de **engenharia de deep learning**
  mais forte do projeto e está enterrado num `.md` de avaliação. Promovido a subsecção do Cap. 3/4
  fecha parcialmente ANN/Deep Learning **e** Privacidade/Segurança (controlo da cadeia de fornecimento).
- **Scoreboard ao vivo**: `post_validate.py` já dá precisão 0,667 vs base rate 0,455, Brier 0,229 em
  n=33. Deixar acumular mais duas semanas duplica o n a custo zero.

---

## 6. O que NÃO construir (e o argumento honesto de cada corte)

| Cortado | Porquê |
|---|---|
| **Recomendações/price targets de analistas** | Importar previsões de terceiros para um sistema cuja tese fundadora é "nunca prevê preços" é auto-contradição. O júri encontra-a. Cortar **por princípio** e dizê-lo alto no Cap. 6 pontua mais do que a feature. |
| **Carteira: posições, custo médio, concentração, correlação** | Segundo produto, com modelo de dados próprio e superfície de privacidade própria (dados financeiros pessoais + LLM de terceiros = problema RGPD para *resolver*, não para descrever). E "as tuas 4 maiores são uma só aposta" é aconselhamento, seja como for redigido — empurra para recomendação personalizada (MiFID II), a fronteira exata que a afirmação ética mais limpa da tese depende de não cruzar. **Escrever a recusa como parágrafo de ética.** |
| **Insider / MSPR / Form 4** | Free tier não verificado (relatos de 403); o fallback SEC EDGAR é 20h+ de XML para dados atrasados dias — estruturalmente incapazes de explicar o movimento de hoje, que é a única função dos alertas. |
| **Feed de SEC filings** | Genuinamente útil, genuinamente grátis — e genuinamente um parser novo, fail-open, data card, testes e prosa bilingue para uma feature sem avaliação associada. Trabalho Futuro. |
| **Reescrita do Streamlit do zero** | Já foi redesenhado nas sessões 33, 36, 37 e 41. O critério de rejeição é estético ("both suck") — **não tem condição de paragem**. Redesenhar sim; reescrever do zero não. |
| **Chatbot multi-turno / agentes / RAG com memória** | Um LLM com cinco ferramentas não é um sistema multi-agente. Reivindicá-lo entrega ao júri a superfície de ataque mais fácil que existe. |
| **RQ5 e RQ6 novas** | Os rótulos RQ aparecem em ch1, ch6, ambos os abstracts, o paper IEEE, 19 slides, o guia de 77 slides e dois documentos de defesa. Renumerar é churn puro em duas línguas. Latência vira limitação medida; privacidade vira secção do Cap. 4 com tabela de modelo de ameaça. |
| **Bolsas europeias na superfície do produto** | Já construído, fora do âmbito US, valor zero para as personas. Manter o módulo, parar de o destacar. |

---

## 7. Tempo real — decisão a rever

O aluno escolheu **Oracle Cloud + WebSocket**. A revisão adversária recomenda **cortar o WebSocket**:

- ~30h para reconnect/backoff, agregação tick→barra, dedup, wheels ARM.
- **Ambas as personas de utilizador dizem, independentemente, que não notariam a diferença entre 5
  segundos e 5 minutos.**
- **Não responde a nenhuma questão de investigação.** Latência nunca foi RQ e não pode passar a ser.
- Socket sempre aberto numa caixa gratuita que a Oracle reclama por baixa utilização de CPU — e que
  o aluno não sabe depurar em semanas de exame.
- **A Oracle cortou o Always Free a meio de 2026** e há relatos de "out of host capacity" na criação.

**Alternativa recomendada:** o loop de polling de 60s **que já está escrito** (`run_alerts.py --watch`,
`archive/deploy/setup_vm.sh`, unidade systemd). 8–12h em vez de 30h, latência ~1 min em vez de ~2h — 99% do
ganho por 30% do custo.

**Salvaguarda obrigatória, seja qual for a escolha:** timebox de **1 dia** na semana 1, com critério
de sucesso escrito de antemão (24h de uptime + heartbeat + uma latência ponta-a-ponta medida). Se
falhar, escreve-se o parágrafo honesto de limitação — que **já existe em forma anterior e já é
defensável** — e segue-se. O resto da semana 1 tem de ser completável independentemente.

**Bottleneck a corrigir:** `_push_history_safe` faz `git add/commit/pull --rebase/push` **a cada
ciclo**. A 60s isto compete com o workflow do Actions na mesma branch. Solução: bufferizar localmente
e fazer flush em temporizador lento (10–15 min), desacoplado da deteção.

---

## 8. Fontes de dados — o que vale mesmo a pena

Verificado nesta sessão. **Track A só precisa da primeira linha.**

| Fonte | Dá | Acesso | Pista |
|---|---|---|---|
| **SPY + ETF de setor** (yfinance) | a decomposição de A2 | já temos | **A** |
| **Finnhub earnings calendar** | datas de resultados | chave que já temos — **sondar antes de planear** | A (mínimo) |
| **FRED** | taxas, macro US | grátis, chave | B |
| **GDELT** | volume e tom de notícia global por entidade | aberto, sem chave | B |
| **ApeWisdom** | menções Reddit/wallstreetbets por ticker | **aberto, sem registo** | B |
| **Twelve Data** | 800 pedidos/dia (vs 25/dia da Alpha Vantage) | chave grátis | B |
| **Marketaux** | notícia + sentimento + tickers, 100/dia | chave grátis | B |
| **SEC EDGAR** | filings, Form 4 | aberto, só User-Agent | B / Futuro |
| **CoinGecko, Polymarket, EIA, ECB, BIS** | contexto cripto / probabilidades de eventos / energia / taxas | abertos | B |

**Nota sobre o calendário de resultados:** construir o mínimo (lista datada para 10 tickers em cache
JSON) e gastar o esforço na **análise**: que fração dos disparos |z|>limiar cai a ±1 dia de um evento
agendado, e a precisão da triagem difere entre agendado e não-agendado? Uma tabela de estratificação,
~1 dia, conteúdo académico real. Se o endpoint der 403, curar 10 tickers × 8 trimestres à mão num CSV
e dizê-lo — honesto e suficiente.

---

## 9. O que roubar ao worldmonitor (Track B, com crédito)

O co-orientador **Rafael Silva** recomendou o [worldmonitor.app](https://www.worldmonitor.app)
(código AGPL-3.0, [koala73/worldmonitor](https://github.com/koala73/worldmonitor)). **Deve ser citado
na tese e o Rafael creditado nos agradecimentos** — é honesto e é um gesto certo.

Ideias adaptáveis, por ordem de valor:

1. **Convergência multi-sinal.** O worldmonitor dispara quando sinais independentes se corroboram.
   Adaptado: um alerta ganha força quando anomalia de preço **+** pico de volume **+** notícia
   relevante **+** precedente forte convergem. É melhor produto **e** conteúdo académico real
   (fusão de sinais para priorização, avaliável contra baselines de sinal único).
2. **Dossier por entidade.** Eles: clicar num país → índice + componentes + brief com citações +
   timeline de 7 dias. Nós: **dossier por ticker**.
3. **Citação em todo o lado, zero score caixa-preta.** É literalmente a nossa postura XAI —
   validação externa de que a escolha está certa.
4. **Índice composto com componentes à vista** (o Country Instability Index deles). Nós: um
   "índice de atenção" por ticker com todos os componentes visíveis.
5. **Estética:** escuro, denso em dados, sem signup, sem tour, carrega em segundos, paleta por sinal.
6. **Command palette (⌘K).** Barato, e faz parecer produto a sério.

> ⚠️ O worldmonitor tem 65+ fornecedores, 5.132 commits e um autor a tempo inteiro. É **referência de
> ambição, não de âmbito**. Track B.

---

## 10. Marca

**Crítica honesta do logo atual** (`app/assets/logo.svg`): mete três metáforas num só ícone
(sobrolho, olho de réptil, linha de mercado); a 16px o sobrolho funde-se com o olho e a linha vira
borrão; o olho de pupila em fenda lê-se como predador — subtilmente **contra a mensagem** de um
produto cuja ética é "mostramos evidência, nunca caçamos nem prevemos"; e a paleta verde-pântano+ouro
lê-se mais casino do que fintech. Não há wordmark, nem variante monocromática, nem variante de ícone
de app. É um ícone, não um sistema de marca.

**Direção escolhida pelo aluno: "The Tail".** Um traço contínuo que se lê ao mesmo tempo como a
cauda serrilhada de um jacaré e como uma linha de mercado a subir. Uma ideia, uma forma, legível a
16px, funde *Invest* (a linha) e *Gator* (a cauda) sem desenhar um animal literal.

**Entregáveis:** ícone SVG, lockup horizontal com wordmark, variante monocromática, favicon/ícone de
app, e `.streamlit/config.toml` afinado. Paleta: reformar o verde-pântano+ouro → tela quase-preta ou
tinta profunda com **uma** cor-sinal viva (esmeralda ou lima ácida). Apresentar 2–3 conceitos
renderizados para escolha antes de commitar seja o que for.

---

## 11. Tese — o que muda

- **Cap. 1 Problem Statement** → personas P1/P2, as três perguntas, proposta de valor explícita. É o
  "quem/porquê/o quê" pedido e mapeia em CO1.
- **Cap. 2** → matriz comparativa a sério (Robinhood, Yahoo, TradingView, Seeking Alpha, Koyfin,
  Finviz, assistentes LLM genéricos, Bloomberg como referência paga) pontuada contra as três
  perguntas. Literatura nova só para geração ancorada / fidelidade.
- **Cap. 4** → secção **Casos de Uso** (UC1–UC5 + diagrama UML), a decomposição, o contrato de
  cadência, secção de privacidade com tabela de modelo de ameaça.
- **Cap. 5** → os quatro estudos ficam **intocados**; entram estudos novos para decomposição,
  varrimento de política e fidelidade do narrador.
- **Cap. 6** → veredictos revistos, RQ3 fechada pelo estudo de utilidade, cortes justificados como
  posição (não como omissão), Trabalho Futuro rico.
- **RQs: continuam QUATRO.** RQ3 estende-se (fidelidade da narração + piloto humano); RQ4 ganha o
  enquadramento decisório. **Zero renumeração.**

**Regra dura:** números congelados (P@5 0,595; triagem 0,542/0,496/0,632/0,163; benchmarks de
embedders) e os bundles em `models/` ficam **byte-iguais**, verificados por `git diff` vazio em cada
gate. Afirmação nova exige experiência nova, nunca edição de experiência antiga.

---

## 12. Onde gastar os ~80 € de Fable

O Fable compensa onde **julgamento, qualidade de escrita e síntese de contexto grande** decidem;
desperdiça-se em trabalho mecânico.

| Gastar em | Porquê | Quando ligar |
|---|---|---|
| **Prosa da tese**: Cap. 1 posicionamento, Cap. 4 desenho, casos de uso, Cap. 6 | É o artefacto avaliado. Tem de ler-se humano e sobreviver a interrogatório. | **Fase 3** (semanas 4–5) |
| **Narrador + arnês de fidelidade** | Subtil, alto risco, sensível à qualidade; é a contribuição de topo. | **Fase 2** (semana 3) |
| **Redesenho do Streamlit numa passagem, a partir de spec detalhada** | Autocontido e denso em design — o instinto do aluno aqui está certo. | **Fase 2** (semana 3) |
| **Slides, narrativa de defesa, conceitos de logo** | Síntese criativa; a apresentação vale metade da nota. | **Fase 4** (semana 6) |

**NÃO gastar Fable em:** testes, clientes de API, plumbing de dados, refactors, CI, tradução
bilingue. É mecânico e um modelo mais barato faz igual.

---

## 13. Logística que o aluno pediu

- **Chaves num só sítio.** Um `.env` único na raiz + `.env.example` sincronizado + espelho em GitHub
  Actions Secrets. Criar `docs/design/keys.md` com um bloco único para copiar/colar e a origem de
  cada chave. **Nunca versionar o `.env`.**
- **Repositório público com um único commit.** **Já está construído:**
  `scripts/make_public_bundle.py --git` parte de `git ls-files` (nunca inclui `.env`, segredos nem
  corpora), remove caminhos internos (`progress/`, `CLAUDE.md`, `.claude/`, `docs/defence/`,
  `slides/`, CHECKLIST, RELATORIO), corre scan de segredos e faz **1 commit**. Nunca faz push — o
  push é clique do aluno. Testado: 210 ficheiros, 21 internos excluídos, scan limpo.
- **Hospedagem 24/7 grátis.** Com a VM Oracle já existe `archive/deploy/investigator-app.service` para servir
  o Streamlit na mesma máquina (porta 8501). Somar **Cloudflare Tunnel** dá HTTPS + domínio próprio,
  grátis, sem abrir portas. Alternativa para o chat: **Gradio em Hugging Face Spaces** (grátis,
  sempre-ligado na prática).
- **Mensagem final PT-PT ao orientador.** No fim: PDF da tese, slides, link da app, link do canal
  Telegram, link do repo público, e o que ele deve ver primeiro. Fica para a Fase 4.

---

## 14. Calendário

| Fase | Semanas | Conteúdo | Gate |
|---|---|---|---|
| **1 — Fundações** | 1–2 | A1 (cadência + timestamps + provenance), VM com timebox de 1 dia, A6 (funil), A3 (varrimentos) | testes verdes; `git diff` vazio nos congelados |
| **2 — Motores + produto** | 3–4 | A2 (decomposição), A5 (narrador + fidelidade), redesenho do Streamlit **com critérios de aceitação escritos ANTES**, marca | **congelamento de features no fim da semana 4** |
| **3 — Escrita** | 5 | Cap. 1/2/4/6 bilingue, estudos novos no Cap. 5, A7 (ONNX em evidência) | ambas as teses compilam, 0 erros |
| **4 — Defesa** | 6 | slides, demo gravada, A4 (estudo de utilidade), mensagem ao orientador, repo público | 2 simulacros completos |

**Timebox duro no redesenho da app:** wireframe + critérios de aceitação escritos **antes** de código,
3 dias, **uma** ronda de revisão, screenshot recapturado e **congelado** no fim da semana 4. Sem isto,
o critério estético não tem condição de paragem — foi o que aconteceu nas sessões 33/36/37/41.

---

## 15. Decisões tomadas (2026-07-29)

1. ✅ **Tempo real = polling de 60s na VM Oracle.** WebSocket **cortado** (o aluno tinha escolhido
   WebSocket antes da análise adversária; reverteu com a evidência). Código já escrito:
   `run_alerts.py --watch`, `archive/deploy/setup_vm.sh`, unidade systemd. Timebox de 1 dia na semana 1.
2. ✅ **Cortes da §6 aceites na íntegra** — price targets de analistas, carteira/holdings,
   insider/MSPR/Form 4, feed de SEC filings, reescrita do Streamlit do zero, chatbot multi-turno,
   enquadramento multi-agente, RQ5/RQ6 novas, bolsas europeias em destaque.
   Cada um vira **parágrafo justificado no Cap. 6**, não feature meia-construída.

### Ainda por decidir

3. **Conta Oracle Cloud** — criar (desbloqueia o polling; custa cliques, não engenharia).
4. **Fornecedor de LLM grátis** para o narrador — a escolher e a **sondar** antes de depender dele.
5. **Ordem do Track B** depois da entrega.
