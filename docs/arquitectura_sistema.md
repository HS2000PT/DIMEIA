# arquitectura_sistema.md — Arquitetura técnica do sistema

> **Fase C.** Arquitetura detalhada (diagrama textual de componentes + as duas camadas de dados).
> Princípio orientador: **XAI-first** (toda a lógica exposta e rastreável) e **simplicidade defensável** (§5.5).
> Conceitos novos explicados em PT-PT em `docs/learning.md`. Justificação académica detalhada das metodologias
> e citações verificadas entram na tarefa seguinte da Fase C (metodologias) e em `docs/citation_log.md`.

## 1. Visão geral
O sistema gera **alertas financeiros explicáveis** para investidores de retalho no mercado US (NYSE/NASDAQ),
acionados por **dois gatilhos independentes**:
1. **Movimento abrupto de mercado** (anomalia estatística num ativo) → alerta + explicação.
2. **Nova notícia financeira** → alerta + impacto potencial + **precedentes históricos** análogos.

O **núcleo** é o *motor de correlação notícia–mercado*: dada uma notícia, recupera notícias históricas
semelhantes (FNSPID) e mede o impacto que tiveram nos preços, usando-as como **evidência explicativa**.

## 2. Duas camadas de dados (NÃO confundir)
```
┌──────────────────────────────────────────────────────────────────────────┐
│ CAMADA HISTÓRICA (offline, batch) — construir a base de conhecimento       │
│   FNSPID (Zihan1004/FNSPID, CC BY-SA 4.0)                                  │
│     → subconjunto de tickers + janela temporal (data_card.md)             │
│     → para cada notícia: texto + data + ticker + impacto observado nos     │
│       preços (janelas pós-notícia: +1d, +3d, …) e embedding do texto       │
│     → índice de similaridade (vetores) consultável                        │
│   Construída por: scripts/download_data.py + src/historical_kb/           │
├──────────────────────────────────────────────────────────────────────────┤
│ CAMADA LIVE (online, tempo real) — acionar os gatilhos                     │
│   Preços: yfinance (base) [+ Finnhub/Alpha Vantage a confirmar — Fase C]  │
│   Notícias: RSS financeiro / Finnhub / GNews (free tier — a confirmar)    │
│   Alertas: Telegram Bot API (gratuito)                                     │
│   Servida por: src/market_data/, src/news_fetcher/, src/telegram_bot/     │
└──────────────────────────────────────────────────────────────────────────┘
```
> **Porque o histórico vem do FNSPID e não de APIs de notícias:** os free tiers de APIs de notícias dão
> tipicamente só ~30 dias, são "development-use" e atrasados → não servem para construir histórico. (Confirmar
> limites na tarefa de APIs da Fase C — `free_apis.md`.)

## 3. Diagrama de componentes (textual)
```
                         ┌───────────────────────────┐
        GATILHO 1        │   src/market_data (LIVE)  │
   (movimento abrupto)   │   preços OHLCV (yfinance)  │
                         └─────────────┬─────────────┘
                                       ▼
                         ┌───────────────────────────┐
                         │  src/anomaly_detector     │  z-score de retornos vs.
                         │  (estatística transparente)│  média/desvio móveis
                         └─────────────┬─────────────┘
                                       │ anomalia + contexto
                                       ▼
        GATILHO 2        ┌───────────────────────────┐     ┌────────────────────────┐
   (nova notícia)        │  src/correlation_engine   │◄────│ src/historical_kb       │
 ┌────────────────┐      │  embeddings + similaridade │     │ (FNSPID: embeddings +   │
 │ src/news_fetcher│────►│  → precedentes + impacto   │     │  impacto pré-calculado) │
 │   (LIVE)        │      │    (event-study)          │     └────────────────────────┘
 └────────────────┘      └─────────────┬─────────────┘
                                       │ precedentes + impacto medido
                                       │           (opcional) ▼
                                       │            ┌────────────────────────┐
                                       │            │ src/impact_analyzer    │ tickers do mesmo
                                       │            │ (impacto setorial)      │ setor (OPCIONAL)
                                       │            └───────────┬────────────┘
                                       ▼                        │
                         ┌───────────────────────────┐         │
                         │  src/explanation_engine   │◄────────┘
                         │  (XAI: regras + precedentes│
                         │   + atribuição opcional)  │
                         └─────────────┬─────────────┘
                                       │ alerta + explicação + fontes + precedentes
                                       ▼
                         ┌───────────────────────────┐
                         │  src/telegram_bot (LIVE)  │  → utilizador
                         └───────────────────────────┘

           Orquestração: src/main.py   ·   Configuração/segredos: .env
```

