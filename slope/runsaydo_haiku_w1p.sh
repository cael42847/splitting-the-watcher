#!/bin/zsh
# Launch: zsh slope/runsaydo_haiku_w1p.sh > slope/runs/saydo-haiku-launch.log 2>&1 &
# Paper 2, PREREG-HAIKU-BOARD-2026-10-25.md: Paper 2's board cell (TP0) and silent cell (SP0) exactly, with Claude Haiku 5.5 in all three seats.
# WAVE 1P (amendment B): the patrol half, 9 board + patrol (TH1 reps 1-9) + 3 silent + patrol (SH1 reps 1-3), PATROL exactly as runsaydo.sh. Every flag is runsaydo.sh's ($B + $TALK); only --models changes. One wave (board reps 1-9, silent reps 1-3), the cheap seat rotating as in runsaydo.sh, balance read before it.
cd "$(dirname "$0")"
H=anthropic/claude-haiku-5.5
B=(--n 3 --alpha 3.2 --ceiling none --wording P1x --provider Together --a2 1 --money potchoice --netprofit 1 --startcoins 38 --deposit 1 --costpublic 1 --memshop 1 --pledge 1 --pledgehalf 1 --rounds 100 --models $H,$H,$H)
TALK=(--board free --decouple 1 --talknote plain --boardk 5 --nonum 1)
SILENT=(--board none --decouple 0)
PATROL=(--probe-rounds 20,40,60,80 --probe-pct 10)
ROT=("0.7,1,1" "1,0.7,1" "1,1,0.7")
OUT=runs/money/saydo; mkdir -p $OUT
balance() { curl -s https://openrouter.ai/api/v1/credits -H "Authorization: Bearer $(cat ../../../.secrets/openrouter.key)" | python3 -c "import json,sys; d=json.load(sys.stdin)['data']; print(round(d['total_credits']-d['total_usage'],2))"; }
WAVES=("1 2 3 4 5 6 7 8 9")
for w in $WAVES; do
  b=$(balance); echo "== $(date +%H:%M:%S) balance $b, wave reps: $w"
  [[ -z $b ]] && { echo "STOP: no balance read"; exit 1; }
  if (( $(echo "$b < 20" | bc -l) )); then echo "STOP: balance under 20"; exit 0; fi
  for r in ${=w}; do
    c=${ROT[$(( (r-1)%3+1 ))]}
    python3 game.py $B $TALK $PATROL --costs $c --rep $r --out $OUT/SAY-TH1-rep$r.jsonl >/dev/null 2>&1 & sleep 1
    (( r <= 3 )) && { python3 game.py $B $SILENT $PATROL --costs $c --rep $r --out $OUT/SAY-SH1-rep$r.jsonl >/dev/null 2>&1 & sleep 1 }
  done
  wait
done
echo "== $(date +%H:%M:%S) balance $(balance); haiku board batch done"
