# Reprodução do corpus FNSPID — auditoria de 2026-09-09

> **Conclusão em uma linha:** o corpus sobre o qual a tese foi avaliada — **79 753 títulos,
> catorze empresas** — foi **reproduzido exatamente**, ticker a ticker, a partir do ficheiro
> em bruto de 23,2 GB fixado por revisão e por `sha256`. Os números publicados estão certos.
> O que estava errado era uma **reconstrução posterior**, de 2026-09-08, que ficou em disco
> por cima do corpus original.

## 1. A pergunta

A 2026-09-08 uma reconstrução do corpus devolveu **78 481** linhas, quando a tese declara
**79 753**. Havia menos linhas apesar de aparecer mais um ticker (META). Enquanto essa
diferença não fosse explicada, nenhum resultado de recuperação ou de triagem podia ser
considerado assente.

## 2. Método

Duas fragilidades do procedimento antigo foram removidas antes de medir:

| Fragilidade | O que era | O que passou a ser |
|---|---|---|
| Origem móvel | `resolve/main` — ponteiro que segue o ramo | revisão fixa `bf9189c4…79fc45` |
| Paragem antecipada | `early_stop` assumia o ficheiro ordenado por ticker | **varredura completa**, sem suposição |

O ficheiro em bruto foi descarregado uma única vez, de forma resumível
(`scripts/fetch_fnspid_raw.py`), e a sua identidade fixada no código:

```
Stock_news/nasdaq_exteral_data.csv
23 232 979 597 bytes
sha256 1a7a3eb8e6b97ec19f286f2cfca3371542bddb272ab1eb8f36e33ad98fa5c4da
```

A filtragem passou a ser local e auditada (`scripts/build_corpus_canonical.py`), com registo
do número de violações da ordenação por ticker — o facto que a paragem antecipada pressupunha
sem nunca ter verificado.

## 3. Resultado principal: reprodução exata

`data/fnspid_news_canonical.csv` — `sha256 af61708c…d0197b` — contra a tabela congelada em
`docs/evaluation/kb_fnspid_build.md` (build de 2026-07-05):

| Ticker | Canónico | Tese | | Ticker | Canónico | Tese |
|---|---:|---:|---|---|---:|---:|
| TSLA | 10 587 | 10 587 | | AMZN | 5 060 | 5 060 |
| NVDA | 10 059 | 10 059 | | JPM | 2 883 | 2 883 |
| AAPL | 9 338 | 9 338 | | GOOGL | 1 754 | 1 754 |
| MSFT | 8 737 | 8 737 | | JNJ | 977 | 977 |
| WMT | 8 686 | 8 686 | | PFE | 932 | 932 |
| CVX | 7 416 | 7 416 | | BAC | 742 | 742 |
| XOM | 7 346 | 7 346 | | **Total** | **79 753** | **79 753** |
| KO | 5 236 | 5 236 | | | | |

Catorze de catorze. Intervalo `2018-01-01 … 2023-12-16`, igual ao declarado.

Uma segunda verificação, independente da primeira, fecha o mesmo número pelo lado da triagem.
`docs/evaluation/evaluation_triage.md` regista os blocos 28 574 / 17 710 / 32 649, e a tese
afirma que «o embargo descarta 820 das 79 753»:

```
28 574 + 17 710 + 32 649 + 820  =  79 753
```

A soma fecha ao registo. O conjunto de treino da triagem e o corpus canónico são o mesmo.

## 4. De onde vinham as 78 481 linhas

Os três artefactos em disco reconciliam-se sem resto:

```
corpus canónico (varredura completa, catorze tickers)          79 753
  menos duplicados exactos (ticker, data, título)              − 1 704
  = títulos únicos                                              78 049
  mais linhas de META recuperadas do símbolo antigo FB          +   432
  = reconstrução de 2026-09-08                                   78 481
```

E a verificação decisiva, ao nível dos conjuntos e não das contagens: o conjunto de trios
únicos `(ticker, data, título)` do canónico e o da reconstrução, retirada a META, são
**idênticos** — diferença simétrica **zero**, nos dois sentidos, sobre 78 049 elementos.

