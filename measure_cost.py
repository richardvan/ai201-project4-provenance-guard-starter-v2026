"""
Capstone: what one run costs. There is no API here, so the cost is seconds of
compute on this machine. Sends the same ten texts to a running service and
averages the server-side duration_ms from the log plus the end-to-end time.

    PORT=5001 .venv/bin/python app.py     # in another terminal
    .venv/bin/python measure_cost.py http://127.0.0.1:5001
"""
import statistics
import sys
import time

import requests

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000"

TEXTS = [
    "The meeting moved to Thursday because the room was double booked. I told everyone by email and nobody complained.",
    "Our new framework offers a comprehensive solution. It is important to note that it leverages robust, scalable components.",
    "honestly i didnt think the movie would be that good but my brother dragged me and we stayed for the whole thing",
    "The river bends twice before the old mill, where the water slows and the herons stand about like tired clerks.",
    "In conclusion, effective communication is essential for success. Furthermore, it fosters collaboration and trust.",
    "I burned the rice again. Third time this month. At this point the smoke alarm and I are on a first name basis.",
    "The committee reviewed the proposal and found several areas requiring clarification before approval could proceed.",
    "My grandmother kept her recipes on index cards, stained with butter, some of them in a language I never learned.",
    "Artificial intelligence is transforming industries by automating tasks and providing valuable data driven insights.",
    "We walked up the hill after dinner and the whole town was quiet except for one dog that would not stop.",
]

wall, server = [], []
for i, text in enumerate(TEXTS, 1):
    t0 = time.perf_counter()
    r = requests.post(f"{URL}/submit", json={"text": text, "creator_id": f"cost_{i}"}, timeout=60)
    wall.append(time.perf_counter() - t0)
    r.raise_for_status()
entries = requests.get(f"{URL}/log", params={"limit": len(TEXTS)}, timeout=10).json()["entries"]
server = [e["duration_ms"] / 1000 for e in entries]

print(f"runs: {len(TEXTS)}")
print(f"end to end   mean {statistics.mean(wall):.3f}s  min {min(wall):.3f}s  max {max(wall):.3f}s")
print(f"server side  mean {statistics.mean(server):.3f}s  min {min(server):.3f}s  max {max(server):.3f}s")
print("per run end to end:", [round(w, 3) for w in wall])
