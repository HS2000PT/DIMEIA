# data_card.md — Cartão de dados (reproduzível)

> Fonte, licença, atribuição, subconjunto exato de tickers e janela temporal escolhidos, e cada decisão de
> pré-processamento/limpeza (para o dataset ser reproduzível).

## FNSPID (camada histórica)
- **Fonte:** Hugging Face `Zihan1004/FNSPID`; repo `Zdong104/FNSPID_Financial_News_Dataset`.
- **Licença:** **CC BY-SA 4.0** — atribuição obrigatória no README e na tese.
- **Referência:** Dong, Fan & Peng (2024), arXiv:2402.06698 (`dong2024fnspid`).

### Subconjunto escolhido (default proposto — ajustável pelo aluno)
Para ser tratável num portátil (§5.4 / R2), começamos com um subconjunto pequeno e representativo:
- **Tickers (15, large-cap US, multissetorial):** AAPL, MSFT, AMZN, GOOGL, NVDA, TSLA, META, JPM, BAC, XOM,
  CVX, JNJ, PFE, WMT, KO.
  - Racional: cobre tecnologia, banca, energia, saúde e consumo → permite o cenário de "impacto setorial"
    (ex.: notícia da Tesla → outras de tecnologia/EV) sem o peso das ~4.775 empresas do dataset.
- **Janela temporal:** **2018-01-01 a 2023-12-31** (6 anos; o FNSPID vai até 2023). Recente o suficiente para ser
  relevante e suficientemente longo para ter precedentes.
- **Granularidade:** diária (notícias com data; preços de fecho diários).

### Pré-processamento (a aplicar em `historical_kb`/`download_data.py`)
- Filtrar por ticker e janela acima; remover notícias sem data ou sem ticker associado.
- Para cada notícia: guardar `data, ticker, título/texto, embedding (SBERT), impacto pós-evento (+1/+3/+5d)`.
- Impacto medido por `src/correlation_engine/event_study.py` (retornos pós-evento; ver nota anti-lookahead aí).
- Seeds fixas; decisões registadas aqui à medida que forem tomadas.

> **Estado:** subconjunto **proposto** (decisão autónoma documentada, D-009). O aluno pode ajustar tickers/janela;
> a metodologia não muda. O download real (via `download_data.py`) e a construção da KB são o próximo passo (S12).

## Camada live
- **Preços:** yfinance (base) + Finnhub (fallback). **Notícias:** Finnhub news + RSS (ver `free_apis.md`).
- Tratamento: mesmos campos da camada histórica para permitir comparação por similaridade.

## Governança (ambas as camadas)
- Dados grandes **gitignored** e recriados por `scripts/download_data.py`; só **amostras pequenas** em
  `data/samples/`. **Não republicar** texto integral de notícias de terceiros na tese — citar minimamente (§5.4).
