#!/bin/zsh
# Paper 2 sprint cells — PREREG-MARKET-B-SPRINT-2026-10-23.md
cd "$(dirname "$0")"
D=deepseek/deepseek-v4.1-flash
B=(--n 3 --alpha 3.2 --ceiling none --wording P1x --board free --decouple 1 --talknote plain --provider Together --a2 1 --boardk 5 --money potchoice --netprofit 1 --startcoins 38 --deposit 1 --nonum 1 --costpublic 1 --memshop 1 --pledge 1 --pledgehalf 1 --rounds 30 --models $D,$D,$D)
ROT=("0.7,1,1" "1,0.7,1" "1,1,0.7"); ROT2=("0.7,0.7,1" "0.7,1,0.7" "1,0.7,0.7")
mkdir -p runs/money/sprint; date +%H:%M:%S
for r in $(seq 1 10); do
  c=${ROT[$(( (r-1)%3+1 ))]}; c2=${ROT2[$(( (r-1)%3+1 ))]}
  python3 game.py $B --costs $c --rep $r --out runs/money/sprint/MB-base-rep$r.jsonl >/dev/null 2>&1 & sleep 1
  python3 game.py $B --costs $c --probe-rounds 8,15,22 --probe-pct 10 --rep $r --out runs/money/sprint/MB-patrol-rep$r.jsonl >/dev/null 2>&1 & sleep 1
  python3 game.py $B --costs $c2 --rep $r --out runs/money/sprint/MB-twocheap-rep$r.jsonl >/dev/null 2>&1 & sleep 1
done
for r in $(seq 7 20); do
  c=${ROT[$(( (r-1)%3+1 ))]}
  python3 game.py $B --costs $c --offer 1 --rep $r --out runs/money/map/ds-E-rep$r.jsonl >/dev/null 2>&1 & sleep 1
done
wait; date +%H:%M:%S; echo "marketb batch done"
