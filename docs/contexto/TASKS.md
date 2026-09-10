# TASKS — Programa de fecho da dissertação

> **Estado:** [ ] pendente · [/] em curso · [x] concluída · [~] descartada (com razão)
>
> **Prioridade nº 1 em todas as sessões** até estar tudo fechado.
> Plano completo e racional: doc de projeto `claude/PLANO-MESTRE.md`.
> Diagnóstico da Fase 1: artefacto publicado a 08/09/2026.
>
> **Mandato (Henrique, 08/09/2026):** execução autónoma. Não há prazo — o critério é
> «explorado ao máximo», não «entregue a tempo». O autor revê no fim.
> **Critério de aceitação do trabalho novo:** contribuição genuinamente pioneira,
> estabelecida com evidência de literatura, não afirmada.

## Invariantes — nunca violar

- [x] **Explicar sem prever.** Nenhum componente novo pode produzir, direta ou indiretamente,
      uma expectativa sobre a direção futura do preço. Treino sobre `|impacto|`, nunca sobre o sinal.
- [x] **Sem lookahead.** Todo o pipeline novo leva teste de mutação do futuro (cf. Excerto 3.2).
- [x] **Determinismo.** Sementes fixas; as do arnês existente são 42–46.
- [x] **Arnês inalterado.** Qualquer codificador novo é medido em `investigator/evaluation/retrieval_eval.py`
      com o mesmo protocolo, mesmas linhas de base, mesmas sementes. Não se altera a métrica para acomodar um método.
- [x] **Nada inventado.** Dúvida assinala-se; não se preenche.
- [x] **Paridade bilingue — a versão EN entrega-se em sincronia, não no fim.** Decisão do autor
      a 2026-09-09: as dissertações de referência que consultou estão todas em inglês, pelo que a
      `tese-eng/` tem de estar **pronta ao mesmo tempo** que a `tese-pt/`, e não tratada como
      tradução posterior. Consequência prática: **nenhuma fase fecha com a PT alterada e a EN por
      alterar.** Toda a tarefa das fases D a H tem duas metades, e `check_bilingual_parity.py`
      verde é condição de fecho, não verificação final.
- [x] **Suite de verificação verde** antes de fechar qualquer fase (`scripts/verify.sh`, `check_*.py`).

---

## FASE A — Novidade e posicionamento

> Estabelecer com evidência o que é novo, antes de construir. Se houver trabalho anterior,
> a contribuição afina-se; não se ignora.

> Resultados em `claude/fase-A-novidade.md` (doc de projeto).
> Workspace Undermind: 13174fd4-21ce-45f3-953a-0dfebb977e9c

- [x] A1 · Pesquisa: fine-tuning contrastivo de codificadores para notícias financeiras
- [x] A2 · Pesquisa: recuperação consciente do desfecho — **lacuna confirmada** pela pesquisa profunda
- [x] A4 · Pesquisa: alertas explicáveis para retalho — **79 trabalhos; revelou literatura em falta**
- [x] A5 · Adaptação de domínio: FinBERT2 (KDD 2025) já o fez → braço passa a controlo
- [x] A6 · Nota de posicionamento redigida
- [x] A8 · **Decisão: a QI4 mantém-se, com o desenho corrigido** — treinar sobre `|impacto|`,
      ajustar o codificador (não uma cabeça congelada), e acrescentar a variante com sinal
      como linha de base, replicando [Jeong26] no arnês desta tese
- [/] A3 · Raciocínio baseado em casos em finanças — encontrados [Oh07], [But91]; falta ler
- [ ] A9 · Ler o sumário da pesquisa profunda 2 quando concluir
- [ ] A10 · Ler em texto integral: [Lee26d], [Du24], [Nee25], [Cha22c], [Ber23], [Waa21]
- [ ] A11 · Confirmar se existe recuperação treinada por magnitude comparável em **qualquer** domínio

### A12 — Literatura em falta no Capítulo 2 (achado novo, não previsto no diagnóstico)

> A §2.2 estabelece a lacuna inspecionando **produtos comerciais** e nunca a literatura académica
> sobre esta classe de sistema, que existe desde 2004. É exposição real perante um júri de SI.

> **2026-09-09.** Os quatro PDFs que faltavam foram lidos em texto integral. O que cada um diz,
> e o que mudou na tese por causa disso, está em `docs/design/capitulo2_literatura_2026-09-09.md`.
> Oito entradas novas na bibliografia, todas verificadas; uma correção encontrada de caminho
> (`robertson2009bm25`); uma correção no próprio verificador, com testes.

- [x] A12.1 · [Mun09] em §2.2 — a lacuna passa a ser de **postura epistémica** (prever vs. explicar)
      e não de ausência de sistemas. O MoFiN DSS é DSR, é para o mesmo público, e já usava
      **magnitude** e não direção como definição de acontecimento relevante. §2.9 ressalvada.
      *(Os outros cinco Muntermann não foram lidos; [Mun09] é o mais desenvolvido e chega.)*
- [x] A12.2 · [Oh07] em §2.6 — CBR em finanças classifica o **mercado inteiro** e nunca mostra os
      casos. Serve de contraste. *([But91] não foi obtido; não é necessário.)*
- [x] A12.3 · [Liu23d] em §2.1 — três parágrafos no corpo, não em nota: alertas de limiar pioraram
      o desempenho de investidores particulares em ~1 p.p. em seis meses. A resposta da tese é
      limitada e declarada como tal. §2.6 deixou de transpor a fadiga de alertas do domínio
      clínico por analogia. *([Ell20], [Arn19b] não obtidos; [Liu23d] sozinho sustenta o ponto.)*
- [x] A12.4 · [Waa21], [Cau23b], [Ber23] em §2.7 — cinco parágrafos de contraevidência e resposta.
      **⚠️ ERRO MEU CORRIGIDO:** eu tinha escrito que [Waa21] «justifica empiricamente a opção por
      explicação baseada em casos». É o contrário: as explicações por exemplos **não se
      distinguiram de não dar explicação nenhuma** (p = 0,796 e p = 0,283), e o domínio é diabetes,
      não finanças. A resposta da tese usa o diagnóstico dos próprios autores.
- [ ] A12.4b · Descarregar os PDFs de [Cau23b] e [Ber23] (ISEP) — hoje só se cita o que consta dos
      resumos do editor. Sem os PDFs não se citam participantes nem valores. **Tarefa do Henrique.**
- [ ] A12.5 · **→ consolidado em Z3.** [Nee25] SPA, [Cha22c] DeepTrust, [Fer19] Squawk Bot em §2.2
- [ ] A12.6 · **→ consolidado em Z3.** [Fen21b] SIGIR em §6.5
- [ ] A12.7 · **→ consolidado em Z3.** [Cor21] em §3.6/§5.4
- [x] A12.8 · Tabela 2.3 reconstruída (linha «Por que razão acreditar?» passa a declarar que as
      medições com pessoas não confirmam o ganho) e afirmação de lacuna da §2.9 reavaliada
- [x] A12.11 · [Du24] em §2.4 — o vizinho revisto por pares mais próximo. A **ablação dele** mostra
      que aprendizagem contrastiva só sobre texto **degrada** a exatidão. Terceira indicação
      independente de que a direção é o sinal errado
- [x] A12.12 · **FEITO**: `du2024contrastive` está citado no corpo. Ficava: fechar a ligação à QI4 em §2.2 e §2.4, onde o texto descrevia [Du24] e [Mun09]
      sem dizer que esta tese ajusta o codificador e treina sobre magnitude, porque o Capítulo 1
      ainda declara três questões. Meia frase em cada sítio, depois de C7/C8

## FASE B — Fechar as lacunas que a própria tese nomeia

> ⚠️ **B3 a B6 continuam ABERTAS, e a tese declara-o em voz alta.** Ao verificá-las, ler o
> parágrafo e não fazer `grep`: o B5 acerta em «assimetria de referencial» porque a frase que
> **propõe** eliminá-la usa o termo, e o B4 acerta em «sensibilidades encolhidas» dentro de
> «*A experiência que resolveria a questão… Não foi*». Dei os dois por feitos a 2026-09-10 e
> só a leitura do contexto mostrou o erro. **Se forem escritas como resolvidas, a tese passa a
> afirmar o que não fez, nos quatro sítios que um arguente procura primeiro.**

- [x] B1 · Linha de base BM25 na recuperação — **FEITO** (verificado a 2026-09-10):
      `scripts/evaluate_retrieval_bm25.py` → `docs/evaluation/evaluation_retrieval_bm25.md`,
      e o corpo cita BM25 sete vezes (§2 e §5). Estava marcado como aberto.
- [x] B2 · Intervalos de confiança por setor em §5.3 — **FEITO** (verificado a 2026-09-10):
      `docs/evaluation/evaluation_per_sector.md` e `evaluation_per_sector_composicao.md`.
- [ ] B3 · Comparação com um assistente genérico: 20 acontecimentos, 3 perguntas, contar respostas
      com evidência conferível (data + fonte). Fecha a pergunta mais provável de 2026
