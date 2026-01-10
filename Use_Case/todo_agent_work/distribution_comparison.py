"""
Distribution comparison visualization using violin plots and box plots
to compare baseline vs ST-GRPO performance distributions across all conditions.
Generates publication-quality distribution plots for top-tier conferences.
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
    'legend.fontsize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Data from the table
conditions = ['Original', 'Weather', 'Occlusion', 'Shake', 'Lighting', 'Average']
frame_counts = ['16F', '32F', '48F', '64F']

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

# Create figure with subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Prepare data for different visualizations
# 1. Overall distribution comparison
all_baseline = []
all_st_grpo = []
all_conditions_expanded = []
all_methods = []

for condition in conditions:
    for i, frame in enumerate(frame_counts):
        all_baseline.append(baseline_data[condition][i])
        all_st_grpo.append(st_grpo_data[condition][i])
        all_conditions_expanded.extend([condition] * 2)
        all_methods.extend(['Baseline', 'ST-GRPO'])

# Combine all data for plotting
all_scores = all_baseline + all_st_grpo
methods = ['Baseline'] * len(all_baseline) + ['ST-GRPO'] * len(all_st_grpo)

# Plot 1: Overall distribution comparison using violin plot
violin_data = [all_baseline, all_st_grpo]
parts = ax1.violinplot(violin_data, positions=[1, 2], widths=0.6, showmeans=True, showmedians=True)
parts['bodies'][0].set_facecolor('#3498db')
parts['bodies'][0].set_alpha(0.7)
parts['bodies'][1].set_facecolor('#e74c3c')
parts['bodies'][1].set_alpha(0.7)

ax1.set_xticks([1, 2])
ax1.set_xticklabels(['Baseline', 'ST-GRPO'])
ax1.set_ylabel('Performance Score', fontweight='bold')
ax1.set_title('Performance Distribution Comparison\n(All Conditions & Frame Counts)', fontweight='bold')
ax1.grid(True, alpha=0.3)

# Add statistical annotations
baseline_mean = np.mean(all_baseline)
st_grpo_mean = np.mean(all_st_grpo)
improvement = ((st_grpo_mean - baseline_mean) / baseline_mean) * 100

ax1.text(1.5, 0.42, f'Mean Improvement: +{improvement:.1f}%', 
         ha='center', va='center', fontsize=11, fontweight='bold',
         bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

# Plot 2: Box plot by frame count
frame_baseline_data = []
frame_st_grpo_data = []
frame_labels = []

for i, frame in enumerate(frame_counts):
    baseline_values = [baseline_data[cond][i] for cond in conditions]
    st_grpo_values = [st_grpo_data[cond][i] for cond in conditions]
    
    frame_baseline_data.append(baseline_values)
    frame_st_grpo_data.append(st_grpo_values)

positions_base = np.arange(1, len(frame_counts)*2, 2) - 0.2
positions_st = np.arange(1, len(frame_counts)*2, 2) + 0.2

bp1 = ax2.boxplot(frame_baseline_data, positions=positions_base, widths=0.3, 
                  patch_artist=True)
bp2 = ax2.boxplot(frame_st_grpo_data, positions=positions_st, widths=0.3, 
                  patch_artist=True)

for patch in bp1['boxes']:
    patch.set_facecolor('#3498db')
    patch.set_alpha(0.7)
for patch in bp2['boxes']:
    patch.set_facecolor('#e74c3c')
    patch.set_alpha(0.7)

ax2.set_xticks(range(1, len(frame_counts)*2, 2))
ax2.set_xticklabels(frame_counts)
ax2.set_xlabel('Frame Count', fontweight='bold')
ax2.set_ylabel('Performance Score', fontweight='bold')
ax2.set_title('Performance Distribution by Frame Count', fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend([bp1['boxes'][0], bp2['boxes'][0]], ['Baseline', 'ST-GRPO'])

# Plot 3: Box plot by condition
condition_baseline_data = []
condition_st_grpo_data = []

for condition in conditions:
    condition_baseline_data.append(baseline_data[condition])
    condition_st_grpo_data.append(st_grpo_data[condition])

positions_base = np.arange(len(conditions)) - 0.2
positions_st = np.arange(len(conditions)) + 0.2

bp3 = ax3.boxplot(condition_baseline_data, positions=positions_base, widths=0.3, 
                  patch_artist=True)
bp4 = ax3.boxplot(condition_st_grpo_data, positions=positions_st, widths=0.3, 
                  patch_artist=True)

for patch in bp3['boxes']:
    patch.set_facecolor('#3498db')
    patch.set_alpha(0.7)
for patch in bp4['boxes']:
    patch.set_facecolor('#e74c3c')
    patch.set_alpha(0.7)

ax3.set_xticks(range(len(conditions)))
ax3.set_xticklabels(conditions, rotation=45)
ax3.set_xlabel('Condition', fontweight='bold')
ax3.set_ylabel('Performance Score', fontweight='bold')
ax3.set_title('Performance Distribution by Condition', fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend([bp3['boxes'][0], bp4['boxes'][0]], ['Baseline', 'ST-GRPO'])

# Plot 4: Improvement distribution
improvements = []
improvement_labels = []

for condition in conditions:
    for i in range(len(frame_counts)):
        baseline = baseline_data[condition][i]
        st_grpo = st_grpo_data[condition][i]
        improvement = ((st_grpo - baseline) / baseline) * 100
        improvements.append(improvement)
        improvement_labels.append(f'{condition}\n{frame_counts[i]}')

# Create histogram
ax4.hist(improvements, bins=10, color='#2ecc71', alpha=0.7, edgecolor='black')
ax4.axvline(np.mean(improvements), color='red', linestyle='--', linewidth=2, 
           label=f'Mean: {np.mean(improvements):.1f}%')
ax4.axvline(np.median(improvements), color='blue', linestyle='--', linewidth=2, 
           label=f'Median: {np.median(improvements):.1f}%')

ax4.set_xlabel('Improvement Percentage (%)', fontweight='bold')
ax4.set_ylabel('Frequency', fontweight='bold')
ax4.set_title('Distribution of ST-GRPO Improvements', fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend()

# Add statistics text box
stats_text = f'Min: {np.min(improvements):.1f}%\nMax: {np.max(improvements):.1f}%\nStd: {np.std(improvements):.1f}%'
ax4.text(0.75, 0.75, stats_text, transform=ax4.transAxes, 
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
         fontsize=10, verticalalignment='top')

# Add overall title
fig.suptitle('Qwen2.5-VL-7B Performance Distributions: Baseline vs ST-GRPO on PEV Dataset', 
             fontsize=16, fontweight='bold', y=0.98)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.93)

# Save the figure
output_path = 'E:/pycharm_project/lightweight-agent/Use_Case/todo_agent_work/distribution_comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"Distribution comparison visualization saved to: {output_path}")

# Close the figure to free memory
plt.close()