import os
import json
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# 1. 初始化大模型
load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 2. 读取实验一清洗好的数据
df = pd.read_csv("data/clean_data.csv")

# 3. 定义提示词（Prompt）
prompt = """
你是一个自然语言处理专家。请从下面这段景区游览文本中，提取出三种实体：
1. POI（景点名称，如：太和殿、西湖）
2. TRANSPORT（交通方式，如：步行、缆车、大巴）
3. TIME（时间节点，如：上午、下午、8点）

请严格按照以下 JSON 数组格式输出，不要输出任何其他多余的解释：
[
  {"entity": "提取的词", "type": "类型(POI/TRANSPORT/TIME)"}
]

文本内容：
"""

# 4. 遍历数据，让大模型逐条分析
results = []
print("开始调用 DeepSeek 进行实体识别...\n")


for index, row in df.iterrows():
    text = row['clean_text']
    print(f"正在分析第 {index+1} 条文本...")
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt + text}],
        temperature=0  # 设为0，让模型输出最稳定
    )
    
    # 获取模型的回答
    answer = response.choices[0].message.content
    # 去掉可能包含的 Markdown 标记 (```json ... ```)
    answer = answer.replace("```json", "").replace("```", "").strip()
    
    try:
        # 把字符串转成 Python 列表
        entities = json.loads(answer)
        # 加上来源信息
        for e in entities:
            e['doc_id'] = row['doc_id']
            e['scenic_area'] = row['scenic_area']
            results.append(e)
    except Exception as e:
        print(f"解析失败，模型输出为：{answer}")

# 5. 保存为 JSON 文件
with open("outputs/exp2_entities.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n=== 实体识别完成！ ===")
print(f"共提取了 {len(results)} 个实体，已保存到 outputs/exp2_entities.json")