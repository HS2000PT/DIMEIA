# INVESTIGATOR — MASTER PLAN

> **O que este ficheiro é.** O plano-mestre do produto e da dissertação, criado a 2026-08-13 em
> resposta à directiva-mestra do aluno. Sucede ao [`progress/PLANO_V2.md`](progress/PLANO_V2.md) e
> herda-lhe a decisão estruturante (duas pistas), que continua correcta.
>
> **O que este ficheiro NÃO é.** Não é um segundo sítio onde os números vivem. Este projecto já
> pagou o custo de ter a mesma quantidade escrita em dois sítios: elas divergem, e a divergência
> não dá erro. **Regra deste ficheiro: nenhum número congelado é copiado para aqui.** Onde um
> número interessa, aponta-se para o ficheiro que o produz. Os únicos números escritos aqui são os
> que foram medidos nesta sessão e ainda não têm casa.
>
> **Estado, sempre:** [`CLAUDE.md`](CLAUDE.md). **O que falta em cliques humanos:**
> [`CHECKLIST.md`](CHECKLIST.md).

---

## Mapa de conformidade com a directiva

| Secção pedida (directiva §65/§78) | Onde está |
|---|---|
| Project Vision · Research Problem · Research Questions | §1, §2, §3 |
| Hypotheses · Scientific Contribution | §3.3, §4 |
| AI Strategy (+ matriz de selecção §9) | §5 |
| Architecture · Data Strategy · Model Strategy | §6 — e os documentos que já os detalham |
| Evaluation Strategy | §7 |
| Completed · In Progress · Blocked · Deferred | §8 (matriz de conclusão) |
| Known / AI / UX / Data / Architecture Issues · Technical Debt | §9 (registo de achados) |
| Thesis Structure · Thesis Gaps · Evidence Gaps | §10 |
| Decisions Log · Experiment Log · Model Registry · Dataset Registry | §11 (ponteiros — todos já existem) |
| Traceability matrix (§10/§66) | §12 |
| Open Questions · Next Priorities · Completion Matrix | §13 (roteiro priorizado) |
| Session History | [`progress/SESSIONS.md`](progress/SESSIONS.md) + `CLAUDE.md` |

---

## 1. Project Vision

Um sistema que responde às três perguntas que um investidor de retalho faz por esta ordem — *isto é
invulgar? foi a empresa ou o mercado? já aconteceu antes e o que se seguiu?* — com cada afirmação
rastreável ao procedimento que a produziu, sobre APIs gratuitas, e **sem prever preços**.

A recusa de prever não é uma limitação a pedir desculpa: é o que torna cada saída verificável. Uma
afirmação sobre o que já aconteceu confronta-se com o registo; uma previsão não.

## 2. Research Problem

**O problema técnico central**, formulado como a directiva pede (e não como "juntar APIs"):

> Dado um fluxo heterogéneo de preços e notícias, decidir **quando falar**, **sobre o quê**, e
> **com que evidência anexada**, de modo a que um não-especialista possa verificar a decisão em vez
> de confiar nela.

Decompõe-se em quatro subproblemas que o sistema resolve de facto: detecção de anomalia relativa à
norma do próprio activo; atribuição (mercado/sector/empresa); recuperação de precedentes por
significado com medição do desfecho; e triagem de materialidade sob orçamento de atenção.

**⚠️ O subproblema que a directiva obriga a nomear e que este trabalho descobriu por medição:**
onde é que uma componente **aprendida** deve ficar num pipeline em que filtros determinísticos
baratos correm primeiro. Está medido (ver §4.2) e hoje vive no Cap. 6 como *limitação*. É a
constatação mais transferível do trabalho e a que está pior arrumada.

## 3. Research Questions

### 3.1 As quatro em vigor
RQ1 detecção transparente · RQ2 recuperação de precedentes · RQ3 explicações fiéis e úteis ·
RQ4 triagem aprendida. Texto exacto: [`thesis/ch1/chapter1.tex`](thesis/ch1/chapter1.tex).

### 3.2 Candidatas analisadas — e porque NÃO se renumera
A directiva §4 obriga a gerar e avaliar alternativas. Foram avaliadas três:

| Candidata | Valor | Custo | Veredicto |
|---|---|---|---|
| **C1** — manter as quatro | Já respondidas com medição, incluindo um negativo | zero | **Escolhida** |
| **C2** — "onde deve ficar a componente aprendida num pipeline filtrado?" | Alto: há evidência ao vivo única (§4.2) | Reestruturar a tese a 31 dias da entrega | Rejeitada como RQ; **adoptada como achado nomeado** |
| **C3** — "pode gerar-se linguagem ao lado de resultados calculados sem que ela se torne um canal factual?" | Alto e transferível | Idem; a RQ3 já cobre fidelidade | Rejeitada como RQ; já é a 5.ª contribuição |

**Razão da escolha, dita em voz alta:** renumerar propaga por ch1, ch6, dois abstracts, o artigo
IEEE, 28+28 slides, o guia de 93, o quizz de 64 e o pack de defesa. A sessão 42 já tinha rejeitado
RQ5/RQ6 pelo mesmo motivo. O ganho de C2 e C3 obtém-se **sem** renumerar: promovendo-as de
*limitação* a *achado*, que é escrita e não estrutura.

### 3.3 Hipóteses testáveis ainda em aberto
- **H-a.** Um modelo treinado na população **implantada** (pós-filtros) ordena melhor do que o
  treinado na população de treino. *Testável hoje;* provável inconclusivo (145 unidades efectivas).
- **H-b.** Um relatório ancorado ajuda um não-especialista mais do que os painéis sozinhos.
  *Precisa do estudo humano.*
- **H-c.** Similaridade do cosseno prediz utilidade do precedente. *Testável; nunca testada — é o
  que justificaria o chão `min_similarity`.*

## 4. Scientific Contribution

As cinco contribuições estão em [`thesis/ch6`](thesis/ch6/chapter6.tex) §Contributions Revisited.
Duas notas que este plano acrescenta:

**4.1 A contribuição está no critério que sabe dizer não.** Quatro capacidades foram construídas,
medidas e **não** implantadas (taxonomia de eventos, score de convergência, features estendidas,
EWMA). Oito afirmações foram retiradas ou estreitadas pelas próprias medições
([Matriz de Evidência](thesis/appendices/appendixA.tex)).

