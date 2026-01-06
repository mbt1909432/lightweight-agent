import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

# 设置中文字体支持（如果需要显示中文）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 创建一个包含多个子图的画布
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Matplotlib 图表集合示例', fontsize=16, fontweight='bold')

# 1. 折线图
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
axes[0, 0].plot(x, y1, label='sin(x)', linewidth=2, color='blue')
axes[0, 0].plot(x, y2, label='cos(x)', linewidth=2, color='red', linestyle='--')
axes[0, 0].set_title('正弦和余弦函数')
axes[0, 0].set_xlabel('x')
axes[0, 0].set_ylabel('y')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

# 2. 散点图
np.random.seed(42)
x_scatter = np.random.randn(100)
y_scatter = np.random.randn(100)
colors = np.random.rand(100)
axes[0, 1].scatter(x_scatter, y_scatter, c=colors, alpha=0.6, cmap='viridis')
axes[0, 1].set_title('随机散点图')
axes[0, 1].set_xlabel('x')
axes[0, 1].set_ylabel('y')

# 3. 柱状图
categories = ['A', 'B', 'C', 'D', 'E']
values = [23, 45, 56, 78, 32]
colors_bar = ['red', 'green', 'blue', 'orange', 'purple']
bars = axes[0, 2].bar(categories, values, color=colors_bar, alpha=0.7)
axes[0, 2].set_title('分类数据柱状图')
axes[0, 2].set_xlabel('类别')
axes[0, 2].set_ylabel('数值')
# 在柱子上添加数值标签
for bar, value in zip(bars, values):
    axes[0, 2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    str(value), ha='center', va='bottom')

# 4. 饼图
sizes = [30, 25, 20, 15, 10]
labels = ['苹果', '香蕉', '橙子', '葡萄', '草莓']
colors_pie = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'lightpink']
wedges, texts, autotexts = axes[1, 0].pie(sizes, labels=labels, colors=colors_pie, 
                                          autopct='%1.1f%%', startangle=90)
axes[1, 0].set_title('水果销售占比')

# 5. 直方图
data = np.random.normal(100, 15, 1000)
axes[1, 1].hist(data, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
axes[1, 1].set_title('正态分布直方图')
axes[1, 1].set_xlabel('数值')
axes[1, 1].set_ylabel('频次')
axes[1, 1].axvline(np.mean(data), color='red', linestyle='dashed', linewidth=2, label=f'均值: {np.mean(data):.1f}')
axes[1, 1].legend()

# 6. 热力图（使用imshow）
data_heatmap = np.random.rand(10, 10)
im = axes[1, 2].imshow(data_heatmap, cmap='hot', interpolation='nearest')
axes[1, 2].set_title('随机热力图')
axes[1, 2].set_xlabel('X轴')
axes[1, 2].set_ylabel('Y轴')
# 添加颜色条
cbar = plt.colorbar(im, ax=axes[1, 2], shrink=0.8)
cbar.set_label('强度值')

# 调整子图间距
plt.tight_layout()

# 保存图片到文件（避免使用 plt.show() 阻塞程序）
plt.savefig('E:/pycharm_project/lightweight-agent/examples/todo_agent_work/matplotlib_demo.png', 
            dpi=300, bbox_inches='tight')
print("图表已保存为: matplotlib_demo.png")

# 创建第二个单独的图表 - 3D图
fig2 = plt.figure(figsize=(10, 8))
ax = fig2.add_subplot(111, projection='3d')

# 创建3D数据
x = np.linspace(-5, 5, 50)
y = np.linspace(-5, 5, 50)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

# 绘制3D表面图
surface = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
ax.set_title('3D 表面图示例')
ax.set_xlabel('X轴')
ax.set_ylabel('Y轴')
ax.set_zlabel('Z轴')

# 添加颜色条
fig2.colorbar(surface, shrink=0.5, aspect=10)

# 保存3D图
plt.savefig('E:/pycharm_project/lightweight-agent/examples/todo_agent_work/3d_plot_demo.png', 
            dpi=300, bbox_inches='tight')
print("3D图表已保存为: 3d_plot_demo.png")

# 创建第三个图表 - 动态风格的图表
fig3, ax = plt.subplots(figsize=(12, 6))

# 创建一些模拟的时间序列数据
dates = np.arange('2023-01', '2024-01', dtype='datetime64[M]')
stock_price = 100 + np.cumsum(np.random.randn(len(dates)) * 2)
volume = np.random.randint(1000, 5000, len(dates))

# 创建双Y轴图表
ax1 = ax
ax2 = ax1.twinx()

# 绘制股价线图
line1 = ax1.plot(dates, stock_price, color='blue', linewidth=2, marker='o', label='股票价格')
ax1.set_xlabel('日期')
ax1.set_ylabel('价格 ($)', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# 绘制成交量柱状图
bars = ax2.bar(dates, volume, alpha=0.3, color='orange', width=20, label='成交量')
ax2.set_ylabel('成交量', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

# 添加标题和图例
ax1.set_title('股票价格与成交量分析图', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

# 设置日期格式
fig3.autofmt_xdate()

# 保存图表
plt.savefig('E:/pycharm_project/lightweight-agent/examples/todo_agent_work/stock_analysis.png', 
            dpi=300, bbox_inches='tight')
print("股票分析图表已保存为: stock_analysis.png")

print("\n所有图表创建完成！")
print("总共生成了3个图表文件：")
print("1. matplotlib_demo.png - 多种基础图表集合")
print("2. 3d_plot_demo.png - 3D表面图")
print("3. stock_analysis.png - 双Y轴时间序列图")