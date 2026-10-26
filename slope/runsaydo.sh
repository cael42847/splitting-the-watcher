#!/bin/zsh
# Launch: zsh slope/runsaydo.sh > slope/runs/saydo-launch.log 2>&1 &
# Paper 2, say and do — PREREG-SAY-DO-MARKET-B-2026-10-24.md (v4): 2x2 board x patrol + the watched-talk cell in Market B, 21 runs per cell (105), four waves, balance checked between waves.
cd "$(dirname "$0")"
D=deepseek/deepseek-v4.1-flash
B=(--n 3 --alpha 3.2 --ceiling none --wording P1x --provider Together --a2 1 --money potchoice --netprofit 1 --startcoins 38 --deposit 1 --costpublic 1 --memshop 1 --pledge 1 --pledgehalf 1 --rounds 100 --models $D,$D,$D)
TALK=(--board free --decouple 1 --talknote plain --boardk 5 --nonum 1)
SILENT=(--board none --decouple 0)
PATROL=(--probe-rounds 20,40,60,80 --probe-pct 10)
ROT=("0.7,1,1" "1,0.7,1" "1,1,0.7")
OUT=runs/money/saydo; mkdir -p $OUT
balance() { curl -s https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $(cat ../../../.secrets/openrouter.key)" | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(round(d['total_credits']-d['total_usage'],2))"; }
WAVES=("1 2 3 4 5 6" "7 8 9 10 11" "12 13 14 15 16" "17 18 19 20 21")
for w in $WAVES; do
  b=$(balance); echo "== $(date +%H:%M:%S) balance $b, wave reps: $w"
  [[ -z $b ]] && { echo "STOP: no balance read"; exit 1; }
  if (( $(echo "$b < 20" | bc -l) )); then echo "STOP: balance under 20"; exit 0; fi
  for r in ${=w}; do
    c=${ROT[$(( (r-1)%3+1 ))]}
    python3 game.py $B $TALK   --costs $c --rep $r --out $OUT/SAY-TP0-rep$r.jsonl >/dev/null 2>&1 & sleep 1
    python3 game.py $B $TALK   $PATROL --costs $c --rep $r --out $OUT/SAY-TP1-rep$r.jsonl >/dev/null 2>&1 & sleep 1
    python3 game.py $B $SILENT --costs $c --rep $r --out $OUT/SAY-SP0-rep$r.jsonl >/dev/null 2>&1 & sleep 1
    python3 game.py $B $SILENT $PATROL --costs $c --rep $r --out $OUT/SAY-SP1-rep$r.jsonl >/dev/null 2>&1 & sleep 1
    python3 game.py $B $TALK --monitor 1 --costs $c --rep $r --out $OUT/SAY-TW0-rep$r.jsonl >/dev/null 2>&1 & sleep 1
  done
  wait
done
echo "== $(date +%H:%M:%S) balance $(balance); saydo batch done"
