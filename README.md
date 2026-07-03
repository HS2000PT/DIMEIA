<img src="app/assets/investigator.svg" width="150" align="right" alt="InvestiGator mascot — a friendly detective alligator">

# InvestiGator 🐊🔍 — Explainable Financial Alerts for Retail Investors

*Investigate. Don't speculate.*

**▶ Try it live: <https://investigator.streamlit.app>**

[![CI (tests + lint)](https://github.com/HS2000PT/DIMEIA/actions/workflows/ci.yml/badge.svg)](https://github.com/HS2000PT/DIMEIA/actions/workflows/ci.yml)
[![Compile thesis (LaTeX)](https://github.com/HS2000PT/DIMEIA/actions/workflows/compile-thesis.yml/badge.svg)](https://github.com/HS2000PT/DIMEIA/actions/workflows/compile-thesis.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)

> MSc in Artificial Intelligence Engineering (MEIA) — ISEP — Master's Dissertation
> Author: **Henrique José da Silva Santos** (nº 1180934) · Supervisor: Prof. Luís Gomes · Co-supervisor: Rafael Silva

**InvestiGator** is an **explainable (XAI-first)** financial-alert system for retail investors in the US market
(NYSE/NASDAQ), together with the LaTeX dissertation that documents it. For every alert it exposes the full
reasoning chain — detected event → explanation → sources → historical precedents — and delivers it over the
**Telegram Bot API**. No price prediction, no algorithmic trading, free APIs only.

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

## 🔎 Or click through it — the dashboard
**Live at <https://investigator.streamlit.app>** — both triggers plus the evaluation, in the browser,
nothing to install. To run it locally instead (no keys, nothing sent):

```bash
pip install -r requirements.txt -r requirements-app.txt
streamlit run app/streamlit_app.py
```

Hosting details (Streamlit Community Cloud, free): **`docs/design/deployment.md`**. The app runs the
offline baseline embedder; the SBERT numbers are on the dashboard's *Evaluation* page.

## 📡 Live 24/7 (free, no server)
Turn InvestiGator into a running service without paying or babysitting a server:
- **Scheduled alerts** → `scripts/run_alerts.py` scans a watchlist (`config/alerts.yaml`) and posts
  explainable alerts to a **Telegram channel**; a free **GitHub Actions timer**
  (`.github/workflows/alerts.yml`) runs it after the US close. Users just **join the channel**.
- **The webpage, any time** → the dashboard on Streamlit Community Cloud (`docs/design/deployment.md`).
- Try the scan now (sends nothing): `python scripts/run_alerts.py --dry-run`.

Full runbook (create the channel, set 3 GitHub secrets, deploy): **`docs/design/going_live.md`**.
The interactive per-user bot (users DM `/watch TSLA`) is designed there as a later, hosted phase.

## 🖱️ Prefer clicking? (no console)
- **Double-click** a launcher in **`run/`** (`dashboard.bat`, `demo.bat`, `tests.bat`, `thesis-pdf.bat`).
- Or use the **VS Code** buttons: *Run and Debug* ▶ (Dashboard / Demo) and *Terminal → Run Task* (tests,
  compile thesis/slides/paper). Full guide: **`docs/design/run_in_vscode.md`**.
- Track what's done vs pending in **[`CHECKLIST.md`](CHECKLIST.md)**.

## Learn it / prepare the defence
- **From-zero visual study guide (PT-PT):** **`slides/guia_estudo/main.pdf`** — teaches the whole thesis
  assuming *no* AI background (60 slides): the AI ideas actually used, the data shown, the code line by line,
  the end-to-end workflow with real examples, the evaluation, and prepared jury questions.
- **Defence slides (EN):** `slides/main.pdf` (15 frames).
- **PT-PT defence companion (prose):** `docs/defence/caderno_de_defesa.md`.

## Project status
**Validated and submission-ready (pending human sign-off).** Both triggers are proven end to end;
**47 automated tests** + lint green. The two core components are evaluated on **real data**, and the
statistics were independently re-run and reproduce the thesis figures exactly. The **six-chapter
dissertation** compiles cleanly (`thesis/main.pdf`, ~72 pp, 0 errors), with **50 references each verified by
DOI/arXiv/ISBN or primary source** (audit in `docs/decisions/page_audit.md`). An **IEEE paper** (`paper/`)
and **defence slides** (`slides/`) compile. Remaining items are human-only: confirm the exact ISEP AI-use
declaration wording + submission date, and the author's final read. The full multi-year FNSPID knowledge
base is optional future work (a long download; the streaming pipeline is implemented and verified). See
`CLAUDE.md` for the exact state and `progress/SESSIONS.md` for per-session history.

## Repository layout
```
thesis/        LaTeX dissertation (6 chapters + front matter + appendix)
paper/         IEEE paper (IEEEtran) distilled from the thesis
slides/        defence slides (Beamer, 15 frames)
  guia_estudo/   from-zero PT-PT study guide (Beamer, 60 slides)
src/           system code, one package per component
app/           streamlit_app.py — interactive dashboard (thin UI over src/)
run/           double-click launchers (dashboard/demo/tests/thesis)
.vscode/       click-to-run: Run & Debug configs + tasks + recommended extensions
scripts/       demo.py (run it) + run_alerts.py (24/7 scan) + data / figures / build automation
config/        alerts.yaml — watchlist + thresholds for the scheduled alert runner
tests/         automated tests
docs/          documentation (see docs/README.md for the full index), grouped:
  design/        how_to_run, architecture, data card, free APIs, setup
  evaluation/    auto-generated evaluation results (do not edit by hand)
  decisions/     decisions rationale, citation log, glossary, reviews
  defence/       PT-PT defence companion
  internal/      internal continuity docs (e.g. the original root prompt)
  _archive/      early-phase analyses kept for provenance
data/samples/  small committed samples (large data gitignored, recreated by scripts)
progress/      continuity logs (TRACKER, SESSIONS, DECISIONS, MASTER_PLAN)
CITATION.cff   how to cite this work    requirements.txt (light) / requirements-ml.txt (torch+SBERT)
```

## Setup & verify (reproducible)
- Python **3.12** in a virtual environment: `bash scripts/setup_env.sh` installs the **light** stack
  (`requirements.txt`) — enough for the demo, the tests and the evaluations. The heavy ML stack (`torch` CPU,
  `sentence-transformers`, in `requirements-ml.txt`) is needed only for the real SBERT paths and installs with
  `bash scripts/setup_env.sh --ml` (it pulls `torch` from the PyTorch CPU index, not PyPI).
- Verification loop: `bash scripts/verify.sh` (47 tests + lint + LaTeX note).
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

bash scripts/build_pdf.sh                               # thesis/main.pdf (also built in CI)
cd paper   && latexmk -pdf main.tex                     # paper/main.pdf
cd slides  && latexmk -pdf main.tex                     # slides/main.pdf
cd slides/guia_estudo && latexmk -pdf main.tex          # the study guide
```
Re-running these reproduces the thesis numbers exactly (see `docs/decisions/implementation_review.md`).
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
This dissertation is produced with AI assistance (Claude Code), declared per ISEP/MEIA rules. Every citation
is verified against a real source and logged in `docs/decisions/citation_log.md` — no fabricated references.
