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
    'axes.spines.top': False,
    'axes.spines.right': False,
    'legend.framealpha': 0.95,
    'legend.edgecolor': '#CCCCCC',
})

# Create figure with constrained layout
fig, ax = plt.subplots(figsize=(6.8, 4.0), constrained_layout=True)

# Data preparation
variants = ['Full AMTD', 'Replace with\nOBD', 'Single-scale\nTCN', 'Multi-scale TCN\nw/o Self-Attention\nFusion']
f1_scores = [0.778, 0.762, 0.755, 0.748]

# Define colors and markers for each variant
colors = ['#2E86AB', '#E15554', '#F6AE2D', '#33A02C']
markers = ['o', 's', '^', 'D']
marker_sizes = [120, 100, 100, 100]  # Larger marker for full model

# Plot scatter points
for i, (variant, score, color, marker, size) in enumerate(zip(variants, f1_scores, colors, markers, marker_sizes)):
    ax.scatter(i, score, color=color, marker=marker, s=size, zorder=3, 
               edgecolors='white', linewidth=2, label=variant if i == 0 else None)

# Connect points with lines to show performance drops
for i in range(1, len(f1_scores)):
    ax.plot([0, i], [f1_scores[0], f1_scores[i]], 
            color='gray', linestyle='--', linewidth=1.5, alpha=0.5, zorder=1)

# Add value labels above each point
for i, score in enumerate(f1_scores):
    ax.text(i, score + 0.002, f'{score:.3f}', ha='center', va='bottom', 
            fontsize=11, fontweight='bold')

# Set axis properties
ax.set_xlim(-0.5, len(variants) - 0.5)
ax.set_ylim(0.745, 0.785)
ax.set_xticks(range(len(variants)))
ax.set_xticklabels(variants, fontsize=11)
ax.set_ylabel('Average F1 Score', fontsize=14, fontweight='bold', labelpad=8)
ax.set_title('Ablation Study: AMTD Component Contributions', 
             fontsize=16, fontweight='bold', pad=12)

# Add grid
ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.8, color='#999999')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add a text box highlighting the performance drop
textstr = 'Performance drops from Full AMTD:\n• OBD: -2.1%\n• Single-scale: -2.9%\n• w/o Attention: -3.9%'
props = dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.95, edgecolor='#CCCCCC')
ax.text(0.98, 0.35, textstr, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', horizontalalignment='right', bbox=props)

# Ensure the output directory exists
output_path = Path(r'E:\pycharm_project\rewrite_agent\backend\app\services\workflows\figure_generation_workflow_utils\sample\output\c0ab150e-6665-44d2-ab5c-5070f1805f50\generated_figures\ablation')
output_path.mkdir(parents=True, exist_ok=True)

# Save the figure
plt.savefig(r'E:\pycharm_project\rewrite_agent\backend\app\services\workflows\figure_generation_workflow_utils\sample\output\c0ab150e-6665-44d2-ab5c-5070f1805f50\generated_figures\ablation\ablation_amtd_scatter_plot.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()