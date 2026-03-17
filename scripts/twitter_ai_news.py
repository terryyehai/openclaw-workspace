#!/usr/bin/env python3
"""
Twitter AI News Scraper - 每4小時爬文
AI 相關熱門內容擷取與分析
"""

import asyncio
import json
import subprocess
from datetime import datetime
from playwright.async_api import async_playwright

KEYWORDS = ["OpenClaw", "Claude AI", "Codex CLI", "Anthropic", "AI agent", "OpenAI GPT"]
COLLECTED_FILE = "/tmp/twitter_ai_news.json"

def load_posts():
    try:
        with open(COLLECTED_FILE, 'r') as f:
            return json.load(f)
    except: return []

def save_posts(posts):
    with open(COLLECTED_FILE, 'w') as f:
        json.dump(posts[-100:], f, ensure_ascii=False, indent=2)

def get_chrome_pages():
    """取得 Chrome 分頁"""
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:9222/json'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except: return []

async def scrape_from_page(page):
    """從現有分頁爬取內容"""
    results = []
    
    try:
        # 滾動載入內容
        for _ in range(2):
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(0.5)
        
        # 取得文章
        articles = await page.query_selector_all("article")
        
        for art in articles[:8]:
            try:
                # 取得文字
                text = await art.inner_text()
                if text and len(text) > 50:
                    results.append({
                        'text': text[:800],
                        'time': datetime.now().isoformat()
                    })
            except: pass
    except Exception as e:
        print(f"Scraping error: {e}")
    
    return results

async def main():
    print("=" * 50)
    print("Twitter AI News Scraper")
    print("=" * 50)
    
    collected = load_posts()
    all_results = []
    
    # 取得 Chrome 分頁
    pages = get_chrome_pages()
    x_pages = [p for p in pages if 'x.com' in p.get('url','')]
    
    print(f"找到 {len(x_pages)} 個 X 分頁")
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        
        for ctx in browser.contexts:
            for page in ctx.pages:
                url = page.url
                if 'x.com' in url and ('home' in url or 'search' in url):
                    print(f"爬取: {url[:40]}...")
                    
                    results = await scrape_from_page(page)
                    all_results.extend(results)
        
        await browser.close()
    
    # 過濾重複
    new_posts = [p for p in all_results 
                 if not any(p['text'][:50] in c.get('text','') for c in collected)]
    
    if new_posts:
        collected.extend(new_posts)
        save_posts(collected)
        
        print(f"\n📊 新內容: {len(new_posts)} 篇")
        
        # 翻譯和研究清單
        print("\n" + "=" * 50)
        print("📋 工作研究清單")
        print("=" * 50)
        
        for i, post in enumerate(new_posts[:3], 1):
            text = post['text'][:100]
            print(f"\n{i}. {text}...")
    else:
        print("\n無新內容")

if __name__ == "__main__":
    asyncio.run(main())