A reconstrução de 2026-09-08 não descobriu nem perdeu conteúdo: aplicou, sem o declarar,
uma **desduplicação** e um **mapeamento FB→META** que o corpus da tese não tem. Ficou
arquivada em `data/_arquivo/fnspid_news_subset_divergente_2026-09-08.csv`
(`sha256 cb3a1620…07378`) e o corpus de trabalho foi reposto a partir do canónico.

## 5. O que o ficheiro em bruto contém, de facto

Varredura binária dos 23,2 GB (`scripts/_diag_raw.py`, 3,3 minutos, bytes lidos = tamanho
do ficheiro):

| Observação | Valor |
|---|---|
| Colunas | `Unnamed: 0, Date, Article_title, Stock_symbol, Url, Publisher, Author, Article, Lsa_summary, Luhn_summary, Textrank_summary, Lexrank_summary` |
| Primeiro registo | índice `0.0`, `2023-12-16 23:00:00 UTC`, símbolo `A` |
| Ordenação | por ticker ascendente, por data **descendente** dentro de cada ticker |
| Mudanças de linha | 94 624 412 — **não** é o número de registos: o campo `Article` contém mudanças de linha |
| Registos lidos pelo analisador | 15 549 299, em 78 blocos |
| Violações da ordenação por ticker | **18** (a primeira no bloco 12: mínimo `A` contra máximo já visto `WSO-B`) |

As dezoito violações liquidam a suposição em que assentava a paragem antecipada: o ficheiro
é uma **concatenação de blocos ordenados**, não uma sequência ordenada. Uma varredura que
parasse ao passar `XOM` perderia tudo o que vem depois do primeiro bloco. **A paragem
antecipada fica proibida** — e agora com prova, não com receio.

## 6. Meta: o símbolo não existe no conjunto

Contagem de padrões sobre os 23,2 GB:

| Padrão | Ocorrências |
|---|---:|
| `,META,` | **8** |
| `"META"` | 0 |
| `,FB,` | 507 |
| `"FB"` | 11 |
| `,AAPL,` | 9 616 |
| `,XOM,` | 7 722 |

O FNSPID **não indexa a Meta**. As oito ocorrências de `,META,` num ficheiro de 23 GB são
compatíveis com texto de artigo, não com um campo de símbolo. A empresa aparece apenas sob
o símbolo antigo `FB`, com 507 ocorrências em todo o ficheiro, das quais **432 títulos
únicos** caem na janela 2018–2023 — e todos entre **2020-02-19 e 2020-06-10**, quatro meses
de seis anos.

É por isto que o corpus tem **catorze** empresas e a avaliação da deteção tem **quinze**.
A Tabela 3.1 da tese já distingue as duas linhas corretamente; o que falta é dizer **porquê**.
Ver a Secção 8.

## 7. A extração antiga (`.gz`) duplicava linhas

`data/fnspid_artigos_15tickers.csv.gz` tem 93 093 linhas, das quais **12 927 são repetições
byte a byte da linha inteira** — mesma data, mesmo título, mesmo `Url`, mesmo `Publisher`,
mesmo corpo. Das 14 469 chaves `(ticker, data, título)` repetidas, apenas 1 630 têm mais do
que um `Url` distinto.

Que a duplicação foi **introduzida pela extração**, e não herdada da origem, prova-se por
aritmética. O ficheiro em bruto contém no máximo 9 616 ocorrências de `,AAPL,` em **todos**
os anos; o `.gz` declara 9 811 linhas de AAPL só em **2018–2023**. Um ficheiro não pode
render mais linhas de um símbolo do que as vezes que esse símbolo lá aparece.

A causa provável é a retoma da descarga em fluxo, que reprocessava um bloco já lido — o
mesmo modo de falha que produziu o `IncompleteRead` observado a 2026-09-09. **Isto é uma
hipótese, não um facto medido:** o que está provado é que as linhas a mais não acrescentam
um único título novo.

Verificada ainda a última divergência entre os dois artefactos: 140 trios `(ticker, data,
título)` apareciam num e não no outro. São **140 de 140 o mesmo título com um espaço final**
— `'…Buy and Hold Forever '` contra `'…Buy and Hold Forever'`. O `normalize_columns` apara o
espaço, a leitura em bruto não. Descontado isso, a concordância entre a extração antiga e a
varredura canónica é **total**: nem um único título difere.

## 8. O que isto obriga a mudar na tese

Nenhum número publicado muda. O que falta é **declarar** o que sustenta esses números.

