# ROOT PROMPT — MEIA MASTER'S DISSERTATION | ISEP
## Henrique José da Silva Santos
### Definitive version (v3 — English, premium autonomous build)

---

> **INITIAL INSTRUCTION:** Read this document in full before taking any action.
> Follow the phase order without exception. **Phase 0 (Setup & Authorization) runs before everything else.**
> Do not advance to a phase until the previous one meets its Definition of Done (see §8).
> This project runs over **~30 work sessions (a planning guide, not a hard limit)**, across multiple devices. **Continuity between sessions is the single most critical requirement of the whole project**, and it depends on disciplined git hygiene (§12) and an always-current `CLAUDE.md` (§11).
> Optimise for **quality, defensibility, and reproducibility — not speed**. Token cost is not a constraint. A correct, verified, well-explained result is always worth more than a fast one.

---

## 0. CONFIGURATION — LANGUAGE POLICY (read and confirm in Phase 0)

These are the project's working languages. They are deliberate. Confirm them with the student in Phase 0 and then keep them **absolutely consistent**.

| Setting | Value | Notes |
|---|---|---|
| **Thesis language** | **English** | Lock **EN-GB *or* EN-US in Phase 0** and never mix. (Recommended: EN-GB, given ISEP/EU context — student decides.) |
| **Student-facing explanations** (`docs/learning.md`, `docs/glossary.md`, every concept explanation, every "how I'd defend this" note) | **PT-PT** | This is intentional: the student learns and reasons best in his native language, and must be able to *defend* the work. Comprehension comes first. **If the student prefers these in English, change only this row — it is the single toggle.** |
| **Code & LaTeX comments** | **PT-PT** | Keep consistent with the above. |
| **Internal docs** (`progress/`, `docs/`, commit messages) | **PT-PT** | |
| **This root prompt** | **English** | The meta-instructions to the agent. |

> The split (thesis in EN, learning in PT-PT) is a feature, not an inconsistency: the *deliverable* is international and citable; the *understanding* is in the student's strongest language.

---

## 1. PROJECT IDENTITY

| Field | Value |
|---|---|
| **Student** | Henrique José da Silva Santos |
| **Programme** | MSc in Artificial Intelligence Engineering (MEIA) — ISEP |
| **Stage** | 2nd year — Dissertation |
| **Supervisor** | Prof. Luís Gomes |
| **Co-supervisor** | Rafael Silva |
| **Thesis language** | English (lock EN-GB/EN-US in Phase 0) |
| **Comment / internal-doc language** | PT-PT |
| **Git platform** | GitHub |
| **Project horizon** | ~30 work sessions (flexible; quality-driven) |

---

## 2. AUTONOMY CHARTER — HOW MUCH FREEDOM YOU HAVE (and the few hard limits)

The student has asked for maximal autonomy: "full control, I agree with everything." This section makes that **safe and real**. The limits below are not friction — they are the reason "full control" never becomes "lost the thesis" or "leaked a secret." They make autonomy *trustworthy*.

### 2.1 You may do all of this autonomously, without asking each time
- Read, create, edit, refactor, move and delete files **inside the project repository**.
- Run the project's own scripts, the test suite, linters, and the LaTeX build.
- Search the web and scholarly APIs (Crossref, OpenAlex, Semantic Scholar, arXiv, DBLP) for literature, data, and verification.
- Stage, commit, `pull --rebase`, and push to the project's own GitHub remote.
- Install Python dependencies into the project's virtual environment.
- Generate figures, tables, documentation, and thesis text.

> Pre-authorise these in `.claude/settings.json` (see §19) so the student is not approving routine actions all day.

### 2.2 Hard limits — NEVER do these without an explicit, in-chat heads-up and the student's confirmation
1. **Never expose a secret.** No token, password, API key, or credential is ever written into any committed file, the prompt, `CLAUDE.md`, commit messages, logs, or the thesis. Secrets live only in a gitignored `.env`. Before *every* commit, scan the staged diff for anything that looks like a secret and abort if found.
2. **Never fabricate.** Do not invent data, results, metrics, quotes, or — above all — **references**. Every citation must be verified against a real source (§6 Citation-Integrity Protocol). A made-up citation is the fastest way to fail a defense.
3. **Never perform irreversible or destructive git operations without a heads-up:** no `git push --force` / `--force-with-lease`, no history rewrite (`rebase -i` on pushed commits, `reset --hard` that discards work, `filter-branch`), no branch deletion, no `git clean -fdx` that would erase un-tracked work.
4. **Never delete or overwrite anything outside the repo**, no recursive deletes outside the project, no `sudo`, no system-level changes.
5. **Never spend money.** Free tiers only (§5.2). If a step would require a paid plan or a credit card, stop and report it.
6. **Never automate logins to publisher portals** (IEEE Xplore, ACM DL, etc.) with the student's institutional credentials — terms-of-service risk for the whole institution. Use open scholarly APIs for discovery; the student supplies any gated PDFs himself into a gitignored folder.
7. **Pause at every phase gate** (§8) and at any genuinely irreversible academic decision (final title, scope cuts, methodology changes) for the student to confirm or redirect.

### 2.3 Secrets policy (operational)
- `.env` holds all secrets and is in `.gitignore`. `.env.example` (committed) lists the variable **names only**, never values.
- CI secrets (e.g. for the GitHub Action) go in **GitHub → Settings → Secrets and variables → Actions**, never in the workflow YAML.
- If you ever detect a secret has been committed, **stop immediately**, tell the student, and treat the secret as compromised (it must be rotated).

---

## 3. ABOUT THE STUDENT — READ THIS FIRST AND ADJUST ALL OF YOUR BEHAVIOUR TO IT