**4.2 O achado de colocação (C2), medido.** O gate implantado ordena ao acaso na população que vê
(ROC-AUC 0,494, IC de cluster [0,391, 0,601]) porque os filtros baratos a montante já removeram o
que ele foi treinado para remover (materialidade 0,626 ao vivo contra 0,378 no treino). Fonte:
[`docs/evaluation/evaluation_live_transfer.md`](docs/evaluation/evaluation_live_transfer.md).

## 5. AI Strategy — matriz de selecção

Regra (directiva §9, §72, §73): **seleccionar, não coleccionar**; não converter em ML o que deve
ser determinístico; não deixar em regra escrita à mão o que pode ser aprendido e comparado.

| Método | Problema | Interpretab. | Avaliado contra | Veredicto | Estado |
|---|---|---|---|---|---|
| z-score deslizante | anomalia | alta | limiar fixo, IF, LOF, EWMA | **must** | implantado |
| EWMA σ | anomalia | alta | rolling σ | melhor no proxy | **medido, não implantado** (explicabilidade) |
| Isolation Forest / LOF | anomalia | baixa | z-score | perde | rejeitado com número |
| Decomposição 2 factores + Vasicek | atribuição | alta | corte fixo ±4 | **must** | implantado |
| Estudo de evento | rótulo e desfecho | alta | — | **must** | implantado |
| SBERT (MiniLM) + cosseno | recuperação | média | lexical, aleatório, recência, FinBERT, E5, BGE | **must** | implantado |
| ONNX int8 | servir o mesmo modelo | — | paridade medida | **must** | implantado |
| LR + Platt (triagem) | materialidade | alta | volatilidade, GBM, texto | **ver §9-A1** | implantado atrás de gate |
| Predição conformal | incerteza | alta | — | forte | medido, não exposto |
| PSI/KS (deriva) | MLOps | alta | — | forte | medido |
| Taxonomia de eventos | filtrar precedentes | média | AMI vs ticker/sector | fraco demais | construído, não ligado |
| Geração ancorada + guarda | linguagem | média | red team, controlos fiéis | **must** | implantado |
| Narrador allowlist | alerta empurrado | alta | red team | forte | construído, `enabled: false` |
| **Dedup semântico de histórias** | fadiga/novidade | média | **nunca medido** | **candidato** | **ausente** (só Jaccard lexical) |
| RL / bandits · multi-agente · visão | — | — | — | fora de âmbito | rejeitado por escrito (ch6) |

## 6. Architecture · Data · Model Strategy

Arquitectura viva (v5): cliente `web/` → serviço `api/` → motores `investigator/`. **Nenhum número
é calculado na API** — é o que impede o produto e a avaliação de divergirem.
Detalhe: [`docs/design/arquitectura_sistema.md`](docs/design/arquitectura_sistema.md),
[`thesis/ch4`](thesis/ch4/chapter4.tex).
Dados: [`docs/design/data_card.md`](docs/design/data_card.md) · Modelos: [`models/README.md`](models/README.md).

## 7. Evaluation Strategy

Desenho fixado antes das experiências; linhas de base pré-comprometidas; negativos reportados;
tudo regenerável por script versionado. Índice: [`docs/evaluation/`](docs/evaluation/) (30 ficheiros).

**⚠️ Emenda que esta sessão obriga:** um chão de comparação também é uma escolha de desenho, e este
trabalho tinha um chão que não media o que dizia medir (§9-A1). Passa a valer a regra: *toda a
métrica com orçamento declara como resolve empates.*

## 8. Completion Matrix

| Área | Investigado | Decidido | Implementado | Testado | Avaliado | Documentado | Estado |
|---|---|---|---|---|---|---|---|
| Detecção de anomalia | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | fechado |
| Atribuição / decomposição | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | fechado |
| Recuperação de precedentes | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | fechado |
| Triagem aprendida (RQ4) | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | **reaberto — §9-A1, A2, A3** |
| Geração ancorada | ✅ | ✅ | ✅ | ✅ | ⚠️ parcial | ✅ | red team incompleto (4/6 lentes) |
| Explicação / XAI | ✅ | ✅ | ✅ | ✅ | ✅ fidelidade · ❌ utilidade | ✅ | **metade aberta (RQ3)** |
| Produto / UI (v5) | ✅ | ✅ | ✅ | ❌ | ⚠️ | ✅ | **sem testes no caminho vivo** |
| Dados e proveniência | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | fechado |
| Privacidade / segurança | ✅ | ✅ | ✅ | ✅ | — | ✅ | credenciais por rodar (humano) |
| Tese (EN+PT) | ✅ | ✅ | ✅ | portas | ✅ | ✅ | verde; ver §10 |

## 9. Registo de achados desta sessão

> **⚠️ Como foram obtidos, porque isso muda o peso de cada um.** Foi lançada uma auditoria de 8
> lentes com verificação adversária. **Uma lente completou; sete morreram no limite de gasto da
> conta, e morreram TODOS os verificadores.** É a 6.ª vez que este padrão acontece neste projecto e
> continua a ser a mesma armadilha: um workflow que perde os verificadores devolve um veredicto
> aparentemente limpo que é, de facto, **ausência de verificação**. Por isso: os achados marcados
> **[V]** foram reproduzidos por mim contra o código e os dados; os marcados **[NV]** vêm da lente
> sobrevivente e **ainda não foram verificados**. As sete áreas por auditar estão em §13.

### A. Achados de IA / avaliação

**A1 — [V] O chão da precisão@orçamento não mede o que diz medir. CRÍTICO.**
A tese afirma que a triagem sobe a fracção de alertas materiais de `0,163` **"(picking blindly)"**
para `0,632`, *"quase quatro vezes"* (`thesis/ch5/chapter5.tex:524`, ecoado em `ch6:38`, `ch6:131`,
`appendixA:198` e `:293`, e em três documentos de defesa).
`alert-always` usa um score **constante**; `precision_at_daily_budget` ordena com `argsort(...,
kind="stable")`; o CSV está ordenado por `(date, ticker)`. Logo o chão não escolhe às cegas —
**escolhe por ordem alfabética**. Reproduzido: as 1.105 linhas seleccionadas são **todas AAPL**.
Medido agora, sob o mesmo protocolo (que reproduz o congelado 0,632 como porta):

