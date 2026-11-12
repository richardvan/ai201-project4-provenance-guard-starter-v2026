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

False positives: of 10 pieces I wrote myself, at most 1 is labelled high-confidence AI, and this holds in each of 3 trials. The 10 pieces are fixed in scenarios.py before I test, and include plain and formal writing.



**Why this target:**

Wrongly accusing a real writer costs that person far more than missing some AI text costs the site, so this is the target I would least want to miss. I accept at most 1 in 10 because the unsure band, not the AI label, is where borderline human writing should land. Trials are repeated because the model signal can score the same text differently twice.

---

## 2.

Score spread: the average combined score of 5 clearly-AI pieces is at least 0.20 higher than the average of 5 clearly-human pieces. Both sets of 5 are fixed in scenarios.py before I test.



**Why this target:**

If the two groups don't separate, the score carries no information and the labels are decoration. This is a test of ordering, not of crossing a threshold: a 0.20 gap can still leave both groups in the unsure band (0.35 to 0.65 in config.py), which is acceptable here and is checked by criterion 1.

---

## 3.

Edited AI: at least 3 of 5 lightly-edited AI pieces (an AI-written piece with about 10% of its words changed by hand, fixed in scenarios.py before I test) get a combined score above 0.5.



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


---

# Capstone criteria — hardening Provenance Guard

Written before I ran anything for the capstone. The first four are about the
new failure handling. The fifth is about whether the original system still
works after I added it. Criteria 1, 2 and 3 are about what happens on the bad
path.

## 1. Bad input gets a clear error, not a crash

I send 10 bad requests to `/submit`: a body that is a JSON list, a body that is
a bare number, `text` missing, `text` empty, `text` only spaces, `text` as a
number, `text` as a list, `text` over 10,000 characters, `text` of one word,
and a `creator_id` that is a list. **All 10 must come back with a 4xx status
and a JSON body that has an `error` field.** None may be a 500, and none may be
an HTML page. I need 10 of 10 in each of three trials.

*Why this target:* a crash on a bad request is the most common real failure
this service can have, and before the capstone three of these ten (the list
body, the one-word text and the list `creator_id`) were 500s or worse. It has
to be all ten and not nine because a single 500 means a person typed something
and got a stack trace back. I'm not going to ask for less, and ten kinds of bad
input is as many as I can think of for a text box.

## 2. Every failed request leaves a log entry

After the same 10 bad requests, the audit log must have gained **exactly 10
new entries**, each with `"event": "rejected"`, a non-empty `reason`, and a
`duration_ms` that is a number. I need 10 of 10 in each of three trials.

*Why this target:* in unit 8 the rule I took from the attack run was that an
attack that shows up only as an absence is one I'll never find. Exactly 10, not
at least 10, because a request that writes two entries or none means the log
can't be trusted to count things. I check it by counting lines before and
after, so two people would get the same answer.

## 3. When scoring itself fails, the service says so and decides nothing

Two ways scoring can fail, tested on purpose:

- **Model won't load.** I start the service with `AI201_DETECTOR_MODEL` set to
  a model name that doesn't exist and `HF_HUB_OFFLINE=1`, then send 5 normal
  submissions. Each must come back **503** with an `error` field of
  `detector_unavailable`.
- **Scoring takes too long.** I start the service with
  `AI201_SCORING_TIMEOUT=0.01` and send 5 normal submissions. Each must come
  back **504** with an `error` field of `scoring_timeout`, in **under 2
  seconds**.

All 10 must get the right status, and **none of the 10 may leave a `decided`
entry in the log** (each must leave a `rejected` entry with the matching
reason instead). I need 10 of 10 in each of three trials.

*Why this target:* the worst thing this service can do is label a writer when
the check didn't actually run, so "decides nothing" matters as much as the
status code. Under 2 seconds because the whole point of the timeout is that the
caller doesn't sit waiting, and the response should arrive just after the limit
I set, not after the scoring finishes in the background.

## 4. An appeal for an unknown ID is refused every time, and a real one still works

I send 5 appeals for a `content_id` that doesn't exist, using the **same fake
ID each time**. Each must get **404**. Then I submit 5 real texts and appeal
each one: each appeal must get **200** with `"status": "under_review"`, and the
log must show the appeal entry after the original decision. That is 10 of 10 in
each of three trials.

*Why this target:* the bug I fixed was that the second appeal for the same
fake ID got a 200, because the first 404 had written a log entry that counted
as proof the ID existed. Five repeats of one ID is the case that triggers it. I
also test the real appeals in the same criterion because a fix that refuses
everything would pass the first half. An appeal is the only thing a wrongly
labelled writer has, so a wrong answer here costs more than anywhere else.

## 5. The original path still works, and fast, after the changes

I send 20 normal, different texts to `/submit` after the model has loaded,
each with its own `creator_id`. At least **19 of 20** must return 200 with all
six fields (`content_id`, `guess`, `confidence`, `label`, `model_score`,
`style_score`), each must have a `decided` log entry, and at least **19 of 20**
must have a `duration_ms` under **500**. I need that in each of three trials.

*Why this target:* this is the regression check for the capstone. The new
code wraps the scoring in a worker thread, and I want to know it didn't break
the normal case or make it slower. I measured a warm run at about 0.03 seconds,
so 500 ms is about 15 times that. It is loose on purpose, because it should
only catch a real slowdown and not a busy laptop. I allow one run in 20 to
miss it because the first request after startup can run slower than the rest.
