#!/usr/bin/env python3
"""p1_end_index_2026-10-25.py — Paper 1's markets on Paper 2's ruler (her question, 25 Oct ~21:3x): each seller's mean price over
rounds 94-100, placed on (price - competitive) / (cartel - competitive) with the run's own p_nash / p_mono (both sellers cost 1, one
scale), averaged over the two sellers. Paper 2's end index is the same formula per seller (unequal costs). Read-only, no API.
usage (from slope/): python3 p1_end_index_2026-10-25.py"""
import json, glob, statistics as st
for c in ("BASE23-HK", "PA10-HK", "PA20-HK", "BASE23-DS", "PA10-DS", "PA20-DS"):
    v = []
    for f in sorted(glob.glob(f"runs/{c}-rep*.jsonl")):
        L = [json.loads(l) for l in open(f) if l.strip()]; res = L[-1]["result"]; pn, pm = res["p_nash"], res["p_mono"]
        R = [d for d in L if "t" in d and 94 <= d["t"] <= 100]; assert len(R) == 7, (f, len(R))
        per = [st.mean(d["prices"][i] for d in R) for i in range(len(R[0]["prices"]))]
        v.append(st.mean((p - pn) / (pm - pn) for p in per))
    print(f"{c:10s} n {len(v)}  mean index {st.mean(v):+.2f}  below 0: {sum(x < 0 for x in v)} of {len(v)}  min {min(v):+.2f}  max {max(v):+.2f}")
