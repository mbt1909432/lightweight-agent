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

# Data preparation based on experiment description
methods = ['BMN', 'TCN', 'PC', 'CoSeg', 'ESTimator', 'ESTimator++']
f1_scores = [0.745, 0.752, 0.789, 0.782, 0.761, 0.778]
categories = ['Offline\nSupervised', 'Offline\nSupervised', 'Offline\nSupervised', 
              'Offline\nUnsupervised', 'Online', 'Online']

# Define colors for each category
colors = {
    'Offline\nSupervised': '#2E86AB',  # Deep sea blue
    'Offline\nUnsupervised': '#33A02C',  # Forest green
    'Online': '#E15554'  # Coral red
}

# Get colors for each bar
bar_colors = [colors[cat] for cat in categories]

# Create bar positions
x_pos = np.arange(len(methods))

# Create bars
bars = ax.bar(x_pos, f1_scores, color=bar_colors, width=0.7, edgecolor='black', linewidth=1.2)

# Add value labels on top of bars
for i, (bar, score) in enumerate(zip(bars, f1_scores)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.005,
            f'{score:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Customize axes
ax.set_xlabel('Methods', fontsize=14, fontweight='bold', labelpad=8)
ax.set_ylabel('Average F1 Score', fontsize=14, fontweight='bold', labelpad=8)
ax.set_title('Comparison of Average F1 Scores on Kinetics-GEBD Dataset', 
             fontsize=16, fontweight='bold', pad=12)

# Set x-axis ticks and labels
ax.set_xticks(x_pos)
ax.set_xticklabels(methods, fontsize=12)

# Set y-axis limits with some margin
ax.set_ylim(0.7, 0.82)

# Add grid
ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.8, color='#999999')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Create custom legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#2E86AB', edgecolor='black', label='Offline Supervised'),
    Patch(facecolor='#33A02C', edgecolor='black', label='Offline Unsupervised'),
    Patch(facecolor='#E15554', edgecolor='black', label='Online')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=11, 
          frameon=True, framealpha=0.95, edgecolor='#CCCCCC')

# Add horizontal line to highlight ESTimator++ performance
ax.axhline(y=0.778, color='#E15554', linestyle='--', linewidth=1.5, alpha=0.7)

# Add subtle category separators
ax.axvline(x=2.5, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax.axvline(x=3.5, color='gray', linestyle=':', linewidth=1, alpha=0.5)

# Ensure directory exists
output_path = Path(r'E:\pycharm_project\rewrite_agent\backend\app\services\workflows\figure_generation_workflow_utils\sample\output\c0ab150e-6665-44d2-ab5c-5070f1805f50\generated_figures\main_result\offline_kinetics_avgf1_barchart.png')
output_path.parent.mkdir(parents=True, exist_ok=True)

# Save figure
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()