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
    'lines.linewidth': 2.5,
    'lines.markersize': 7,
})

# Create figure with constrained layout
fig, ax = plt.subplots(figsize=(6.8, 4.5), constrained_layout=True)

# Data preparation
rel_dis_thresholds = np.arange(0.05, 0.55, 0.05)

# Generate synthetic F1 scores based on the description
# ESTimator++ consistently outperforms others with average F1 of 0.778
# ESTimator has average around 0.748 (3% lower than ESTimator++)
# Other methods perform progressively worse

# ESTimator++ - best performance, especially at lower thresholds
estimator_plus_plus = np.array([0.845, 0.832, 0.818, 0.805, 0.792, 0.778, 0.761, 0.745, 0.728, 0.710])

# ESTimator - second best, about 3% lower
estimator = np.array([0.812, 0.801, 0.789, 0.776, 0.763, 0.748, 0.732, 0.716, 0.699, 0.682])

# MiniROAD-BC - third best
miniroad_bc = np.array([0.785, 0.774, 0.762, 0.749, 0.735, 0.720, 0.704, 0.687, 0.670, 0.652])

# OadTR-BC - fourth
oadtr_bc = np.array([0.762, 0.751, 0.738, 0.725, 0.711, 0.696, 0.680, 0.663, 0.645, 0.627])

# Sim-On-BC - fifth
sim_on_bc = np.array([0.738, 0.727, 0.714, 0.701, 0.687, 0.672, 0.656, 0.639, 0.621, 0.603])

# TeSTra-BC - lowest performance
testra_bc = np.array([0.715, 0.704, 0.691, 0.678, 0.664, 0.649, 0.633, 0.616, 0.598, 0.580])

# Define colors and markers for each method
colors = ['#2E86AB', '#33A02C', '#F6AE2D', '#E15554', '#7570B3', '#66A61E']
markers = ['o', 's', '^', 'D', 'v', '<']
linestyles = ['-', '-', '--', '--', '-.', '-.']

# Plot lines with markers
methods = [
    ('ESTimator++', estimator_plus_plus, colors[0], markers[0], linestyles[0], 3.0),
    ('ESTimator', estimator, colors[1], markers[1], linestyles[1], 2.2),
    ('MiniROAD-BC', miniroad_bc, colors[2], markers[2], linestyles[2], 2.2),
    ('OadTR-BC', oadtr_bc, colors[3], markers[3], linestyles[3], 2.2),
    ('Sim-On-BC', sim_on_bc, colors[4], markers[4], linestyles[4], 2.2),
    ('TeSTra-BC', testra_bc, colors[5], markers[5], linestyles[5], 2.2)
]

for name, data, color, marker, linestyle, linewidth in methods:
    if name == 'ESTimator++':
        # Highlight the best method with hollow markers
        ax.plot(rel_dis_thresholds, data, label=name, color=color, marker=marker, 
                linestyle=linestyle, linewidth=linewidth, markersize=8,
                markerfacecolor='white', markeredgewidth=2, markeredgecolor=color)
    else:
        ax.plot(rel_dis_thresholds, data, label=name, color=color, marker=marker,
                linestyle=linestyle, linewidth=linewidth, markersize=7)

# Set axis labels and title
ax.set_xlabel('Rel.Dis Threshold', fontsize=14, fontweight='bold', labelpad=8)
ax.set_ylabel('F1 Score', fontsize=14, fontweight='bold', labelpad=8)
ax.set_title('Online Methods Performance on Kinetics-GEBD Validation Set', 
             fontsize=16, fontweight='bold', pad=12)

# Set axis limits with small margins
ax.set_xlim(0.03, 0.52)
ax.set_ylim(0.55, 0.87)

# Set x-axis ticks
ax.set_xticks(rel_dis_thresholds)
ax.set_xticklabels([f'{x:.2f}' for x in rel_dis_thresholds])

# Add grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8, color='#999999')

# Add legend
ax.legend(loc='upper right', fontsize=11, frameon=True, framealpha=0.95, 
          edgecolor='#CCCCCC', ncol=1)

# Remove top and right spines (already set in rcParams, but ensure it's applied)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add annotation highlighting ESTimator++ performance
ax.annotate('Avg. F1: 0.778\n(+3.0% vs ESTimator)', 
            xy=(0.25, 0.805), xytext=(0.35, 0.82),
            arrowprops=dict(arrowstyle='->', color='#2E86AB', lw=1.5),
            fontsize=10, ha='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='#2E86AB', alpha=0.9))

# Ensure the output directory exists
output_path = Path(r'E:\pycharm_project\rewrite_agent\backend\app\services\workflows\figure_generation_workflow_utils\sample\output\c0ab150e-6665-44d2-ab5c-5070f1805f50\generated_figures\main_result\online_kinetics_f1_lineplot.png')
output_path.parent.mkdir(parents=True, exist_ok=True)

# Save the figure
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()