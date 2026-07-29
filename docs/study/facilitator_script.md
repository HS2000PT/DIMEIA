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
