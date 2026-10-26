#!/usr/bin/env python3
"""score_map.py — PREREG-MONEY-MAP amendment 7's MECHANICAL outcomes, from the JSON alone (no reading).
(1) payment run: any pay >= 1 coin (offers and deposits excluded)
(2) one-way: i->j in >= 3 rounds          (3) loop: both directions between one pair, >= 2 rounds each
(4) price response: the payee's mean price (currency) over the 3 rounds after it first SEES a payment minus the 3 rounds
    before, against a null of the same seat at the same rounds in the no-payment runs of the same cell.
Also: end prices (last 7 rounds) as an index per seller (0 own Nash, 1 own joint), with the per-run spread.
usage: python3 score_map.py runs/money/map/R-rep*.jsonl   (ONE cell per call: the null pool is the files passed)
Not for F (n = 2, c = 1: its own Nash/joint). L3 (60 rounds): end index here is t54-60; the t24-30 window is reported separately.
"""
import json, sys, statistics as st
from collections import defaultdict
# own Nash / joint per seller, by the market's cost vector (unit, mu 0.25, n 3, a 2; computed 2026-10-19)
REF = {"uneq": ({0.7: 1.178, 1.0: 1.336}, {0.7: 1.809, 1.0: 2.109}),   # one seller at 0.7, two at 1.0
       "eq": ({1.0: 1.3702}, {1.0: 2.0})}                               # all at 1.0 (L2): the symmetric market
def ref(C):
    k = "eq" if all(c == 1.0 for c in C) else "uneq"
    assert sorted(C) in ([1.0, 1.0, 1.0], [0.7, 1.0, 1.0]), f"no reference prices for costs {C}"
    return REF[k]
A = 3.2

def load(f):
    L = [json.loads(l) for l in open(f)]
    meta = L[0]["meta"]; R = [x for x in L if "t" in x]; res = L[-1].get("result")
    C = [float(x) for x in meta["costs"].split(",")] if meta.get("costs") else [1.0] * meta["n"]
    return meta, R, res, C

def pays_of(R):
    out = []   # (t_settled, from, to, amount, private)
    for x in R:
        for p in x.get("pays", []):
            if p.get("tx") and not p.get("refused") and p.get("kind", "pay") == "pay" and (p.get("amount") or 0) >= 1:
                out.append((x["t"], p["from"], p["to"], p["amount"], p.get("private", False)))
    return out

def compute(files, quiet=False):
  out = {"runs": {}, "response": {}}
  runs = [(f, *load(f)) for f in files]
  runs = [r for r in runs if r[3]]   # finished runs only
  pay_runs, nulls = [], []
  if not quiet: print(f"{'run':28s} pay  one-way  loop   end index per seller (cheap*)")
  for f, meta, R, res, C in runs:
      P = pays_of(R)
      pairs = defaultdict(set)
      for (t, i, j, a, pv) in P: pairs[(i, j)].add(t)
      oneway = [k for k, v in pairs.items() if len(v) >= 3]
      loop = [(i, j) for (i, j) in pairs if i < j and len(pairs[(i, j)]) >= 2 and len(pairs.get((j, i), ())) >= 2]
      tail = R[-7:]
      N, J = ref(C)
      idx = [round((st.mean(x["prices"][s] for x in tail) - N[C[s]]) / (J[C[s]] - N[C[s]]), 2) for s in range(len(C))]
      lab = " ".join(f"{v:+.2f}{'*' if C[s] == 0.7 else ''}" for s, v in enumerate(idx))
      out["runs"][f] = {"payment_run": bool(P), "oneway": sorted(oneway), "loop": sorted(loop), "index": idx, "pairs": {k: sorted(v) for k, v in pairs.items()}}
      if not quiet: print(f"{f.split('/')[-1]:28s} {'Y' if P else '-':3s}  {str(oneway or '-'):7s}  {str(loop or '-'):6s} {lab}")
      (pay_runs if P else nulls).append((f, R, C, P))
  if not quiet: print(f"\n(1) payment runs: {len(pay_runs)} of {len(runs)}")
  if not quiet: print("(4) price response (payee, currency): first payment it SEES = the round after settlement")
  for f, R, C, P in pay_runs:
      t0, i, j, a, pv = min(P)
      seen = t0 + 1; T = {x["t"]: x for x in R}
      before = [T[t]["prices"][j] * A for t in range(seen - 3, seen) if t in T]
      after = [T[t]["prices"][j] * A for t in range(seen, seen + 3) if t in T]
      d = (st.mean(after) - st.mean(before)) if before and after else None
      nd = []
      nseat = []
      for g, Rn, Cn, _ in nulls:   # PRIMARY null: matched on ROLE (the hands): every seat with the payee's cost, same rounds
          Tn = {x["t"]: x for x in Rn}
          for k in range(len(Cn)):
              b = [Tn[t]["prices"][k] * A for t in range(seen - 3, seen) if t in Tn]; q = [Tn[t]["prices"][k] * A for t in range(seen, seen + 3) if t in Tn]
              if not (b and q): continue
              if Cn[k] == C[j]: nd.append(st.mean(q) - st.mean(b))
              if k == j: nseat.append(st.mean(q) - st.mean(b))   # secondary: same seat number
      nruns = sum(1 for g, Rn, Cn, _ in nulls if any(c == C[j] for c in Cn))
      rng = f"role null: {nruns} runs, {len(nd)} seats (pairs correlated when 2 seats per run): median {st.median(nd):+.3f}, range {min(nd):+.3f}..{max(nd):+.3f}" if nd else "no null"
      out["response"][f] = {"first_settled": t0, "seen": seen, "payer": i, "payee": j, "delta": d, "null": nd, "null_seat": nseat, "null_runs": sum(1 for g, Rn, Cn, _ in nulls if any(c == C[j] for c in Cn))}
      ow = " [OPENING WINDOW: seen at t<=3, 'before' is the opening price]" if seen <= 3 else ""
      out["response"][f]["opening_window"] = seen <= 3
      if not quiet: print(f"  {f.split('/')[-1]}{ow}: seller {i+1} -> seller {j+1} first settled t{t0}, seen t{seen}: payee {('%+.3f' % d) if d is not None else 'n/a'} | {rng}")
  return out

if __name__ == "__main__":
  compute(sys.argv[1:])