## 4. Componentes (responsabilidade · entrada → saída · método simples e defensável)
- **market_data** — obter preços OHLCV recentes de tickers US. `ticker, janela → série de preços/retornos`.
  Método: `yfinance` (base). Sem previsão de preços.
- **news_fetcher** — obter notícias financeiras recentes relevantes. `→ {título, texto, data, tickers}`.
  Método: RSS/Finnhub/GNews (a confirmar). Só para o gatilho live (nunca para histórico).
- **historical_kb** — base de conhecimento histórica a partir do FNSPID. Para cada notícia histórica guarda
  `texto, data, ticker, embedding, impacto(+1d/+3d/…)`. Expõe consulta por similaridade. Construída offline.
- **anomaly_detector** — detetar movimento abrupto. `retornos → é_anomalia? + score (z-score)`.
  Método: **z-score** dos retornos vs. média/desvio-padrão **móveis** (rolling). Transparente = vantagem XAI.
  (Só subir para algo como Isolation Forest se academicamente justificado — §5.5.)
- **correlation_engine (núcleo)** — dada uma notícia (ou o contexto de uma anomalia), recuperar precedentes
  históricos análogos e medir o seu impacto. `notícia → top-k precedentes + impacto observado`.
  Método: **embeddings** de frases (modelo open-source) + **similaridade do cosseno**; impacto via
  **event-study** (retorno a +1d, +3d, …). Janela e métrica documentadas = parte da contribuição.
- **impact_analyzer (OPCIONAL)** — identificar tickers do mesmo setor historicamente afetados por notícias
  análogas. Cortável sem prejuízo (§5.3).
- **explanation_engine (XAI)** — montar a explicação rastreável. Combina (i) regras/heurísticas transparentes,
  (ii) os precedentes recuperados como evidência, (iii) opcionalmente atribuição (ex.: SHAP) sobre o detetor.
  `evento + evidências → texto explicativo passo a passo + fontes`.
- **telegram_bot** — enviar o alerta final (evento + explicação + fontes + precedentes) via Telegram Bot API.
- **main.py** — orquestrar os dois fluxos; agendar polling da camada live; aplicar configuração de `.env`.

## 5. Fluxos end-to-end (os dois gatilhos)
**Gatilho 1 — anomalia de mercado:** `market_data → anomaly_detector` deteta o movimento → `correlation_engine`
procura notícias/precedentes que coincidam no período → `explanation_engine` explica (causas prováveis +
contexto histórico) → `telegram_bot` alerta.

**Gatilho 2 — nova notícia:** `news_fetcher` capta a notícia → `correlation_engine` recupera precedentes
históricos análogos (FNSPID) e mede o impacto observado → (`impact_analyzer` opcional para o setor) →
`explanation_engine` apresenta impacto potencial + exemplos concretos → `telegram_bot` alerta.

## 6. Thin slice (primeira fatia fina end-to-end — §5.3, ~Sessão 10)
**Gatilho 1, mínimo:** `market_data` (1 ticker, yfinance) → `anomaly_detector` (z-score simples) →
`explanation_engine` (explicação mínima baseada em regra) → `telegram_bot` (1 alerta real).
Sem correlação/precedentes ainda. Valida o caminho completo e o `tests/test_smoke.py` real.