- [ ] B4 · Reconstruir o rótulo da triagem com sensibilidades estimadas e encolhidas (§3.4) e repetir
      as seis famílias — resolve a hipótese alternativa de §5.4.7
- [ ] B5 · Eliminar a assimetria de referencial do «retorno do próprio dia» (§6.5, item 7)
- [ ] B6 · Reordenação por codificador cruzado sobre os top-k (§6.5, direção técnica 1)

## FASE C — Contribuição nova (QI4)

> Depende de A8. Pré-registar o critério de sucesso antes de qualquer medição.

- [x] C1 · Base de conhecimento reconstruída — `data/kb_fnspid_sbert.jsonl`, **78 481 registos**,
      all-MiniLM-L6-v2, dim 384, 15 tickers, 2018-01-01…2023-12-26. 287 s em CPU.
- [x] C1b · **Tentativa de reprodução — e o achado que dela saiu.** Correção de uma leitura
      apressada: escrevi primeiro que «reproduz dentro do desvio entre sementes». **Não reproduz,
      e a causa não é a semente: é o corpus.**

      | Medida | Publicado (2026-07-27) | Reconstrução (2026-09-09) |
      |---|---|---|
      | manchetes | **79 753** | **78 481** |
      | tickers | **14** (sem META) | **15** (com META) |
      | intervalo | — | 2018-01-01…2023-12-26 |
      | precision@5 | 0,595 ± 0,024 | 0,604 ± 0,018 |
      | taxa-base | 0,333 | 0,337 |
      | concordância de direção | 0,708 | 0,706 |

      A taxa-base mudou, o que só acontece se a **composição setorial do corpus** mudou. Não é
      ruído de amostragem.

### C1c — ACHADO DE REPRODUTIBILIDADE (crítico, não previsto)

> `data/fnspid_news_subset.csv` **não está sob controlo de versões** (não é conhecido do git) e
> foi regenerado a 2026-09-08. O corpus que produziu os números publicados **não é
> reconstruível a partir do repositório**. Filtrar o META não resolve: hoje há *menos* linhas
> apesar de haver *mais* um ticker.
>
> O Apêndice A.1 afirma que os corpora de origem «são reconstruídos pelos procedimentos de
> preparação descritos na Secção 3.2». A reconstrução corre — mas **não devolve o mesmo corpus**,
> e nada no procedimento o detetaria.

#### Causa-raiz identificada (2026-09-09)

Duas, ambas do nosso lado — **a origem não derivou**: o dataset Hugging Face
`Zihan1004/FNSPID` não é modificado desde **2024-04-09** (SHA `bf9189c4…`).

1. **Revisão móvel.** `download_data.py` apontava para `resolve/main`. O mesmo comando podia
   devolver conteúdo diferente em datas diferentes. → **CORRIGIDO:** revisão fixada em
   `FNSPID_REVISION = "bf9189c41527198897d1af3e17b1a0095279fc45"`.
2. **Paragem antecipada não verificada.** `early_stop` interrompe quando o mínimo alfabético de
   um chunk passa `XOM`, assumindo ordenação perfeita por ticker — assumida, nunca verificada.
   Uma exceção à ordenação, ou uma fronteira de chunk diferente, trunca o corpus **em silêncio**.
   → **CORRIGIDO:** auditoria de ordenação por chunk, e a construção canónica corre
   `--no-early-stop` (varredura completa, ~3,4 h, uma única vez).

#### O que passa a existir

- [x] C1c.1 · Revisão do Hugging Face fixada no script
- [x] C1c.2 · **Manifesto** `docs/design/fnspid_corpus_manifest.json` (versionado): revisão da
      fonte, tickers pedidos, janela, linhas, tickers presentes, intervalo de datas,
      **linhas por ticker**, **sha256 do CSV**, e a auditoria de varredura (chunks, violações
      de ordenação, se parou cedo). É isto que torna verdadeira a afirmação do Apêndice A.
- [x] C1c.5 · Sondagem — **falhou, e o modo de falha foi informativo.** O *stream* de 23,2 GB
      numa única ligação HTTP partiu-se:
      `IncompleteRead(5941119 bytes read, 23227038478 more expected)`. Uma varredura de horas
      dependente de uma ligação aguentar não é um procedimento reprodutível.
- [x] C1c.5b · **Abordagem substituída.** Separadas as duas responsabilidades:
      **descarregar** o bruto uma vez, resumível e fixado por revisão, via `huggingface_hub`
      (cache endereçada por conteúdo, logo a identidade é garantida pela revisão);
      e **filtrar** localmente, com varredura completa, as vezes que forem precisas.
      Novo procedimento: `scripts/build_corpus_canonical.py`.
      Medido: ~20 MB/s → **~20 min de descarga**, contra as 3,4 h estimadas para o *stream*.
- [x] C1c.5c · **FICHEIRO EM BRUTO OBTIDO E IDENTIFICADO.** `data/raw/nasdaq_exteral_data.csv`
      — **23 232 979 597 bytes**, descarregado por `scripts/fetch_fnspid_raw.py` (Range,
      resumível), da revisão fixada.
      **`sha256 = 1a7a3eb8e6b97ec19f286f2cfca3371542bddb272ab1eb8f36e33ad98fa5c4da`**
      Tamanho e soma estão agora **codificados em `build_corpus_canonical.py`**, que recusa
      correr se o ficheiro em disco não for este — falha em vez de produzir outro corpus em
      silêncio, que é o defeito original.
      A partir daqui, filtrar por outros tickers ou outras janelas é uma operação **local**,
      determinística, de minutos, e nunca mais depende da rede.
- [x] C1c.6 · **CORPUS DA TESE REPRODUZIDO EXATAMENTE.** Varredura completa do bruto fixado,
      sem paragem antecipada: **79 753 linhas, catorze tickers, 2018-01-01…2023-12-16**,
      `sha256 af61708c…d0197b`. Bate com `docs/evaluation/kb_fnspid_build.md` (2026-07-05)
      **ticker a ticker, catorze em catorze**. Fecho independente pelo lado da triagem:
      28 574 + 17 710 + 32 649 (blocos de `evaluation_triage.md`) + 820 (embargo, §5.4) =
      **79 753**. Auditoria completa em `docs/design/reproducao_corpus_2026-09-09.md`.

> **Nota de método (custou três tentativas):** a ponte remove os `$` de comandos PowerShell
> inline, e processos lançados por sessão morrem com ela. Regra: comandos PowerShell vão em
> ficheiro `.ps1` corrido com `-File`, e trabalhos longos vão num `.bat` lançado com
> `Start-Process`, com registo em ficheiro.
> Ficheiros temporários a apagar no fim: `scripts/_ps_*.ps1`, `scripts/_probe_fnspid.bat`,
> `scripts/_run_canonical.bat`, `data/_probe*.{csv,log}`, `data/_canonical.log`.
- [x] C1c.7a · **Consistência interna PROVADA entre os dois artefactos em disco.**
      `fnspid_artigos_15tickers.csv.gz` tem 93 093 linhas, das quais **14 612 são duplicados
      exactos**. Deduplicado dá **78 481** — e bate com `fnspid_news_subset.csv`
      **ticker a ticker, delta zero nos quinze**. Os dois ficheiros são a mesma extração.
- [x] C1c.7b · **A explicação escrita em `fnspid_corpus_local.md` está errada.** Atribui a
      diferença 79 753 → 78 481 a «deduplicação ligeiramente diferente». A conta não fecha:
      a META traz 432 linhas **novas** (entra como `FB` no FNSPID e só agora é normalizada),
      logo os restantes catorze tickers caíram de 79 753 para **78 049** — **menos 1 704
      linhas, 2,1%**, e não 1,6%. É uma hipótese não medida.
- [x] C1c.7c · ~~Pista: a janela de datas não é a mesma.~~ **HIPÓTESE REFUTADA.** As duas
      datas reconciliam-se: `2018-01-01` é feriado e `2023-12-16` é sábado, e o alinhamento
      remete-os para a sessão seguinte — `2018-01-02` e `2023-12-18`. A Tabela 3.1 mostra
      **dias de negociação depois do alinhamento**, não datas de notícia. Não falta nada; o
      que faltava era a legenda dizê-lo — **corrigido em C1c.16**.
- [x] C1c.7d · **As três perguntas, respondidas com a varredura completa:**
      **(1) Não.** Nada depois de 2023-12-16 — é o máximo do próprio FNSPID (o primeiro
      registo do bruto é `2023-12-16 23:00:00 UTC`, ordenado por data descendente).
      **(2) 79 753**, catorze tickers, antes de deduplicar.
      **(3) 1 704** duplicados exactos `(ticker, data, título)` no canónico — 2,1%, não os
      14 612 (15,7%) que o `.gz` exibia. Ver C1c.7e.