- I am a MEIA (ISEP) student in the dissertation stage. **I am not an AI specialist** and, honestly, I have foundational gaps. Assume I do not know a concept until you have explained it to me in plain language.
- My goal is to **finish a solid dissertation and, above all, defend it calmly**. I am a nervous person. Everything we build must be something **I can explain and defend before the jury**. If I don't understand something, it is a risk — no matter how impressive it looks.
- **Therefore your golden rule is: teach me as you go.** Never introduce a concept, technique, metric, or library without giving me, in PT-PT, a clear paragraph on what it is and why we use it. Keep that record in `docs/learning.md` and the glossary in `docs/glossary.md`. Before closing each component, write — in defense language — "how I explain this to the jury in 3 sentences."
- **Defensible simplicity > sophistication.** Between two approaches with similar results, always choose the simpler, more standard, easier-to-explain one.
- **My contribution (assume and reinforce this throughout the documentation):** this is an **AI Engineering** thesis. The contribution is NOT inventing new algorithms — it is to *integrate, apply and critically evaluate* existing components in a functional, explainable, reproducible system, with a documented news-impact correlation methodology. Using existing models and tools **is** the engineering work, not a weakness. Whenever you document a decision, frame it to reinforce this contribution.

---

## 4. THESIS TITLE

As a starting point, consider this suggested title:

> *"Towards Transparent Financial Alerts: An Explainable AI System for Retail Investors Integrating Market Anomaly Detection and News Impact Correlation"*

In **Phase C**, propose 3 academic alternatives with justification for each, including an evaluation of this suggestion. The final decision is the student's.

---

## 5. THEME AND SYSTEM TO BE DEVELOPED

### 5.1 Central theme
An intelligent financial-alert system for retail investors, with **total explainability (XAI-first)**. The system is driven by two independent triggers:

**Trigger 1 — Abrupt market movement (NYSE/NASDAQ):**
- Detects a statistical anomaly in a US asset.
- Alerts the user via Telegram.
- Generates a traceable explanation for the movement (probable causes, historical context, news coinciding in the period).

**Trigger 2 — New financial news:**
- Detects relevant news in real time.
- Alerts the user via Telegram.
- Assesses the potential impact on the mentioned asset(s).
- Identifies other tickers historically affected by similar news in the same sector (e.g. Tesla news → historical impact on other EV companies).
- Presents concrete historical examples of analogous news and the impacts observed.

**News–market correlation engine (core of the thesis):**
- A **historical** knowledge base: past news + observed temporal impact on assets (see §5.4 — this base comes from FNSPID, not live APIs).
- When new news arrives, the system retrieves analogous historical news (by similarity) and measures the impact they had, using them as explanatory evidence.
- All reasoning logic is exposed to the user — no black boxes.

**Final output:**
- Alerts via the **Telegram Bot API** (free).
- Each alert contains: detected event + detailed explanation + sources + historical precedents.
- Principle: the user knows **100% how the system reached that conclusion**.

### 5.2 Non-negotiable constraints
```
✅ Free APIs only (market + news + Telegram)
✅ Focus on the US market: NYSE and NASDAQ
✅ XAI-first: all logic is transparent and traceable
✅ Genuinely useful to a real retail investor
✅ Academic rigour: AI methodologies documented and justified
❌ No price prediction / stock forecasting
❌ No algorithmic trading of any kind
❌ No paid APIs
❌ No filler content
```

### 5.3 SCOPE DISCIPLINE (the project's survival rule)
The system has many components. To avoid derailing:
- **Build a thin end-to-end slice first** (one trigger → one simple detection → one Telegram alert with a minimal explanation). Only then add depth, component by component.
- **Every component starts as its simplest, most defensible version** (see §5.5). No premature sophistication.
- **Before adding any new complexity**, ask the student: "is this needed for the thesis, or are we bloating?" If the September timeline tightens, propose cuts — a smaller, complete system beats a large, unfinished one.
- **Optional components (cuttable without regret):** multi-ticker sector-impact analysis; extra sentiment models (VADER, etc.); any refinement the student cannot explain.

### 5.4 DATA ARCHITECTURE (read carefully)
The system needs **two distinct data layers**. Do not confuse them.

**(A) HISTORICAL layer — to build the correlation engine's knowledge base.**
- Primary source: **FNSPID** (Financial News and Stock Price Integration Dataset). Financial news **already time-aligned with prices**, for ~4,775 S&P 500 companies, 1999–2023. Exactly what we need to build the "news → observed impact" history without scraping.
- Hugging Face dataset id: `Zihan1004/FNSPID`. Reference GitHub: `Zdong104/FNSPID_Financial_News_Dataset`. **Licence CC BY-SA 4.0 — attribution mandatory in the README and the thesis.**
- It is huge; subselect a tractable set of tickers and time window so it runs on a laptop. S&P 500 companies are NYSE/NASDAQ large caps, which fits the US-market focus.
- **Why we do not use news APIs for history:** free tiers (NewsAPI.org and similar) typically give only the **last ~30 days**, are "development-use only", and are delayed. They cannot build a historical base. Confirm in Phase C, but proceed from this principle.

**(B) LIVE layer — for the real-time triggers.**
- Real-time prices/market: `yfinance` (starting point), and to be confirmed Alpha Vantage / Finnhub (free tiers).
- Real-time news: to be confirmed among Finnhub (free tier, includes news), GNews API (free tier) and financial RSS feeds. NewsAPI only as a last resort and only for "live", never historical.
- Alerts: **Telegram Bot API** (free). Keep the token in `.env` (never committed); maintain `.env.example`.
- **Verify current limits (rate limits, history, ticker coverage, reliability) in Phase C** and document in `docs/free_apis.md`. Conditions change; do not assume, confirm.

**Data governance (applies to both layers):**
- Produce a short **data card** in `docs/data_card.md`: source, licence, attribution, the exact ticker subset and time window chosen, and every preprocessing/cleaning decision (so the dataset is reproducible).
- All large data is gitignored and **recreated** by `scripts/download_data.py`; commit only tiny samples under `data/samples/`. Treat news text as potentially containing personal references — do not republish raw third-party article text in the thesis; quote minimally and cite.

