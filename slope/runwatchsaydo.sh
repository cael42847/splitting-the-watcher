#!/bin/zsh
# Paper 2 watchers on the 105 test runs (PREREG-SAY-DO-MARKET-B-2026-10-24.md, frozen a579fc2a + fixes 362c7058; the hands' GO 19:4x).
# Waits for the market batch to finish, builds every report, then runs the three arms, one process per cell (uniform: every arm reads all 105).
cd "$(dirname "$0")"
until grep -q "saydo batch done" runs/saydo-launch.log; do sleep 30; done
echo "== $(date +%H:%M:%S) markets done; building reports"
W=runs/money/saydo-watch
for c in TP0 TP1 SP0 SP1 TW0; do
  mkdir -p $W/reports/$c $W/out/$c
  for f in runs/money/saydo/SAY-$c-rep*.jsonl; do python3 watch_report.py $f $W/reports/$c >> $W/build.log 2>&1; done
done
echo "== $(date +%H:%M:%S) $(ls $W/reports/*/*.report.txt | wc -l) reports built; watchers start"
for c in TP0 TP1 SP0 SP1 TW0; do python3 watch_run.py $W/reports/$c $W/out/$c > $W/run-$c.log 2>&1 & sleep 2; done
wait
echo "== $(date +%H:%M:%S) watchers done: $(ls $W/out/*/*.watch.json 2>/dev/null | wc -l) complete, $(ls $W/out/*/*.partial.json 2>/dev/null | wc -l) partial"
