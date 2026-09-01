# Repository index — InvestiGator 🐊

> ⛳ **PRIORIDADE MÁXIMA: ler `PLANO_FINAL_2026-09-01.md` na raiz de `DIMEIA/` antes de tocar em seja o que for.** Criado a 2026-09-01. Manda sobre este ficheiro e sobre todos os outros planos do repositório, incluindo `progress/PLANO_FINAL_ENTREGA.md`, `progress/PLANO_EMERGENCIA_DEFESA_2026-08-30.md` e `INVESTIGATOR_MASTER_PLAN.md`, que ficam como registo histórico.

A map of where everything lives, so you can navigate the project at a glance. For a 10-minute
written overview of the whole project, read **[`RELATORIO_FINAL.md`](RELATORIO_FINAL.md)**.

---

## Start here

| What | Where |
|------|-------|
| **The dissertation (English)** | [`thesis/main.pdf`](thesis/main.pdf) |
| **A dissertação (Português)** | [`thesis-pt/main.pdf`](thesis-pt/main.pdf) |
| **Project overview + how to run** | [`README.md`](README.md) |
| **10-minute written summary** | [`RELATORIO_FINAL.md`](RELATORIO_FINAL.md) |
| **The live product** | [`api/main.py`](api/main.py) + [`web/`](web/) — the v5 service and client, served by the `Procfile`. The Streamlit generations in `app/` are kept as a record and are no longer served |
| **The intelligence layer** | [`investigator/intelligence/`](investigator/intelligence/) — evidence bundles, grounded report, analyst, and the fidelity guard |

---

## The dissertation

| Item | Where |
|------|-------|
| English source (chapters, front matter, appendix) | [`thesis/`](thesis/) — `ch1/`…`ch6/`, `frontmatter/`, `appendices/` |
| Portuguese source (faithful translation, kept in sync) | [`thesis-pt/`](thesis-pt/) |
| Reproducible figures (scripts → PDF) | [`scripts/figures/`](scripts/figures/) → `thesis/figures/` |
| IEEE paper (distilled from the thesis) | [`paper/main.pdf`](paper/main.pdf) |
| Defence slides (short deck) | [`slides/main.pdf`](slides/main.pdf) |
| Study guide (teaches the thesis from zero, PT-PT) | [`slides/guia_estudo/`](slides/guia_estudo/) |
| **Personal cheat sheet (PT-PT) — open this first before the defence** | [`docs/defence/guia_pessoal.md`](docs/defence/guia_pessoal.md) |
| **Every number → origin, calculation, code:line, data, thesis section (PT-PT)** | [`docs/defence/THESIS_FACT_SHEET.md`](docs/defence/THESIS_FACT_SHEET.md) |
| **Question → simple answer → technical answer → where to prove it (PT-PT)** | [`docs/defence/DEFENSE_QA.md`](docs/defence/DEFENSE_QA.md) |
| **Graduated course, zero AI knowledge → defence (8 levels, phone, offline)** | [`study/index.html`](study/index.html) |
| Self-test app (48 questions, phone, works offline) | [`quiz/index.html`](quiz/index.html) — quick recall only; the course above is the one to learn from |

---

## The product (the running system)

| Item | Where |
|------|-------|
| Web service (v5) | [`api/main.py`](api/main.py) · [`api/services.py`](api/services.py) |
| Web client (v6) | [`web/index.html`](web/index.html) — um ficheiro, três secções. A v5 (nove rotas, relatório gerado, 48 KB de JS) foi retirada |
| Grounded generation | [`context.py`](investigator/intelligence/context.py) · [`guard.py`](investigator/intelligence/guard.py) · [`report.py`](investigator/intelligence/report.py) · [`analyst.py`](investigator/intelligence/analyst.py) |
| Dashboard (Streamlit, superseded) | [`app/dashboard_v4.py`](app/dashboard_v4.py) · [`snapshot_io.py`](app/snapshot_io.py) · [`method.py`](app/method.py) · [`verdict.py`](app/verdict.py) |
| Alert runner (scan → detect → explain → Telegram) | [`scripts/run_alerts.py`](scripts/run_alerts.py) |
| Configuration (watchlist, thresholds) | [`config/alerts.yaml`](config/alerts.yaml) |
| Scheduled scan (GitHub Actions, after US close) | [`.github/workflows/`](.github/workflows/) |

