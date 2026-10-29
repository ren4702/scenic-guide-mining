import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 里的密钥
load_dotenv()

# 连接 DeepSeek
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

print("正在呼叫 DeepSeek，请稍等...")

# 发送请求
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "请用一句话向我打个招呼，并告诉我你是什么模型。"}
    ]
)

print("\n=== DeepSeek 回复 ===")
print(response.choices[0].message.content)
print("=====================")