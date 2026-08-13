# Facilitator script (8 participants, ~15 min each)

## Before you start
- Print or open `stimuli.md`. Keep `counterbalancing.md` beside you.
- Copy `responses_template.csv` to `responses.csv` and fill it as you go.
- Recruit adults with **no** finance or AI background. Colleagues and family are the right
  profile — they are the actual target user.

## Consent (read aloud, ~20 s)
> "You'll see a few financial alerts. You don't need to know anything about markets. For each
> one I'll ask what you understood. There are no wrong answers about you — I'm testing the
> alerts, not you. It's anonymous, and you can stop at any time."

## Per participant
1. Look up their row in `counterbalancing.md`.
2. **Condition 1** — show each listed stimulus in that condition, then ask:
   - *"What did the system detect here?"* → score `p1_detected` 1 if correct, else 0
   - *"Why was this flagged?"* → `p1_why` 1/0
   - *"Is this a prediction of what happens next?"* → `p1_not_prediction` 1 if they say **NO**
   - Then the five 1–5 statements (Q1–Q5 in `usefulness_study.md` §4).
3. **Condition 2** — same, with the other stimuli.
4. Ask once at the end: *"What was missing or confusing?"* → `open_comment`.

## Do not
- Do not explain, hint, or fill silence. If they ask what something means, say
  *"whatever it means to you"* and move on. That silence **is** the measurement.

## When done
    python scripts/analyse_usefulness.py

That writes `docs/evaluation/evaluation_usefulness.md` — the Case Study 5 table.

## Optional block C — the generated report (exploratory)

Run this only if the participant still has energy; it adds ~10 min. It is **exploratory**, so its
sheet is separate (`responses_block_c_template.csv`) and its rows must never be pooled with A/B.

- Stimuli: `report_stimuli.md`, captured once from production and **frozen** (the report is written
  by a language model and is not reproducible; generating it live would measure the model's
  variation instead of the condition).
- C1 = the panels alone · C2 = the panels plus the anchored report.
- Then the part that matters most, and needs no statistics: pick **three anchored sentences** in
  advance and ask the participant to open the cited fact and say whether it supports the sentence.
  **Give no help.** If people cannot do it, the anchoring contribution is true and unusable.
- Record `report_source` for each stimulus: one that fell back to the deterministic composition
  does **not** test the generative layer.
