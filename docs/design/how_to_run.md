# how_to_run.md — Como correr o CLARION (guia do operador)

> Guia prático e **honesto** de como correr o sistema de ponta a ponta. Complementa o `setup.md`
> (que trata do ambiente). Tudo aqui reflete o código real do repositório; quando algo ainda não
> tem interface de linha de comandos, é dito explicitamente.
>
> **Pré-requisito:** ambiente criado com `bash scripts/setup_env.sh` (Python 3.12, `.venv/`, **stack leve** —
> chega para a demo, os testes e as avaliações). Para a recuperação SBERT real, usar
> `bash scripts/setup_env.sh --ml` (acrescenta torch CPU + sentence-transformers).
> Correr sempre com o Python do venv: `./.venv/Scripts/python.exe` (Windows) ou `.venv/bin/python` (Linux/macOS).

---

## 0.0 Ver a app a funcionar — **1 comando, sem configurar nada**

O ponto de partida. Corre os **dois gatilhos** e mostra o resultado, **offline** (o gatilho de notícia usa
a KB de amostra; não precisa de chaves nem, para essa parte, de internet). É Windows-safe (força UTF-8).

```bash
./.venv/Scripts/python.exe scripts/demo.py
```

Saída real (determinística no gatilho de notícia):

```
==== GATILHO DE NOTICIA  (offline, base de conhecimento de amostra) ====
Alerta NVDA | impacto medio 5 dias: +6,46%
 - 2023-05-25 NVDA (sim 0.60) +5d  +3,55%  "Nvidia guidance surges..."
 - 2023-04-25 MSFT (sim 0.38) +5d +10,89%  "Microsoft cloud growth..."
 - 2023-06-13 NVDA (sim 0.38) +5d  +4,93%  "Nvidia unveils new AI..."
==== GATILHO DE MERCADO  (precos ao vivo; nao envia) ====
 No anomaly for AAPL today (z-score +0.89, within +-3).
```

> **Nota (Windows):** os alertas têm emojis (📰, ⚠️); a consola `cp1252` rebenta ao imprimi-los. A demo já
> força `UTF-8`. Se correres o teu próprio `print(...)` e vires `UnicodeEncodeError`, define
> `PYTHONIOENCODING=utf-8`.

### 0.1 Ver a app num **dashboard** (Streamlit) — clicável

Alternativa visual à demo de consola: os dois gatilhos + a avaliação, numa interface web local.

```bash
pip install -r requirements.txt -r requirements-app.txt
streamlit run app/streamlit_app.py     # abre http://localhost:8501
```

Não envia nada e não precisa de chaves. Para publicar de graça (URL público), ver
[`deployment.md`](deployment.md).

---

## 0. Segredos (`.env`) — uma só vez

O envio para o Telegram e a recolha de notícias do Finnhub precisam de chaves. **Nunca** vão para o
repositório (o `.env` está no `.gitignore`).

```bash
cp .env.example .env      # depois preencher os valores localmente
```

Campos (ver `.env.example`): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (via @BotFather),
`FINNHUB_API_KEY` e, opcionalmente, `ALPHAVANTAGE_API_KEY` / `GNEWS_API_KEY`.

> Sem `.env`, **tudo o que é offline continua a correr** (deteção, recuperação na KB-amostra, testes,
> avaliações com dados já guardados). Só falham os passos que falam com a rede (enviar Telegram, buscar
> notícias ao vivo).

---

## 1. Gatilho 1 — Movimento abrupto de mercado (anomalia)

A fatia fina (`run_thin_slice`) busca preços ao vivo de um ticker, calcula log-returns, corre o
*z*-score sobre a janela anterior e (opcionalmente) envia o alerta para o Telegram.

**Correr com os defaults (AAPL, janela 20, limiar 3):**
```bash
./.venv/Scripts/python.exe -m src.main
```
Imprime o texto do alerta/explicação e a linha `[is_anomaly=... z=...]`.

> ⚠️ O ponto de entrada `-m src.main` corre `run_thin_slice` com `send=True`, por isso **tenta enviar
> para o Telegram** e dá erro (`RuntimeError`) se o `.env` não tiver `TELEGRAM_BOT_TOKEN`/`CHAT_ID`.
> Para correr **offline** (sem enviar), usar `send=False` em Python (abaixo).

**Correr para outro ticker / parâmetros, sem enviar (em Python):**
```python
from src.main import run_thin_slice
result, text = run_thin_slice(ticker="TSLA", window=20, threshold=3.0, send=False)
print(text, result.is_anomaly, result.z_score)
```

---

## 2. Gatilho 2 — Nova notícia (precedentes + impacto)