| # | Onde | O que acrescentar | Prioridade |
|---|---|---|---|
| 1 | §3.2 | A revisão fixa e o `sha256` do ficheiro de origem, para que um terceiro reconstrua o corpus. Hoje a secção nomeia o FNSPID mas não a versão — e o `resolve/main` é um ponteiro móvel. | CRÍTICO |
| 2 | §3.2 | **Porque são catorze empresas e não quinze.** O FNSPID não indexa a Meta; a empresa só existe sob o símbolo antigo `FB`, com quatro meses de cobertura em seis anos. Uma frase resolve o que hoje é uma discrepância aparente entre as duas linhas da Tabela 3.1. | CRÍTICO |
| 3 | §3.2 | **A política de duplicados.** O corpus conserva 1 704 títulos exactamente repetidos (2,1%), tal como o FNSPID os entrega. Isso é uma decisão e está por declarar. | CRÍTICO |
| 4 | Tabela 3.1 | A legenda diz «lidos dos ficheiros», mas `2018-01-02 … 2023-12-18` são **dias de negociação após o alinhamento**; as notícias vão de `2018-01-01` a `2023-12-16` (um feriado e um sábado, remetidos para a sessão seguinte). A legenda deve dizê-lo. | IMPORTANTE |
| 5 | §5.4 | Uma verificação de sensibilidade à desduplicação: repetir a medição sobre os 78 049 títulos únicos e reportar a diferença. Se for pequena, a decisão de conservar deixa de precisar de defesa. | IMPORTANTE |
| 6 | §3.2 | Que a paragem antecipada foi **abandonada**, e porquê: dezoito violações da ordenação medidas sobre o ficheiro. É um pormenor de procedimento com consequência real. | MELHORIA |

## 9. Regras que passam a valer

1. **A origem fixa-se por revisão, nunca por `main`.** Um ponteiro móvel não é uma fonte.
2. **Sem paragem antecipada.** Está medido que o ficheiro não é uma sequência ordenada.
3. **O ambiente da tese é o `.venv` (Python 3.12.10)**, com `sentence-transformers 5.6.0`,
   `torch 2.12.1+cpu`, `pandas 2.2.3`. O Python global (3.13.13) **não tem
   `sentence-transformers`** e traz `pandas 3.0.2`. Qualquer coisa que toque no pipeline
   corre pelo `.venv`.
4. **Nunca escrever por cima de um ficheiro congelado citado pela tese.** Avaliações vão
   para caminhos descartáveis; `docs/evaluation/*.md` só muda por decisão explícita.
5. **Os preços não estão congelados.** O `load_prices` vai ao yfinance, que reajusta o
   histórico a cada dividendo. Ver a Secção 10.

## 10. Os preços (ponto fechado na Secção 13)

O corpus está fixado; os **preços não**. O `scripts/build_kb.py` obtém as séries por
yfinance no momento do build, e os fechos ajustados são reescritos retroativamente sempre
que há dividendo ou desdobramento. Duas consequências:

- os impactos (+1d/+3d/+5d) guardados na base podem afastar-se dos de 2026-07-05;
- os rótulos da triagem dependem desses mesmos retornos.

A amostra versionada `data/samples/kb_fnspid_sample.jsonl` (50 registos do build original)
permite **medir** o desvio em vez de o supor. É a verificação seguinte, e a decisão que dela
decorre — congelar a cache de preços e registar um manifesto — fica por tomar.

## 11. A cadeia verificada de ponta a ponta

Depois de reposto o corpus, tudo o que dele depende foi refeito e comparado com o congelado.

| Elo | Verificação | Resultado |
|---|---|---|
| Ficheiro em bruto | revisão fixa + `sha256` + tamanho | fixado, e o procedimento recusa outro |
| Corpus | varredura completa contra `kb_fnspid_build.md` | **79 753**, catorze de catorze tickers |
| Corpus (2.ª via) | blocos da triagem + embargo | 28 574+17 710+32 649+820 = **79 753** |
| KB — impactos | 50 registos congelados de `kb_fnspid_sample.jsonl` | `\|delta\|` máximo **2,3e-07** |
| KB — embeddings | os mesmos 50 registos | cosseno **1,000000000** |
| Resultado QI2 | reexecução do protocolo publicado | **P@5 0,595 ± 0,024**, acaso **0,333** |

