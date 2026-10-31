import json
import re
import pandas as pd

# 读取真实游记
df = pd.read_csv("data/clean_data.csv")
travelogues = df[df['source_type'] == '游客游记']

pronouns = ["它", "他", "她", "这里", "那里", "这", "那"]
detected_list = []

for index, row in travelogues.iterrows():
    text = row['clean_text']
    for p in pronouns:
        if p in text:
            detected_list.append({
                "doc_id": row['doc_id'],
                "scenic_area": row['scenic_area'],
                "pronoun": p,
                "sentence_text": text[:50] + "..." # 截取前50字作为证据
            })

with open("outputs/exp4_pronoun_detection.json", "w", encoding="utf-8") as f:
    json.dump(detected_list, f, ensure_ascii=False, indent=2)

# 生成一个简易的消解文本供展示
sample_text = travelogues.iloc[0]['clean_text'] if len(travelogues) > 0 else ""
resolved_text = sample_text.replace("它", "[该景点]").replace("那里", "[该地点]")

with open("outputs/exp4_resolved_text.txt", "w", encoding="utf-8") as f:
    f.write("【原始文本】\n" + sample_text + "\n\n【消解后文本】\n" + resolved_text)
    
eval_report = f"=== 共指消解检测报告 ===\n在 {len(travelogues)} 篇游记中，共检测到 {len(detected_list)} 处代词。\n"
eval_report += "已使用规则进行替换，详见 exp4_resolved_text.txt。"
with open("outputs/exp4_evaluation.txt", "w", encoding="utf-8") as f:
    f.write(eval_report)

print(f"共检测到 {len(detected_list)} 处代词，已保存结果。")