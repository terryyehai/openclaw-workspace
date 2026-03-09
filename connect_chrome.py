#!/usr/bin/env python3
"""
連接到已存在的 Chrome 瀏覽器
使用 Chrome Remote Debugging 而不是啟動新的瀏覽器
"""
import sys
import os

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

from playwright.sync_api import sync_playwright

def connect_to_existing_chrome():
    """連接到已存在的 Chrome"""
    print("=" * 60)
    print("連接到已存在的 Chrome 瀏覽器")
    print("=" * 60)
    
    playwright = sync_playwright().start()
    
    try:
        # 嘗試連接到已存在的 Chrome (remote-debugging-port)
        browser = playwright.chromium.connect_over_cdp(
            "http://127.0.0.1:18800"
        )
        print("✓ 已連接到 Chrome!")
        
    except Exception as e:
        print(f"✗ 連接失敗: {e}")
        print("\n請先手動開啟 Chrome:")
        print('  google-chrome-stable --remote-debugging-port=18800')
        browser = None
    
    if browser:
        print("\n可用分頁:")
        for page in browser.contexts[0].pages:
            print(f"  - {page.url}")
        
        print("\n請告訴我要操作哪個分頁")
    
    playwright.stop()

def launch_chrome_with_debugging():
    """使用 Remote Debugging 啟動 Chrome"""
    print("=" * 60)
    print("使用 Remote Debugging 啟動 Chrome")
    print("=" * 60)
    
    import subprocess
    
    # 使用 remote-debugging-port 啟動 Chrome
    cmd = [
        'google-chrome-stable',
        '--remote-debugging-port=18800',
        '--no-first-run',
        '--no-default-browser-check',
        '--user-data-dir=/tmp/chrome-debug',
    ]
    
    print(f"啟動命令: {' '.join(cmd)}")
    
    try:
        proc = subprocess.Popen(cmd)
        print(f"✓ Chrome 已啟動 (PID: {proc.pid})")
        print("等待瀏覽器就緒...")
        import time
        time.sleep(3)
        
        # 嘗試連接
        playwright = sync_playwright().start()
        browser = playwright.chromium.connect_over_cdp(
            "http://127.0.0.1:18800"
        )
        print("✓ 已連接到 Chrome!")
        
        # 前往遊戲網站
        page = browser.contexts[0].new_page()
        page.goto("https://gp001-qa1-simulation.xwautc.online/index")
        
        print("✓ 已打開遊戲測試工具")
        print("\n請在瀏覽器中操作，按 Enter 結束...")
        input()
        
        browser.close()
        playwright.stop()
        
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "connect":
        connect_to_existing_chrome()
    else:
        launch_chrome_with_debugging()
