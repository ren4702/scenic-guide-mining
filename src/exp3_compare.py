import json
import re

# 模拟一段非常口语化的游客游记（毫无排版可言）
travelogue_text = """
今天去了故宫，人超级多！我们上午从东华门绕过去的，走了好久。
中午在冰窖餐厅吃了炸酱面，有点贵。
下午去看了珍宝馆，然后从神武门出来了。
"""

def parse_travelogue(text):
    # 初始化结果
    result = {
        "上午": [],
        "中午": [],
        "下午": []
    }
    
    # 游客文本没有明显的“上午：”，我们需要用包含时间关键词的句子来切分
    # 我们按句号、感叹号把游记切成一句一句话
    sentences = re.split(r'[。！]', text)
    
    current_time = "上午" # 默认第一句话属于上午
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # 如果句子里包含“中午”、“吃”，说明进入中午阶段
        if any(word in sentence for word in ["中午", "吃", "午饭"]):
            current_time = "中午"
        # 如果句子里包含“下午”、“傍晚”，进入下午阶段
        elif any(word in sentence for word in ["下午", "傍晚"]):
            current_time = "下午"
        # 如果又提到“上午”，切回上午
        elif "上午" in sentence:
            current_time = "上午"
            
        # 把这句话塞进对应的时间段里
        result[current_time].append(sentence)
        
    return result

# 运行
print("=== 游客游记的解析结果 ===")
travelogue_result = parse_travelogue(travelogue_text)
print(json.dumps(travelogue_result, ensure_ascii=False, indent=2))

# 对比报告（简单算一下景点的数量）
print("\n=== 官方路线与游客路线差异对比 ===")
print("官方路线：时间划分明确，景点顺序高度紧凑。")
print("游客路线：受口语表达影响，包含大量如“人超级多”等主观感受，且路线包含“绕路”等非官方行为。")

# --- 补充：将结果保存为文件 ---

# 1. 将游记的解析结果保存为 JSON
with open("outputs/exp3_travelogue_structured.json", "w", encoding="utf-8") as f:
    json.dump(travelogue_result, f, ensure_ascii=False, indent=2)

# 2. 将对比分析的结论保存为 txt 文件
comparison_text = """
=== 官方路线与游客路线差异对比分析 ===
1. 结构差异：官方路线通常有明确的时间词（上午/中午/下午）引导，结构清晰；游客游记呈流水账式，时间词与叙述高度融合。
2. 内容差异：官方路线侧重景点客观描述；游记包含大量如“人超级多”、“绕路”等主观感受与非官方行为。
3. 处理建议：面对游记文本，单纯依靠标点切分效果不佳，建议在后续处理中结合实体识别的结果，用“时间词+附近POI”进行更精准的层级划分。
"""

with open("outputs/exp3_comparison_analysis.txt", "w", encoding="utf-8") as f:
    f.write(comparison_text)

print("\n解析结果和对比分析已保存到 outputs/ 文件夹！")