## 7. Garantias transversais
- **Sem lookahead (§6.5):** features num instante nunca usam dados do futuro; o impacto histórico usa apenas
  janelas **pós-evento** bem definidas. Documentado e testado.
- **Rastreabilidade (XAI):** cada alerta guarda as entradas, a regra/medida aplicada e as fontes — o utilizador
  vê 100% como se chegou à conclusão.
- **Reprodutibilidade (§7):** seeds fixas; dados grandes recriados por `download_data.py`; dependências fixadas.
- **Sem fabricação (§2.2/§6.4):** nenhum número ou citação inventado; métricas só as reproduzíveis.

## 8. Decisões em aberto (a fechar na Fase C)
- APIs live concretas + limites verificados (`free_apis.md`).
- Modelo de embeddings concreto + métrica/janela do event-study (tarefa de metodologias).
- Subconjunto de tickers + janela temporal do FNSPID (`data_card.md`).
- Incluir ou não `impact_analyzer` (opcional) e análise de sentimento (FinBERT) — decidir por defensibilidade.

## 9. Metodologias por componente — justificação e referências (verificadas)
> Enquadramento (§3): a contribuição é de **engenharia de IA** — integrar, aplicar e avaliar criticamente
> componentes existentes. Todas as referências abaixo estão **verificadas** em `docs/citation_log.md`
> (DOI/arXiv, 2026-06-21). Entram no `references.bib` na Fase D. Princípio: **simplicidade defensável** (§5.5).

| Componente | Método escolhido | Justificação (porquê este, e não mais complexo) | Referência verificada |
|---|---|---|---|
| **Deteção de anomalias** | z-score de retornos vs. média/desvio móveis | Estatístico e **transparente** → vantagem XAI; é o baseline padrão antes de métodos opacos (Isolation Forest etc., só se justificado) | Chandola et al. (2009) — taxonomia de deteção de anomalias `chandola2009anomaly` |
| **Embeddings de notícias** | Sentence-BERT (modelo open-source), **inferência apenas** | Padrão para similaridade semântica de frases; integrar (não treinar) é o trabalho de engenharia | Reimers & Gurevych (2019) `reimers2019sbert` |
| **Correlação / precedentes (núcleo)** | Recuperação top-k por **similaridade do cosseno** + **event-study** (retornos pós-evento +1d/+3d) | Event-study com retornos diários é o método seminal e reproduzível para medir impacto; janelas/métrica documentadas = nossa contribuição; **sem lookahead** (§6.5) | Brown & Warner (1985) — event studies com retornos diários `brown1985daily` |
| **Sentimento (OPCIONAL)** | FinBERT, **inferência apenas** | Padrão de domínio citável; sinal adicional para a explicação; cortável se não acrescentar valor | Araci (2019) `araci2019finbert` |
| **Motor de explicação (XAI)** | Regras transparentes + precedentes como evidência + atribuição **SHAP** (opcional) sobre o detetor | Combinar lógica transparente com atribuição local dá explicações que o utilizador segue passo a passo | Lundberg & Lee (2017) SHAP `lundberg2017shap`; enquadramento XAI: Arrieta et al. (2020) `arrieta2020xai`, Adadi & Berrada (2018) `adadi2018peeking` |
| **Base histórica** | FNSPID (subconjunto de tickers + janela) | Notícias já alinhadas a preços → permite construir histórico sem scraping; **CC BY-SA 4.0** (atribuição) | Dong et al. (2024) `dong2024fnspid` |

> Mistura **seminal + recente** (§6.2): Brown & Warner 1985, Chandola 2009, Lundberg & Lee 2017, Adadi & Berrada
> 2018, Reimers & Gurevych 2019, Araci 2019, Arrieta 2020, Dong 2024. Tabelas comparativas de abordagens (com
> vantagens/limitações) serão construídas na revisão de literatura (fase de escrita).
