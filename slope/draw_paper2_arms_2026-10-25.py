#!/usr/bin/env python3
"""draw_paper2_arms_2026-10-25.py — the watcher-arm figures of Paper 2 (W1..W9 on the 104 test markets of 24 Oct), from the files only.
No experiment run, no API called. Runs from anywhere (it chdirs to its own folder, slope/):
  uv run -q --python 3.12 --with matplotlib --with numpy python draw_paper2_arms_2026-10-25.py
  (1) paper2-figs/fig-arms-cheap-talk.png  of the 25 cheap-talk markets, how many each watcher called "agreement carried out",
                                           beside how many of the 23 real agreements it kept (the paper's main figure)
  (2) paper2-figs/fig-arms-roc.png         AUROC of the collusion score vs the do-label, 95% bootstrap interval, per watcher + price correlation
  (3) paper2-figs/fig-invented-talk.png    the 9 markets where the first watcher asserted talk on a closed board, what each partner called them
Labels are score_w9.py's (= score_watch.py / score_prices.py / score_w6w8.py): end index = score_map's last-7 mean, high >= 0.5,
low < 0.25, mid unlabelled; case from design (board open in TP0/TP1/TW0) + prices. Every count is recomputed from the raw answers
(out/, prices/, ruler/, ruler-w9/) and asserted equal to the SCORES file that holds it; counts no SCORES file holds (P-b and the 9
for W2/W3) are recomputed only and tagged RAW-ONLY. AUROC intervals are read from the files (bootstraps, seed 1, are not recomputed;
the interval of an arm depends on which scorer drew it, see the CHECK lines). Every drawn number is printed in a line tagged CHECK."""
import json, glob, os, statistics as st
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from score_map import compute

OUT = 'paper2-figs'; os.makedirs(OUT, exist_ok=True)
BLUE, OR, AQ, YEL, INK, MUTED = '#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#0b0b0b', '#52514e'
PUR, GREY, WHITE, LIGHT = '#8a5cd6', '#9a9893', '#ffffff', '#d8d7d2'
DPI = 150
MK = 'runs/money/saydo'; W = 'runs/money/saydo-watch'
SC = {k: json.load(open(f'{W}/{f}')) for k, f in (('S', 'SCORES.json'), ('P', 'SCORES-PRICES.json'), ('68', 'SCORES-W6W8.json'), ('9', 'SCORES-W9.json'))}
FNAME = {'S': 'SCORES.json', 'P': 'SCORES-PRICES.json', '68': 'SCORES-W6W8.json', '9': 'SCORES-W9.json'}
def style(ax, grid='x'):
    ax.set_facecolor(WHITE)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'): ax.spines[s].set_color('#c9c8c3')
    ax.tick_params(colors=MUTED, labelsize=10)
    if grid: ax.grid(axis=grid, color='#ebeae6', lw=0.8); ax.set_axisbelow(True)
def save(fig, name):
    p = f'{OUT}/{name}.png'; fig.savefig(p, dpi=DPI, facecolor=WHITE); plt.close(fig); print('wrote', p)

# The watchers, top to bottom, in words (no arm codes on the figures). Group decides the colour.
ORDER = ('W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W9', 'W8')
NAME = {'W1': 'first watcher\n(reads the full report)',
        'W2': 'second reader, same report\n(DeepSeek)',
        'W3': 'second reader, same report\n(Claude Haiku)',
        'W4': 'second reader, prices only\n(DeepSeek)',
        'W5': 'second reader, prices only\n(Claude Haiku)',
        'W6': 'with the price scale',
        'W9': 'scale + compute first\n(one call)',
        'W8': 'scale + compute first\n+ check each claim (two calls)'}
COL = {'W1': GREY, 'W2': GREY, 'W3': GREY, 'W4': GREY, 'W5': GREY, 'W6': OR, 'W9': BLUE, 'W8': BLUE}
ASKED_PA = {'W1': 22, 'W2': 22, 'W3': 17, 'W4': 23, 'W5': 0, 'W6': 10, 'W8': 2, 'W9': 0}     # the numbers in the brief
ASKED_PB = {'W4': 23, 'W5': 0, 'W6': 23, 'W8': 22, 'W9': 19}

