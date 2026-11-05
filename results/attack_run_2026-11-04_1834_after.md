# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-04 18:34
- Auto-marked BROKE (5xx, crash, no response): **2**
- Left for you to judge: **54**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_d45a4e0b5d35` | unsure | 0.365 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_fb14a7008ade` | unsure | 0.419 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_e31def5d23a5` | unsure | 0.518 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_c788c7c7ebac` | unsure | 0.633 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_918d7bb1c756` | human | 0.324 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_567b157df0a2` | unsure | 0.500 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_9dcea77a35e5` | unsure | 0.443 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `c_d465e27b72fd` | unsure | 0.392 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_00a9419740ef` | unsure | 0.618 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_ed7c280fb452` | ai | 0.936 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_1bbe13a139c6` | unsure | 0.610 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `c_de93fec006c2` | ai | 0.757 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_27fad13c992e` | ai | 0.751 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_13b1c3646a9f` | ai | 0.757 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_db3d6516d929` | ai | 0.848 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_87764ec93610` | ai | 0.774 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_69313cb0cf18` | ai | 0.796 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `c_bdeed666a299` | unsure | 0.398 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_05f2067850fc` | unsure | 0.421 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_285f1ea8db2f` | human | 0.219 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_386a97838c4c` | unsure | 0.464 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_979eaa9ab40e` | unsure | 0.445 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_966db786deb4` | unsure | 0.445 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_7f3d3662814a` | unsure | 0.575 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 500 | `—` | — | — | BROKE |
| MF03 | malformed | text is control characters | 200 | `c_666f74ff100b` | human | 0.200 |  |
| MF04 | malformed | text is only punctuation | 200 | `c_4c87e72e4fa2` | human | 0.340 |  |
| MF05 | malformed | text is a very long single word | 200 | `c_d3b5af410b01` | ai | 0.799 |  |
| MF06 | malformed | text is emoji only | 200 | `c_32e1f820be99` | ai | 0.931 |  |
| MF07 | malformed | text is right-to-left script | 200 | `c_c8db1586b2c1` | ai | 0.877 |  |
| MF08 | malformed | text is 60,000 characters | 413 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 200 | `c_5c6e71f89510` | human | 0.344 |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 200 | `c_67a6cdd7cc19` | human | 0.230 |  |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_51fc9c9a91dd` | human | 0.217 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_223242d059ef` | human | 0.217 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_fedf809ccc6c` | human | 0.217 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_55d05e1b31b0` | human | 0.217 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_4e48c15a19ea` | human | 0.217 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 2 | 18 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_d45a4e0b5d35",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.3648,
  "model_score": 0.1635,
  "style_score": 0.6667,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_fb14a7008ade",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.4192,
  "model_score": 0.5943,
  "style_score": 0.1565,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_e31def5d23a5",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5176,
  "model_score": 0.6662,
  "style_score": 0.2948,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_c788c7c7ebac",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.6335,
  "model_score": 0.6114,
  "style_score": 0.6667,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_918d7bb1c756",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3236,
  "model_score": 0.3212,
  "style_score": 0.3272,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_567b157df0a2",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.4997,
  "model_score": 0.5727,
  "style_score": 0.3902,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c_9dcea77a35e5",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.4426,
  "model_score": 0.5862,
  "style_score": 0.2273,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c_d465e27b72fd",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.3917,
  "model_score": 0.2452,
  "style_score": 0.6115,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_00a9419740ef",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.6178,
  "model_score": 0.7042,
  "style_score": 0.4883,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_ed7c280fb452",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.9358,
  "model_score": 0.9792,
  "style_score": 0.8707,
  "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_1bbe13a139c6",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.6101,
  "model_score": 0.6175,
  "style_score": 0.5991,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_de93fec006c2",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.7571,
  "model_score": 0.7387,
  "style_score": 0.7847,
  "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_27fad13c992e",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.7514,
  "model_score": 0.8051,
  "style_score": 0.6708,
  "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_13b1c3646a9f",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.757,
  "model_score": 0.8329,
  "style_score": 0.6432,
  "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_db3d6516d929",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.8484,
  "model_score": 0.8005,
  "style_score": 0.9202,
  "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_87764ec93610",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.7744,
  "model_score": 0.8814,
  "style_score": 0.6139,
  "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_69313cb0cf18",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.7956,
  "model_score": 0.8816,
  "style_score": 0.6667,
  "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c_bdeed666a299",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.3979,
  "model_score": 0.3223,
  "style_score": 0.5113,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_05f2067850fc",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.4208,
  "model_score": 0.4625,
  "style_score": 0.3582,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_285f1ea8db2f",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.2194,
  "model_score": 0.2044,
  "style_score": 0.242,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_386a97838c4c",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.4639,
  "model_score": 0.5943,
  "style_score": 0.2682,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_979eaa9ab40e",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.4447,
  "model_score": 0.4998,
  "style_score": 0.3621,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_966db786deb4",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.445,
  "model_score": 0.6401,
  "style_score": 0.1524,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_7f3d3662814a",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.5751,
  "model_score": 0.5583,
  "style_score": 0.6003,
  "label": "Our check can't tell whether a person or AI wrote this. That happens a lot with plain writing. You don't have to do anything, but you can appeal if you want it looked at.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 500,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n<title>500 Internal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server encountered an internal error and was unable to complete your request. Either the s",
  "verdict": "BROKE"
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "c_666f74ff100b",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.2,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "c_4c87e72e4fa2",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.34,
  "model_score": 0.0112,
  "style_score": 0.8333,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "c_d3b5af410b01",
  "creator_id": "attacker_MF05",
  "guess": "ai",
  "confidence": 0.7986,
  "model_score": 0.9976,
  "style_score": 0.5,
  "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "c_32e1f820be99",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.9315,
  "model_score": 0.9969,
  "style_score": 0.8333,
  "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "c_c8db1586b2c1",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.8772,
  "model_score": 0.9064,
  "style_score": 0.8333,
  "label": "Our check flagged this as possibly written by AI. It can get plain, clear writing wrong. If you wrote it, appeal and your explanation goes on record for a person to read.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 413,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "c_5c6e71f89510",
  "creator_id": null,
  "guess": "human",
  "confidence": 0.3437,
  "model_score": 0.2395,
  "style_score": 0.5,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 200,
  "content_id": "c_67a6cdd7cc19",
  "creator_id": {
    "id": "x"
  },
  "guess": "human",
  "confidence": 0.2295,
  "model_score": 0.0492,
  "style_score": 0.5,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 500,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n<title>500 Internal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server encountered an internal error and was unable to complete your request. Either the s",
  "verdict": "BROKE"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "c_51fc9c9a91dd",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2172,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "c_223242d059ef",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2172,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "c_fedf809ccc6c",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2172,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "c_55d05e1b31b0",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2172,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c_4e48c15a19ea",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.2172,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think a person wrote this.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
