# MASTER DIRECTIVE v2 — a clean start, written from what v1 cost

> **What this is.** A complete, self-contained mandate for building an AI-Engineering Master's
> dissertation project from an empty repository. It replaces the v1 directive. It is written after
> 57 sessions of building the first one, and its main advantage over v1 is not ambition — it is
> knowing exactly where that ambition went wrong.
>
> **Read §0 and §1 before anything else. They are the parts that decide whether this succeeds.**

---

## §0. How to read this, and what beats what

This document is a **contract**, not inspiration. When two parts of it conflict, this is the order
of precedence:

1. **Truth.** Nothing may be claimed that is not measured. This beats everything, including me.
2. **The deadline.** A brilliant unfinished dissertation scores zero.
3. **The examiner's questions.** Every decision must survive *"why?"* asked twice.
4. **Scope discipline.** Depth on three things beats breadth on twelve.
5. **Everything else in this document.**

If you (the assistant) find that following an instruction here would produce a false statement,
**stop and say so**. That is not disobedience; it is the primary requirement.

### The single question this project must answer well

> **What intelligent capability does the system learn, from which data, why is that the right thing
> to learn, how do we know it works, how do we explain it to a non-expert, and which part of that
> intelligence is genuinely ours?**

If a session's work does not move that question forward, it is probably busywork.

---

## §1. THE ONE DECISION THAT DETERMINES THE GRADE

Read this section twice. Everything else is downstream of it.

### 1.1 The lesson v1 paid the most for

The first project chose, as its central learning task: **"given a news headline and market context,
predict whether an abnormally large price move follows."**

It was engineered carefully — anti-lookahead labels enforced by mutation tests, temporal splits with
embargo, Platt calibration, cluster bootstrap, conformal prediction. The engineering was not the
problem. The result was:

- no text model beat a **volatility-only baseline** (PR-AUC 0.542 vs 0.496), and that negative
  survived a fair re-test, a change of metric, a cluster bootstrap, and all nine label definitions;
- in deployment the gate ranked at **chance** (ROC-AUC 0.494, cluster CI [0.391, 0.601]);
- a **13-constant lookup table** of per-ticker median volatility beat the trained model on the
  product metric (0.662 vs 0.632).

The honest reading is not "the model was bad". It is: **the task was chosen at the edge of market
efficiency, where the signal barely exists.** If headlines reliably predicted abnormal returns, the
information would already be in the price. The project spent its central learning effort on a task
whose answer was close to "you cannot", and then had to defend a negative result as its
contribution.

A negative result reported honestly *is* defensible — v1 defended it well. But you only get one
central learning task, and it should be one where **learning demonstrably beats not-learning**.

### 1.2 The rule

> **Choose a learning task whose signal provably exists, whose labels can be obtained honestly, and
> whose success is visible to the user.**

Before committing to *any* central learning task, run this test:

| Test | Pass condition |
|---|---|
| **Signal exists** | Can you name a mechanism by which the label is determined by the input? "Efficient markets already priced it in" is a failing answer. |
| **Labels are obtainable** | Can you produce ≥500 trustworthy labels without fabricating any? Human annotation of 300 items in an afternoon is a legitimate answer. |
| **A dumb baseline can lose** | Can you state a simple baseline, and is it plausible that learning beats it? If the baseline is obviously unbeatable, pick another task. |
| **⚠️ Outcome is uncertain** | Can you state, **in writing and before running**, a specific mechanism by which the learned model *loses* on your data? **If you cannot, this is a demonstration, not a study.** |
| **⚠️ Commodity check** | Name the off-the-shelf solution (MinHash, SimHash, a stock sentence-transformer, a keyword rubric) and the exact condition under which it fails **on your data and under your constraints** — domain vocabulary, CPU/latency budget, label distribution, cost asymmetry. If it fails nowhere, the model is not your contribution: relocate the contribution explicitly to the decision layer, the dataset, the guarantee or the evaluation, and say so in §3.0. |
| **The user sees it** | If the model improves, does something visibly improve for the user? |
| **Failure is informative** | If the model loses, do you learn something worth a chapter? |

> **Why the two ⚠️ rows exist.** Without them this section trades v1's error for its mirror image.
> v1 asked a hard question and got a negative answer. The temptation here is to ask an easy question
> whose answer is known in advance — *"do sentence embeddings beat Jaccard on near-duplicates?"* —
> and a jury reads a foregone positive as an undergraduate lab exercise. **That is worse than v1's
> honest negative.** The uncertainty must be real, and it usually lives in the *decision* the model
> feeds, not in the model's accuracy.