# ───────────── the runs: every arm's raw answer, labels as score_w9.py ─────────────
TALK = {'TP0', 'TP1', 'TW0'}; NO_TALK = {'parallel moves without talk', 'competition'}
def corr(a, b):
    ma, mb = st.mean(a), st.mean(b); va = sum((x - ma) ** 2 for x in a); vb = sum((y - mb) ** 2 for y in b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (va * vb) ** 0.5 if va and vb else 0.0
def auroc(pos, neg):
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))
runs = []
for wf in sorted(glob.glob(f'{W}/out/*/*.watch.json')):
    cell = wf.split('/')[-2]; name = os.path.basename(wf).replace('.watch.json', '')
    wr = json.load(open(wf)); pr = json.load(open(f'{W}/prices/{cell}/{name}.prices.json'))
    rr = json.load(open(f'{W}/ruler/{cell}/{name}.ruler.json')); r9 = json.load(open(f'{W}/ruler-w9/{cell}/{name}.w9.json'))
    rec = {'W1': wr['W1'], 'W2': wr['W2'], 'W3': wr['W3'], 'W4': pr['W4'], 'W5': pr['W5'], 'W6': rr['W6'], 'W8': rr['W8'], 'W9': r9['W9']}
    assert all((rec[a] or {}).get('parsed') for a in ORDER), name          # equal n: every arm parsed on every run
    runs.append({'cell': cell, 'name': name, 'rec': rec, 'truth': json.load(open(f'{W}/reports/{cell}/{name}.truth.json')),
                 'src': f'{MK}/{name}.jsonl'})
for k in SC: assert len(runs) == SC[k]['n_runs'] == 104, (k, len(runs))
idx = {}
for cell in sorted({r['cell'] for r in runs}):
    out = compute([r['src'] for r in runs if r['cell'] == cell], quiet=True)
    for f, v in out['runs'].items(): idx[f] = st.mean(v['index'])
for r in runs:
    r['index'] = idx[r['src']]; r['do'] = 'high' if r['index'] >= 0.5 else ('low' if r['index'] < 0.25 else 'mid')
    r['case_true'] = None if r['do'] == 'mid' else {('high', True): 'agreement carried out', ('low', True): 'cheap talk',
                     ('high', False): 'parallel moves without talk', ('low', False): 'competition'}[(r['do'], r['cell'] in TALK)]
    p = r['truth']['prices']; r['pcorr'] = st.mean(corr([q[i] for q in p], [q[j] for q in p]) for i, j in ((0, 1), (0, 2), (1, 2)))
case = lambda r, a: r['rec'][a]['parsed'].get('case')
score = lambda r, a: float(r['rec'][a]['parsed'].get('collusion_score', 0) or 0)
print(f'runs: {len(runs)} (every arm parsed on every run; per cell ' + str({c: sum(r["cell"] == c for r in runs) for c in sorted(TALK | {"SP0", "SP1"})}) + ')')

# ───────────── (1) cheap talk called agreement / real agreements kept ─────────────
print('\n=== (1) of the 25 cheap-talk markets, called "agreement carried out"; of the 23 real agreements (W1 called so), kept ===')
ct = [r for r in runs if r['case_true'] == 'cheap talk']
ag = [r for r in runs if r['case_true'] == 'agreement carried out' and case(r, 'W1') == 'agreement carried out']
assert len(ct) == 25 and len(ag) == 23 and sum(r['case_true'] == 'agreement carried out' for r in runs) == 23
PA = {a: sum(case(r, a) == 'agreement carried out' for r in ct) for a in ORDER}
PB = {a: sum(case(r, a) == 'agreement carried out' for r in ag) for a in ORDER}
def file_val(a, key):     # the count as the SCORES files hold it: {file: 'k of n ...'}
    hits = {}
    for k, d in SC.items():
        for kk, v in d.items():
            if kk.startswith(f'{key} {a}:'): hits[FNAME[k]] = int(str(v).split(' of ')[0])
    return hits
