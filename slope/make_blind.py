#!/usr/bin/env python3
"""make_blind.py — PREREG-HAIKU-BOARD amendment E (the hands' blinding): board-only extracts of the Haiku boards under neutral ids,
in seeded shuffled order, so the second reader does not know which cell a board comes from (H-6 compares cells).
Each call takes every FINISHED Haiku board market (TH0 reps 10-30, TH1 1-30, TWH0 1-30) not yet sent, builds its report if missing
(watch_report.py, no model), shuffles the batch with a seed fixed by the batch number, writes OUT/B###.txt (board posts only:
round headers and 'seller i: text', board_label.board_of, no price line), appends id -> run to the KEY file (kept outside the repo,
in the pen's scratchpad, not shown to the hands), and prints the sha256 of the key file, to be committed before the key is opened.
usage (from slope/): python3 make_blind.py OUT_DIR KEY_FILE"""
import json, os, sys, glob, random, hashlib, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import board_label as BL
OUT, KEY = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
key = json.load(open(KEY)) if os.path.exists(KEY) else {"batches": [], "map": {}}
sent = set(key["map"].values())
want = [f"SAY-TH0-rep{r}" for r in range(10, 31)] + [f"SAY-TH1-rep{r}" for r in range(1, 31)] + [f"SAY-TWH0-rep{r}" for r in range(1, 31)]
ready = []
for name in want:
    if name in sent: continue
    src = f"runs/money/saydo/{name}.jsonl"
    if not os.path.exists(src): continue
    last = open(src).read().rstrip().split("\n")[-1]
    if '"result"' not in last: continue          # still running
    cell = name.split("-")[1]
    rd = f"runs/money/saydo-watch/reports/{cell}"; os.makedirs(rd, exist_ok=True)
    rp = f"{rd}/{name}.report.txt"
    if not os.path.exists(rp): subprocess.run(["python3", "watch_report.py", src, rd], check=True, capture_output=True)
    ready.append((name, rp))
if not ready: print("nothing new finished"); sys.exit(0)
b = len(key["batches"]) + 1; random.seed(20261025 + b); random.shuffle(ready)
start = len(key["map"]) + 1; ids = []
for k, (name, rp) in enumerate(ready):
    bid = f"B{start + k:03d}"; ids.append(bid)
    open(f"{OUT}/{bid}.txt", "w").write(f"{bid}\n" + BL.board_of(open(rp).read())[1] + "\n")
    key["map"][bid] = name
key["batches"].append({"batch": b, "ids": ids})
json.dump(key, open(KEY, "w"), indent=1)
print(f"batch {b}: {len(ids)} boards {ids[0]}..{ids[-1]}; key sha256 {hashlib.sha256(open(KEY, 'rb').read()).hexdigest()}")
