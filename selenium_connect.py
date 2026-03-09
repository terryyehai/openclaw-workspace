#!/usr/bin/env python3
"""
使用一般 Selenium 連接到已存在的 Chrome
"""
import sys
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def connect_selenium():
    """使用 Selenium 連接到 Chrome"""
    print("=" * 60)
    print("Selenium 連接到 Chrome")
    print("=" * 60)
    
    try:
        # 連接到已存在的 Chrome
        print("\n[1] 連接到 Chrome...")
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:18800")
        
        driver = webdriver.Chrome(options=options)
        print("✓ 已連接!")
        
        # 獲取分頁
        print("\n[2] 分頁列表:")
        for i, handle in enumerate(driver.window_handles):
            print(f"   [{i}] {driver.title}")
        
        # 前往遊戲
        print("\n[3] 前往遊戲測試工具...")
        driver.get("https://gp001-qa1-simulation.xwautc.online/index")
        time.sleep(3)
        
        # 截圖
        driver.save_screenshot("/tmp/selenium_game.png")
        print("   截圖: /tmp/selenium_game.png")
        
        print("\n" + "=" * 60)
        print("按 Enter 關閉")
        print("=" * 60)
        
        input()
        driver.quit()
        
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    connect_selenium()