| ordenação | precisão@5 |
|---|---|
| chão publicado (alfabético) | 0,1629 |
| **aleatório real, 40 sementes** | **0,3790 ± 0,0170** |
| **prior de volatilidade por ticker (13 constantes, só treino)** | **0,6624** |
| modelo implantado | 0,6317 |

⇒ o ganho é **1,67×**, não ~4×; e **uma tabela de 13 constantes bate o modelo treinado**.
Evidência regenerável nova: [`scripts/evaluate_budget_baselines.py`](scripts/evaluate_budget_baselines.py)
→ [`docs/evaluation/evaluation_budget_baselines.md`](docs/evaluation/evaluation_budget_baselines.md).
**Não afecta** PR-AUC/ROC-AUC/Brier nem o negativo da RQ4.
**Isto fortalece a tese** — é a terceira vez que o método simples ganha, e a tese já defende isso.

**A2 — [V] RESOLVIDO nesta sessão, e a afirmação da tese fica de pé.** O artefacto que sustentava
*"survives cluster bootstrap"* **não continha as linhas do texto**:
`evaluate_triage_uncertainty.py:69` corre `families = ["vol", "context"]` salvo `--with-text`, e o
`.md` tinha só essas duas linhas e a diferença `vol−context` — enquanto a prosa por baixo falava de
`vol−full` e `context−full`. Re-corrido com `--with-text`: as cinco famílias reproduzem os
congelados **ao milésimo** (Δ ±0,000) e as diferenças em falta aparecem —
`vol−full +0,0480` IC [+0,0320, +0,0660] · `context−full +0,0432` IC [+0,0269, +0,0610], ambas
P(Δ>0)=1,00. **O veredicto do texto é cluster-robusto e agora tem artefacto.**

⚠️ **A lição vale mais do que o achado, e é nova neste projecto:** os números batem exactamente com
os que o `CLAUDE.md` registou na sessão 41, portanto a corrida original **foi** feita com texto — e
uma corrida posterior **sem** a flag reescreveu o ficheiro por cima e **apagou três linhas de
evidência sem um único erro**. Um artefacto regenerável regenerado com argumentos diferentes é
indistinguível de um artefacto correcto. *Remédio: o script deve gravar as famílias que correu no
cabeçalho e recusar-se a emitir prosa sobre diferenças que não calculou.*

**A3 — [NV] AMD e NFLX são pontuados fora da distribuição em produção.** `triage/dataset.py::SECTORS`
não os tem; `infer.py:48` faz `SECTORS.get(t, "")` ⇒ one-hot de sector **todo a zeros**, padrão que
não existe em nenhuma das 79.753 linhas de treino. São 2 dos 12 nomes da watchlist. *(O mapa da
`relevance.py` regista explicitamente esta divergência — para outro mapa.)* **Verificado por mim
que o mapa não os tem e que o fallback é silencioso**; não verificado o efeito no score.

**A4 — [NV] Grelha de rótulos por usar.** `build_dataset.py` escreve nove colunas
`label_t{τ}_h{h}`; nenhum script alguma vez as lê. Todo o veredicto da RQ4 assenta num único
(τ=0,02, h=3) sem análise de sensibilidade — que já está paga em disco.

**A5 — [NV] Platt calibrado numa validação a 47,0% e aplicado a uma população a 37,8%**; os limiares
implantados (`min_materiality`, `materiality_ladder`) assentam nessa escala.

### B. Achados de produto / UX

**B1 — [V] O filtro temporal não propaga.** `S.range` só reconstrói o gráfico
(`web/assets/app.js:738-741`); o painel de notícias mostra 60 dias (`:298`) e os alertas 12
(`:258`) seja qual for o intervalo. **A v3 tinha garantido o contrário** — a sessão 47 fez o gráfico
devolver a janela desenhada para as tabelas a consumirem, "para não poderem divergir". Esse
invariante vivia em `app/tables.py`, que hoje **só é importado pelo dashboard v3 retirado** e pelos
seus 24 testes. Capacidade perdida na reconstrução v5. *(Directiva §34.)*

**B2 — [V] Dois documentos de governo em contradição.**
`docs/design/dashboard_acceptance.md:217` proíbe a probabilidade da triagem em **qualquer** vista de
produto (critério H2, "é um número para a frente"). A v5 serve-a em `/api/triage/{ticker}`, em
`/api/evidence`, no pacote de evidência (`intelligence/context.py:277`) e o analista pode pedi-la
por pergunta em linguagem natural. A moldura no produto está **correcta** ("either direction",
materialidade e não direcção) — e é a sessão 55 que estabelece que a distinção certa é
*materialidade vs direcção*. **O que está desactualizado é o critério**, e um critério contornado
em silêncio é indistinguível de um critério corrigido em silêncio.

**B3 — [V] O caminho vivo não tem um único teste.** Zero testes tocam `api/` ou `web/`
(359 + 352 + 821 linhas). Entretanto o Streamlit retirado tem 67 (`test_dashboard_v3` 16,
`test_tables` 24, `test_app_triage` 14, `test_v4_views` 10, `test_dashboard_launch` 3).

### C. Ferramentas e documentação

**C1 — [V] `scripts/check_all_gates.py` rebentava antes de correr uma única porta.** Numa consola
`cp1252` (o caso do Windows do aluno) o primeiro `print` de um cabeçalho com `═` levantava
`UnicodeEncodeError`. `corre()` já forçava utf-8 na descodificação dos **subprocessos** — faltava a
saída do **próprio script**. **CORRIGIDO nesta sessão.**

**C2 — [V] A mesma porta reportava `? passaram`.** O `addopts` do `pyproject` já traz `-q`; a porta
juntava outro ⇒ `-qq`, e a `-qq` o pytest suprime a linha de resumo. Perdia exactamente o número que
oito documentos deste projecto sincronizam. **CORRIGIDO nesta sessão.**

