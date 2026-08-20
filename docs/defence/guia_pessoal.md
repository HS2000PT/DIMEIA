# Tese — Guia Pessoal (TL;DR)

> ⚠️ **Este documento foi escrito para a tese longa em inglês.** A que vais defender é a
> tese curta em português (`tese/`), que tem **três QI** e não quatro RQ, e onde alguns
> números foram corrigidos. Lê o [`LEIA-ME-PRIMEIRO.md`](LEIA-ME-PRIMEIRO.md) antes de
> estudares por aqui.

> **Isto não é a tese.** É a minha folha de apoio: informal, directa, para abrir antes de falar
> com o orientador ou antes da defesa. Tudo o que está aqui está verificado — se um número
> aparece nesta página, existe um ficheiro gerado por script que o produz.
>
> **Regra de ouro:** honestidade > brilho. Um "sim" honesto e um "isso não medi" defendem-se
> sempre. Um exagero rebenta à primeira pergunta.

---

## 1. O que é isto, em 30 segundos

Um sistema de alertas financeiros **explicáveis** para investidores de retalho nos EUA. Vigia
12 empresas. Quando alguma coisa acontece, manda um alerta ao Telegram que responde a **três
perguntas**:

1. **Isto é invulgar para esta acção?** (não "subiu 3%", mas "3% é muito *para esta*?")
2. **É a empresa ou é o mercado?**
3. **Já aconteceu antes, e o que se seguiu?**

E **nunca prevê preços**. Isso não é uma falha — é a restrição que define o trabalho.

**A contribuição é de Engenharia de IA:** não inventei algoritmos. Integrei, apliquei e avaliei
criticamente componentes que já existiam, num sistema que funciona, é explicável e é
reprodutível.

---

## 2. Porque é que isto interessa

Um investidor de retalho vê "a NVIDIA caiu 4%" e não sabe se deve preocupar-se. Falta-lhe:
contexto (é muito para esta acção?), atribuição (foi ela ou foi o mercado?) e precedente (isto
já aconteceu?).

As ferramentas gratuitas dão **uma** dessas coisas cada. Os terminais profissionais dão as
três — a um preço que este utilizador não paga. **É essa a lacuna.**

---

## 3. Como funciona, de uma ponta à outra

```text
API de notícias (Finnhub)          Preços (yfinance + 4 fontes de recurso)
        │                                     │
        ▼                                     ▼
  normalizar (guardo data, ticker,      log-retornos
  título; DEITO FORA o resumo)              │
        │                                     ▼
        ▼                             z-score sobre os 20 dias ANTERIORES
  filtro de relevância                        │
  (nomeia a empresa? não é                    ▼
   boilerplate de mercado?)            |z| > limiar?
        │                                     │
        ▼                                     │
  embedding SBERT 384-d                       │
        │                                     │
        ▼                                     │
  cosseno contra a base de casos              │
  (top-3 + impacto medido a +1/+3/+5d)        │
        │                                     │
        ▼                                     │
  5 portões: frescura · chão de               │
  evidência · triagem · tecto · dedup         │
        └──────────────┬──────────────────────┘
                       ▼
              motor de explicação
              (renderiza dos objectos calculados)
                       ▼
                 Telegram + painel
```

**A frase para decorar:** *o texto do alerta é renderizado a partir dos mesmos objectos que o
sistema calculou — por isso não pode divergir do cálculo.*

---

## 4. Os dados: de onde vêm, onde ficam, o que lhes acontece

| camada | fonte | o que é | onde fica |
|---|---|---|---|
| **Histórica** | FNSPID (CC BY-SA 4.0) | 79.753 exemplos notícia–mercado, 2018–2023 | `data/` local, **não versionado** (é grande) |
| **Base curada** | subconjunto do FNSPID | 2.016 casos com embedding 384-d | versionada (7,7 MB) — é o que a app consulta |
| **Corpus de avaliação** | Finnhub | 3.714 títulos, **27 dias** (28 mai–24 jun 2026) | `data/finnhub_news.csv` |
| **Viva** | Finnhub + preços | decisões e alertas que o sistema toma | branch `alerts-history` |

**O que deito fora de propósito:** o *resumo* que o fornecedor manda com cada notícia. Guardo
só o título. Razão: republicar texto de artigos de terceiros seria distribuir conteúdo
licenciado; o título é o mínimo para calcular semelhança.