Dada uma notícia, o sistema gera o embedding, recupera os precedentes mais semelhantes na KB e mede o
impacto observado desses precedentes. **Ainda não tem CLI**; corre-se programaticamente via
`run_news_trigger`.

**Por defeito** usa o `HashingEmbedder` (dim 64) e a KB-amostra commitada
(`data/samples/kb_sample.jsonl`) — totalmente offline e reproduzível, sem descarregar modelos:
```python
from src.main import run_news_trigger
precedents, text = run_news_trigger(
    ticker="NVDA",
    headline="Nvidia demand surges on AI chip orders",
    top_k=3, horizon=5, send=False,
)
print(text)
for rec, score in precedents:
    print(f"{score:.3f}  {rec.ticker} {rec.date}  +5d={rec.impacts.get('5'):+.2%}  {rec.headline}")
```

**Com SBERT (recuperação semântica real):** requer a stack pesada (`bash scripts/setup_env.sh --ml`
instala torch CPU + sentence-transformers) **e** uma KB construída com o mesmo embedder (ver §4). Depois:
```python
from src.main import run_news_trigger
from src.historical_kb.embedder import SbertEmbedder
precedents, text = run_news_trigger(
    ticker="NVDA", headline="...", kb_path="data/kb_sbert.jsonl",
    embedder=SbertEmbedder(), top_k=5, horizon=3, send=False,
)
```

> ⚠️ **Regra de coerência:** o embedder usado para consultar tem de ser o mesmo (mesma dimensão/modelo)
> com que a KB foi construída. A KB-amostra é dim-64 (HashingEmbedder); não a consultar com SBERT.

---

## 3. Recolher notícias ao vivo (Finnhub) — opcional

```bash
./.venv/Scripts/python.exe scripts/fetch_finnhub_news.py     # escreve CSV (date,ticker,headline)
```
Precisa de `FINNHUB_API_KEY` no `.env`. Serve de fonte para construir a KB (§4) e para a avaliação.

---

## 4. Construir a base de conhecimento (KB)

A partir de um CSV de notícias (`date,ticker,headline`), alinha cada notícia ao 1.º dia de negociação,
busca preços (yfinance), mede o impacto (+1/+3/+5d) e gera os embeddings.

**Baseline (HashingEmbedder, offline, rápido):**
```bash
./.venv/Scripts/python.exe scripts/build_kb.py --news data/finnhub_news.csv --out data/kb.jsonl
```
**SBERT (semântico, requer stack pesada):**
```bash
./.venv/Scripts/python.exe scripts/build_kb.py --news data/finnhub_news.csv --out data/kb_sbert.jsonl --sbert
```

> O FNSPID completo (multi-ano) descarrega-se com `scripts/download_data.py` (streaming + filtro por
> ticker/janela). É um trabalho longo e os dados grandes **nunca** são versionados (ver `data_card.md`).

---

## 5. Reproduzir as experiências da tese

Todos os números do Cap. 5 são gerados por scripts com seed fixa; as figuras vão direto para
`thesis/figures/`.

```bash
./.venv/Scripts/python.exe scripts/evaluate.py            # recuperação: SBERT vs baselines (multi-seed)
./.venv/Scripts/python.exe scripts/evaluate_per_sector.py # precisão por setor
./.venv/Scripts/python.exe scripts/evaluate_anomaly.py    # anomalia: taxa de disparo + ablação (janela fixada)
```

---

## 6. Testes e qualidade

```bash
bash scripts/verify.sh        # pytest (exclui @telegram e @sbert) + ruff
./.venv/Scripts/python.exe -m pytest -m telegram   # envio real ao Telegram (precisa de .env)
./.venv/Scripts/python.exe -m pytest -m sbert      # validação semântica (precisa da stack pesada)
```

---

## 7. Compilar a tese

```bash
bash scripts/build_pdf.sh     # latexmk + biber -> thesis/main.pdf (versionado)
```

---

## Limites práticos (honestos)
- O Gatilho 2 não tem CLI próprio (corre-se via `run_news_trigger`); é uma conveniência por fazer, não
  uma limitação de investigação.
- O *tier* gratuito de notícias devolve só uma janela recente → a KB ao vivo é mais rasa do que a do
  FNSPID completo (afeta cobertura, não o método).
- Não há agendador nem alojamento: cada gatilho corre um ciclo completo quando invocado. Em produção,
  um agendador chamaria estes mesmos pontos de entrada (mercado: 1×/dia após o fecho; notícias: a cada
  publicação do *feed*).
- O envio real ao Telegram foi confirmado em teste — o caminho dados → telemóvel do investidor está
  provado de ponta a ponta.
