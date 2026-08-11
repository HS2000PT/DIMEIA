# THESIS_FACT_SHEET — cada número, de onde veio, e onde o provo

> **Para que serve:** se alguém apontar para um número e perguntar *"de onde vem isso?"*, a
> resposta está nesta página em três segundos.
>
> **Regra:** uma célula vazia é um problema. Não há células vazias — e onde a cadeia é mais
> fraca, está dito na coluna do meio em vez de ficar escondido.
>
> **Como ler a coluna `código`:** `ficheiro.py:linha` é onde a grandeza é **calculada**, não
> onde é impressa. O script é o que a produz de ponta a ponta.

---

## 0. A cadeia, em geral

```text
API / corpus  →  ficheiro em data/  →  script scripts/evaluate_*.py
              →  docs/evaluation/*.md  →  número citado na tese
```

Nenhum número da tese é digitado à mão a partir de um ecrã: todos vêm de um `.md` que um
script escreveu. Verifiquei isto exaustivamente — **os 3 dígitos decimais do corpo inteiro
(33 ficheiros fonte) têm todos correspondência num ficheiro gerado; zero órfãos.**

---

## 1. RQ1 — detecção de anomalias

| O que digo | Valor | De onde veio | Como calculei | Código | Dados | Tese |
|---|---|---|---|---|---|---|
| Amplitude da taxa de disparo, z-score | **0,015** | 15 tickers, 750 dias cada | `max(taxa) − min(taxa)` entre tickers | `anomaly_eval.py:62` | preços yfinance | §5.2 |
| Amplitude, limiar fixo 3% | **0,344** | idem | idem, com regra `\|r\|>3%` | `anomaly_eval.py:36,62` | idem | §5.2 |
| F1 do z-score vs proxy extremo | **0,516** | mesmo conjunto | `2PR/(P+R)`, proxy = percentil 99 do próprio ticker | `anomaly_eval.py:41,49` | idem | §5.2 |
| F1 do limiar fixo | **0,218** | idem | idem | `anomaly_eval.py:49` | idem | §5.2 |
| z-score vs Isolation Forest | **0,530** vs **0,269** | mesma região causal | ambos vêem retorno + volatilidade 20d | `evaluate_anomaly_ext.py` | idem | §5.2 |
| z-score vs LOF | 0,530 vs **0,280** | idem | idem | `evaluate_anomaly_ext.py` | idem | §5.2 |
| EWMA vs deslizante | **0,664** vs 0,516 | idem | σ com λ=0,94 | `evaluate_anomaly_ext.py` | idem | §5.2 |
| Regra do detector | `\|z\|>k` | — | janela `[-w-1:-1]`, exclui o dia julgado | **`detector.py:28`** | — | §3.3.1 |

**Ficheiro gerado:** `docs/evaluation/evaluation_anomaly.md`, `evaluation_anomaly_ext.md`

---

## 2. RQ2 — recuperação

| O que digo | Valor | De onde veio | Como calculei | Código | Dados | Tese |
|---|---|---|---|---|---|---|
| P@5 semântica (MiniLM) | **0,514 ± 0,015** | 3.714 manchetes | dos 5 vizinhos, quantos do mesmo setor; empresa própria **excluída**; média de 5 sementes | `retrieval_eval.py:33` | `data/finnhub_news.csv` | §5.3 |
| P@5 lexical | **0,346** | idem | mesma fórmula, embedder de sobreposição de palavras | `retrieval_eval.py:33` | idem | §5.3 |
| P@5 acaso | **0,240** | idem | taxa-base do setor | `retrieval_eval.py:58` | idem | §5.3 |
| P@5 recência | **0,126** | idem | k mais recentes | `retrieval_eval.py:80` | idem | §5.3 |
| P@5 à escala | **0,595** | 80k manchetes | mesmo protocolo | `evaluate_retrieval_fnspid.py` | FNSPID | §5.3 |
| Corpus: nº de manchetes | **3.714** | Finnhub company-news | `count()` após filtro de setor conhecido | `evaluate.py:73-79` | `finnhub_news.csv` | §3.2.3 |
| Corpus: amplitude | **27 dias** (28 mai–24 jun 2026) | idem | `max(data) − min(data)` | `evaluate_corpus_and_filter.py` | idem | §3.2.3 |
| Vizinhos anteriores à consulta | **31,1%** | 300 consultas × top-5 | compara datas do vizinho e da consulta | `evaluate_corpus_and_filter.py` | idem | §3.2.3 |
| Consistência de direção | 0,708 vs chão 0,688 | FNSPID | quota de precedentes na mesma direção | `evaluate_retrieval_fnspid.py` | FNSPID | §5.3 |

**⚠️ O elo mais fraco desta secção:** "relevante" = **mesmo setor**, que é um *proxy* e não
julgamento humano. Está declarado como limitação em §5.10.

