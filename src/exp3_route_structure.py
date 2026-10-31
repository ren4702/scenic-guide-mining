import json
import re
import pandas as pd

# 读取清洗后的数据
df = pd.read_csv("data/clean_data.csv")
# 筛选出官方路线
official_routes = df[df['source_type'] == '官方路线']

structured_routes = {}
for index, row in official_routes.iterrows():
    text = row['clean_text']
    scenic = row['scenic_area']
    
    route_dict = {"上午": [], "中午": [], "下午": []}
    # 依然用正则按时间词拆分
    parts = re.split(r'(上午|中午|下午)', text)
    for i in range(1, len(parts), 2):
        time_key = parts[i]
        content = parts[i+1].strip()
        content = re.sub(r'^[：:，,。.]+', '', content)
        items = [item.strip() for item in re.split(r'[，。、；\->]', content) if item.strip()]
        if time_key in route_dict:
            route_dict[time_key].extend(items)
            
    # 如果拆分后为空，兜底处理
    if not any(route_dict.values()):
        route_dict["上午"] = [text]
        
    structured_routes[scenic] = route_dict

with open("outputs/exp3_structured_route.json", "w", encoding="utf-8") as f:
    json.dump(structured_routes, f, ensure_ascii=False, indent=2)

print(f"已成功解析 {len(structured_routes)} 个景区的官方路线，保存至 outputs/")