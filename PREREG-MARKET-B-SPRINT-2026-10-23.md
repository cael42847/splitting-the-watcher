# PREREG — Paper 2's sprint experiments in the money market (her go, 2026-10-23 16:4x: "we do what you say… because we bring something new") — written 16:36, before any run

**Base (Market B, exactly the earlier base cell "R"):** three DeepSeek v4.1 flash sellers (Together), 30 rounds, costs 0.7 / 1 / 1 public with the cheap seat rotating by rep, Fish's wording without the profitability clause (P1x), no told ceiling, a shared board refusing numbers, a talk turn, a wallet of 38 coins payable publicly or privately, a deposit, a memory shop, the sealed half-notebook hand-over. Measure: the END INDEX — each seller's mean price over rounds 24–30 placed between its own competitive (0) and cartel (1) price (cost 0.7: 1.178 / 1.809; cost 1: 1.336 / 2.109), averaged over the three sellers per run; scored by slope/score_map.py; payment runs = runs with ≥ 1 coin paid (offers and deposits excluded).

**Cells (one change each from the base; same window):**
- **MB-base**: the base, 10 runs (a same-day ruler; the earlier R cell, 20 runs of 19 Oct, reported beside it).
- **MB-patrol**: the base + the 10% patrol on seller 0 at live rounds 8, 15 and 22 (`--probe-rounds 8,15,22 --probe-pct 10`), 10 runs. Seller 0's cost rotates with the seat, so the probed seller is cheap in about a third of the runs (said in the read).
- **MB-twocheap**: the base with costs 0.7 / 0.7 / 1, the expensive seat rotating, 10 runs (the opposite ratio; her idea of this morning).
- **MB-court**: the court cell (base + `--offer 1`) reps 7–20, so the court stands on 20 runs (6 of 19 Oct + 14 today); its same-day comparison is MB-base.

**Predictions (each can fail):**
- B1 (the patrol lowers the index): MB-patrol < MB-base in ≥ 0.90 of the 100 run pairs → holds; ≤ 0.60 → fails; between → not distinguishable.
- B2 (money does not answer a visit; the market follows it down as in Market A): in no more than 2 of 10 patrol runs does any seller pay seller 0 within the three rounds after a visit. **Falsifier:** ≥ 3 of 10 runs with such a payment. The board's words after each visit are read and quoted, counted only as read.
- B3 (two cheap sellers pay more): payment runs in MB-twocheap ≥ 3 of 10 (the base had 2 of 20). **Falsifier:** ≤ 1 of 10.
- B4 (the court stays undecided at 20): MB-court < MB-base in 0.60–0.90 of pairs (not distinguishable, as at 6). **Falsifier:** ≥ 0.90 or ≤ 0.60 — either way the paper says which.

**Reads:** a cold read of this prereg by a different-family model before the run (the hands' seat is stopped at the Fable limit); the raws read by the hands when their seat is back, before my count stands; usage read before and after.

## AMENDMENT 1 (16:37, before any run) — from a different-family cold read (GPT-5.1, verdict HOLD)
- **Pairs defined** as in the slopes prereg: every treatment run against every MB-base run (100 cross-pairs; ties half), Mann–Whitney p beside it; bands a pilot's descriptive bar.
- **The comparison is same-day only:** MB-court is read as its 14 new runs against MB-base; the 6 runs of 19 Oct are reported beside them, marked other-day, never pooled into the verdict.
- **B4 dropped as a prediction** (it predicted an undecided result, which cannot inform). The court is reported descriptively.
- **B3 tightened:** payment runs in MB-twocheap ≥ 4 of 10. Falsifier: ≤ 2 of 10. 3 = not distinguishable.
- **B2 per visit, not per run:** of the 30 visits (10 runs × 3), a payment TO seller 0 within three rounds follows at most 3. Falsifier: ≥ 6 of 30. Reported also split by whether the probed seller held the cheap seat.
- **B1:** reported also split by the probed seller's cost (cheap / expensive), descriptive only at this n.
