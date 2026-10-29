# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1.

False positives: of 10 pieces I wrote myself, at most 1 is labelled high-confidence AI, and this holds in each of 3 trials. The 10 pieces are fixed in samples/ before I test, and include plain and formal writing.



**Why this target:**

Wrongly accusing a real writer costs that person far more than missing some AI text costs the site, so this is the target I would least want to miss. I accept at most 1 in 10 because the unsure band, not the AI label, is where borderline human writing should land. Trials are repeated because the model signal can score the same text differently twice.

---

## 2.

Score spread: the average combined score of 5 clearly-AI pieces is at least 0.20 higher than the average of 5 clearly-human pieces. Both sets of 5 are fixed in samples/ before I test.



**Why this target:**

If the two groups don't separate, the score carries no information and the labels are decoration. This is a test of ordering, not of crossing a threshold: a 0.20 gap can still leave both groups in the unsure band (0.35 to 0.65 in config.py), which is acceptable here and is checked by criterion 1.

---

## 3.

Edited AI: at least 3 of 5 lightly-edited AI pieces (an AI-written piece with about 10% of its words changed by hand, fixed in samples/ before I test) get a combined score above 0.5.



**Why this target:**

Tidying AI text is the cheapest attack on a detector, and the one a real user is most likely to try. I want to know early whether it works. 0.5 is inside the unsure band, so this tests whether the score moves toward AI, not whether the label reads AI.

---

## 4.

Appeal path: of 5 appeals sent with valid content IDs, all 5 change the status to under_review and appear in GET /log next to the original decision. An unknown content_id returns 404 and writes nothing.



**Why this target:**

The appeal is the only defence a wrongly flagged writer has, so it can't fail even once. Checking the 404 case covers the typo failure the starter warns about.

---

## 5.

Consistency: submitting the same text 5 times gives a combined score that varies by no more than 0.05.



**Why this target:**

The model signal can score identical input differently, and unit 8 needs targets that hold across 3 trials. A score that drifts could flip a label between two submissions of the same text.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
