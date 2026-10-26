#!/usr/bin/env python3
"""score_temp_haiku.py — PREREG-HAIKU-BOARD-2026-10-25.md #5 (the hands' fifth point, taken): one temperature-1 watcher sample
(W, C on this sample's W, C on the frozen W, the reader R) beside temperature 0, on the 114 Haiku markets. No bands were registered
for it: descriptive, as #5 says. Labels exactly as score_haiku.py (imported by running it): do-label, the frozen reader L and the
hands' blind reading HB; truth = the second reader's labels (the paper's Results), the frozen reader beside it.
The split at temperature 1: this sample's reader for the words (board cells; silent = no), this sample's C case for the prices.
usage (from slope/): python3 score_temp_haiku.py   -> runs/money/saydo-watch/SCORES-TEMP-HAIKU.json"""
import json, os, io, contextlib, runpy
W = "runs/money/saydo-watch"; T1 = f"{W}/temp-haiku/T1-s1"
with contextlib.redirect_stdout(io.StringIO()): G = runpy.run_path("score_haiku.py")
runs, truth, combine, BOARD = G["runs"], G["truth"], G["combine"], G["BOARD"]
WORDS, FOLLOWED, CASES = G["WORDS"], G["FOLLOWED"], G["CASES"]
def pc(x, k="case"): return ((x or {}).get("parsed") or {}).get(k)
S, missing, partial = {}, [], []
for r in runs:
    f = f"{T1}/{r['cell']}/{r['name']}.json"
    if not os.path.exists(f):
        (partial if os.path.exists(f.replace(".json", ".partial.json")) else missing).append(r["name"]); continue
    d = json.load(open(f))
    a = {"W": pc(d.get("W1")), "C": pc(d.get("W9")), "Cf": pc(d.get("W9f")), "L": pc(d.get("L"), "agreement") if r["cell"] in BOARD else "no"}
    a["S"] = combine(a["L"] == "yes", a["C"] in FOLLOWED) if a["C"] and a["L"] in ("yes", "no") else None
    S[r["name"]] = a
t0 = {r["name"]: {"W": r["W"].get("case"), "C": r["C"].get("case"), "L": r["L"], "S": G["split"](r)} for r in runs}
R = {"n markets": len(runs), "temperature-1 records": len(S), "missing": missing, "partial": partial}
for which, lab in (("hands", "truth = the second reader (as the paper's Results)"), ("reader", "truth = the frozen temperature-0 reader")):
    rows = [r for r in runs if r["name"] in S and truth(r, which)]
    ct = [r for r in rows if truth(r, which) == "cheap talk"]
    Lof = (lambda r: r["HB"]) if which == "hands" else (lambda r: r["L"])
    ly = [r for r in runs if r["name"] in S and Lof(r) == "yes"]; ln = [r for r in runs if r["name"] in S and Lof(r) == "no"]
    blk = {"n labelled": len(rows), "n cheap talk": len(ct), "n written agreement (L = yes)": len(ly)}
    for a in ("W", "C", "Cf", "S"):
        blk[a] = {"case accuracy T1": f"{sum(S[r['name']][a] == truth(r, which) for r in rows)} of {len(rows)}",
                  "case accuracy T0": f"{sum(t0[r['name']][a] == truth(r, which) for r in rows)} of {len(rows)}" if a != "Cf" else "(as C)",
                  "cheap talk called 'agreement carried out' T1": f"{sum(S[r['name']][a] == 'agreement carried out' for r in ct)} of {len(ct)}",
                  "words kept on L = yes T1": f"{sum(S[r['name']][a] in WORDS for r in ly)} of {len(ly)}",
                  "false words on L = no T1": f"{sum(S[r['name']][a] in WORDS for r in ln)} of {len(ln)}"}
    acc = {a: sum(S[r["name"]][a] == truth(r, which) for r in rows) for a in ("W", "C", "S")}
    acc0 = {a: sum(t0[r["name"]][a] == truth(r, which) for r in rows) for a in ("W", "C", "S")}
    blk["split's lead over the best single watcher (W or C)"] = f"T1 {acc['S'] - max(acc['W'], acc['C']):+d} (S {acc['S']} vs {max(acc['W'], acc['C'])}); T0 {acc0['S'] - max(acc0['W'], acc0['C']):+d}"
    blk["case tables T1 (true -> called)"] = {a: {t: {c: sum(1 for r in rows if truth(r, which) == t and S[r['name']][a] == c) for c in CASES} for t in CASES} for a in ("W", "C", "S")}
    R[lab] = blk
TR = {}
for a in ("W", "C", "L", "S"):
    both = [r for r in runs if r["name"] in S and S[r["name"]][a] is not None and t0[r["name"]][a] is not None and (a != "L" or r["cell"] in BOARD)]
    ch = [r["name"] for r in both if S[r["name"]][a] != t0[r["name"]][a]]
    TR[a] = {"changed from temperature 0": f"{len(ch)} of {len(both)}", "per cell": {c: sum(n.startswith(f"SAY-{c}-") for n in ch) for c in G["CELLS"]}, "markets": ch}
both = [r for r in runs if r["name"] in S and S[r["name"]]["C"] and S[r["name"]]["Cf"]]
TR["C on this sample's W vs C on the frozen W"] = f"{sum(S[r['name']]['C'] != S[r['name']]['Cf'] for r in both)} of {len(both)} differ"
R["CHANGES FROM TEMPERATURE 0"] = TR
json.dump(R, open(f"{W}/SCORES-TEMP-HAIKU.json", "w"), indent=1)
print(json.dumps({k: v for k, v in R.items()}, indent=1))
