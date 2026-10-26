#!/usr/bin/env python3
"""draw_paper2_cases_2026-10-25.py — Table 5 as four quadrants (her design, 25 Oct ~22:0x), laid out as Table 2: rows written
agreement / none, columns prices high / low. Per quadrant: M = markets of that true case, then how many W, C, S put in it;
DeepSeek line orange, Haiku line blue, M in black. Counts from score_indep.py --hands-L (R's words for S) and score_haiku.py
(truth = the label checker). No API.  uv run -q --python 3.12 --with matplotlib python draw_paper2_cases_2026-10-25.py"""
import os, sys, io, contextlib, runpy, json
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def run(path, argv):
    sys.argv = [path] + argv
    with contextlib.redirect_stdout(io.StringIO()): return runpy.run_path(path)
D = run('score_indep.py', ['--hands-L']); Lr = {r['name']: r['L'] for r in run('score_indep.py', [])['runs']}
FOL = {"agreement carried out", "parallel moves without talk"}
CASES = ("agreement carried out", "cheap talk", "parallel moves without talk", "competition")
def comb(w, f): return {(True, True): CASES[0], (True, False): CASES[1], (False, True): CASES[2], (False, False): CASES[3]}[(w, f)]
def callD(r, a):
    if a == 'W': return D['case'](r, 'W1')
    c = D['case'](r, 'W9'); return c if a == 'C' else comb(Lr[r['name']] == 'yes', c in FOL)
lab = [r for r in D['runs'] if r['case_true']]
N = {'DeepSeek': {t: [sum(r['case_true'] == t for r in lab)] + [sum(r['case_true'] == t and callD(r, a) == t for r in lab) for a in 'WCS'] for t in CASES}}
Hc = json.load(open('runs/money/saydo-watch/SCORES-HAIKU.json'))['truth = hands']['case tables (true -> called)']
N['Haiku'] = {t: [sum(Hc['S'][t].values())] + [Hc[a][t][t] for a in 'WCS'] for t in CASES}
for m in N: print('CHECK', m, N[m], 'all', [sum(N[m][t][i] for t in CASES) for i in range(4)])
COL = {'DeepSeek': '#eb6834', 'Haiku': '#2a78d6'}; INK = '#0b0b0b'
NAME = {CASES[0]: 'agreement carried out', CASES[1]: 'cheap talk', CASES[2]: 'parallel moves', CASES[3]: 'competition'}
fig, ax = plt.subplots(figsize=(9.0, 4.2)); ax.set_xlim(0, 10); ax.set_ylim(0.75, 6.2); ax.axis('off')
X0, CW, Y0, RH = 1.6, 4.2, 0.9, 2.3   # grid origin, cell width, bottom, row height
ax.text(X0 + CW / 2, Y0 + 2 * RH + 0.35, 'prices low', ha='center', fontsize=11.5, fontweight='bold')
ax.text(X0 + 1.5 * CW, Y0 + 2 * RH + 0.35, 'prices high', ha='center', fontsize=11.5, fontweight='bold')
ax.text(X0 - 0.15, Y0 + 1.5 * RH, 'written\nagreement', ha='right', va='center', fontsize=11.5, fontweight='bold')
ax.text(X0 - 0.15, Y0 + 0.5 * RH, 'no\nagreement', ha='right', va='center', fontsize=11.5, fontweight='bold')
POS = {CASES[0]: (1, 1), CASES[1]: (0, 1), CASES[2]: (1, 0), CASES[3]: (0, 0)}
for t, (cx, cy) in POS.items():
    x, y = X0 + cx * CW, Y0 + cy * RH
    ax.add_patch(plt.Rectangle((x, y), CW, RH, fill=False, ec='#8a8984', lw=1))
    ax.text(x + 0.18, y + RH - 0.38, NAME[t], fontsize=11, style='italic', color='#3d3c39')
    for k, m in enumerate(('DeepSeek', 'Haiku')):
        yy = y + RH - 1.0 - k * 0.6; v = N[m][t]
        ax.text(x + 0.18, yy, m, fontsize=9.5, color=COL[m])
        ax.text(x + 1.35, yy, f'M {v[0]}', fontsize=11, color=INK, fontweight='bold')
        if v[0] == 0:
            ax.text(x + 2.15, yy, 'none', fontsize=10.5, color=COL[m], style='italic'); continue
        for j, a in enumerate('WCS'):
            ax.text(x + 2.15 + j * 0.68, yy, f'{a} {v[j + 1]}', fontsize=11, color=COL[m], fontweight='bold' if a == 'S' else 'normal')
fig.tight_layout(); fig.savefig('paper2-figs/fig-cases-quadrants.png', dpi=150, facecolor='white'); print('wrote')
