import re
import json
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv("data/clean_data.csv")

data_list = []
pattern = r'(如果|假如|若是|若|建议|可以|要)(.*?)[，,。](建议|可以|则|要)(.*?)[。]'

# 按景区和来源逐条遍历
for index, row in df.iterrows():
    scenic = row['scenic_area']
    text = str(row['clean_text'])
    
    matches = re.findall(pattern, text)
    for match in matches:
        trigger, cond, sug_trigger, sug = match
        cond = cond.strip()
        sug = sug.strip()
        
        # 过滤掉长度超过 30 的废话长句，保证条件建议短小精悍
        if len(cond) > 30 or len(sug) > 30:
            continue
            
        visitor_type = "通用"
        if any(w in cond + sug for w in ["老人", "孩子", "亲子", "爷爷奶奶"]):
            visitor_type = "特殊人群"
        elif any(w in cond + sug for w in ["雨", "天气"]):
            visitor_type = "天气"
            
        data_list.append({
            "condition_id": f"c_{len(data_list)+1:03d}",
            "scenic_area": scenic,  # 【核心修复】绑定景区
            "condition_type": visitor_type,
            "condition_text": cond,
            "suggestion_text": sug,
            "visitor_type": visitor_type
        })

df_out = pd.DataFrame(data_list)
if len(df_out) > 0:
    df_out = df_out.drop_duplicates(subset=['scenic_area', 'condition_text', 'suggestion_text'])
    
df_out.to_json("outputs/exp5_condition_mapping.json", orient="records", force_ascii=False, indent=2)
df_out.to_csv("outputs/exp5_condition_mapping.csv", index=False, encoding="utf-8-sig")

print(f"提取并去重后得到 {len(df_out)} 条条件建议。")