### 5.5 METHODOLOGY NOTES PER COMPONENT (keep it simple and defensible)
- **Anomaly detection:** start with transparent, easy-to-explain statistical methods (returns vs. rolling mean/std, z-score, volatility thresholds). Only if academically justified, move up to something like Isolation Forest. Transparency here is an XAI advantage.
- **Correlation / precedents engine:** represent each news item with embeddings (an open-source sentence-embeddings model) and retrieve the most similar historical items; measure "observed impact" with post-news return windows (simple *event-study* style: return at +1 day, +3 days, etc.). Document the choices (window, similarity metric) — they are your decisions and part of the contribution.
- **News sentiment (if used):** **FinBERT** (`ProsusAI/finbert`) via `transformers`, **inference only, no training**. It is the citable domain standard.
- **Explanation engine (XAI):** combine (i) transparent rules/heuristics, (ii) the retrieved historical precedents as evidence, and (iii) optionally feature attribution (e.g. SHAP) over the anomaly detector. The goal is an explanation the user can follow step by step.
- All evaluation respects the rigour rules of §6.5.

---

## 6. ACADEMIC & EDITORIAL RULES (PERMANENT)

### 6.1 Contextualisation
- For **market data, statistics and trends**: use **current sources (2025–2026)**, real and verifiable (US market statistics, recent charts, trends in AI applied to finance).
- This "recency" rule applies to **contextualisation**, NOT to the theoretical foundation or the literature review (see §6.2).

### 6.2 Literature Review
- **Mandatorily include seminal/foundational works** in the relevant areas (anomaly detection, XAI/explainability, financial NLP), **even if older** — without them the review and methodology have no foundation and the jury will notice.
- Combine these with **recent** works to show the current state of the art.
- Preferred sources: **peer-reviewed** — IEEE Xplore, ACM Digital Library, scientific journals. arXiv is acceptable for relevant preprints (much serious XAI work lives there), **but cite the published version when one exists.**
- Mandatory structure: **comparative tables** of approaches — methodologies, technologies, advantages and limitations of each.
- Each cited work must make clear: what they did, how they did it, what is missing/limitations.

### 6.3 Literature discovery workflow (ToS-clean, login-free)
- Discover and gather metadata via open APIs: **Crossref, OpenAlex, Semantic Scholar, arXiv, DBLP**. These need no institutional login.
- Never automate logins to IEEE/ACM/publisher portals. When a full PDF behind institutional access is needed, **ask the student to download it** and place it in `data/literature/` (gitignored). Read it locally; cite the published version.

### 6.4 CITATION-INTEGRITY PROTOCOL (critical — this protects the defense)
This is the most important academic safeguard in the project. AI-assisted writing fails defenses primarily through **fabricated or wrong citations**. Therefore:
- **Every `.bib` entry must be verified against a real, resolvable source** — a DOI resolved via Crossref/OpenAlex, an arXiv id, or a real publisher/DBLP record — **before** it is cited in the thesis.
- Maintain `docs/citation_log.md`: for each reference, record the verified identifier (DOI/arXiv id/URL), the date checked, and which source confirmed it.
- **If a citation cannot be verified, it does not enter the thesis.** No placeholder citations, no "approximate" references, no invented author/year/venue. Ever.
- Quotations follow fair use: paraphrase by default, quote sparingly and minimally, always attributed. Never paste long passages from a source.
- Before any major writing milestone, run a citation pass: every claim that needs a source has one, and every source in the `.bib` is verified and actually used.

### 6.5 Methodological rigour (permanent)
- **No lookahead / future information leakage:** when measuring historical impact or evaluating any model, the features at an instant may never peek into the future. Document this explicitly.
- **Honest evaluation:** define metrics appropriate to each component (e.g. precision/recall for anomaly detection; quality of retrieved precedents; perceived usefulness of explanations). A modest result, reported honestly, is valid and defensible. **Never inflate or invent numbers.**
- **Reproducibility:** fixed seeds, pinned dependencies (see §7), documented steps, regenerable figures (see §6.7).
- **Every claim has a source; every technical decision has a justification.**

### 6.6 Writing style and process
- Language: **English**, consistent (EN-GB or EN-US — locked in Phase 0).
- Tone: clear, direct, academic but accessible; never pompous or vague.
- **Natural, high-quality writing**, in the register of the reference dissertation (analysed in Phase A): varied paragraph structure, no empty generic sentences, no repetitive patterns. The goal is good, readable academic prose.
- Quality > Quantity: every sentence adds value.
- **Writing happens in passes:** outline → draft → revise. **The student reviews and edits every section** so the prose is genuinely his and he can defend each sentence. This is part of the workflow, not an afterthought.

### 6.7 Visual artefacts — TOP PRIORITY
Reach a count comparable to the reference dissertation. Mandatory types:
- **Architecture diagrams** of the system (overview + individual components).
- **Literature comparison tables** (approaches, methodologies, metrics).
- **Results charts** (evaluation metrics, performance).
- **Experimental results tables.**
- **Recent charts and statistics** in the contextualisation (2025–2026 US-market data).
- **Illustrative figures** of concepts, flows and pipelines.

Each artefact is generated or adapted specifically for this dissertation and stored in `thesis/figures/`. **Every data/results figure is produced by a script in the repo (reproducible), not hand-made one-offs** — prefer vector output (PDF/SVG) for LaTeX. Keep the generating script alongside or referenced in `docs/`.

### 6.8 Academic integrity (READ — protects you in the defense)
- **Declare the use of AI** (Claude Code) in producing the dissertation, per ISEP/MEIA rules. **Ask the student for the exact policy and follow it.** If he doesn't know it, remind him to confirm with the supervisor.
- **The student must understand and be able to defend everything we deliver** — every component, every decision, every sentence. Ensuring this is part of your job: explain, summarise, and prepare him. His protection in the defense is mastery of the work, not its appearance.

---

## 7. REPRODUCIBILITY & ENVIRONMENT (multi-device)

Because work happens on multiple devices, the environment must be reconstructable with one command.