- [x] C1c.7e · **A extração antiga (`.gz`) duplicava linhas, e está provado.** Das 93 093
      linhas, **12 927 são repetições byte a byte da linha inteira** (mesmo `Url`, mesmo
      `Publisher`, mesmo corpo). Prova aritmética: o bruto contém no máximo **9 616**
      ocorrências de `,AAPL,` em **todos** os anos, e o `.gz` declara **9 811** linhas de
      AAPL só em 2018–2023 — impossível a partir de uma leitura limpa. Causa provável (não
      medida): retoma da descarga em fluxo a reprocessar um bloco já lido.
      **Conteúdo perdido: nenhum.** Descontado um espaço final em 140 títulos, a concordância
      entre o `.gz` e o canónico é **total** — diferença simétrica zero sobre 78 049 trios.
- [ ] C1c.10 · **A política de duplicados nunca foi declarada — e a decisão real é o
      contrário do que se supôs.** O corpus da tese **conserva** 1 704 títulos exactamente
      repetidos (2,1%), tal como o FNSPID os entrega; não desduplica coisa nenhuma. Isso é
      uma decisão de construção e a §3.2 não a menciona. Tem de passar a constar, com o
      número — é do mesmo tipo das nove definições de rótulo que a §5.4 mede em vez de assumir.
      Acompanha-a uma verificação de sensibilidade (ver B7): repetir a medição sobre os
      **78 049** títulos únicos e reportar a diferença.
- [x] C1c.8 · **`tests/test_corpus_canonico.py`** — sete testes, todos a passar. Fixa a
      identidade do corpus em três níveis: origem (revisão + `sha256` do bruto), manifesto
      versionado (linhas, `sha256`, datas, contagem por ticker) e ficheiro local (soma de
      controlo e composição, saltado quando ausente). Inclui o fecho independente pelos
      blocos da triagem e a proibição explícita da paragem antecipada. Mudar o corpus passa
      a exigir mudar este teste — ou seja, uma decisão consciente.
- [x] C1c.3 · **Confirmado: a triagem partilha o mesmo CSV.** O ficheiro congelado
      `evaluation_retrieval_fnspid.md` diz «79753 manchetes · 14 tickers», e §3.2 diz
      «79 753 exemplos, 14 empresas». **O mesmo problema atinge a QI3**, não só a QI2.
- [x] C1c.9 · ~~Recorrer QI2 e QI3 e atualizar os «79 753»~~ — **desnecessário: os números
      publicados estão certos.** O corpus foi reproduzido exactamente, logo §1.4, §3.2,
      §4.2.3, §5.4.1 e §6.1 ficam **como estão**. O que estava errado era o ficheiro em disco
      a 2026-09-08, não a tese. Corpus de trabalho reposto a partir do canónico; o divergente
      ficou em `data/_arquivo/fnspid_news_subset_divergente_2026-09-08.csv`.
- [x] C1c.11 · **A KB foi reconstruída sobre o corpus reposto: 79 753 registos, «0 descartes»**
      — igual ao build congelado de 2026-07-05. Embedder SBERT `all-MiniLM-L6-v2` (dim 384),
      `HF_HUB_OFFLINE=1`, amostra versionada protegida por `--sample` descartável.
- [x] C1c.12 · **Sem desvio mensurável.** `scripts/verificar_desvio_kb.py` compara a KB
      reconstruída com os 50 registos congelados de `data/samples/kb_fnspid_sample.jsonl`:
      **50/50 encontrados**; impactos +1d/+3d/+5d com `|delta|` máximo de **2,3e-07**;
      embeddings SBERT com **cosseno 1,000000000** em todos. Os preços do yfinance não se
      moveram de forma detetável para estes tickers e datas, e o embedder é estável entre
      versões. Um rótulo só mudaria se estivesse a menos de 2e-07 do limiar.
- [x] C1c.13 · **Preços fixados, com proveniência registada.** Não havia cache nenhuma: cada
      construção ia à rede, e por baixo estava uma cadeia de **cinco fontes** — se o yfinance
      falhasse num ticker, outra servia **sem que isso aparecesse em lado nenhum**. Era um
      buraco maior do que o reajuste retroativo dos dividendos.
      Feito, por TDD (onze testes escritos antes da implementação):
      `investigator/market_data/price_cache.py` grava cada série num CSV por
      `(ticker, janela)` e regista fonte, dimensão, extremos e `sha256` num manifesto;
      `load_close_series` ganhou `cache_dir` e `refrescar` — **opcionais**, para a camada viva
      continuar a ir à rede; o `build_kb.py` passa a usar a cache por omissão e publica
      `docs/design/precos_manifest.json` (versionado).
      `tests/test_precos_manifesto.py` vigia a coerência do registo, incluindo um teste que
      **falha se alguma série passar a vir de outra fonte**.
- [x] C1c.13b · **A primeira versão da cache perdia dígitos, e foi um teste que a apanhou.**
      O `assert_series_equal` compara com tolerância relativa de 1e-5 por omissão — deixava
      passar exactamente o defeito. Com `check_exact=True` e um caso à mão (`0,1+0,2`, que em
      dupla precisão vale `0,30000000000000004`), o `pandas` mostrou-se lossy **dos dois
      lados**: escrevia `0.3` e, mesmo escrito com dezassete dígitos, o leitor rápido devolvia
      `0.3`. Corrigido com `float_format="%.17g"` na escrita e `float_precision="round_trip"`
      na leitura. **Uma cache que perde dígitos não fixa coisa nenhuma.**
- [x] C1c.14 · **CADEIA VERIFICADA DE PONTA A PONTA.** A QI2 recorrida sobre a KB reconstruída
      devolve **P@5 = 0,595 ± 0,024**, acaso **0,333** — os dois valores exactamente iguais aos
      publicados. Bruto (`sha256`) → corpus (`sha256`, 79 753) → KB (impactos a sete casas,
      embeddings idênticos) → **resultado publicado**. Escrito para
      `data/_arquivo/_qi2_verificacao.md`; o ficheiro congelado ficou intacto.
      Acrescentado `--out` ao `evaluate_retrieval_fnspid.py` para que uma verificação nunca
      mais tenha de arriscar escrever por cima do artefacto citado pela tese.
      **Isto confirma o que ficou dito a 2026-09-08: o `0,604` não era variação de semente.**
- [x] C1c.15 · **B1 recorrido sobre a KB correta — resultado válido, e mais modesto do que o
      anterior.** SBERT **0,5946±0,0240** · BM25 **0,5214±0,0159** · acaso 0,3333 · recência
      0,0900. Diferença emparelhada **+0,0733±0,0112**, positiva nas cinco repetições
      (+0,0584 a +0,0920). Zero colocações com pontuação nula no BM25.
      **Leitura honesta:** a margem do BM25 sobre o acaso é +0,1881 e a do SBERT +0,2613 — o
      *baseline* lexical sozinho capta **72%** da vantagem que a tese atribui à representação
      semântica. O ganho semântico é real e consistente, mas é o menor dos dois efeitos, e a
      §5.3 tem de o dizer.
      (A execução de 2026-09-08 dava +0,0798 e 70%; corria sobre o corpus errado.)
- [x] C1c.16 · **§3.2 escrita, nas duas línguas.** Quatro declarações que faltavam entraram em
      `tese-pt/ch3` e `tese-eng/ch3`: (a) a origem fixada por revisão e `sha256`, com o
      manifesto e o teste que a guarda; (b) a política de duplicados — 1 704 repetições
      exactas (2,1%) **conservadas** tal como o FNSPID as entrega; (c) porque são catorze
      empresas e não quinze — o FNSPID indexa a Meta como `FB`, e isso são 432 títulos em 87
      dias entre fevereiro e junho de 2020; (d) a varredura completa, com as dezoito violações
      de ordenação como razão. Legendas das Tabelas 3.1 e 3.2 corrigidas: as datas são dias de
      negociação depois do alinhamento, e a empresa em falta passa a ter nome.
      **Ambas compilam sem erro: PT 130 páginas, EN 126.**
- [x] C1c.17 · **§5.3.4 acolheu o BM25, nas duas línguas.** Dois parágrafos: a medição
      (0,521 contra 0,595, acaso 0,333, emparelhado +0,073 positivo nas cinco repetições) e a
      leitura que ela obriga — o comparador lexical da Figura 5.6 é sobreposição de palavras,
      mais fraco do que o BM25, e a sua ausência deixava a vantagem semântica parecer maior do
      que é. Citação `robertson2009bm25`, já existente nas duas bibliografias.
      **PT 130 páginas, EN 126, zero erros; as únicas advertências são formas de tipo de letra
      que já lá estavam.**
      Nota de método: o `chapter5.tex` usa CRLF e o `chapter3.tex` usa LF. Uma edição em modo
      de texto reescreveria as 1 751 linhas do capítulo 5. Edições nos `.tex` fazem-se em
      **modo binário**, com o terminador preservado.

### C1h — REGRA DO AUTOR (2026-09-09): o que não se reproduz aqui, desconsidera-se

> «Tudo o que for resultados anteriores, que não tenhamos a certeza da sua viabilidade, ou que
> não consigamos reproduzir atualmente neste computador, devem ser desconsiderados. Nem que
> tenhamos que fazer download de modelos e de datasets do zero.»

