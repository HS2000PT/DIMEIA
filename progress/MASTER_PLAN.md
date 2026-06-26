# MASTER PLAN — DIMEIA / CLARION (the long road to submission, publication & defence)

> **Purpose.** One committed roadmap for the whole remaining mission, so work can continue **on any device,
> any day**, always picking up where it stopped. This file is the spine; `progress/TRACKER.md` holds the
> per-session checklist and `CLAUDE.md` holds the live "next action". Read all three at the start of a session.
>
> **How to resume each day:** (1) `git pull`; (2) read `CLAUDE.md` → *Próxima ação*; (3) open the current
> Phase below, find the first unchecked `[ ]`; (4) do it; (5) end the session: build + verify + commit + push
> and tick the box + update `CLAUDE.md`/`SESSIONS.md`.

## Non-negotiable guardrails (apply in EVERY phase)
- **Citations: zero fabrication.** No reference enters `references.bib` without a verified DOI/arXiv/primary
  identifier logged in `docs/decisions/citation_log.md`. Cited set = bib set = rendered set. This is the
  single biggest risk to the whole thesis — treat it as sacred.
- **No fabricated data, results or numbers.** Every number comes from a versioned script with a fixed seed.
- **The text is the student's.** Henrique reviews and owns every chapter (§6.6); the voice stays natural,
  measured, human — not "AI". Quality over page count; never pad.
- **EN-GB** in the thesis; **PT-PT** in the defence guide and internal docs.
- **Each session ends green:** compiles (0 errors, 0 undefined citations, 0 overfull >15pt), tests + ruff pass,
  everything committed and pushed.

## Current status snapshot (start of the long road)
- Thesis: **68 pp**, 6 chapters, **40 verified references**, 6 figures + inline diagrams; compiles clean.
- Voice: examiner-validated on Ch1 (16–18/20); naturalness pass largely done; consistency pass ongoing.
- Code: 41 tests green, ruff clean; venv 3.12 with full ML stack (torch + SBERT) present in this environment.
- Known waste: **List of Algorithms** and **List of Source Code** are empty (no algorithms/listings yet);
  `twoside` adds blank verso pages.

---

## PHASE A — Content & visuals to ~80 pp (fix the "empty pages")
*Goal: reach ~80 pp with genuine, examiner-friendly content and the visual workflow the student wants — not padding.*
- [ ] **A1. Algorithm pseudocode floats** (populate the empty List of Algorithms): z-score anomaly detection;
      precedent retrieval (CBR retrieve+reuse); event-study impact; knowledge-base build. (~3 pp, formal & defensible)
- [ ] **A2. End-to-end data/step workflow figure** — one full-page diagram of the whole pipeline (sources →
      KB build → triggers → engines → explanation → Telegram), reused later in the defence guide.
- [ ] **A3. Supporting visuals**: alert sequence diagram (time-ordered); embedding/retrieval concept figure
      (headline → vector → nearest neighbours); event-study timeline (event day, +1/+3/+5 d).
- [ ] **A4. Worked numeric examples** (pedagogical, "with examples" per the brief): a small z-score worked
      table (returns → rolling mean/std → z → decision); a worked precedent-retrieval example.
- [ ] **A5. Resolve empty lists**: either keep List of Algorithms (now populated by A1) and **remove the empty
      List of Source Code**, or populate it; remove any other near-empty front-matter list.
- **Done when:** ~80 pp; every new float referenced in text; List of Algorithms non-empty; no empty list pages;
  compiles clean.

## PHASE B — Finish the naturalness / consistency pass
*Goal: the whole document reads like Ch1 (examiner-validated), consistently.*
- [ ] B1. Ch2 body (technical sections kept formal; transitions/topic sentences naturalised).
- [ ] B2. Ch3 (Methods), Ch4 (CLARION), Ch5 (Case Studies) narrative prose to the same standard.
- [ ] B3. Global: em-dash density down, no pet-phrase clusters, no meta-signposting, short-sentence rhythm kept.
- **Done when:** a read-through finds no "AI tells"; the student confirms the voice on a sampled chapter.

## PHASE C — Independent critical thesis review (from zero)
*Goal: an external-examiner pass over the finished-content document; find weaknesses/wrongs; fix them.*
- [ ] C1. Cold read of all 6 chapters + front/back matter; produce a findings log (`docs/decisions/review_log.md`).
- [ ] C2. Categorise: factual errors, unsupported claims, logical gaps, structure, clarity, figures.
- [ ] C3. Fix every finding; re-read to confirm; nothing left unaddressed.
- **Done when:** the review log shows every finding fixed or explicitly, defensibly deferred.