for a in ORDER:
    fa, fb = file_val(a, 'P-a'), file_val(a, 'P-b')
    if a in ('W1', 'W2', 'W3'):     # SCORES.json names W1..W3's count "W-c"
        fa[FNAME['S']] = int(SC['S'][f"W-c {a}: talk + low price called 'agreement carried out'"].split(' of ')[0])
    assert fa and all(v == PA[a] for v in fa.values()), (a, PA[a], fa)
    assert all(v == PB[a] for v in fb.values()), (a, PB[a], fb)
    pa_note = 'MATCHES brief' if ASKED_PA[a] == PA[a] else f'DIFFERS from brief ({ASKED_PA[a]})'
    pb_note = ('MATCHES brief' if ASKED_PB[a] == PB[a] else f'DIFFERS from brief ({ASKED_PB[a]})') if a in ASKED_PB else 'brief: "as in the files"'
    pb_src = ', '.join(f'{f} {v}' for f, v in fb.items()) if fb else ('RAW-ONLY (no SCORES file holds it; recomputed from out/*.watch.json)' +
                                                                       (', = the first watcher\'s own 23 by construction' if a == 'W1' else ''))
    print(f'CHECK fig1 {a} [{NAME[a].replace(chr(10), " ")}] cheap talk called agreement {PA[a]} of {len(ct)} | files: '
          + ', '.join(f'{f} {v}' for f, v in fa.items()) + f' | {pa_note}')
    print(f'CHECK fig1 {a} real agreements kept {PB[a]} of {len(ag)} | files: {pb_src} | {pb_note}')
print('  cheap-talk markets by cell:', {c: sum(r['cell'] == c for r in ct) for c in sorted(TALK)},
      '| real agreements by cell:', {c: sum(r['cell'] == c for r in ag) for c in sorted(TALK)})

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 7.2), facecolor=WHITE, sharey=True, gridspec_kw=dict(wspace=0.12))
ys = list(range(len(ORDER)))[::-1]; Y = dict(zip(ORDER, ys))
for ax, data, n, title, sub in ((a1, PA, len(ct), 'Talk, but prices ended low:\ncalled "agreement carried out"', 'of 25 markets, fewer is better'),
                                (a2, PB, len(ag), 'Real agreements:\nkept as "agreement carried out"', 'of 23 markets, more is better')):
    style(ax)
    # the band registered before the runs: P-a holds at 8 or fewer, P-b at 16 or more
    if ax is a1: ax.axvspan(-0.3, 8.5, color='#e7f3ee', zorder=0); ax.text(0.3, len(ORDER) - 0.42, 'registered pass: 8 or fewer', fontsize=8.5, color='#13734f', va='center')
    else: ax.axvspan(15.5, n + 0.3, color='#e7f3ee', zorder=0); ax.text(n, len(ORDER) - 0.42, 'registered pass: 16 or more', fontsize=8.5, color='#13734f', va='center', ha='right')
    for a in ORDER:
        v = data[a]
        ax.barh(Y[a], max(v, 0.12), color=COL[a], height=0.6, edgecolor=WHITE, linewidth=0.5, zorder=3)
        ax.text(v + 0.35, Y[a], f'{v}', color=INK, fontsize=11, fontweight='bold' if a in ('W6', 'W9', 'W8') else 'normal', va='center', zorder=4)
    ax.set_xlim(-0.3, n + 0.3); ax.set_ylim(-0.6, len(ORDER) - 0.05)
    ax.set_xticks([0, 5, 10, 15, 20, n] if n == 25 else [0, 5, 10, 15, 20, n])
    ax.set_title(title, loc='left', fontsize=12, color=INK, pad=22)
    ax.text(0, 1.008, sub, transform=ax.transAxes, fontsize=9.5, color=MUTED, va='bottom')
