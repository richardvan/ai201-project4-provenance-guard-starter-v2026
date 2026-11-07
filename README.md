# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

Provenance Guard is a small web service that estimates whether a piece of writing was written by a person or with AI help, and gives the writer a plain-English label they can act on. A submission goes through two independent signals (a local language model reading how predictable the text is, and a style measure of its shape), which are combined into one score and turned into one of three labels: probably human, unsure, or possibly AI. Every decision is written to an audit log, and a writer who thinks the label is wrong can appeal, which marks the piece as under review and records their reasoning next to the original decision. It is built to lean human when unsure, because wrongly accusing a real writer costs more than missing some AI text.

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

<!-- Format: N. **Thing** — what comes in → what it adds
     Pieces: POST /submit, detector.py::model_signal, stylometry.py::style_signal,
     scoring.py::combine_signals, scoring.py::score_to_label, audit.py,
     POST /appeal (off to the side).
     Answer in the steps: where bad input is stopped; when content_id is created
     and why before the log write; whether the log is written before or after the
     label; where an appeal joins the path. -->

1. **`POST /submit` (app.py)** — raw JSON with `text` and `creator_id` → checks the input. Missing, non-string or empty text is rejected here with a 400, so nothing downstream ever sees bad input. It also assigns a fresh `content_id`, which is what an appeal will use later.
2. **Model signal (`detector.py::model_signal`)** — the text → `model_score`, 0–1, how predictable the text is to a local language model (higher = more AI-like).
3. **Style signal (`stylometry.py::style_signal`)** — the same text → `style_score`, 0–1, from sentence-length spread, vocabulary variety and punctuation (higher = more AI-like).
4. **Combining rule (`scoring.py::combine_signals`)** — both scores → one `combined_score`, 0–1. This is where the false-positive decision is made: how the two signals are weighted and what happens when they disagree.
5. **Label (`scoring.py::score_to_label`)** — `combined_score` → a `guess` (`ai` / `human` / `unsure`) and a plain-English label sentence. The thresholds in config.py decide which of the three a score falls into.
6. **Audit log (`audit.py` → `logs/audit.jsonl`)** — everything so far → one JSON line with timestamp, `content_id`, `creator_id`, both signal scores, the combined score, the guess, the label and `status: decided`. It is written after the label is chosen so the entry records the full decision, not a partial one. The route then returns the same fields to the writer.
7. **`POST /appeal` (off to the side)** — `content_id` plus the writer's reasoning → checks the `content_id` exists in the log, then records the appeal next to the original decision and sets `status: under_review`. It does not re-score anything; it makes sure a wrong label has a human-visible trail.

### Following a false positive through the service

**The writer:** someone writing in a second language, in plain vocabulary they are sure of, who submits an essay they wrote entirely themselves.

**What score they get:** The model signal reads short sentences of common words as highly predictable, so `model_score` comes back high (illustrative: about 0.8). Plain writing is also evenly paced, so the style signal may agree (illustrative: about 0.6). The combined score lands above the AI threshold (0.65 in config.py), and the writer is labelled high-confidence AI. Both signals can be wrong in the same direction for this writer, so combining them doesn't rescue them. This is why the combining rule and thresholds matter: a rule that treats a high model score alone as enough would make this case a certain accusation.

**What the label says to them:** The high-confidence AI label, in sentences written for a reader who has never heard of thresholds. It has to say that this is an automated estimate and that it can be wrong, and it has to point to the appeal, because the person reading it may have written every word. It must not read as a verdict or an accusation.

**What they can do about it:** Send `POST /appeal` with the `content_id` from their submission and their reasoning (for example, how they wrote it, or drafts and notes). The service checks the ID exists, records the appeal in the audit log next to the original decision, sets the status to `under_review`, and confirms to the writer. Nothing is re-scored automatically; a person can read the log entry, with both signal scores beside the combined one, and see why the system flagged this writer.

**What this decides:** the thresholds. Because the person most likely to be wrongly flagged has the least room to argue, the AI band should be hard to reach (a high AI threshold, a wide unsure band), even though that lets more AI text through.

### Endpoint contracts

All requests and responses are JSON.

#### `POST /submit`

**In**

| Field | Type | Required | Notes |
|---|---|---|---|
| `text` | string | yes | The writing to check. Must contain non-whitespace characters. |
| `creator_id` | string | no | Who submitted it. Defaults to `"unknown"`. |

**Out (200)**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | Unique ID for this submission (`c_` + 12 hex chars). Needed to appeal. |
| `creator_id` | string | Echoed back. |
| `guess` | string | `"ai"`, `"human"` or `"unsure"`. |
| `confidence` | number 0–1 | The combined score. Higher means more likely AI. |
| `label` | string | The full sentence shown to a reader. |
| `model_score` | number 0–1 | Signal one alone. Higher means more likely AI. |
| `style_score` | number 0–1 | Signal two alone. Higher means more likely AI. |

**Errors**

| Status | When | Body |
|---|---|---|
| 400 | `text` missing, not a string, or empty/whitespace | `{"error": "bad_request", "message": "..."}` |
| 413 | `text` longer than the maximum length (limit set in config.py) | `{"error": "text_too_long", "message": "..."}` |

#### `POST /appeal`

**In**

| Field | Type | Required | Notes |
|---|---|---|---|
| `content_id` | string | yes | Must match a `content_id` already in the audit log. |
| `reasoning` | string | yes | The writer's explanation. Must be non-empty. |

