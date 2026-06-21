# data_card.md — Cartão de dados (reproduzível)

> Fonte, licença, atribuição, subconjunto exato de tickers e janela temporal escolhidos, e cada decisão de
> pré-processamento/limpeza (para o dataset ser reproduzível).

## FNSPID (camada histórica)
- **Fonte:** Hugging Face `Zihan1004/FNSPID`; repo `Zdong104/FNSPID_Financial_News_Dataset`.
- **Licença:** **CC BY-SA 4.0** — atribuição obrigatória no README e na tese.
- **Referência:** Dong, Fan & Peng (2024), arXiv:2402.06698 (`dong2024fnspid`).
- **Ficheiro de notícias (verificado 2026-06-21):** `Stock_news/nasdaq_exteral_data.csv` —
  HTTP 200, `text/csv`, **~23,2 GB** (daí o streaming). Colunas:
  `Unnamed: 0, Date, Article_title, Stock_symbol, Url, Publisher, Author, Article,
  Lsa_summary, Luhn_summary, Textrank_summary, Lexrank_summary`. Mapeamento interno:
  `Date→date`, `Stock_symbol→ticker`, `Article_title→headline`.

### Subconjunto escolhido (default proposto — ajustável pelo aluno)
Para ser tratável num portátil (§5.4 / R2), começamos com um subconjunto pequeno e representativo:
- **Tickers (15, large-cap US, multissetorial):** AAPL, MSFT, AMZN, GOOGL, NVDA, TSLA, META, JPM, BAC, XOM,
  CVX, JNJ, PFE, WMT, KO.
  - Racional: cobre tecnologia, banca, energia, saúde e consumo → permite o cenário de "impacto setorial"
    (ex.: notícia da Tesla → outras de tecnologia/EV) sem o peso das ~4.775 empresas do dataset.
- **Janela temporal:** **2018-01-01 a 2023-12-31** (6 anos; o FNSPID vai até 2023). Recente o suficiente para ser
  relevante e suficientemente longo para ter precedentes.
- **Granularidade:** diária (notícias com data; preços de fecho diários).

### Pré-processamento (implementado em `download_data.py` + `build_kb.py` + `src/historical_kb/`)
- `scripts/download_data.py`: lê o CSV de notícias do FNSPID **em streaming** (chunks, sem descarregar os
  ~dezenas de GB), normaliza colunas (`date, ticker, headline`), filtra por ticker e janela, grava o
  subconjunto em `data/fnspid_news_subset.csv` (gitignored) e uma amostra de títulos em `data/samples/`.
- `scripts/build_kb.py`: junta o subconjunto às cotações de fecho (yfinance, índice tz-naive) e constrói a KB:
  para cada notícia guarda `data, ticker, título, impacto pós-evento (+1/+3/+5d), embedding`. Grava JSONL.
- **Alinhamento evento↔preço:** dia do evento = 1.º dia de negociação **>= data da notícia** (`searchsorted`);
  impacto medido a partir do **fecho** desse dia (evita captar o salto já refletido na abertura — ver
  `learning.md` §11). Impacto via `src/correlation_engine/event_study.py` (nota anti-lookahead aí).
- **Embedder:** `HashingEmbedder` (baseline determinístico, default) ou `SbertEmbedder` (SBERT, com `--sbert`).
- Notícias sem cotações para o ticker, ou cuja data ultrapassa a série, são descartadas (sem impacto observável).

> **Estado:** pipeline **implementado e validado** ponta-a-ponta com a amostra sintética
> `data/samples/news_sample.csv` + cotações reais (yfinance) → `data/samples/kb_sample.jsonl` (10 registos,
> impactos coerentes com a realidade). O `SbertEmbedder` foi validado e usado para a KB real do Finnhub
> (3.692 notícias). O aluno pode ajustar tickers/janela; a metodologia não muda (decisão autónoma, D-009).

### Download do FNSPID — correção e viabilidade (S17)
- **Correção (bug real):** `download_data.py` passou a fazer *stream* via `requests` — `pd.read_csv(url)`
  **bloqueava** neste endpoint do Hugging Face. Acrescentado: leitura de só 3 colunas (`usecols`) e
  **paragem antecipada** por ordenação de ticker (`early_stop`). **Verificado**: extraiu 379 notícias da
  Agilent (ticker `A`) 2018-2023 e parou cedo, corretamente.
- **Viabilidade:** débito ~1.300 linhas/s; ~15M linhas → **~3,4 h para varrer tudo**. Como os 15 tickers vão
  de `A` a `X`, não há atalho por ordenação. **Não é praticável neste ambiente**; é um job para correr numa
  máquina/ligação adequada (ex.: durante a noite): `python scripts/download_data.py` →
  `python scripts/build_kb.py --news data/fnspid_news_subset.csv --sbert`.
- **Decisão honesta:** a avaliação (Cap. 6) usa a KB **real do Finnhub** (3.692 notícias, multi-seed); a KB
  multi-ano do FNSPID fica como **trabalho futuro reprodutível** (script pronto e verificado).

## Camada live
- **Preços:** yfinance (base) + Finnhub (fallback). **Notícias:** Finnhub news + RSS (ver `free_apis.md`).
- Tratamento: mesmos campos da camada histórica para permitir comparação por similaridade.

### Conjunto de avaliação preliminar (Finnhub, S11)
- `scripts/fetch_finnhub_news.py` recolheu **3.692 notícias reais** dos 15 tickers (Finnhub
  `/company-news`, ~250 recentes por ticker; gitignored em `data/finnhub_news.csv`, amostra em
  `data/samples/`). Usado pela avaliação da recuperação (`scripts/evaluate.py` →
  `docs/evaluation_results.md`). **É real mas recente** (não o histórico multi-ano do FNSPID, que
  continua a ser a fonte mais rica para a avaliação final).

## Governança (ambas as camadas)
- Dados grandes **gitignored** e recriados por `scripts/download_data.py`; só **amostras pequenas** em
  `data/samples/`. **Não republicar** texto integral de notícias de terceiros na tese — citar minimamente (§5.4).
