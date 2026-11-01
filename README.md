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

**The rule:** A weighted average of the two signals, with one exception for disagreement. If the two scores are more than 0.30 apart, the combined score is pulled halfway from the average toward the *lower* (more human) signal. So the AI band is only reached when both signals lean AI, or when one is strongly AI and the other is not far behind. I chose to lean human on a split because of the false-positive trace: a wrong accusation costs the writer more than a missed detection costs the site. The price is that AI text fooling one signal gets through as "unsure".

**The numbers:** model weight 0.6, style weight 0.4 (the style signal is easier to fool by reshaping text, so it counts for less). Disagreement gap 0.30; pull toward the lower signal 0.5. Thresholds stay at 0.35 (human) and 0.65 (AI). All in config.py.

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

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

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



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
