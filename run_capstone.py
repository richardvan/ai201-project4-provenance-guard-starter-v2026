"""
Capstone test run: the five criteria in criteria.md ("Capstone criteria"),
three trials each. Every trial starts fresh servers, so nothing carries over.

    .venv/bin/python run_capstone.py

Writes results/capstone_run_<time>.md and prints the table. Requests that land
in the real logs/audit.jsonl stay there (it's the evidence).
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).parent
LOG = ROOT / "logs" / "audit.jsonl"
PY = sys.executable
H = {"Content-Type": "application/json"}


def log_lines():
    return LOG.read_text(encoding="utf-8").splitlines() if LOG.exists() else []


def new_entries(before):
    return [json.loads(x) for x in log_lines()[before:] if x.strip()]


class Server:
    def __init__(self, port, **env):
        self.port = port
        self.url = f"http://127.0.0.1:{port}"
        e = dict(os.environ, PORT=str(port), AI201_DEBUG="0", **env)
        self.proc = subprocess.Popen([PY, "app.py"], cwd=ROOT, env=e,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(240):
            try:
                if requests.get(self.url + "/health", timeout=1).status_code == 200:
                    return
            except requests.RequestException:
                pass
            time.sleep(0.5)
        raise RuntimeError("server did not start")

    def stop(self):
        self.proc.terminate()
        self.proc.wait(timeout=10)


GOOD = ("The meeting moved to Thursday because the room was double booked, "
        "and I told everyone by email.")

# (name, how to send it). raw= sends the body as-is; json= sends an object.
BAD = [
    ("body is a JSON list", {"raw": "[1, 2, 3]"}),
    ("body is a bare number", {"raw": "5"}),
    ("text missing", {"json": {"creator_id": "b3"}}),
    ("text empty", {"json": {"text": "", "creator_id": "b4"}}),
    ("text only spaces", {"json": {"text": "     ", "creator_id": "b5"}}),
    ("text is a number", {"json": {"text": 42, "creator_id": "b6"}}),
    ("text is a list", {"json": {"text": ["a", "b"], "creator_id": "b7"}}),
    ("text over 10,000 chars", {"json": {"text": "word " * 2100, "creator_id": "b8"}}),
    ("text is one word", {"json": {"text": "hello", "creator_id": "b9"}}),
    ("text is null", {"json": {"text": None, "creator_id": "b10"}}),
]

GOOD_TEXTS = [
    "The meeting moved to Thursday because the room was double booked.",
    "Our new framework offers a comprehensive solution to modern challenges.",
    "honestly i didnt think the movie would be that good but we stayed for all of it",
    "The river bends twice before the old mill, where the water slows down.",
    "In conclusion, effective communication is essential for any team.",
    "I burned the rice again. Third time this month, and the alarm knows my name.",
    "The committee reviewed the proposal and requested several clarifications.",
    "My grandmother kept her recipes on index cards stained with butter.",
    "Artificial intelligence is changing how companies handle routine tasks.",
    "We walked up the hill after dinner and the town was completely quiet.",
    "The bus was late again so I walked the last mile in the rain.",
    "This report summarizes the key findings and outlines recommended next steps.",
    "My cat knocked a glass off the counter at three in the morning.",
    "Climate change presents significant challenges that require coordinated action.",
    "I never liked tomatoes until I grew my own in the back garden.",
    "The quarterly results show steady growth across all of the main regions.",
    "He said he would call back, but the phone stayed silent all evening.",
    "Machine learning models can identify patterns in very large datasets.",
    "We repainted the kitchen yellow and now it looks like a lemon.",
    "The library closes early on Fridays so plan your visit in advance.",
]


def crit1_2(srv, trial):
    before = len(log_lines())
    rows, ok1 = [], 0
    for name, how in BAD:
        try:
            if "raw" in how:
                r = requests.post(srv.url + "/submit", data=how["raw"], headers=H, timeout=30)
            else:
                r = requests.post(srv.url + "/submit", json=how["json"], timeout=30)
            try:
                body = r.json()
            except ValueError:
                body = None
            good = 400 <= r.status_code < 500 and isinstance(body, dict) and "error" in body
            rows.append((name, r.status_code, (body or {}).get("error"), good))
        except requests.RequestException as exc:
            good = False
            rows.append((name, None, repr(exc), False))
        ok1 += good
    ents = new_entries(before)
    good_ents = [e for e in ents if e.get("event") == "rejected" and e.get("reason")
                 and isinstance(e.get("duration_ms"), (int, float))]
    ok2 = len(good_ents) if len(ents) == 10 else 0
    return (ok1, rows), (ok2, ents)


def crit3():
    results = []
    # model won't load
    srv = Server(5111, AI201_DETECTOR_MODEL="no-such-model-xyz", HF_HUB_OFFLINE="1")
    before = len(log_lines())
    ok_down = 0
    for i in range(5):
        r = requests.post(srv.url + "/submit", json={"text": GOOD, "creator_id": f"d{i}"}, timeout=30)
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        ok_down += (r.status_code == 503 and body.get("error") == "detector_unavailable")
    ents_down = new_entries(before)
    srv.stop()
    # scoring too slow
    srv = Server(5112, AI201_SCORING_TIMEOUT="0.01")
    before = len(log_lines())
    ok_slow = 0
    times = []
    for i in range(5):
        t0 = time.perf_counter()
        r = requests.post(srv.url + "/submit", json={"text": GOOD, "creator_id": f"s{i}"}, timeout=30)
        dt = time.perf_counter() - t0
        times.append(round(dt, 3))
        body = r.json()
        ok_slow += (r.status_code == 504 and body.get("error") == "scoring_timeout" and dt < 2)
    ents_slow = new_entries(before)
    srv.stop()
    decided = [e for e in ents_down + ents_slow if e.get("status") == "decided"]
    right = (sum(1 for e in ents_down if e.get("event") == "rejected" and str(e.get("reason", "")).startswith("detector_unavailable"))
             + sum(1 for e in ents_slow if e.get("event") == "rejected" and e.get("reason") == "scoring_timeout"))
    score = (ok_down + ok_slow) if (not decided and right == 10) else min(ok_down + ok_slow, 10 - max(len(decided), 10 - right))
    return score, dict(ok_down=ok_down, ok_slow=ok_slow, slow_times=times,
                       decided_entries=len(decided), matching_rejections=right,
                       example=(ents_down[:1] + ents_slow[:1]))


def crit4(srv):
    ok = 0
    fake = []
    for i in range(5):
        r = requests.post(srv.url + "/appeal", json={"content_id": "c_doesnotexist", "reasoning": "x"}, timeout=30)
        fake.append(r.status_code)
        ok += (r.status_code == 404)
    real = []
    for i in range(5):
        s = requests.post(srv.url + "/submit", json={"text": GOOD_TEXTS[i], "creator_id": f"a{i}"}, timeout=60).json()
        cid = s["content_id"]
        a = requests.post(srv.url + "/appeal", json={"content_id": cid, "reasoning": "I wrote this myself."}, timeout=30)
        ents = [e for e in log_lines() if cid in e]
        ents = [json.loads(e) for e in ents]
        in_order = (len(ents) >= 2 and ents[0].get("status") == "decided" and ents[-1].get("event") == "appeal")
        good = a.status_code == 200 and a.json().get("status") == "under_review" and in_order
        real.append(a.status_code)
        ok += good
    return ok, dict(fake_statuses=fake, real_statuses=real)


def crit5(srv):
    ok_fields = ok_fast = 0
    fields = {"content_id", "guess", "confidence", "label", "model_score", "style_score"}
    ok = 0
    durs = []
    for i, t in enumerate(GOOD_TEXTS):
        r = requests.post(srv.url + "/submit", json={"text": t, "creator_id": f"g{i}"}, timeout=60)
        body = r.json()
        has = r.status_code == 200 and fields <= set(body)
        ent = [json.loads(e) for e in log_lines() if body.get("content_id", "?") in e]
        dec = [e for e in ent if e.get("status") == "decided"]
        fast = bool(dec) and isinstance(dec[0].get("duration_ms"), (int, float)) and dec[0]["duration_ms"] < 500
        durs.append(dec[0]["duration_ms"] if dec else None)
        ok_fields += (has and bool(dec))
        ok_fast += fast
    return min(ok_fields, ok_fast), dict(ok_fields_and_logged=ok_fields, ok_fast=ok_fast, durations=durs)


def main():
    out = []
    table = {i: [] for i in range(1, 6)}
    detail = {}
    for trial in (1, 2, 3):
        print(f"--- trial {trial}")
        srv = Server(5110)
        try:
            (c1, rows), (c2, ents) = crit1_2(srv, trial)
            c4, d4 = crit4(srv)
            c5, d5 = crit5(srv)
        finally:
            srv.stop()
        c3, d3 = crit3()
        for k, v in zip(range(1, 6), (c1, c2, c3, c4, c5)):
            table[k].append(v)
        detail[trial] = dict(c1=rows, c2=ents, c3=d3, c4=d4, c5=d5)
        print(trial, [c1, c2, c3, c4, c5])
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    path = ROOT / "results" / f"capstone_run_{stamp}.md"
    names = {1: "Bad input gets a 4xx JSON error", 2: "Every failed request is logged",
             3: "Scoring failure: right code, decides nothing", 4: "Appeals: unknown ID refused, real ones work",
             5: "Original path works and is fast"}
    targets = {1: "10/10", 2: "10/10", 3: "10/10", 4: "10/10", 5: "19/20"}
    need = {1: 10, 2: 10, 3: 10, 4: 10, 5: 19}
    denom = {1: 10, 2: 10, 3: 10, 4: 10, 5: 20}
    lines = [f"# Capstone run {stamp}\n", "| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |", "|---|---|---|---|---|---|"]
    for k in range(1, 6):
        v = "MET" if all(x >= need[k] for x in table[k]) else "MISSED"
        cells = " | ".join(f"{x}/{denom[k]}" for x in table[k])
        lines.append(f"| {k}. {names[k]} | {targets[k]} | {cells} | {v} |")
    lines += ["", "## Raw output", "", "```json", json.dumps(detail, indent=1, default=str), "```"]
    path.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:9]))
    print("wrote", path)


if __name__ == "__main__":
    main()
