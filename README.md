# Transparent Financial Alerts — Explainable AI for Retail Investors

> MSc in Artificial Intelligence Engineering (MEIA) — ISEP — Master's Dissertation
> Author: **Henrique José da Silva Santos** (nº 1180934) · Supervisor: Prof. Luís Gomes · Co-supervisor: Rafael Silva

This repository hosts an **explainable (XAI-first)** financial-alert system for retail investors, focused on the
US market (NYSE/NASDAQ), and the LaTeX dissertation that documents it. The system raises alerts via the
**Telegram Bot API** and, for every alert, exposes the full reasoning chain: detected event → explanation →
sources → historical precedents. No price prediction, no algorithmic trading, free APIs only.

## What it does
- **Trigger 1 — Abrupt market move:** detects a statistical anomaly in a US asset and explains it (probable
  causes, historical context, coinciding news).
- **Trigger 2 — New financial news:** detects relevant news, assesses potential impact, and retrieves
  analogous historical news with the impact those precedents had.
- **News–market correlation engine (core):** a historical knowledge base (FNSPID) of past news + observed
  price impact; new news is matched to similar past news to provide explanatory evidence.

## Project status
**Working draft complete.** Both triggers are implemented and proven end to end (anomaly detection →
explanation → Telegram; news → SBERT retrieval of precedents → explanation), with 41 automated tests.
The two core components are evaluated on **real data** (see `docs/evaluation_results.md` and
`docs/evaluation_anomaly.md`), and the seven-chapter dissertation is drafted and compiles
(`thesis/main.pdf`). The full multi-year FNSPID knowledge base is the main remaining item (a long
download job; the streaming pipeline is implemented and verified). See `CLAUDE.md` for the exact
current state and `progress/SESSIONS.md` for the per-session history.

## Repository layout
See the full structure in `ROOT_PROMPT_CLAUDE_CODE.md` (§9). Key folders: `src/` (system code by component),
`thesis/` (LaTeX), `docs/` (design, decisions, learning notes — PT-PT), `progress/` (continuity logs),
`scripts/` (automation), `data/` (samples committed; large data gitignored and recreated by scripts).

## Setup (reproducible)
- Python **3.12** in a virtual environment: `bash scripts/setup_env.sh` (deps pinned in
  `requirements.txt` / `requirements.lock.txt`). The ML stack (`torch` CPU, `sentence-transformers`)
  is needed only for the SBERT paths.
- Verification loop: `bash scripts/verify.sh` (tests + lint + LaTeX note).
- Secrets live only in a local, gitignored `.env` (see `.env.example` for variable names).
- LaTeX builds locally (MiKTeX/TeX Live) and via GitHub Actions on each push (CI is the source of truth for the PDF).

## Reproducing the results
Every result and figure is produced by a versioned script with a fixed seed:
```bash
# Retrieval (Question A): fetch real news, run the ablation → docs/evaluation_results.md + figure
python scripts/fetch_finnhub_news.py                         # needs FINNHUB_API_KEY in .env
python scripts/evaluate.py --news data/finnhub_news.csv \
    --sbert-models all-MiniLM-L6-v2 all-mpnet-base-v2

# Anomaly detector (Question 1): real prices → docs/evaluation_anomaly.md + figure
python scripts/evaluate_anomaly.py --period 3y

# Build the dissertation PDF (also built in CI)
bash scripts/build_pdf.sh
```
The full multi-year FNSPID knowledge base (a ~23 GB streaming scan, see `docs/data_card.md`) is built by
`scripts/download_data.py` followed by `scripts/build_kb.py --sbert`; this is a long, deliberate job.

## Attributions & licences
- **FNSPID** (Financial News and Stock Price Integration Dataset) — `Zihan1004/FNSPID`,
  repo `Zdong104/FNSPID_Financial_News_Dataset`. Licence **CC BY-SA 4.0** — attribution mandatory.
- **FinBERT** — `ProsusAI/finbert` (via `transformers`), inference only.
- **ISEP MEIA LaTeX template** — `meia-style.cls`, licence **CC BY-NC-SA 3.0** (adapted by L. Faria, N. Pereira,
  P. Baltarejo, DEI/ISEP; based on the Masters/Doctoral Thesis template from LaTeXTemplates.com).
- **yfinance**, **Telegram Bot API**, and other free-tier APIs documented in `docs/free_apis.md`.

## Academic integrity
This dissertation is produced with AI assistance (Claude Code), declared per ISEP/MEIA rules. Every citation is
verified against a real source and logged in `docs/citation_log.md` — no fabricated references.