- **Pin the Python version** (record it in `docs/setup.md` and, if used, a `.python-version`). Recommend a recent stable 3.x — confirm and fix it in Phase 0.
- **Use a virtual environment** (`.venv/`, gitignored). Never install into the system Python.
- **Pin dependencies** in `requirements.txt` with exact versions; generate a lockfile (e.g. `pip freeze > requirements.lock.txt`) so any device reproduces the exact environment.
- `scripts/setup_env.sh` creates the venv, installs pinned deps, and verifies key imports. Running it on a fresh machine must yield an identical working environment.
- Record the LaTeX approach in `docs/setup.md`: the **GitHub Action is the source of truth for the compiled PDF** (so a device without a LaTeX install can still see output); document the optional local install for those who want it.
- Fixed random seeds everywhere randomness appears; record them in code and in the methodology.

---

## 8. TESTING, VERIFICATION & DEFINITION OF DONE

Premium quality comes from verification loops, not from doing more. Nothing is "done" until it is verified.

### 8.1 Testing strategy
- A `tests/` folder with lightweight unit tests for the core logic (anomaly detection thresholds, similarity retrieval, impact-window computation, explanation assembly).
- A **smoke test for the thin slice**: an automated check that the end-to-end path runs and a Telegram message is actually sent (using a test chat/token from `.env`).
- As each new component lands, **re-run the thin-slice smoke test** to catch regressions.

### 8.2 `scripts/verify.sh`
A single command that: runs the test suite, runs linters/formatters, compiles the LaTeX (or confirms CI did), and reports a clear pass/fail summary. Run it before every `end_session`.

### 8.3 Definition of Done (DoD) — gate for advancing any phase
A phase is complete only when **all** hold:
- [ ] Its deliverables exist and are committed.
- [ ] `verify.sh` passes (tests green, LaTeX compiles).
- [ ] Every new concept used is explained in `docs/learning.md` (PT-PT) with a 3-sentence "defense" note.
- [ ] Every new citation is verified and logged in `docs/citation_log.md`.
- [ ] No secret is present in any committed file.
- [ ] `CLAUDE.md` is updated with the new state and the precise next action.
**Pause at each gate and confirm with the student before proceeding.**

---

## 9. REPOSITORY STRUCTURE (Git)

Create exactly this structure. No unlisted files, no duplicates.

```
/
├── ROOT_PROMPT_CLAUDE_CODE_v3.md       # This document (foundational instructions)
├── CLAUDE.md                           # Persistent memory — UPDATE at the end of every session
├── README.md                           # Project overview + attributions (FNSPID, FinBERT, etc.)
├── .gitignore                          # LaTeX artifacts, Python cache, .venv, .env, large data, models
├── .gitattributes                      # Normalise line endings across devices (LF), mark binaries
├── .env.example                        # Example variable NAMES only (Telegram token, API keys) — no values
├── requirements.txt                    # Pinned Python dependencies
├── requirements.lock.txt               # Full lockfile (pip freeze) for exact reproduction
├── .python-version                     # Pinned Python version (optional but recommended)
│
├── .claude/
│   └── settings.json                   # Claude Code permission allow/deny rules (see §19)
│
├── .github/
│   └── workflows/
│       └── compile-thesis.yml          # GitHub Action: compiles LaTeX and publishes the PDF on each push
│
├── scripts/
│   ├── setup_env.sh                    # Create venv + install pinned deps + verify imports
│   ├── start_session.sh                # Pull-rebase + show state (see §13)
│   ├── end_session.sh                  # Verify + commit + pull-rebase + push (conflict-safe)
│   ├── verify.sh                       # Tests + lint + LaTeX build + pass/fail summary
│   └── download_data.py                # Downloads/prepares FNSPID (with attribution)
│
├── tests/                              # Unit tests + thin-slice smoke test
│
├── thesis/                             # LaTeX project (based on the ISEP template)
│   ├── main.tex
│   ├── chapters/
│   │   ├── 01_introduction.tex
│   │   ├── 02_contextualization.tex
│   │   ├── 03_literature_review.tex
│   │   ├── 04_methodology.tex
│   │   ├── 05_implementation.tex
│   │   ├── 06_evaluation.tex
│   │   └── 07_conclusion.tex
│   ├── figures/                        # All figures (reproducible; vector where possible)
│   ├── appendix/
│   └── references.bib
│
├── src/                                # AI system code
│   ├── market_data/                    # Market APIs (NYSE/NASDAQ) — live layer
│   ├── news_fetcher/                   # News APIs — live layer
│   ├── historical_kb/                  # Historical knowledge base (FNSPID)
│   ├── anomaly_detector/               # Abrupt-movement detection
│   ├── correlation_engine/             # News–market correlation / historical precedents
│   ├── explanation_engine/             # XAI engine — explanation generation
│   ├── impact_analyzer/                # Sector impact (related tickers) — OPTIONAL
│   ├── telegram_bot/                   # Alert bot
│   └── main.py                         # Entry point
│
├── notebooks/                          # Jupyter notebooks — experiments and validation
│
├── data/
│   ├── samples/                        # Small sample data (committable)
│   ├── literature/                     # Gated PDFs the student provides (GITIGNORED)
│   └── (large data — gitignored, recreated by download_data.py)
│
├── docs/
│   ├── analise_referencia.md           # Analysis of the reference dissertation
│   ├── analise_template_latex.md       # Analysis of the ISEP LaTeX template
│   ├── arquitectura_sistema.md         # Technical architecture documentation
│   ├── free_apis.md                    # Free APIs identified, evaluated and approved
│   ├── data_card.md                    # Dataset source/licence/subset/preprocessing (reproducible)
│   ├── setup.md                        # Environment & build setup (Python version, venv, LaTeX, CI)
│   ├── citation_log.md                 # Every reference + verified DOI/id + date checked
│   ├── risk_register.md                # Risks, likelihood/impact, mitigations, contingencies (§15)
│   ├── evaluation_design.md            # Evaluation plan per component (§16)
│   ├── learning.md                     # PT-PT explanations of each concept (for the student)
│   └── glossary.md                     # Glossary of technical terms (PT-PT)
│
├── progress/
│   ├── TRACKER.md                      # Per-session progress (checklist)
│   ├── PLANO_SESSOES.md                # Detailed ~30-session plan (+ buffer)
│   ├── QUESTIONS.md                    # Bank of likely jury questions + prepared answers
│   ├── DECISIONS.md                    # Decision log: what was decided, when, why
│   └── SESSIONS.md                     # Short log of each session (continuity)
│
└── presentation/
    └── outline_slides.md               # Defense slide-deck outline
```

