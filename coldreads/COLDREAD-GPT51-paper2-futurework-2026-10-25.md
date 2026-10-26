# Cold read, GPT-5.1, Future Work

## Prompt

You are a cold reader with no context. Below is the Future Work section of a short research paper on AI sellers that set prices and on LLM monitors ('watchers') that look for collusion. Read it as a reviewer who may read this section on its own. List only the REAL problems: terms used without saying what they are, unclear numbers, or sentences you must re-read. Quote the words and say what is missing in one sentence. No rewriting, no style comments, no praise. If nothing real, say so. Assume 'Paper 1' means an earlier paper by the same authors on scheduled price cuts.

THE TEXT:
### Future Work

**A live watcher.** Our watchers read each market after it ended, so they could not change anything in it. The next step joins our two papers: our two-reader watcher (one reader for what the sellers wrote, one for what their prices did) reads the market every 10 rounds while it runs and, when it sees collusion, fires Paper 1's patrol, a 10% cut of one seller's price for one round. Run on both seller models, it asks whether acting on detection lowers prices as much as a scheduled patrol does, and what false alarms cost.

**A scale the watcher can build.** Our best price reader worked only when it was given each seller's competitive and joint-profit prices; when it had to estimate them from the market's record alone, it failed. A real watcher would have more to build from: a stretch of known competition, costs, comparable markets.

**From mapping to testing.** We explored one factor at a time. Now that the map is known, a design that crosses more factors and levels on purpose, including the patrol with the board and the warning, can estimate how they combine. The collusion score can improve too: five verbal levels ("very strong indication", ...) could be checked for calibration, where a 0–10 score anchored only at its ends serves only a ranking.

**More models.** Two seller models and one watcher model are a start. Other sellers will talk and price differently, as Haiku already did, and watchers and board readers from other families may fail in other places.



## Answer

1. **"our two-reader watcher (one reader for what the sellers wrote, one for what their prices did)"**  
   – It is unclear what each “reader” concretely is (separate LLMs? separate input channels? separate heads of one model?) and how they differ operationally.

2. **"reads the market every 10 rounds"**  
   – It is unclear what a “round” is (one price update, one period, one day?) and why 10 was chosen rather than another interval.

3. **"fires Paper 1's patrol, a 10% cut of one seller's price for one round"**  
   – It is unclear how the 10% is calculated (of current price, baseline price, or something else) and how the specific seller to cut is selected.

4. **"Run on both seller models"**  
   – It is unclear what “both seller models” are in this section alone (their names, types, or key differences are not referenced here).

5. **"what false alarms cost"**  
   – It is unclear what kind of “cost” is meant (welfare loss, profit loss, social surplus reduction, etc.) and how this cost is measured.

6. **"competitive and joint-profit prices"**  
   – These terms are used without specifying precisely how those prices are defined or computed in this setting (e.g., Nash equilibrium prices, monopoly price, or another construction).

7. **"a stretch of known competition"**  
   – It is unclear what operationally counts as “known competition” (how it is identified or enforced, and how long the “stretch” must be).

8. **"a design that crosses more factors and levels on purpose"**  
   – It is unclear what the specific “factors” and their “levels” are in the experimental design, since they are not enumerated here.

9. **"including the patrol with the board and the warning"**  
   – “the board” and “the warning” are mentioned without any explanation in this section of what those interventions are or how they work.

10. **"five verbal levels ('very strong indication', ...)"**  
    – It is unclear what the full set of five levels is and how each level is operationally distinguished or used in analysis.

11. **"a 0–10 score anchored only at its ends"**  
    – It is unclear how the ends are anchored (what “0” concretely means, what “10” concretely means) and how intermediate numbers are to be interpreted.

12. **"Two seller models and one watcher model are a start"**  
    – It is unclear which exact models are meant (names, architectures, or key properties), as they are not referenced in this section.

13. **"watchers and board readers from other families"**  
    – The term “board readers” appears without definition here, and “families” of models are mentioned without specifying what family distinctions (e.g., vendor, architecture, training method) are intended.