- [x] C1h.1 · **Inventário feito.** `scripts/auditar_reprodutibilidade.py` percorre os 50
      documentos de `docs/evaluation/`, encontra o gerador de cada um e verifica se as entradas
      existem. Saída em `docs/design/auditoria_reprodutibilidade.json`.
- [x] C1h.2 · **Quatro documentos dependem do corpus do Finnhub, que não existe.** Os scripts
      são `evaluate.py`, `evaluate_per_sector.py`, `evaluate_corpus_and_filter.py` e
      `evaluate_retrieval_embedders.py`. Entre eles sustentam **§5.3.1, §5.3.2 (Figura 5.6),
      §5.3.3 (Figura 5.7, painel A)** e a comparação de codificadores.
      Pela regra acima: **saem, a menos que o ficheiro apareça** (ver tarefa manual nº 2).
- [x] C1h.3 · **Os outros três «em falta» não são perdas.**
      `data/_cache_volumes.csv` é uma cache que o próprio script refaz do yfinance;
      `data/narrator_harness_log.jsonl` é **saída** do arnês, não entrada;
      `data/triage_dataset_ext.csv` reconstrói-se com `build_dataset.py --ext`.
- [x] C1h.4 · **RESOLVIDO por outra via**: a §5.3 passou a medir sobre o subconjunto **equilibrado por setor** (569 de cada um dos cinco, 2 845 no total) do corpus Finnhub fixado por manifesto, e o Finnhub apareceu. O plano B era: refazer a §5.3 sobre o FNSPID, e era uma
      melhoria mesmo que apareça: o resultado principal passa de um corpus de 27 dias
      irrepetível para um de seis anos fixado por `sha256`. Inclui refazer a alternativa
      trivial e a análise por setor (hoje na §5.3.3) e a comparação de codificadores.
      **Nota já medida:** no bloco de teste do FNSPID a taxa-base de setor é 0,629 (nove
      empresas) e no corpus completo 0,333 (catorze) — a escolha do conjunto de candidatos tem
      de ser declarada, porque muda o acaso por um factor de dois.
- [x] C1h.5 · **FEITO**: o FinBERT está medido a `0{,}275` no corpus novo. Codificadores da comparação (MPNet, FinBERT, E5-small,
      BGE-small) e refazer o `evaluation_retrieval_embedders.md` sobre o FNSPID. O autor
      autorizou descarregar do zero.
- [ ] C1h.6 · **→ consolidado em Z2**, com a causa medida (o yfinance ajusta retroativamente). `evaluate_anomaly.py` vai ao yfinance sem cache e a §5.2 não é determinística
      hoje. Aplicar-lhe a cache de preços, como se fez ao `build_kb.py`.
- [ ] C1h.7 · **Verificar os 28 documentos cuja dependência a auditoria não detectou.** A
      deteção por expressão regular não apanha caminhos construídos em `argparse`. Não é
      «estão bem»: é «ainda não se sabe».

### C1e — ACHADO NOVO: o corpus da avaliação preliminar não existe

- [x] C1e.1 · **RESOLVIDO**: existe um CSV de notícias do Finnhub em `data/`, e a §5.3 passou a usar o subconjunto equilibrado (569 por setor) do corpus fixado por manifesto. Era o corpus das 3 714
      manchetes sobre o qual assenta a §5.3.2 — a Figura 5.6, o resultado de recuperação que a
      tese apresenta em primeiro lugar (MiniLM 0,514 · lexical 0,346 · acaso 0,240). Não está
      no disco, não está no histórico do git (`data/**` é gitignored) e não está no `archive/`.
      Só sobrevivem amostras: 30 linhas em `data/samples/finnhub_news_sample.csv` e 50 registos
      em `kb_finnhub_sbert_sample.jsonl`.
      **Consequência:** a Figura 5.6 não é reproduzível. E `evaluation_results.md`, que a
      gerou, abre com «Resultados da avaliação (reprodutível)» — uma afirmação que hoje não se
      sustenta para este braço.
      Contraste: a réplica à escala da §5.3.4 **é** reproduzível de ponta a ponta, e ficou
      provada hoje.
- [x] C1e.1b · **Procurado na máquina inteira: não está cá.** Varrido todo o perfil
      `C:\Users\ruifa` (incluindo ficheiros ocultos): de `finnhub*` só existem o logótipo em
      três sítios e a amostra de 30 linhas. Nenhum `*news*.csv` fora do repositório. E
      **`triage_dataset.csv` também não existia** — ver C1f, onde se reconstruiu.
      Os perfis desta máquina são `ruifa`, `1180934` e contas de sistema: **não há perfil
      `henri` aqui**, logo o caminho que o `evaluation_triage.md` regista é de outra máquina.
- [ ] C1e.2 · **PERGUNTA PARA O HENRIQUE, antes de escrever seja o que for na tese.**
      O `docs/evaluation/evaluation_triage.md` aponta para
      `C:\Users\henri\Desktop\DIMEIA\data\triage_dataset.csv` — **outro perfil de utilizador**.
      O corpus do Finnhub pode estar nessa máquina, ou numa cópia de segurança. Enquanto isso
      não estiver esclarecido, **não se escreve na tese que o corpus não foi conservado**: era
      afirmar o que não está verificado, e o teu próprio enunciado diz para assinalar em vez de
      inventar.
      Se aparecer: versioná-lo (ou a uma amostra) e fixá-lo por `sha256`, como se fez ao FNSPID.
      Se não aparecer: declarar em §5.3.1 e §5.3.5, e ponderar dar mais peso narrativo à §5.3.4,
      que é o braço que qualquer pessoa pode voltar a correr.

### C1f — A QI3 também reproduz (o conjunto de treino não existia, e voltou)

- [x] C1f.1 · **`data/triage_dataset.csv` não estava em disco.** O conjunto sobre o qual
      assenta toda a §5.4 tinha desaparecido, tal como o do Finnhub. A diferença é decisiva:
      **este é reconstruível**, porque o `build_dataset.py` o deriva do corpus (agora fixado
      por `sha256`) e dos preços (agora fixados por manifesto).
- [x] C1f.2 · **Reconstruído, e bate ao número.** `build_dataset.py` sobre o corpus canónico:
      **79 753 linhas**, descartes todos a zero, e a divisão cronológica devolve
      **embargo 820 · treino 28 574 · validação 17 710 · teste 32 649**, com prevalências de
      **38,5% / 47,0% / 37,8%**. São exactamente os valores de
      `docs/evaluation/evaluation_triage.md` e o `0,378` que a §5.4.1 cita como prevalência do
      bloco de teste. **A QI3 é reproduzível a partir da origem fixada.**
- [x] C1f.3 · **Acrescentados `--out` e `--figuras-dir` ao `train_triage.py`.** O script
      escrevia sempre por cima do `evaluation_triage.md` congelado **e** de duas figuras da
      tese (`eval_triage_pr.pdf`, `eval_triage_calibration.pdf`). Uma verificação não pode
      correr esse risco; por omissão o comportamento é o de sempre.
- [x] C1f.4 · **Os PR-AUC reproduzem — quatro dos cinco exactamente, e o quinto explica-se.**
      Volatilidade **0,542**, contexto **0,538**, texto **0,439**, `full` **0,496** — iguais
      aos publicados. O `gbm` dá **0,470** contra os **0,469** da tese.
      O `git diff` do `models/triage_gbm.json` deu a comparação ao décimo dígito, sem
      arredondamento: `full` desvia-se **2,7e-05** no PR-AUC e o `gbm` **6,0e-04** — vinte
      vezes mais. As linhas, os blocos e as contagens de positivos são **idênticos**, a semente
      é a mesma: nenhum rótulo virou. O que muda são as **features contínuas**, que derivam dos
      preços, e os preços de setembro não são bit a bit os de julho. Um corte de árvore é
      descontínuo e amplifica o que o modelo linear absorve.
      **A conclusão da §5.4 não mexe**: 0,496 e 0,470 continuam abaixo de 0,542.
      É exactamente a deriva que a cache de preços (C1c.13) elimina daqui para a frente.
- [x] C1f.5 · **Duas armadilhas fechadas.** O `train_triage.py` escrevia sempre por cima do
      `evaluation_triage.md` congelado, de duas figuras da tese **e dos modelos que a aplicação
      usa** — os modelos chegaram a ser substituídos nesta execução e foram repostos por
      `git checkout`. Ganhou `--out`, `--figuras-dir` e `--modelos-dir`, com o comportamento de
      sempre por omissão. A mensagem final passou a imprimir os caminhos reais, em vez de
      afirmar `tese-pt/figures` mesmo quando escreveu noutro sítio.

### C1g — COLISÃO DE CACHES apanhada antes de morder

