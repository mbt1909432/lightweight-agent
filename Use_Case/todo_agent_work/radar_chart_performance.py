"""
Radar chart visualization showing performance across different conditions 
for selected frame counts. Compares baseline vs ST-GRPO in multi-dimensional space.
Generates publication-quality radar charts for top-tier conferences.
"""

import matplotlib.pyplot as plt
import numpy as np

# Set up publication-quality style
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 10,
    'legend.fontsize': 11,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Data from the table
conditions = ['Original', 'Weather', 'Occlusion', 'Shake', 'Lighting']
frame_counts = ['16 Frames', '32 Frames', '48 Frames', '64 Frames']

# Baseline data for each condition across frame counts
baseline_data = {
    'Original':  [0.287, 0.3158, 0.329, 0.332],
    'Weather':   [0.254, 0.2857, 0.296, 0.303],
    'Occlusion': [0.280, 0.3175, 0.331, 0.334],
    'Shake':     [0.277, 0.3122, 0.324, 0.328],
    'Lighting':  [0.272, 0.3078, 0.321, 0.325],
}

# ST-GRPO data for each condition across frame counts
st_grpo_data = {
    'Original':  [0.348, 0.3883, 0.402, 0.406],
    'Weather':   [0.318, 0.3410, 0.354, 0.359],
    'Occlusion': [0.342, 0.3875, 0.398, 0.402],
    'Shake':     [0.350, 0.3980, 0.410, 0.416],
    'Lighting':  [0.336, 0.3787, 0.392, 0.397],
}

# Function to create radar chart
def create_radar_chart(ax, values_baseline, values_st_grpo, labels, title):
    # Number of variables
    N = len(labels)
    
    # Angle for each axis
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Complete the circle
    
    # Add values to complete the circle
    values_baseline += values_baseline[:1]
    values_st_grpo += values_st_grpo[:1]
    
    # Plot
    ax.plot(angles, values_baseline, 'o-', linewidth=2.5, label='Baseline', color='#3498db')
    ax.fill(angles, values_baseline, alpha=0.25, color='#3498db')
    
    ax.plot(angles, values_st_grpo, 'o-', linewidth=2.5, label='ST-GRPO', color='#e74c3c')
    ax.fill(angles, values_st_grpo, alpha=0.25, color='#e74c3c')
    
    # Add labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    
    # Set y-axis limits and labels
    ax.set_ylim(0.2, 0.45)
    ax.set_yticks([0.25, 0.30, 0.35, 0.40])
    ax.set_yticklabels(['0.25', '0.30', '0.35', '0.40'])
    
    # Add grid
    ax.grid(True)
    
    # Add title
    ax.set_title(title, size=14, fontweight='bold', pad=20)
    
    # Add legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))

# Create figure with subplots for different frame counts
fig, axes = plt.subplots(2, 2, figsize=(16, 12), subplot_kw=dict(projection='polar'))

# Create radar charts for each frame count
for i, (frame_count, ax) in enumerate(zip(frame_counts, axes.flat)):
    baseline_values = [baseline_data[condition][i] for condition in conditions]
    st_grpo_values = [st_grpo_data[condition][i] for condition in conditions]
    
    create_radar_chart(ax, baseline_values.copy(), st_grpo_values.copy(), 
                      conditions, f'{frame_count}')

# Add overall title
fig.suptitle('Radar Chart Comparison: Baseline vs ST-GRPO Performance\nAcross Different Conditions and Frame Counts', 
             fontsize=16, fontweight='bold', y=0.98)

# Adjust layout
plt.tight_layout()
plt.subplots_adjust(top=0.90)

# Save the figure
output_path = 'E:/pycharm_project/lightweight-agent/Use_Case/todo_agent_work/radar_chart_performance.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"Radar chart visualization saved to: {output_path}")

# Close the figure to free memory
plt.close()

# Create a second figure with different radar chart layout
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 8), subplot_kw=dict(projection='polar'))

# Radar chart 1: 32 frames vs 64 frames comparison
baseline_32 = [baseline_data[condition][1] for condition in conditions]
st_grpo_32 = [st_grpo_data[condition][1] for condition in conditions]
baseline_64 = [baseline_data[condition][3] for condition in conditions]
st_grpo_64 = [st_grpo_data[condition][3] for condition in conditions]

# First subplot: 32 Frames
N = len(conditions)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

baseline_32 += baseline_32[:1]
st_grpo_32 += st_grpo_32[:1]

axes2[0].plot(angles, baseline_32, 'o-', linewidth=3, label='Baseline (32F)', color='#3498db', markersize=8)
axes2[0].fill(angles, baseline_32, alpha=0.25, color='#3498db')
axes2[0].plot(angles, st_grpo_32, 'o-', linewidth=3, label='ST-GRPO (32F)', color='#e74c3c', markersize=8)
axes2[0].fill(angles, st_grpo_32, alpha=0.25, color='#e74c3c')

axes2[0].set_xticks(angles[:-1])
axes2[0].set_xticklabels(conditions, fontsize=11)
axes2[0].set_ylim(0.2, 0.45)
axes2[0].set_yticks([0.25, 0.30, 0.35, 0.40])
axes2[0].set_yticklabels(['0.25', '0.30', '0.35', '0.40'])
axes2[0].grid(True)
axes2[0].set_title('32 Frames Performance', size=14, fontweight='bold', pad=20)
axes2[0].legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

# Second subplot: 64 Frames
baseline_64 += baseline_64[:1]
st_grpo_64 += st_grpo_64[:1]

axes2[1].plot(angles, baseline_64, 'o-', linewidth=3, label='Baseline (64F)', color='#2980b9', markersize=8)
axes2[1].fill(angles, baseline_64, alpha=0.25, color='#2980b9')
axes2[1].plot(angles, st_grpo_64, 'o-', linewidth=3, label='ST-GRPO (64F)', color='#c0392b', markersize=8)
axes2[1].fill(angles, st_grpo_64, alpha=0.25, color='#c0392b')

axes2[1].set_xticks(angles[:-1])
axes2[1].set_xticklabels(conditions, fontsize=11)
axes2[1].set_ylim(0.2, 0.45)
axes2[1].set_yticks([0.25, 0.30, 0.35, 0.40])
axes2[1].set_yticklabels(['0.25', '0.30', '0.35', '0.40'])
axes2[1].grid(True)
axes2[1].set_title('64 Frames Performance', size=14, fontweight='bold', pad=20)
axes2[1].legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

fig2.suptitle('Detailed Radar Comparison: 32 vs 64 Frames Performance', 
              fontsize=16, fontweight='bold', y=0.95)

plt.tight_layout()
plt.subplots_adjust(top=0.85)

# Save the second figure
output_path2 = 'E:/pycharm_project/lightweight-agent/Use_Case/todo_agent_work/radar_detailed_comparison.png'
plt.savefig(output_path2, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"Detailed radar comparison saved to: {output_path2}")

plt.close()