**C3 — [V] `docs/defence/mapa_competencias.md` não tem uma linha para a camada generativa** — a 5.ª
contribuição, e a que corresponde à UC de *Natural Language and Generative AI*. Nem nas "três
respostas que valem mais", nem na tabela de buracos.

**C4 — [V] CORRIGIDO.** O `CHECKLIST.md:44` dizia PT 134 pp (são 139) e EN 128 (são 130 depois de P1); o guião e o simulacro de defesa diziam 124/134. Todos ressincronizados.

**C5 — [V] Constantes que travam alertas e nunca foram derivadas:** `min_similarity: 0.45`,
`max_per_ticker_per_day: 2`, `recency_half_life_days: 120`, e o limiar `0.6` do
`quase_repetida`. Contrastam com a `materiality_ladder`, que o projecto **derivou** do varrimento de
política precisamente para não ter constantes escolhidas. A `min_similarity` é o gate mais agressivo
do funil. *(Achado em convergência independente: por mim e pela lente sobrevivente.)*

### E. Camada de inteligência *(lente feita à mão, 2026-08-13)*

**E1 — [V] FURO REAL NA GUARDA, reproduzido e FECHADO nesta sessão.** A correcção da sessão 56
ligou cada número **à frase** que o cita. Mas a isenção de citações verbatim continuou a ser do
**pacote**: `_mask_exempt` percorria `bundle.facts` **todos**. A assimetria deixava um canal aberto:

```
NVDA stood out today, moving 8% [f1]      → rejeitado  (correcto)
NVDA stood out today, "up 8%"  [f1]       → PASSAVA    (mesmo 8, mesma âncora)
```

porque `"up 8%"` é substring da manchete do `f2`. O leitor via a âncora resolver para um facto que
**não continha aquele número** — exactamente a travessia que a camada existe para garantir.
**Não é um bypass geral:** a cadeia tem de ser mesmo substring de uma manchete capturada (um valor
inventado entre aspas continua a ser rejeitado), portanto o número é real mas **mal atribuído**.
**Corrigido:** `_mask_exempt(text, bundle, fids)` limita as manchetes citáveis às dos factos que a
frase cita; a passagem de **linguagem** proibida mantém o âmbito do pacote de propósito (citar a
previsão de uma fonte é legítimo). **+2 testes de regressão nos dois sentidos**; corpus do red team
inalterado (**23/23** ataques bloqueados, **8/8** controlos fiéis), 50/50 testes da camada verdes.

**⚠️ CORRECÇÃO A MIM PRÓPRIO (lente §9-I, feita depois).** Escrevi aqui que isto *"obriga a emendar
o `RESIDUAL` e a tese"*. **Não obriga — é o contrário.** Lida a frase exacta, o `ch6` afirma que a
verificação confirma *"that the sentence's numbers belong to it"* (`thesis/ch6:382`,
`thesis-pt/ch6:400`). Essa afirmação era **falsa antes da correcção** e é **verdadeira depois**.
Ou seja: E1 era uma inconsistência **tese↔código** em que a tese prometia a garantia certa e o
código não a entregava toda, e foi resolvida do lado certo. **Nenhuma frase da tese precisa de
mudar.** O que pode valer uma linha é a *história* — a garantia teve um furo por texto citado e foi
fechada —, mas isso é escolha editorial, não correcção.

**E2 — [V] E eu reproduzi ao vivo o defeito que documentei em §9-A2.** Corri
`evaluate_intelligence_guard.py --offline` para confirmar o corpus; a flag regenerou o `.md` **sem**
a secção "Geração real" (27 secções, latência 1,6 s, mistura de fornecedores) — que a tese cita e
que a Matriz de Evidência usa. **23 linhas de evidência apagadas, exit 0, nenhum aviso.** Restaurado
do git. É a **segunda** instância da mesma classe em duas horas, agora com demonstração.
*Remédio (vale para os dois scripts): um gerador que só regenera parte do documento tem de recusar
escrever, ou declarar no cabeçalho o que não recalculou.*

### F. Recuperação / KB *(à mão)*

**F1 — [V] A deduplicação de precedentes é de texto exacto; a de alertas não é.** `merged_precedents`
deduplica por `" ".join(headline.lower().split())` — igualdade literal. O comentário ao lado explica
por que razão isto importa, e explica-o melhor do que eu conseguiria: mostrar a mesma história como
precedentes independentes *"não é uma imprecisão de apresentação, é uma afirmação falsa sobre a
evidência: três observações independentes pesam muito mais do que uma vista três vezes"*. A correcção
de 2026-08-02 fechou o caso do **texto idêntico** entre tickers. **A mesma história escrita por dois
meios continua a contar como duas observações** — e o alerta di-lo em voz alta: *"3 of 3 shown cases
moved down"*. O projecto **já tem** o detector para isto (`quase_repetida`, Jaccard 0,6) e aplica-o
**só ao caminho dos alertas** (`run_alerts.py:280`), nunca aos precedentes. Verificado: é a única
invocação no repositório.

### G. Pipeline de decisão *(à mão)*

**G1 — [V] O 5.º gate não é instrumentado, e o ecrã mente por causa disso.** `_gate(...)` é chamado
**dentro** de `scan_news`; `filter_new_alerts` (tecto diário, escada de materialidade,
quase-repetição) corre **depois**, e nada re-etiqueta o que ele suprime. Logo `stage="alerted"`
significa *"sobreviveu à varredura"*, não *"foi entregue"*. E o SPA traduz `alerted` para
**"Alert sent"** (`web/assets/app.js:635`). ⇒ **o screener pode dizer ao utilizador que um alerta
foi enviado quando não foi** — na vista cuja razão de existir é *"o silêncio é uma decisão deste
sistema, logo tem de ser inspeccionável"*. É também o único gate cuja coluna "efeito medido" no
`cadence_contract.md` não tem número, e agora sabe-se porquê: não há de onde o tirar.
*(A contagem "cinco gates" da tese está **correcta** — bate com o `cadence_contract`. O `gate_log`
só cobre os quatro primeiros.)*

### H. Dados e licenciamento *(à mão)*

**H1 — [V] A atribuição do FNSPID está cumprida** (tese `appendixA:341`, `ch3:292` e `ch3:1002`,
`data_card.md`, `README:201`). Sem achado.

