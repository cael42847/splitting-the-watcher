#!/usr/bin/env python3
"""draw_paper2_indep_2026-10-25.py — the figures of PREREG-INDEPENDENT-LABEL-AND-OWN-SCALE-2026-10-25.md, from SCORES-INDEP.json only.
No experiment run, no API called. Runs from anywhere (it chdirs to slope/):
  uv run -q --python 3.12 --with matplotlib --with numpy python draw_paper2_indep_2026-10-25.py [SCORES.json] [OUT_PREFIX]
  (1) paper2-figs/fig-tradeoff.png   one dot per watcher: x = cheap-talk markets called "agreement carried out" (of 25, the price error),
                                     y = written agreements it kept (share of boards where the reader found one, the word error)
  (2) paper2-figs/fig-two-labels.png AUROC of each watcher's collusion score against the price label and against the written-agreement
                                     label, side by side, with the two no-model baselines
Every drawn number is printed in a line tagged CHECK."""
import json, os, re, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

SRC = sys.argv[1] if len(sys.argv) > 1 else 'runs/money/saydo-watch/SCORES-INDEP.json'
PRE = sys.argv[2] if len(sys.argv) > 2 else 'paper2-figs/'
os.makedirs(os.path.dirname(PRE) or '.', exist_ok=True)
R = json.load(open(SRC)); p1 = R['PART 1 — L, the written-agreement label']; p2 = R['PART 2 — W10, own scale, against the do-label']
BLUE, OR, AQ, GREY, INK, MUTED, WHITE, PUR = '#2a78d6', '#eb6834', '#1baf7a', '#9a9893', '#0b0b0b', '#52514e', '#ffffff', '#8a5cd6'
NAME = {'W1': 'first watcher', 'W2': 'same report, DeepSeek', 'W3': 'same report, Haiku', 'W4': 'prices only, DeepSeek',
        'W5': 'prices only, Haiku', 'W6': 'given the scale', 'W8': 'scale + compute + claims', 'W9': 'scale + compute first',
        'W10': 'builds its own scale + compute first'}
COL = {'W1': INK, 'W2': GREY, 'W3': GREY, 'W4': GREY, 'W5': GREY, 'W6': OR, 'W8': BLUE, 'W9': BLUE, 'W10': AQ}
def style(ax):
    ax.set_facecolor(WHITE)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'): ax.spines[s].set_color('#c9c8c3')
    ax.tick_params(colors=MUTED, labelsize=10); ax.grid(color='#ebeae6', lw=0.8); ax.set_axisbelow(True)
def frac(s):   # "23 of 62 = 0.37" or "23 of 62"
    m = re.match(r'(\d+) of (\d+)', s); return int(m.group(1)), int(m.group(2))

# P-a for every arm: the core arms from Part 2; W2–W5 from the earlier recounts (SCORES.json / SCORES-PRICES.json, unchanged)
PA = {a: frac(p2[f"P-a {a}: cheap talk called 'agreement carried out'"])[0] for a in ('W1', 'W6', 'W8', 'W9', 'W10')}
PA.update({'W2': 22, 'W3': 17, 'W4': 23, 'W5': 0})
KEEP = {a: frac(p1[f'words flagged, {a}']['recall on L=yes']) for a in NAME}
FA = {a: frac(p1[f'words flagged, {a}']['false alarm on L=no']) for a in NAME}

# (1) the trade-off
fig, ax = plt.subplots(figsize=(8.6, 6.2)); style(ax)
off = {'W2': (-150, -14), 'W3': (-150, -18), 'W4': (10, 4), 'W5': (8, 4), 'W1': (12, -14), 'W6': (8, 4), 'W8': (8, 4), 'W9': (8, 6), 'W10': (-30, -24)}
ax.scatter([0], [100], s=260, facecolor='none', edgecolor=INK, lw=1.3, ls='--', zorder=2)
ax.annotate('where a good watcher would be', (0, 100), xytext=(-6, -26), textcoords='offset points', fontsize=9.5, color=INK, style='italic')
for a in NAME:
    k, n = KEEP[a]; x, y = PA[a], 100 * k / n
    ax.scatter([x], [y], s=110, color=COL[a], zorder=3, edgecolor=WHITE, lw=1.2)
    ax.annotate(NAME[a], (x, y), xytext=off[a], textcoords='offset points', fontsize=9.5, color=COL[a] if COL[a] != GREY else MUTED)
    print(f'CHECK tradeoff {a}: cheap talk called agreement {x}/25; written agreements kept {k}/{n} = {y:.0f}%; false alarm on no-agreement {FA[a][0]}/{FA[a][1]}')