- [x] C1g.1 · **Duas caches de preços, o mesmo nome de ficheiro, esquemas diferentes.**
      O `build_dataset.py` guarda a sua cache em `data/prices/` como
      `{ticker}_{inicio}_{fim}.csv`, gravando um `Series` com índice (colunas `Date,Close`) e
      lendo `["Close"]`. A cache nova, na primeira versão, apontava para a **mesma pasta** com
      o **mesmo nome** e o esquema `date,close` — e chegou a escrever catorze ficheiros lá.
      Bastaria o `build_dataset.py` pedir a mesma janela para ler o ficheiro errado: `KeyError`
      no melhor caso, valores errados no pior.
      Corrigido: a cache nova vive em `data/prices_kb/`, com dois testes a impedir que as
      pastas voltem a coincidir e a verificar que o `build_kb.py` aponta para a certa.

#### O que NÃO era o problema

`fnspid/`, `tmp/`, `work/`, `data-temp/` **não existem em disco** — as limpezas já tinham sido
feitas e o `.gitignore` é exemplar. O que ocupa espaço é `.venv` (1,6 GB, é o ambiente) e
`.git` (0,65 GB de histórico, que não se reescreve antes da defesa). **Não há limpeza de
ficheiros que resolva a reprodutibilidade** — resolve-se fixando a origem, que é o que foi feito.

### C1d — Lição de processo (erro meu, apanhado pela suite dele)

Reconstruir a KB sobrescreveu dois artefactos que não devia:
- `data/samples/kb_sample.jsonl` — amostra **versionada** com vetores de 64 dim do HashingEmbedder;
  passou a ter 384 dim do SBERT e partiu `test_knowledge_base` e `test_smoke` (que correm offline).
- `docs/evaluation/evaluation_retrieval_fnspid.md` — resultado **congelado** que a tese cita;
  o 0,595 desapareceu e `test_method.py` apanhou-o de imediato.

Ambos revertidos com `git checkout`. **Regra a partir daqui:** `build_kb.py` corre sempre com
`--sample` para um caminho descartável, e nenhuma avaliação nova escreve por cima de um
ficheiro congelado citado pela tese.
- [x] C2 · **Protocolo de pares fixado e declarado.** `investigator/qi4/pares.py`.
      Alvo de um par: `1 − |percentil(a) − percentil(b)|` sobre o retorno anormal ao horizonte
      primário. O percentil, e não a diferença bruta, por duas razões declaradas: os retornos
      têm cauda pesada e meio ponto percentual não significa o mesmo no meio e no extremo; e o
      alvo fica em `[0,1]` por construção, que é o domínio da `CosineSimilarityLoss`, sem
      escala arbitrária a justificar.
      Pares **entre empresas diferentes**, para não ensinar o contrário do que a avaliação
      exige; **dentro do mesmo bloco**; o **embargo nunca entra**.
- [x] C3 · **Vinte testes, escritos antes da lógica.** `tests/test_qi4_pares.py`. Os três que
      importam: nenhum par cruza fronteira de bloco; o embargo não entra; e **o mapa de
      percentis é ajustado só no treino** — provado metendo valores absurdos no bloco de teste
      e exigindo que os alvos do treino não mexam. É a fuga que nenhum teste de fronteiras
      apanha, porque não há fronteira nenhuma a ser cruzada.
- [x] C3b · **Um teste meu estava errado, e apanhou-me a mim.** Escrevi «inverter o sinal de
      todos os retornos tem de mudar os alvos do braço de direção» — e falhou. Não era o
      código: como o alvo assenta em **percentis**, uma inversão global só inverte a ordem, e
      as diferenças de percentil ficam iguais. A inversão global **não** distingue os braços.
      O que os distingue é um par concreto: para `+x` e `−x`, a magnitude dá alvo **1,0** e a
      direção dá **0,1**. Está agora verificado à mão sobre `±1%…±5%`, com os dois percentis
      calculados no papel. Sem esta correção, o teste teria dado uma falsa garantia sobre a
      única comparação que **é** o resultado da QI4.
- [x] C3c · **DECIDIDA**: o treino correu e a QI4 está fechada, logo a pergunta foi respondida pelos factos. Ficava: **pergunta de fundo, para decidir antes de treinar seja o que for.**
      Se o codificador é ajustado para que a proximidade signifique grandeza comparável, então
      os precedentes que ele devolve são aqueles cuja grandeza ele julga parecida com a do caso
      novo — e mostrar os impactos deles é, na prática, uma estimativa de grandeza para o caso
      novo. Isto roça a restrição fundadora («explicar sem prever»).
      Duas respostas honestas, e a tese tem de escolher uma **em texto**, não por omissão:
      (a) a restrição é sobre **direção**, e dizer «casos como este moveram-se isto» é uma
      afirmação sobre o passado, não uma previsão do futuro;
      (b) assumir que a QI4 **refina** a restrição em vez de a respeitar sem mais — a grandeza
      é parcialmente aprendível do texto, a direção não é, e é isso que os dois braços medem.
      A (b) é mais forte e é o que os resultados provavelmente sustentam, mas muda o
      enquadramento do Cap. 1. **Não avanço para o Cap. 6 sem isto decidido.**
- [x] C3d · **Arnês de avaliação com DUAS métricas, e a razão de a segunda não bastar.**
      A §5.3 mede por pertença ao setor, que não sabe nada sobre materialidade: um codificador
      ajustado para aproximar grandezas parecidas pode descer nessa métrica e estar, ao mesmo
      tempo, a fazer exactamente o que se lhe pediu. Avaliá-lo só por setor seria julgá-lo pela
      métrica de outro trabalho.
      `investigator/qi4/avaliacao.py` + `scripts/avaliar_qi4.py`: **comparabilidade de
      materialidade** (diferença média de grandeza entre consulta e precedentes, em pontos —
      menor é melhor) e **precisão@k por setor** (a da §5.3), sobre as **mesmas consultas**,
      sorteadas antes de qualquer modelo entrar, logo emparelhadas.
- [x] C3e · **A LINHA DE BASE, e é o melhor argumento que a QI4 podia ter.** Bloco de teste,
      protocolo simétrico, 500 consultas × 5 repetições, k=5:

      | | Comparabilidade (pp) | Precisão@5 |
      |---|---:|---:|
      | SBERT da tese, sem ajuste | **2,173 ± 0,062** | 0,771 ± 0,011 |
      | acaso | **2,259 ± 0,107** | 0,629 ± 0,007 |

      **O codificador da tese é praticamente indistinguível do acaso na comparabilidade de
      materialidade**: 2,173 contra 2,259 pontos, uma diferença de 0,086 sobre desvios de
      0,062 e 0,107. Os precedentes que ele devolve são tematicamente certos e, quanto à
      grandeza do movimento, tão informativos como escolher ao acaso. **É exactamente a lacuna
      que a QI4 existe para preencher, e agora está medida em vez de suposta.**
      ⚠️ **Estes números NÃO se comparam com os `0,595`/`0,333` da §5.3.4.** O conjunto de
      candidatos é outro: o bloco de teste tem **nove** empresas e o corpus completo tem
      catorze, o que sobe a taxa-base de setor de 0,333 para 0,629. As comparações que valem
      são as de dentro desta tabela, que são emparelhadas. Tem de constar do texto.
- [x] C5-v1 · **PRIMEIRA TENTATIVA: colapso total da representação. Resultado descartado.**
      Os dois braços treinaram (40 000 pares, 1 época, `lr=2e-5`, CoSENT) e a tabela parecia
      um resultado nulo modesto — magnitude 2,156 pp contra 2,173 da base, direção 2,188.
      **Não era um resultado nulo, era uma experiência partida**, e só se soube porque se foi
      verificar se o modelo se tinha mexido:

      | | cosseno entre manchetes DIFERENTES | norma do vetor médio |
      |---|---:|---:|
      | base | 0,2234 | 0,4732 |
      | magnitude | **0,9929** | **0,9964** |
      | direção | **0,9912** | **0,9956** |

      Os modelos ajustados mapeiam **todas** as manchetes para praticamente o mesmo vetor. O
      desvio por dimensão caiu dez vezes. Nenhum número dessa tabela vale nada.
- [x] C5-v1b · **A causa: a amostragem de pares, e a culpa é do desenho, não do modelo.**
      Sorteando dois índices ao acaso, a diferença de percentis é **triangular** — média `1/3`,
      quase nada nos extremos — e o alvo `1 − |Δ|` fica agarrado a `0,665` (medido: média 0,665,
      desvio 0,237). Com um alvo assim concentrado, a perda mínima obtém-se a prever a média
      para tudo, e prever a média para tudo **é** colapsar a representação.
- [x] C5-v1c · **Correcção: amostragem estratificada — e a primeira correcção também estava
      errada.** Escrevi «sorteia um índice e soma-lhe `±d`, cortando a `[0,1]`». Falhou no
      teste: `E[min(d, 1−p)] = 1/3` com `d` e `p` uniformes, ou seja **o corte devolvia
      exactamente a triangular que se queria evitar**. A versão certa sorteia `d` primeiro e só
      depois o ponto de partida dentro da margem que `d` admite, `p_a ~ U(0, 1−d)`, de forma
      que `|Δ| = d` por construção. Sobre os dados reais: alvo médio **0,499**, desvio
      **0,289** — a uniforme exacta.
      Cinco testes novos, incluindo um que **documenta o defeito** (a triangular) para que não
      volte, e um que compara as duas amostragens pela cauda dos pares dissemelhantes, que é o
      que as distingue.
