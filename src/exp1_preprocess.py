import pandas as pd
import re

# 1. 读取原始文本
with open("data/raw_data.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# 2. 数据清洗
# 去除 HTML 标签，比如 <br> <p>
clean_text = re.sub(r'<.*?>', '', raw_text)
# 去除特殊字符（保留中文、英文、数字和基本标点）
clean_text = re.sub(r'[^\w\s\u4e00-\u9fa5，。！？：；、\-—]', '', clean_text)
# 统一空白符（把多个换行合并成一个）
clean_text = re.sub(r'\s+', '\n', clean_text).strip()

# 3. 结构化拆分（这里简单模拟，把每段按行拆开当一条数据）
lines = clean_text.split('\n')
data_list = []

for i, line in enumerate(lines):
    if len(line) > 10: # 过滤掉太短的空行
        data_list.append({
            "doc_id": f"doc_{i+1:03d}",
            "scenic_area": "故宫",
            "source_type": "official" if "官方" in line else "travelogue",
            "raw_text": line,
            "clean_text": line
        })

# 4. 保存为 CSV
df = pd.DataFrame(data_list)
df.to_csv("data/clean_data.csv", index=False, encoding="utf-8-sig")

print("=== 清洗完成！ ===")
print(df)
print("已保存到 data/clean_data.csv")