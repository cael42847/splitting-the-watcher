#!/bin/zsh
# PREREG-PRICE-PARTNER-2026-10-25.md (frozen c3204b79 + the hands' all_tries fix), the hands' GO. One process per cell; W1 not re-run.
cd "$(dirname "$0")"
W=runs/money/saydo-watch
echo "== $(date +%H:%M:%S) price partner start"
for c in TP0 TP1 SP0 SP1 TW0; do python3 watch_run_prices.py $W $W/prices --cell $c > $W/prices-run-$c.log 2>&1 & sleep 1; done
wait
echo "== $(date +%H:%M:%S) price partner done: $(ls $W/prices/*/*.prices.json 2>/dev/null | wc -l) complete, $(ls $W/prices/*/*.partial.json 2>/dev/null | wc -l) partial"