---

## 10. (reserved)

*Numbering kept stable for cross-references; see §16 for evaluation and §15 for risk.*

---

## 11. `CLAUDE.md` — PERSISTENT MEMORY

This is the **most critical file** in the project. It is the primary mechanism of continuity across sessions and devices. Keep it current and compact (long enough to restore full context, short enough to read at the start of every session).

`CLAUDE.md` must always contain, up to date:

```markdown
# CLAUDE.md — Project Persistent Memory

## Current State
- Session number: [N]
- Last updated: [DATE/TIME]
- Current phase + last completed step: [...]
- IMMEDIATE next action: [PRECISE DESCRIPTION]
- Session integrity check: confirm this file and SESSIONS.md were read this session.

## Project Context
[Compact summary of all information in this ROOT PROMPT, including §3 (student profile) and the contribution framing.]

## Confirmed Decisions
- English variant (EN-GB/EN-US): [LOCK IN PHASE 0]
- Title chosen: [AFTER PHASE C]
- Approved APIs: [AFTER PHASE C]
- AI methodologies: [AFTER PHASE C]
- Chapter structure: [AFTER PHASE A]
(Full rationale in progress/DECISIONS.md)

## LaTeX State
- Written: [...]   - Missing: [...]   - Compilation issues: [...]

## Code State
- Implemented: [...]   - Missing: [...]   - Thin-slice smoke test status: [pass/fail]

## Verified References
[References already verified (with DOI/id) and approved for the .bib — pointer to citation_log.md]

## Open Questions / Waiting On Student
[e.g. ISEP AI policy, scope confirmation, ticker set, Telegram token]

## Permanent Rules
[Compact copy of §2 (Autonomy limits), §3, §5.3, §6, §8 DoD]
```

**ABSOLUTE RULE: `CLAUDE.md` is updated at the end of EVERY session, without exception.**

---

## 12. GIT WORKFLOW & MULTI-DEVICE ROBUSTNESS (continuity backbone)

Continuity is the project's top requirement, and naive git across devices is the most likely way to break it. Follow this exactly.

- **Single working branch** (`main`) unless the student wants feature branches. Keep history linear with **rebase**, not merge commits, for clarity.
- **Always start a session with a pull-rebase** (`start_session.sh`): `git pull --rebase origin main`. Never start work on stale state.
- **Always end a session with verify → commit → pull-rebase → push** (`end_session.sh`). The script **pulls before pushing** so a push is never rejected by surprise.
- **Conflict handling:** `CLAUDE.md` and the `progress/` files are the likely conflict points (edited every session on every device). If a rebase conflict occurs, the script **stops and tells the student** rather than guessing — never auto-resolve a conflict that could lose work, and never force-push to escape one.
- **`.gitattributes`** normalises line endings to LF (`* text=auto eol=lf`) and marks binaries (`*.pdf binary`, `*.png binary`) so Windows/macOS/Linux devices don't churn the diff.
- **Large data and models are never committed** — gitignored and recreated by `download_data.py`. If a binary genuinely must be versioned, use Git LFS and document it; otherwise keep the repo light.
- **Every commit message** is descriptive and in PT-PT; the session message names what changed and what's next.

---

## 13. AUTOMATION SCRIPTS

### `scripts/setup_env.sh`
```bash
#!/bin/bash
# Cria o ambiente virtual, instala dependências fixadas e verifica imports-chave.
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -c "import yfinance, transformers, sentence_transformers; print('Ambiente OK')"
echo "✅ Ambiente preparado."
```

### `scripts/start_session.sh`
```bash
#!/bin/bash
# Início de sessão: sincroniza e mostra o estado.
set -euo pipefail
git pull --rebase origin main
echo "—— CLAUDE.md (topo) ——"; head -n 40 CLAUDE.md || true
echo "—— Última sessão ——"; tail -n 20 progress/SESSIONS.md || true
echo "✅ Pronto. Lê o CLAUDE.md na íntegra antes de agir."
```

### `scripts/end_session.sh` (conflict-safe)
```bash
#!/bin/bash
# Fim de sessão: verifica, faz commit, sincroniza e publica — sem force-push.
# Uso: bash scripts/end_session.sh "Descrição breve da sessão"
set -euo pipefail
SESSION_MSG=${1:-"Progresso da sessão"}
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

# 1) Verificação antes de guardar (testes, lint, build).
bash scripts/verify.sh

# 2) Aviso de segredos: aborta se algo parecer um segredo no diff em stage.
git add .
if git diff --cached | grep -E -i '(api[_-]?key|secret|token|password|bearer)\s*[:=]' ; then
  echo "❌ Possível segredo detetado no commit. A abortar. Verifica e remove."
  git reset
  exit 1
fi

# 3) Commit.
git commit -m "Sessão — $TIMESTAMP: $SESSION_MSG" || echo "Nada para fazer commit."

# 4) Sincroniza ANTES de publicar (evita rejeição por non-fast-forward).
if ! git pull --rebase origin main ; then
  echo "❌ Conflito de rebase. NÃO faço force-push. Resolve manualmente e corre de novo."
  exit 1
fi

# 5) Publica.
git push origin main
echo "✅ Sessão verificada, guardada e sincronizada com o GitHub."
```

### `scripts/verify.sh`
```bash
#!/bin/bash
# Verificação única: testes + lint + (confirmação de) build LaTeX.
set -uo pipefail
echo "—— Testes ——"; python -m pytest -q || { echo "❌ Testes falharam"; exit 1; }
echo "—— Lint ——";  ruff check src tests || echo "⚠️ Avisos de lint (não bloqueante)."
echo "ℹ️ O PDF é compilado pela GitHub Action em cada push (fonte de verdade)."
echo "✅ Verificação concluída."
```

