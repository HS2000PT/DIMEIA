# Contrato de dados do retreino — auditoria do registo de decisões

Data: 2026-09-03. Executa o passo 1 de [`RETREINO_CONTROLADO.md`](RETREINO_CONTROLADO.md):
inventariar o que existe antes de construir treino nenhum.

**O que esta passagem é.** Inspeção de código e configuração, mais um script de auditoria novo
que ainda não correu contra o registo real. **O que não é.** Não houve treino, escrita em
`models/`, deploy, descarregamento de dados nem alteração de números da tese. Não corri a suite
de testes: não tenho o venv do projeto, e a leitura abaixo é do código e dos nomes dos testes.

## 1. O que já está implementado — e está mais adiantado do que o plano diz

O contrato de *snapshot* por decisão está ligado de ponta a ponta. Evidência:

| Peça | Onde | O que faz |
|---|---|---|
| Campos opcionais no registo | `investigator/triage/postval.py:26–47` | `log_decision` aceita `feature_snapshot` e `model_info`; ausentes, escreve exatamente o registo antigo. |
| Vetor exato da inferência | `investigator/triage/infer.py:91–116` | `score_context_with_snapshot` devolve o esquema, o `as_of` e o valor de cada uma das nove entradas. |
| Identidade do modelo | `investigator/triage/infer.py:46–52` | `_model_info` com artefacto, sha256, data de treino, família e `feature_schema`. |
| Propagação no runner | `scripts/run_alerts.py:447–459` e `895–917` | `_log_decision_safe` recebe e escreve os dois; falha do registo nunca trava o envio. |
| Testes | `tests/test_postval.py`, `tests/test_triage_infer.py` | Ida e volta, compatibilidade com registos antigos, propagação pelo runner, falha silenciosa do registo, *fail-open* sem histórico e com preços em falta. |

O que falta do passo 1 não é código: é **caracterizar os dados**. É isso que as quatro
restrições abaixo fazem, e cada uma delas decide uma linha do protocolo de aceitação.

## 2. Quatro restrições que a inspeção encontrou

### R1 — A população registada não é a população das notícias

O registo só recebe uma linha **depois** de a manchete atravessar o filtro de relevância, o
filtro de frescura e o chão de precedente (`run_alerts.py:855–899`; cada um faz `continue` antes
de chegar ao registo). E o varrimento pontua **uma manchete por empresa por ciclo** — a mais
recente relevante (`run_alerts.py:864`, `latest = max(relevantes, key=...date)`).

O conjunto de retreino é, portanto, um sobrevivente filtrado, e não uma amostra das notícias.
É a mesma causa que a dissertação já dá para o modelo não ajudar em produção: quando é
invocado, os filtros elementares já removeram grande parte do que ele foi treinado para remover.
**Um candidato treinado neste registo herda esse enviesamento.**

Duas saídas, e é uma decisão, não um detalhe:

- **(a)** registar a decisão **antes** das portas, com a etapa onde cada candidata morreu. Dá a
  população real e muito mais linhas; obriga a mexer no caminho de envio.
- **(b)** manter como está e **estreitar a afirmação**: o modelo ordena candidatas que já
  passaram as portas, e é só isso que qualquer resultado sustentará.

### R2 — `kept` deixou de discriminar

`run_alerts.py:913–916`: `kept = so_ordena or gated is not None`, com
`so_ordena = orcamento is not None`. E `config/alerts.yaml:63` tem `daily_budget: 5`.
Logo **todas as linhas novas têm `kept=True`**.

A consequência é concreta e não se resolve com mais dados: a comparação entre decisões mantidas
e suprimidas que a dissertação reporta — `0,589` contra `0,617`, sobre 825 decisões maturadas —
**não é recalculável sobre a janela nova**, porque já não há linhas suprimidas. O número
publicado continua válido para a janela em que foi medido; deixa de ser reproduzível para a
frente.

O rótulo continua a vir dos preços, portanto o retreino em si é possível. O que deixa de ser
possível é medir a qualidade da porta por esse contraste. **O protocolo de aceitação não pode
assentar nele.**

### R3 — Só as linhas novas são reproduzíveis

Nenhuma linha anterior a hoje tem `feature_snapshot`. Recalcular agora as entradas de um dia
passado usaria uma série de preços que já contém o que veio a seguir — é exatamente a
reconstrução com futuro que o plano proíbe.

Daqui sai a classificação, e ela é dura:

| Linhas | Estado | Para que servem |
|---|---|---|
| Sem `feature_snapshot` (todo o histórico) | B — histórico rastreável | Caracterizar a operação, contar decisões, descrever o funil. |
| Com `feature_snapshot` (a partir de hoje) | A — confirmado | Treino e avaliação. |

**O relógio do retreino começou hoje.** Antes de fixar mínimos de dias e de classes, é preciso
saber quantos títulos distintos por dia entram no registo — e isso mede-se, não se estima.

### R4 — Duplicação por reavaliação

A mesma manchete é repontuada a cada ciclo de sessenta segundos.
`evaluation_gate_selectivity_unicos.md` mede o pior caso em **181 decisões por título** (JNJ),
e é justamente nas empresas com menos notícias que a duplicação é maior — ou seja, a duplicação
não é uniforme e desloca qualquer média ponderada.

O remédio existe: `dedup_decisions` (`postval.py:64–74`) mantém a primeira ocorrência de cada
`(news_date, ticker, headline)`, e `post_validate.py:82` já o usa. **Qualquer treino ou avaliação
nova tem de passar por lá**, senão o peso de cada empresa passa a ser a frequência com que o
sistema a republica, e não a frequência com que ela aparece nas notícias.

