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
**Validated and submission-ready (pending human sign-off).** Both triggers are implemented and proven end
to end (anomaly detection → explanation → Telegram; news → SBERT retrieval of precedents → explanation),
with **42 automated tests** + lint green. The two core components are evaluated on **real data**; the
statistics were **independently re-run** and reproduce the thesis figures exactly. The **six-chapter
dissertation** compiles cleanly (`thesis/main.pdf`, ~76 pp, 0 errors), with **50 references each verified
by DOI/arXiv/ISBN or primary source** (audit in `docs/decisions/page_audit.md`). An **IEEE paper**
(`paper/`) and **defence slides** (`slides/`) are drafted and compile, and a PT-PT **visual defence guide**
is in `docs/defence/caderno_de_defesa.md`. Remaining items are human-only: confirm the exact ISEP AI-use
declaration wording + submission date, and the author's final read. The full multi-year FNSPID knowledge
base is optional future work (a long download; the streaming pipeline is implemented and verified). See
`CLAUDE.md` for the exact state and `progress/SESSIONS.md` for per-session history.

## Repository layout
```
thesis/        LaTeX dissertation (6 chapters + front matter + appendix)
paper/         IEEE paper (IEEEtran) distilled from the validated thesis
slides/        defence slides (Beamer, 14 frames)
src/           system code, one package per component
scripts/       data, figures, build/verify/session automation
tests/         automated tests
docs/          PT-PT documentation, grouped:
  design/        architecture, data card, free APIs, evaluation design, setup, risks
  evaluation/    auto-generated evaluation results (do not edit by hand)
  decisions/     decisions rationale, citation log, glossary, learning notes
  defence/       PT-PT study guide for the defence
  _archive/      early-phase analyses kept for provenance
data/samples/  small committed samples (large data gitignored, recreated by scripts)
progress/      continuity logs (TRACKER, SESSIONS)
```

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
# Retrieval (Question A): fetch real news, run the ablation → docs/evaluation/evaluation_results.md + figure
python scripts/fetch_finnhub_news.py                         # needs FINNHUB_API_KEY in .env
python scripts/evaluate.py --news data/finnhub_news.csv \
    --sbert-models all-MiniLM-L6-v2 all-mpnet-base-v2

# Per-sector retrieval breakdown → docs/evaluation/evaluation_per_sector.md + figure
python scripts/evaluate_per_sector.py --news data/finnhub_news.csv

# Anomaly detector (Question 1): real prices, pinned window → docs/evaluation/evaluation_anomaly.md + figure
python scripts/evaluate_anomaly.py

# Build the dissertation, the IEEE paper, and the slides
bash scripts/build_pdf.sh            # thesis/main.pdf (also built in CI)
cd paper && latexmk -pdf main.tex    # paper/main.pdf
cd slides && latexmk -pdf main.tex   # slides/main.pdf
```
Re-running these reproduces the thesis numbers exactly (validated 2026-06-27; see
`docs/decisions/implementation_review.md`).
The full multi-year FNSPID knowledge base (a ~23 GB streaming scan, see `docs/design/data_card.md`) is built by
`scripts/download_data.py` followed by `scripts/build_kb.py --sbert`; this is a long, deliberate job.

## Attributions & licences
- **FNSPID** (Financial News and Stock Price Integration Dataset) — `Zihan1004/FNSPID`,
  repo `Zdong104/FNSPID_Financial_News_Dataset`. Licence **CC BY-SA 4.0** — attribution mandatory.
- **FinBERT** — `ProsusAI/finbert` (via `transformers`), inference only.
- **ISEP MEIA LaTeX template** — `meia-style.cls`, licence **CC BY-NC-SA 3.0** (adapted by L. Faria, N. Pereira,
  P. Baltarejo, DEI/ISEP; based on the Masters/Doctoral Thesis template from LaTeXTemplates.com).
- **yfinance**, **Telegram Bot API**, and other free-tier APIs documented in `docs/design/free_apis.md`.

## Academic integrity
This dissertation is produced with AI assistance (Claude Code), declared per ISEP/MEIA rules. Every citation is
verified against a real source and logged in `docs/decisions/citation_log.md` — no fabricated references.
