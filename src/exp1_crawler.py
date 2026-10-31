import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# 1. 自动读取外部的链接列表文件
try:
    df_urls = pd.read_csv("data/urls.csv")
    url_list = df_urls.to_dict(orient="records")
    print(f"成功读取到 {len(url_list)} 条待爬取链接。")
except Exception as e:
    print(f"读取 data/urls.csv 失败，请检查文件是否存在。错误: {e}")
    exit()

# 伪装成浏览器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def crawl_page(item):
    url = item['url']
    print(f"\n正在爬取: {item['景区']} - {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # 使用 apparent_encoding 自动识别编码，防止某些老网站（如新浪）乱码
        response.encoding = response.apparent_encoding
        
        if response.status_code != 200:
            print(f"  [失败] 状态码: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 通用正文提取策略
        content_div = (
            soup.find('article') or 
            soup.find('div', class_='content') or 
            soup.find('div', id='content') or
            soup.find('div', class_='post-content') or
            soup.find('div', class_='article-content')
        )
        
        paragraphs = []
        if content_div:
            paragraphs = content_div.find_all(['p', 'div'])
        else:
            paragraphs = soup.find_all('p')
        
        if not paragraphs or sum(len(p.get_text(strip=True)) for p in paragraphs) < 50:
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                raw_text = meta_desc['content']
            else:
                raw_text = ""
        else:
            raw_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        if len(raw_text) < 50:
            print("  [跳过] 未抓取到有效正文（可能是动态网页或结构不匹配）。")
            return None

        # 保留噪声供后续清洗
        raw_text = "<div>" + raw_text + "</div> [爬虫提示] 抓取成功"
        
        print(f"  [成功] 抓取字数: {len(raw_text)}")
        return {
            "景区": item["景区"],
            "文本类型": item["文本类型"],
            "来源": item["来源"],
            "url": url,           # 新增：把 url 保存下来，方便溯源和去重
            "原始内容": raw_text
        }
        
    except Exception as e:
        print(f"  [报错] {e}")
        return None

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    results = []
    
    # 2. 自动循环爬取
    for item in url_list:
        data = crawl_page(item)
        if data:
            results.append(data)
        
        # 自动休眠，防封IP
        time.sleep(2)

    # 3. 追加并真正去重保存到 CSV
    if results:
        df_new = pd.DataFrame(results)
        
        file_path = "data/raw_dataset.csv"
        if os.path.exists(file_path):
            df_old = pd.read_csv(file_path)
            # 合并新旧数据
            df_all = pd.concat([df_old, df_new], ignore_index=True)
            # 真正的去重：根据 url 列去掉完全重复的记录
            df_all = df_all.drop_duplicates(subset=['url'], keep='last')
            df_all.to_csv(file_path, index=False, encoding="utf-8-sig")
        else:
            df_new.to_csv(file_path, index=False, encoding="utf-8-sig")
            
        print(f"\n✅ 本次运行成功爬取 {len(df_new)} 条数据，合并去重后总计 {len(df_all) if os.path.exists(file_path) else len(df_new)} 条。")
        print(f"已自动保存至 {file_path}，你可以去运行实验一清洗代码了！")
    else:
        print("\n❌ 本轮所有链接均未抓取到有效正文，请检查 urls.csv 里的链接。")