## 3. Ferramenta nova para fechar o passo 1

`scripts/auditar_registo_decisoes.py` → `docs/evaluation/registo_decisoes_auditoria.md`.

Lê o registo (por defeito `origin/alerts-history:predictions_log.jsonl`, ou `--ficheiro`) e
conta: linhas contra títulos distintos, decisões por título e por empresa, títulos distintos por
dia, fração com `prob`/`feature_snapshot`/`model_info`, distribuição de `kept`, e a relação entre
`as_of` e a data da notícia. Não treina, não escreve em `models/` e não toca em números da tese.

⚠️ **Ainda não correu contra o registo real.** Foi verificado sobre um registo sintético com as
duas eras (linhas antigas sem *snapshot* e `kept` variável; linhas novas com *snapshot* e `kept`
constante) e produz o relatório corretamente; `ruff` limpo. Os números só valem depois de
`git fetch` e uma execução no venv do projeto.

## 4. Ordem proposta para o resto

1. **Correr a auditoria** contra a branch de dados. Dá os números reais de R2, R3 e R4, e o
   tamanho do bloco de comparação.
2. **Decidir R1** — registar antes das portas, ou estreitar a afirmação. Tudo o resto depende
   desta escolha, incluindo o que o resultado poderá afirmar.
3. **Fixar mínimos e critérios de aceitação** a partir dos números do ponto 1, e **antes** de
   ver qualquer candidato. Sem o contraste mantidas/suprimidas (R2): PR-AUC, Brier e ordenação
   sobre um bloco temporal, contra o modelo atual e contra a linha de base de volatilidade.
4. **Passo 2 do plano — candidato isolado — continua por implementar.** `scripts/train_triage.py`
   escreve em caminhos fixos de `models/` e regenera relatórios e figuras; **não pode ser corrido
   como retreino operacional**. Falta a saída por execução com manifesto (hashes, esquema,
   parâmetros, versões, datas, semente) e sem escrita no modelo ativo.

## 5. O que continua por verificar, e não sai do repositório

- Se a publicação do registo na branch de dados está mesmo a acontecer no processo em produção
  (`run_alerts.py:1708–1709` publica; `1618–1619` semeia no arranque). O código está lá; a
  confirmação exige ver o sistema no ar.
- Quantas linhas o registo tem hoje, e desde quando. Depende do ponto 1.
- Se a suite de testes passa nesta árvore. Não a corri.

---

## 6. Fecho do passo 1 — 2026-09-04

A auditoria correu contra o registo real, e o número que ela devolveu contradiz este documento.

### O que a auditoria mediu

| | |
|---|---|
| Linhas | 39 595 |
| Títulos distintos | 257 |
| Período | 2026-08-27 a 2026-09-03 |
| Mediana de decisões por título | 78 (máximo 1406) |
| Mediana de títulos distintos por dia | 28 |
| `feature_snapshot` presente | **0,0%** |
| `kept` verdadeiro | **100,0%** |

**A secção 1 deste documento estava errada, e é a correção mais importante da passagem.**
Dizia que o contrato de *snapshot* estava «ligado de ponta a ponta» e que «o relógio do
retreino começou hoje». Não tinha começado: o código existia apenas na árvore de trabalho,
nunca foi commitado nem implantado. Zero linhas de classe A tinham sido recolhidas.

R2 e R4 ficam confirmados por medição, e não por inspeção: `kept` é constante, portanto o
contraste mantidas/suprimidas não é recalculável nesta janela; e a duplicação por reavaliação
é real e não uniforme.

### Decisão R1 do autor: registar antes das portas

Escolhida a saída **(a)**. O registo passa a receber toda a manchete relevante, com `stage` a
dizer onde cada candidata morreu. A razão é a que o próprio contrato deu: o conjunto anterior
era um sobrevivente filtrado, e é essa filtragem que a dissertação já dá como causa de o
modelo não ajudar em produção.

`stage` substitui `kept` como variável discriminante, porque `kept` deixou de discriminar.

Uma linha por `(news_date, ticker, headline)`. Resolve R4 no ponto de escrita em vez de a
jusante, e tira do ficheiro a duplicação que fazia o peso de cada empresa ser a frequência
com que o sistema a republica.

### Verificado num ciclo real

691 candidatas registadas, todas com *snapshot*: 408 `not_latest`, 283 `stale`. Contra a
mediana de 28 títulos por dia do esquema anterior.

E o registo passou a mostrar sozinho o que exigia um script à parte: três manchetes AAPL do
mesmo dia pontuam `0,38588`, `0,38595` e `0,38602`. A única entrada que difere entre elas é o
comprimento do título. É o item 15 da matriz dos anexos, agora observável na saída de
produção.

### ⚠️ O que falta, e é um passo humano

O **worker do Heroku continua a correr o código antigo**. Não há implantação automática, e
esta máquina não tem a CLI do Heroku nem o respetivo token. Até o worker ser implantado, a
recolha de classe A vem só do cron do GitHub Actions, que corre `run_alerts.py` a partir do
`main` de 30 em 30 minutos em horário de mercado — muito menos denso do que o ciclo de 60 s.

Comando, numa máquina com a CLI: `heroku login` e depois
`python scripts/deploy_heroku.py`.

### O que continua por fixar

Os mínimos e os critérios de aceitação, que dependem da data da defesa. O horizonte primário
do rótulo é de **3 dias de bolsa** (`build_dataset.py`, `--primary-horizon 3`), ou seja cerca
de cinco de calendário: dados recolhidos a menos de cinco dias da defesa não maturam a tempo.
