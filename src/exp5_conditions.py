import re
import json
import pandas as pd
import matplotlib.pyplot as plt

# 解决画图中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 模拟包含条件建议的文本（含官方指南与游客游记风格）
text_data = """
官方指南：如果遇到下雨天气，建议前往故宫室内的珍宝馆参观。如果带老人同行，建议租借轮椅并使用无障碍通道。
游客游记：假如你想避开人流，可以在早上8点前从午门进入。若是带孩子游玩，建议去御花园休息。如果体力不佳，建议乘坐观光车。
"""

# ================= 1. 条件触发词与抽取规则设计 =================
# 定义触发词
condition_triggers = ["如果", "假如", "若是", "若"]
suggestion_triggers = ["建议", "可以", "则"]

# 正则表达式：捕获 (触发词)(条件内容)，(建议词)(建议内容)
# 例如：如果(遇到下雨天气)，建议(前往珍宝馆参观)
pattern = r'(如果|假如|若是|若)(.*?)[，,。](建议|可以|则)(.*?)[。]'

# ================= 2. 条件-建议信息抽取 =================
matches = re.findall(pattern, text_data)

data_list = []
for i, match in enumerate(matches):
    cond_trigger, condition, sug_trigger, suggestion = match
    condition = condition.strip()
    suggestion = suggestion.strip()
    
    # 简单分类逻辑（根据条件里的词判断游客类型或条件类型）
    visitor_type = "通用"
    cond_type = "其他"
    
    if any(w in condition for w in ["老人", "孩子", "亲子"]):
        visitor_type = "特殊人群"
        cond_type = "人员"
    elif any(w in condition for w in ["雨", "天气"]):
        cond_type = "天气"
    elif any(w in condition for w in ["人流", "时间", "早"]):
        cond_type = "时间/客流"
    elif any(w in condition for w in ["体力"]):
        cond_type = "身体状况"

    data_list.append({
        "condition_id": f"c_{i+1:03d}",
        "condition_type": cond_type,
        "condition_text": condition,
        "suggestion_text": suggestion,
        "visitor_type": visitor_type,
        "source": "混合文本"
    })

# ================= 3. 映射表构建与去重 =================
df = pd.DataFrame(data_list)
# 去重：如果条件内容和建议内容完全一样，就删掉
df = df.drop_duplicates(subset=['condition_text', 'suggestion_text'])

# 保存到 outputs
df.to_csv("outputs/exp5_condition_mapping.csv", index=False, encoding="utf-8-sig")
df.to_json("outputs/exp5_condition_mapping.json", orient="records", force_ascii=False, indent=2)

# ================= 4. 分组统计与可视化 =================
# 统计不同游客类型的建议数量
type_counts = df["visitor_type"].value_counts()

plt.figure(figsize=(8, 5))
# 画柱状图
bars = plt.bar(type_counts.index, type_counts.values, color=['#4CAF50', '#2196F3'])
plt.title("不同游客类型的条件建议数量对比")
plt.xlabel("游客类型")
plt.ylabel("建议条数")

# 在柱子上标数字
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom', ha='center')

plt.savefig("outputs/exp5_condition_bar.png", dpi=300)
plt.close()

print("=== 实验五处理完成！ ===")
print(f"成功抽取并去重后，共得到 {len(df)} 条条件-建议映射。")
print("\n【映射表预览】")
print(df[["condition_type", "condition_text", "suggestion_text"]].to_string())
print("\n成果已输出至 outputs/ 文件夹 (包含CSV、JSON、柱状图)")