**H2 — [V] Mas a decisão de licença pendente tem duas restrições que o `CHECKLIST` não menciona.**
O `CHECKLIST.md:45` apresenta a escolha como livre ("MIT/Apache"). Só que o repositório **já
distribui**: (a) três ficheiros derivados do FNSPID — `data/samples/fnspid_news_sample.csv`,
`kb_fnspid_sample.jsonl` e `kb_fnspid_light.jsonl` (este é o que a app implantada lê) — sob
**CC BY-SA 4.0**, que é **share-alike**; e (b) `meia-style.cls` sob **CC BY-NC-SA 3.0**, que é
share-alike **e NonCommercial**. Não sou jurista e não é um defeito: é uma restrição sobre uma
decisão em aberto, e um `LICENSE` que diga "MIT" sem ressalva seria inexacto para esses caminhos.
**Levar isto ao orientador junto com a pergunta**, não depois.

### I. Consistência tese↔código *(a última lente, feita à mão)*

**Método:** não amostragem. Lidos o `ch4` §Decision Logic, §The Life of One Alert e §Overview contra
`run_alerts.py`, `detector.py`, `explain.py` e `config/alerts.yaml`; e os **quatro excertos de código**
que o `ch3` publica contra os ficheiros que citam.

**I1 — [V] Os quatro excertos de código NÃO derivaram.** `lst:zscore` bate com `detect_latest`
linha a linha, incluindo a fatia `r.iloc[-window - 1 : -1]`, o `ddof=1` e a guarda `sigma > 0`;
`lst:split` bate com `assign_splits`; `lst:contrib` bate com `lr_group_contributions`. É o resultado
que interessa: um excerto publicado que já não é o código é indefensável, e não há nenhum.

**I2 — [V] As afirmações verificáveis do `ch4` conferem.** Tecto de 2/ticker/dia
(`max_per_ticker_per_day: 2`); pisos derivados 0,49/0,64 (`materiality_ladder`); "o scan emite no
máximo uma manchete por empresa por ciclo"; o detector devolver *(z, μ, σ, janela, limiar)* —
`AnomalyResult` tem exactamente esses campos; funil 944→42 = **22:1** bate com
`alert_funnel.md`; "as dez empresas que a watchlist tinha então" está correctamente datado agora que
são doze. **Também confere a frase que já foi um defeito:** *"ships disabled in the default
configuration and is enabled in the reference deployment"* — o defeito do código é `None`
(desligado) e é o ficheiro de configuração implantado que o liga.

**I3 — [V] E1 era, afinal, desta classe — a tese estava certa e o código é que não cumpria.**
Ver a correcção dentro de §9-E1. Nenhuma frase da tese muda.

**I4 — [V] O alcance de A1 é MUITO maior do que eu disse.** Tinha escrito "8 artefactos"; são
**~48 sítios em 20 ficheiros**: as duas teses (`ch4`, `ch5`, `ch6`, apêndice), o **artigo IEEE**
(`paper/main.tex:39` e `:239`), os **três decks** (EN, PT e guia de estudo, 7 sítios só no guia), o
**quizz** (`index.html:301`, `:303`, `:567`, `:667` — e a pergunta 301 diz *"vs 0,163 às cegas"*,
com resposta auto-corrigida), cinco documentos de defesa e o `learning.md`.
⚠️ **E seis sítios com `0.163` NÃO são este número** — são a precisão do LOF na tabela de detectores
(`ch5:169`, `ch5:200` e os gémeos PT, `evaluation_anomaly_ext.md:17`, `guia_estudo:2060`). Confundi-los
seria a 5.ª vez que um grep ingénuo produz falsos positivos nesta linha de trabalho: a separação
faz-se exigindo `0,632` na mesma linha e conferindo o resto à vista.

### D. Dívida técnica
- `numpy 2.5` emite `DeprecationWarning` ao carregar os bundles joblib (70 avisos na suite);
  falhará numa versão futura. Advisory aberto desde a sessão 41.
- `Procfile.v4.bak`, `app/dashboard*.py`, `app/streamlit_app.py` continuam versionados. **Isto é
  deliberado** (as figuras das teses documentam a v3/v4) — mas não está escrito em lado nenhum
  que seja deliberado.

## 10. Thesis Gaps · Evidence Gaps

- **Estrutural:** nada. Portas verdes: 709 testes, ruff limpo, EN 130 pp / PT 139 pp, 274 refs /
  168 labels sem tipo errado, paridade EN↔PT 0 assimetrias, congelados intactos (12/12 verdes,
  verificado nesta sessão).
- **De conteúdo:** A1 (chão errado, propaga a 8 artefactos) e A2 (evidência em falta).
- **Em aberto por desenho:** utilidade (RQ3) sem estudo humano; red team da guarda em 2 de 6 lentes.

## 11. Registos que já existem (não duplicar)

| Registo | Ficheiro |
|---|---|
| Decisions Log | [`progress/DECISIONS.md`](progress/DECISIONS.md) + `CLAUDE.md` |
| Experiment Log | [`docs/evaluation/`](docs/evaluation/) — 30 documentos regeneráveis |
| Model Registry | [`models/`](models/) + sidecars `.json` |
| Dataset Registry | [`docs/design/data_card.md`](docs/design/data_card.md) |
| Claim audit | [`thesis/appendices/appendixA.tex`](thesis/appendices/appendixA.tex) §Evidence Matrix |
| Competências | [`docs/defence/mapa_competencias.md`](docs/defence/mapa_competencias.md) |

## 12. Traceability Matrix (componente → utilizador)

Eixo diferente da Matriz de Evidência (que audita **afirmações**): aqui segue-se cada **componente**
até ao ecrã. A coluna que interessa é a última — expõe o que foi avaliado e nunca chega ao
utilizador, e o que chega ao utilizador sem avaliação.