---

## The code — `investigator/` package

| Module | Responsibility |
|--------|----------------|
| [`market_data/`](investigator/market_data/) | Price fetching (fallback chain) and market-hours / exchange status |
| [`anomaly_detector/`](investigator/anomaly_detector/) | Rolling z-score detection of abrupt moves (no look-ahead) |
| [`news_fetcher/`](investigator/news_fetcher/) | News ingestion (Finnhub, RSS) and relevance filtering |
| [`historical_kb/`](investigator/historical_kb/) | Precedent knowledge base and the embedders (Hashing / SBERT / ONNX) |
| [`correlation_engine/`](investigator/correlation_engine/) | Event-study impact and cosine-similarity retrieval |
| [`explanation_engine/`](investigator/explanation_engine/) | Builds the explainable alert text |
| [`triage/`](investigator/triage/) | Materiality-triage model (RQ4) and inference |
| [`narrator/`](investigator/narrator/) | Grounded narration: the LLM writes the language, never the facts, behind a runtime faithfulness guard |
| [`convergence.py`](investigator/convergence.py) | Multi-signal fusion (measured, not wired to production) |
| [`evaluation/`](investigator/evaluation/) | Offline evaluation and live-monitoring metrics |
| [`telegram_bot/`](investigator/telegram_bot/) | Telegram delivery and the interactive bot |
| **Tests** | [`tests/`](tests/) — the automated suite (`pytest`) |

Single-file modules in the package root: `main.py` (entry points for both triggers),
`config.py` (environment/secrets), `alerts_history.py` (the shared record the app mirrors),
`gate_log.py` (which gate stopped each ticker), `live_kb.py` (the growing case base),
`convergence.py` (multi-signal fusion, measurement layer),
`settings_overrides.py` (safe live tunables), `console.py`.

---

## Documentation — `docs/`

| Area | What's there |
|------|--------------|
| [`docs/README.md`](docs/README.md) | Full documentation index |
| [`docs/design/`](docs/design/) | How to run, setup, deployment, architecture, data card |
| [`docs/evaluation/`](docs/evaluation/) | Results (generated by scripts, not edited by hand) |
| [`docs/decisions/`](docs/decisions/) | Rationale, learning notes, glossary, citation log |
| [`docs/defence/`](docs/defence/) | Defence rehearsal pack, demo script, message to the supervisor |
| [`docs/study/`](docs/study/) | Materials for the human usefulness study (stimuli, counterbalancing, response sheet) |

---

## Running it yourself

| Item | Where |
|------|-------|
| Windows one-click launchers | [`run/`](run/) |
| Always-on deployment (systemd units, VM setup) | [`deploy/`](deploy/) |
| End-to-end walkthrough notebook | [`notebooks/`](notebooks/) |
| Dashboard theme | [`.streamlit/config.toml`](.streamlit/config.toml) |
| What is still outstanding | [`CHECKLIST.md`](CHECKLIST.md) |
| How to cite this software | [`CITATION.cff`](CITATION.cff) |

---

## Data & models

| Item | Where |
|------|-------|
| Sample data (small, versioned) | [`data/samples/`](data/samples/) |
| Trained triage models (small, versioned) | [`models/`](models/) |
| Requirements (light / ML / app) | `requirements.txt`, `requirements-ml.txt`, `requirements-app.txt` |

> Large corpora, secrets and downloaded models are never versioned — they are regenerated by the
> data scripts. Working notes used while building the project live in `progress/` and `CLAUDE.md`.
