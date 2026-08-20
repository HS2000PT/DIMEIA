# INVESTIGATOR — Auditoria-mestra

> Escrita a 2026-08-20, em execução do §78 da directiva-mestra, que manda **inspeccionar antes
> de mexer**. Tudo o que está aqui foi medido nesta sessão com comandos sobre o repositório, e
> não citado de memória nem do `CLAUDE.md`. Onde um número vem de um documento gerado, o
> documento é nomeado.
>
> A auditoria acompanha o [`INVESTIGATOR_MASTER_PLAN.md`](INVESTIGATOR_MASTER_PLAN.md), que
> guarda o plano; aqui fica o **retrato do que existe**.

---

## 1. O que existe, contado

| | |
|---|---|
| Ficheiros versionados | 210 `.py` · 123 `.md` · 36 `.tex` · 53 `.png` |
| `investigator/` (a biblioteca) | **8 214** linhas em 63 ficheiros, 13 subpacotes |
| `scripts/` (experiências e portas) | 16 531 linhas em 80 ficheiros |
| `tests/` | 7 973 linhas em 55 ficheiros · **746 testes a passar** |
| `api/` + `web/` (o produto no ar) | 580 + 722 linhas |
| Documentos de avaliação regeneráveis | **38** em `docs/evaluation/` |
| Modelos versionados | 3 (`triage_lr`, `triage_context_lr`, `triage_gbm`) + taxonomia |
| Dados locais | 1,7 GB (gitignored); o corpus de treino tem **79 753** linhas |

A proporção que interessa a esta auditoria: **`scripts/` é o dobro de `investigator/`**. Isso não
é desarrumação — é a assinatura de um trabalho onde a experiência pesa mais do que o produto, que
é o que a §2 da directiva pede.

---

## 2. Onde está a inteligência, decisão a decisão

A pergunta da §7 e da §73 não é *"há IA?"* mas *"as decisões centrais são aprendidas, e onde não
são, foi por medição ou por preguiça?"*. O sistema toma **nove** decisões antes de interromper
alguém. Esta é a lista, com o estado de cada uma:

| # | Decisão | Como é tomada | Alternativa aprendida? | Veredicto |
|---|---|---|---|---|
| 1 | Esta notícia é **desta empresa**? | regra: menção + lista de excepções | **nunca testada** — ver §4 | ⚠️ a lacuna real |
| 2 | A notícia é **fresca**? | limite temporal (2 dias) | não se aplica (§72) | determinístico, e bem |
| 3 | O movimento de hoje é **invulgar**? | *z*-score contra a norma de 20 dias da própria empresa | **sim**: Isolation Forest e LOF | aprendidas **perderam** ($F_1$ 0.516 vs 0.271 e 0.280) |
| 4 | Foi a **empresa ou o mercado**? | regressão de dois factores com encolhimento de Vasicek | parcialmente aprendida (betas estimados) | sem verdade humana para comparar, e a tese di-lo |
| 5 | Há um **precedente forte**? | cosseno ≥ 0.45 sobre embeddings SBERT | o chão foi testado: **não é derivável** | controlo de volume, declarado como tal |
| 6 | A notícia **merece um alerta**? | **modelo treinado** (LR + Platt, 79 753 exemplos) | é ela a aprendida | ⚠️ **não bate a volatilidade sozinha** (0.496 vs 0.542) |
| 7 | Qual das candidatas **primeiro**? | ordenação pelo score do modelo, orçamento de 5/dia | idem | a política que a dissertação avalia |
| 8 | Já contei **esta história**? | quase-duplicação por palavras de conteúdo | semântica seria possível | declarado no Cap. 6 como trabalho futuro |
| 9 | O texto do alerta é **fiel**? | verificação determinística contra os motores | não deve ser aprendida (§72) | correcto |

**Duas leituras que um arguente vai querer.** Primeira: a decisão nº 6 é a única genuinamente
aprendida no caminho de produção, e o resultado dela é **negativo** — o que a dissertação reporta
como resultado, não como falha, e sustenta por três caminhos independentes. Segunda: as decisões
nº 3 e nº 5 são determinísticas **por medição**, e é isso que as separa de uma regra escolhida por
conveniência.

