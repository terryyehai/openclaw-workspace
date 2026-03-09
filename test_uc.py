#!/usr/bin/env python3
"""
遊戲自動化測試 - 使用 undetected-chromedriver
專為繞過反機器人偵測設計
"""
import sys
import os

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

import undetected_chromedriver as uc

def test_undetected():
    """測試 undetected-chromedriver"""
    print("=" * 60)
    print("遊戲自動化測試 - undetected-chromedriver")
    print("=" * 60)
    
    try:
        # 啟動 undetected Chrome
        print("\n[1] 啟動 Chrome...")
        driver = uc.Chrome(
            headless=False,  # 顯示瀏覽器視窗
            version_main=None,  # 自動偵測版本
        )
        
        print("✓ Chrome 已啟動 (undetected mode)")
        
        # 前往遊戲測試工具
        print("\n[2] 前往遊戲測試工具...")
        driver.get("https://gp001-qa1-simulation.xwautc.online/index")
        
        print("[3] 等待頁面載入...")
        import time
        time.sleep(3)
        
        # 截圖
        driver.save_screenshot("/tmp/uc_login.png")
        print("[4] 截圖: /tmp/uc_login.png")
        
        # 打印環境資訊
        print("\n[5] 環境資訊:")
        print(f"   WebDriver: {driver.execute_script('return navigator.webdriver')}")
        
        print("\n" + "=" * 60)
        print("請在瀏覽器中操作遊戲")
        print("按 Enter 關閉瀏覽器")
        print("=" * 60)
        
        input()
        
        driver.quit()
        print("\n✓ 完成!")
        
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_undetected()