Os dois valores da última linha são **exactamente** os que a tese publica. A cadeia
`bruto → corpus → base de conhecimento → resultado` está fechada, e cada elo tem uma verificação
que falha sozinha se algo mudar.

Isto confirma também, pela negativa, o que ficou registado a 2026-09-08: o `0,604` obtido nessa
altura **não** era variação de semente. Era outro corpus.

## 12. O que a reposição destapou: o BM25

Com a base correta, ficou possível correr a comparação que faltava — a recuperação semântica contra
um *baseline* lexical clássico, no mesmo protocolo, sobre as mesmas consultas.

| | P@5 | Margem sobre o acaso |
|---|---:|---:|
| SBERT (`all-MiniLM-L6-v2`) | 0,5946 ± 0,0240 | +0,2613 |
| BM25 (k1=1,5, b=0,75) | 0,5214 ± 0,0159 | +0,1881 |
| Acaso | 0,3333 | — |
| Recência | 0,0900 | — |

Diferença emparelhada SBERT − BM25: **+0,0733 ± 0,0112**, positiva nas cinco repetições. Zero
colocações com pontuação nula no BM25 — o *baseline* nunca teve de adivinhar.

**A leitura honesta é desconfortável e tem de constar da §5.3:** o BM25 sozinho capta **72%** da
margem que a tese atribui à representação semântica. O ganho do SBERT é real, consistente e
mensurável, mas é o menor dos dois efeitos. Sem esta comparação, a §5.3 deixava em aberto a
pergunta mais óbvia que um júri faz a um resultado de recuperação — e a resposta favorece menos a
tese do que o silêncio deixava supor.

## 13. Os preços, fixados — e um defeito que só um teste exigente apanhou

O buraco era maior do que o reajuste dos dividendos. O `load_close_series` **não tinha cache
nenhuma**: cada construção ia à rede. E por baixo tinha uma cadeia de cinco fontes — yfinance,
Tiingo, Polygon, Stooq, Alpha Vantage. Se o yfinance falhasse num ticker, **outra servia, sem
que isso aparecesse no resultado**. A mesma janela podia vir de fontes diferentes em execuções
diferentes, e nada o denunciava.

O que se fez, por TDD:

- `investigator/market_data/price_cache.py` — cada série num CSV por `(ticker, janela)`, com
  fonte, dimensão, extremos e `sha256` num manifesto ao lado;
- `load_close_series` ganhou `cache_dir` e `refrescar`, **opcionais**: a camada viva tem de
  continuar a ir à rede, e o comportamento sem eles fica exactamente como estava;
- o `build_kb.py` usa a cache por omissão e publica `docs/design/precos_manifest.json`;
- `tests/test_precos_manifesto.py` vigia o registo — incluindo um teste que **falha se alguma
  série passar a vir de outra fonte**.

### O defeito

A primeira versão da cache **perdia dígitos**, e nenhum dos testes o via: o
`assert_series_equal` compara com tolerância relativa de `1e-5` por omissão. Com
`check_exact=True` e um caso escolhido à mão — `0,1 + 0,2`, que em dupla precisão vale
`0,30000000000000004` — o `pandas` mostrou-se lossy **dos dois lados**: escrevia `0.3`, e mesmo
depois de escrito com dezassete dígitos o leitor rápido devolvia `0.3`. Resolvido com
`float_format="%.17g"` na escrita e `float_precision="round_trip"` na leitura.

Uma cache que perde dígitos não fixa coisa nenhuma. O teste frouxo teria deixado passar
exactamente aquilo que a cache existe para impedir — e é por isso que o caso está escrito com
o valor à mão, e não com uma tolerância.

## 14. O que fica por resolver: o corpus da avaliação preliminar

`data/finnhub_news.csv` — as 3 714 manchetes sobre as quais assenta a §5.3.2, isto é, a
Figura 5.6 e o resultado de recuperação que a tese apresenta **em primeiro lugar** — não está
no disco, não está no histórico do git (`data/**` é ignorado) e não está no `archive/`.
Sobrevivem apenas amostras: 30 linhas e 50 registos.

