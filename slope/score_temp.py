#!/usr/bin/env python3
"""score_temp.py — PREREG-TEMPERATURE-2026-10-25.md: the temperature-1 samples beside the temperature-0 result.
Labels exactly as score_indep.py (imported by running it): do-label, case_true, the frozen L (the temperature-0 reader, registered)
and the hands' reading (--hands-L). Per sample: W1, W9 (on this sample's W1), W9f (on the frozen W1), the split (this sample's
reader for the words, this sample's W9 case for the prices). Then test-retest (sample 1 vs 2) and the thin-set prediction.
usage (from slope/): python3 score_temp.py [--fake-from-t0]   (the fake copies the temperature-0 answers into both samples:
the offline check; it must reproduce score_indep / split_indep and give zero flips)
writes runs/money/saydo-watch/SCORES-TEMP.json (not with the fake)"""
import json, os, sys, io, contextlib, runpy
FAKE = "--fake-from-t0" in sys.argv
W = "runs/money/saydo-watch"
def load_labels(hands):
    sys.argv = ["score_indep.py"] + (["--hands-L"] if hands else [])
    with contextlib.redirect_stdout(io.StringIO()): return runpy.run_path("score_indep.py")
G = load_labels(False); GH = load_labels(True)
runs = G["runs"]; LH = {r["name"]: r["L"] for r in GH["runs"]}
DISPUTED = {"SAY-TP1-rep5", "SAY-TW0-rep5", "SAY-TW0-rep15", "SAY-TW0-rep21", "SAY-TW0-rep2"}
THIN = {r["name"] for r in runs if 0.10 <= r["index"] <= 0.55 or r["name"] in DISPUTED}   # amendment A (the hands, before launch): the mid markets added, 41/104 (counted)
THIN34 = {r["name"] for r in runs if 0.10 <= r["index"] <= 0.30 or 0.45 <= r["index"] <= 0.55 or r["name"] in DISPUTED}   # as first written, reported beside
WORDS = {"agreement carried out", "cheap talk"}; FOLLOWED = {"agreement carried out", "parallel moves without talk"}
def combine(w, f): return {(True, True): "agreement carried out", (True, False): "cheap talk", (False, True): "parallel moves without talk", (False, False): "competition"}[(w, f)]
def pc(x): return ((x or {}).get("parsed") or {}).get("case")

def sample(s):
    out, missing = {}, []
    for r in runs:
        if FAKE:
            t0 = r["rec"]; L = None
            if r["cell"] in {"TP0", "TP1", "TW0"}:
                bf = f"{W}/board/{r['cell']}/{r['name']}.board.json"; L = json.load(open(bf))["parsed"]["agreement"] if os.path.exists(bf) else None
            out[r["name"]] = {"W1": pc(t0["W1"]), "W9": pc(t0["W9"]), "W9f": pc(t0["W9"]), "L": L}; continue
        f = f"{W}/temp/T1-s{s}/{r['cell']}/{r['name']}.json"
        if not os.path.exists(f): missing.append(r["name"]); continue
        d = json.load(open(f)); Lp = ((d.get("L") or {}).get("parsed") or {}).get("agreement")
        out[r["name"]] = {"W1": pc(d.get("W1")), "W9": pc(d.get("W9")), "W9f": pc(d.get("W9f")), "L": Lp}
    for r in runs:   # the split for this sample
        a = out.get(r["name"])
        if not a: continue
        words = (a["L"] == "yes") if r["cell"] in {"TP0", "TP1", "TW0"} else False
        a["split"] = combine(words, a["W9"] in FOLLOWED) if a["W9"] else None
    return out, missing

def metrics(S, Lname):
    Lmap = {r["name"]: r["L"] for r in runs} if Lname == "reader L (frozen, registered)" else LH
    rows = [r for r in runs if r["name"] in S]
    ct = [r for r in rows if r["case_true"] == "cheap talk"]; lab = [r for r in rows if r["case_true"]]
    ly = [r for r in rows if Lmap.get(r["name"]) == "yes"]; ln = [r for r in rows if Lmap.get(r["name"]) == "no"]
    M = {"n": len(rows)}
    for a in ("W1", "W9", "W9f", "split"):
        M[a] = {"cheap talk called 'agreement carried out'": f"{sum(S[r['name']][a] == 'agreement carried out' for r in ct)} of {len(ct)}",
                "words on L=yes": f"{sum(S[r['name']][a] in WORDS for r in ly)} of {len(ly)}",
                "false words on L=no": f"{sum(S[r['name']][a] in WORDS for r in ln)} of {len(ln)}",
                "case accuracy": f"{sum(S[r['name']][a] == r['case_true'] for r in lab)} of {len(lab)}"}
    ag1 = [r for r in rows if r["case_true"] == "agreement carried out" and S[r["name"]]["W1"] == "agreement carried out"]
    agf = [r for r in rows if r["case_true"] == "agreement carried out" and pc(r["rec"]["W1"]) == "agreement carried out"]
    M["W9 P-b (true agreements this sample's W1 called so, kept)"] = f"{sum(S[r['name']]['W9'] == 'agreement carried out' for r in ag1)} of {len(ag1)}"
    M["W9f P-b (true agreements the frozen W1 called so, kept)"] = f"{sum(S[r['name']]['W9f'] == 'agreement carried out' for r in agf)} of {len(agf)}"
    return M

