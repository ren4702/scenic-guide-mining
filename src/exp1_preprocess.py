import pandas as pd
import re
import os

# 确保 outputs 文件夹存在
os.makedirs("outputs", exist_ok=True)

# 1. 读取爬虫生成的原始数据
try:
    df_raw = pd.read_csv("data/raw_dataset.csv", encoding="utf-8-sig")
    print(f"成功读取原始数据，共 {len(df_raw)} 条。")
except Exception as e:
    print(f"读取失败，请检查 data/raw_dataset.csv 是否存在。错误: {e}")
    exit()

# 2. 定义清洗函数
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text)
    # 去除 HTML 标签
    text = re.sub(r'<.*?>', '', text)
    # 去除特殊字符（保留中文、英文、数字和基本标点）
    text = re.sub(r'[^\w\s\u4e00-\u9fa5，。！？：；、\-—]', '', text)
    # 统一空白符（把多个换行或空格合并成一个换行）
    text = re.sub(r'\s+', '\n', text).strip()
    return text

# 3. 批量清洗
print("正在批量清洗文本...")
df_raw['clean_text'] = df_raw['原始内容'].apply(clean_text)

# 4. 结构化整理
df_clean = pd.DataFrame({
    "doc_id": [f"doc_{i+1:03d}" for i in range(len(df_raw))],
    "scenic_area": df_raw['景区'],
    "source_type": df_raw['文本类型'],
    "source_name": df_raw['来源'],
    "raw_text": df_raw['原始内容'],
    "clean_text": df_raw['clean_text']
})

# 5. 保存结果
df_clean.to_csv("data/clean_data.csv", index=False, encoding="utf-8-sig")
df_clean.to_csv("outputs/exp1_clean_data_result.csv", index=False, encoding="utf-8-sig")

# 6. 数据质量验证报告
quality_report = "=== 数据质量检查报告 ===\n"
quality_report += f"1. 数据总条数: {len(df_clean)} 条\n"
quality_report += f"2. 景区分布:\n{df_clean['scenic_area'].value_counts().to_string()}\n"
quality_report += f"3. 文本类型分布:\n{df_clean['source_type'].value_counts().to_string()}\n"
quality_report += f"4. 缺失值检查:\n{df_clean.isnull().sum().to_string()}\n"
quality_report += f"5. 重复记录检查: 发现 {df_clean.duplicated(subset=['clean_text']).sum()} 条完全重复的记录\n"

with open("outputs/exp1_quality_report.txt", "w", encoding="utf-8") as f:
    f.write(quality_report)

print(quality_report)
print("实验一数据采集与清洗完成！")