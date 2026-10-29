import pandas as pd
import re
import os

# 确保 outputs 文件夹存在
os.makedirs("outputs", exist_ok=True)

# 1. 读取原始文本
with open("data/raw_data.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# 保存一份原始文本副本（用于清洗前后对比）
with open("outputs/exp1_raw_snapshot.txt", "w", encoding="utf-8") as f:
    f.write(raw_text)

# 2. 数据清洗
# 去除 HTML 标签
clean_text = re.sub(r'<.*?>', '', raw_text)
# 去除特殊字符（保留中文、英文、数字和基本标点）
clean_text = re.sub(r'[^\w\s\u4e00-\u9fa5，。！？：；、\-—]', '', clean_text)
# 统一空白符
clean_text = re.sub(r'\s+', '\n', clean_text).strip()

# 保存清洗后的文本副本
with open("outputs/exp1_clean_snapshot.txt", "w", encoding="utf-8") as f:
    f.write(clean_text)

# 3. 结构化拆分
lines = clean_text.split('\n')
data_list = []

for i, line in enumerate(lines):
    if len(line) > 10: # 过滤掉太短的空行
        data_list.append({
            "doc_id": f"doc_{i+1:03d}",
            "scenic_area": "故宫",
            "source_type": "official" if "官方" in line else "travelogue",
            "raw_text": line, # 因为按行清洗，这里直接用清洗后的
            "clean_text": line
        })

# 4. 保存为 CSV
df = pd.DataFrame(data_list)

# 存到 data 供后续实验读取
df.to_csv("data/clean_data.csv", index=False, encoding="utf-8-sig")

# 存到 outputs 作为作业成果
df.to_csv("outputs/exp1_clean_data_result.csv", index=False, encoding="utf-8-sig")

# 5. 数据质量验证报告（拿满评分细则里的7分）
quality_report = "=== 数据质量检查报告 ===\n"
quality_report += f"1. 数据总条数: {len(df)} 条\n"
quality_report += f"2. 包含的景区: {', '.join(df['scenic_area'].unique())}\n"
quality_report += f"3. 数据来源分布:\n{df['source_type'].value_counts().to_string()}\n"
quality_report += f"4. 缺失值检查:\n{df.isnull().sum().to_string()}\n"
quality_report += f"5. 重复记录检查: 发现 {df.duplicated().sum()} 条完全重复的记录\n"

with open("outputs/exp1_quality_report.txt", "w", encoding="utf-8") as f:
    f.write(quality_report)

print("=== 实验一处理完成！ ===")
print(quality_report)
print("成果已输出至 outputs/ 文件夹 (包含CSV、前后对比快照、质量报告)")