**⚠️ O que tenho de saber dizer sobre o corpus de avaliação:** são **27 dias**, não meses.
Não sustenta nenhuma afirmação sobre generalização no tempo. É por isso que o resultado é
preliminar e foi repetido à escala no FNSPID multi-ano.

---

## 5. Que IA existe aqui, e o que NÃO existe

| componente | é IA? | é aprendizagem? | treinado por mim? |
|---|---|---|---|
| Detector de anomalias (z-score) | sim (regra) | **não** — é estatística | não |
| Triagem de materialidade | sim | **sim, supervisionada** | **SIM** ← o único |
| SBERT (embeddings) | sim, deep learning | sim, mas pré-treinado | **não** — descarregado |
| Taxonomia de eventos (k-means) | sim | não supervisionada | sim (descritivo) |
| **Geração ancorada** (relatório + analista) | **sim, generativa** | não (é inferência) | não — LLM externo, **guardado** |

**A resposta a "isto é deep learning?":** *"Não, e uso deep learning."* Por esta ordem. O único
modelo que treinei é uma regressão logística. Uso um SBERT pré-treinado, e a engenharia aí foi
pô-lo a correr em 512 MB sem framework (ONNX quantizado) e **provar** que continua a devolver
os mesmos vizinhos.

**⚠️ A pergunta mais provável de todas: «onde está a inteligência artificial?»**
A resposta tem quatro andares, e digo-os por esta ordem:

| andar | o quê | natureza |
|---|---|---|
| 1 · **dados** | preços, títulos, carimbos temporais | medido |
| 2 · **estatística** | z-score, excedência empírica, decomposição | determinístico |
| 3 · **aprendizagem** | SBERT + recuperação semântica + triagem calibrada | modelos treinados |
| 4 · **geração** | relatório de situação e analista, em linguagem | LLM, ancorado |

**A frase que fecha a pergunta:** *"O modelo não sabe o que aconteceu. É-lhe dito — por um motor
de recuperação sobre 80 mil títulos com desfecho **medido** a cinco dias, por um classificador
calibrado, e por uma decomposição com betas encolhidos. E cada número que ele escreve é
verificado contra essa evidência antes de chegar ao ecrã."*

**E a seguir MOSTRA, não expliques:** no relatório, clica num identificador `[f1]` e abre-se o
facto que o sustenta, com a origem declarada. Três segundos. Vale mais do que qualquer parágrafo,
e é a diferença entre este trabalho e um wrapper de LLM.

---

## 6. O modelo treinado, em concreto

- **O que faz:** dá a probabilidade de se seguir um movimento anormalmente grande, **em
  qualquer direcção**, nos 3 dias após uma notícia.
- **Entradas (9):** volatilidade dos 20 dias anteriores, momento a 5 dias, retorno do próprio
  dia, comprimento do título, e 5 colunas de setor.
- **Rótulo:** `|retorno do ticker − retorno do SPY|` nos 3 dias seguintes `≥ 2%`. Produzido pelo
  meu próprio código, não à mão.
- **Divisão:** temporal, **por dia único**, 70/15/15, com **embargo de 5 dias** entre blocos
  (custa 820 linhas, e isso está reportado).
- **Calibração:** Platt (2 parâmetros) só no bloco de validação.
- **Onde vive:** `models/triage_context_lr.joblib` — **1,8 KB** — mais um `.json` ao lado com a
  semente, os tamanhos dos blocos e as métricas. Esse par **é** um registo de modelos.

**A melhor frase que tenho sobre isto:** *"há um teste que carrega o ficheiro implantado,
recalcula as quatro métricas que a tese cita e exige igualdade exacta. Não é preciso acreditar
em mim."*

---

## 7. O sistema aprende sozinho? **NÃO.**

Quatro palavras diferentes, e confundi-las é a forma mais rápida de perder credibilidade:

- **Inferência** — pontuar com pesos fixos. Corre a cada 60 s. ✅ existe
- **Treino** — descobrir os pesos. Aconteceu **uma vez**, offline. ✅ aconteceu
- **Re-treino** — repetir com dados novos. Documentado, **nunca executado**. ⬜
- **Aprendizagem contínua** — re-treino automático. **Não existe.** ❌

O que corre continuamente é **recolha de rótulos e monitorização**: cada decisão é registada e,
dias depois, rotulada com o que aconteceu ao preço. Nenhum peso muda. É a *pré-condição* de um
re-treino, não um re-treino.

---

## 8. Os resultados, e como foram calculados

