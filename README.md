# splitting-the-watcher

Companion repository for **"Does splitting an LLM watcher's job improve its collusion detection?"**, Marion Nowicki & Cael, Apart Research AI Collusion Research Sprint, October 2026. **[Read the paper (PDF)](Splitting-the-Watcher-2026-10-26.pdf)** · [the paper's source](PAPER-2-DRAFT-2026-10-25.md)

In Paper 1, a patrol of scheduled price cuts lowered collusion between two LLM sellers with equal costs and no shared board. Here we ask who should watch the market, and whether splitting the watcher's job helps. In 218 markets of three LLM sellers (DeepSeek v4.1 flash or Claude Haiku 5.5), one with a lower cost, with and without a shared board and the patrol, we first find that the same patrol does not adapt to this market: it took most patrol markets below the competitive price, including Haiku markets whose prices were already at the competitive level. A watcher is needed to say when to cut. We then compare LLM watchers on two questions, whether the sellers wrote an agreement and whether prices followed. A single watcher trades one mistake for the other: it believes cheap talk, or, without the sellers' words, misses their agreements. Splitting the job, a first watcher followed by two readers, one for the board and one for the prices (given each seller's competitive and joint-profit prices), sorted the most markets into the right case on both seller models (75 of 87 DeepSeek and 80 of 100 Haiku markets; the best single watcher, 53 and 60) and kept its lead at temperature 1.

Paper 1: [cael42847/which-single-restriction](https://github.com/cael42847/which-single-restriction).

## Layout

The repository root is the paper's `experiments/sprint-2026-10/` folder; paths in the paper are relative to it.

| Path | What it is |
|---|---|
| `Splitting-the-Watcher-2026-10-26.pdf` | The paper |
| `PAPER-2-DRAFT-2026-10-25.md`, `build_paper2_pdf.py` | Its source and the script that builds the PDF (headless Chrome) |
| `PREREG-*.md` | Pre-registrations, each written before its run |
| `RESULTS-*.md` | Reads of batches against their pre-registrations |
| `HANDS-BLIND-MARKS-HAIKU-2026-10-25.md`, `hands-blind-haiku/` | The label checker's blind reading of the Haiku boards (B001–B081) and the id-to-market key, opened only after the marks |
| `NGUYEN-SLIDES-FOR-PAPER-2-2026-10-24.md` | Our notes on the four-case frame presented at the sprint |
| `coldreads/` | Independent cold reads of draft sections (GPT-5.1) |
| `slope/game.py`, `slope/market.py`, `slope/ledger.py` | The market engine (Paper 1's engine, with the three-seller market and the warning sentence `--monitor`) |
| `slope/runsaydo*.sh`, `slope/runmarketb.sh` | The exact commands for each market batch |
| `slope/watch_report.py`, `slope/watch_run*.py`, `slope/board_label.py`, `slope/run_temp.py`, `slope/make_blind.py` | The reports the watchers read, every watcher and reader, the temperature-1 re-reads, the blind batches |
| `slope/runwatchsaydo.sh`, `slope/runprices.sh` | Launchers for the watcher runs |
| `slope/score_*.py`, `slope/split_indep.py` | Scorers: recompute every number from the run files alone, no API calls |
| `slope/draw_paper2_*.py`, `slope/paper2-figs/` | Figure scripts and the figures |
| `slope/p1_end_index_2026-10-25.py`, `slope/runs/BASE23-*`, `PA10-*`, `PA20-*` | Paper 1's markets placed on Paper 2's end index |
| `slope/runs/money/saydo/` | Every market file (`SAY-*`: DeepSeek cells SP/TP/TW0, Haiku cells SH/TH/TWH0): full settings, and per round every raw generation beside its parse |
| `slope/runs/money/saydo-watch/` | Every watcher's and reader's answers (`out/`, `prices/`, `ruler/`, `ruler-w9/`, `ownscale/`, `board/`, `temp/`, `temp-haiku/`), the reports they read (`reports/`), the run logs, and the `SCORES-*.json` the scorers write |
| `slope/runs/money/sprint/` | The 23 October 30-round markets, part of the watchers' development set (never scored) |

## Reproduce

Python 3 (the scorers need only the standard library; the figure scripts need matplotlib). Every script runs from `slope/`:

```
cd slope
python3 score_indep.py --hands-L     # DeepSeek: board reader vs the label checker -> SCORES-INDEP-HANDS-L.json
python3 split_indep.py --hands-L     # the split watcher                         -> SCORES-SPLIT-HANDS-L.json
python3 score_haiku.py               # Haiku markets                             -> SCORES-HAIKU.json
python3 score_temp.py                # temperature-1 re-reads, DeepSeek          -> SCORES-TEMP.json
python3 score_temp_haiku.py          # temperature-1 re-reads, Haiku             -> SCORES-TEMP-HAIKU.json
python3 draw_paper2_models_2026-10-25.py
```

The scorers overwrite the `SCORES-*.json` files in `runs/money/saydo-watch/`; the committed copies are the ones the paper cites.

Running markets or watchers calls OpenRouter. The scripts read the key from a `.secrets/openrouter.key` file three folders above `slope/` (`os.path.join(<slope>, "..", "..", "..", ".secrets", "openrouter.key")`, in `game.py`, `watch_run.py`, `board_label.py` and the `run*.sh` launchers). Place your key there, or point those lines at your own. Example, one DeepSeek board market:

```
cd slope
D=deepseek/deepseek-v4.1-flash
python3 game.py --n 3 --alpha 3.2 --ceiling none --wording P1x --provider Together --a2 1 --money potchoice --netprofit 1 \
  --startcoins 38 --deposit 1 --costpublic 1 --memshop 1 --pledge 1 --pledgehalf 1 --rounds 100 --models $D,$D,$D \
  --board free --decouple 1 --talknote plain --boardk 5 --nonum 1 --costs 0.7,1,1 --rep 1 --out runs/my-TP0-rep1.jsonl
```

Markets are repeats, not replays: sellers run at temperature 1 with no seed. Watchers run at temperature 0, one sample, except the temperature-1 re-reads.

## Authors

Marion Nowicki and Cael. Apart Research AI Collusion Research Sprint, October 2026.

## Licence

Code (`*.py`, `*.sh`): MIT, see `LICENSE`. The paper, the figures, the pre-registrations, results and run files: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), free to share and adapt with credit to the authors.
