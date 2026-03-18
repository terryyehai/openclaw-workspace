#!/usr/bin/env python3
"""
Twitter AI News Scraper - 主動搜尋版
AI 相關熱門內容擷取與分析
"""

import asyncio
import json
import subprocess
from datetime import datetime
from playwright.async_api import async_playwright

KEYWORDS = ["OpenClaw", "Claude AI", "Codex CLI", "Anthropic", "AI agent", "OpenAI GPT", "Cursor AI", "Devin AI"]
COLLECTED_FILE = "/tmp/twitter_ai_news.json"
SEARCH_URL = "https://x.com/explore/tabs/for-you"

def load_posts():
    try:
        with open(COLLECTED_FILE, 'r') as f:
            return json.load(f)
    except: return []

def save_posts(posts):
    with open(COLLECTED_FILE, 'w') as f:
        json.dump(posts[-100:], f, ensure_ascii=False, indent=2)

async def search_and_scrape(page, keyword):
    """搜尋關鍵字並爬取內容"""
    results = []
    
    try:
        # 打開搜尋頁面
        search_url = f"https://x.com/search?q={keyword}&src=typed_query&f=live"
        await page.goto(search_url, timeout=30000)
        await asyncio.sleep(3)
        
        # 滾動載入更多內容
        for _ in range(3):
            await page.evaluate("window.scrollBy(0, 800)")
            await asyncio.sleep(1)
        
        # 取得文章
        articles = await page.query_selector_all("article")
        
        for art in articles[:5]:
            try:
                text = await art.inner_text()
                if text and len(text) > 50:
                    results.append({
                        'keyword': keyword,
                        'text': text[:800],
                        'time': datetime.now().isoformat()
                    })
            except: pass
        
        print(f"  [{keyword}] 找到 {len(results)} 篇")
        
    except Exception as e:
        print(f"  [{keyword}] 錯誤: {e}")
    
    return results

async def main():
    print("=" * 50)
    print("Twitter AI News Scraper - 主動搜尋版")
    print("=" * 50)
    
    collected = load_posts()
    print(f"已收集: {len(collected)} 篇")
    
    all_results = []
    
    async with async_playwright() as p:
        # 連接到現有 Chrome
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("✅ 已連接到 Chrome")
        except Exception as e:
            print(f"❌ 無法連接 Chrome: {e}")
            return
        
        # 建立新分頁進行搜尋
        page = await browser.new_page()
        
        for keyword in KEYWORDS:
            print(f"\n🔍 搜尋: {keyword}")
            results = await search_and_scrape(page, keyword)
            all_results.extend(results)
            await asyncio.sleep(2)  # 避免請求过快
        
        await page.close()
        await browser.close()
    
    # 過濾重複（比对文字前50字）
    new_posts = []
    for p in all_results:
        is_duplicate = any(
            p['text'][:50] in c.get('text', '') 
            for c in collected
        )
        if not is_duplicate:
            new_posts.append(p)
    
    if new_posts:
        collected.extend(new_posts)
        save_posts(collected)
        
        print(f"\n" + "=" * 50)
        print(f"📊 新內容: {len(new_posts)} 篇")
        print("=" * 50)
        
        for i, post in enumerate(new_posts[:5], 1):
            text = post['text'][:120].replace('\n', ' ')
            print(f"\n{i}. [{post['keyword']}] {text}...")
    else:
        print("\n⚠️ 無新內容")

if __name__ == "__main__":
    asyncio.run(main())