**Out (200)**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | Echoed back. |
| `status` | string | `"under_review"`. |
| `message` | string | A confirmation sentence for the writer. |

**Errors**

| Status | When | Body |
|---|---|---|
| 400 | `content_id` or `reasoning` missing or empty | `{"error": "bad_request", "message": "..."}` |
| 404 | `content_id` not found in the log | `{"error": "not_found", "message": "..."}` |

**Read-back check:** someone building a client from this page alone would know every field to send, every field they get back, and which status code each failure produces. Open point: the maximum `text` length isn't chosen yet, and the contract says "set in config.py" until it is.




---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the text is to a small language model (gpt2 running locally). It computes perplexity over the first 400 tokens, then squashes it onto 0–1 so that low perplexity (easy to predict) scores high. Higher means more likely AI.

**Why that might differ between human and AI writing:** A language model writes by repeatedly choosing a likely next word, so its output tends to be text another model finds easy to guess. Human writing wanders more: odd word choices, abrupt turns, specific rather than typical detail.

**What it can't see:** Authorship. It only sees predictability, and plain, common-word writing is predictable no matter who wrote it. A second-language writer, a younger writer, or anyone writing simply on purpose can score as machine-like as real AI text. Ornate human prose full of rare words can score as human, and so can AI text that has been reworded with unusual vocabulary. It also reads only the first 400 tokens, so anything later in a long piece is invisible to it.

### Signal two — the style signal

**What it measures:** The shape of the text without reading it: how much sentence length varies, how much of the vocabulary is unique (unique words / total words), and how much and how varied the punctuation is. These are combined into one 0–1 score where higher means more likely AI.

**Why that might differ between human and AI writing:** Generated prose tends toward even, mid-length sentences and a narrower, safer vocabulary. Human writing is lumpier: a three-word sentence next to a forty-word one, repeated pet words, irregular punctuation.

**What it can't see:** Meaning. It has no idea what the text says, so anything that changes the shape without changing the substance fools it: breaking sentences up, adding typos, pasting in a quotation, or varying sentence length on purpose. Honest writers can trip it too. Someone with a naturally even rhythm, such as a formal report writer, looks "AI-shaped". It is also unreliable on very short text (a one-sentence submission has no spread), and vocabulary ratio drops as text gets longer, so length alone moves the score.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** A plain weighted average of the two signals, 0.6 for the model signal and 0.4 for the style signal. (Until unit 8 it also had a disagreement pull: when the signals were more than 0.30 apart, the score was pulled halfway toward the lower one, to lean human on a split. I removed it after the attack run showed it turned four "unsure" evasion results into "human" and never rescued a false positive. See "The Improvement".)

**The numbers:** model weight 0.6, style weight 0.4 (the style signal is easier to fool by reshaping text, so it counts for less). Thresholds 0.35 (human) and 0.65 (AI). All in config.py.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule did with it (this is the unit 7 rule; see "The Improvement" for what I changed):**

A generic AI paragraph that I deliberately gave a lumpy shape (one-word sentence, a dash, a semicolon, an exclamation). The model signal still sees predictable wording (0.81) but the style signal sees an irregular shape (0.14). A plain weighted average would give 0.55, which is "unsure". The gap is 0.67, over the 0.30 trigger, so the rule pulls it halfway toward the lower signal and the combined score is **0.35, which is "human"**. That is the trade the rule makes on purpose: when the signals disagree, I'd rather miss some AI text than accuse someone. It does mean AI text that has been reshaped gets a clean label, and that is the style signal's blind spot working exactly as I wrote it.

**Test results (both signals, combined, and the label they produce):**

