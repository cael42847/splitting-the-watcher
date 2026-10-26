#!/usr/bin/env python3
"""run_temp.py — PREREG-TEMPERATURE-2026-10-25.md: the chain that carries Paper 2, re-read at temperature 1, two samples per market.
Her idea (25 Oct 15:2x: "we should have done the test with the temperature 1"); the hands' four changes (hands-log 15:35:28).

Per market and per sample s (1, 2), at temperature T (default 1):
  W1   the first watcher, watch_run.WATCHER on the full report (unchanged prompt), DeepSeek v4.1 flash, Together pinned
  W9   watch_run_ruler.W9_PROMPT on the ruler block + stripped record, reading THIS sample's W1 answer (reasoning removed)
  W9f  (the hands' change 4) the same W9 prompt reading the FROZEN temperature-0 W1 answer (out/), so W9's own noise is
       separate from the noise it inherits
  L    the board reader (board_label.READER + RETRY, GPT-5.1), talk cells only, quotes checked by board_label.check_quotes
Prompts are imported, never edited; their hashes are printed at start and stored. Retries (parse / quote failures) are kept
under 'tries' as before; a SAMPLE is a separate, independent read. max_tokens as at temperature 0 (4000 / 1500).
Output: runs/money/saydo-watch/temp/T<T>-s<s>/<cell>/<run>.json   (.partial.json if any part never parsed)

Usage (from slope/): python3 run_temp.py --sample S [--temp 1] [--cell C] [--limit N] [--src-reports DIR] [--watch DIR] [--src RUN_DIR] [--out DIR]
"""
import json, os, sys, glob, argparse, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from watch_run import WATCHER, parse, rounds_text, balance, h, DS, KEY
from watch_run_prices import strip
from watch_run_ruler import W9_PROMPT, HASHES_W9, ruler_block, costs_of
import board_label as BL

def ask(messages, model, T, max_tokens):
    req = {"model": model, "temperature": T, "max_tokens": max_tokens, "messages": messages}
    if "deepseek" in model:
        req["provider"] = {"order": ["Together"], "allow_fallbacks": False}; req["reasoning"] = {"enabled": False}
    body = json.dumps(req).encode(); err = ""
    for attempt in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", body,
                {"Content-Type": "application/json", "Authorization": "Bearer " + KEY}), timeout=300)
            j = json.load(r); return j["choices"][0]["message"]["content"] or "", j.get("provider", "?"), j.get("usage", {})
        except Exception as e:
            err = str(e); time.sleep(5 * (attempt + 1))
    return "ERROR " + err, "?", {}

def call_watch(prompt, T):   # up to 2 retries on a parse failure, every try kept (as at temperature 0)
    tries = []
    for _ in range(3):
        raw, prov, u = ask([{"role": "user", "content": prompt}], DS, T, 4000); tries.append({"raw": raw, "provider": prov, "usage": u})
        pz = parse(raw)
        if pz is not None: return {"raw": raw, "parsed": pz, "provider": prov, "usage": u, "tries": len(tries), "all_tries": tries}
    return {"raw": tries[-1]["raw"], "parsed": None, "tries": len(tries), "all_tries": tries}

def call_reader(report_text, T):   # board_label.label at temperature T: same prompt, same retry-with-reason, same quote check
    posts, board = BL.board_of(report_text)
    msgs = [{"role": "user", "content": BL.READER.format(BOARD=board)}]; tries = []
    for _ in range(3):
        raw, prov, u = ask(msgs, BL.MODEL, T, 1500); j = BL.parse(raw); ok, why = (BL.check_quotes(j, posts) if j else (False, "no JSON"))
        tries.append({"raw": raw, "provider": prov, "usage": u, "quote_check": why})
        if j and ok: return {"parsed": j, "quote_check": why, "tries": len(tries), "all_tries": tries}
        msgs = msgs + [{"role": "assistant", "content": raw}, {"role": "user", "content": BL.RETRY.format(WHY=why)}]
    return {"parsed": None, "quote_check": tries[-1]["quote_check"], "tries": len(tries), "all_tries": tries}

HASHES = {"WATCHER": h(WATCHER), "W9": HASHES_W9["W9"], "W9_PROMPT": HASHES_W9["W9_PROMPT"], "READER": BL.HASHES["READER"], "RETRY": BL.HASHES["RETRY"]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, required=True); ap.add_argument("--temp", type=float, default=1.0)
    ap.add_argument("--cell", default="*"); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--watch", default="runs/money/saydo-watch"); ap.add_argument("--src", default="runs/money/saydo")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(a.watch, "temp", f"T{a.temp:g}-s{a.sample}")
    print("prompt hashes:", json.dumps(HASHES), "| temperature", a.temp, "| sample", a.sample, "| out", out, flush=True)
    done = 0
    for rp in sorted(glob.glob(os.path.join(a.watch, "reports", a.cell, "*.report.txt"))):
        cell = rp.split("/")[-2]; name = os.path.basename(rp).replace(".report.txt", "")
        frozen = os.path.join(a.watch, "out", cell, name + ".watch.json")
        if not os.path.exists(frozen): continue   # only the markets that have a temperature-0 W1 (the 104)
        od = os.path.join(out, cell); os.makedirs(od, exist_ok=True); outp = os.path.join(od, name + ".json")
        if os.path.exists(outp): continue
        if a.limit and done >= a.limit: break
        if done % 10 == 0:
            bal = balance(); print(f"{time.strftime('%H:%M:%S')} balance {bal:.2f} at run {done}", flush=True)
            if bal < 15: print("STOP: balance under 15"); return
        report = open(rp).read(); truth = json.load(open(rp.replace(".report.txt", ".truth.json"))); R = rounds_text(truth)
        C, _ = costs_of(a.src, name); rec_w9 = ruler_block(C) + "\n\n" + strip(report)
        rec = {"run": name, "cell": cell, "temperature": a.temp, "sample": a.sample, "hashes": HASHES}
        rec["W1"] = call_watch(WATCHER.format(ROUNDS=R, REPORT=report), a.temp)
        w1 = rec["W1"]["parsed"]
        if w1 is not None:
            rec["W9"] = call_watch(W9_PROMPT.format(ROUNDS=R, FIRST=json.dumps({k: v for k, v in w1.items() if k != "reasoning"}), REPORT=rec_w9), a.temp)
        w1f = json.load(open(frozen))["W1"]["parsed"]
        rec["W9f"] = call_watch(W9_PROMPT.format(ROUNDS=R, FIRST=json.dumps({k: v for k, v in w1f.items() if k != "reasoning"}), REPORT=rec_w9), a.temp)
        if cell in BL.TALK or cell == "DEV": rec["L"] = call_reader(report, a.temp)
        need = ["W1", "W9", "W9f"] + (["L"] if "L" in rec else [])
        ok = all((rec.get(k) or {}).get("parsed") is not None for k in need)
        json.dump(rec, open(outp if ok else outp.replace(".json", ".partial.json"), "w"), indent=1); done += 1
        print(name, *(f"{k} {'ok' if (rec.get(k) or {}).get('parsed') is not None else 'FAIL'}" for k in need), flush=True)

if __name__ == "__main__": main()
