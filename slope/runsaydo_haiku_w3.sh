#!/bin/zsh
# Launch: zsh slope/runsaydo_haiku_w3.sh > slope/runs/saydo-haiku-w3-launch.log 2>&1 &
# WAVE 3 (amendment D): Haiku board + the monitor sentence (TW0 exactly: $TALK --monitor 1), no patrol, reps 1-30, three waves of 10.
cd "$(dirname "$0")"
H=anthropic/claude-haiku-5.5
B=(--n 3 --alpha 3.2 --ceiling none --wording P1x --provider Together --a2 1 --money potchoice --netprofit 1 --startcoins 38 --deposit 1 --costpublic 1 --memshop 1 --pledge 1 --pledgehalf 1 --rounds 100 --models $H,$H,$H)
TALK=(--board free --decouple 1 --talknote plain --boardk 5 --nonum 1)


ROT=("0.7,1,1" "1,0.7,1" "1,1,0.7")
OUT=runs/money/saydo; mkdir -p $OUT
balance() { curl -s https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $(cat ../../../.secrets/openrouter.key)" | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(round(d['total_credits']-d['total_usage'],2))"; }
BW=("1 2 3 4 5 6 7 8 9 10" "11 12 13 14 15 16 17 18 19 20" "21 22 23 24 25 26 27 28 29 30")
for i in 1 2 3; do
  b=$(balance); echo "== $(date +%H:%M:%S) balance $b, board reps: ${BW[$i]}, warned board"
  [[ -z $b ]] && { echo "STOP: no balance read"; exit 1; }
  if (( $(echo "$b < 20" | bc -l) )); then echo "STOP: balance under 20"; exit 0; fi
  for r in ${=BW[$i]}; do c=${ROT[$(( (r-1)%3+1 ))]}
    python3 game.py $B $TALK --monitor 1 --costs $c --rep $r --out $OUT/SAY-TWH0-rep$r.jsonl >/dev/null 2>&1 & sleep 1
  done
  wait
done
echo "== $(date +%H:%M:%S) balance $(balance); haiku warned-board wave done"