### RQ1 — detecção transparente · **SIM**
- Amplitude da taxa de disparo entre 15 tickers: **0,015** (z-score) vs **0,344** (limiar fixo).
- *Porquê é este o argumento principal:* **não precisa de rótulo nenhum.** Um bom detector
  universal devia disparar a taxa parecida em acções diferentes. O meu varia 20× menos.
- Contra detectores aprendidos, com a **mesma informação**: z-score F1 **0,530** vs Isolation
  Forest **0,269** vs LOF **0,280**.

### RQ2 — recuperar casos análogos · **SIM**
- P@5 **0,514** vs 0,346 (lexical), 0,240 (acaso), 0,126 (recência). À escala: **0,595** em 80k.
- *Como se calcula:* dos 5 vizinhos mais próximos, quantos são do mesmo setor da consulta? Com
  a **própria empresa excluída** — não posso ganhar a acertar em mim mesmo.
- **⚠️ O que NÃO posso dizer:** que são "precedentes". Naquele corpus de 27 dias, só **31,1%**
  dos vizinhos são anteriores à consulta. Digo *recuperação semântica de itens do mesmo setor*.
  Em produção são anteriores por construção (base até 2023, consultas em 2026).

### RQ3 — explicações fiéis · **FIÉIS SIM, ÚTEIS EM ABERTO**
- Fiel por construção: o texto é renderizado dos objectos calculados.
- **Útil:** não medido. Falta o estudo humano. **Não afirmo nada.**

### RQ4 — triagem aprendida · **OFFLINE SIM, TEXTO NÃO, AO VIVO NÃO**
- PR-AUC: volatilidade **0,542** > contexto 0,538 > contexto+texto **0,496** > GBM 0,469.
  **O texto piora.** Comparação pré-comprometida.
- Valor de produto (em dados retidos): precisão dentro do orçamento de 5 alertas/dia sobe de
  **0,379** para **0,632**.
- **⚠️ Ao vivo não transfere:** ROC-AUC **0,494**, IC [0,391, 0,601] sobre 145 pares
  empresa-dia. Centrado no acaso.

---

## 9. O achado de que mais me orgulho (e é negativo)

O gate de triagem **não funciona em produção**, e sei *porquê*.

Duas falhas produzem o mesmo sintoma e pedem correcções opostas:
- se o score **ordena** e só a escala está errada → recalibra-se (2 parâmetros);
- se o score **não ordena** → recalibrar não serve, porque a sigmóide é **monótona**: preserva
  a ordem exactamente.

Medi: ROC-AUC 0,494. **Não há ordem para preservar.**

E a explicação não é "modelo avariado", é **modelo redundante**: a materialidade entre as
decisões registadas corre a **0,626**, contra **0,378** no treino — porque só se registam
títulos que já passaram os filtros de relevância e frescura. Os filtros baratos a montante já
tinham feito o trabalho.

**A lição, e é o que um arguente quer ouvir de um engenheiro:** *um modelo avaliado isolado e
implantado atrás de filtros nunca foi avaliado na distribuição que ia ver.* É um erro de
integração, não de modelação — e só apareceu porque instrumentei o gate.

---

## 10. Mapa de navegação — onde está cada resposta

| Se me perguntarem | Resposta curta | Secção | Prova |
|---|---|---|---|
| Que dados usa? | FNSPID 2018–23 (histórico) + Finnhub (vivo) | §3.2 | data card |
| Quantos exemplos? | 79.753 para a triagem; 3.714 para recuperação | §3.2, §5.1 | `evaluation_triage.md` |
| Como são criados os rótulos? | `\|ret − ret_SPY\|` a 3 dias ≥ 2%, pelo meu código | §3.3.4 | `dataset.py` |
| Como divide treino/teste? | Temporal, por dia único, 70/15/15 + embargo 5d | §3.3.4 | Excerto 3.2 |
| Como sei que não há lookahead? | Teste que muta o futuro: features iguais, rótulo muda | §3.3.4 | Excerto 3.1 |
| Porque exclui certas notícias? | Tem de nomear a empresa; sem boilerplate. Descarta 2/3 | §4.5 | `evaluation_relevance_filter.md` |
| Como calcula a precisão? | PR-AUC no bloco de teste; e precisão@orçamento diário | §3.6.4 | `evaluation_triage.md` |
| Onde está o modelo? | `.joblib` de 1,8 KB + `.json` de metadados | §4.9 | teste de reprodução |
| Aprende continuamente? | **Não.** Inferência + recolha de rótulos | §3.3.4 | — |
| O modelo funciona? | Offline sim; ao vivo não (ROC-AUC 0,494) | §6.5 | `evaluation_live_transfer.md` |
| A latência? | ~2,5 h de descoberta + ~1 s de entrega | §6.2 | `evaluation_latency.md` |
| Está mesmo a correr? | Sim, 332 alertas com carimbos | Apêndice A | branch `alerts-history` |