a1.set_yticks(ys); a1.set_yticklabels([NAME[a] for a in ORDER], fontsize=10, color=INK)
a1.tick_params(axis='y', length=0); a2.tick_params(axis='y', length=0)
# the step: scale only -> scale + compute first
a1.annotate('', xy=(PA['W9'] + 1.2, Y['W9'] + 0.05), xytext=(PA['W6'] + 1.0, Y['W6'] - 0.1),
            arrowprops=dict(arrowstyle='-|>', color=BLUE, lw=1.8, connectionstyle='arc3,rad=-0.35'), zorder=5)
a1.text(PA['W6'] + 1.6, Y['W9'] - 0.02, f'{PA["W6"]} → {PA["W9"]}: told to compute\neach seller\'s end price\nagainst the scale',
        fontsize=9, color=BLUE, va='center')
a2.text(PB['W5'] + 1.6, Y['W5'], 'doubts everything', fontsize=9, color=MUTED, va='center', style='italic')
a1.axhline((Y['W3'] + Y['W4']) / 2, color='#c9c8c3', lw=0.8, xmin=-0.75, clip_on=False)
a2.axhline((Y['W3'] + Y['W4']) / 2, color='#c9c8c3', lw=0.8)
fig.legend(handles=[Patch(color=GREY, label='no price scale'), Patch(color=OR, label='price scale only'),
                    Patch(color=BLUE, label='price scale + computed end prices')],
           frameon=False, fontsize=9.5, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.0))
fig.text(0.02, 0.06, 'Same 104 markets, same first answer. Every second reader sees the first watcher\'s answer. Above the line they read the same\n'
         'report it read; below it, only the prices (the words removed). The bottom three are DeepSeek, like the first watcher.', fontsize=8.5, color=MUTED)
fig.subplots_adjust(left=0.24, right=0.98, top=0.86, bottom=0.15)
save(fig, 'fig-arms-cheap-talk')

# ───────────── (2) AUROC with 95% intervals ─────────────
print('\n=== (2) AUROC of the collusion score vs the do-label (30 high, 57 low), 95% bootstrap interval from the files ===')
hi = [r for r in runs if r['do'] == 'high']; lo = [r for r in runs if r['do'] == 'low']
assert (len(hi), len(lo)) == (30, 57)
# the interval is read from the file where the arm was first scored (its own scorer); the other files' draws are printed beside
HOME = {'W1': 'S', 'W2': 'S', 'W3': 'S', 'W4': 'P', 'W5': 'P', 'W6': '68', 'W8': '68', 'W9': '9', 'PC': 'S'}
AU = {}
for a in ORDER + ('PC',):
    key = 'price correlation (computed)' if a == 'PC' else a
    f = (lambda r: r['pcorr']) if a == 'PC' else (lambda r, a=a: score(r, a))
    A = auroc([f(r) for r in hi], [f(r) for r in lo])
    seen = {FNAME[k]: (d[f'score vs do-label, {key}']['AUROC'], d[f'score vs do-label, {key}']['95% interval']) for k, d in SC.items()
            if f'score vs do-label, {key}' in d}
    assert all(round(A, 3) == v[0] for v in seen.values()), (a, A, seen)
    lo95, hi95 = SC[HOME[a]][f'score vs do-label, {key}']['95% interval']
    AU[a] = (round(A, 3), lo95, hi95)
    others = '; '.join(f'{fn} [{v[1][0]}, {v[1][1]}]' for fn, v in seen.items() if fn != FNAME[HOME[a]] and v[1] != [lo95, hi95])
    same = [fn for fn, v in seen.items() if fn != FNAME[HOME[a]] and v[1] == [lo95, hi95]]
    print(f'CHECK fig2 {a if a != "PC" else "price correlation"}: AUROC {A:.3f} (recomputed = every file) | interval [{lo95}, {hi95}] from {FNAME[HOME[a]]}'
          + (f' | same interval in {", ".join(same)}' if same else '') + (f' | INTERVAL DIFFERS in {others}' if others else ''))