A consequência é directa: **a Figura 5.6 não é reproduzível**, e `evaluation_results.md`, que a
gerou, abre com «Resultados da avaliação (reprodutível)» — uma afirmação que hoje não se
sustenta para este braço. A réplica à escala da §5.3.4, essa, é reproduzível de ponta a ponta,
e ficou provada nesta sessão.

**Não se escreve nada disto na tese enquanto não estiver esclarecido.** O
`docs/evaluation/evaluation_triage.md` aponta para `C:\\Users\\henri\\Desktop\\DIMEIA\\…` — outro
perfil de utilizador. O corpus pode estar nessa máquina ou numa cópia de segurança, e afirmar
que não foi conservado seria afirmar o que não está verificado.

## 15. A QI3 também reproduz — e o resíduo diz porquê

`data/triage_dataset.csv` **também não estava em disco**. A diferença face ao corpus do Finnhub
é decisiva: este deriva do corpus (fixado por `sha256`) e dos preços (fixados por manifesto),
logo reconstrói-se.

Reconstruído, bate ao número:

| | Reconstruído | `evaluation_triage.md` |
|---|---:|---:|
| Linhas | 79 753 | — |
| Embargo | 820 | 820 (§5.4) |
| Treino | 28 574 (38,5% pos.) | 28 574 (38.5%) |
| Validação | 17 710 (47,0% pos.) | 17 710 (47.0%) |
| Teste | 32 649 (37,8% pos.) | 32 649 (37.8%) |

O `0,378` é o mesmo que a §5.4.1 cita como prevalência do bloco de teste. Descartes por falta
de preços, de histórico ou de futuro: **todos a zero**.

### Os modelos, ao décimo dígito

O treino guarda um `.json` com as métricas completas, e o `git diff` contra o ficheiro de
2026-07-04 dá a comparação exacta — não arredondada a três casas:

| Métrica | Tese (04-07, máquina `henri`) | Hoje | Diferença |
|---|---:|---:|---:|
| `full` PR-AUC | 0,49614796 | 0,49617471 | +2,7e-05 |
| `full` ROC-AUC | 0,62212465 | 0,62215450 | +3,0e-05 |
| `full` Brier | 0,22879886 | 0,22879383 | −5,0e-06 |
| `full` P@orçamento | 0,58461538 | 0,58461538 | **igual** |
| `gbm` PR-AUC | 0,46948321 | 0,47007921 | +6,0e-04 |
| `gbm` ROC-AUC | 0,62356308 | 0,62378419 | +2,2e-04 |
| `gbm` Brier | 0,22760866 | 0,22734860 | −2,6e-04 |
| `gbm` P@orçamento | 0,55113122 | 0,56018100 | +9,0e-03 |

Os três *baselines* reproduzem-se ao terceiro decimal que a tese publica: volatilidade
**0,542**, contexto **0,538**, texto **0,439**.

### O resíduo tem explicação, e não é ruído

As linhas, os blocos e as contagens de positivos são **idênticos**, a semente é a mesma e o
embedder é o mesmo. O que muda são os **valores contínuos**: as características de contexto
derivam dos preços, e os preços de setembro não são bit a bit os de julho. Nenhum rótulo virou
— a contagem de positivos não mexeu —, mas as features deslocaram-se na sétima casa.

O modelo linear desloca-se `1e-05`; o de árvores desloca-se **vinte vezes mais**, porque um
corte é descontínuo e uma perturbação minúscula chega para o mudar de sítio. É por isso que o
`gbm` lê `0,470` onde a tese diz `0,469`, e o `full` lê `0,496` nas duas.

**A conclusão da §5.4 não mexe:** `full` (0,496) e `gbm` (0,470) continuam abaixo da linha de
volatilidade (0,542), que é a comparação decisiva.

E o resíduo é precisamente o argumento para a cache de preços da Secção 13: a partir de agora
esta deriva desaparece, porque os preços deixaram de vir da rede a cada execução.

### Duas armadilhas fechadas pelo caminho

O `train_triage.py` escrevia **sempre** por cima de três coisas que uma verificação não pode
tocar: o `evaluation_triage.md` congelado, duas figuras da tese, e os **modelos que a
aplicação usa**. Os modelos chegaram a ser substituídos nesta execução e foram repostos por
`git checkout`. O script ganhou `--out`, `--figuras-dir` e `--modelos-dir`; por omissão o
comportamento é o de sempre.