**Ficheiro gerado:** `evaluation_results.md`, `evaluation_retrieval_fnspid.md`, `evaluation_relevance_filter.md`

---

## 3. O filtro de notícias — o que é excluído, e porquê

| O que digo | Valor | De onde veio | Como calculei | Código | Dados | Tese |
|---|---|---|---|---|---|---|
| Manchetes mantidas | **811 de 2.478** (32,7%) | 12 tickers com aliases | `is_relevant()` sobre o corpus | **`relevance.py:114`** | `finnhub_news.csv` | §4.5 |
| Descartadas por boilerplate | **74** (3,0%) | idem | regex de 11 padrões | `relevance.py:92-105` | idem | §4.5 |
| Descartadas por não mencionar | **1.593** (64,3%) | idem | sem alias nem ticker, palavra inteira | `relevance.py:109` | idem | §4.5 |

**A regra, em uma linha:**
`relevante(manchete, ticker) = não-vazia ∧ ¬boilerplate ∧ menciona(ticker ∨ alias)`

**⚠️ Duas coisas a assumir, e estão na tese (§4.5):**
1. A regra foi escrita **depois** de ler os primeiros 27 alertas — não é a priori.
2. As listas de aliases são **escritas à mão**; outro investigador obteria retenções diferentes.

**Ficheiro gerado:** `docs/evaluation/evaluation_relevance_filter.md`

---

## 4. RQ4 — o modelo treinado

| O que digo | Valor | De onde veio | Como calculei | Código | Dados | Tese |
|---|---|---|---|---|---|---|
| Exemplos de treino | **79.753** | FNSPID 2018–23 | (manchete, ticker, dia) com preços alinhados | `build_dataset.py` | `triage_dataset.csv` | §3.2.1 |
| Blocos treino/val/teste | **28.574 / 17.710 / 32.649** | idem | divisão temporal por **dia único**, 70/15/15 | **`dataset.py:108`** | idem | §3.3.4 |
| Linhas largadas no embargo | **820** | idem | 5 dias únicos após cada fronteira | `dataset.py:108` | idem | §3.3.4 |
| Prevalência por bloco | 0,385 / 0,470 / 0,378 | idem | `mean(label)` | — | idem | §5.8 |
| Definição do rótulo | `\|r_tkr − r_SPY\| ≥ 2%` a 3d | preços | diferença de retornos acumulados | **`dataset.py:99`** | idem | §3.3.4 |
| Features (9) | vol20, mom5, ret_event, len, 5×setor | preços + manchete | todas ao fecho do dia `d` | **`dataset.py:39`** | idem | §3.3.4 |
| PR-AUC volatilidade | **0,542** | bloco de teste | área sob precisão–recall | **`model.py:68`** | idem | §5.5 |
| PR-AUC contexto | 0,538 | idem | idem | `model.py:68` | idem | §5.5 |
| PR-AUC contexto+texto | **0,496** | idem | idem | `model.py:68` | idem | §5.5 |
| PR-AUC GBM | 0,469 | idem | idem | `model.py:68` | idem | §5.5 |
| Chão (alertar sempre) | 0,378 | idem | = prevalência do teste | `model.py:68` | idem | §5.5 |
| Precisão @5 alertas/dia | **0,632** vs 0,163 | idem | ordena o dia por p, admite top-5 | **`model.py:82`** | idem | §5.5 |
| Brier | 0,224 | idem | `mean((p−y)²)` | `model.py:68` | idem | §5.5 |
| Calibração de Platt | a=3,700 · c=−2,313 | bloco de **validação** | sigmóide de 2 parâmetros | **`model.py:61`** | idem | §3.3.4 |
| Exemplo trabalhado (META) | u=+0,699 → 0,668 → **0,539** | alerta real 12 jul 2026 | soma dos `w·x` → sigmóide → Platt | `explain.py:21` | branch de dados | §3.3.4 |

**Verificação independente:** `tests/test_frozen_reproducibility.py` carrega o `.joblib`
implantado, recalcula PR-AUC, ROC-AUC, Brier e precisão@orçamento e exige **igualdade exacta**.
Se alguém re-treinar com outra semente, a suite parte.

**Ficheiro gerado:** `docs/evaluation/evaluation_triage.md` + `models/triage_*.json`

---

## 5. O que o modelo faz AO VIVO (o resultado negativo)