**Run a 2-day feasibility spike on the task before building anything around it.** Label 200 items
by hand, train a logistic regression, look at the number. If the ceiling is chance, change the task
now — not in month four.

### 1.3 Tasks that pass this test in this domain (ranked)

These are candidates, not orders. Pick **one** as central; the others may become secondary.

1. **Novelty-aware delivery under an attention budget.** Not *"can embeddings beat Jaccard at
   detecting duplicates?"* — that answer is known, and framing it that way fails the commodity
   check. The research object is the **decision**: *given a fixed number of alerts a reader will
   tolerate per week, what should be suppressed as already-told, and what does that cost in missed
   distinct events?* The outcome is genuinely unknown, because it depends on the duplicate rate in
   your corpus, on the cost asymmetry between a repeat and a miss, and on where the operating point
   sits — none of which you know in advance. Measured in **distinct events delivered per week** and
   **repeats suppressed**, against a tuned lexical threshold, not against a strawman.
   Labels are cheap and reliable (annotate pairs; agreement is high), it directly serves alert
   fatigue, and the improvement is visible to the user. **v1 never built this** — it shipped a
   hand-tuned Jaccard threshold of 0.6 and never evaluated it, and separately measured that its
   precedent deduplication was exact-text only.
2. **Relevance classification.** *"Is this article actually about this company, or is it a
   market-roundup listing twenty tickers?"* v1 solved this with hand-written rules and measured that
   the rules discard **64.3%** of arrivals for "no mention" and 3.0% as boilerplate — a strong,
   honest baseline that a learned model can be compared against. Labels: annotate 400 headlines.
3. **Event-type classification.** *"Is this an earnings item, a regulatory action, a product launch,
   an analyst action?"* Weak supervision from keyword rubrics, then a learned classifier that beats
   the rubric. v1 measured an event taxonomy (AMI 0.358 vs 0.188 for ticker) and found it too weak
   to filter on — but that was *clustering*, not supervised classification. Supervised is a
   different and more promising question.
4. **Importance ranking with human feedback.** Requires a feedback loop and users; strong if you can
   get them, a trap if you cannot.

