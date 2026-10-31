import json
import re
import pandas as pd

# 读取清洗后的数据
df = pd.read_csv("data/clean_data.csv")
# 筛选出游记
travelogues = df[df['source_type'] == '游客游记']

if len(travelogues) > 0:
    # 取第一篇真实游记进行解析
    travelogue_text = travelogues.iloc[0]['clean_text']
else:
    travelogue_text = "无游记数据"

def parse_travelogue(text):
    result = {"上午": [], "中午": [], "下午": []}
    sentences = re.split(r'[。！]', text)
    current_time = "上午" 
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if any(word in sentence for word in ["中午", "吃", "午饭"]):
            current_time = "中午"
        elif any(word in sentence for word in ["下午", "傍晚"]):
            current_time = "下午"
        elif "上午" in sentence:
            current_time = "上午"
            
        if current_time in result:
            result[current_time].append(sentence)
    return result

travelogue_result = parse_travelogue(travelogue_text)

with open("outputs/exp3_travelogue_structured.json", "w", encoding="utf-8") as f:
    json.dump(travelogue_result, f, ensure_ascii=False, indent=2)

comparison_text = f"""
=== 官方路线与游客路线差异对比分析 ===
【真实游记样例】{travelogue_text[:50]}...

1. 结构差异：官方路线通常有明确的时间词（上午/中午/下午）引导，结构清晰；游客游记呈流水账式，时间词与叙述高度融合。
2. 内容差异：官方路线侧重景点客观描述；游记包含大量如主观感受与非官方行为。
3. 处理建议：面对游记文本，单纯依靠标点切分效果不佳，建议在后续处理中结合实体识别结果，用时间词+附近POI进行层级划分。
"""
with open("outputs/exp3_comparison_analysis.txt", "w", encoding="utf-8") as f:
    f.write(comparison_text)

print("真实游记解析完成，对比分析已保存。")