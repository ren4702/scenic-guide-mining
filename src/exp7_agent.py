import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

os.makedirs("outputs", exist_ok=True)

# ================= 1. 知识图谱查询工具 =================
def query_knowledge_graph(scenic_area, visitor_type):
    print(f"  [工具调用] 正在查询图谱：景区={scenic_area}, 游客类型={visitor_type}")
    
    try:
        with open("outputs/exp5_condition_mapping.json", "r", encoding="utf-8") as f:
            cond_data = json.load(f)
    except Exception:
        cond_data = []
        
    try:
        with open("outputs/exp3_structured_route.json", "r", encoding="utf-8") as f:
            all_routes = json.load(f)
    except Exception:
        all_routes = {}

    target_route = all_routes.get(scenic_area, all_routes.get("故宫", {}))

    matched_suggestions = []
    for item in cond_data:
        # 【核心修复】1. 必须是指定景区的，或者完全通用的
        # 2. 条件或建议中必须命中用户的游客类型（或完全通用）
        is_same_scenic = (item.get("scenic_area") == scenic_area)
        is_visitor_match = (visitor_type in item.get("condition_text", "") or 
                            visitor_type in item.get("suggestion_text", "") or 
                            item.get("visitor_type") == "通用")
        
        if is_same_scenic and is_visitor_match:
            matched_suggestions.append(item.get("suggestion_text", ""))

    # 去重并截取前 3 条最核心的建议
    matched_suggestions = list(set(matched_suggestions))[:3]

    result = {
        "selected_scenic_area": scenic_area,
        "route": target_route,
        "suggestions": matched_suggestions
    }
    return json.dumps(result, ensure_ascii=False)

# ================= 2. Agent 核心推理流程 =================
def run_agent(user_query, task_id):
    print(f"\n[{task_id}] 用户输入: {user_query}")
    
    trace_record = {
        "task_id": task_id,
        "user_query": user_query,
        "thought_intent": None,
        "action_tool_call": None,
        "observation_tool_result": None,
        "final_answer": None
    }

    # 步骤 1：意图解析 (Thought)
    print("[Agent 思考] 正在解析用户意图...")
    parse_prompt = f"""
    请从用户的输入中提取关键约束。
    用户输入："{user_query}"
    请以严格的 JSON 格式输出，不要输出其他废话：
    {{"scenic_area": "景区名称", "visitor_type": "游客类型(如老人/亲子/情侣/通用)", "duration": "游玩时长"}}
    """
    response1 = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": parse_prompt}],
        temperature=0
    )
    intent_json_str = response1.choices[0].message.content.replace("```json", "").replace("```", "").strip()
    print(f"  [解析结果] {intent_json_str}")
    
    try:
        intent = json.loads(intent_json_str)
    except:
        intent = {"scenic_area": "故宫", "visitor_type": "通用", "duration": "一天"}
    
    trace_record["thought_intent"] = intent

    # 步骤 2：调用工具 (Action & Observation)
    trace_record["action_tool_call"] = f"query_knowledge_graph(scenic_area='{intent.get('scenic_area')}', visitor_type='{intent.get('visitor_type')}')"
    kg_data = query_knowledge_graph(intent.get("scenic_area", "故宫"), intent.get("visitor_type", "通用"))
    trace_record["observation_tool_result"] = json.loads(kg_data)
    
    # 步骤 3：生成回答 (Final Answer)
    print("[Agent 行动] 根据图谱查询结果生成最终建议...")
    generate_prompt = f"""
    你是一个专业的旅游规划助手。
    用户需求：{user_query}
    提取的约束条件：{intent_json_str}
    从知识图谱中查询到的信息：{kg_data}
    
    请根据以上信息，为用户生成一份合理的行程安排和游览建议。要求语言自然，必须包含图谱中查到的建议和路线。
    """
    response2 = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": generate_prompt}],
        temperature=0.7
    )
    
    final_answer = response2.choices[0].message.content
    trace_record["final_answer"] = final_answer
    print("\n=== 最终旅游规划方案 ===")
    print(final_answer[:150] + "......\n(完整内容见输出文件)")
    
    return trace_record

# ================= 3. 功能测试与成果输出 =================
if __name__ == "__main__":
    # 覆盖 3 个景区的测试场景
    test_queries = [
        ("测试场景1（故宫-老人）", "我想带爷爷奶奶去故宫玩一天，怎么安排比较好？"),
        ("测试场景2（黄山-体力不佳）", "我平时不怎么锻炼，去黄山有什么省力的路线和建议吗？"),
        ("测试场景3（西湖-下雨）", "下雨天去西湖，怎么逛比较合适？")
    ]
    
    all_traces = []
    for task_id, query in test_queries:
        record = run_agent(query, task_id)
        all_traces.append(record)

    # 保存结构化结果
    with open("outputs/exp7_agent_traces.json", "w", encoding="utf-8") as f:
        json.dump(all_traces, f, ensure_ascii=False, indent=2)
        
    # 保存 Markdown 证据
    md_content = "# 实验七：Agent 工具调用记录与结果证据\n\n"
    for trace in all_traces:
        md_content += f"## {trace['task_id']}\n"
        md_content += f"**用户输入:** {trace['user_query']}\n\n"
        md_content += f"**1. 意图解析(Thought):**\n```json\n{json.dumps(trace['thought_intent'], ensure_ascii=False, indent=2)}\n```\n"
        md_content += f"**2. 工具调用(Action):** `{trace['action_tool_call']}`\n"
        md_content += f"**3. 观察结果(Observation):**\n```json\n{json.dumps(trace['observation_tool_result'], ensure_ascii=False, indent=2)}\n```\n"
        md_content += f"**4. 最终回答(Final Answer):**\n{trace['final_answer']}\n\n"
        md_content += "---\n"

    with open("outputs/exp7_agent_evidence.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print("\n=========================================")
    print("✅ 所有测试已完成！")
    print("证据已保存至 outputs/exp7_agent_evidence.md")
    print("=========================================")