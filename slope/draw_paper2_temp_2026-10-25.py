#!/usr/bin/env python3
"""draw_paper2_temp_2026-10-25.py — the trade-off at temperature 0 and in the two temperature-1 samples, from SCORES-INDEP,
SCORES-SPLIT and SCORES-TEMP only (registered L). No API. Runs from anywhere:
  uv run -q --python 3.12 --with matplotlib python draw_paper2_temp_2026-10-25.py   -> paper2-figs/fig-tradeoff-temp.png"""
import json, os, re
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
W = 'runs/money/saydo-watch'
I = json.load(open(f'{W}/SCORES-INDEP.json')); S = json.load(open(f'{W}/SCORES-SPLIT.json')); T = json.load(open(f'{W}/SCORES-TEMP.json'))
p1 = I['PART 1 — L, the written-agreement label']; p2 = I['PART 2 — W10, own scale, against the do-label']
def fr(s): m = re.match(r'(\d+) of (\d+)', s); return int(m.group(1)), int(m.group(2))
pts = {'first watcher': [], 'scale + compute first': [], 'the split': []}
k = fr(p2["P-a W1: cheap talk called 'agreement carried out'"])[0]; a, b = fr(p1['words flagged, W1']['recall on L=yes']); pts['first watcher'].append((k, 100*a/b, 'T0'))
k = fr(p2["P-a W9: cheap talk called 'agreement carried out'"])[0]; a, b = fr(p1['words flagged, W9']['recall on L=yes']); pts['scale + compute first'].append((k, 100*a/b, 'T0'))
sp = S['words from reader L']; k = fr(sp["cheap talk called 'agreement carried out'"])[0]; a, b = fr(sp['words reported on L=yes']); pts['the split'].append((k, 100*a/b, 'T0'))
for s in ('1', '2'):
    M = T[f'sample {s}, reader L (frozen, registered)']
    for name, key in (('first watcher', 'W1'), ('scale + compute first', 'W9'), ('the split', 'split')):
        k = fr(M[key]["cheap talk called 'agreement carried out'"])[0]; a, b = fr(M[key]['words on L=yes']); pts[name].append((k, 100*a/b, 'T1'))
acc = {'first watcher': [p2['case accuracy W1'], T['sample 1, reader L (frozen, registered)']['W1']['case accuracy'], T['sample 2, reader L (frozen, registered)']['W1']['case accuracy']],
       'scale + compute first': [p2['case accuracy W9'], T['sample 1, reader L (frozen, registered)']['W9']['case accuracy'], T['sample 2, reader L (frozen, registered)']['W9']['case accuracy']],
       'the split': [sp['case accuracy (87 labelled)'], T['sample 1, reader L (frozen, registered)']['split']['case accuracy'], T['sample 2, reader L (frozen, registered)']['split']['case accuracy']]}
COL = {'first watcher': '#0b0b0b', 'scale + compute first': '#2a78d6', 'the split': '#8a5cd6'}
fig, ax = plt.subplots(figsize=(8.6, 6.0)); ax.set_facecolor('#ffffff')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.grid(color='#ebeae6', lw=0.8); ax.set_axisbelow(True)
ax.scatter([0], [100], s=260, facecolor='none', edgecolor='#0b0b0b', lw=1.3, ls='--')
ax.annotate('where a good watcher would be', (0, 100), xytext=(-6, -26), textcoords='offset points', fontsize=9.5, style='italic')
for name, P in pts.items():
    c = COL[name]; xs = [p[0] for p in P]; ys = [p[1] for p in P]
    ax.plot(xs, ys, color=c, lw=1, alpha=0.4)
    ax.scatter(xs[:1], ys[:1], s=130, color=c, edgecolor='white', lw=1.2, zorder=3)
    ax.scatter(xs[1:], ys[1:], s=70, facecolor='white', edgecolor=c, lw=1.8, zorder=3)
    lab = f"{name}\ncases right: {fr(acc[name][0])[0]} at T=0, {fr(acc[name][1])[0]} and {fr(acc[name][2])[0]} at T=1"
    off = {'first watcher': (-210, -40), 'scale + compute first': (14, -8), 'the split': (16, 4)}[name]
    ax.annotate(lab, (xs[0], ys[0]), xytext=off, textcoords='offset points', fontsize=9.5, color=c)
    for p in P: print('CHECK', name, p)
ax.scatter([], [], s=110, color='#777', label='temperature 0 (one reading)'); ax.scatter([], [], s=60, facecolor='white', edgecolor='#777', lw=1.8, label='temperature 1 (two more readings)')
ax.legend(loc='lower right', frameon=False, fontsize=9)
ax.set_xlim(-1.5, 27); ax.set_ylim(-5, 108)
ax.set_xlabel('cheap-talk markets it calls "agreement carried out" (of 25)\n← fewer mistakes about prices', fontsize=10.5)
ax.set_ylabel('written agreements it still reports (%)\nfewer mistakes about words →', fontsize=10.5)
ax.set_title('Read three times, the split stays closest to the corner', loc='left', fontsize=13, pad=12)
fig.tight_layout(); os.makedirs('paper2-figs', exist_ok=True); fig.savefig('paper2-figs/fig-tradeoff-temp.png', dpi=150, facecolor='white'); print('wrote')