| Componente | RQ | Dados | Métrica | Chega ao utilizador? |
|---|---|---|---|---|
| z-score | RQ1 | preços | amplitude da taxa de disparo | ✅ veredicto + tira de raridade |
| Excedência (raridade) | RQ1 | preços | contagem empírica | ✅ tira de marcas |
| Decomposição | — | preços + ETF | — (identidade por construção) | ✅ barras divergentes |
| Volume | — | preços | — | ✅ texto ("3,2× usual") |
| Recuperação SBERT | RQ2 | FNSPID + KB viva | precision@5 | ✅ rota `/api/precedents` |
| Estudo de evento | RQ2 | preços | impacto medido | ✅ desfecho a +5d |
| Triagem LR+Platt | RQ4 | FNSPID | PR-AUC, prec@orçamento | ⚠️ gate silencioso + pacote de evidência (ver B2) |
| Conformal | RQ4 | FNSPID | cobertura | ❌ **medido, nunca exposto** |
| Deriva PSI/KS | — | ao vivo | PSI | ❌ **medido, nunca exposto** |
| Taxonomia | RQ2 | FNSPID | AMI | ❌ construído, não ligado |
| Convergência | — | multi-sinal | prec@orçamento | ❌ construído, perdeu |
| Guarda de ancoragem | RQ3 | pacote | ataques bloqueados | ✅ âncoras `[f3]` clicáveis |
| Dedup de histórias | — | manchetes | **nenhuma** | ✅ actua, **nunca medido** |

## 12a. Auditoria-mestra (§78) — 2026-08-20

A directiva foi reenviada e a §78 manda **inspeccionar antes de mexer**. A inspecção está em
[`INVESTIGATOR_MASTER_AUDIT.md`](INVESTIGATOR_MASTER_AUDIT.md): o inventário contado, as **nove
decisões** que o sistema toma antes de interromper alguém com o estado de cada uma (aprendida,
determinística por medição, ou determinística por falta de rótulos), a matriz de rastreabilidade
com os sete elos da §66, e a classificação de cada dependência externa de IA que a §30 exige.

**Produziu dois achados, e um deles virou experiência.**

**A1 — a recuperação foi avaliada podendo ver o futuro, e isso não estava dito.** O protocolo da
QI2 proíbe o candidato de ser da mesma empresa e mais nada; não o proíbe de ser posterior à
consulta. Corrido o mesmo protocolo com a restrição da produção — só candidatos **estritamente
anteriores** — a precisão@5 desce de $0.595$ para $0.513$, **mas o chão desce quase o mesmo**
($0.333 	o 0.259$) e a margem sobre o acaso muda apenas $0.008$. O método mantém a vantagem.
`scripts/evaluate_retrieval_causal.py` → `docs/evaluation/evaluation_retrieval_causal.md`; a tese
ganha a Secção 5.5.4 e a Matriz de Evidência ganha uma linha **estreitada**.

**A2 — a relevância é a única decisão central que continua uma regra, e não pode ser aprendida
honestamente.** Deita fora 67.3% das manchetes e é classificação binária de texto, portanto
aprendível em princípio; mas o único rótulo disponível seria a saída da própria regra, o que torna
a experiência circular, e a §12 e a §63 proíbem fabricar rótulos. **É o mesmo bloqueio do estudo
de utilidade:** duzentos itens anotados desbloqueiam os dois.

---

## 12b. Validação contra a directiva-mestra (2026-08-20)

> O aluno reenviou a directiva-mestra e pediu para a **validar**. Isto é a validação, e a
> primeira coisa a dizer é sobre o **calendário**: a directiva descreve um programa de
> investigação e engenharia que ela própria admite poder durar *"semanas ou meses"* — novos
> conjuntos de dados, novas experiências, treino de modelos, reestruturação da dissertação.
> **Faltam 24 dias para a entrega**, e a instrução mais recente do aluno, na mesma sessão, é
> *"minimizar erros e bugs, simplicidade, clareza, deixar pronto para entrega, mesmo que
> tenhamos de remover coisas de que não temos a certeza"*.
>
> As duas coisas não se executam ao mesmo tempo, e não é preciso escolher às cegas: a maior
> parte da directiva **já está satisfeita** por trabalho feito nas sessões anteriores. O que
> falta é maioritariamente do tipo que a própria directiva manda declarar em vez de fabricar
> (§60, §63, §64). Portanto: **valida-se, declara-se o que falta, e não se abre obra nova.**

| § | O que a directiva exige | Estado | Onde |
|---|---|---|---|
| 3–5 | problema de investigação formulado, subproblemas identificados | ✅ | Cap. 1; três QI |
| 6 | identidade técnica própria, não `API → LLM → resposta` | ✅ | dados, modelo e avaliação próprios; a camada de LLM foi **retirada do produto** |
| 7, 73 | as decisões centrais aprendidas dos dados, não só regras | ⚠️ **parcial, e medido** | a triagem é aprendida (79 753 exemplos, LR+Platt); a **detecção é estatística por decisão**, e o Cap. 5 mostra que os detectores aprendidos (IF, LOF) perdem |
| 9 | seleccionar, não coleccionar métodos | ✅ | matriz §5; três técnicas construídas e **duas não implantadas por medição** |
| 11–12 | dados como artefacto de primeira classe, conjunto próprio | ✅ | 79 753 exemplos com rótulo anti-lookahead + 38 214 precedentes medidos |
| 14–15 | linhas de base primeiro, comparação de modelos | ✅ | e é o resultado central: **o simples ganhou três vezes** |
| 16–17 | explicabilidade ≠ geração | ✅ | contribuições aditivas do modelo; a geração saiu do produto |
| 19–21 | inteligência temporal, evento vs anomalia | ✅ | z-score contra a norma da própria empresa; embargo; maturação a 8 dias |
| 22–23 | alerta é mais do que um limiar; relevância ≠ importância | ✅ | funil de nove etapas; relevância e materialidade são camadas distintas |
| 24 | novidade e redundância semântica | ✅ | `investigator/dedup.py`, usado nos dois caminhos |
| 25 | fadiga de alertas | ✅ | orçamento diário, piso escalonado, supressão registada |
| 26–27 | personalização e humano no ciclo | ❌ **não feito** | declarado como trabalho futuro |
| 28–30 | ciclo de vida e artefactos do modelo | ✅ | `models/` versionado, congelados verificados por porta |
| 31–32 | estratégia de LLM; o *chatbot* deve existir? | ✅ **decidido: não** | retirado a 2026-08-20 — ver `api/main.py` |
| 34 | filtro temporal global | ⚠️ **não implementado** | a v6.1 tem **uma selecção** (empresa) que governa a página; não tem 1D/5D/1M. A dissertação não o afirma |
| 35–37 | auditoria de UX, divulgação progressiva | ✅ | revisão F6 |
| 42–45 | avaliação desenhada antes das afirmações, erros, ablação | ✅ | `docs/evaluation/`, 20+ documentos regeneráveis |
| 47 | fugas temporais | ✅ | divisão cronológica + embargo + **teste que muta o futuro** |
| 48–49 | ética, privacidade, segurança | ✅ | sem previsão de direcção; guarda de vocabulário; credenciais por rodar (humano) |
| 53 | tese ↔ código consistentes | ✅ | verificado nesta sessão antes de mexer no painel |
| 60 | avaliação com utilizadores | ❌ **não feita, e declarada** | pacote pronto; é o único item com relógio |
| 61 | agradecimentos | ⚠️ rascunho | falta a voz do aluno |
| 62 | declaração de IA | ⚠️ **e há uma tensão a resolver com o orientador** | a directiva sugere descrevê-la como auxiliar de sintaxe e LaTeX; para este trabalho isso **subestima**, e a declaração actual diz a extensão real |
| 63–64 | nada fabricado; afirmações classificadas | ✅ | Matriz de Evidência, com 13 afirmações **retiradas ou estreitadas** |
| 65–68 | plano-mestre, rastreabilidade, matriz, continuidade | ✅ | este ficheiro + `CLAUDE.md` |