## PHASE D — Critical implementation & design review (+ "how to run")
*Goal: confirm the system is the right way to meet the goals, works in real life, is useful — and is runnable.*
- [ ] D1. Design critique: is z-score / SBERT / event-study / CBR the best defensible choice for each goal?
      Document the alternatives considered and why the choice stands (or change it if it does not).
- [ ] D2. Real-world viability: end-to-end runnability, scheduling/deployment gap, API limits, failure modes,
      usefulness to an actual retail investor; state honestly what is prototype vs production.
- [ ] D3. **"How to run it" guide** (`docs/design/how_to_run.md` + README section): exact steps from clone →
      env → keys → build KB → run both triggers → receive a Telegram alert.
- [ ] D4. Validate experiments + statistics: multi-seed already done; add significance/dispersion where it
      strengthens claims; confirm baselines are fair; confirm no lookahead; reproduce every reported number.
- **Done when:** the design is defended in writing, the system runs from a clean checkout per the guide, and
  every statistic is reproduced and sound (this also gates the IEEE paper).

## PHASE E — Final ultra-rigorous validation (SUBMISSION GATE) — mandatory, zero misses
*Goal: nothing for the jury to attack. Everything transparent, explained, with examples.*
- [ ] E1. **Page-by-page check** of the compiled PDF, one page at a time, against a checklist (text, figures,
      tables, captions, cross-refs, numbers, spacing). Log each page in `docs/decisions/page_audit.md`.
- [ ] E2. **Full citation re-verification**: re-check EVERY entry in `references.bib` against its source
      (DOI/arXiv/publisher); re-confirm cited = bib = rendered; 0 undefined; 0 unverifiable. Re-log all.
- [ ] E3. Consistency sweep: every number identical across chapters/abstract/conclusions; acronyms defined;
      no PT in the EN body; figures all EN; no overfull boxes.
- [ ] E4. Reproducibility check: a clean run regenerates every figure/number; tests + CI green.
- [ ] E5. Front matter: integrity + AI-use declaration final (confirm exact ISEP wording — human input);
      submission date set.
- **Done when:** the page audit and citation re-verification are 100% complete with zero open items; thesis is
  declared **submission-ready**.

## PHASE F — IEEE publication (only after D + E validated)
*Goal: a conference/journal paper derived from the validated work.*
- [ ] F1. New `paper/` dir with the IEEE template (IEEEtran); pick target venue/format.
- [ ] F2. Condense the validated thesis into the paper (8-ish pp): problem, method (CLARION), evaluation, results.
- [ ] F3. Every claim/number traced to the validated experiments; citations verified (same guardrail).
- [ ] F4. Compile clean; co-author/supervisor review.
- **Done when:** a complete, honest, compiling IEEE paper exists, consistent with the thesis.

## PHASE G — Defence presentation slides
- [ ] G1. Slide deck (problem → contribution → system → results → limitations → demo) with the workflow visual.
- [ ] G2. Timed to the defence slot; speaker notes; backup slides for hard questions.
- **Done when:** a complete deck exists, aligned with the thesis and the defence guide.

## PHASE H — Improved defence guide (PT-PT, visual)
- [ ] H1. Extend `docs/defence/caderno_de_defesa.md` with the **visual data/step workflow** (the A2 diagram)
      and step-by-step walkthroughs with examples.
- [ ] H2. Ensure every component, decision and result has a "como explico em 3 frases" + a worked example.
- **Done when:** the student can study and visualise the entire workflow and reasoning from one PT-PT document.

---

## Whole-mission Definition of Done
Thesis ~80 pp, natural and consistent, **submission-ready** (page audit + citation re-verification 100%, zero
attack surface), the implementation defended and runnable from a clean checkout, an IEEE paper drafted from the
validated work, defence slides ready, and a visual PT-PT defence guide complete. Everything honest, reproducible,
and the student's own.

## Sequencing & cadence
A → B → C → D → **E (gate)** → F → G → H. (H can begin in parallel once A2's workflow figure exists.)
Each phase is multiple sessions; tick boxes here, mirror status in `TRACKER.md`, update `CLAUDE.md` next-action,
commit + push every session for multi-device continuity.
