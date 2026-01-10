"""
Heatmap visualization showing improvement ratios (ST-GRPO vs Baseline) 
across different conditions and frame counts for Qwen2.5-VL-7B on PEV dataset.
Generates a publication-quality heatmap for top-tier conferences.
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set up publication-quality style
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Data from the table
conditions = ['Original', 'Weather', 'Occlusion', 'Shake', 'Lighting', 'Average']
frame_counts = ['16 Frames', '32 Frames', '48 Frames', '64 Frames']

# Baseline data for each condition across frame counts
baseline_data = {
    'Original':  [0.287, 0.3158, 0.329, 0.332],
    'Weather':   [0.254, 0.2857, 0.296, 0.303],
    'Occlusion': [0.280, 0.3175, 0.331, 0.334],
    'Shake':     [0.277, 0.3122, 0.324, 0.328],
    'Lighting':  [0.272, 0.3078, 0.321, 0.325],
    'Average':   [0.274, 0.3078, 0.320, 0.324],
}

# ST-GRPO data for each condition across frame counts
st_grpo_data = {
    'Original':  [0.348, 0.3883, 0.402, 0.406],
    'Weather':   [0.318, 0.3410, 0.354, 0.359],
    'Occlusion': [0.342, 0.3875, 0.398, 0.402],
    'Shake':     [0.350, 0.3980, 0.410, 0.416],
    'Lighting':  [0.336, 0.3787, 0.392, 0.397],
    'Average':   [0.339, 0.3787, 0.3912, 0.396],
}

# Create figure with subplots for different heatmap views
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# 1. Improvement percentage heatmap
improvement_matrix = np.zeros((len(conditions), len(frame_counts)))
for i, condition in enumerate(conditions):
    for j in range(len(frame_counts)):
        baseline = baseline_data[condition][j]
        st_grpo = st_grpo_data[condition][j]
        improvement = ((st_grpo - baseline) / baseline) * 100
        improvement_matrix[i, j] = improvement

im1 = ax1.imshow(improvement_matrix, cmap='RdYlGn', aspect='auto', vmin=15, vmax=30)
ax1.set_title('ST-GRPO Improvement Percentage (%)\nover Baseline', fontweight='bold', pad=15)
ax1.set_xticks(range(len(frame_counts)))
ax1.set_xticklabels(frame_counts)
ax1.set_yticks(range(len(conditions)))
ax1.set_yticklabels(conditions)

# Add text annotations
for i in range(len(conditions)):
    for j in range(len(frame_counts)):
        text = ax1.text(j, i, f'{improvement_matrix[i, j]:.1f}%',
                       ha="center", va="center", color="black", fontweight='bold')

# Add colorbar
cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
cbar1.set_label('Improvement (%)', fontweight='bold')

# 2. Baseline performance heatmap
baseline_matrix = np.array([baseline_data[condition] for condition in conditions])
im2 = ax2.imshow(baseline_matrix, cmap='Blues', aspect='auto', vmin=0.25, vmax=0.35)
ax2.set_title('Baseline Performance Scores', fontweight='bold', pad=15)
ax2.set_xticks(range(len(frame_counts)))
ax2.set_xticklabels(frame_counts)
ax2.set_yticks(range(len(conditions)))
ax2.set_yticklabels(conditions)

for i in range(len(conditions)):
    for j in range(len(frame_counts)):
        text = ax2.text(j, i, f'{baseline_matrix[i, j]:.3f}',
                       ha="center", va="center", color="white", fontweight='bold')

cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.8)
cbar2.set_label('Baseline Score', fontweight='bold')

# 3. ST-GRPO performance heatmap
st_grpo_matrix = np.array([st_grpo_data[condition] for condition in conditions])
im3 = ax3.imshow(st_grpo_matrix, cmap='Reds', aspect='auto', vmin=0.31, vmax=0.42)
ax3.set_title('ST-GRPO Performance Scores', fontweight='bold', pad=15)
ax3.set_xticks(range(len(frame_counts)))
ax3.set_xticklabels(frame_counts)
ax3.set_yticks(range(len(conditions)))
ax3.set_yticklabels(conditions)

for i in range(len(conditions)):
    for j in range(len(frame_counts)):
        text = ax3.text(j, i, f'{st_grpo_matrix[i, j]:.3f}',
                       ha="center", va="center", color="white", fontweight='bold')

cbar3 = plt.colorbar(im3, ax=ax3, shrink=0.8)
cbar3.set_label('ST-GRPO Score', fontweight='bold')

# 4. Absolute improvement heatmap
absolute_improvement = st_grpo_matrix - baseline_matrix
im4 = ax4.imshow(absolute_improvement, cmap='viridis', aspect='auto', vmin=0.05, vmax=0.08)
ax4.set_title('Absolute Improvement\n(ST-GRPO - Baseline)', fontweight='bold', pad=15)
ax4.set_xticks(range(len(frame_counts)))
ax4.set_xticklabels(frame_counts)
ax4.set_yticks(range(len(conditions)))
ax4.set_yticklabels(conditions)

for i in range(len(conditions)):
    for j in range(len(frame_counts)):
        text = ax4.text(j, i, f'{absolute_improvement[i, j]:.3f}',
                       ha="center", va="center", color="white", fontweight='bold')

cbar4 = plt.colorbar(im4, ax=ax4, shrink=0.8)
cbar4.set_label('Absolute Improvement', fontweight='bold')

# Add overall title
fig.suptitle('Qwen2.5-VL-7B Performance Analysis: ST-GRPO vs Baseline on PEV Dataset', 
             fontsize=18, fontweight='bold', y=0.98)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.93)

# Save the figure
output_path = 'E:/pycharm_project/lightweight-agent/Use_Case/todo_agent_work/heatmap_improvement.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"Heatmap visualization saved to: {output_path}")

# Close the figure to free memory
plt.close()