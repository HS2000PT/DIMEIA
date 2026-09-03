<img src="app/assets/logo.svg" width="120" align="right" alt="InvestiGator — a rising market line drawn as an alligator's ridged tail">

# InvestiGator — Explainable Financial Alerts for Retail Investors

> **Project continuity — read first:** [current priority and four-attachment review](docs/planos/REVISAO_PRIORITARIA_ANEXOS.md), then [master plan](docs/planos/PLANO_FINAL_2026-09-01.md), section 0. This applies to Codex, Claude and human contributors. All dissertation figures will be remade in English for the paper; the dissertation remains Portuguese unless the author later decides otherwise. Older checklists do not override these decisions.

*Markets move. We investigate.*

**▶ Try it live: <https://investigator-ddc9d8618935.herokuapp.com>**

[![CI (tests + lint)](https://github.com/HS2000PT/DIMEIA/actions/workflows/ci.yml/badge.svg)](https://github.com/HS2000PT/DIMEIA/actions/workflows/ci.yml)
[![Compile thesis (LaTeX)](https://github.com/HS2000PT/DIMEIA/actions/workflows/compile-thesis.yml/badge.svg)](https://github.com/HS2000PT/DIMEIA/actions/workflows/compile-thesis.yml)
[![Alerts (scheduled scan)](https://github.com/HS2000PT/DIMEIA/actions/workflows/alerts.yml/badge.svg)](https://github.com/HS2000PT/DIMEIA/actions/workflows/alerts.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)

> MSc in Artificial Intelligence Engineering (MEIA) — ISEP — Master's Dissertation
> Author: **Henrique José da Silva Santos** (nº 1180934) · Supervisor: Prof. Luís Gomes · Co-supervisor: Rafael Silva

**InvestiGator** is an **explainable (XAI-first)** financial-alert system for retail investors in the US market
(NYSE/NASDAQ), together with the LaTeX dissertation that documents it. For every alert it exposes the full
reasoning chain — detected event → explanation → sources → historical precedents — and delivers it over the
**Telegram Bot API**. No price prediction, no algorithmic trading, free APIs only.

## Where things are
| I want to… | Go to |
|---|---|
| Navigate the whole repo | [`docs/planos/INDEX.md`](docs/planos/INDEX.md) — the repository map |
| **Read the dissertation being submitted** | **`tese-v2/main.pdf`** — Portuguese; current submission candidate |
| Read the earlier versions | `tese/main.pdf` · `thesis/main.pdf` · `thesis-pt/main.pdf`. Superseded, kept for the record |
| Study for the defence | `tese/slides/main.pdf` (19) · `tese/guia/main.pdf` (20) · `tese/quiz/index.html`. Older material in `docs/defence/` targets the long thesis — read [`docs/defence/LEIA-ME-PRIMEIRO.md`](docs/defence/LEIA-ME-PRIMEIRO.md) first |
| See it live | <https://investigator-ddc9d8618935.herokuapp.com> + Telegram <https://t.me/InvestiGatorMEIA> |
| Get a 10-minute overview | [`archive/reports/RELATORIO_FINAL.md`](archive/reports/RELATORIO_FINAL.md) |
| Run it myself | `python scripts/demo.py` · full guide `docs/design/how_to_run.md` |
| See what's left to do | [`docs/planos/CHECKLIST.md`](docs/planos/CHECKLIST.md) |

## What it does
- **Trigger 1 — Abrupt market move:** flags a statistical anomaly (rolling *z*-score, no lookahead) and
  explains it in plain language.
- **Trigger 2 — New financial news:** finds analogous historical news (sentence-embedding retrieval) and
  shows the impact those precedents had (event study), as **evidence, never a prediction**.
- **News–market correlation engine (core):** a knowledge base of past news + observed price impact; a new
  headline is matched to similar past cases (case-based reasoning).

## ▶ Run it in one command
No keys, no configuration — the news trigger runs fully offline on a bundled sample knowledge base
(Windows-safe: forces UTF-8):

```bash
bash scripts/setup_env.sh     # once: Python 3.12 venv (light stack)
python scripts/demo.py        # runs BOTH triggers; nothing is sent
```

You should see the **news trigger** (offline, deterministic — reproduces the thesis worked example, mean
`+6.46%`) and the **market trigger** on live prices (e.g. `No anomaly for AAPL today (z-score +0.89)`).
Full operator guide (Telegram, live news, building your own KB): **`docs/design/how_to_run.md`** (start at
§0.0).

## 🔎 Or click through it — the live dashboard
**Live at <https://investigator-ddc9d8618935.herokuapp.com>** — a grid with one card per company,
ordered by how *rare* the day was. Every card opens with a sentence you can act on, and only then
shows the numbers behind it: *"only 5 of the last 249 trading days moved this much"*. That is a
**count**, not a probability — turning a z-score into a probability would assume normality, and
returns have fat tails, so the figure would be wrong on exactly the days that matter. A quiet day
shows the count that makes it quiet, rather than asking you to take our word for it. One click
opens the detail: the price chart with detected events on it, the market/sector/company split,
past cases retrieved by meaning, and the alerts exactly as the Telegram channel received them
(never recomputed). A separate page carries the frozen evaluation numbers, including the negative
result. Read-only by design, and built against acceptance criteria written before the code
(`docs/design/app_acceptance.md`). To run it locally (no keys, nothing sent):

```bash
pip install -r requirements.txt
uvicorn api.main:app --port 8099
```

The web process serves **JSON and static files**; the browser holds the state, so interacting with
the chart touches no network at all (measured: range changes cost 2.5–7.3 ms with zero requests,
against ~750 ms for the server-rendered design it replaced). The app retrieves
precedents **semantically** — the thesis's MiniLM model exported to ONNX (~23 MB, CPU, no torch;
numerical parity vs SBERT verified in `docs/evaluation/onnx_minilm_validation.md`) — falling back to
the word-overlap baseline only if the model is unavailable.

**Prefer a notebook?** `archive/streamlit-app/notebooks/investigator_walkthrough.ipynb` — the same three components
(anomaly detector, retrieval, the trained triage model), one hands-on cell at a time; see
`docs/design/how_to_run.md` §5.2.

## 📡 Live 24/7 (free)
Quality-first alerting to a **Telegram channel**, with honest engineering:
- **Relevance-filtered news** — a headline must actually mention the company (mistagged and
  boilerplate items are rejected), needs at least one strong historical precedent (similarity
  floor), is capped at 2 news alerts per ticker per day, and is gated by the **trained triage
  model**. Mixed-direction precedent sets carry an explicit warning.
- **Market presence every day** — anomaly alerts (rolling z-score), **intraday detection**
  in watch mode (today's move in progress from a real-time quote, same transparent z-score),
  and a **daily close summary** (all 10 tickers, anomalies highlighted — honest on calm days).
  When an anomaly fires, the system **investigates**: it attaches the freshest relevant
  headline as a possible explanation — or honestly says none was found.
- **A living knowledge base** — every relevant scanned headline becomes a precedent days
  later (impact measured at +5d against real prices); retrieval merges the live KB with the
  historical one using age decay, and every precedent shows its age ("3y ago").
- **Two producers, one memory** — a near-real-time **watch mode** (`run_alerts.py --watch`,
  runs on any always-on machine/VM; `docs/design/vm_watch.md`) plus the GitHub Actions cron as
  a safety net (weekday market hours, mornings and weekends for news); both share the
  `alerts-history` branch so nothing is ever duplicated.
- Try the scan now (sends nothing): `python scripts/run_alerts.py --dry-run`.

Full runbook (create the channel, set 3 GitHub secrets, deploy): **`docs/design/going_live.md`**.
- **Personal watchlists (interactive bot, no server needed)** → run `python scripts/run_bot.py`
  (long-polling) and anyone can DM the bot `/watch TSLA`, `/list`, `/stop`; the scheduled scan then
  also delivers each subscriber's tickers (`bot.enabled` in `config/alerts.yaml`, off by default).

## 🖱️ Prefer clicking? (no console)
- **Double-click** a launcher in **`archive/streamlit-app/run/`** (`dashboard.bat`, `demo.bat`, `tests.bat`, `thesis-pdf.bat`).
- Or use the **VS Code** buttons: *Run and Debug* ▶ (Dashboard / Demo) and *Terminal → Run Task* (tests,
  compile thesis/slides/paper). Full guide: **`docs/design/run_in_vscode.md`**.
- Track what's done vs pending in **[`docs/planos/CHECKLIST.md`](docs/planos/CHECKLIST.md)**.

## Learn it / prepare the defence — ONE source
- **THE study guide (PT-PT):** **`slides/guia_estudo/main.pdf`** — the single, consolidated source
  (83 slides): teaches the whole thesis from zero, the code line by line, the evaluation, **the oral
  script (3-min opening + per-RQ answers), the anticipated defence questions, the frozen-numbers table
  and the defence plan B**. Everything previously scattered across companion documents now lives here.
- **Project summary (PT-PT):** **[`archive/reports/RELATORIO_FINAL.md`](archive/reports/RELATORIO_FINAL.md)** — everything in this
  repository and where it lives, in a 10-minute read.
- **Defence slides (EN):** `slides/main.pdf` (17 frames) — the short deck for the day itself.

## Project status
The current submission candidate is **`tese-v2/main.pdf`**: six chapters, 70 references,
126 physical pages and **94 numbered pages before the annexes**, within the official 120-page limit.
It compiles with zero errors, undefined references or undefined citations. The canonical quality gate
checks every included source (including the generated Telegram-feedback fragment), the compilation log,
the page limit, references, floats, PT-PT writing and damaged LaTeX escapes.

The three evaluated components use real data and versioned procedures. The FNSPID corpus contains
79,753 examples; the temporal training split used by the triage model contains 28,574. The live model
is evidence triage, never a price forecast or an investment recommendation. The Telegram pilot currently
has 20 effective votes from two people; 19 rate their alert useful, but one participant supplies 80% of
the sample, so the dissertation explicitly says that the pilot does not support an independent reading.
Remaining human inputs include the committee names, the final author read, consent-message pinning before
inviting participants, credential rotation and the supervisor decisions listed in
[`docs/REGISTO_PEDIDOS.md`](docs/REGISTO_PEDIDOS.md).

## Repository layout
```
tese-v2/       canonical Portuguese dissertation candidate (6 chapters + 2 appendices)
tese/, thesis/, thesis-pt/  superseded dissertation trees, kept temporarily for traceability
paper/         IEEE paper (IEEEtran) distilled from the thesis
slides/        defence slides (Beamer, 17 frames)
  guia_estudo/   THE study guide (PT-PT, Beamer, 83 slides — single study source)
investigator/  system code, one package per component (investigator/triage/ = the trained ML component, RQ4)
models/        trained triage models (joblib, versioned; context-only variant runs in production)
archive/streamlit-app/notebooks/     investigator_walkthrough.ipynb — hands-on tour of the 3 components, executed & committed
api/           FastAPI service: data routes over investigator/, plus the AI report and analyst
web/           the served single-page client (Lightweight Charts v5, vendored, Apache 2.0)
app/           earlier Streamlit generations (v1/v3/v4), kept because thesis figures cite them;
               verdict.py and method.py are still used — the API calls them, so the sentences
               the reader sees cannot drift from the tested Python that produces them
archive/deploy/        VM watch mode: systemd unit + setup script (docs/design/vm_watch.md)
archive/streamlit-app/run/           double-click launchers (dashboard/demo/tests/thesis)
.vscode/       click-to-run: Run & Debug configs + tasks + recommended extensions
scripts/       demo.py (run it) + run_alerts.py (alerts runner, --watch mode) + evaluation/build scripts
config/        alerts.yaml — watchlist + thresholds + quality knobs for the alert runner
tests/         automated tests
docs/          documentation (see docs/README.md for the full index), grouped:
  design/        how_to_run, going_live, vm_watch, deployment, architecture, data card
  evaluation/    auto-generated evaluation results (do not edit by hand)
  decisions/     citation log, page audit, product review, learning notes, glossary
  internal/      provenance (the original root prompt)
data/samples/  small committed samples (large data gitignored, recreated by scripts)
progress/      continuity logs (TRACKER, SESSIONS, DECISIONS, PLANO_V2)
               _historico/ superseded plans, kept as a record
CITATION.cff   how to cite this work    requirements.txt (light) / requirements-ml.txt (torch+SBERT)
```

## Setup & verify (reproducible)
- Python **3.12** in a virtual environment: `bash scripts/setup_env.sh` installs the **light** stack
  (`requirements.txt`) — enough for the demo, the tests and the evaluations. The heavy ML stack (`torch` CPU,
  `sentence-transformers`, in `requirements-ml.txt`) is needed only for the real SBERT paths and installs with
  `bash scripts/setup_env.sh --ml` (it pulls `torch` from the PyTorch CPU index, not PyPI).
- Canonical dissertation gate: `python scripts/check_tese_v2.py` (strict) or
  `python scripts/check_tese_v2.py --permitir-pendencias-humanas` while committee names are unknown.
- General verification loop: `bash scripts/verify.sh` (tests + lint; its historical LaTeX note is not
  the canonical dissertation gate).
- Secrets live only in a local, gitignored `.env` (see `.env.example` for variable names).
- LaTeX builds locally (MiKTeX/TeX Live) and via GitHub Actions on each push.

## Reproducing the results
Every result and figure is produced by a versioned script with a fixed seed:
```bash
python scripts/fetch_finnhub_news.py                    # real news CSV (needs FINNHUB_API_KEY)
python scripts/evaluate.py --news data/finnhub_news.csv \
    --sbert-models all-MiniLM-L6-v2 all-mpnet-base-v2   # retrieval vs baselines (multi-seed)
python scripts/evaluate_per_sector.py --news data/finnhub_news.csv   # per-sector precision
python scripts/evaluate_anomaly.py                      # anomaly firing-rate + window ablation (pinned window)

cd tese-v2 && latexmk -r latexmkrc -pdf -recorder \
    -interaction=nonstopmode main.tex                   # canonical dissertation, also built in CI
python scripts/check_tese_v2.py --permitir-pendencias-humanas
cd paper   && latexmk -pdf main.tex                     # paper/main.pdf
cd slides  && latexmk -pdf main.tex                     # slides/main.pdf
cd slides/guia_estudo && latexmk -pdf main.tex          # the study guide
```
Re-running these reproduces the thesis numbers exactly (independently re-verified; audit trail in `docs/decisions/page_audit.md`).
The full multi-year FNSPID knowledge base (a ~23 GB streaming scan, see `docs/design/data_card.md`) is built
by `scripts/download_data.py` then `scripts/build_kb.py --sbert`; this is a long, deliberate job.

## Attributions & licences
- **Code licence — to be confirmed.** No `LICENSE` file is committed yet: the licence for this repository's
  own code should be chosen **with the supervisor**, after confirming ISEP's policy on IP over thesis code
  (a common, permissive choice for academic code is MIT or Apache-2.0). Until then, default copyright applies.
- **How to cite:** see `CITATION.cff` (GitHub shows a "Cite this repository" button).
- **FNSPID** (Financial News and Stock Price Integration Dataset) — `Zihan1004/FNSPID`,
  repo `Zdong104/FNSPID_Financial_News_Dataset`. Licence **CC BY-SA 4.0** — attribution mandatory.
- **FinBERT** — `ProsusAI/finbert` (via `transformers`), inference only.
- **ISEP MEIA LaTeX template** — `meia-style.cls`, licence **CC BY-NC-SA 3.0** (adapted by L. Faria, N. Pereira,
  P. Baltarejo, DEI/ISEP; based on the Masters/Doctoral Thesis template from LaTeXTemplates.com).
- **yfinance**, **Telegram Bot API**, and other free-tier APIs documented in `docs/design/free_apis.md`.

## Academic integrity
This dissertation is produced with AI assistance, declared per ISEP/MEIA rules. Every citation
is verified against a real source and logged in `docs/decisions/citation_log.md` — no fabricated references.