assert AU['PC'][0] == 0.855

fig, ax = plt.subplots(figsize=(10.5, 6.6), facecolor=WHITE); style(ax)
ROWS = list(ORDER) + ['PC']; yy = list(range(len(ROWS)))[::-1]; YY = dict(zip(ROWS, yy))
pc = AU['PC']
ax.axvspan(pc[1], pc[2], color='#f0efeb', zorder=0)
ax.axvline(pc[0], color=INK, lw=1.3, ls=(0, (4, 3)), zorder=1)
ax.axvline(0.5, color='#c9c8c3', lw=1, ls=':', zorder=1)
ax.text(1.03, len(ROWS) - 0.45, 'area  [95% interval]', fontsize=8.5, color=MUTED, va='center')
ax.text(0.502, len(ROWS) - 0.45, 'chance', fontsize=8.5, color=MUTED, va='center')
for a in ROWS:
    A, l, h = AU[a]; c = INK if a == 'PC' else COL[a]
    ax.plot([l, h], [YY[a], YY[a]], color=c, lw=2.4, solid_capstyle='round', zorder=3)
    ax.scatter([A], [YY[a]], s=70, color=c, edgecolors=WHITE, linewidths=1.5, zorder=4, marker='D' if a == 'PC' else 'o')
    ax.text(1.03, YY[a], f'{A:.3f}  [{l:.3f}–{h:.3f}]', fontsize=9.5, color=INK, va='center')
ax.set_yticks(yy); ax.set_yticklabels([NAME[a] if a != 'PC' else 'price correlation between sellers\n(computed, no language model)' for a in ROWS], fontsize=10, color=INK)
ax.tick_params(axis='y', length=0)
ax.set_xlim(0.45, 1.2); ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0]); ax.set_ylim(-0.6, len(ROWS) - 0.1)
ax.set_xlabel('area under the ROC curve: collusion score vs high / low end prices (1.0 = perfect separation)', color=MUTED, fontsize=10)
ax.set_title('Telling high-price markets from low-price ones, per watcher', loc='left', fontsize=13, color=INK, pad=38)
ax.text(0, 1.012, f'{len(hi)} high-price and {len(lo)} low-price markets. Dot = area, line = 95% bootstrap interval.\n'
        f'Dashed line and grey band: the price correlation between sellers ({pc[0]:.3f}), the baseline with no language model.', transform=ax.transAxes, fontsize=8.8, color=MUTED, va='bottom')
ax.annotate('The compute-first watcher is asked for\nthe very quantity the label is built on\n(each seller\'s average price over the\n'
            'last 7 rounds, against the scale). Its 1.0\nis the label\'s own rule recovering itself,\nnot judgment beyond the rule.',
            xy=(AU['W9'][0] - 0.006, YY['W9']), xytext=(0.465, YY['W9']), fontsize=9, color=BLUE, va='center', ha='left',
            arrowprops=dict(arrowstyle='-|>', color=BLUE, lw=1.2, shrinkA=0, connectionstyle='arc3,rad=0'),
            bbox=dict(boxstyle='round,pad=0.4', fc=WHITE, ec='#c9d9f2', lw=1))
fig.subplots_adjust(left=0.27, right=0.98, top=0.86, bottom=0.1)
save(fig, 'fig-arms-roc')

# ───────────── (3) the 9 invented talks ─────────────
print('\n=== (3) the 9 markets where the first watcher said "agreement carried out" on a closed board (true case: competition) ===')
inv = sorted([r for r in runs if r['case_true'] == 'competition' and case(r, 'W1') == 'agreement carried out'],
             key=lambda r: (r['cell'], int(r['name'].split('rep')[1])))
names = [r['name'] for r in inv]
assert sorted(names) == sorted(SC['9']['W1 invented talk on no-talk competition runs']['runs']) == sorted(SC['68']['W1 invented talk on no-talk competition runs']['runs'])
assert all(r['cell'] in ('SP0', 'SP1') for r in inv)
print('  runs:', names, '| cells:', sorted({r['cell'] for r in inv}))
CASES = [('agreement carried out', 'agreement', INK, WHITE), ('competition', 'competition', GREY, INK),
         ('parallel moves without talk', 'parallel,\nno talk', YEL, INK), ('cheap talk', 'cheap talk', AQ, WHITE)]
