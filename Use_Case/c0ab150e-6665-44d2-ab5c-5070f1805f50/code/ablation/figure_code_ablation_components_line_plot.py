import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Set publication-quality style parameters
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue', 'Arial', 'DejaVu Sans'],
    'font.size': 12,
    'axes.linewidth': 1.5,
    'axes.labelweight': 'bold',
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'axes.titleweight': 'bold',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'legend.framealpha': 0.95,
    'legend.edgecolor': '#CCCCCC',
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
})

# Create figure with constrained layout
fig, ax = plt.subplots(figsize=(6.8, 4.5), constrained_layout=True)

# Data preparation
variants = ['Baseline', '+HMT', '+SMPE', '+SCL', '+AMTD']
f1_scores = [0.715, 0.733, 0.754, 0.769, 0.798]
deltas = [None, 0.018, 0.021, 0.015, 0.029]

# Plot the line with markers
ax.plot(variants, f1_scores, 'o-', 
        color='#2E86AB',  # Deep sea blue
        linewidth=3.0, 
        markersize=10, 
        markerfacecolor='white',
        markeredgewidth=2.5,
        markeredgecolor='#2E86AB',
        zorder=10)

# Add delta annotations
for i in range(1, len(variants)):
    # Position annotation slightly above the point
    y_pos = f1_scores[i] + 0.003
    ax.annotate(f'+{deltas[i]:.3f}', 
                xy=(i, f1_scores[i]), 
                xytext=(i, y_pos),
                ha='center', 
                va='bottom',
                fontsize=11,
                fontweight='bold',
                color='#E15554',  # Coral red for emphasis
                zorder=15)

# Highlight the baseline and final performance
ax.axhline(y=f1_scores[0], color='#999999', linestyle=':', linewidth=1.2, alpha=0.6)
ax.axhline(y=f1_scores[-1], color='#33A02C', linestyle='--', linewidth=1.5, alpha=0.7)

# Add text annotations for baseline and final
ax.text(0.02, f1_scores[0] + 0.002, f'Baseline: {f1_scores[0]:.3f}', 
        transform=ax.get_yaxis_transform(),
        fontsize=10, 
        color='#666666',
        va='bottom')

ax.text(0.98, f1_scores[-1] - 0.002, f'Full Model: {f1_scores[-1]:.3f}', 
        transform=ax.get_yaxis_transform(),
        fontsize=10, 
        color='#33A02C',
        fontweight='bold',
        ha='right',
        va='top')

# Set axis properties
ax.set_xlabel('Model Variants', fontsize=14, fontweight='bold', labelpad=8)
ax.set_ylabel('Average F1 Score', fontsize=14, fontweight='bold', labelpad=8)
ax.set_title('Cumulative Performance Improvement with Each Component', 
             fontsize=16, fontweight='bold', pad=12)

# Set y-axis limits with some padding
ax.set_ylim(0.705, 0.810)

# Add grid
ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.8, color='#999999')

# Customize tick parameters
ax.tick_params(axis='both', which='major', labelsize=11, width=1.5)
ax.tick_params(axis='x', labelrotation=0)

# Add a subtle background shading to emphasize improvement
ax.fill_between(range(len(variants)), f1_scores[0], f1_scores, 
                alpha=0.1, color='#2E86AB', zorder=1)

# Remove top and right spines (already set in rcParams, but ensure it's applied)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Make left and bottom spines more prominent
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_linewidth(1.5)

# Add a text box with total improvement
total_improvement = f1_scores[-1] - f1_scores[0]
textstr = f'Total Improvement: +{total_improvement:.3f} ({total_improvement/f1_scores[0]*100:.1f}%)'
props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.95, edgecolor='#CCCCCC')
ax.text(0.95, 0.05, textstr, transform=ax.transAxes, fontsize=11,
        verticalalignment='bottom', horizontalalignment='right', bbox=props)

# Ensure the parent directory exists
output_path = Path(r'E:\pycharm_project\rewrite_agent\backend\app\services\workflows\figure_generation_workflow_utils\sample\output\c0ab150e-6665-44d2-ab5c-5070f1805f50\generated_figures\ablation\ablation_components_line_plot.png')
output_path.parent.mkdir(parents=True, exist_ok=True)

# Save the figure
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()