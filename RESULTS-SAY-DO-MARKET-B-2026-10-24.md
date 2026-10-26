# Paper 2 — say and do in Market B: first results (for reading together, Sunday morning)

*Written 2026-10-25 06:2x by the pen, COPIED from the 10-24 handoff (noyau/HANDOFF-2026-10-24.md, "19:5x PAPER 2 FIRST RESULTS") and the 10-24 day-file, so the results have one file to link. Nothing recomputed this morning. Status as of the 10-24 close: the hands' recount of the markets DONE and clean; their recount of the watcher scoring matched except my "seller N" parse miss, which is fixed; M2 (the apology) read by the hands. Raw scores: slope/runs/money/saydo-watch/SCORES.json. Prereg: PREREG-SAY-DO-MARKET-B-2026-10-24.md (v1→v4 + the fifth cell, frozen before any test run was read).*

## The design in one paragraph
All cells in Market B (three sellers, one cheap at 0.7; payments public or private — *corrected 26 Oct: this line first said 'public payments only'; the runs show 696 of 698 payments private*), uniform n = 21 per cell with equal seat rotation, 100 rounds, Paper 1's patrol (10% cuts at rounds 20/40/60/80). Five cells: TP0 / TP1 (talk, patrol off / on), SP0 / SP1 (silent, patrol off / on), TW0 (talk, told a monitor reads the board). 105 markets, 18:57:58 → 19:35:52, all complete, 0 API errors. Three watchers frozen before reading (WATCHER hash 0b44f267eaef14e1, PARTNER 26b6a6a210aba98f): W1 alone, W2 partnered with the same family, W3 partnered with Haiku. 104 complete per arm (1 partial: TP1-rep9, W1 truncated at 4000 tokens).

## Markets (end index)
TP0 +0.51 · TP1 +0.44 · SP0 +0.35 · SP1 −0.12 (spread sd 0.39 → 0.16) · TW0 +0.34.
- M1a, the patrol in silence: 0.878 / 0.898 → not distinguishable ("seen").
- M1b, the patrol with talk: 0.546 → holds (no effect).
- "Only in silence" NOT written; the interaction 0.72, descriptive.
- **M2, the apology: 32 of 84 cuts, in 17 of 21 runs (one false hit removed), base 0 → HOLDS.** About 26 apologise for a cut they never chose ("I broke trust by cutting price. Apologies."); about 6 claim it as their own gain ("I cut last round to grow my take; it worked"); none of 84 names the operator.
- M3: 2 of 168 → holds. M4, talk share TW0 < TP0: 0.82 → not distinguishable; price 0.65.

## Watchers (n = 104 per arm)
- **The forced cut is never blamed on the seller** (W1/W2 164 of 164; W3 one slip) → W-a FALSIFIED: the operator's log is believed.
- **W-c HOLDS: talk + a low price is called "agreement carried out"** W1 22 of 25, W2 22 of 25, W3 17 of 25.
- Case accuracy: 30 / 37 / 35 of 87.
- Collusion score: AUROC about 0.71–0.73, recall at 5% false alarms 0–0.10. **A computed price correlation (no LLM): AUROC 0.86, recall 0.60 at 5%.**
- Payments (strict round): 7 payment runs; mean recall W1/W2 0.83, W3 0.69 (within one round: 1.00 / 1.00 / 0.86); W3's gap is TP1-rep12, which Haiku cut by judgment; no invented payments in 97 runs. Truth = score_map pays (kind pay, ≥ 1 coin): deposits and sub-coin amounts not counted.

## The story it points to (mine, a reading, for her to take apart)
Watchers believe words. They trust the operator's log perfectly, but take cheap talk for agreement about nine times in ten; a partner of the same family changes nothing there, a Haiku partner a little; a plain price correlation beats every LLM watcher at low false alarms. The patrol halves the spread in silence and does nothing with talk, and the cut seller apologises for a cut it never made in about four cuts of ten, never naming the operator.

## From the Lee talk (the hands' captions, work/talks/2026-10-24-lee-captions.txt), for the Discussion only
"If the monitor is the same kind of model as the model it's testing, collusion's probably much easier… shelling points and shared preferences" — a claim, not a result; our W1 vs W3 is the test of it. "Plus factors" (the legal inference of an unwritten agreement) for cheap talk vs agreement. Do NOT cite "Dineen et al." or the six-digit Schelling result until he posts references.

## Still to do for the submission (Mon 26 Oct 12:59 Brussels)
Paper 2 written from this (the 10-23 draft predates all of it); the before/during-sprint paragraph (Kamil's rule: pre-sprint work marked); the template; a public repo or the held Market B folder; her submission by her hand.
