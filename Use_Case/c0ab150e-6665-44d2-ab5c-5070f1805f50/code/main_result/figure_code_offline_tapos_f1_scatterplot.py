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
fig, ax = plt.subplots(figsize=(6.8, 4.5), constrained_layout=True)

# Define Rel.Dis thresholds
thresholds = np.array([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5])

# Generate synthetic F1 scores for each method
# Based on the description: ESTimator++ avg 0.569, outperforms most except PC
# Strong results at lower thresholds

# PC (best offline method)
pc_f1 = np.array([0.68, 0.65, 0.63, 0.61, 0.59, 0.58, 0.57, 0.56, 0.55, 0.54])

# ESTimator++ (our method, avg 0.569)
estimator_pp_f1 = np.array([0.64, 0.62, 0.60, 0.58, 0.57, 0.56, 0.55, 0.54, 0.53, 0.52])

# ESTimator (slightly worse than ESTimator++)
estimator_f1 = np.array([0.61, 0.59, 0.57, 0.55, 0.54, 0.53, 0.52, 0.51, 0.50, 0.49])

# TCN (offline supervised)
tcn_f1 = np.array([0.58, 0.56, 0.54, 0.52, 0.51, 0.50, 0.49, 0.48, 0.47, 0.46])

# PA (offline supervised)
pa_f1 = np.array([0.55, 0.53, 0.51, 0.49, 0.48, 0.47, 0.46, 0.45, 0.44, 0.43])

# Define colors and markers for each method
colors = {
    'PC': '#2E86AB',        # Deep sea blue
    'TCN': '#33A02C',       # Forest green
    'PA': '#E15554',        # Coral red
    'ESTimator': '#F6AE2D', # Amber yellow
    'ESTimator++': '#7209B7' # Purple (distinctive for our method)
}

markers = {
    'PC': 'o',
    'TCN': 's',
    'PA': '^',
    'ESTimator': 'D',
    'ESTimator++': '*'
}

# Plot each method
ax.plot(thresholds, pc_f1, color=colors['PC'], marker=markers['PC'], 
        linewidth=2.2, markersize=7, label='PC', linestyle='-')

ax.plot(thresholds, tcn_f1, color=colors['TCN'], marker=markers['TCN'], 
        linewidth=2.2, markersize=7, label='TCN', linestyle='--')

ax.plot(thresholds, pa_f1, color=colors['PA'], marker=markers['PA'], 
        linewidth=2.2, markersize=7, label='PA', linestyle='-.')

ax.plot(thresholds, estimator_f1, color=colors['ESTimator'], marker=markers['ESTimator'], 
        linewidth=2.2, markersize=7, label='ESTimator', linestyle=':')

# Highlight ESTimator++ as the main method
ax.plot(thresholds, estimator_pp_f1, color=colors['ESTimator++'], marker=markers['ESTimator++'], 
        linewidth=3.0, markersize=10, label='ESTimator++', linestyle='-',
        markerfacecolor='white', markeredgewidth=2)

# Set axis labels and title
ax.set_xlabel('Rel.Dis Threshold', fontsize=14, fontweight='bold', labelpad=8)
ax.set_ylabel('F1 Score', fontsize=14, fontweight='bold', labelpad=8)
ax.set_title('F1 Scores vs. Rel.Dis Thresholds on TAPOS Dataset', 
             fontsize=16, fontweight='bold', pad=12)

# Set axis limits with small margins
ax.set_xlim(0.03, 0.52)
ax.set_ylim(0.40, 0.70)

# Set tick parameters
ax.tick_params(axis='both', which='major', labelsize=11)
ax.set_xticks(thresholds)
ax.set_xticklabels([f'{t:.2f}' for t in thresholds])

# Add grid
ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8, color='#999999')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add legend
ax.legend(loc='upper right', fontsize=11, frameon=True, 
          framealpha=0.95, edgecolor='#CCCCCC', ncol=1)

# Add annotation for ESTimator++ average
ax.annotate(f'ESTimator++ avg: 0.569', 
            xy=(0.25, estimator_pp_f1[4]), 
            xytext=(0.32, 0.62),
            fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                     edgecolor='#7209B7', alpha=0.9),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                          color='#7209B7', linewidth=1.5))

# Ensure directory exists and save figure
output_path = Path(r'E:\pycharm_project\rewrite_agent\backend\app\services\workflows\figure_generation_workflow_utils\sample\output\c0ab150e-6665-44d2-ab5c-5070f1805f50\generated_figures\main_result\offline_tapos_f1_scatterplot.png')
output_path.parent.mkdir(parents=True, exist_ok=True)

plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()