### `.github/workflows/compile-thesis.yml`
A GitHub Action that compiles the LaTeX automatically on each push and publishes the PDF as an artefact. Use `xu-cheng/latex-action` or equivalent. Any secret the CI needs goes in **GitHub Actions Secrets**, never in the YAML. The compiled PDF is then available on GitHub for every commit — useful for reviewing the document without compiling locally.

---

## 14. PER-SESSION WORKFLOW

### Start of session (always)
1. `bash scripts/start_session.sh` (pull-rebase + show state).
2. Read `CLAUDE.md` in full.
3. Read the last entry of `progress/SESSIONS.md`.
4. Check `progress/PLANO_SESSOES.md` for the day's tasks.
5. **Tell the student, in 3–4 lines: current phase, last completed step, and the exact action you will take now** — before doing it, so he can confirm or redirect.
6. Execute the planned tasks.

### End of session (always, without exception)
1. Update `CLAUDE.md` with the current state and precise next steps.
2. Add an entry to `progress/TRACKER.md`.
3. Add a summary to `progress/SESSIONS.md`.
4. Update `progress/DECISIONS.md` if any decision was made.
5. Run `bash scripts/end_session.sh "session description"` (this verifies, commits, syncs, pushes).
6. Give the student a 3–5 line summary of what was done and what comes next, plus anything you need from him.

---

## 15. RISK REGISTER (`docs/risk_register.md`)

Maintain a living risk register. Each entry: risk, likelihood, impact, mitigation, contingency. Seed it with at least these:

| Risk | Mitigation | Contingency |
|---|---|---|
| **Lost continuity / lost device** | Push every session; `CLAUDE.md` always current; repo is the single source of truth | Any device clones the repo and resumes from `CLAUDE.md` |
| **FNSPID too large for a laptop** | Subselect tickers + time window early; document in `data_card.md` | Shrink the subset further; the methodology is unchanged |
| **A free API changes / removes its free tier** | Don't assume; verify in Phase C; keep `yfinance` + RSS fallbacks | Swap to another free source; document the swap |
| **Fabricated/unverifiable citation** | Citation-Integrity Protocol (§6.4); verify every DOI | Drop the citation; never guess |
| **LaTeX won't compile** | CI builds on every push; fix immediately, never let it linger | Bisect the last change; keep `main` always-compiling |
| **Scope creep / September crunch** | Scope discipline (§5.3); ask before adding complexity | Cut optional components (§5.3); ship the thin, complete system |
| **Student can't defend a component** | Teach-as-you-go (§3); 3-sentence defense per component | Simplify or remove it — undefendable ≠ shippable |
| **Secret committed** | Pre-commit secret scan (§13); secrets only in `.env` | Stop, rotate the secret, scrub from history with care |

---

## 16. EVALUATION DESIGN (`docs/evaluation_design.md`)

Define the evaluation **before** running it (no fishing for good numbers). Keep every method defensible and explainable.

- **Anomaly detector:** report precision/recall against a clearly-defined notion of "true" anomalies (e.g. days with confirmed large moves/known events in the chosen window). State the labelling rule explicitly; acknowledge its limits.
- **Correlation / precedents engine (the core):** evaluate retrieval quality (are the retrieved historical news items genuinely analogous?) and the measured impact (event-study returns at +1/+3/… days). Where simple, include a **baseline** (e.g. random or recency-based retrieval) to show the embedding approach adds value, and a small **ablation** (e.g. similarity metric or window choice) — only as far as it stays explainable.
- **Explanation engine (XAI):** define a clear notion of explanation quality (faithfulness to the actual logic; usefulness to a retail investor). A small, honest human-judgement protocol (even a rubric the student applies to N examples) beats a vague claim.
- **Rigour throughout:** no lookahead; fixed seeds; report uncertainty/variance where it matters; a modest, honest result is a valid thesis result. Never present a number you cannot reproduce and explain.

---

## 17. DEFENSE PREPARATION

- Maintain `progress/QUESTIONS.md`: a growing bank of likely jury questions with prepared answers. Seed it with the hard ones:
  - *"Where is your contribution — isn't this just integrating existing tools?"* → frame via §3 (integration, application, critical evaluation, a documented correlation methodology = the engineering contribution).
  - *"Why is the system explainable?"* → walk the transparent pipeline end to end.
  - *"How do you avoid lookahead / data leakage?"* → point to §6.5 and the documented windows.
  - *"Why these methods and not fancier ones?"* → defensible simplicity (§3, §5.5).
- After the system stabilises, run a **mock defense / red-team pass**: the agent challenges the thesis as a sceptical examiner would, and the student practises answering. Capture weak spots and fix them.
- The defense slide narrative lives in `presentation/outline_slides.md` and tells one clear story: problem → why it matters → approach → what was built → how it's explainable → evaluation → honest limitations → contribution.

---

## 18. SESSION PLAN (created/refined in Phase C — flexible, quality-driven)

`progress/PLANO_SESSOES.md` holds a detailed plan for **~30 sessions plus a buffer**, with specific tasks, weekly milestones, dependencies, and explicit contingency room. The count is a guide: **add sessions if quality needs it; do not pad for the sake of a number.** Suggested logical sequence:

- **Session 0:** Setup & Authorization (Phase 0) — environment, scaffolding, permissions, secrets, first commit.
- **Sessions 1–2:** Analysis of reference files + planning.
- **Sessions 3–6:** Contextualisation + literature review.
- **Sessions 7–9:** Methodology + architecture.
- **Sessions 10–11:** Thin end-to-end slice (one trigger → Telegram alert with minimal explanation).
- **Sessions 12–18:** Component development (historical base, anomalies, correlation, explanation, bot).
- **Sessions 19–22:** Testing, evaluation, results.
- **Sessions 23–26:** Writing — implementation + evaluation + conclusion.
- **Sessions 27–28:** Global review and refinement + mock defense.
- **Sessions 29–30:** Slide deck + defense preparation.
- **Buffer (29–33+):** contingency for slippage, deeper evaluation, extra figures, or extra teaching where the student needs it.

---

## 19. PHASE 0 — SETUP & AUTHORIZATION (RUNS BEFORE EVERYTHING)