| O que digo | Valor | De onde veio | Como calculei | Código | Dados | Tese |
|---|---|---|---|---|---|---|
| Decisões registadas | **1.087** | produção | uma linha por decisão de triagem | `postval.py:26` | `predictions_log.jsonl` | §6.5 |
| Decisões maturadas | **530** | idem | janela (d, d+3] fechada | `postval.py:71` | idem | §6.5 |
| Unidades efectivas | **145** pares (ticker, dia) | idem | o rótulo é por ticker-dia | `evaluate_live_transfer.py` | idem | §6.5 |
| Mantidas materiais | **0,592** | idem | `mean(label)` nas mantidas | `postval.py:88` | idem | §6.5 |
| Suprimidas materiais | **0,647** | idem | idem nas suprimidas | `postval.py:88` | idem | §6.5 |
| ROC-AUC ao vivo | **0,494** | idem | prob. de um positivo ficar acima de um negativo | `evaluate_live_transfer.py` | idem | §6.5 |
| IC 95% (bootstrap de **cluster**) | **[0,391; 0,601]** | idem | reamostra pares ticker-dia inteiros | `evaluate_live_transfer.py` | idem | §6.5 |
| Prevalência ao vivo vs treino | **0,626** vs 0,378 | idem | `mean(label)` | idem | idem | §6.5 |

**Ficheiro gerado:** `docs/evaluation/evaluation_live_transfer.md`, `live_monitoring.md`

---

## 6. Sistema e implantação

| O que digo | Valor | De onde veio | Como calculei | Código | Dados | Tese |
|---|---|---|---|---|---|---|
| Cosseno ONNX vs SBERT | **0,992** (mín 0,983) | 503 consultas | cosseno par-a-par | `evaluate_onnx_parity.py` | KB curada | §4.9 |
| Vizinhos partilhados | **95%** | idem | interseção dos top-3 | idem | idem | §4.9 |
| Folga mediana nas divergências | 0,006 | idem | diferença de similaridade | idem | idem | §4.9 |
| Cobertura de notícias | **88,5%** (90,4% a \|z\|≥3) | 1 ano, 12 nomes | dias com ≥1 manchete relevante / dias invulgares | `evaluate_news_coverage.py` | branch de dados | §6.5 |
| Deriva (PSI) na volatilidade | **0,281** | treino vs teste | `Σ(p_c−p_r)·ln(p_c/p_r)` em bins por quantil | `evaluate_drift.py` | `triage_dataset.csv` | §5.8 |
| Cobertura conformal a 90% | decisão definida em **39,5%** | bloco de teste | conjuntos de predição split-conformal | `evaluate_conformal.py` | idem | §5.7 |
| AMI tipo de evento vs ticker | **0,358** vs 0,188 | FNSPID | informação mútua ajustada, mesmas linhas | `evaluate_event_taxonomy.py` | idem | §5.6 |
| Fusão vs melhor sinal | ganha em **1 de 3** orçamentos | 1.951 pares | P@k por orçamento | `evaluate_convergence.py` | idem | §5.9 |
| Latência: publicação→detecção | **~158 min** (mediana) | 101 alertas | `detected_at − event_at` | `evaluate_latency.py` | `alerts_history.jsonl` | §6.2 |
| Latência: detecção→entrega | **~1 s** | idem | `sent_at − detected_at` | idem | idem | §6.2 |
| Funil de produção | 944 manchetes → **42** alertas (22:1) | 5 dias ao vivo | contagens do registo | `alert_funnel.md` | branch de dados | §4.8 |
| Alertas reais entregues | **332** | produção | linhas do histórico partilhado | — | `alerts_history.jsonl` | Apêndice A |

---

## 6b. A camada generativa (v5)

> ⚠️ **A pergunta que isto responde é a mais provável de todas:** *"onde é que está a IA?"*
> A resposta curta está no §9. Esta tabela é o que a sustenta.

| O que digo | Valor | De onde veio | Como calculei | Código | Tese |
|---|---|---|---|---|---|
| Ataques adversários bloqueados | **23 / 23** | corpus versionado | cada ataque tem de dar `ok=False` | `evaluate_intelligence_guard.py` | §4.8 |
| Controlos de texto fiel aceites | **8 / 8** | idem | cada controlo tem de dar `ok=True` | idem | §4.8 |
| Secções geradas conformes | **27 / 27** | **1 corrida de 6 relatórios** | re-verificação de cada secção entregue | idem | §4.8 |
| Secções entregues com violação | **0** | idem | contagem; tem de ser zero **em todas as corridas** | idem | §4.8 |

