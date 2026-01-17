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

# Data preparation based on the experiment description
variants = ['Full SMPE', 'w/o E^{(r)}', 'w/o E^{(s)}', 'w/o E^{(m)}', 
            'Only E^{(r)}', 'Only E^{(s)}', 'Only E^{(m)}']
f1_scores = [0.778, 0.762, 0.745, 0.758, 0.748, 0.738, 0.752]

# Define colors for different categories
colors = ['#2E86AB',  # Full SMPE (deep sea blue)
          '#F6AE2D', '#F6AE2D', '#F6AE2D',  # Ablated variants (amber yellow)
          '#E15554', '#E15554', '#E15554']  # Single component variants (coral red)

# Create bar chart
bars = ax.bar(range(len(variants)), f1_scores, color=colors, edgecolor='black', linewidth=1.2)

# Add value labels on top of bars
for i, (bar, score) in enumerate(zip(bars, f1_scores)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.002,
            f'{score:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Set axis labels and title
ax.set_xlabel('SMPE Variants', fontsize=14, fontweight='bold', labelpad=8)
ax.set_ylabel('Average F1 Score', fontsize=14, fontweight='bold', labelpad=8)
ax.set_title('Ablation Study: Impact of Error Components in SMPE', 
             fontsize=16, fontweight='bold', pad=12)

# Set x-axis ticks and labels
ax.set_xticks(range(len(variants)))
ax.set_xticklabels(variants, rotation=45, ha='right', fontsize=11)

# Set y-axis range with some margin
ax.set_ylim(0.72, 0.79)
ax.set_yticks(np.arange(0.72, 0.80, 0.02))

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add grid for better readability
ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.8, color='#999999')
ax.set_axisbelow(True)

# Create custom legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#2E86AB', edgecolor='black', label='Full SMPE'),
    Patch(facecolor='#F6AE2D', edgecolor='black', label='Ablated Components'),
    Patch(facecolor='#E15554', edgecolor='black', label='Single Components')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=11, 
          frameon=True, framealpha=0.95, edgecolor='#CCCCCC')

# Add a subtle annotation highlighting the key finding
ax.annotate('Largest drop', xy=(2, 0.745), xytext=(2.5, 0.73),
            arrowprops=dict(arrowstyle='->', color='#666666', lw=1.5),
            fontsize=10, ha='center', color='#666666')

# Ensure the output directory exists
output_path = Path(r'E:\pycharm_project\rewrite_agent\backend\app\services\workflows\figure_generation_workflow_utils\sample\output\c0ab150e-6665-44d2-ab5c-5070f1805f50\generated_figures\ablation\ablation_smpe_bar_chart.png')
output_path.parent.mkdir(parents=True, exist_ok=True)

# Save the figure
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()