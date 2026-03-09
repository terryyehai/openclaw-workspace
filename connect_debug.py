#!/usr/bin/env python3
"""
連接到已啟動的 Chrome (使用 Remote Debugging)
"""
import sys
import os

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

from playwright.sync_api import sync_playwright

def connect_to_chrome():
    """連接到已存在的 Chrome"""
    print("=" * 60)
    print("連接到 Chrome (Remote Debugging)")
    print("=" * 60)
    
    playwright = sync_playwright().start()
    
    try:
        # 連接到已存在的 Chrome
        browser = playwright.chromium.connect_over_cdp(
            "http://127.0.0.1:18800"
        )
        print("✓ 已連接到 Chrome!")
        
        # 列出所有分頁
        print("\n可用分頁:")
        for i, page in enumerate(browser.contexts[0].pages):
            print(f"  [{i}] {page.url[:60]}...")
        
        # 創建新分頁
        page = browser.contexts[0].new_page()
        
        # 前往遊戲
        print("\n[1] 前往遊戲測試工具...")
        page.goto("https://gp001-qa1-simulation.xwautc.online/index")
        page.wait_for_timeout(3000)
        
        print("[2] 截圖...")
        page.screenshot(path="/tmp/game_connected.png")
        
        print("[3] 環境資訊:")
        print(f"   WebDriver: {page.evaluate('navigator.webdriver')}")
        
        print("\n" + "=" * 60)
        print("✓ 請在瀏覽器中操作遊戲")
        print("   按 Enter 關閉連線")
        print("=" * 60)
        
        input()
        
        # 關閉分頁
        page.close()
        browser.close()
        
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    playwright.stop()

if __name__ == "__main__":
    connect_to_chrome()
