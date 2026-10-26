#!/usr/bin/env python3
"""draw_paper2_map_2026-10-25.py — every market on one picture (her design, 25 Oct ~21:0x): x = end index (prices), y = written
agreement yes / no by the label checker; one panel per seller model. Shaded: low (< 0.25), between (not scored), high (>= 0.5).
Filled = in Table 5 (price label high or low); hollow = between, not in Table 5. The box = the markets Figure 1 counts (written
agreement yes, all prices). From the run files via score_indep.py --hands-L and score_haiku.py. No API.
  uv run -q --python 3.12 --with matplotlib python draw_paper2_map_2026-10-25.py -> paper2-figs/fig-markets-map.png"""
import os, sys, io, contextlib, runpy, random
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
def run(path, argv):
    sys.argv = [path] + argv
    with contextlib.redirect_stdout(io.StringIO()): return runpy.run_path(path)
D = run('score_indep.py', ['--hands-L']); H = run('score_haiku.py', [])
M = {'DeepSeek': [(r['index'], r['L'] == 'yes', r['cell']) for r in D['runs']],
     'Haiku': [(r['index'], r['HB'] == 'yes', r['cell']) for r in H['runs']]}
def kind(c): return 'patrol' if c.endswith('1') else ('warning' if 'W' in c else 'none')
MK = {'none': 'o', 'patrol': 'v', 'warning': 's'}
COL = {'DeepSeek': '#eb6834', 'Haiku': '#2a78d6'}; LIGHT = {'DeepSeek': '#f6b79a', 'Haiku': '#9cc1ee'}
fig, axes = plt.subplots(2, 1, figsize=(9.6, 7.2), sharex=True)
random.seed(3)
for ax, m in zip(axes, ('DeepSeek', 'Haiku')):
    pts = M[m]; xs = [x for x, *_ in pts]
    lo, hi = -0.45, 1.36
    ax.axvspan(0.25, 0.5, color='#ebeae6', zorder=0); ax.axvline(0, color='#52514e', lw=0.8, ls=':', zorder=1)
    for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
    ax.set_yticks([0, 1]); ax.set_yticklabels(['no written\nagreement', 'written\nagreement'], fontsize=9.5); ax.tick_params(axis='y', length=0)
    ax.set_ylim(-0.68, 1.5)
    for x, w, c in pts:
        y = (1 if w else 0) + random.uniform(-0.28, 0.28); scored = x < 0.25 or x >= 0.5
        ax.scatter([x], [y], s=46 if kind(c) == 'patrol' else 34, marker=MK[kind(c)], facecolor=(LIGHT[m] if c.startswith('S') else COL[m]) if scored else 'white', edgecolor=LIGHT[m] if c.startswith('S') else COL[m], lw=1.1, zorder=3)
    nyes = sum(w for _, w, _ in pts); nsc = sum(1 for x, *_ in pts if x < 0.25 or x >= 0.5)
    npb = sum(1 for x, w, c in pts if kind(c) == 'patrol' and x < 0); npt = sum(1 for *_, c in pts if kind(c) == 'patrol')
    for x, y, t, ha in ((lo + 0.02, 1.32, 'cheap talk', 'left'), (hi - 0.02, 1.32, 'agreement carried out', 'right'), (lo + 0.02, -0.5, 'competition', 'left'), (hi - 0.02, -0.5, 'parallel moves', 'right')):
        ax.text(x, y, t, ha=ha, va='center', fontsize=9, color='#3d3c39', style='italic', zorder=5,
                bbox=dict(boxstyle='round,pad=0.25', fc='#f4f3ef', ec='#b5b4ae', lw=0.8))
    nlo = sum(1 for x, *_ in pts if x < 0.25); nmid = sum(1 for x, *_ in pts if 0.25 <= x < 0.5); nhi = sum(1 for x, *_ in pts if x >= 0.5)
    for x, t, ha in ((0.23, f'{nlo} markets\nlow prices', 'right'), (0.375, f'{nmid} markets\nnot scored', 'center'), (0.52, f'{nhi} markets\nhigh prices', 'left')):
        ax.text(x, 0.5, t, ha=ha, multialignment=ha, va='center', fontsize=9.5, color='#52514e', zorder=4)
    print(f'CHECK {m} zones: low {nlo}, between {nmid}, high {nhi}')
    ax.text(-0.135, 0.5, m, transform=ax.transAxes, rotation=90, ha='center', va='center', fontsize=14, color=COL[m], fontweight='bold')
    ax.set_xlim(lo, hi)
    print(f'CHECK {m}: n {len(pts)}, written agreement {nyes}, scored {nsc}, patrol below 0: {npb} of {npt}, index range {min(xs):.2f}..{max(xs):.2f}')
a = axes[1]
axes[1].set_xlabel('end index: 0 = competitive price, 1 = joint-profit price', fontsize=10)
from matplotlib.lines import Line2D
H_ = [Line2D([], [], marker=MK[k], ls='', ms=11, mfc='#52514e', mec='#52514e', label=l) for k, l in (('none', 'no patrol'), ('patrol', 'patrol (cuts at rounds 20, 40, 60, 80)'), ('warning', 'board + warning, no patrol'))] + [Line2D([], [], marker='o', ls='', ms=11, mfc='#c9c8c3', mec='#c9c8c3', label='light: no board')]
fig.legend(handles=H_, loc='upper right', ncol=4, frameon=False, fontsize=10.5, bbox_to_anchor=(0.99, 0.955), handletextpad=0.3, columnspacing=1.6)
fig.suptitle('Every market: what the sellers wrote, and where prices ended', x=0.01, ha='left', fontsize=13)
fig.text(0.01, 0.005, 'Hollow: prices ended between low and high (not scored). Written agreement by the label checker. Left of the dotted line: prices ended below the competitive price.', fontsize=8, color='#52514e', va='bottom')
fig.tight_layout(rect=(0.04, 0.03, 1, 0.92)); fig.savefig('paper2-figs/fig-markets-map.png', dpi=150, facecolor='white'); print('wrote')