---

## 11. ⚠️ ZONA DE PERIGO — as perguntas que doem

### P1. «Só 31% dos vossos precedentes são anteriores à consulta?»
**Porque é vulnerável:** parece lookahead.
**A verdade:** não é lookahead — a métrica pontua concordância de **setor**, e o setor não muda
com o tempo. Mas a palavra "precedente" estava errada.
**Resposta segura:** *"Nessa experiência, sim, e por isso chamo-lhe recuperação semântica de
itens do mesmo setor, não recuperação de precedentes. O corpus tem 27 dias — não dá para exigir
anterioridade. Em produção a base termina em 2023 e as consultas são de 2026, portanto a
anterioridade é estrutural. E a medição do impacto olha sempre só para a frente."*

### P2. «Deitam fora dois terços das notícias?»
**Resposta segura:** *"Sim, e medi-o em vez de o esconder. 811 de 2.478. E só 3% é a regra de
boilerplate que descrevo — os outros 64% falham por o título nunca nomear a empresa. Prefiro
mostrar a taxa de descarte do que a de sobrevivência."*

### P3. «De onde veio a regra do filtro?»
**Porque é vulnerável:** foi feita **depois** de ver os dados.
**Resposta segura:** *"De ler os primeiros 27 alertas que o canal enviou. É código
determinístico — duas pessoas aplicam-na e obtêm o mesmo — mas não é um critério a priori, e a
tese diz isso. As listas de aliases são escritas à mão, e outro investigador obteria taxas de
retenção diferentes."*

### P4. «Então o vosso machine learning não funciona?»
**Resposta segura:** *"Como selector em produção, não — ROC-AUC 0,494, medido. Em dados retidos,
sim. As duas coisas são verdade porque são populações diferentes, e a tese diz as duas. O que
isto ensina é sobre pôr um componente aprendido dentro de uma pipeline."*

### P5. «"Mesmo setor" não é "análogo".»
**Porque é vulnerável:** é o elo mais fraco da RQ2.
**Resposta segura:** *"Concordo, é um proxy, e está declarado como tal. Três defesas: excluo a
própria empresa, o que torna a métrica mais difícil e não mais fácil; o ganho é maior onde o
vocabulário é distintivo (energia +0,377) e menor no consumo, que é genérico — o que é o padrão
que se esperaria se estivesse a captar significado; e a alternativa honesta seria um estudo
humano de relevância, que não fiz."*

### P6. «Prevêem ou não prevêem?»
**Resposta segura:** *"Prevejo uma coisa, de forma estreita: a **materialidade** — se o mercado
reage de forma anormalmente grande. Nunca a direcção nem o preço. Uma versão anterior do alerta
dizia 'not a forecast' e isso era falso; está corrigido."*

### P7. «O modelo é uma regressão logística com 9 números.»
**Resposta segura:** *"É, e testei modelos com mais capacidade: o gradient boosting saiu-se
PIOR (0,469 vs 0,542). Se o problema fosse falta de capacidade, teria ganho. O que é modesto
aqui é o sinal, não a solução — e a contribuição está no método: divisão temporal com embargo,
teste de fuga, calibração só na validação, e um negativo que sobreviveu a três tentativas de o
derrubar."*

### P8. «Porque tantos resultados negativos?»
**Resposta segura:** *"Porque foram comparações pré-comprometidas, e porque um trabalho que só
reporta o que correu bem é um trabalho em que não se pode confiar. Todas as retiradas caíram
por medições minhas, não por revisão de outra pessoa. O apêndice tem uma matriz que marca cada
afirmação como mantida, estreitada ou retirada — e as retiradas ficam lá de propósito."*

### P9. «A vossa guarda é uma blocklist — não escreveu na tese que blocklists perdem sempre?»
> **A armadilha mais bem construída que me podem fazer, porque cita o meu próprio trabalho.
> Não me defendo: concordo primeiro.**

