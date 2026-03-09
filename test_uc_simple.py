#!/usr/bin/env python3
"""
遊戲自動化測試 - 使用 undetected-chromedriver
"""
import sys
import os
import time

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

import undetected_chromedriver as uc

def test_undetected():
    """測試 undetected-chromedriver"""
    print("=" * 60)
    print("測試 undetected-chromedriver")
    print("=" * 60)
    
    try:
        # 簡單配置
        print("\n[1] 啟動 Chrome...")
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        
        driver = uc.Chrome(options=options, headless=False, version_main=None)
        print("✓ Chrome 已啟動")
        
        # 簡單測試
        print("\n[2] 開啟空白頁面...")
        driver.get("about:blank")
        time.sleep(1)
        
        # 打印資訊
        print(f"   URL: {driver.current_url}")
        
        # 關閉
        print("\n[3] 關閉...")
        driver.quit()
        print("✓ 完成")
        
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_undetected()
