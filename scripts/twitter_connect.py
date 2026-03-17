#!/usr/bin/env python3
"""
Twitter Web Bot - 使用已登入的 Chrome 會話
"""

import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    import sys
    
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else f"🤖 Test from OpenClaw!"
    
    async with async_playwright() as p:
        # 連接已啟動的 Chrome
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        
        # 取得第一個 context
        contexts = browser.contexts
        if not contexts:
            print("❌ 沒有找到 Chrome 會話")
            return
        
        context = contexts[0]
        page = await context.new_page()
        
        try:
            # 確保在 Twitter
            await page.goto("https://twitter.com/home", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # 點擊發推
            await page.click('a[href="/compose/tweet"]')
            await asyncio.sleep(1)
            
            # 輸入推文
            await page.fill('div[contenteditable="true"][role="textbox"]', text)
            await asyncio.sleep(0.5)
            
            # 點擊發送
            await page.click('button[data-testid="tweetButton"]')
            await asyncio.sleep(2)
            
            print(f"✅ 推文已發送: {text}")
            
        except Exception as e:
            print(f"❌ 錯誤: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
