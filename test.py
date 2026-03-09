#!/usr/bin/env python3
"""
測試腳本 - 測試 AI Operator 系統
"""
import sys
import os

# 加入路徑
sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

from browser.playwright_controller import BrowserController

def test_browser():
    """測試瀏覽器"""
    print("正在啟動瀏覽器...")
    browser = BrowserController(headless=False)
    
    print("正在開啟網頁...")
    browser.open("https://gp001-qa1-simulation.xwautc.online/index")
    
    print("正在截圖...")
    browser.screenshot("/tmp/ai-operator-test.png")
    
    print("截圖完成: /tmp/ai-operator-test.png")
    print("按 Enter 關閉瀏覽器...")
    input()
    
    browser.close()
    print("完成!")

if __name__ == "__main__":
    test_browser()
