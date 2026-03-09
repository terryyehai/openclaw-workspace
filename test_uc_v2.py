#!/usr/bin/env python3
"""
遊戲自動化測試 - 使用 undetected-chromedriver + webdriver-manager
"""
import sys
import os
import time

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def test_undetected():
    """測試 undetected-chromedriver"""
    print("=" * 60)
    print("測試 undetected-chromedriver")
    print("=" * 60)
    
    try:
        # 使用 webdriver-manager 自動下載正確的 ChromeDriver
        print("\n[1] 安裝正確版本的 ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        print(f"   ChromeDriver 路徑: {service.path}")
        
        # 啟動 Chrome
        print("\n[2] 啟動 Chrome...")
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = uc.Chrome(options=options, service=service, headless=False)
        print("✓ Chrome 已啟動")
        
        # 測試
        print("\n[3] 開啟遊戲測試工具...")
        driver.get("https://gp001-qa1-simulation.xwautc.online/index")
        time.sleep(3)
        
        # 截圖
        driver.save_screenshot("/tmp/uc_game.png")
        print("   截圖: /tmp/uc_game.png")
        
        # 環境資訊
        print("\n[4] 環境資訊:")
        print(f"   WebDriver: {driver.execute_script('return navigator.webdriver')}")
        
        print("\n" + "=" * 60)
        print("請在瀏覽器中操作，按 Enter 關閉")
        print("=" * 60)
        
        input()
        
        driver.quit()
        print("\n✓ 完成")
        
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_undetected()
