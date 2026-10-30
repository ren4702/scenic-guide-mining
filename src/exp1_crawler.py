import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

# 1. 准备你要爬取的网页链接列表（这里以微信文章为例，你可以换成任何游记的链接）
# 你也可以找官方的路线介绍网页，混在一起
url_list = [
    {
        "景区": "黄山", 
        "文本类型": "游客游记", 
        "来源": "github", 
        "url": "https://www.greentourasia.com/video/xihushijing-OsZVWE" 
    }

    # 你可以照着格式继续往下加，至少凑够3个景区，每个景区1官1游（共6个链接以上最好）
]

# 伪装成浏览器，防止被网站直接拒绝（这是爬虫的基本礼仪）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def crawl_page(item):
    print(f"正在爬取: {item['景区']} - {item['url']}")
    try:
        # 发送网络请求获取网页内容
        response = requests.get(item['url'], headers=headers, timeout=10)
        response.encoding = 'utf-8' # 统一编码，防止中文乱码
        
        # 如果网页返回状态码不是 200，说明被拦截或链接错了
        if response.status_code != 200:
            print(f"  请求失败，状态码: {response.status_code}")
            return None

        # 使用 BeautifulSoup 解析网页结构
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 针对微信文章：正文通常在一个 id="js_content" 的 div 里
        content_div = soup.find('div', id='js_content')
        
        # 如果不是微信文章，或者没找到这个 div，我们就退而求其次，抓取网页里所有的 <p> 段落
        if not content_div:
            paragraphs = soup.find_all('p')
        else:
            paragraphs = content_div.find_all('p')
            
        # 把所有的段落拼接成一段长文本
        raw_text = ""
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                raw_text += text + "\n"
                
        # 如果抓出来还是空的，说明网页是动态加载的，或者结构不同
        if len(raw_text) < 50:
            print("  未抓取到有效正文，可能是动态网页或结构不匹配。")
            return None

        # 在文本里人为加点 HTML 标签和乱码，为了实验一后面的“数据清洗”有东西可洗
        raw_text = "<div>" + raw_text + "</div> [系统提示] 爬虫抓取成功！"
        
        return {
            "景区": item["景区"],
            "文本类型": item["文本类型"],
            "来源": item["来源"],
            "原始内容": raw_text
        }
        
    except Exception as e:
        print(f"  爬取出错: {e}")
        return None

# 主程序
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    results = []
    
    for item in url_list:
        data = crawl_page(item)
        if data:
            results.append(data)
        # 停顿 1 秒，防止请求过快被封 IP（这叫爬虫的“休眠”）
        time.sleep(1)

    # 保存为 CSV 文件
    if results:
        df = pd.DataFrame(results)
        df.to_csv("data/raw_dataset.csv", index=False, encoding="utf-8-sig")
        print(f"\n成功爬取 {len(df)} 条数据，已保存至 data/raw_dataset.csv")
        print("现在你可以去运行 python src/exp1_preprocess.py 进行清洗了！")
    else:
        print("\n所有链接爬取失败。请检查网络，或者换几个网页链接试试。")