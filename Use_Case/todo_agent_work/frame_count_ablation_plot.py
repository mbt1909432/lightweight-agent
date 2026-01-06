"""
Performance visualization of Qwen2.5-VL-7B with and without ST-GRPO training
across different frame counts on the PEV dataset.
Generates a publication-quality grouped bar chart for top-tier conferences.
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
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--',
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

# Create figure
fig, ax = plt.subplots(figsize=(14, 7))

# Set up positions for grouped bars
n_conditions = len(conditions)
n_frames = len(frame_counts)
bar_width = 0.12
group_gap = 0.3

# Color palettes for Baseline and ST-GRPO
baseline_colors = ['#7fbfff', '#6baed6', '#4292c6', '#2171b5']  # Blue shades
st_grpo_colors = ['#ff9999', '#fc8d62', '#e74c3c', '#c0392b']   # Red/Orange shades

# X positions for each condition group
x_positions = np.arange(n_conditions) * (2 * n_frames * bar_width + group_gap)

# Plot bars for each frame count
for i, (frame, baseline_color, st_grpo_color) in enumerate(zip(frame_counts, baseline_colors, st_grpo_colors)):
    # Get data for this frame count
    baseline_values = [baseline_data[cond][i] for cond in conditions]
    st_grpo_values = [st_grpo_data[cond][i] for cond in conditions]
    
    # Position offset for this frame count
    offset_baseline = (i * 2) * bar_width - (n_frames - 0.5) * bar_width
    offset_st_grpo = (i * 2 + 1) * bar_width - (n_frames - 0.5) * bar_width
    
    # Plot baseline bars
    bars_base = ax.bar(x_positions + offset_baseline, baseline_values, bar_width,
                       label=f'{frame} (Baseline)' if i == 0 else f'{frame} (Base)',
                       color=baseline_color, edgecolor='black', linewidth=0.8,
                       hatch='///' if i % 2 == 0 else '', alpha=0.85)
    
    # Plot ST-GRPO bars
    bars_st = ax.bar(x_positions + offset_st_grpo, st_grpo_values, bar_width,
                     label=f'{frame} (+ST-GRPO)',
                     color=st_grpo_color, edgecolor='black', linewidth=0.8, alpha=0.9)

# Customize the plot
ax.set_xlabel('Condition', fontsize=14, fontweight='bold')
ax.set_ylabel('Performance Score', fontsize=14, fontweight='bold')
ax.set_title('Performance Comparison: Baseline vs ST-GRPO across Frame Counts\n(Qwen2.5-VL-7B on PEV Dataset)', 
             fontsize=15, fontweight='bold', pad=15)

# Set x-axis ticks
ax.set_xticks(x_positions)
ax.set_xticklabels(conditions, fontsize=12)

# Set y-axis range
ax.set_ylim(0.20, 0.45)
ax.set_yticks(np.arange(0.20, 0.46, 0.05))

# Add legend with custom layout
legend = ax.legend(loc='upper left', ncol=4, framealpha=0.95, 
                   edgecolor='black', fancybox=False,
                   bbox_to_anchor=(0.0, 1.0))

# Add subtle horizontal grid lines
ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
ax.xaxis.grid(False)

# Add improvement annotations for Average condition (last group)
avg_idx = conditions.index('Average')
for i in range(n_frames):
    base_val = baseline_data['Average'][i]
    st_val = st_grpo_data['Average'][i]
    improvement = ((st_val - base_val) / base_val) * 100
    
    # Position for annotation
    x_pos = x_positions[avg_idx] + (i * 2 + 0.5) * bar_width - (n_frames - 0.5) * bar_width
    y_pos = st_val + 0.008
    
    ax.annotate(f'+{improvement:.1f}%', xy=(x_pos, y_pos), fontsize=8, 
                ha='center', va='bottom', fontweight='bold', color='darkgreen')

# Adjust layout
plt.tight_layout()

# Save the figure
output_path = 'E:/pycharm_project/lightweight-agent/Use_Case/todo_agent_work/frame_count_ablation.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"Figure saved to: {output_path}")

# Close the figure to free memory
plt.close()
