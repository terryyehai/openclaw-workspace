#!/usr/bin/env python3
"""
Twitter Web Bot - 支援 Google 帳號登入
"""

import asyncio
import os
import json
from datetime import datetime
from playwright.async_api import async_playwright

CONFIG_FILE = "/home/terry/.openclaw/twitter/config.json"

class TwitterWebBot:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
    async def init_browser(self, headless=False):
        """初始化瀏覽器"""
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = await self.context.new_page()
        
    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def login_with_google(self, google_email, google_password):
        """透過 Google 登入 Twitter"""
        try:
            await self.page.goto("https://twitter.com/i/flow/login", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # 輸入 Google 帳號
            print(f"輸入 Google 帳號: {google_email}")
            await self.page.fill('input[name="text"]', google_email)
            await self.page.click('button:has-text("Next")')
            await asyncio.sleep(3)
            
            # 檢查是否跳轉到 Google 登入頁面
            current_url = await self.page.url
            
            if "google" in current_url.lower() or "accounts.google" in current_url:
                print("偵測到 Google 登入頁面...")
                
                # 輸入 Google 密碼
                await self.page.fill('input[type="email"]', google_email)
                await self.page.click('button:has-text("Next")')
                await asyncio.sleep(2)
                
                # 輸入密碼
                await self.page.fill('input[type="password"]', google_password)
                await self.page.click('button:has-text("Next")')
                await asyncio.sleep(3)
                
            # 檢查是否需要驗證
            if "verification" in await self.page.url.lower() or "challenge" in await self.page.url.lower():
                print("⚠️ 需要額外驗證（手機驗證碼或 email 驗證）")
                print("請在手機/email 完成驗證，然後回覆「完成」")
                input("按 Enter 繼續...")
            
            # 等待登入完成
            await self.page.wait_for_url("**/home**", timeout=30000)
            print("✅ 登入成功！")
            
            # 儲存會話
            await self.context.storage_state(path=CONFIG_FILE)
            print(f"會話已儲存")
            return True
            
        except Exception as e:
            print(f"登入錯誤: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def post_tweet(self, text):
        """發推文"""
        try:
            await self.page.goto("https://twitter.com/home", wait_until="networkidle")
            await asyncio.sleep(2)
            
            # 點擊發推
            await self.page.click('a[href="/compose/tweet"]')
            await asyncio.sleep(1)
            
            # 輸入推文
            await self.page.fill('div[contenteditable="true"][role="textbox"]', text)
            await asyncio.sleep(0.5)
            
            # 點擊發送
            await self.page.click('button[data-testid="tweetButton"]')
            await asyncio.sleep(2)
            
            print(f"✅ 推文已發送!")
            return {"success": True, "text": text}
            
        except Exception as e:
            print(f"發推錯誤: {e}")
            return {"error": str(e)}
    
    async def load_session(self):
        """載入已有會話"""
        if os.path.exists(CONFIG_FILE):
            try:
                self.context = await self.browser.new_context(
                    storage_state=CONFIG_FILE,
                    viewport={'width': 1280, 'height': 720}
                )
                self.page = await self.context.new_page()
                return True
            except:
                return False
        return False

async def main():
    import sys
    
    bot = TwitterWebBot()
    await bot.init_browser(headless=False)
    
    # 嘗試載入會話
    has_session = await bot.load_session()
    
    if not has_session:
        google_email = "terryyeh.ai@gmail.com"
        google_password = os.environ.get("GOOGLE_PASSWORD")
        
        if not google_password:
            print("請設定環境變數: export GOOGLE_PASSWORD='你的 Google 密碼'")
            return
            
        print(f"使用 Google 帳號登入: {google_email}")
        success = await bot.login_with_google(google_email, google_password)
        
        if not success:
            print("登入失敗")
            await bot.close()
            return
    
    # 發推測試
    test_text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else f"🤖 Test from OpenClaw at {datetime.now().strftime('%H:%M')}"
    
    result = await bot.post_tweet(test_text)
    print(f"結果: {result}")
    
    await asyncio.sleep(2)
    await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