- [x] C5-v2 · **Retreino dos dois braços com estratificação e `lr=5e-6`: terminado.**
      `magnitude_v2` 1250 passos / 3351 s · `direcao_v2` 1250 passos / 2691 s, os dois com
      `EXITCODE=0`. Perda final 8,031 e 8,045 — as duas trajetórias praticamente sobrepostas.
- [x] C5-v2b · **Diagnóstico de colapso repetido antes de qualquer métrica, e passa nos dois.**
      Cosseno entre manchetes diferentes `0,2709` e `0,2771` contra `0,2052` da base (o v1
      colapsado dava `0,9936`). E os dois **moveram** mesmo o espaço — cosseno base↔ajustado
      `0,782` e `0,775` — preservando a geometria das semelhanças (`0,607` e `0,630`), que é o
      que separa «aprendeu» de «não degenerou».
- [x] C6-v2 · **AVALIAÇÃO CORRIDA NO AMBIENTE CANÓNICO A 2026-09-10, e o resultado é NEGATIVO.**
      Bloco de teste, 32 649 manchetes, 9 empresas, protocolo simétrico, 500 consultas × 5
      repetições, consultas idênticas nos três braços (logo emparelhadas):

      | Braço | Comparabilidade (pp) ↓ | Precisão@5 ↑ |
      |---|---:|---:|
      | base (sem ajuste) | **2,173 ± 0,062** | **0,771 ± 0,011** |
      | `magnitude_v2` | 2,185 ± 0,065 | 0,746 ± 0,009 |
      | `direcao_v2` | 2,157 ± 0,071 | 0,744 ± 0,006 |
      | acaso | 2,259 ± 0,107 | 0,629 ± 0,007 |

      **Na métrica que o ajuste existe para melhorar, nada acontece:** `+0,012` pp e `−0,016` pp
      face à base, ou seja **cerca de um quinto** do desvio entre repetições do próprio braço.
      **E o ajuste tem um custo que se mede:** a precisão@5 por setor cai `0,026`, com o mesmo
      sinal nos dois braços e acima da dispersão. Como o treino verificadamente funcionou (C5-v2b),
      **é a hipótese que não se confirma, não a montagem que falhou.**
      ⚠️ **A proveniência ficou fechada:** estes números foram primeiro medidos num contentor
      Linux (`sentence-transformers` 6.0.1) e reproduziram-se aqui — a **precisão@5 exactamente
      nos quatro braços**, a comparabilidade com 0,005 a 0,012 pp de diferença. Artefactos:
      `data/_arquivo/_qi4_tres_v2.md` (contentor) e `_qi4_tres_v2_local.md` (canónico), que
      coexistem de propósito. Detalhe em `docs/design/qi4_resultado_2026-09-09.md` §5.
- [x] C6b · **DEFEITO CORRIGIDO a 2026-09-10, e a variante causal correu.** O `topo_k`
      **rebenta** em vez de devolver falsos vizinhos; o filtro é do chamador
      (`consultas_viaveis`), aplicado uma vez por lote **antes** de qualquer modelo — só vê
      tickers e datas, logo os braços continuam emparelhados —, e a consola e o relatório
      declaram quantas consultas caíram. Extensão real: **2 de 2500 (0,08%)**. Seis testes
      novos, com o controlo no sentido oposto. Prova de que o defeito era real, no mesmo input:
      sem candidato elegível o código antigo devolvia `[0 1 2 3 4]`; no causal devolvia
      `[0 1 2]`, **incluindo a própria consulta e o futuro**.
      **Resultado causal — o negativo é robusto ao protocolo da produção:**

      | Braço | Comparabilidade (pp) ↓ | Precisão@5 ↑ |
      |---|---:|---:|
      | base (sem ajuste) | **2,287 ± 0,049** | **0,747 ± 0,011** |
      | `magnitude_v2` | 2,309 ± 0,069 | 0,722 ± 0,013 |
      | `direcao_v2` | 2,289 ± 0,074 | 0,720 ± 0,012 |
      | acaso | 2,336 ± 0,067 | 0,621 ± 0,015 |

      ⚠️ **E dá uma observação que a variante simétrica não podia dar:** a margem da base sobre
      o acaso **encolhe** de `0,086` pp para `0,049` pp. No protocolo real o codificador sem
      ajuste está ainda mais perto do acaso, o que reforça a motivação da QI4 e torna o negativo
      mais claro. Artefacto: `data/_arquivo/_qi4_causal_local.md`.
- [x] C9 · **A porta congelada da QI3 afinada em voz alta.** O
      `test_frozen_reproducibility` falhava nas três métricas a `abs=1e-12`. **Não era o
      `scipy`** (o `predict_proba` é bit-idêntico a uma sigmoide em `numpy` puro e o Brier à
      mão iguala o do `sklearn`) e **não era ruído de vírgula flutuante** (a deriva em `p` é
      ~6e-9 por elemento, sete ordens acima do eps). A causa estava já diagnosticada nas §15 e
      §16 da auditoria do corpus: o sidecar é de julho e **de outra máquina**, e as features
      derivam de preços que já não são bit a bit os mesmos. A porta era inatingível por
      construção, e um critério que não pode passar deixa de ser porta. Passa a verificar o
      número que a tese publica (três casas) **e** um envelope medido de `1e-6`, com a razão
      escrita dentro do teste. Verificado que dispara com deriva 10× acima do envelope e com a
      terceira casa mudada.
- [x] C6c · *(registo histórico do diagnóstico — corrigido em C6b; fica porque descreve a
      forma do defeito, que importa mais do que a extensão)* ~~DEFEITO POR DECIDIR antes
      de a variante causal poder ser lida.~~ Consultas do
      primeiro dia do bloco não têm candidato elegível: o `rng.choice` do braço do acaso
      **rebenta** (2 em 2500) e — pior — o `topo_k` devolve `[0 1 2 3 4]` **em silêncio**, pelo
      que sem o rebentamento do acaso a tabela sairia com falsos vizinhos lá dentro. Não
      corrigido: qualquer das duas opções **muda a população de medição**, e isso é decisão do
      autor. As duas opções estão escritas em `docs/design/qi4_resultado_2026-09-09.md` §3.
- [x] C4 · Braço de **controlo** — **FEITO** (verificado a 2026-09-10): `docs/design/qi4_resultado_2026-09-09.md` nomeia «o braço de controlo C4 (`ProsusAI/finbert`)» e reporta o colapso. ⚠️ A minha primeira verificação deu falso negativo por exigir o cosseno `0,970` no mesmo ficheiro.
      Despromovido de contribuição a controlo: o FinBERT2 (KDD 2025) já mostrou que resulta
- [x] C5 · Braço **principal** — **FEITO**: o valor `2{,}185` está na tese e o artefacto existe. Ajuste contrastivo por materialidade comparável (`|impacto|`,
      nunca direção). Ajustar **o codificador**, não uma cabeça sobre embeddings congelados —
      é a limitação declarada de [Jeong26] e é o que faz disto extensão e não repetição
- [x] C5b · Braço de **replicação** — **FEITO**: `2{,}157` na tese. A mesma montagem com retorno **com sinal**, reproduzindo
      [Jeong26] no arnês desta tese. **A comparação magnitude vs. direção é o resultado da QI4**
- [x] C6 · **FEITO**: artefacto do resultado + os desvios (`± 0{,}062`) na tese. Avaliados os três no arnês idêntico, com intervalos por reamostragem
- [x] C7 · **FEITO**: a secção existe no corpo (`sec:av_qi4`), com o que do resultado não decorre
- [x] C8 · **FEITO** (verificado a 2026-09-10): a QI4 é nomeada no Cap. 1 (§1.3) e no Cap. 6. ⚠️ A minha verificação deu falso negativo por procurar `QI4` quando a tese escreve `\gls{QI}4` — é a terceira vez hoje que um padrão acerta ao lado da forma real.

## FASE D — Estrutura e secções novas

- [ ] D1 · Nova §3.7 «Onde entra a inteligência artificial neste sistema» + figura
- [ ] D2 · Parágrafo que enuncia «57% calibrado + modelo sem discriminação demonstrada»
- [ ] D3 · Frase de enquadramento na abertura do Cap. 4 sobre o estatuto das suas medições
- [ ] D4 · Retirar a Figura 4.4; aliviar a Tabela 4.2
- [ ] D5 · Comprimir o Cap. 6 de 14 para ~10 páginas («o Cap. 5 mede, o Cap. 6 interpreta»)
- [ ] D6 · Reformular a QI2 (retirar a autorreferência às «alternativas avaliadas»)
- [ ] D7 · Alinhar a Contribuição 2 (§1.4) com o que a §5.3 entrega
- [ ] D8 · Frase que justifica o modelo continuar implantado
- [ ] D9 · Renomear o Cap. 5 («Avaliação»); decidir o destino de §4.8 (promover, ligada a D1)
- [ ] D10 · Apêndice: fundir A.1+A.2, cortar A.5 a meia página, promover as linhas «Retirada» para o corpo
- [ ] D11 · Frase sobre o canal público não constituir prestação de serviço (§3.8.3)
- [ ] D12 · Resumo/Abstract: acrescentar operação contínua e o diagnóstico como resultado

