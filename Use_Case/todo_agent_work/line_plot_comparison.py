"""
Line plot visualization of Qwen2.5-VL-7B performance trends across frame counts.
Shows how both baseline and ST-GRPO methods improve with more frames.
Generates publication-quality line plots for top-tier conferences.
"""

import matplotlib.pyplot as plt
import numpy as np

# Set up publication-quality style
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 11,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.linewidth': 1.2,
    'lines.linewidth': 2.5,
    'lines.markersize': 8,
})

# Data from the table
conditions = ['Original', 'Weather', 'Occlusion', 'Shake', 'Lighting', 'Average']
frame_counts = [16, 32, 48, 64]

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
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Color palette for different conditions
colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1a1a1a']
markers = ['o', 's', '^', 'D', 'v', 'h']
linestyles = ['-', '-', '-', '-', '-', '--']

# Plot 1: All conditions trends
for i, condition in enumerate(conditions):
    baseline_values = baseline_data[condition]
    st_grpo_values = st_grpo_data[condition]
    
    # Plot baseline
    ax1.plot(frame_counts, baseline_values, 
             color=colors[i], marker=markers[i], linestyle='--',
             alpha=0.6, label=f'{condition} (Baseline)')
    
    # Plot ST-GRPO
    ax1.plot(frame_counts, st_grpo_values, 
             color=colors[i], marker=markers[i], linestyle='-',
             linewidth=2.5, label=f'{condition} (+ST-GRPO)')

ax1.set_xlabel('Frame Count', fontweight='bold')
ax1.set_ylabel('Performance Score', fontweight='bold')
ax1.set_title('Performance Trends Across Frame Counts\n(All Conditions)', fontweight='bold')
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
ax1.set_xticks(frame_counts)
ax1.set_ylim(0.24, 0.43)

# Plot 2: Focus on Average performance with improvement margins
avg_baseline = baseline_data['Average']
avg_st_grpo = st_grpo_data['Average']

ax2.plot(frame_counts, avg_baseline, 'o-', color='#3498db', linewidth=3, 
         markersize=10, label='Baseline', alpha=0.8)
ax2.plot(frame_counts, avg_st_grpo, 'o-', color='#e74c3c', linewidth=3, 
         markersize=10, label='+ST-GRPO')

# Fill between to show improvement
ax2.fill_between(frame_counts, avg_baseline, avg_st_grpo, 
                alpha=0.2, color='green', label='Improvement')

# Add improvement percentage annotations
for i, (frames, baseline, st_grpo) in enumerate(zip(frame_counts, avg_baseline, avg_st_grpo)):
    improvement = ((st_grpo - baseline) / baseline) * 100
    ax2.annotate(f'+{improvement:.1f}%', 
                xy=(frames, st_grpo), xytext=(frames, st_grpo + 0.015),
                ha='center', va='bottom', fontsize=11, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='darkgreen', lw=1.5))

ax2.set_xlabel('Frame Count', fontweight='bold')
ax2.set_ylabel('Average Performance Score', fontweight='bold')
ax2.set_title('Average Performance Improvement\nwith ST-GRPO Training', fontweight='bold')
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.legend(fontsize=12)
ax2.set_xticks(frame_counts)
ax2.set_ylim(0.30, 0.42)

# Adjust layout
plt.tight_layout()

# Save the figure
output_path = 'E:/pycharm_project/lightweight-agent/Use_Case/todo_agent_work/line_plot_comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"Line plot comparison saved to: {output_path}")

# Close the figure to free memory
plt.close()