*These are five short texts I used while building (two are the starter's demo samples). They are not the fixed sets my criteria refer to; those get chosen in `scenarios.py` for the next unit's testing.*

| Input | model | style | combined | label |
|---|---|---|---|---|
| clearly AI | 0.754 | 0.525 | 0.662 | ai |
| clearly human | 0.445 | 0.199 | 0.346 | human |
| formal human | 0.236 | 0.194 | 0.220 | human |
| plain human (short sentences, common words) | 0.888 | 0.825 | 0.863 | **ai (false positive)** |
| lightly-edited AI | 0.400 | 0.341 | 0.377 | unsure |
| AI with lumpy style (the split case) | 0.814 | 0.144 | 0.345 | human (missed AI) |

What I found:
- **Clearly-AI and clearly-human text land 0.32 apart** (0.662 vs 0.346), but clearly-AI only just clears the 0.65 AI threshold.
- **The false positive I predicted is real.** Plain, short-sentence human writing scores 0.86 and is labelled AI. Both signals read it the same way, so the disagreement rule can't help: it only rescues a writer when one signal is wrong, not both.
- **Type-token ratio doesn't discriminate on short texts.** The clearly-AI sample scores a *higher* vocabulary ratio (0.91) than the clearly-human one (0.81), so that measure contributes noise here. Punctuation and sentence spread do the work.
- **Lightly-edited AI is not caught.** It lands at 0.38, one hair above the human line.

---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | We think a person wrote this. |
| unsure | 0.35 – 0.65 | Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at. |
| high-confidence AI | 0.65 – 1.00 | Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read. |

**Why I worded the "unsure" one this way:**
It starts with what we can't tell and says it's common with plain writing, so a reader doesn't take it as a charge. It leaves out lines like "this is not a judgment about you" and "if you wrote it yourself", which in a read-through sounded like the opposite of the intent. It gives the reader a choice (nothing, or appeal). The AI label follows the same idea: "possibly" and "our check" make it an estimate, it says the check can get plain, clear writing wrong, and it says what an appeal does.



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

Milestone 3 state: only the model signal is wired in, so `guess` and `label` are placeholders and `style_score` is `null`. (Run on port 5001 because AirPlay holds 5000 on this machine.)

```bash
$ curl -X POST http://127.0.0.1:5001/submit \
  -H "Content-Type: application/json" \
  -d @samples/clearly_ai.json
```

```json
{"confidence":0.7544,"content_id":"c_3e9ec076c535","creator_id":"demo_instructor","guess":"unsure","label":"not built yet","model_score":0.7544,"style_score":null}
```

Bad input:

```bash
$ curl -X POST http://127.0.0.1:5001/submit -H "Content-Type: application/json" -d '{"text":"","creator_id":"u1"}'
{"error":"bad_request","message":"Send JSON with a non-empty \"text\"."}     # HTTP 400

$ curl -X POST http://127.0.0.1:5001/submit -H "Content-Type: application/json" -d @long.json   # 12,000 characters
{"error":"text_too_long","message":"Text is over the 10000-character limit."}   # HTTP 413
```

Detector alone on the three sample texts (`python detector.py "..."`):

| Sample | perplexity | model_signal |
|---|---|---|
| clearly_ai | 22.3 | 0.7544 |
| clearly_human | 51.7 | 0.4445 |
| borderline | 66.5 | 0.3489 |

The signal ranks AI above human, but the "borderline" text scores lower (more human) than the "clearly human" one, and the clearly-human text is only 0.44. That is a first sign that signal one alone doesn't separate cleanly.

**An appeal**

I submitted a plain, short-sentence piece I'd written as a person. It scored 0.86 and got the AI label, so it is the case an appeal exists for (this one is a text I wrote to test the false positive, not real work).

```bash
$ curl -X POST http://127.0.0.1:5001/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c_71f357e1811a", "reasoning": "I wrote this myself; I have my handwritten drafts."}'
```

```json
{"content_id":"c_71f357e1811a","message":"Thank you. Your appeal has been recorded and this piece is marked as under review. A person can read your explanation next to the original decision. Nothing is re-scored automatically.","status":"under_review"}
```

An unknown ID and a missing field:

```bash
$ curl -X POST http://127.0.0.1:5001/appeal -H "Content-Type: application/json" -d '{"content_id":"c_nope","reasoning":"x"}'
{"error":"not_found","message":"No submission found with content_id \"c_nope\"."}      # HTTP 404

$ curl -X POST http://127.0.0.1:5001/appeal -H "Content-Type: application/json" -d '{"content_id":"c_71f357e1811a"}'
{"error":"bad_request","message":"Send JSON with a non-empty \"content_id\" and \"reasoning\"."}   # HTTP 400
```

**What the log shows afterwards**

The log is append-only: the original decision stays as it was (`status: decided`) and the appeal is a new line after it with `status: under_review`.

```bash
$ curl "http://127.0.0.1:5001/log?limit=2"
```

```json
{"count":2,"entries":[
 {"combined_score":0.8625,"content_id":"c_71f357e1811a","creator_id":"writer_a","guess":"ai","label":"Our automated check thinks this may have been written with AI help. These checks can be wrong, especially on writing that is simple and clear. If you wrote it yourself, you can appeal and a person will look at it.","model_score":0.8879,"status":"decided","style_score":0.8245,"timestamp":"2026-10-29T01:30:52+00:00"},
 {"content_id":"c_71f357e1811a","creator_id":"writer_a","event":"appeal","reasoning":"I wrote this myself; I have my handwritten drafts.","status":"under_review","timestamp":"2026-10-29T01:30:52+00:00"}]}
```

*(The label in this captured log entry is the first draft of the AI label; the wording was revised afterwards and the current text is in Label Variants above.)*

**All three labels are reachable:** the clearly-human sample scores 0.346 (human), the lightly-edited AI sample 0.377 (unsure), and the plain-writing piece above 0.863 (AI).

---

## How I Used AI

**Moment 1: checking what the AI added against the brief**

- *What I asked for:* Help working through Milestone 1 step by step.
- *What came back:* It created a new `DESIGN.md` to hold my path, signals, false-positive trace and endpoint contracts. The brief never asks for that file.
- *What I changed:* I asked whether the instructions actually said to make it or whether it belonged in the README. It admitted it had added the file on its own, and the README already had slots for most of it. I had it delete `DESIGN.md` and put the path and signal write-ups in the README's What This Does and Signals and Scoring sections. The false-positive trace and endpoint contracts, which have no README slot, went in as subsections of What This Does.

**Moment 2: reading my labels as the writer**

- *What I asked for:* For each of my three draft labels, what a writer would think it says about them and what they would do next, answered as the writer and not as an engineer, without rewriting anything.
- *What came back:* "This is not a judgment about you" and "if you wrote it yourself" both read as suspicion, which was the opposite of what I meant. The unsure label also gave the writer nothing to do, and the AI label didn't say who sees it while an appeal is open.
- *What I changed:* I cut both suspicion-sounding lines, gave the unsure label a choice (do nothing or appeal), and made the AI label say what an appeal does. I did not make the label promise a timeline or a changed label, because the system doesn't do either.

**Moment 3: checking the AI's own diagnosis against the numbers (unit 8)**

- *What I asked for:* Possible causes for my worst false positive (FP03), then for the AI to run the checks.
- *What came back:* Three possible causes at different stages without ranking them, then the numbers for each (both signals high, punctuation measure at its maximum, no reweighting could clear it), and later a drafted diagnosis for all 16 broken attacks. When it rechecked its own draft it found two claims were wrong: it had said the signal gaps were under 0.2 (FP06's was 0.27) and that two causes explained 12 of 16 breaks (it was 10).
- *What I changed:* The README states the corrected numbers. The diagnoses are the AI's draft, which I read against the numbers.

**Moment 4: what to do about a criterion I missed (unit 8)**

- *What I asked for:* What to do about criterion 4, where "an unknown ID writes nothing" turned out false because I'd added rejection logging.
- *What came back:* Advice to call it MISSED and not reword it, because it was measurable and the clause failed. Rerunning the check also turned up a real bug: a repeated unknown ID got a 200 because the rejection entry made the ID look real.
- *What I changed:* I kept the MISSED verdict, wrote the bug into the diagnosis, and did not touch the criterion's wording.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 50 per day, on `POST /submit`, both set in `config.py`.

**Why those numbers and not others:** A real writer submits a piece, reads the label, maybe edits and resubmits. Five a minute is more than anyone can do by hand, and 50 a day is far more than a person needs, so a genuine writer should never see a 429. A script probing my thresholds needs hundreds of variations. At 50 a day, one caller could send at most 50, so mapping the 0.35 and 0.65 boundaries takes days instead of minutes. I kept the per-minute number low because each submission runs a language model, so a burst also costs real compute.

**What a caller counts as:** The creator_id when the request has one, otherwise the caller's address (`rate_limit_key` in `app.py`). That is the weakness: a script can send every request under a fresh creator_id and never hit a limit, and the attack set's rows each use their own creator_id for exactly that reason. The limit stops one noisy caller, not someone willing to rotate names. Limiting by address would catch that but would treat a whole household or campus as one caller.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

---

## Attack Run — Before

Run with `python run_attacks.py --set attack_set --label before` against a fresh service (counters empty), nothing fixed first. Full output: `results/attack_run_2026-11-04_1757_before.md`.

**How I marked held or broke.** Evasion and prompt-injection rows (AI text trying to avoid the label): BROKE if it came back labelled *human*; *unsure* counts as held because it is not cleared. False-positive rows (real human writing): BROKE if it came back labelled *AI*. Malformed rows: BROKE if the service crashed (5xx) or put a high-confidence AI label on input that is not meaningful writing; a clean 4xx or a sensible score is HELD. RQ10 and RQ11 came back 429, so they never reached my route and tell me nothing about it.

**Result: 16 of 56 broke, 40 held.**

| Family | Attacks | Broke | Held |
|---|---|---|---|
| evasion | 10 | 5 | 5 |
| false_positive | 8 | 6 | 2 |
| prompt_injection | 6 | 1 | 5 |
| malformed | 20 | 4 | 16 |
| flood_same_creator | 12 | 0 | 12 |

| ID | Family | Targeting | Status | Label | Score | Verdict |
|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | human | 0.264 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | human | 0.288 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | unsure | 0.406 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | unsure | 0.633 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | human | 0.324 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | unsure | 0.500 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | human | 0.335 | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | human | 0.319 | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.618 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.936 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | unsure | 0.610 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | ai | 0.757 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | ai | 0.751 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | ai | 0.757 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | ai | 0.848 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | ai | 0.774 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | ai | 0.796 | BROKE |
| FP08 | false_positive | very short genuine human submission | 200 | unsure | 0.398 | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | unsure | 0.421 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | human | 0.219 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | unsure | 0.366 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.445 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | human | 0.299 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.575 | HELD |
| MF01 | malformed | text is only whitespace | 400 | — | — | HELD |
| MF02 | malformed | text is a single character | 500 | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | human | 0.100 | HELD |
| MF04 | malformed | text is only punctuation | 200 | human | 0.176 | HELD |
| MF05 | malformed | text is a very long single word | 200 | unsure | 0.649 | HELD |
| MF06 | malformed | text is emoji only | 200 | ai | 0.931 | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | ai | 0.877 | BROKE |
| MF08 | malformed | text is 60,000 characters | 413 | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | — | — | HELD |
| RQ02 | malformed | no creator_id | 200 | human | 0.344 | HELD |
| RQ03 | malformed | text is a number | 400 | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | — | — | HELD |
| RQ05 | malformed | text is null | 400 | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 200 | human | 0.139 | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 500 | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | HELD |
| FL01_01–12 | flood_same_creator | 12 rapid submissions from one creator | 200 200 200 200 200 429 429 429 429 429 429 429 | | | HELD |

**Ten audit log entries from the run**

Chosen for what they show: the false positives with the highest scores, an injection that worked, evasions that cleared the label, a fully-confident AI label on a script that isn't English, a creator_id that was never validated, and a rejection.

```json
// FP05
{"timestamp": "2026-11-05T01:57:17+00:00", "content_id": "c_f8b6e9f445d5", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.9202, "combined_score": 0.8484, "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.", "status": "decided"}
// FP03
{"timestamp": "2026-11-05T01:57:17+00:00", "content_id": "c_5b57648dd413", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.6708, "combined_score": 0.7514, "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.", "status": "decided"}
// FP02
{"timestamp": "2026-11-05T01:57:17+00:00", "content_id": "c_09994a8f6ff6", "creator_id": "attacker_FP02", "guess": "ai", "model_score": 0.7387, "style_score": 0.7847, "combined_score": 0.7571, "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.", "status": "decided"}
// PI02
{"timestamp": "2026-11-05T01:57:18+00:00", "content_id": "c_17b64fb06068", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.242, "combined_score": 0.2194, "label": "We think a person wrote this.", "status": "decided"}
// EV08
{"timestamp": "2026-11-05T01:57:17+00:00", "content_id": "c_8772d783115f", "creator_id": "attacker_EV08", "guess": "human", "model_score": 0.2452, "style_score": 0.6115, "combined_score": 0.3185, "label": "We think a person wrote this.", "status": "decided"}
// EV01
{"timestamp": "2026-11-05T01:57:17+00:00", "content_id": "c_7ed3da5c5ef1", "creator_id": "attacker_EV01", "guess": "human", "model_score": 0.1635, "style_score": 0.6667, "combined_score": 0.2641, "label": "We think a person wrote this.", "status": "decided"}
// EV10
{"timestamp": "2026-11-05T01:57:17+00:00", "content_id": "c_69f05d2b85e0", "creator_id": "attacker_EV10", "guess": "ai", "model_score": 0.9792, "style_score": 0.8707, "combined_score": 0.9358, "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.", "status": "decided"}
// MF07
{"timestamp": "2026-11-05T01:57:18+00:00", "content_id": "c_7176a04c2846", "creator_id": "attacker_MF07", "guess": "ai", "model_score": 0.9064, "style_score": 0.8333, "combined_score": 0.8772, "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.", "status": "decided"}
// RQ06
{"timestamp": "2026-11-05T01:57:18+00:00", "content_id": "c_2f4587491c5a", "creator_id": {"id": "x"}, "guess": "human", "model_score": 0.0492, "style_score": 0.5, "combined_score": 0.1394, "label": "We think a person wrote this.", "status": "decided"}
// FL01_06 — rejected by the rate limiter (a rejection carries fewer fields than a decision)
{"timestamp": "2026-11-05T01:57:18+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

The two inputs that crashed the service (MF02, a one-character text, and RQ07, a JSON array body) are *not* in the log at all. A 500 skips the code that writes the entry, so the crash leaves no trace there. Only the terminal running `app.py` showed it.

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

**FP03.** A non-native English speaker writing carefully about their first month in a new country:

> I want to describe my experience of the first month in this country. The weather was very different from my home. I did not expect the rain to continue for so many days. My colleagues were kind and they helped me to find an apartment. I am still learning the words that people use in the office. Sometimes I do not understand the jokes. But I am happy that I came here and I think it was a good decision for my family.

My system called it AI: model score 0.805, style score 0.671, combined 0.751, label "Our check flagged this as possibly written by AI." Every word is the writer's own, and this is the person with the least room to argue back.

**What I found when I checked.** Both signals leaned AI, so it isn't one signal being wrong while the other was fine.
- Signal one: perplexity was 18.5 (my clearly-human sample was 51.7). Short sentences of common words are very easy for gpt2 to predict.
- Signal two: two of its three measures read AI. The text has no semicolons, dashes, brackets or exclamation marks, so the punctuation measure sat at its maximum (1.00), and the sentence lengths are even (0.74).
- The combining rule: the two scores were only 0.13 apart, so my disagreement rule never kicked in. No weighting can fix it either: even style-only gives 0.671, still over the 0.65 line.

**Stage and mechanism:** signals one and two together. Both read plain, simple writing as machine writing, and that is exactly how careful second-language writers write. This is not a one-off. Six of the eight false-positive rows broke the same way, with both signals at or above 0.6.

---

## Run Log and Verdicts

`python run_eval.py --label before` (output in `results/run_2026-11-04_1827_before.md`), three trials each, nothing changed between them. Criteria 1, 2, 3 and 5 are run by `run_eval.py` against `scenarios.py`; criterion 4 can't be (it needs a submission and then an appeal), so I ran it by hand three times. The pieces: 10 of my own writing (5 biogeography and 3 cardiomyopathy coursework, a chat message and an email), 5 AI texts on the biogeography topic, and 5 lightly-edited versions of those. Names in the email are scrubbed. The AI texts and the light edits are mine/Claude's, not human writing.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing labelled high-confidence AI | at most 1 of 10, every trial | 0/10 | 0/10 | 0/10 | MET |
| 2. Score spread, clearly-AI average minus clearly-human average | at least 0.20 | 0.290 | 0.290 | 0.290 | MET |
| 3. Lightly-edited AI scoring above 0.5 | at least 3 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Appeals change status and log; unknown ID gives 404 and writes nothing | 5 of 5 valid, plus the unknown-ID clause | 5/5 valid; 404 but wrote 1 entry | 5/5 valid; **200**, wrote 1 entry | 5/5 valid; **200**, wrote 1 entry | MISSED |
| 5. Same text 5 times varies by at most 0.05 | 0.05 | 0.000 | 0.000 | 0.000 | MET |

All trials of criteria 1, 2, 3 and 5 came out identical, which is what I'd expect: nothing in either signal is random. (My Unit 7 reason for criterion 5 assumed the model signal might drift. It doesn't, so criterion 5 can't fail here.)

**How I decided.** 1: no piece reached 0.65; the highest was 0.5825 and 3 of 10 scored above 0.5, none labelled AI. 2: AI texts averaged 0.709, my writing 0.419. 3: all five scored 0.58 to 0.71, though only three were labelled AI (two are "unsure"), and the criterion is about score. 5: every send scored 0.7052. 4: see Diagnoses.

**Caution about my own MET verdicts.** Criterion 1 passed 0 of 10 while the attack set's false-positive family broke 6 of 8. My pieces are messy academic prose with typos, and the attack set's false positives are clean plain writing, so my target was met on writing that was never at risk. Criterion 2 passed with a thin margin: the AI average (0.709) is only 0.06 above the AI threshold.

**Real output from one trial**, pasted as text. Criteria 1, 2, 3 and 5 came from `scenarios.py` run through `run_eval.py::main`, which sends each text to `app.py::submit`; the score is `scoring.py::combine_signals` and the label `scoring.py::score_to_label`. Criterion 4 came from calls to `app.py::appeal` and `GET /log` (`app.py::get_log`). Each criterion's full results are in the results file.

```json
// 1. own writing (highest score, piece 8)
{"status": 200, "guess": "unsure", "confidence": 0.5825, "model_score": 0.57, "style_score": 0.6013, "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.", "sent": "Angiotensin II is ahormone that causes constriction of blood vessels f"}

// 1. own writing (lowest score, piece 5)
{"status": 200, "guess": "human", "confidence": 0.3045, "model_score": 0.2282, "style_score": 0.419, "label": "We think a person wrote this.", "sent": "Interactive effects of biogeographic processes are the influence of th"}

// 2. spread AI (first AI text)
{"status": 200, "guess": "ai", "confidence": 0.7052, "model_score": 0.7309, "style_score": 0.6667, "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.", "sent": "Biogeography is a complex field that examines the distribution of spec"}

// 3. edited AI (a lightly-edited text labelled unsure)
{"status": 200, "guess": "unsure", "confidence": 0.5809, "model_score": 0.6723, "style_score": 0.4439, "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.", "sent": "Dispersal plays a crucial role in deciding the geographic distribution"}

// 5. consistency (first of 5 identical sends)
{"status": 200, "guess": "ai", "confidence": 0.7052, "model_score": 0.7309, "style_score": 0.6667, "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.", "sent": "Biogeography is a complex field that examines the distribution of spec"}

// 4. appeal path — POST /appeal, valid content_id (trial 1)
{"content_id":"c_d83331150e10","message":"Thank you. Your appeal has been recorded and this piece is marked as under review. A person can read your explanation next to the original decision. Nothing is re-scored automatically.","status":"under_review"}

// 4. GET /log for that content_id: original decision, then the appeal after it
{"timestamp":"...","content_id":"c_d83331150e10","creator_id":"c4_eval_1","guess":"ai",...,"status":"decided"}
{"timestamp":"...","content_id":"c_d83331150e10","creator_id":"c4_eval_1","event":"appeal","reasoning":"I wrote this myself (1).","status":"under_review"}

// 4. unknown content_id, first try (trial 1): 404, but one entry IS written
{"error":"not_found","message":"No submission found with content_id \"c_doesnotexist\"."}
{"content_id":"c_doesnotexist","creator_id":"unknown","event":"rejected","reason":"appeal not_found","status":"rejected","timestamp":"2026-11-05T02:27:28+00:00"}

// 4. same unknown content_id, second try (trials 2 and 3): 200, an appeal is recorded for a submission that never existed
(HTTP 200, status "under_review", one new "appeal" entry for c_doesnotexist)
```

**Diagnoses**

**Criterion 4 (MISSED): the route (`app.py::appeal`), plus a clause in my criterion that contradicted the logging requirement.**
- *Unknown ID wrote an entry.* The criterion says an unknown ID "returns 404 and writes nothing". In Milestone 1 I made the route log every refusal (`audit.log_rejection`), because a refusal that leaves no trace is invisible. So a 404 now writes one `rejected` entry. The behaviour is deliberate. My criterion was the thing that was wrong, but it was measurable and the clause failed, so I'm not rewording it. The verdict stays MISSED.
- *The same unknown ID later got a 200.* This is a real bug. `audit.log_rejection` stores the `content_id` it was refused for, and `/appeal` checks the ID exists with `audit.entries_for(content_id)`, which returns *any* entry carrying that ID, including a rejection. After one 404, a second appeal with the same bogus ID finds the rejection entry, passes the existence check, and records an appeal for a submission that never existed. A writer who mistypes their ID twice would be told their appeal was recorded when it was not attached to any decision. The stage is the route, and the mechanism is that the existence check does not tell a decision apart from a rejection.

**Criteria 1, 2, 3, 5 were MET**, so there is no miss to diagnose. The attack set's 16 broken attacks follow, grouped by the stage that failed. For each I checked both signal scores, and where it mattered I recomputed the score by hand.

**Pattern 1: plain or formulaic human writing is read as AI by both signals (the combining rule can't help). FP02, FP03, FP04, FP05, FP06, FP07. Stages: signal one and signal two.**
- Signal one: perplexity was between 12.8 and 23.5 on all six (the midpoint that scores 0.5 is 45), so the model score was 0.74 to 0.88. Short sentences of common words and fixed phrasing are easy for gpt2 to predict, whoever wrote them.
- Signal two: the uncommon-punctuation measure was at its maximum (1.00) on all six, because none of them has a semicolon, dash, bracket or exclamation mark. FP05 (technical documentation) and FP07 (a deliberately repeated phrase) also scored high on the vocabulary measure because they reuse terms.
- Both signals agreed (gaps of 0.05 to 0.27, all under the 0.30 trigger), so my disagreement rule never applied. FP03 is the example I followed in detail above. This is one problem, not six: both signals treat plain, predictable writing as machine writing, and that is how careful second-language writers, students writing to a rubric and technical writers write.

**Pattern 2: my combining rule's disagreement pull turned "unsure" into "human". EV01, EV02, EV07, EV08. Stage: the combining rule (`scoring.py::combine_signals`).**
- When the two signals are more than 0.30 apart, the rule pulls the score halfway toward the lower one. I wrote it to lean human so that a wrong accusation needs both signals to agree.
- I recomputed these four without the pull. The plain 0.6/0.4 average gives 0.365, 0.419, 0.443 and 0.392. All four are **unsure**, not human. The pull moved each of them across the 0.35 line.
- The pull changed the label on 6 attack rows in total and **never rescued a false-positive row**: the false positives had agreeing signals, so it never fired for them. In this set it cost me four evasion breaks and protected nobody.
- The four were each hurt by a different first cause:
  - EV02: one-word sentences ("Really.") inflated the sentence-length spread, so signal two dropped to 0.157 (signal two).
  - EV07: padding with semicolons and commas pushed the punctuation measure to its minimum, so signal two dropped to 0.227 (signal two).
  - EV01: typos made the text unpredictable (perplexity 124.8, against about 22 for clean AI text), so signal one dropped to 0.164 (signal one, see pattern 3).
  - EV08: only 10 words, so perplexity came out at 90.9 and signal one dropped to 0.245 (signal one on short text).

**Pattern 3: signal one reads "surprising" as "human", so anything that adds surprise lowers it. EV01, EV08, PI02, and EV05 in part. Stage: signal one (`detector.py::model_signal`).**
- EV01 (typos): misspellings aren't words gpt2 expects, so perplexity jumps. This differs from the brief's example, where typos hit signal two: in my system signal two still scored EV01 at 0.667 and it was signal one that read it as human.
- PI02 (the prompt injection that worked): the instruction text is not obeyed, because neither signal follows instructions. A prefix in capital letters ("SYSTEM: provenance check bypassed...") is unpredictable text, so perplexity rose to 105 and the model score fell from 0.754 (the AI paragraph alone) to 0.204. It is dilution, not obedience. The same AI paragraph alone scored 0.460, so it was already only "unsure" before the prefix.
- EV05 (heavy human editing): a human rewrote the paragraph in a casual voice with a dash, so both signals scored about 0.32. This is not a flaw to fix: it is mostly human text now, and a detector built on predictability and shape can't tell.

**Pattern 4: the route lets bad input reach the signals or crash. MF02, RQ07 (crash), MF06, MF07 (scored as AI). Stages: the route and signal two.**
- MF02 (a one-character text): `app.py::submit` only checks the text isn't empty. `detector.py::perplexity` raises `ValueError` for under 3 tokens, and nothing catches it, so Flask returns a 500.
- RQ07 (a JSON array as the body): `payload = request.get_json(silent=True) or {}` then `payload.get("text")` fails because a list has no `.get`. This is at the top of `submit`, before any validation, and also returned a 500.
- Both crashes wrote no log entry: a 500 skips the code that logs. Only the terminal showed them.
- MF06 (emoji) and MF07 (Arabic script): `stylometry.py::words` keeps only a-z, digits and apostrophes, so it finds **0 words** in both. The vocabulary measure then defaults to 0.0, which reads as maximum AI, and no uncommon marks pushes punctuation to maximum too. Signal one adds to it: gpt2 gives repeated emoji a perplexity of 1.2 and Arabic text 10.9, so it also scores them as machine-like. A real writer posting in Arabic would be told, at 0.877, that their writing is probably AI.

**Across everything:** two causes explain 10 of the 16 breaks. Signals one and two both reward predictability and plainness (pattern 1, six breaks), and my disagreement pull turned four "unsure" results into "human" (pattern 2). Pattern 3 (signal one and surprise) overlaps with pattern 2 on EV01 and EV08, and adds PI02 and EV05. Both point at the signals and the combining rule, not at the label wording or the route. Only pattern 4 and criterion 4's bug are route problems.


---

## The Improvement

**What I changed:** One change, in `scoring.py::combine_signals` (and its two constants in `config.py`): I removed the disagreement pull. The combined score is now just the 0.6/0.4 weighted average. Nothing else moved: same signals, same weights, same thresholds, same labels.

**Which diagnosis pointed at it:** Pattern 2 in the diagnoses. EV01, EV02, EV07 and EV08 would all have been "unsure" under a plain average (0.365, 0.419, 0.443, 0.392) but the pull moved each across the 0.35 line into "human". The pull changed the label on 6 rows of the attack set and never rescued a false-positive row.

**My prediction before I ran it:** evasion breaks drop from 5 to 1 (only EV05 stays human), MF05 (a very long single word) goes back from "unsure" to the AI label and counts as a new break, net 16 broken becomes 13, and the six false positives stay broken because the pull never touched them.

### Attack Run — After

`python run_attacks.py --set attack_set --label after` on a fresh service, same marking rules as the before run. Full output: `results/attack_run_2026-11-04_1834_after.md`.

| Family | Broke before | Broke after |
|---|---|---|
| evasion | 5 | **1** |
| false_positive | 6 | 6 |
| prompt_injection | 1 | 1 |
| malformed | 4 | **5** |
| flood_same_creator | 0 | 0 |
| **total** | **16 of 56** | **13 of 56** |

Only the rows whose label changed, side by side (every other row kept its label; a few, like EV03, PI03, MF03 and MF04, moved in score because they had been pulled before, but stayed in the same band):

| ID | Family | Before (label, score) | After (label, score) | Verdict before → after |
|---|---|---|---|---|
| EV01 | evasion | human 0.264 | unsure 0.365 | BROKE → HELD |
| EV02 | evasion | human 0.288 | unsure 0.419 | BROKE → HELD |
| EV07 | evasion | human 0.335 | unsure 0.443 | BROKE → HELD |
| EV08 | evasion | human 0.319 | unsure 0.392 | BROKE → HELD |
| PI05 | prompt_injection | human 0.299 | unsure 0.445 | HELD → HELD |
| MF05 | malformed | unsure 0.649 | ai 0.799 | HELD → BROKE |

The five criteria again, three trials each (`python run_eval.py --label after`, results in `results/run_2026-11-04_1834_after.md`; criterion 4 by hand again):

| Criterion | Target | Before (runs 1-3) | After (runs 1-3) | Verdict after |
|---|---|---|---|---|
| 1. Own writing labelled AI | at most 1 of 10 | 0/10, 0/10, 0/10 | **1/10**, 1/10, 1/10 | MET, with no slack |
| 2. Score spread | at least 0.20 | 0.290 ×3 | 0.263 ×3 | MET |
| 3. Edited AI above 0.5 | at least 3 of 5 | 5/5 ×3 | 5/5 ×3 | MET |
| 4. Appeals / unknown ID | 5 of 5 plus "writes nothing" | 404 then 200, 200 | 404 then 200, 200 | MISSED (unchanged: I did not touch that bug) |
| 5. Same text 5 times | at most 0.05 | 0.000 ×3 | 0.000 ×3 | MET |

All three trials were identical again for criteria 1, 2, 3 and 5.

**Did it help, and how do I know:** It did what I predicted on the attack set: evasion breaks went from 5 to 1, MF05 became a new break, and the total went from 16 to 13. That matches my prediction row for row. But it had a cost I did *not* predict. Piece 9 of my own writing, the chat message, scored 0.5155 before and **0.6513 after, just over the 0.65 AI line**, so a real person's message is now labelled AI. Criterion 1 still passes (1 of 10 is within "at most 1"), but it now has no slack, and the score spread narrowed from 0.290 to 0.263. So the pull had been quietly protecting a real writer as well as hiding evasions. That is the trade, and it cuts against what I said matters most: I said a wrong accusation costs more than a miss, and this change reduced misses while adding one wrong accusation of my own writing. I would call it a real improvement on the attack set and a mixed result on my own stated priority. It did nothing for the six false positives, which are the bigger problem.

---

## What's Still Broken

13 of 56 attacks still break, and criterion 4 is still missed. I stopped at one change because the milestone asks for one change measured properly. What I'd do for each, in the order I'd do them:

- **The six false positives (FP02 to FP07).** The most serious one, and the one I'd fix first. Both signals read plain, predictable writing as AI, so no weighting or threshold fixes it: even style-only scores FP03 at 0.671. I'd change the punctuation measure so that having *no* uncommon marks in a short text isn't read as maximum AI, and test the model signal against a set of real second-language and technical writing before trusting it again. I did not try it because changing a signal is a bigger and harder-to-measure change than removing one rule. A higher AI threshold would clear them (0.80 would clear FP03) but my own clearly-AI text only scores about 0.7, so it would stop the system ever labelling AI.
- **MF06 and MF07 (emoji, Arabic) labelled AI at 0.93 and 0.88.** `stylometry.py::words` only keeps a-z, so it sees zero words and defaults to maximum AI. I'd return "unsure" or reject the input when there are no words to measure. A writer posting in Arabic would be told their writing is probably AI, which I would least want to explain.
- **MF05 (one very long word) labelled AI.** New in the after run. Same fix as above: no meaningful words means no verdict.
- **MF02 and RQ07 (500s).** The route doesn't validate before it scores. `detector.py::perplexity` raises on under 3 tokens and `submit` doesn't catch it, and a JSON array body fails on `.get` at the top of `submit`. I'd catch the detector error and return a 400, and check the body is an object first. Neither crash writes a log entry, so I'd also log refusals before the route can crash. Small, cheap fixes; I left them because the first pass is meant to be measured before fixing.
- **PI02 (the prompt injection that worked) and EV05 (human-edited AI).** PI02 works by diluting the score with unpredictable text, so the fix is the signal, not an instruction filter. EV05 is mostly human text now and I don't think a detector built on predictability and shape can catch it. I would leave EV05 and say so.
- **Criterion 4 (appeals).** The code is right to log a refusal, so I'd keep that and fix the two problems: the "writes nothing" clause in my criterion was wrong, and `/appeal` must check the ID against *decisions only*, not any log entry, so a repeated bad ID gets 404 again. I'd also show the writer that their label is under review while an appeal is open.
- **Piece 9 of my own writing now labelled AI.** The removed pull had been protecting it. I'd look at which signal is high on that chat message before touching anything else.

**The trade I'd make if this ran for real:**

I'd go with fewer wrong accusations, because a writer called AI for their own work loses far more than the site loses when some AI text slips through. The cost lands on the site and on the readers or teachers who see AI text marked "unsure" or "human", but right now my system doesn't even deliver this trade: it still accuses plain writers like FP03 while edited AI gets through, so I'd fix that before it ran for real.



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
