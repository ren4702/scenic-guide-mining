import json
import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# 解决中文乱码
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

os.makedirs("outputs", exist_ok=True)

# ================= 1. 多源数据读取 =================
print("正在读取多源数据...")

# 读取实验三的官方路线结构（如果没有，用默认数据兜底）
route_file = "outputs/exp3_structured_route.json"
if os.path.exists(route_file):
    with open(route_file, "r", encoding="utf-8") as f:
        route_data = json.load(f)
else:
    route_data = {"上午": ["太和殿", "保和殿"], "中午": ["冰窖餐厅"], "下午": ["乾清宫"]}

# 读取实验五的条件建议（如果没有，用默认数据兜底）
cond_file = "outputs/exp5_condition_mapping.json"
if os.path.exists(cond_file):
    cond_data = pd.read_json(cond_file).to_dict(orient="records")
else:
    cond_data = [{"condition_text": "带老人", "suggestion_text": "租借轮椅", "visitor_type": "特殊人群"}]

# ================= 2. 知识图谱模式设计与构建 =================
# 创建一个有向图
G = nx.DiGraph()

# 添加核心景区节点
scenic = "故宫"
G.add_node(scenic, type="景区")

# 融合实验三：遍历多个景区的路线结构
for scenic_name, time_dict in route_data.items():
    # 添加景区节点
    G.add_node(scenic_name, type="景区")
    
    for time_slot, pois in time_dict.items():
        time_node_name = f"{scenic_name}_{time_slot}" # 区分不同景区的上午
        G.add_node(time_node_name, type="时间")
        G.add_edge(scenic_name, time_node_name, relation="包含时间")
        
        for i, poi in enumerate(pois):
            G.add_node(poi, type="景点/活动")
            G.add_edge(time_node_name, poi, relation="发生于")
            
            # 如果是指定序列，增加前后顺序边
            if i > 0:
                G.add_edge(pois[i-1], poi, relation="游览顺序")

# 融合实验五：条件与建议
for item in cond_data:
    cond_text = item["condition_text"]
    sug_text = item["suggestion_text"]
    v_type = item["visitor_type"]
    
    # 为条件创建一个特征节点
    G.add_node(v_type, type="游客特征")
    G.add_edge(scenic, v_type, relation="适用条件")
    
    # 为建议创建一个节点
    G.add_node(sug_text, type="游览建议")
    G.add_edge(v_type, sug_text, relation="触发建议")

# ================= 3. 导出图谱结构化文件 =================
# 导出节点和边为 CSV（满足任务书要求的可检查结构化文件）
nodes_data = [{"id": n, "type": d["type"]} for n, d in G.nodes(data=True)]
edges_data = [{"source": u, "target": v, "relation": d["relation"]} for u, v, d in G.edges(data=True)]

pd.DataFrame(nodes_data).to_csv("outputs/exp6_nodes.csv", index=False, encoding="utf-8-sig")
pd.DataFrame(edges_data).to_csv("outputs/exp6_edges.csv", index=False, encoding="utf-8-sig")
print("图谱结构已导出至 outputs/exp6_nodes.csv 和 exp6_edges.csv")

# ================= 4. 图谱可视化 =================
plt.figure(figsize=(16, 10)) # 1. 把画布调大，字才不会挤在一起

# 布局算法（k值调大一点，让节点散开）
pos = nx.spring_layout(G, k=2.0, seed=42)

# 按节点类型给不同颜色
node_colors = []
for n, d in G.nodes(data=True):
    if d["type"] == "景区": node_colors.append("#FF6B6B")     # 红色
    elif d["type"] == "时间": node_colors.append("#4ECDC4")   # 蓝绿色
    elif d["type"] == "景点/活动": node_colors.append("#FFE66D") # 黄色
    elif d["type"] == "游客特征": node_colors.append("#1A535C") # 深色
    else: node_colors.append("#A2D2FF")                     # 浅蓝色

# 画节点
nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2500, alpha=0.9)
# 画边
nx.draw_networkx_edges(G, pos, edge_color="gray", arrows=True, arrowsize=20, width=1.5, alpha=0.6)
# 画文字标签
nx.draw_networkx_labels(G, pos, font_size=9, font_family="SimHei")

# 添加图例
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w', label='景区', markerfacecolor='#FF6B6B', markersize=15),
    plt.Line2D([0], [0], marker='o', color='w', label='时间', markerfacecolor='#4ECDC4', markersize=15),
    plt.Line2D([0], [0], marker='o', color='w', label='景点', markerfacecolor='#FFE66D', markersize=15),
    plt.Line2D([0], [0], marker='o', color='w', label='建议/特征', markerfacecolor='#A2D2FF', markersize=15)
]
plt.legend(handles=legend_elements, loc="upper right")

# 2. 修改标题，体现多源融合！
plt.title("多景区程序性知识图谱（NetworkX 构建）", fontsize=18)
plt.axis("off")
plt.tight_layout()

plt.savefig("outputs/exp6_knowledge_graph.png", dpi=300)
print("=== 图谱可视化已保存至 outputs/exp6_knowledge_graph.png ===")