---

## 3. Rastreabilidade: problema → método → dados → experiência → resultado → tese

| Problema | Método | Dados | Experiência | Métrica | Resultado | Onde no produto | Capítulo |
|---|---|---|---|---|---|---|---|
| detectar o invulgar | *z*-score rolante | preços diários, 12 empresas | `evaluate_anomaly.py` | amplitude da taxa de disparo, $F_1$ | **0.015 vs 0.344**; $F_1$ 0.516 | marcas no gráfico, alerta de mercado | 3.1 / 5 QI1 |
| separar empresa de mercado | 2 factores + Vasicek | preços + ETF de setor | `evaluate_decomposition.py` | $R^2$, discriminação | mediana **0.460**, 1 negativo | barra de repartição | 3.2 / 5 |
| encontrar casos parecidos | SBERT + cosseno | 79 753 manchetes FNSPID | `evaluate_retrieval_fnspid.py` | precisão@5 | **0.595** vs 0.240 acaso | precedentes no alerta | 3.3 / 5 QI2 |
| … com a restrição da produção | idem, só passado | idem | `evaluate_retrieval_causal.py` **(novo)** | precisão@5 | ver §4 | idem | a integrar |
| decidir o que alerta | LR + Platt | 79 753 exemplos rotulados | `train_triage.py` + 6 famílias | PR-AUC, Brier, prec.@orçamento | **0.538**, perde para 0.542 | ordenação e orçamento | 3.4 / 5 QI3 |
| o modelo é uma tabela? | ablação da identidade | idem | `evaluate_triage_identity.py` | PR-AUC | **0.534** sem ver a notícia | — | 5 |
| o sistema inteiro vale? | linhas de base ponta a ponta | idem | `evaluate_endtoend_baselines.py` | precisão@5/dia | 0.489 · **0.632** · 0.662 · oráculo 0.968 | — | 5 |

Cada linha tem os sete elos que a §66 exige. **A linha nova é a única com um elo em aberto**, e
fecha-se nesta sessão.

---

## 4. Os achados desta auditoria

### A1 — ⚠️ A recuperação foi avaliada podendo ver o futuro, e isso nunca foi dito

O protocolo da QI2 proíbe o candidato de ser da **mesma empresa** e mais nada. Não o proíbe de ser
**posterior** à consulta. `evaluation_relevance_filter.md` já tinha medido a consequência sobre o
corpus recente — **38.7%** dos vizinhos devolvidos são posteriores à consulta e **30.2%** são do
mesmo dia — e esse facto **não aparece em nenhum sítio da dissertação**.

Não é uma fuga no sentido habitual: o rótulo é *"mesmo setor"*, e o setor não muda com o tempo. Mas
a frase da QI2 no Capítulo 1 diz *"encontrar notícias **passadas**"*, e o sistema em produção só
consegue devolver casos passados, porque a base de precedentes só recebe um caso oito dias depois
de o impacto amadurecer. O número reportado descreve, portanto, uma tarefa um pouco mais fácil do
que a que o produto executa.

**Acção tomada:** `scripts/evaluate_retrieval_causal.py` (novo, aditivo) corre o mesmo protocolo
com a máscara acrescentada — o candidato tem de ser **estritamente anterior** — e reproduz o
número simétrico na mesma corrida, para a comparação ser emparelhada. As consultas sem passado
suficiente são contadas e excluídas, e o relatório di-lo, porque um filtro silencioso muda a
população medida. Resultado em `docs/evaluation/evaluation_retrieval_causal.md`.

### A2 — A relevância é a única decisão central que continua uma regra, e não pode ser aprendida honestamente

A decisão nº 1 da tabela do §2 — *esta notícia é desta empresa?* — deita fora **67.3%** das
manchetes, e é a que mais material remove de todo o sistema. É uma regra escrita à mão, e a
directiva (§73) manda perguntar se podia ser aprendida.

Podia, em princípio: é uma classificação binária de texto. **Mas não há rótulos.** O único rótulo
disponível seria a saída da própria regra, o que tornaria a experiência circular, e a §12 e a §63
proíbem fabricar rótulos. A via legítima é anotação humana de uma amostra — que é **exactamente o
mesmo bloqueio** do estudo de utilidade que já está declarado como o único item com relógio.

