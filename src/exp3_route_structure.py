import json
import re

# 模拟一段稍微复杂一点的官方路线文本（为了演示效果，我们直接用字符串）
# 在真实作业中，这里应该去读取 data/clean_data.csv 里的官方路线
route_text = """
故宫经典一日游路线：
上午：从午门进入，参观太和殿、中和殿、保和殿。
中午：在冰窖餐厅用餐，稍作休息。
下午：游览乾清宫、交泰殿，最后从神武门离开。
"""

def parse_route(text):
    # 1. 初始化结果字典
    structured_route = {
        "上午": [],
        "中午": [],
        "下午": []
    }
    
    # 2. 按照“上午”、“中午”、“下午”把文本切成三块
    # 使用正则表达式，把时间词作为分割线
    # split_text 切割后会变成：['故宫经典一日游路线：\n', '：从午门进入...\n', '：在冰窖餐厅...\n', '：游览乾清宫...\n']
    parts = re.split(r'(上午|中午|下午)', text)
    
    # 3. 遍历切分后的文本，把对应的内容塞进对应的时间段
    # parts[0] 是第一个时间词之前的内容，我们不要
    # parts[1] 是时间词，parts[2] 是该时间词后的内容，以此类推
    for i in range(1, len(parts), 2):
        time_key = parts[i]          # 当前时间词（上午/中午/下午）
        content = parts[i+1].strip() # 对应的文本内容
        
        # 去掉内容开头的冒号或标点
        content = re.sub(r'^[：:，,。.]+', '', content)
        
        # 4. 把内容里的景点提取出来（这里用简单的标点符号分割作为演示）
        # 按逗号、句号、顿号切分，去掉空字符串
        items = [item.strip() for item in re.split(r'[，。、；]', content) if item.strip()]
        
        structured_route[time_key] = items
        
    return structured_route

# 运行解析函数
result = parse_route(route_text)

# 打印出来看看
print("=== 解析结果 ===")
print(json.dumps(result, ensure_ascii=False, indent=2))

# 保存到 outputs 文件夹
with open("outputs/exp3_structured_route.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n解析完成，已保存到 outputs/exp3_structured_route.json")