> ⚠️ **Estas quatro linhas não se lêem da mesma maneira, e é a primeira coisa a dizer se
> perguntarem por elas.**
>
> | classe | quais | reproduz? |
> |---|---|---|
> | **determinística** | ataques, controlos | **sim, exactamente** — a guarda é pura e o corpus é fixo |
> | **amostrada** | secções conformes | **não** — depende de quantos relatórios gerei e do que o modelo escreveu. **Cita-se a taxa, não a contagem** |
> | **invariante** | entregues com violação | **tem de ser 0 sempre** — não é estatística, é propriedade a verificar |
>
> **Se perguntarem "porque é que este número mudaria?":** *"O 23/23 e o 8/8 não mudam — a guarda
> é determinística. As contagens de secções mudam com o tamanho da corrida, por isso o que se cita
> é a taxa. E o zero tem de valer em todas as corridas: se não valesse, era um defeito do caminho
> de entrega, não uma variação de amostra."*
| Exploits reproduzidos pelo red team | **21** de **114** tentativas | 2 de 6 lentes | ataque reproduzido em Python real | — | §6.5 |
| Latência do relatório | **~1,5 s** | produção | tempo do fornecedor + guarda | `/api/report` | §4.8 |
| Latência do analista | **~1,3 s** | produção | roteamento + resposta | `/api/ask` | §4.8 |

**Onde vive cada peça do código:**

| Peça | Ficheiro | O que faz |
|---|---|---|
| Pacote de evidência | `investigator/intelligence/context.py` | cada facto com id citável e origem declarada |
| Guarda de fidelidade | `investigator/intelligence/guard.py` | ligação numérica por frase, registos proibidos, âncoras |
| Relatório | `investigator/intelligence/report.py` | secções fixas, rejeição por secção, chão determinístico |
| Analista | `investigator/intelligence/analyst.py` | pergunta → plano validado → evidência → resposta |
| Risco residual | `guard.RESIDUAL` | os quatro riscos que os números **não** fecham |

---

## 6c. A interface (v5) — os números de desempenho

| O que digo | Valor | Como medi | Tese |
|---|---|---|---|
| Carga da superfície de abertura | **1,0 s** (era 5,5–6,2 s) | `performance.timing` no browser, em produção | §4.7.1 |
| Pedidos para essa superfície | **1** (eram 12) | contador de `fetch` | §4.7.1 |
| Mudar o intervalo do gráfico | **2,5–7,3 ms** (era ~750 ms) | mediana de 5 mudanças | §4.7.1 |
| Chamadas de rede ao mudar intervalo | **0** | `fetch` instrumentado | §4.7.1 |

> **Se perguntarem "porquê trocar de tecnologia?":** a resposta não é estética. O Streamlit
> re-executa o script **do lado do servidor** a cada interacção. O zero da última linha é a
> afirmação estrutural: mudar de intervalo é uma fatia de um vector que o browser já tem.

---

## 7. ⚠️ Onde a cadeia é mais fraca (dizer antes que perguntem)

| Grandeza | Porque é mais fraca | O que digo |
|---|---|---|
| P@5 (relevância) | "mesmo setor" é proxy, não julgamento humano | *"É um proxy e está declarado. A alternativa honesta é um estudo humano, que não fiz."* |
| Corpus de 27 dias | curto demais para generalização temporal | *"Por isso o resultado é preliminar e foi repetido à escala."* |
| Filtro de relevância | regra escrita depois de ver falhas; aliases à mão | *"Determinística e reprodutível, mas não a priori — e a tese di-lo."* |
| FNSPID bruto | os ~23 GB originais não estão nesta máquina | *"Tenho o subconjunto derivado e o script que o constrói; a fonte original é pública e citada."* |
| Latência | `event_at` é a hora que a fonte declara | *"É um limite inferior, e está dito no relatório."* |
| Guarda generativa | a defesa linguística é uma **blocklist**, não uma allowlist | *"É mais fraca do que a do alerta, de propósito, e está declarada. O alerta é empurrado sem evidência ao lado; o relatório é pedido com a evidência a um clique. Os quatro riscos que fica por fechar estão escritos em `guard.RESIDUAL` e no §6.5."* |
| Red team da guarda | **2 de 6** lentes completaram; **nenhum verificador** correu | *"Bateu no limite de gasto da conta. O workflow devolveu 'nenhum exploit sobreviveu', e isso é a AUSÊNCIA de verificação, não um resultado limpo. Verifiquei os achados à mão. A força medida é um limite inferior."* |
| Relevância da âncora | verifica-se que o facto citado EXISTE, não que sustenta a frase | *"Uma frase pode citar um facto verdadeiro e caracterizá-lo mal sem usar número nenhum. Está no risco residual."* |

---

## 8. Reprodutibilidade — o que responder a *"como reproduzo isto?"*

- **Python** 3.12 · dependências em `requirements.txt` (leve) e `requirements-ml.txt` (pesada)
- **Semente** 42 em todo o lado onde há aleatoriedade
- **Modelo** versionado em `models/` (1,8 KB) com metadados `.json` ao lado
- **Comandos** no Apêndice A, um por resultado
- **Suite** 707 testes, offline e determinísticos

**O que NÃO é reproduzível a partir do repositório, e digo-o:** o corpus FNSPID bruto
(~23 GB) e o `triage_dataset.csv` (15 MB) não estão versionados. São regeneráveis pelos
scripts, a partir da fonte pública citada.