SPL = 'runs/money/saydo-watch/SCORES-SPLIT.json'
if os.path.exists(SPL) and len(sys.argv) <= 1:
    sp = json.load(open(SPL))['words from reader L']; x = frac(sp["cheap talk called 'agreement carried out'"])[0]; k, n = frac(sp['words reported on L=yes'])
    ax.scatter([x], [100 * k / n], s=170, marker='D', color=PUR, zorder=4, edgecolor=WHITE, lw=1.2)
    ax.annotate('the split: words from the board reader,\nprices from "scale + compute first"', (x, 100 * k / n), xytext=(14, -6), textcoords='offset points', fontsize=9.5, color=PUR)
    print(f'CHECK split: cheap talk called agreement {x}/25; written agreements kept {k}/{n}; case accuracy {sp["case accuracy (87 labelled)"]}')
ax.set_xlim(-1.5, 27); ax.set_ylim(-5, 105)
ax.set_xlabel('cheap-talk markets it calls "agreement carried out" (of 25)\n← fewer mistakes about prices', color=INK, fontsize=10.5)
ax.set_ylabel('written agreements it still reports (%)\nfewer mistakes about words →', color=INK, fontsize=10.5)
ax.set_title('One watcher trades one mistake for the other. Two readers don\'t have to.', loc='left', fontsize=13, color=INK, pad=36)
ax.text(0, 1.01, f"written agreements: found on the board by a separate reader (GPT-5.1) that saw only the posts, in {p1['L-0: talk markets with a written agreement'].split(' (')[0]} talk markets\n(62 of 62 after a second reader checked every disputed board)",
        transform=ax.transAxes, fontsize=8.8, color=MUTED, va='bottom', ha='left')
ax.text(0, 1.01, '', transform=ax.transAxes)
fig.tight_layout(); fig.savefig(PRE + 'fig-tradeoff.png', dpi=150, facecolor=WHITE); plt.close(fig); print('wrote', PRE + 'fig-tradeoff.png')

# (2) two labels
rows = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W8', 'W9', 'W10', 'price correlation (no model)', 'raw end price (no model, no ruler)']
lab = {**NAME, 'price correlation (no model)': 'price correlation (no model)', 'raw end price (no model, no ruler)': 'raw end price (no model, no scale)'}
def au(part, key):
    b = part.get(key) or {}; return b.get('AUROC'), b.get('95% interval')
fig, ax = plt.subplots(figsize=(8.6, 6.4)); style(ax)
for i, a in enumerate(rows):
    y = len(rows) - 1 - i
    dl = au(p2, f'score vs do-label, {a}') if a not in ('W2', 'W3', 'W4', 'W5') else (None, None)
    ll = au(p1, f'score vs L, talk markets only, {a}')
    for (v, ci), c, dy, tag in ((dl, OR, 0.13, 'price label'), (ll, PUR, -0.13, 'written-agreement label')):
        if v is None: continue
        ax.plot(ci, [y + dy] * 2, color=c, lw=2, alpha=0.5); ax.scatter([v], [y + dy], color=c, s=55, zorder=3)
        print(f'CHECK two-labels {a} vs {tag}: AUROC {v} {ci}')
ax.set_yticks(range(len(rows))); ax.set_yticklabels([lab[a] for a in rows][::-1], fontsize=9.5)
ax.axvline(0.5, color='#c9c8c3', lw=1, ls='--'); ax.set_xlim(0, 1.05)
ax.set_xlabel('AUROC of the collusion score (0.5 = chance, 1 = perfect)', color=INK, fontsize=10.5)
ax.scatter([], [], color=OR, label='against the price label (end price vs the scale; circular)')
ax.scatter([], [], color=PUR, label='against the written agreement (talk markets only; not the watcher\'s number)')
ax.legend(loc='lower left', fontsize=8.8, frameon=False, bbox_to_anchor=(0, 1.0))
ax.set_title('One score, two truths', loc='left', fontsize=13, color=INK, pad=34)
fig.tight_layout(); fig.savefig(PRE + 'fig-two-labels.png', dpi=150, facecolor=WHITE); plt.close(fig); print('wrote', PRE + 'fig-two-labels.png')