**Conclusão registada:** é uma limitação de dados, não de método, e passa a estar dita nesses
termos. Duzentos itens anotados desbloqueiam as duas coisas ao mesmo tempo.

### A3 — Dívida técnica declarada: as três aplicações Streamlit retiradas

`app/dashboard.py`, `app/dashboard_v4.py` e `app/streamlit_app.py` já não são servidas (o
`Procfile` serve uvicorn), mas continuam versionadas, com **67 testes** e a arrastar `streamlit` e
`plotly` para o `requirements.txt` que o Heroku instala.

**Decisão: ficam, e a razão é ser reversível.** Não são importadas pelo caminho vivo, logo não
custam memória em produção; custam tamanho de *slug*. As figuras das duas teses longas
documentam-nas. Apagá-las a três semanas da entrega trocaria uma coisa inerte por um risco.
A receita de remoção fica escrita para depois da entrega: tirar os três ficheiros, os quatro de
teste (`test_app_triage`, `test_dashboard_launch`, `test_dashboard_v3`, `test_v4_views`) e as duas
dependências.

### A4 — Dependências externas de IA, classificadas como a §30 exige

| Dependência | Papel | Classe | Podia ser nossa? |
|---|---|---|---|
| SBERT `all-MiniLM-L6-v2` | embeddings de manchete | **essencial**, e é a única | não sem treinar um modelo de linguagem — e não haveria dados |
| ONNX Runtime | correr o mesmo modelo sem `torch` | essencial em produção | é infra-estrutura, não inteligência |
| Groq / Gemini | narrador e relatório | **retirada do produto a 2026-08-20** | a decisão foi não depender |
| yfinance, Finnhub, Alpha Vantage, Polygon | preços e notícias | essenciais, e substituíveis entre si | são fontes, não modelos |

Depois de 20 de agosto, **o caminho que serve o utilizador não chama um único modelo de linguagem
de terceiros**. O que se descarrega é um codificador de frases de 23 MB, com SHA256 fixado, que
corre no próprio contentor.

---

## 5. O que falta para isto ser uma dissertação forte de MEIA

Por ordem de valor, e com a razão pela qual está ou não em execução:

1. **Verdade humana.** Três avaliações assentam em aproximações (percentil, mesmo-setor, limiar de
   retorno) e **nenhuma foi confrontada com um julgamento humano**. Desbloqueia a QI2, a
   relevância (A2) e a metade em aberto do quarto objectivo. Pacote pronto; falta recrutar.
2. **A restrição temporal na recuperação** (A1). Em execução nesta sessão.
3. **Deriva corrigida e não só medida.** Está declarada; corrigi-la exige re-treino, que exige
   dados novos e reabre os congelados. Trabalho futuro, com o custo escrito.
4. **Duplicação semântica ao nível do acontecimento** (§24). Hoje é por palavras de conteúdo.
   Declarado.

O que **não** falta, e vale a pena dizer porque é o que sustenta a defesa: dados próprios com
rótulo anti-lookahead imposto por teste, comparação contra linhas de base em todas as perguntas,
ablação, incerteza por reamostragem de grupos, calibração declarada com o seu enviesamento, e
treze afirmações retiradas ou estreitadas por medição.

---

## 6. O que esta auditoria decidiu NÃO fazer, e porquê

| | Razão |
|---|---|
| Reformular as perguntas de investigação (§4) | As três actuais têm medição, linha de base e resultado — incluindo um negativo. Reformular a 24 dias trocaria resultados por intenções |
| Reestruturar a dissertação (§54) | Seis capítulos, zero erros, auditada afirmação a afirmação |
| Agentes, multi-agente, aprendizagem por reforço (§8) | A própria directiva avisa duas vezes para não os acrescentar por serem actuais. Nenhum problema deste sistema os pede |
| Mais fontes de dados (§39) | Três, escolhidas por medição, com uma rejeitada por medição |
| Converter a relevância em modelo (§73) | Impossível sem rótulos — ver A2. Fabricá-los violaria a §63 |