**Resposta segura:** *"Escrevi, e mantenho. É por isso que o **alerta** — que é empurrado para o
telemóvel sem evidência ao lado — usa a allowlist de vocabulário fechado. O relatório é **pedido**
pelo utilizador, na página, com a evidência a um clique. Perfis de risco diferentes, garantias
diferentes, e a diferença está numa tabela da tese, não escondida. O que se mantém idêntico nos
dois é a parte verificável: os números vêm de um conjunto fechado e, no relatório, ligados à frase
que os cita."*

**Se insistirem:** *"E os quatro riscos que a garantia mais fraca não fecha estão escritos —
relevância da âncora, paráfrase, qualificadores e omissão."*

### P10. «O red team confirmou que a guarda é segura?»
> **NÃO deixar passar isto sem correcção. Se eu deixar, estou a afirmar o que não medi.**

**Resposta segura:** *"Não. Encomendei seis lentes de ataque; duas completaram, e **nenhuma etapa
de verificação independente correu** — bateram no limite de gasto da conta. O relatório final
dizia 'nenhum exploit sobreviveu à verificação', e isso é a **ausência** de verificação, não um
resultado limpo. Verifiquei os achados eu próprio contra o código, fechei-os, e guardei-os como
testes de regressão. A força medida é um **limite inferior**."*

**Porque é que isto é uma boa resposta:** porque a pergunta era uma armadilha e eu desarmei-a
antes de ela fechar. Ninguém ataca quem já concordou.

---

## 12. 🚫 O que NUNCA posso afirmar

| Não dizer | Porquê |
|---|---|
| "0,667 vs 0,455 prova que o mecanismo funciona ao vivo" | Eram 12 decisões; com 530 o sinal **inverte-se** |
| "O gate selecciona notícias materiais" | ROC-AUC 0,494 — retirado |
| "O corpus abrange meses" | São 27 dias |
| "Recuperamos precedentes" (sobre a avaliação) | Só 31,1% são anteriores |
| "Top-3 idêntico em 20 de 23" (ONNX) | Não reproduz; a grandeza estável é 95% de vizinhos |
| "A latência é limitada pelo ciclo de sondagem" | Medido: está toda na descoberta |
| "O sistema aprende continuamente" | Nada re-treina |
| "O filtro é um critério objectivo a priori" | Foi escrito depois de ver falhas |
| "Perguntámos aos utilizadores" | São **personas**. Nenhum estudo humano foi feito |
| "As explicações são úteis" | Não medido |
| "A guarda do relatório é tão forte como a do alerta" | É blocklist, não allowlist — **mais fraca, e declarada** |
| "A guarda passou um red team completo" | 2 de 6 lentes; **nenhum verificador** correu (limite de gasto) |
| "O texto gerado está sempre correcto" | Verifico o **número** e a **âncora**, não se a frase caracteriza bem o facto |

---

## 13. Os meus pontos mais fortes (dizer sem modéstia)

1. **Dois testes justos e pré-comprometidos que o método transparente venceu** — z-score vs
   Isolation Forest, e volatilidade vs texto. Reportados tal como caíram.
2. **Um teste que parte se os números deixarem de reproduzir.** O bundle congelado regenera
   PR-AUC, ROC-AUC, Brier e precisão@orçamento **exactamente**.
3. **Uma ferramenta de re-treino que se recusa a correr** e explica porquê.
4. **Uma matriz de evidência que regista o que retirei.**
5. **Defeitos que encontrei em mim próprio** — medi a coisa errada a favor do meu trabalho
   (FCP), um teste que se dizia determinístico e não era, um alerta que se contradizia.

## 14. Os meus pontos mais fracos (dizer antes que perguntem)

1. **Não há estudo humano.** Metade da RQ3 fica em aberto.
2. **O proxy de relevância é concordância de setor**, não julgamento humano.
3. **O corpus de recuperação tem 27 dias.**
4. **O gate não transfere para produção.**
5. **12 empresas, mercado americano, grandes capitalizações.**

---

## 15. Antes de entrar na sala

- [ ] `python scripts/demo_defesa.py --dia 2026-08-09` corrido **uma vez com internet** (fica
      em cache; depois usa `--offline`)
- [ ] `tese/main.pdf`, `tese/slides/main.pdf` e `tese/guia/main.pdf` no portátil (são estes, e não as teses longas)
- [ ] Ler as secções 11 e 12 desta página. São as que salvam a defesa.
- [ ] Uma frase de cabeça: **"a simplicidade defensável venceu, e tenho as medições que o
      mostram — incluindo as que correram contra mim."**