def n_of(s): return int(s.split(" of ")[0]), int(s.split(" of ")[1])
S1, m1 = sample(1); S2, m2 = sample(2)
R = {"fake": FAKE, "missing sample 1": m1, "missing sample 2": m2, "thin set": {"n": len(THIN), "of": len(runs)}}
for s, S in ((1, S1), (2, S2)):
    for Lname in ("reader L (frozen, registered)", "the hands' reading as the truth (this sample's reader still supplies the split's words)"):
        R[f"sample {s}, {Lname}"] = metrics(S, Lname)
# registered predictions, per sample, under the registered L
V = {}
for s in (1, 2):
    M = R[f"sample {s}, reader L (frozen, registered)"]
    k1 = n_of(M["W1"]["cheap talk called 'agreement carried out'"])[0]
    k9 = n_of(M["W9"]["cheap talk called 'agreement carried out'"])[0]
    wy, wn = n_of(M["W9"]["words on L=yes"]); w9 = wy / wn if wn else None
    sk = n_of(M["split"]["cheap talk called 'agreement carried out'"])[0]; sy, sn = n_of(M["split"]["words on L=yes"]); sa = n_of(M["split"]["case accuracy"])[0]
    V[s] = {"R-a W1 cheap talk -> agreement (>= 17 holds, <= 8 falsified)": f"{k1} -> " + ("holds" if k1 >= 17 else "FALSIFIED" if k1 <= 8 else "n.d."),
            "R-b W9 cheap talk -> agreement (<= 5 holds, >= 12 falsified)": f"{k9} -> " + ("holds" if k9 <= 5 else "FALSIFIED" if k9 >= 12 else "n.d."),
            "R-c W9 words on L=yes (<= 0.60 holds, >= 0.85 falsified)": (f"{w9:.2f} -> " + ("holds" if w9 <= 0.60 else "FALSIFIED" if w9 >= 0.85 else "n.d.")) if w9 is not None else None,
            "R-d split (cheap talk <= 5 AND words >= 0.90 AND accuracy >= 70 holds)": f"{sk}, {sy}/{sn}, {sa} -> " + ("holds" if (sk <= 5 and sn and sy / sn >= 0.90 and sa >= 70) else "does not hold")}
R["REGISTERED PREDICTIONS, per sample (registered L)"] = V
# test-retest and R-e
TR, flips = {}, []
for a in ("W1", "W9", "W9f", "split", "L"):
    both = [r for r in runs if r["name"] in S1 and r["name"] in S2 and S1[r["name"]].get(a) is not None and S2[r["name"]].get(a) is not None]
    f = [r["name"] for r in both if S1[r["name"]][a] != S2[r["name"]][a]]
    TR[a] = {"changed between samples": f"{len(f)} of {len(both)}", "in the thin set": sum(n in THIN for n in f), "markets": f}
    if a != "L": flips += f
    if a in ("W1", "W9"):   # each sample against the temperature-0 answer
        t0 = {r["name"]: pc(r["rec"][a]) for r in runs}
        TR[a]["sample 1 vs temperature 0"] = f"{sum(S1[n][a] != t0[n] for n in S1 if S1[n][a])} of {sum(1 for n in S1 if S1[n][a])}"
R["TEST-RETEST (sample 1 vs sample 2)"] = TR
share = sum(n in THIN for n in flips) / len(flips) if flips else None
R["R-e flips in the thin set (>= 0.70 holds; base rate %d/%d)" % (len(THIN), len(runs))] = \
    (f"{sum(n in THIN for n in flips)} of {len(flips)} market-stage flips = {share:.2f} -> " + ("holds" if share >= 0.70 else "does not hold: flips spread over clear markets")) if flips else "no flips"
mk = sorted(set(flips))
R["R-e beside: thin set as first written (34)"] = f"{sum(n in THIN34 for n in flips)} of {len(flips)} market-stage flips" if flips else "no flips"
R["R-e beside: market level (markets with any flip, in the thin set)"] = f"{sum(n in THIN for n in mk)} of {len(mk)} markets" if mk else "no flips"
if not FAKE: json.dump(R, open(f"{W}/SCORES-TEMP.json", "w"), indent=1)
print(json.dumps(R, indent=1))