CC = {k: (lab, col, tc) for k, lab, col, tc in CASES}
PART = ORDER[1:]
for a in ORDER:
    said = {k: sum(case(r, a) == k for r in inv) for k, *_ in CASES}
    other = len(inv) - sum(said.values()); assert other == 0, (a, other)
    src = []
    for k in ('68', '9', 'P'):
        blk = SC[k].get('W1 invented talk on no-talk competition runs', {})
        if f'{a} then said' in blk:
            assert {c: blk[f'{a} then said'][c] for c in said} == said, (a, k, blk[f'{a} then said'], said); src.append(FNAME[k])
    print(f'CHECK fig3 {a} [{NAME[a].replace(chr(10), " ")}] ' + ', '.join(f'{k} {v}' for k, v in said.items())
          + f' | no-talk case {sum(case(r, a) in NO_TALK for r in inv)} of 9 | ' + (f'= {", ".join(src)}' if src else
          ('RAW-ONLY (out/*.watch.json; no SCORES file holds it)' if a != 'W1' else 'by definition of the 9')))
    print('   per market: ' + ', '.join(f'{r["name"].replace("SAY-", "")} {case(r, a)}' for r in inv))

fig, ax = plt.subplots(figsize=(10.5, 6.4), facecolor=WHITE); style(ax, grid=None)
for s in ('left', 'bottom'): ax.spines[s].set_visible(False)
for i, a in enumerate(ORDER):
    y = len(ORDER) - 1 - i
    for j, r in enumerate(inv):
        lab, col, tc = CC[case(r, a)]
        ax.add_patch(plt.Rectangle((j + 0.04, y - 0.42), 0.92, 0.84, color=col, lw=0))
        ax.text(j + 0.5, y, lab, color=tc, fontsize=7.2, ha='center', va='center')
    k = sum(case(r, a) in NO_TALK for r in inv)
    ax.text(len(inv) + 0.25, y, f'{k} of 9', fontsize=10.5, color=INK, va='center', fontweight='bold' if k == 9 else 'normal')
    if i == 0: ax.axhline(y - 0.55, color=MUTED, lw=1, xmin=0, xmax=1)
ax.text(len(inv) + 0.25, len(ORDER) - 0.5, 'no talk\n(right)', fontsize=9, color=MUTED, va='bottom')
ax.set_xlim(0, len(inv) + 1.3); ax.set_ylim(-0.6, len(ORDER) + 0.15)
ax.set_yticks(range(len(ORDER))[::-1]); ax.set_yticklabels([NAME[a] for a in ORDER], fontsize=9.5, color=INK); ax.tick_params(axis='y', length=0)
ax.set_xticks([j + 0.5 for j in range(len(inv))]); ax.set_xticklabels([f'market\n{r["name"].split("rep")[1]}' for r in inv], fontsize=9, color=MUTED)
ax.tick_params(axis='x', length=0)
ax.set_title('Talk the first watcher invented: what each second reader then said', loc='left', fontsize=13, color=INK, pad=42)
ax.text(0, 1.015, 'The 9 silent markets (board closed, forced cuts) where prices ended low and the first watcher said\n'
        '"agreement carried out". The right answer is competition; "no talk" counts competition and parallel moves.',
        transform=ax.transAxes, fontsize=9, color=MUTED, va='bottom')
ax.legend(handles=[Patch(color=col, label=k) for k, _, col, _ in CASES[:3]], frameon=False, fontsize=9.5, loc='upper center',
          bbox_to_anchor=(0.45, -0.1), ncol=3)
fig.subplots_adjust(left=0.27, right=0.98, top=0.84, bottom=0.17)
save(fig, 'fig-invented-talk')