**O que a directiva pede e este trabalho conscientemente NÃO faz**, com a razão:

1. **Agentes, sistemas multi-agente, aprendizagem por reforço.** A directiva avisa duas vezes
   para não os acrescentar por serem actuais (§8, §71). Não há problema neste sistema que os
   peça.
2. **Mais fontes de dados.** §39 pede que cada fonte tenha um papel justificado. As três
   actuais foram escolhidas por medição, e há uma rejeitada por medição.
3. **Reestruturar a dissertação** (§54). A estrutura actual tem seis capítulos, compila a zero
   erros e está auditada afirmação a afirmação. Reestruturar a 24 dias trocaria uma coisa
   verificada por uma por verificar.

---

## 13. Next Priorities

**Realidade que enquadra tudo:** entrega **13/09/2026** — 31 dias. Herda-se a decisão da sessão 42:
**Track A** (tese, aditivo, congelados intactos) até à entrega; **Track B** (ambição de produto)
depois. Nada abaixo pede reestruturação da tese.

### P1 — ✅ **FEITO** (2026-08-13). Chão da precisão@orçamento corrigido em todo o lado
Executada a opção aditiva recomendada: a tabela congelada **fica** (é uma saída real do protocolo) e
passa a trazer a ressalva na legenda; ao lado entra a **Tabela dos chãos** com as quatro ordenações,
nas duas línguas. O `0.163` que sobrevive no texto é sempre a explicar-se a si próprio.

**Alcance coberto (~48 sítios, 20 ficheiros):** `ch4`, `ch5`, `ch6` ×3 e `appendixA` ×2 nas **duas**
teses; artigo IEEE ×2; slides EN e PT ×3 cada; guia de estudo ×6; quizz ×4 (a resposta
auto-corrigida continua a ser a mesma opção); `guiao_de_defesa` ×4, `simulacro_defesa` ×3,
`THESIS_FACT_SHEET`, `autoteste`, `guia_pessoal`, `learning.md`, `roadmap_rq4`.
Os **6 sítios do LOF** ficaram intocados, como deviam.

**O que a tese passa a dizer:** o ganho é **1,67×** e não ~4×; um prior de 13 constantes dá
**0,662** contra os 0,632 do modelo; e o veredicto da RQ4 ganha a ressalva de que *ordenar por
volatilidade* compensa, não que *aprender* compensa. A Matriz de Evidência ganha duas linhas
(uma **estreitada duas vezes**, uma **retirada**) e o total de retiradas passa de "oito" — que já
estava **desactualizado em três** — para **doze**.

⚠️ **Uma coisa que NÃO se fez, de propósito:** o `docs/evaluation/evaluation_triage.md` continua a
mostrar `0.163` sem ressalva. É gerado pelo `train_triage.py` e editá-lo à mão contraria a regra
"não editar à mão"; corrigi-lo a sério obriga a re-correr o treino. **Fica para quando o treino for
re-corrido** — e a ressalva deve entrar no gerador, não no ficheiro.

**Portas depois de P1:** 709 testes, ruff limpo, EN **130 pp** / PT **139 pp** a 0 erros e 0
indefinidas, overfull máx **14 pt** nas duas (a tabela nova precisou de `\small` e coluna mais
estreita: a versão PT chegou a 54 pt), paridade EN↔PT **0 assimetrias**, 274 refs / 169 labels
iguais nas duas, congelados intactos.

### P2 — A2 fechado · resta a guarda que o impede de voltar · S
O artefacto foi reposto e a afirmação da Matriz de Evidência está sustentada (§9-A2). O que **falta**
é impedir a reincidência: `evaluate_triage_uncertainty.py` deve (a) escrever no cabeçalho as
famílias que correu, e (b) tornar o bloco *"Leitura honesta"* condicional em `have_full`, para nunca
mais poder afirmar uma diferença que não calculou.

### P3 — A3 (AMD/NFLX sem sector) · S
2 de 12 nomes implantados pontuados fora da distribuição, em silêncio. Mapear para `tech` na
inferência **ou** falhar alto. Frozen intacto (as colunas já existem).

### P4 — Estudo humano (RQ3) · **só o aluno pode**
Continua a ser a única lacuna verdadeiramente aberta, e agora fecha quatro coisas: metade do
objectivo 4, metade da RQ3 (que passou a cobrir o texto gerado), "chegou a história *certa*?" da
cobertura, e H-b. 6–10 pessoas, ~15 min. Material pronto: `scripts/build_usefulness_pack.py`.

### P5 — ✅ **FEITO** (2026-08-13)