## FASE E — Redundâncias e correções factuais

- [ ] E1 · Encolhimento de Vasicek explicado por extenso em §2.5 e §3.4 → cortar de §2.5
- [ ] E2 · Objetivo de treino do SBERT ×3 (§2.4, §3.5, §5.3.2) → uma vez
- [ ] E3 · «Não é método novo, é seleção e integração» ×3 (§1.4, §2.9, §6.1) → uma vez
- [ ] E4 · Fadiga de alertas ×3 (§2.6, §3.8.3, §4.4) → §3.8.3
- [ ] E5 · Dívida técnica de Sculley ×4 (§2.8, §4.6.1, §5.6.1, §6.4) → §2.8 + §5.6.1
- [ ] E6 · Argumento RAG ×3 (§2.4.1, §4.7.1, §4.8) → §2.4.1 + §4.8
- [ ] E7 · Três causas do atraso ×2 (§4.6, §6.4) → §4.6
- [ ] E8 · «Rótulo favorece a volatilidade» ×3 → §5.4.7 + Tab. 6.1
- [ ] E9 · Defeito dos 36,8% ×2 (§4.5.1, §6.4) → §4.5.1
- [ ] E10 · «Três ocasiões» ×3 (§5.7, §6.1, Fig. 6.1) → a figura basta
- [x] E11 · **Erro CONFIRMADO e corrigido na raiz** (2026-09-10). A §5.5 estava certa. A
      lista vigiada tem **doze** empresas (`config/alerts.yaml`) e o
      `evaluate_decomposition.py` percorre `sorted(SECTOR_OF)`, que tem **dezassete**; o
      artefacto reporta «Tickers decompostos: 17» e «R² ≤ 0: 1 de 17».
      **⚠️ A RAIZ ERA O ARTEFACTO, e é por isso que a correção não parou no `.tex`:** a
      secção 2 do relatório chamava-se «A watchlist toda» e o docstring do gerador dizia
      «medida sobre a watchlist implantada», enquanto os dois decompõem 17. A designação
      errada propagou-se para **dois** sítios do Cap. 4 e para a etiqueta da própria porta
      (`check_tese_numeros`: «R2 mediano sobre a watchlist»). Corrigidos os quatro. Corrigir
      só a tese deixaria a regeneração seguinte a reintroduzir o erro.
      **⚠️ E DOIS ACHADOS PELO CAMINHO, o primeiro com dano.** O
      `evaluate_decomposition.py` **não tinha um único `add_argument`**: o `--out` que lhe
      passei numa verificação foi ignorado em silêncio e a corrida escreveu por cima do
      artefacto congelado **com números diferentes** — o caso trabalhado passou de AMD
      `+6,2944%` a META `+6,3486%`, porque é escolhido como o maior movimento do **dia em
      que o script corre**. Reposto do git, byte-intacto. A regra do *brief* («usar `--out`
      em qualquer verificação») **não era seguível** neste script; passou a ser.
      E o docstring afirmava «Nao toca em nada congelado», o que é **falso**: a §5.5 cita
      dele `0,460`, `0,487` e o exemplo da AMD. Uma afirmação dessas no topo de um script
      autoriza precisamente a corrida que causa o dano.
- [ ] E12 · **Erro:** aritmética dos votos em §5.6.5 (81−10−29−5 = 37, não 42) — reordenar
- [x] E13 · **RETIRADA: a premissa é falsa** (verificado a 2026-09-10). A `fig:av_triagem`,
      que está **na própria §5.4.2**, já desenha as **seis** famílias — `0,378`, `0,439`,
      `0,469`, `0,496`, `0,538` e `0,542` — com os intervalos ao lado. O valor não está «só
      na Tab. 5.4»: está no visual da subsecção que a tarefa queria corrigir.
      **⚠️ E ESCREVI A FRASE ANTES DE VER.** Acrescentei ~40 palavras a nomear em prosa os
      dois valores que a figura ao lado desenha, e revertei. É o defeito que a sessão 66
      documentou («o defeito não era falta de estrutura: era a prosa a reler os rótulos do
      visual ao lado»), num capítulo que tem de perder 2 816 palavras.
      **⚠️ E a minha busca estava cega, duas vezes.** Procurei `0{,}469` e a figura escreve
      `(0.469,gbm)` — coordenadas TikZ usam **ponto**, que é a mesma cegueira vírgula/ponto
      que o Z1 corrigiu na porta dos números, esta vez na minha procura. E a primeira
      verificação da figura usou a âncora `fig:av_triagem` em vez de `label{...}`, apanhando
      uma **remissão** anterior e portanto o bloco de outra figura.
      **O que fica de verdadeiro na tarefa:** nada a fazer na §5.4.2. Se a prosa dela vier a
      ser reescrita, a regra é a inversa da que o E13 propunha — **não** reenumerar os seis
      valores, porque a figura os mostra.
- [ ] E14 · Uniformizar «conjunto de dados» vs «bloco de treino/validação/teste» em todo o documento
- [ ] E15 · Antecipar a nota que explica F1 0,516 vs 0,530 e amplitude 0,015 vs 0,017
- [ ] E16 · Parágrafo-mapa na abertura de §5.4.5
- [ ] E17 · Reescrever a abertura de §5.6.5 sem a percentagem em destaque
- [ ] E18 · Subdividir ou numerar §5.6.1 (cinco argumentos interlaçados)

## FASE F — Visuais

- [ ] F1 · «Onde entra a IA no sistema» (nova §3.7)
- [ ] F2 · Curvas de precisão-cobertura em §5.4.2 (existem nos artefactos, não no documento)
- [ ] F3 · Linha do tempo: 353 min / 5 s / 8 dias (§4.6)
- [ ] F4 · Histogramas do deslocamento da volatilidade, treino vs teste (§5.6.3)
- [ ] F5 · Curva do peso do encolhimento w(SE) (§3.4)
- [ ] F6 · Figura de capa: alerta real ao lado do ecrã da corretora (§1.2)
- [ ] F7 · Crescimento da base de casos (§4.6.1)
- [ ] F8 · Tornar a Figura 3.4 real, com os pares já citados (cos +0,956 / −0,086)
- [ ] F9 · Figuras novas da QI4 (depende da Fase C)

## FASE G — Revisão profunda do texto

> Só depois de C e D, para não rever duas vezes.

- [ ] G1 · Variação de comprimento de frase, documento inteiro
- [ ] G2 · Primeira pessoa em 3–4 momentos escolhidos (§5.4.4, §4.6.1, §4.3.2, §6.6)
- [ ] G3 · Desfazer nominalizações onde o verbo serve
- [ ] G4 · Precisar a frase sobre redação em §3.8.4
- [ ] G5 · Agradecimentos: frase «uma dessas conversas», parágrafo da família, tratamento do coorientador
- [ ] G6 · Decidir o título (depende do desfecho da Fase C)
- [ ] G7 · Revisão palavra a palavra, capítulo a capítulo, preservando a voz

## FASE Z — Garantias por fechar ANTES de escrever (achados de 2026-09-10)

> Estes dois não estavam em lista nenhuma e são pré-requisitos da reescrita: são a rede que
> distingue um número com fonte de uma gralha. Corrigi-los depois de escrever é descobrir os
> defeitos com o documento já montado.

