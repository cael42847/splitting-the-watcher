#!/usr/bin/env python3
"""draw_paper2_models_2026-10-25.py — the trade-off on both seller models, from the run files via score_indep.py (DeepSeek) and
score_haiku.py (Haiku). Truth for the words = the second reader's (hands') blind reading, so the split's words axis is not the board
reader grading itself. x = share of cheap-talk markets called "agreement carried out"; y = share of written agreements still reported.
Colours as Paper 1: DeepSeek orange #eb6834, Haiku blue #2a78d6; marker = reader (W circle, C square, S diamond). No API.
  uv run -q --python 3.12 --with matplotlib python draw_paper2_models_2026-10-25.py -> paper2-figs/fig-tradeoff-models.png"""
import os, sys, io, contextlib, runpy
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
WORDS = {"agreement carried out", "cheap talk"}; FOLLOWED = {"agreement carried out", "parallel moves without talk"}
def run(path, argv):
    sys.argv = [path] + argv
    with contextlib.redirect_stdout(io.StringIO()): return runpy.run_path(path)
D = run('score_indep.py', ['--hands-L']); H = run('score_haiku.py', [])
pts = {}
# DeepSeek: truth rows = the hands' L (62/62 talk = yes); R words = the reader's labels; C = code W9
Lr = {r['name']: r['L'] for r in run('score_indep.py', [])['runs']}
for a in ('W', 'C', 'S'):
    rows = D['runs']; ly = [r for r in rows if r['L'] == 'yes']
    ct = [r for r in rows if r['case_true'] == 'cheap talk']
    def case(r, a=a):
        if a == 'W': return D['case'](r, 'W1')
        c = D['case'](r, 'W9')
        if a == 'C': return c
        return {(True, True): 'agreement carried out', (True, False): 'cheap talk', (False, True): 'parallel moves without talk', (False, False): 'competition'}[(Lr[r['name']] == 'yes', c in FOLLOWED)]
    pts[('DeepSeek', a)] = (100 * sum(case(r) == 'agreement carried out' for r in ct) / len(ct), 100 * sum(case(r) in WORDS for r in ly) / len(ly), len(ct), len(ly))
# Haiku: truth = the hands' blind reading
for a in ('W', 'C', 'S'):
    rows = H['runs']; ly = [r for r in rows if r['HB'] == 'yes']
    ct = [r for r in rows if H['truth'](r, 'hands') == 'cheap talk']
    pts[('Haiku', a)] = (100 * sum(H['caseof'](r, a) == 'agreement carried out' for r in ct) / len(ct), 100 * sum(H['caseof'](r, a) in WORDS for r in ly) / len(ly), len(ct), len(ly))
COL = {'DeepSeek': '#eb6834', 'Haiku': '#2a78d6'}; MK = {'W': 'o', 'C': 's', 'S': 'D'}
NAME = {'W': 'W  first watcher', 'C': 'C  compute first', 'S': 'S  split (R + C)'}
fig, ax = plt.subplots(figsize=(8.6, 6.0)); ax.set_facecolor('white')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.grid(color='#ebeae6', lw=0.8); ax.set_axisbelow(True)
ax.scatter([0], [100], s=280, facecolor='none', edgecolor='#0b0b0b', lw=1.3, ls='--')
ax.annotate('where an ideal watcher would be', (0, 100), xytext=(14, 4), textcoords='offset points', fontsize=9.5, style='italic')
for m in ('DeepSeek', 'Haiku'):
    xs = [pts[(m, a)][0] for a in ('W', 'C', 'S')]; ys = [pts[(m, a)][1] for a in ('W', 'C', 'S')]
    for a in ('W', 'C', 'S'):
        x, y, n1, n2 = pts[(m, a)]
        ax.scatter([x], [y], s=150 if a == 'S' else 110, marker=MK[a], color=COL[m], edgecolor='white', lw=1.2, zorder=3)
        print(f'CHECK {m} {a}: cheap talk -> agreement {x:.0f}% of {n1}; written agreements kept {y:.0f}% of {n2}')
    for a in ('W', 'C', 'S'):
        x, y, n1, n2 = pts[(m, a)]; k1, k2 = round(x * n1 / 100), round(y * n2 / 100)
        ax.annotate(f'{NAME[a]}\n{k1} of {n1} · {k2} of {n2}', (x, y), xytext=(10, 2 if m == 'DeepSeek' else -26), textcoords='offset points', fontsize=9, color=COL[m], linespacing=1.3)
ax.scatter([], [], color=COL['DeepSeek'], s=80, label='DeepSeek sellers'); ax.scatter([], [], color=COL['Haiku'], s=80, label='Haiku sellers')
ax.legend(loc='lower right', frameon=False, fontsize=9.5)
ax.set_xlim(-6, 100); ax.set_ylim(-5, 108)
ax.set_xlabel('cheap-talk markets it calls "agreement carried out" (%)\nlower is better', fontsize=10.5)
ax.set_ylabel('written agreements it still reports (%)\nhigher is better', fontsize=10.5)
ax.set_title('On both seller models, the split stays nearest the corner', loc='left', fontsize=13, pad=12)
fig.text(0.01, 0.005, 'Under each reader: cheap-talk markets it calls "agreement carried out" · written agreements it still reports (written agreement by the label checker).\nR, the board reader, has no point of its own: it answers only the words question, and S takes its words from it.', fontsize=8, color='#52514e', va='bottom')
fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig('paper2-figs/fig-tradeoff-models.png', dpi=150, facecolor='white'); print('wrote')
