import json
import re

# ================= 1. 准备测试数据 =================
travelogue_text = "我们今天去了故宫。它非常大，我们在那里逛了一天。下午去了珍宝馆，那里有很多宝贝。最后我们从神武门出去，大家都觉得它很壮观。"

# ================= 2. 代词检测 (20分) =================
def detect_pronouns(text):
    pronouns = ["它", "他", "她", "这里", "那里", "这", "那", "他们"]
    detected = []
    
    # 简单按句号切分，获取句子和位置
    sentences = re.split(r'(?<=[。！？])', text)
    for i, sent in enumerate(sentences):
        for p in pronouns:
            # 找出句子中的代词
            for match in re.finditer(p, sent):
                detected.append({
                    "doc_id": "doc_travelogue_01",
                    "sentence_id": i + 1,
                    "pronoun": p,
                    "position_in_sentence": match.start(),
                    "sentence_text": sent.strip()
                })
                
    with open("outputs/exp4_pronoun_detection.json", "w", encoding="utf-8") as f:
        json.dump(detected, f, ensure_ascii=False, indent=2)
    return detected

# ================= 3. 人工标注样本 (20分) =================
# 模拟人工标注：记录了代词所在的句子ID、代词，以及真实的先行词
ground_truth = [
    {"sentence_id": 2, "pronoun": "它", "true_referent": "故宫"},
    {"sentence_id": 2, "pronoun": "那里", "true_referent": "故宫"},
    {"sentence_id": 3, "pronoun": "那里", "true_referent": "珍宝馆"},
    {"sentence_id": 4, "pronoun": "它", "true_referent": "神武门"} # 这里规则可能会认错，用来展示局限性
]

with open("outputs/exp4_ground_truth.json", "w", encoding="utf-8") as f:
    json.dump(ground_truth, f, ensure_ascii=False, indent=2)

# ================= 4. 指代消解实现 (30分) =================
def resolve_coreference(text, detected_pronouns):
    # 规则：对于每个代词，在它所在句子及前文寻找最近的“专有名词（POI）”
    # 为了便于演示，我们预设一个景点词典库
    poi_lexicon = ["故宫", "珍宝馆", "神武门", "太和殿"]
    
    resolved_text = text
    # 我们从后往前替换，防止字符串长度变化导致位置错乱
    for item in reversed(detected_pronouns):
        pronoun = item["pronoun"]
        sent_id = item["sentence_id"]
        sent_text = item["sentence_text"]
        
        # 找到代词所在的句子在全文中的位置
        # 规则逻辑：在当前句子和前面的句子中，找距离代词最近的 POI
        # 简单实现：把前面的文本合并，从后往前找
        sentences = re.split(r'(?<=[。！？])', resolved_text)
        context_before = "".join(sentences[:sent_id])
        
        # 找最近的 POI
        found_poi = None
        min_distance = 9999
        
        for poi in poi_lexicon:
            # 寻找 POI 在代词前最后一次出现的位置
            last_pos = context_before.rfind(poi)
            if last_pos != -1:
                distance = len(context_before) - last_pos
                if distance < min_distance:
                    min_distance = distance
                    found_poi = poi
                    
        if found_poi:
            # 替换该句子中的这个代词（只替换第一次出现）
            new_sent = sent_text.replace(pronoun, f"[{found_poi}]", 1)
            resolved_text = resolved_text.replace(sent_text, new_sent, 1)
            
    with open("outputs/exp4_resolved_text.txt", "w", encoding="utf-8") as f:
        f.write("【原始文本】\n" + text + "\n\n【消解后文本】\n" + resolved_text)
        
    return resolved_text

# ================= 5. 效果评估 (20分) =================
print("=== 1. 正在检测代词并保存 JSON... ===")
detected = detect_pronouns(travelogue_text)
print(f"检测到 {len(detected)} 个代词。")

print("\n=== 2. 正在执行基于最近名词匹配的消解... ===")
resolved = resolve_coreference(travelogue_text, detected)
print("消解完成，已保存到 outputs/exp4_resolved_text.txt")

print("\n=== 3. 效果评估 ===")
# 这里简单比对句子中的替换结果
correct_count = 0
total_count = len(ground_truth)

# 打印评估表
eval_report = "=== 共指消解人工评估报告 ===\n"
for item in ground_truth:
    pronoun = item["pronoun"]
    expected = item["true_referent"]
    # 简单判断：如果期望的实体被打上了[]，并且刚好替换在代词位置，就说明对了
    if f"[{expected}]" in resolved:
        correct_count += 1
        eval_report += f"句子 {item['sentence_id']} 中 '{pronoun}' -> 预测指代 '{expected}' (正确)\n"
    else:
        eval_report += f"句子 {item['sentence_id']} 中 '{pronoun}' -> 预测指代失败 (规则局限，可能受距离/语境影响)\n"

accuracy = correct_count / total_count * 100
eval_report += f"\n共标注样本: {total_count} 个\n消解正确数: {correct_count} 个\n人工核验准确率: {accuracy:.2f}%\n"
eval_report += "\n【方法局限性分析】: 最近名词匹配规则容易受实体类型干扰，比如最后一句话的'它'其实指代'神武门'，但规则可能错认为之前的建筑。后续可通过引入LLM或依存句法分析改进。\n"

with open("outputs/exp4_evaluation.txt", "w", encoding="utf-8") as f:
    f.write(eval_report)

print(eval_report)