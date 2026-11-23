"""Regenerate Figures 1 and 2 from version-controlled EvoNIDS summary CSVs.

Run from the LaTeX project directory: python figures/generate_figures.py
Sources: public GitHub full feature-only run (15 Nov 2026) and corrected joint run
(16 Nov 2026). The earlier mislabeled joint run is deliberately excluded.
"""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / 'data'
ORDER = ('GA', 'BPSO', 'PSO', 'NSGA-II')

def load(name):
    with (DATA / name).open(newline='', encoding='utf-8') as f:
        rows = {r['method']: r for r in csv.DictReader(f)}
    assert set(ORDER).issubset(rows), name
    return rows

feature = load('feature_only_summary.csv')
joint = load('corrected_joint_summary.csv')

x = np.arange(len(ORDER))
a = [float(feature[k]['macro_f1_mean']) for k in ORDER]
b = [float(joint[k]['macro_f1_mean']) for k in ORDER]
fig, ax = plt.subplots(figsize=(9.0, 2.8), dpi=170)
ax.bar(x-0.18, a, width=0.35, label='Feature-only')
ax.bar(x+0.18, b, width=0.35, label='Joint RF-HPO')
ax.set_xticks(x, ORDER)
ax.set_ylabel('Mean held-out test Macro-F1')
ax.set_ylim(0.78, 0.91)
ax.legend(ncols=2, loc='upper left', frameon=False)
ax.grid(axis='y', alpha=0.2)
fig.tight_layout()
plt.savefig(HERE / 'figure1.png', dpi=170, bbox_inches='tight')
plt.close(fig)

fig, ax = plt.subplots(figsize=(9.0, 2.7), dpi=170)
for name in ORDER:
    r = joint[name]
    ax.scatter(float(r['mean_reduction_pct']), float(r['macro_f1_mean']), s=75)
    ax.annotate(name, (float(r['mean_reduction_pct']),float(r['macro_f1_mean'])), xytext=(6,6), textcoords='offset points', fontsize=9)
ax.set_xlabel('Mean reduction in raw features (%)')
ax.set_ylabel('Mean held-out test Macro-F1')
ax.set_xlim(65, 90)
ax.set_ylim(0.825, 0.91)
ax.grid(alpha=0.2)
fig.tight_layout()
plt.savefig(HERE / 'figure2.png', dpi=170, bbox_inches='tight')
plt.close(fig)
print('Rebuilt figure1.png and figure2.png from the checked-in summary CSV data.')