- [x] Z1 · **A porta «todo o número tem origem» estava cega aos decimais da árvore canónica.**
      **FECHADO a 2026-09-10.** O `auditar_numeros.py` extraía `\d+\.\d{2,}` (ponto) e a tese
      escreve `$2{,}173$` (vírgula, exigida por outra porta). Declarava «todos têm origem» depois
      de examinar **60** números; passa a examinar **263**.
      Quatro correções, e a segunda só apareceu porque a primeira não bastava:
      (a) o extrator vê `$N{,}NNN$` e normaliza para a forma com ponto;
      (b) **as fontes também são normalizadas** — os relatórios de `docs/design/` são Markdown em
      português e escrevem 148 decimais com vírgula, logo corrigir só o lado da tese tinha movido
      o defeito em vez de o fechar;
      (c) `docs/design/*.md` e `*.json` entram nas fontes, porque é lá que vive a QI4 e sem isso a
      porta acusaria o capítulo mais recente por um defeito que era dela;
      (d) **reconhecimento de arredondamento**: o relatório de colapso publica `0,9936` e a tese
      imprime `0{,}994`. São o mesmo valor, e exigir a cadeia exata reportava quatro números do
      diagnóstico de degeneração como sem fonte — que é precisamente a evidência que torna a QI4
      um resultado e não uma montagem falhada.
      **Triagem dos sete que restaram:** nenhum era defeito. Quatro são aritmética que a tese faz
      à frente do leitor (`0,143` = 0,632−0,489; `0,336` = 0,968−0,632; `0,235` = 0,378×0,622;
      `0,289` = o desvio da uniforme que a construção passou a produzir), um é calculado no
      exemplo trabalhado (`2,725`, o σ da Tesla), e dois **não são afirmações** — são o formato da
      linha do alerta (`2,11` e `1,71`). Cada um com a razão escrita em `JUSTIFICADOS`.
      **Duas justificações retiradas** por o próprio verificador as acusar de já não corresponderem
      a nada: `3.11` e `3.12` ganharam fonte quando `docs/design/` entrou.
      **Controlos nas duas metades, todos verificados:** um valor inventado dispara; um **vizinho**
      de um valor publicado dispara (`0,995` contra `0,9936`) — é o controlo que garante que o
      remédio não trocou cegueira por permissividade; um arredondamento legítimo não dispara; e o
      corpus real não dispara. ⚠️ **E o meu primeiro controlo falhou por minha culpa:** plantei
      `0,101` do registo da sessão 66 e o corpus mudou desde então. Refeito com `0,102`, escolhido
      por **enumeração contra as fontes atuais**.
      **`tests/test_auditar_numeros.py`, 12 testes** — não havia um único teste sobre este
      verificador, e é por isso que a cegueira sobreviveu a uma correção da mesma classe na sessão
      63. Um deles parte se a contagem cair abaixo de 200, para a cegueira não voltar em silêncio.
      ⚠️ **E fica medida a limitação, em vez de suposta:** dos 900 valores `0,NNN`, só **429 estão
      ausentes** das fontes. Um número inventado tem ~**52%** de probabilidade de encontrar par por
      coincidência. A porta apanha os **retirados** e as gralhas na metade livre; **não** é prova
      de que todo o número foi verificado.

- [x] Z2 · **A §5.2 não era reproduzível de um artefacto fixado.** **FECHADO a 2026-09-10.**
      Eram **dois** scripts, não um: o `evaluate_anomaly.py` e o `evaluate_anomaly_ext.py`, e o
      segundo é o que produz o `0,269` do Isolation Forest e o `0,280` do Local Outlier Factor que
      a dissertação cita. Iam ao yfinance ao vivo, e o `_ext` tinha por baixo uma cadeia de cinco
      fornecedores de recurso — a mesma janela podia ser servida por fontes diferentes sem que o
      documento o dissesse.
      **⚠️ E A CAUSA DECLARADA ESTAVA ERRADA.** O `evaluation_anomaly_ext.md` dizia que o
      Isolation Forest diferia ~0,002 do congelado «porque o yfinance reajusta os fechos
      históricos a cada dividendo novo», e apresentava isso como deriva documentada e
      **irredutível**. Medido: **duas buscas da mesma janela a MINUTOS de distância devolvem
      fechos diferentes** — `6e-05` na AAPL, `4e-05` na NVDA, **zero** na TSLA. É precisão de
      *float32*, não acumulação de dividendos. Basta para virar uma decisão no limiar de um
      detetor que sinaliza uma fração fixa dos pontos, e foi o que fez o `F1` do Isolation Forest
      andar **0,271 → 0,270 → 0,269 em três corridas do mesmo dia**.
      **A série está fixada e VERSIONADA** em `data/samples/precos_qi1/` (15 séries, 751 fechos
      cada, 376 KB, `sha256` por empresa no manifesto). ⚠️ A pasta importa: `data/**` está
      gitignored e `data/prices/` tem **zero** ficheiros versionados, logo fixar lá tornava a
      corrida determinística **só nesta máquina**, o que não é reprodutibilidade.
      **Reutilizou-se o que já existia:** o `investigator/market_data/price_cache.py` foi escrito
      para isto — o docstring dele já avisava do reajuste retroativo — e nunca tinha sido aplicado
      aqui. Ganhou `retornos_log`, que **falha alto** quando falta uma série, porque uma avaliação
      sobre catorze empresas publica uma amplitude que no ecrã se lê como a de quinze.
      **✅ E FECHOU UM DESENCONTRO ENTRE ARTEFACTOS.** O `evaluation_anomaly.md` publicava
      `0,159` / `0,271` e o `_ext` `0,158` / `0,269` para a **mesma** comparação. Com a série
      fixada os dois publicam a mesma linha, que é a que a figura da tese já desenhava.
      **Nada do que a tese cita se moveu:** amplitude `0,015` / `0,344`, `F1` `0,516` / `0,218` /
      `0,530`, IF `0,269`, LOF `0,280`, EWMA `0,664` — todos byte-idênticos. O diff nos dois
      artefactos é **uma linha de conteúdo em cada**.
      Novos: `scripts/fixar_precos_qi1.py` (com `--verificar`) e
      `tests/test_precos_qi1_fixados.py` (**9 testes**), incluindo o que garante que a pasta não
      está gitignored e o que exige que os dois artefactos concordem no Isolation Forest — se
      voltarem a divergir, alguém correu um deles com `--rede`.
      ⚠️ **E apanhei-me na armadilha nº 7 a meio:** redirecionei o `--out` e não o `--fig`, e uma
      verificação escreveu por cima de uma figura versionada. Mesmo tamanho e números idênticos,
      reposta do git. **A porta `check_tese_pt` apanhou o resto**: acusou o PDF de ser anterior às
      figuras regeneradas, que é a defesa contra um PDF que não contém as figuras que declara.

- [x] Z3 · **Quatro das cinco referências integradas; a quinta é pergunta ao autor.**
      **FECHADO a 2026-09-10**, com registo em `docs/design/literatura_Z3_2026-09-10.md`.
      | etiqueta | entrada | estado |
      |---|---|---|
      | `[Fer19]` | `dang2020squawk` (IJCAI 2020, pp. 4597–4603) | ✅ Crossref campo a campo. ⚠️ **Etiqueta corrigida**: cita-se a publicação de 2020 e não o preprint de 2019 |
      | `[Fen21b]` | `feng2021hybrid` (SIGIR 2021, pp. 233–243) | ✅ Crossref. ⚠️ A página institucional **duplica** um autor; prevalecem os cinco das actas |
      | `[Nee25]` | `neela2025spa` (arXiv 2512.15008) | ✅ conferida à mão; **preprint, sem revista** — e o texto di-lo |
      | `[Cha22c]` | `chan2022deeptrust` (arXiv 2203.08144) | ✅ conferida à mão; **dissertação de mestrado**, e o texto di-lo |
      | `[Cor21]` | — | ⚠️ **ABERTO, e não se inventa.** A etiqueta e «relevância sem anotação humana» não identificam uma publicação, e os documentos da pesquisa não estão neste *checkout*. **Pergunta ao Henrique: o título ou a ligação.** |
      **⚠️ E O QUE ESTAS QUATRO OBRIGARAM A RETIRAR É O MAIS IMPORTANTE.** A §2.9 afirmava que os
      componentes académicos «nunca» tinham sido integrados num sistema em funcionamento contínuo
      contra fontes reais. É uma afirmação de **ausência universal**, a classe mais atacável que
      existe, e três destes trabalhos mostram-na demasiado forte. Passa a dizer que os trabalhos
      revistos **delimitam** a contribuição e não demonstram ausência de sistemas comparáveis.
      **E concede que «explicar sem prever» é opção partilhada** com o DeepTrust e o SPA — o que
      é o título da dissertação. Verificado antes de aceitar: **nenhum outro sítio** reivindica
      essa opção como novidade ou prioridade (procurado no Cap. 1, Cap. 6 e *front matter*), logo
      a concessão não abre contradição interna.
      **O acrescento do §6.5 respeita a regra da Fase B:** o trabalho de Feng «oferece uma
      formulação a explorar» e o benefício sob o orçamento diário **continua por medir**. Não diz
      que o B6 foi feito.
      **PORTAS: `verify_bibliography` 103/103 sem achados · as duas árvores a 0 erros e 0
      referências por resolver · overfull 6 e 4, iguais ao registo anterior às edições · 141
      páginas antes e depois · paridade PT↔EN 0 assimetrias em 139 chaves, com os dois controlos
      a disparar · `check_entrega` verde nos 23 · 1195 testes · `ruff` limpo.**
      ⚠️ **E uma leitura errada minha, apanhada a medir:** a porta disse «105 de 120 páginas»
      antes e «116 de 120» depois, o que se lê como onze páginas por vinte e sete linhas de
      texto. Não é — a primeira leitura veio do `main.pdf` da **raiz**, que estava obsoleto. É a
      armadilha nº 1 do *brief*, e o efeito real destas edições na contagem física é **zero**.

## FASE H — Validação

- [ ] H1 · Releitura integral como orientador
- [ ] H2 · Releitura integral como elemento do júri
- [ ] H3 · Correr toda a suite `check_*.py` e `verify.sh` — tudo verde
- [ ] H4 · Paridade bilingue com `tese-eng/`
- [ ] H5 · Reconstruir a matriz de evidência (Tab. A.2) com as afirmações novas
- [ ] H6 · Verificação final de números: `check_tese_numeros.py`, `auditar_numeros.py`
- [ ] H7 · Classificação final CRÍTICO / IMPORTANTE / MELHORIA do que restar
