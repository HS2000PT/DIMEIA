# app_acceptance.md — Critérios de aceitação da app (escritos ANTES do código)

> **Porque este documento existe.** A app foi redesenhada nas sessões 33, 36, 37 e 41. O
> critério de rejeição foi sempre estético ("both suck"), e um critério estético **não tem
> condição de paragem** — por construção, há sempre outra versão possível. Este documento é a
> condição de paragem. Quando todos os critérios abaixo estiverem verdes, a app está FEITA,
> independentemente de apetecer mexer mais.
>
> **Regra:** alterar este documento é uma decisão consciente do aluno, não um efeito
> secundário de estar a olhar para o ecrã.

---

## 1. A app existe para responder a três perguntas

São as mesmas três do posicionamento (`progress/PLANO_V2.md` §3). Cada ecrã responde a uma.
Se um elemento do ecrã não ajuda a responder à pergunta desse ecrã, **não pertence ali**.

| Ecrã | A pergunta | Motor que responde |
|---|---|---|
| **Hoje** | *O que na minha watchlist merece a minha atenção agora?* | z-score + triagem |
| **Ticker** | *Isto é a empresa ou é o mercado? Já aconteceu antes?* | decomposição + retrieval |
| **Método** | *Porque é que eu havia de acreditar nisto?* | avaliação congelada |

Três ecrãs. Não quatro. A justificação de cada corte está na §5.

---

## 2. Especificação por ecrã (componentes nomeados)

### 2.1 Hoje — o ecrã de abertura

| Componente | Conteúdo | Regra |
|---|---|---|
| `header_promise` | Uma frase: o que o sistema promete e o que nunca faz | fixo, sempre visível, **uma vez** — nunca repetido por linha |
| `market_state` | Aberto/fechado + hora da última atualização | do `market_hours` |
| `movers_ranked` | Lista ordenada por \|z\|, com movimento, e a decomposição **na própria linha** | máx. 5 linhas expandidas |
| `quiet_row` | Uma linha só: "Calmos: AAPL, JPM, KO…" | os restantes colapsam aqui |
| `latency_badge` | Latência mediana facto→entrega, medida | de `HistoryEntry.latency_seconds()` |

**Proibido neste ecrã:** gráficos, tabelas de avaliação, texto de método, disclaimers
repetidos por linha, mascotes, faixas de tickers a rolar.

### 2.2 Ticker — o aprofundamento

| Componente | Conteúdo | Regra |
|---|---|---|
| `ticker_picker` | Seletor horizontal | renderiza **só** o ticker escolhido (regra de performance já validada) |
| `price_chart` | UM gráfico com marcadores de anomalia | um só; intervalo por defeito 1D |
| `decomposition_panel` | mercado / setor / empresa do último movimento | com a nota de beta indicativo quando aplicável |
| `precedents_list` | Precedentes reais: manchete, data, similaridade, impacto | máx. 3; sempre com "tema ≠ direção" |
| `upcoming_row` | Próximo catalisador agendado, se existir | opcional; ausência é silêncio, não erro |

**Proibido:** segundo gráfico, recomendações, price targets, qualquer número previsto.

### 2.3 Método — para o júri e para o cético

Números congelados da avaliação, o funil de gates com os custos medidos, e o link para o
contrato de cadência. Fora do caminho do dia-a-dia.

---

## 3. Critérios de aceitação (binários — é isto que fecha a discussão)

A app está **feita** quando todos passarem. Nenhum é uma questão de gosto.

**Funcionais**
- [ ] F1. Abre no ecrã *Hoje* sem cliques e sem estado vazio: ou mostra movers, ou diz
      explicitamente que o dia foi calmo.
- [ ] F2. Cada mover mostra a decomposição na própria linha, sem clicar.
- [ ] F3. A frase de promessa aparece **exatamente uma vez** na página.
- [ ] F4. Zero previsões e zero conselho em todo o texto visível (verificável por teste).
- [ ] F5. Cada ecrã responde à sua pergunta sem o utilizador mudar de ecrã.
- [ ] F6. Sem rede/histórico/modelo, degrada com mensagem honesta — nunca traceback.

**Não-funcionais**
- [ ] N1. Uma interação renderiza **um** ticker (regra de performance existente; teste
      `len(at.metric) == 1` mantém-se válido em espírito).
- [ ] N2. Nenhum texto visível em português (regra do projeto).
- [ ] N3. `pytest` + `ruff` verdes; congelados byte-iguais.
- [ ] N4. Screenshot recapturado e **congelado**; legenda da Fig. 4.5 atualizada EN+PT.

**De processo (a condição de paragem propriamente dita)**
- [ ] P1. **Uma** ronda de revisão do aluno. O feedback dessa ronda é aplicado e fecha.
- [ ] P2. Timebox de **3 dias**. O que não couber vira Trabalho Futuro, não uma 6.ª iteração.
- [ ] P3. Depois de F1–F6 e N1–N4 verdes, a app está **congelada** até à entrega. Mudanças
      só se um critério regredir — não por gosto.

---

## 4. O que NÃO se toca

- Os motores (`investigator/`) — a app é uma vista, não lógica nova.
- Os números congelados da avaliação.
- O contrato do histórico partilhado: a app **espelha** o que o Telegram recebeu; nunca
  recalcula alertas por conta própria.

---

## 5. Cortes explícitos, com a razão

| Cortado | Razão |
|---|---|
| Ecrã de carteira/holdings | RGPD + fronteira de aconselhamento (MiFID II). Já cortado no PLANO_V2 §6. |
| Chatbot multi-turno | Um LLM com ferramentas não é multi-agente; o narrador é uma função pura. |
| Mascote, faixa de tickers, painel admin | Ruído; já removidos numa sessão anterior. |
| Bolsas europeias em destaque | Fora do âmbito US das personas. |
| Reescrita do zero | **Redesenhar, não reescrever.** O backend fica; troca-se a camada de UI. |

---

## 6. Definição de pronto

> A app está pronta quando um investidor de retalho abre a página, e em **menos de 10
> segundos** sabe (a) se algo na sua watchlist merece atenção hoje, e (b) se esse algo é a
> empresa ou o mercado — sem clicar, sem ler método, e sem ver uma única previsão.

Se isso for verdade e F1–F6/N1–N4 estiverem verdes, está feita.
