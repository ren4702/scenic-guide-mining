import json
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

# 1. 读取刚才生成的实体 JSON 文件
with open("outputs/exp2_entities.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. 转成表格并统计词频
df = pd.DataFrame(data)

# 先备份一下原始数据（代表优化前）
df_raw = df.copy()

# 迭代优化：根据初步观察，剔除掉太泛的词（比如“今天”这种对游览指南没用的时间词）
# 这就是任务书里要求的“根据可视化调整停用词”
stop_words = ["今天", "这里", "那里"]
df_optimized = df[~df["entity"].isin(stop_words)]

# 3. 画图（优化前 vs 优化后的对比）
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 图1：优化前
counts_raw = df_raw["entity"].value_counts().head(8)
axes[0].bar(counts_raw.index, counts_raw.values, color='skyblue')
axes[0].set_title("Before Optimization (Raw Entities)")
axes[0].set_ylabel("Frequency")
# 让横坐标的中文倾斜，避免挤在一起
axes[0].tick_params(axis='x', rotation=45)

# 图2：优化后
counts_opt = df_optimized["entity"].value_counts().head(8)
axes[1].bar(counts_opt.index, counts_opt.values, color='lightgreen')
axes[1].set_title("After Optimization (Removed Stop Words)")
axes[1].tick_params(axis='x', rotation=45)

# 4. 调整布局并保存
plt.tight_layout()
plt.savefig("outputs/exp2_entity_freq.png", dpi=300)
print("=== 词频对比图已生成，保存在 outputs/exp2_entity_freq.png ===")

# 顺便把优化后的实体存回 JSON，供实验六图谱使用
with open("outputs/exp2_entities_optimized.json", "w", encoding="utf-8") as f:
    json.dump(df_optimized.to_dict(orient="records"), f, ensure_ascii=False, indent=2)