**Explicitly weaker central choices:** predicting price direction (forbidden — see §2.3), predicting
abnormal-return magnitude (v1's negative), sentiment scoring as an end in itself (solved, commodity).

### 1.4 What the market-reaction question becomes

It does not disappear. It becomes a **secondary, honestly-negative study** — which is genuinely
valuable and cheap, because you can reuse the same pipeline. Report it as: *"we also asked whether
headlines predict abnormal moves; on our corpus, they do not beat a volatility baseline, and here is
the evidence."* One chapter section, not the centrepiece.

---

## §2. HARD CONSTRAINTS

### 2.1 The deadline is a design input, not a background fact

Fix the submission date on day one and **write it into the plan file**. Then plan in **dated weeks
against a stated weekly hour budget** — never in percentages. A plan expressed as percentages of an
unknown denominator cannot visibly slip; a line reading *"planned 15 h, spent 6"* can.

Write your assumed weekly hours into `PROJECT_PLAN.md` and log actual hours in `CONTINUITY.md` each
session.

A 26-week shape (adjust to your own calendar, keep the structure):

| Wk | Phase | Ends with | Author-bound share |
|---|---|---|---|
| 1 | Setup, supervisor kickoff, deadline fixed | Repo skeleton, gate runner, plan file | low |
| 2–3 | Collection spike + task selection (§1) | Task chosen, **feasibility spike run** | **high** |
| 4–6 | Thin end-to-end slice | Something a user can run, however ugly | low |
| 7–8 | Annotation of the frozen set + leakage tests | Labelled set, rubric, κ, mutation test | **high** |
| 9–12 | Central model + RQ1 evaluation | Frozen results, baselines beaten or honestly not | medium |
| 13–14 | RQ2: the deployed-distribution study | Decision log instrumented and labelled | medium |
| 15–17 | Product, explanation layer, deployment | Acceptance criteria met, deployed | low |
| 15–16 | **Human study (calendar-bound, runs in parallel)** | Data collected | **high** |
| 18–22 | Writing and propagation | Thesis compiles, every number traced | **high** |
| 23–24 | Slack — unallocated | — | — |
| 25–26 | Final read, supervisor pass, submission | Signed and delivered | **high** |

Three rules that make this survive contact:

1. **Every phase ends with its thesis section drafted, not only its code.** Writing is a parallel
   track, not a final phase. v1's most expensive defects surfaced in the last week and each
   propagated to ~20 files.
2. **The slack rows are not scope buffer.** If unused, they buy "Should" items from §14 — never new
   scope.
3. ⚠️ **Separate assistant-throughput work from author-bound work, and never let the schedule
   assume the assistant absorbs the second.** Code, scaffolding and document mechanics compress
   enormously with an assistant. **Annotation, critically reading generated output, running the
   study, and writing sentences you can defend at a viva do not compress at all.** Those four sit at
   both ends of the schedule and are the ones always underestimated. If a phase is more than ~40%
   author-bound, it cannot be rescued by working the assistant harder — it must be *started
   earlier*.

### 2.2 Resources

- **Free tiers only** unless a paid source is justified in writing and approved. This is a real
  constraint and it becomes a *measured limitation* in the thesis, which is worth more than a
  capability you bought.
- One machine, CPU only. Assume no GPU. This forces sensible model choices and is defensible.
- Deployment must be free or student-credit funded, and must survive the assistant not being there.

### 2.3 Non-negotiable design constraints

- **Never predict price direction.** Not as a feature, not as a number, not implied by phrasing.
  This is the constraint that makes every output checkable: a statement about what already happened
  can be verified against the record; a forecast cannot.
- **Materiality is not direction.** If you predict "an unusually large move in either direction",
  that *is* a statement about the future and must be labelled as such. v1 shipped an alert saying
  "not a forecast" about exactly such a number; it was false and had to be corrected. Say what you
  predict, precisely, or predict nothing.
- **No fabricated anything.** See §6.
- **No personal data.** No portfolios, no holdings, no financial advice. This keeps you clear of
  GDPR and of MiFID II's advice boundary, and the refusal is a defensible position, not a gap.

---

## §3. RESEARCH PROBLEM, CONTRIBUTION AND QUESTIONS

### 3.0 The contribution statement — write it in session one

A jury's opening move is *"what does the field know after this thesis that it did not before?"* A
list of measurements is not an answer. **Write the contribution as an artefact, date it, keep it in
`PROJECT_PLAN.md`, and revise it at every phase gate.** Five sentences, this shape:

> Before this work, **X** was done by **Y**.
> This work shows **Z**, measured by **W**.
> The contribution is at the level of **[task / method / system / evaluation / artefact]**.
> It transfers to **V**.
> It would be wrong if **U** were true.

Rules:

- **If you cannot fill "Before this work" without hand-waving, the task is not chosen yet.** Go back
  to §1.
- Naming the *level* is what keeps you honest. "We integrated and evaluated existing components into
  a working, explainable system" is a legitimate contribution **at the system and evaluation
  level** — most engineering master's contributions are — but it must be *claimed as that*, not
  dressed as a methodological novelty.
- The last clause is the important one. A contribution that could not be wrong is not a finding.

### 3.1 Problem statement

Write it as a decision problem, not a feature list. A good shape:

> Given a continuous stream of heterogeneous information about a set of companies, decide **when to
> speak**, **about what**, and **with what evidence attached**, such that a non-expert can *verify*
> the decision rather than trust it.

### 3.2 Research questions — three, not six

**Three RQs. Each must be answerable with a measurement you can actually run.** v1 had four and
found renumbering impossible later because they propagate into every artefact. Fix them early, then
do not move them.

A defensible set, adapted to your chosen task:

- **RQ1 (the learning question).** Can a learned model of *[your chosen task]* outperform a
  transparent baseline on data it has not seen, under a protocol that prevents leakage?
- **RQ2 (the system question — do not omit this one).** Does the learned component still earn its
  place **inside the assembled pipeline**, measured end-to-end on the distribution the deployed
  system actually sees, rather than in isolation on a held-out split?
- **RQ3 (the explanation question).** Can the explanations be made *faithful* to what the system
  computed, and *useful* to a non-expert?

> ⚠️ **RQ2 is the one most projects omit, and it is where v1's real finding turned out to live.**
> Its learned gate scored well on a held-out split and ranked at **chance** in deployment, because
> cheap upstream filters had already removed most of what it was trained to remove — the materiality
> rate among logged decisions ran at 0.626 against a training prevalence of 0.378. *A model
> evaluated in isolation and deployed behind filters was never evaluated on the distribution it will
> see.* That is a general, transferable lesson, and it only exists as a finding because someone
> measured the deployed population. **Make it an RQ from day one, and instrument the pipeline to log
> every decision and label it later against the outcome that actually followed.**
>
> If you need a retrieval/evidence question as well, fold it into RQ1's evaluation rather than
> adding a fourth RQ — renumbering later propagates into every artefact you own.

RQ3 has two halves. **Faithfulness you can guarantee by construction and test. Usefulness requires
humans.** Plan the human study in month one, not month five (§9).

### 3.3 Hypotheses

State them before running anything, with the threshold that decides them. Put them in the plan file
with a date. Lowering a threshold after seeing data is p-hacking, and in a versioned file it is
visible in the diff — which is exactly why it goes in a versioned file.

---

## §4. ARCHITECTURE

### 4.1 The shape that worked

```
sources → collection → normalisation → relevance → dedup/novelty → feature extraction
   → learned models (the central task + supporting) → decision layer (gates, budget)
   → explanation layer (composed, faithful by construction) → delivery (push + pull)
```

Two rules that saved v1 repeatedly, and that you should adopt on day one:

**(a) All computation lives in one package; the web layer computes nothing.** If the API or the UI
recalculates anything, the product and the evaluation can diverge silently. v1's rule — *"no number
is computed in the API"* — is worth stating in a docstring and enforcing in review.

**(b) Pure logic separated from I/O, with heavy imports lazy.** The numeric core must be unit
testable offline with no network and no model downloads. This makes the test suite fast, which makes
it get run.

### 4.2 Push and pull are different products with different guarantees

- **Push** (an alert arriving uninvited) must be conservative: the reader cannot check anything at
  the moment it arrives. Use the strictest possible guarantees here.
- **Pull** (a page the user opened) can afford a weaker guarantee, because the evidence is on screen
  next to the claim.

v1 formalised this as two levels of guarantee for generated text and it was one of its strongest
contributions. Adopt the distinction from the start.

---

## §5. DATA AND LABELS

### 5.1 Data is a first-class artefact

Maintain a **data card** from the first dataset: source, licence, schema, date range, row counts,
known gaps, and how to regenerate. Licences matter more than people expect — check §5.4.

### 5.2 Your own labelled dataset is a contribution

**Budget one full day for annotation.** 300–500 hand-labelled items with a written rubric and a
measured agreement statistic (annotate 50 twice, report Cohen's κ) is:

- a genuine, citable research asset;
- the difference between "I used a public dataset" and "I built the dataset this problem needed";
- the thing that makes §1.2's "labels are obtainable" test pass.

Write the rubric **before** annotating. Freeze it. If you change it, re-annotate from scratch and
say so.

### 5.3 Leakage is the failure that invalidates everything

For anything time-dependent:

- split **temporally**, never randomly;
- split by **unique day**, so items sharing a day cannot straddle the boundary;
- add an **embargo** at least as long as your label horizon, and report how many rows it costs;
- write a test that **mutates the future and asserts the features do not change while the label
  does.** v1 had exactly this test and it is the single strongest defensive artefact in the
  dissertation. Build it early.

### 5.4 Licence check on day one, not at the end

If you distribute anything derived from a share-alike dataset (CC BY-SA), your repository licence is
constrained. v1 discovered at the end that it was distributing three FNSPID-derived files under
CC BY-SA plus a CC BY-NC-SA template file, while its checklist still described the licence choice as
free. **Resolve licence compatibility before you commit derived data.**

---

## §6. HONESTY AS A MECHANISM, NOT A VIRTUE

This is the section that most distinguishes v2 from v1. v1 said "never fabricate". That is
necessary and insufficient — you cannot exhort your way to accuracy across 130 pages. What actually
worked was **machinery**.

### 6.1 Every number in the thesis is produced by a versioned script

No number is typed by hand. Each evaluation script writes a `.md` with a header saying *"generated
by X, do not edit by hand"*, and the thesis quotes that file. This closes the loop between
computation and document.

⚠️ **And it has a failure mode you must design against, because v1 hit it twice in one day:** a
script that regenerates only *part* of its document, run with different flags, **silently deletes
the evidence it did not recompute** — exit code 0, no warning. Once, this removed three rows that a
thesis claim depended on; the claim then rested on an artefact that no longer contained it.

> **Rule:** a generator must either regenerate the whole document, or refuse to write, or declare in
> its header exactly what it did not recompute.

### 6.2 Reproduction gates

Any script that recomputes something already frozen must **first reproduce the frozen number** and
**refuse to write anything if it does not**. If the protocol differs, every other number it produces
is meaningless. Two lines of code; enormous value.

### 6.3 The Evidence Matrix

Maintain, in an appendix, a table of **every substantive claim**: claim · evidence · where · how
reproducible (script / test / live measurement) · status (kept / narrowed / **withdrawn**).

**Keep the withdrawn rows.** A matrix listing only surviving claims is not an audit. v1 ended with
13 withdrawn-or-narrowed claims, all withdrawn by its own measurements, and that table was among the
most persuasive things in the dissertation. It converts "I might be wrong" into "here is where I
was, and how I found out."

### 6.4 Classify every claim

**Demonstrated** (implementation + experiment) · **Observed** (seen during exploration, not
measured) · **Hypothesised** (proposed, untested) · **Future work**. Never blur them. An examiner
who catches one blurred claim will re-read everything suspiciously.

### 6.5 One command runs every gate

Build `scripts/check_all_gates.py` in the first month. It should run: tests, lint, every document
compile, cross-language parity, reference/label integrity, frozen-artefact integrity, and a clean
working tree. Print one line per gate. **A gate that only runs when someone remembers it is not a
gate.**

### 6.6 Sources are claims too — the highest-risk surface in assisted writing

§6.5's reference gate checks LaTeX `\ref`/`\label` integrity. **That is not the same as checking
that your sources exist and say what you claim.** A plausible, well-formatted, wrong or non-existent
citation is the single failure most associated with LLM-assisted writing, and an examiner who finds
one will re-read everything else suspiciously.

Machinery, not care:

1. **No reference enters the bibliography without a resolved identifier** — DOI, arXiv id, ISBN or
   publisher URL — recorded in a versioned `docs/decisions/citation_log.md` with the resolution date
   and the metadata as the registry returned it.
2. **A gate** that fails on: unresolved identifiers; keys cited but absent; keys present but
   uncited; and **a DOI whose registry title does not match the bibliography title** (this catches
   the identifier that resolves to a *different* paper — the most dangerous case, because everything
   looks right).
3. **A content audit** over every claim-bearing citation: *does the cited work support the sentence
   it is attached to?* Record the verdict per key. When a citation is found to be over-stretched,
   **fix it by weakening your sentence, never by swapping in a different source** until one fits —
   that is reverse-engineering evidence.
4. **The assistant may not add a reference it has not resolved, and may not infer bibliographic
   fields.** State this and hold it.

v1 ran exactly this and it caught two real errors — an anachronism (a 2014 survey cited for a
taxonomy whose third generation is BERT, from 2019) and a stretched attribution. Both were fixed by
weakening the claim. **Also beware your own checker:** v1's first citation-verification run produced
33 findings of which 30 were bugs in the checker (title matching by Jaccard against registry entries
that truncate subtitles, page ranges stored only as first page, LaTeX accents stripped before
comparison). *A verifier that cries wolf stops being read.*

### 6.7 Baselines are a claim too — and the one v1 got wrong

The most instructive defect in the entire first project:

> The thesis claimed triage raised within-budget precision from **0.163 "picking blindly"** to
> 0.632 — *"nearly four times"*. But the 0.163 floor assigned every item the same score, and the
> metric broke ties by row order, and the file was sorted by (date, ticker). So the floor did not
> pick blindly. **It picked alphabetically.** Every one of the 1,105 rows it selected belonged to
> the alphabetically-first company. Measured properly, a random ranking scores 0.379 — and the real
> gain is **1.67×, not 4×**.

Nobody noticed for months, because everyone checked the *model's* number and nobody checked the
*baseline's*.

> **Rule:** for every metric, write down how it breaks ties, and verify your floor measures what its
> name says. When a baseline is a constant, a "ranking" metric is measuring your file's sort order.

---

## §7. EVALUATION

### 7.1 Design the evaluation before the experiment

For each component, write down — in a versioned file, before running anything — the task, the ground
truth, the baseline, the metric, what counts as improvement, and what the known failure modes are.

### 7.2 Baselines, in this order

Deterministic rule → simple heuristic → logistic regression → tree ensemble → embeddings /
transformer. **Stop as soon as the added complexity stops paying.** A simple model that wins is a
result, and it is a *better* thesis than an unnecessary deep model that ties.

### 7.3 Uncertainty is not optional

Point estimates to three decimals across correlated samples are indefensible. Use **cluster
bootstrap** over whatever unit actually shares a label (v1: the (ticker, day) pair — 530 rows were
only 145 effective units). Report intervals. If the interval contains the baseline, say so.

### 7.4 Sensitivity

If a result depends on a threshold or a horizon you chose, **vary it and report the grid**. v1's
negative result survived all nine label definitions, which converted *"you picked τ=0.02, what if
you hadn't?"* from an attack into a table.

### 7.5 Error analysis

Aggregate metrics hide the interesting part. Read the actual failures. v1 found real defects by
reading its own first thirty production alerts — including one that contradicted itself in nine of
thirty cases. **No log would have shown it. Looking did.**

---

## §8. EXPLANATION AND GENERATIVE AI

### 8.1 The separation that makes this defensible

> **Engines produce facts. The language model produces prose. The language model never produces a
> fact.**

Implement this as an **evidence bundle**: a set of records, each with a short citable id, a declared
provenance (`measured` / `computed` / `model`), a label and a value. The generator sees only the
bundle. No record may have provenance `generated`, and a test should assert that.

### 8.2 The guard, and the mistake to avoid inside it

A runtime check verifies that every number in the generated text belongs to the evidence — **bound
per sentence to the records that sentence cites**, not to the bundle as a whole. Global number sets
are the vulnerability: they let the model cite one fact and use another's number.

⚠️ **And keep every scope consistent.** v1 fixed the numeric scope to be per-sentence but left the
verbatim-quote exemption bundle-wide. The result: `moving 8% [f1]` was rejected, while
`"up 8%" [f1]` **passed** — same number, same anchor — because the quoted string appeared in a
different fact's headline. If one part of a check is per-sentence, all of it must be.

### 8.3 Blocklists lose; allowlists hold

For the **push** path, use a closed vocabulary allowlist. For the **pull** path a blocklist is
acceptable because the evidence sits beside the text — but say so, measure it, and **write down the
residual risks you did not close**. A weaker guarantee that was measured is worth more in a thesis
than a strong one that was asserted.

### 8.4 Make the anchoring a traversal the reader can perform

If a sentence cites `[f3]`, the interface must open `f3`. That converts *"our text is grounded"*
from an assertion into something a sceptic can check in two clicks — and it is the part of the
contribution most likely to transfer to other systems.

**Then verify a human can actually do it.** v1's anchoring was verified by machine and by
construction, never by a person. If nobody can perform the traversal, the contribution is true and
useless.

---

## §9. USABILITY, AND THE HUMAN STUDY

### 9.1 Acceptance criteria are written before the code

v1 redesigned its interface **six times** and rejected each on aesthetic grounds, because aesthetic
criteria have no stopping condition. The redesign that finally worked began with a written document:
numbered criteria, each measurable, agreed before implementation.

Write criteria of the form *"content present within 2.5s on first request"*, not *"feels fast"*.
And when a criterion turns out to be wrong, **amend it in writing, dated**. A criterion corrected
silently is indistinguishable from one that was circumvented.

⚠️ **Measure the right thing.** v1 spent half a day claiming a performance win using
first-contentful-paint — which fires when the shell paints, not when the data exists. A page with
*no data* would have scored the same.

### 9.2 One timeframe, one page context

If the user picks a range, it controls **everything on the page** — chart, news, events, alerts,
cards. v1's rebuild lost this invariant: the chart honoured the range while the panels below showed
a fixed window, so the two could disagree on screen. Make the range a single shared state and derive
every panel from it.

### 9.3 Progressive disclosure

Verdict first, then context, then detail, then the full evidence. The first screen answers *"should
I care?"* — not *"here are 36 numbers"*.

### 9.4 Plan the human study in month one

It is the only thing on this list that **cannot be rushed at the end**, because it needs other
people's calendars. It closes the half of RQ3 that no amount of engineering can close.

- 6–10 non-experts, ~15 minutes each, within-subject, counterbalanced.
- Pre-register the analysis threshold before collecting anything.
- **Freeze the stimuli before the first participant.** If stimuli are generated (by a model, or
  selected from a growing corpus), they change between runs — v1 regenerated its pack with the same
  seed and got different stimuli, because the data had grown underneath it.
- Never thank participants who do not exist. If the study did not run, the acknowledgements may not
  imply it did.

---

## §10. THE THESIS

### 10.1 Structure

Use your institution's canonical structure. A shape that worked:

Introduction · State of the Art · Methods and Materials · **The System** · Case Studies (the
evaluations, each framed as a question with an answer) · Conclusions · Appendix (reproducibility +
evidence matrix).

Framing each evaluation as *"Question: … Answer: …"* makes the chapter readable and makes negative
results land as findings rather than as apologies.

**The state-of-the-art chapter must end in a table, not a narrative.** Score named prior systems and
named prior methods against your three RQs, and put your own system in the last row. A related-work
section that does not position *you* against *them* is a reading list, and it is where the jury will
ask "so what is new?" and find no sentence to point at. This table and §3.0 must agree.

### 10.2 Writing rules that save weeks

- **Every number appears once, in the file that generated it.** Everywhere else references it.
  Duplicated numbers drift, and drift is silent.
- If you write bilingually, **make parity a gate**, not a habit. Structural parity, per-chapter
  counts, and identical numbers.
- **Grep the claim, not just the number.** v1 corrected a retracted claim by searching for `0.163`
  and missed 13 places that stated the same claim in words — including all four abstract copies and
  the conference paper.
- Keep a **worked example** running through the thesis: one real item, followed from raw input to
  delivered output, appearing in the methods, the system chapter and the appendix. It is the single
  most effective device for making a system chapter concrete.

### 10.3 The AI declaration must be true

State the **actual** extent of AI assistance, plainly and without minimising. If an assistant wrote
substantial code and drafted prose, say that; then state what remains the author's: the problem, the
questions, the constraints, every decision to build/keep/narrow/discard, and responsibility for the
content.

> ⚠️ **v1's directive suggested describing AI as an auxiliary tool for "Python syntax, LaTeX and
> debugging". For a project built this way, that description would have been false.** A declaration
> that understates is an integrity problem, not a modest one. Confirm the exact required wording
> with your supervisor; never invent institutional policy.

---

## §11. WORKING AGREEMENT WITH THE ASSISTANT

### 11.1 Autonomy

Investigate → decide → implement → validate → document. Do not ask permission for routine
engineering choices. **Do ask** when: the information genuinely cannot be inferred; the action is
irreversible or outward-facing; the options have materially different research implications; or
credentials are involved.

The dedication of a thesis is a good example of something to ask about. A variable name is not.

### 11.2 Never report work as done unless it is

"Done" means implemented **and** run **and** verified. Use precise states: *drafted*, *implemented
but untested*, *measured*, *propagated*. If a step was skipped, say which.

### 11.3 Verification is the assistant's job, not the author's

Run the gates before saying anything passes. Read the output. If a background job returns "no
findings", establish that it actually *looked* — v1 was misled **six times** by multi-agent runs
whose verifiers all died, returning a clean-looking verdict that was in fact the *absence* of
verification.

### 11.4 The assistant will produce defects; design for catching them

Every defect below is one v1's assistant actually introduced. Expect the same class:

- claiming a fix works because a test passed, when the test exercised a scenario production cannot
  produce;
- writing a checker that invents its own predicate instead of reusing the code's
  (*"is this generated?"* implemented as a substring search, reporting 0 when the answer was 4);
- fabricating a plausible sentence in a section nobody audits (acknowledgements thanking
  participants who did not exist);
- a broad `except` turning a programming error into a silent "no data" path;
- measuring the wrong quantity in one's own favour.

**The countermeasure is not care. It is gates, reproduction checks, and reading the output.**

---

## §12. THE TRAPS (read before each session)

Concrete, cheap to avoid, expensive to hit. All observed.

1. **A green test over an impossible scenario** proves nothing. Check the scenario can occur in
   production.
2. **A regenerable artefact regenerated with different arguments** destroys evidence with exit 0.
3. **`grep` on a number** misses the same claim written in words.
4. **A constant-score baseline** under a ranking metric measures your file's sort order.
5. **A broad `except`** makes a bug indistinguishable from missing data. Catch specific exceptions.
6. **Word-count and identity gates** on abstracts break silently when you edit one of four copies.
7. **Portuguese decimals use commas**; a naive numeric comparison across languages invents
   divergences. (And LaTeX in PT should use points in math mode — pick one convention, gate it.)
8. **Heredocs mangle LaTeX**: `\t` in `\textbf` becomes a tab; `\r` in `\ref` becomes a carriage
   return that survives round-trips and breaks compilation. Use file-editing tools or raw strings.
9. **A cheap upstream filter can make a learned component redundant.** A model evaluated in
   isolation and deployed behind filters was never evaluated on the distribution it will see.
10. **Console encoding**: a script that prints box-drawing characters crashes on a Windows cp1252
    console before running a single check. Force UTF-8 on your own stdout, not just subprocesses.

---

## §13. ARTEFACTS TO MAINTAIN

Fewer than v1 demanded, because v1's thirty-section plan file duplicated things that lived
elsewhere, and duplicates drift.

| File | Purpose | Rule |
|---|---|---|
| `PROJECT_PLAN.md` | Vision, problem, **contribution statement (§3.0)**, RQs, hypotheses, weekly hour budget, decisions, priorities, completion matrix | **Never copies a number** that another file owns; it points |
| `docs/decisions/citation_log.md` | Every source, its resolved identifier, the date, the registry metadata | Gated (§6.6); the assistant may not add an unresolved entry |
| `CONTINUITY.md` | State at end of each session: done / discovered / decided / blocked / next | Updated **every** session, without exception |
| `docs/decisions/` | One file per significant decision, with the rejected alternatives and why | Written when decided, not reconstructed later |
| `docs/evaluation/*.md` | One per experiment, generated by script | Never hand-edited |
| `data_card.md` | Every dataset: source, licence, schema, gaps | Updated when data changes |
| `models/` + sidecar JSON | Versioned artefacts with their metrics and config | Frozen; changes are deliberate events |
| Evidence Matrix (appendix) | Every claim and its status, including withdrawn | The audit |

### Session protocol

Start: read `CONTINUITY.md` and `PROJECT_PLAN.md`. End: run all gates, commit, update
`CONTINUITY.md`. A future session must be able to resume from the files alone, with no memory of the
conversation.

---

## §14. WHAT "DONE" LOOKS LIKE

Ten mandatory items are how a plan becomes a panic in the last fortnight. Split them, and **agree
the descope order in writing, dated, before you need it** — so that cutting is a planned decision
rather than an emergency.

**MUST — without these there is no dissertation:**

- three RQs, each answered with a measurement, and at least one answer allowed to be negative;
- **a contribution statement (§3.0)** naming what is new and at what level, positioned against at
  least three named prior works;
- one central learned component evaluated against a stated baseline, with an interval, on data it
  has not seen — **beaten or honestly not**;
- every thesis number produced by a versioned script that reproduces on re-run;
- an evidence matrix including the claims you withdrew;
- a citation log with every source resolved (§6.6);
- one command that runs every gate, and it is green;
- a thesis that compiles clean, and **an author who can defend every sentence in it**.

**SHOULD — cut these before touching MUST:**

- your own labelled dataset with a written rubric and a measured agreement statistic;
- the RQ2 deployed-distribution study;
- a human study, even a small one;
- a deployed system a stranger can use without you present.

**COULD — first to go:**

- the secondary negative study; the generative explanation layer; bilingual output; the conference
  paper.

**Descope order, agreed in advance:** COULD in listed order → deployment → human study (replaced by
*"not measured"*, stated in the same sentence as the claim it would have supported) → labelled
dataset shrinks to a documented subset → RQ2 becomes future work with the instrumentation left in
place. **Nothing in MUST is ever cut**; if MUST is at risk, the scope of the *task* shrinks, not the
rigour.

**The last MUST item is the one that matters.** Everything above exists to make it true.

---

## §15. FIRST SESSION

Do not write product code in session one.

1. Read the institution's template and dissertation requirements; fix the deadline.
2. Draft the problem statement (§3.1) and 4–6 candidate learning tasks.
3. Run each candidate through the §1.2 test; write the results down, including the rejections.
4. Pick one. **Run the feasibility spike**: 200 hand-labelled items, one logistic regression, one
   number.
5. If the spike shows a ceiling at chance, **go back to step 3.** This is the cheapest decision
   point in the entire project and the most valuable.
6. Only then: set up the repository skeleton, the gate runner, and the continuity files.
7. Write `PROJECT_PLAN.md` with the RQs, hypotheses and thresholds, and commit it dated.
8. **Write the contribution statement (§3.0).** If the *"Before this work, X was done by Y"* clause
   cannot be filled without hand-waving, **the task is not chosen yet — return to step 3.**
9. Agree the descope order of §14 with your supervisor, and date it.

---

## Appendix — why v1's advice is not simply repeated here

v1's directive was long, ambitious and mostly right about *values*. It failed in three specific ways
worth naming, because avoiding them is most of v2's value:

1. **It asked for breadth with no stopping condition.** Seventy-eight sections of "investigate
   everything" produced a project that investigated genuinely well but had to defend a central
   negative result. The fix is §1: choose a learnable task, and prove it is learnable before
   building around it.
2. **It treated honesty as an instruction rather than a mechanism.** "Never fabricate" is necessary
   and does not scale to 130 pages. The fix is §6: gates, reproduction checks, generated
   documents, and an evidence matrix that records retractions.
3. **It specified an AI declaration that would have been untrue** for a project built with heavy
   assistance. The fix is §10.3: declare the real extent.

Everything else in v1 — the refusal to predict, the insistence on explainability, the demand that
data be a first-class artefact, the traceability chain — was correct, and is carried forward here in
shorter form.
