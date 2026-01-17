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

# Data preparation
online_methods = ['TeSTra-BC', 'MiniROAD-BC', 'ESTimator', 'ESTimator++']
online_times = [15.3, 12.8, 10.5, 8.2]  # ms per frame

offline_methods = ['TCN', 'PC']
offline_times = [2850, 3420]  # total clip time in ms

# Combine all methods and times
all_methods = online_methods + offline_methods
all_times = online_times + offline_times

# Create color scheme
colors = ['#2E86AB', '#33A02C', '#F6AE2D', '#E15554', '#7570B3', '#E7298A']

# Create bar positions
x_pos = np.arange(len(all_methods))

# Create bars
bars = ax.bar(x_pos, all_times, color=colors[:len(all_methods)], 
               edgecolor='black', linewidth=1.2, alpha=0.85)

# Highlight ESTimator++ bar
bars[3].set_alpha(1.0)
bars[3].set_linewidth(2.0)

# Set logarithmic scale for y-axis
ax.set_yscale('log')

# Add value labels on bars
for i, (bar, time) in enumerate(zip(bars, all_times)):
    if i < len(online_methods):
        label = f'{time:.1f} ms'
    else:
        label = f'{time:.0f} ms'
    
    # Position text above bar
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height * 1.05,
            label, ha='center', va='bottom', fontsize=10, fontweight='bold')

# Add vertical separator line between online and offline methods
separator_x = len(online_methods) - 0.5
ax.axvline(x=separator_x, color='gray', linestyle='--', linewidth=1.5, alpha=0.5)

# Add group labels
ax.text(len(online_methods)/2 - 0.5, 3, 'Online Methods\n(per frame)', 
        ha='center', va='center', fontsize=11, style='italic',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

ax.text(len(online_methods) + len(offline_methods)/2 - 0.5, 500, 'Offline Methods\n(total clip)', 
        ha='center', va='center', fontsize=11, style='italic',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# Customize axes
ax.set_xlabel('Methods', fontsize=14, fontweight='bold', labelpad=8)
ax.set_ylabel('Inference Time (ms)', fontsize=14, fontweight='bold', labelpad=8)
ax.set_title('Inference Efficiency Comparison: Online vs Offline Methods', 
             fontsize=16, fontweight='bold', pad=12)

# Set x-axis
ax.set_xticks(x_pos)
ax.set_xticklabels(all_methods, rotation=45, ha='right')

# Set y-axis limits with margin
ax.set_ylim(5, 5000)

# Customize y-axis ticks for better readability
ax.set_yticks([10, 20, 50, 100, 200, 500, 1000, 2000, 5000])
ax.set_yticklabels(['10', '20', '50', '100', '200', '500', '1000', '2000', '5000'])

# Add grid
ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.8, color='#999999')

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Add annotation for ESTimator++
ax.annotate('ESTimator++:\nOptimal balance of\nspeed & accuracy',
            xy=(3, 8.2), xytext=(4.5, 30),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3',
                          color='#E15554', linewidth=1.5),
            fontsize=10, ha='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFE5E5', alpha=0.9))

# Ensure directory exists
output_path = Path(r'E:\pycharm_project\rewrite_agent\backend\app\services\workflows\figure_generation_workflow_utils\sample\output\c0ab150e-6665-44d2-ab5c-5070f1805f50\generated_figures\main_result\inference_efficiency_barchart.png')
output_path.parent.mkdir(parents=True, exist_ok=True)

# Save figure
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
plt.close()