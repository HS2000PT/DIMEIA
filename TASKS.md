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

- [ ] A12.1 · Integrar o corpo Muntermann ([Mun04], [Mun04b], [Mun05], [Mun05b], [Mun07], [Mun09])
      em §2.2 e reformular a lacuna face à literatura, não só aos produtos
- [ ] A12.2 · [Oh07] *Financial market monitoring by case-based reasoning* e [But91] em §2.6
- [ ] A12.3 · [Liu23d] *Alert for Alerts*, [Ell20], [Arn19b] em §2.1 — o efeito medido dos alertas
      no investidor de retalho, mesmo que complique a premissa fundadora
- [ ] A12.4 · [Ber23] (contraevidência), [Dav21], [Cau23b], [Waa21], [Kim24], [Kim24b] em §2.7 e §6.4.
      [Waa21] justifica empiricamente a opção por explicação baseada em casos, hoje sem apoio
- [ ] A12.5 · [Nee25] SPA, [Cha22c] DeepTrust, [Fer19] Squawk Bot em §2.2 — sistemas próximos e como diferem
- [ ] A12.6 · [Fen21b] SIGIR em §6.5 — a direção técnica 2 deixa de ser especulativa
- [ ] A12.7 · [Cor21] em §3.6/§5.4 — relevância de notícias sem anotação humana
- [ ] A12.8 · Reconstruir a Tabela 2.3 e reavaliar a afirmação de lacuna da §2.9

## FASE B — Fechar as lacunas que a própria tese nomeia

- [ ] B1 · Linha de base BM25 na recuperação — §5.3.2 diz que é «a que tornaria esta conclusão mais forte»
- [ ] B2 · Intervalos de confiança por setor em §5.3 (hoje a §5.4 tem reamostragem e a §5.3 não tem nada)
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

### C1e — ACHADO NOVO: o corpus da avaliação preliminar não existe

- [ ] C1e.1 · **`data/finnhub_news.csv` não está em lado nenhum.** É o corpus das 3 714
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
- [ ] C2 · Protocolo de construção de pares — declarado como decisão, com alternativas medidas
- [ ] C3 · Teste anti-lookahead do construtor de pares (TDD, antes da lógica)
- [ ] C4 · Braço de **controlo** — codificador de domínio + objetivo de semelhança que lhe falta.
      Despromovido de contribuição a controlo: o FinBERT2 (KDD 2025) já mostrou que resulta
- [ ] C5 · Braço **principal** — ajuste contrastivo por materialidade comparável (`|impacto|`,
      nunca direção). Ajustar **o codificador**, não uma cabeça sobre embeddings congelados —
      é a limitação declarada de [Jeong26] e é o que faz disto extensão e não repetição
- [ ] C5b · Braço de **replicação** — a mesma montagem com retorno **com sinal**, reproduzindo
      [Jeong26] no arnês desta tese. **A comparação magnitude vs. direção é o resultado da QI4**
- [ ] C6 · Avaliar os três no arnês idêntico; ablações; intervalos por reamostragem
- [ ] C7 · Redigir a QI4: pergunta, protocolo, resultado, e o que dele não decorre
- [ ] C8 · Atualizar §1.3, §1.4, Cap. 2, §3.5, Cap. 5, Cap. 6 e a matriz de evidência

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
- [ ] E11 · **Erro:** mediana de R² — §4.5.2 diz «lista vigiada», §5.5 diz «17 do mapa de setores»
- [ ] E12 · **Erro:** aritmética dos votos em §5.6.5 (81−10−29−5 = 37, não 42) — reordenar
- [ ] E13 · **Erro:** PR-AUC 0,469 das árvores só existe na Tab. 5.4 — pôr em §5.4.2
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

## FASE H — Validação

- [ ] H1 · Releitura integral como orientador
- [ ] H2 · Releitura integral como elemento do júri
- [ ] H3 · Correr toda a suite `check_*.py` e `verify.sh` — tudo verde
- [ ] H4 · Paridade bilingue com `tese-eng/`
- [ ] H5 · Reconstruir a matriz de evidência (Tab. A.2) com as afirmações novas
- [ ] H6 · Verificação final de números: `check_tese_numeros.py`, `auditar_numeros.py`
- [ ] H7 · Classificação final CRÍTICO / IMPORTANTE / MELHORIA do que restar