**C3 — mapa de competências.** Linha nova para **Linguagem natural e IA generativa** (a UC que
faltava, e a resposta à pergunta D5), com os números da guarda. A resposta *"onde está a engenharia
de IA?"* ganha o exemplo mais forte que há — **contra o próprio trabalho**: verificar o que a minha
linha de base media reduziu o ganho anunciado de ~4× para 1,67×. E dois buracos novos ditos antes
que perguntem: a garantia do texto puxado é **blocklist** (mais fraca que a allowlist do alerta), e
o red team correu **2 de 6 lentes**. **⚠️ Aviso novo em destaque: NÃO dizer "quadruplica".**

**B2 — critério H2 emendado em voz alta.** Dizia *"zero números previstos"* e proibia a coisa
errada — a v5 servia a probabilidade da triagem em três sítios, portanto **o produto implantado
violava o critério tal como estava escrito**. A sessão 55 já tinha estabelecido porquê ao corrigir o
*"not a forecast"* do alerta: a distinção verdadeira é **materialidade vs direcção**. O H2 passa a
proibir a **direcção** e a exigir a moldura onde a probabilidade aparecer; a linha do §6.5 fica
**riscada e datada**, não apagada.

**C4** — feito na P1 (contagens ressincronizadas em 8 ficheiros).

**A4 — grelha de sensibilidade de rótulos: o negativo da RQ4 é MAIS forte do que se sabia.**
As nove colunas `label_t{τ}_h{h}` eram escritas desde sempre e **nunca tinham sido lidas**. Lidas:
a volatilidade iguala ou bate o contexto+texto em **9 de 9 células** (τ ∈ {0,015, 0,02, 0,03} × h ∈
{1, 3, 5}), com prevalências de **0,082 a 0,597**, e a célula congelada reproduz exactamente
(0,542 / 0,538 / 0,496). ⇒ *"escolheste τ=0,02 e h=3 — e se tivesses escolhido outra coisa?"* deixa
de ser uma pergunta com resposta. `scripts/evaluate_triage_labelgrid.py` →
[`evaluation_triage_labelgrid.md`](docs/evaluation/evaluation_triage_labelgrid.md). Na tese: parágrafo
novo nas Ressalvas do CS4, EN+PT.

**C5 — o chão `min_similarity: 0.45` NÃO é derivável, e isso é o resultado.**
A hipótese H-c foi testada: se um cosseno mais alto indicasse um precedente mais informativo, a
concordância de direcção entre o precedente e a consulta subiria com a similaridade. **Não sobe.**
Acima do chão **0,504**, abaixo **0,506**, com o chão de acaso **medido** (emparelhamento aleatório
sob as mesmas restrições, não assumido como 0,5) em **0,507**; a diferença é −0,0012 e o intervalo
contém zero. ⇒ o 0,45 **não** pode ser justificado como escolhendo precedentes que predizem melhor,
e a tese passa a dizer o que ele defensavelmente é: **controlo de volume sobre coerência temática**.
`scripts/evaluate_similarity_floor.py` →
[`evaluation_similarity_floor.md`](docs/evaluation/evaluation_similarity_floor.md). Na tese: passagem
nova no §Fluxo de Dados do Cap. 4, EN+PT.
⚠️ O documento gerado avisa explicitamente para **não comparar** este número com o `0,708` do Caso 3:
são medidas com chãos de acaso diferentes (~0,5 par-a-par vs ~0,69 de maioria interna), e pô-las lado
a lado seria repetir o erro das purezas com cardinalidades diferentes.

**Matriz de Evidência: 12 → 13 linhas retiradas/estreitadas** (a nova é o chão de similaridade), e a
linha do texto-vs-volatilidade ganha *"e às nove definições de rótulo"*.

### P5 (original) — Baixo custo, alto retorno em defesa
- **C3** linha da camada generativa no mapa de competências (é a resposta à pergunta D5, a mais
  provável do júri: *"onde está a IA?"*).
- **B2** actualizar o critério H2 para dizer o que proíbe mesmo (direcção), em voz alta.
- **C4** contagem de páginas no CHECKLIST.
- **A4** grelha de sensibilidade de rótulos — nove regressões minúsculas, dados já em disco.
- **C5** derivar `min_similarity` (testa H-c) — ou declará-la escolhida, com a razão.

### P6 — Track B (depois da entrega)
Dedup semântico de histórias medido contra o Jaccard actual (a 3.ª comparação simples-vs-aprendido);
testes no caminho vivo (B3); propagação do filtro temporal (B1); completar o red team (4/6 lentes).

### Open Questions (do aluno, não minhas)
1. P1: corrigir a tabela congelada ou acrescentar em texto? *(recomendação acima)*
2. Marcar o estudo humano — é calendário, não engenharia.
3. Rodar as 4 credenciais (PAT do GitHub primeiro, tem `admin: true`).
4. Agradecimentos, dedicatória e declaração de IA com o orientador — **a declaração subestima o que
   aconteceu**: foi escrita antes da camada generativa e da reconstrução do produto.

### Estado da auditoria — **completa**
Sete lentes morreram no limite de gasto; **as sete foram refeitas à mão** (§9-B produto/UI,
§9-C ferramentas e documentação, §9-E inteligência, §9-F recuperação/KB, §9-G pipeline de decisão,
§9-H dados e licenciamento, §9-I consistência tese↔código). A manual encontrou o que a automática
não viu — incluindo o furo da guarda (E1), **fechado com regressão nos dois sentidos**.

**O resultado da última lente é largamente positivo e vale dizê-lo:** os quatro excertos de código
publicados na tese **não derivaram**, e as afirmações verificáveis do `ch4` sobre o sistema
implantado **conferem**. A tese descreve o sistema que existe. Os dois defeitos desta classe
encontrados hoje apontam nos dois sentidos opostos: **A1** (a tese afirma mais do que a medição
sustenta) e **E1** (a tese afirmava uma garantia que o código não cumpria — resolvido do lado do
código).

**O currículo MEIA** não precisa de lente: o mapa existe
(`docs/defence/mapa_competencias.md`) e o único buraco é o C3 (sem linha para a camada generativa).
A resposta à pergunta *"onde está a IA?"* está em §4.1 — no critério que sabe dizer não — e ganhou
esta sessão dois exemplos novos e melhores: **A1**, onde a medição correcta reduz o ganho que o
próprio trabalho reivindicava, e **E1**, onde o red team interno encontra e fecha um furo na
garantia mais recente.
