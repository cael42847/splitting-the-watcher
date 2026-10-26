#!/bin/zsh
# Launch: zsh slope/runsaydo_haiku_w2.sh > slope/runs/saydo-haiku-w2-launch.log 2>&1 &
# WAVE 2 (amendment C): the rest of the full Haiku design, decided on cost only before any result: board reps 10-30 (TH0, TH1),
# silent reps 4-12 (SH0, SH1). Every flag is runsaydo.sh's ($B + $TALK / $SILENT + $PATROL); only --models changes. Three waves, balance read before each.
cd "$(dirname "$0")"
H=anthropic/claude-haiku-5.5
B=(--n 3 --alpha 3.2 --ceiling none --wording P1x --provider Together --a2 1 --money potchoice --netprofit 1 --startcoins 38 --deposit 1 --costpublic 1 --memshop 1 --pledge 1 --pledgehalf 1 --rounds 100 --models $H,$H,$H)
TALK=(--board free --decouple 1 --talknote plain --boardk 5 --nonum 1)
SILENT=(--board none --decouple 0)
PATROL=(--probe-rounds 20,40,60,80 --probe-pct 10)
ROT=("0.7,1,1" "1,0.7,1" "1,1,0.7")
OUT=runs/money/saydo; mkdir -p $OUT
balance() { curl -s https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $(cat ../../../.secrets/openrouter.key)" | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(round(d['total_credits']-d['total_usage'],2))"; }
BW=("10 11 12 13 14 15 16" "17 18 19 20 21 22 23" "24 25 26 27 28 29 30")
SW=("4 5 6" "7 8 9" "10 11 12")
for i in 1 2 3; do
  b=$(balance); echo "== $(date +%H:%M:%S) balance $b, board reps: ${BW[$i]}, silent reps: ${SW[$i]}"
  [[ -z $b ]] && { echo "STOP: no balance read"; exit 1; }
  if (( $(echo "$b < 20" | bc -l) )); then echo "STOP: balance under 20"; exit 0; fi
  for r in ${=BW[$i]}; do c=${ROT[$(( (r-1)%3+1 ))]}
    python3 game.py $B $TALK         --costs $c --rep $r --out $OUT/SAY-TH0-rep$r.jsonl >/dev/null 2>&1 & sleep 1
    python3 game.py $B $TALK $PATROL --costs $c --rep $r --out $OUT/SAY-TH1-rep$r.jsonl >/dev/null 2>&1 & sleep 1
  done
  for r in ${=SW[$i]}; do c=${ROT[$(( (r-1)%3+1 ))]}
    python3 game.py $B $SILENT         --costs $c --rep $r --out $OUT/SAY-SH0-rep$r.jsonl >/dev/null 2>&1 & sleep 1
    python3 game.py $B $SILENT $PATROL --costs $c --rep $r --out $OUT/SAY-SH1-rep$r.jsonl >/dev/null 2>&1 & sleep 1
  done
  wait
done
echo "== $(date +%H:%M:%S) balance $(balance); haiku wave 2 done"