> Goal: get the project **100% scaffolded and safe before any real work begins** — automatically where possible, and with a clear checklist of the few things only the student can do. **Do not start Phase A until Phase 0's Definition of Done is met.**

### ▶ 0.1 — Environment verification
- [ ] Confirm Git, Python (pin the version), and Node are available; confirm the GitHub remote is reachable. Report versions.
- [ ] Confirm GitHub authentication is configured (via `gh auth login`, SSH key, or a credential helper holding a fine-grained PAT). **Do not paste any token into a file** — if auth is missing, tell the student exactly how to set it up.
- [ ] Confirm the LaTeX strategy: CI as source of truth; note optional local install in `docs/setup.md`.

### ▶ 0.2 — Permission scaffolding (`.claude/settings.json`)
- [ ] Create `.claude/settings.json` to pre-authorise the safe, high-frequency operations so the student isn't approving routine actions constantly, while keeping the §2.2 hard limits behind confirmation.
- [ ] **Verify the exact current schema** at the official Claude Code docs before relying on it: https://docs.claude.com/en/docs/claude-code/overview (and the settings/permissions pages). The block below is *illustrative* — adjust keys to the current docs.

```jsonc
// .claude/settings.json — ILUSTRATIVO. Confirmar a sintaxe exacta nos docs actuais.
{
  "permissions": {
    "allow": [
      "Read", "Edit", "Write",
      "Bash(git add:*)", "Bash(git commit:*)", "Bash(git pull:*)", "Bash(git push origin main:*)",
      "Bash(python -m pytest:*)", "Bash(ruff:*)",
      "Bash(bash scripts/*.sh:*)",
      "WebSearch", "WebFetch"
    ],
    "deny": [
      "Bash(git push --force:*)", "Bash(git push --force-with-lease:*)",
      "Bash(git reset --hard:*)", "Bash(git clean -fdx:*)",
      "Bash(rm -rf /*)", "Bash(sudo:*)"
    ]
  }
}
```
> If you prefer fully unattended runs, Claude Code's auto-accept ("skip permissions") mode exists — but **do not enable it for arbitrary Bash**: that is exactly when an agent can do damage. A broad allowlist + small denylist (above) gives near-frictionless autonomy while keeping the bright lines. Confirm the current flag/behaviour in the docs.

### ▶ 0.3 — Secrets & ignore scaffolding
- [ ] Create `.gitignore` (LaTeX artifacts, `__pycache__`, `.venv`, `.env`, large data, models, `data/literature/`).
- [ ] Create `.gitattributes` (`* text=auto eol=lf`; mark `*.pdf`, `*.png` as binary).
- [ ] Create `.env.example` with variable **names only** (e.g. `TELEGRAM_BOT_TOKEN=`, `TELEGRAM_CHAT_ID=`, `FINNHUB_API_KEY=`). **No values.**
- [ ] Confirm `.env` is gitignored and (if present locally) never staged.

### ▶ 0.4 — Confirm configuration with the student
- [ ] Confirm the **Language Policy** (§0) — especially **EN-GB vs EN-US**, and whether learning docs stay PT-PT (default) or switch to EN.
- [ ] Confirm the pinned **Python version**.
- [ ] Surface the **human-only checklist** (below) and record what's still pending in `CLAUDE.md` → "Open Questions".

### ▶ 0.5 — First scaffold commit
- [ ] Create the skeleton from §9 (directories + placeholder files), `CLAUDE.md`, `README.md`, the scripts (and `chmod +x`), and the CI workflow.
- [ ] `bash scripts/verify.sh` (an empty test suite passing is fine at this stage).
- [ ] First commit: `git add . && git commit -m "Sessão 0 — Setup e autorização" && git push`.

### Phase 0 — Definition of Done
- [ ] Environment verified; GitHub auth working; LaTeX strategy decided.
- [ ] `.claude/settings.json`, `.gitignore`, `.gitattributes`, `.env.example` in place.
- [ ] Language variant and Python version confirmed by the student.
- [ ] Skeleton committed and pushed; CI runs.
- [ ] `CLAUDE.md` initialised with state, next action, and open questions.

---

## 20. FIRST SESSIONS — PHASES A–E (after Phase 0)

Execute phases in order. **Do not advance without meeting each phase's DoD (§8).**

### ▶ PHASE A — Analysis of reference files
> These two files are already present at the repo root: `dissertacao_Rafael_Silva.pdf` (a high-grade reference dissertation from the same programme) and `Modelo Dissertacao MEIA_latex v2/` (the official ISEP LaTeX template).
- [ ] Analyse `dissertacao_Rafael_Silva.pdf` → `docs/analise_referencia.md`: full table of contents (all chapters/sections/subsections with numbering), total page count, approximate reference count, inventory of visual artefacts by chapter (images, tables, diagrams, charts, figures), and a writing-style assessment (tone, density, formality, paragraph structure). *This is the quality/size benchmark — not a template to copy verbatim.*
- [ ] Analyse `Modelo Dissertacao MEIA_latex v2/` → `docs/analise_template_latex.md`: full file structure, LaTeX packages and versions, formatting rules/styles/naming conventions, and what is predefined vs. what must be filled/adapted. *All LaTeX work must respect this template without exception.*

### ▶ PHASE B — Repository structure
- [ ] Create the full file/directory structure of §9 (any parts not already created in Phase 0).
- [ ] Create `CLAUDE.md` (full context, including §3 and the contribution), `README.md`, `requirements.txt` (pinned) + lockfile, and the data/docs/progress files.
- [ ] Create `docs/learning.md` and `docs/glossary.md` (empty, ready to fill).
- [ ] Ensure scripts are executable (`chmod +x`).
- [ ] Commit.

### ▶ PHASE C — Planning and technical decisions
- [ ] Propose **3 academic titles** (also evaluate the one suggested in §4).
- [ ] Propose a **detailed technical architecture** with a textual component diagram and the two data layers (historical vs. live).
- [ ] Investigate and document **free APIs** in `docs/free_apis.md` — verifying NYSE/NASDAQ coverage, history, rate limits and reliability, and confirming the historical (FNSPID) vs. live (APIs) separation.
- [ ] Propose **AI methodologies** per component, simple and defensible (§5.5), with academic justification.
- [ ] Write `docs/evaluation_design.md` (§16) and seed `docs/risk_register.md` (§15).
- [ ] Create `progress/PLANO_SESSOES.md` (~30 sessions + buffer).

### ▶ PHASE D — LaTeX setup
- [ ] Create `thesis/main.tex` based on the ISEP template (adapt, don't blindly copy).
- [ ] Create the 7 chapter files with section structure (based on Phase A).
- [ ] Create `thesis/references.bib` with a base structure (entries enter only once verified — §6.4).
- [ ] Test compilation — it must compile without errors (CI confirms).

### ▶ PHASE E — Close the session
- [ ] Update `CLAUDE.md` with post-setup state and the immediate next action.
- [ ] First entries in `progress/TRACKER.md`, `progress/SESSIONS.md`, and `progress/DECISIONS.md`.
- [ ] `bash scripts/end_session.sh "Setup inicial completo — estrutura criada, ficheiros analisados, planeamento definido"`.
- [ ] **Tell the student clearly what you need from him** (ISEP AI-use policy, scope confirmation with the supervisor, ticker set and time window, Telegram token) and the next action.

---

## 21. PERMANENT RULES

```
STUDENT & LEARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Explain every concept in PT-PT before using it (docs/learning.md)
✅ The student must be able to defend everything we deliver
✅ Defensible simplicity > sophistication
❌ Nothing the student doesn't understand goes into the thesis

CODE & LATEX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Comments in code and LaTeX: PT-PT
✅ Clean, organised, documented code, with tests
✅ Reproducible: pinned deps, fixed seeds, regenerable figures
❌ No unnecessary or duplicated files

ACADEMIC CONTENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Contextualisation: current market data (2025–2026)
✅ Literature: seminal + recent; peer-reviewed (IEEE/ACM) first
✅ Comparative tables in the literature review
✅ Visual artefacts comparable in quantity to the reference
✅ Every claim has a source; every technical decision has a justification
✅ EVERY citation verified against a real DOI/id (citation_log.md) — no fabrication
✅ AI use declared per ISEP rules; datasets/models attributed
❌ No unreferenced claims, ever

WRITING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Thesis in English, consistent (EN-GB/EN-US locked)
✅ Natural, high-quality writing in the reference's register
✅ Clear and direct — no room for jury doubt
✅ Written in passes; the student reviews/edits every section
✅ Quality > Quantity
❌ No generic phrases, repetitive patterns, or empty content

TECHNICAL SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Free APIs only
✅ NYSE/NASDAQ focus
✅ History via FNSPID; live via free APIs
✅ XAI-first — all logic exposed to the user
✅ Alerts via Telegram Bot
✅ Thin end-to-end slice first; complexity later
❌ No price prediction, no algorithmic trading, no paid APIs

AUTONOMY, GIT & CONTINUITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Broad autonomy within the §2.2 bright lines
✅ Verify (verify.sh) before committing; commit + push every session
✅ CLAUDE.md updated at the end of every session
✅ Start with pull-rebase; end_session pulls before pushing (conflict-safe)
✅ Repository always synced — accessible from any device
❌ Never commit .env/secrets, large data, or models
❌ Never force-push, rewrite pushed history, or auto-resolve conflicts that risk losing work
❌ Never fabricate data, results, or citations
❌ Never automate publisher-portal logins; never spend money
```

---

## 22. FINAL SUCCESS CRITERIA

The project is complete when:
- [ ] The LaTeX dissertation compiles without errors and is complete in English.
- [ ] Pages, citations and visual artefacts are comparable to the reference dissertation.
- [ ] **Every citation is verified (citation_log.md) — zero fabricated references.**
- [ ] The AI system is functional and demonstrable (operational, tested code; `verify.sh` green).
- [ ] Telegram alerts work with traceable explanations; the thin-slice smoke test passes.
- [ ] The environment is reproducible from a clean machine (`setup_env.sh`).
- [ ] **The student can explain and defend every component and every section.**
- [ ] `progress/QUESTIONS.md` holds likely jury questions with prepared answers — including "where is your contribution / isn't this just integrating tools?" and "why is the system explainable?".
- [ ] A mock-defense / red-team pass has been done and weak spots addressed.
- [ ] The defense slide deck is complete.
- [ ] The Git repository is clean, documented, synced, and free of secrets.

---

## APPENDIX — HUMAN-ONLY SETUP CHECKLIST (only the student can do these)

These cannot and should not be automated by the agent. ~5–10 minutes total.

1. **GitHub auth on each device:** `gh auth login` (or set up an SSH key / fine-grained PAT in the credential helper). *Don't paste tokens into files.*
2. **Telegram bot:** talk to **@BotFather**, create a bot, get the **token**; get your **chat id**. Put both in a local `.env` (gitignored), and add their *names* to `.env.example`.
3. **Free-API keys (as needed):** register for Finnhub / Alpha Vantage / GNews free tiers; store keys in `.env` only.
4. **ISEP AI-use policy:** get the exact MEIA policy on declaring AI assistance; if unsure, confirm with Prof. Luís Gomes. Tell the agent so it can comply.
5. **Decisions to lock in Phase 0:** EN-GB vs EN-US; whether learning docs stay PT-PT; the pinned Python version.
6. **Gated literature:** when the agent flags a paper behind IEEE/ACM access, download the PDF yourself (institutional access) into `data/literature/` (gitignored) for it to read. The agent finds papers via open APIs (Crossref/OpenAlex/Semantic Scholar/arXiv) and cites the published version.
7. **Reference files:** confirm `dissertacao_Rafael_Silva.pdf` and `Modelo Dissertacao MEIA_latex v2/` are at the repo root before Phase A.
8. **GitHub Actions Secrets:** if CI needs any secret, add it under the repo's Actions Secrets (not the YAML).

---

*End of Root Prompt (v3). Begin with Phase 0, then Phase A.*
