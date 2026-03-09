#!/usr/bin/env python3
"""
遊戲自動化測試 - 使用真實 Chrome + 反檢測
解決 Canvas/WebGL 黑畫面問題
"""
import sys
import os

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

from playwright.sync_api import sync_playwright

def run_game_test():
    """執行遊戲測試"""
    print("=" * 60)
    print("遊戲自動化測試 - 反檢測版本")
    print("=" * 60)
    
    playwright = sync_playwright().start()
    
    # 使用真實的 Chrome 而不是 Chromium
    browser = playwright.chromium.launch(
        headless=False,  # 非 headless 模式
        executable_path='/usr/bin/google-chrome-stable',  # 使用真實 Chrome
        args=[
            # 啟用硬體加速 (解決 WebGL/Canvas 問題)
            '--ignore-gpu-blocklist',
            '--enable-webgl',
            '--use-gl=desktop',
            '--enable-accelerated-2d-canvas',
            '--enable-gpu-rasterization',
            
            # 反檢測參數 (隱藏自動化特徵)
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--no-first-run',
            '--no-errno-broken',
            
            # 其他優化
            '--disable-dev-shm-usage',
            '--disable-component-extensions-with-background-pages',
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-sync',
            '--metrics-recording-only',
            '--no-default-browser-check',
        ],
        ignore_default_args=['--enable-automation']  # 隱藏 automation 標記
    )
    
    # 建立上下文 - 模擬真實用戶
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        ignore_https_errors=True,
        locale='zh-TW',
        timezone_id='Asia/Taipei',
        permissions=['geolocation', 'notifications'],
        extra_http_headers={
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
    )
    
    # 注入腳本隱藏 navigator.webdriver
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-TW', 'zh', 'en']
        });
        window.chrome = {
            runtime: {}
        };
    """)
    
    page = context.new_page()
    
    print("\n[1] 前往遊戲測試工具...")
    page.goto("https://gp001-qa1-simulation.xwautc.online/index")
    
    print("[2] 等待頁面載入...")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(3000)
    
    # 隱藏 automation 標記
    page.evaluate("""
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    """)
    
    page.screenshot(path="/tmp/game_page.png")
    print("[3] 截圖保存: /tmp/game_page.png")
    
    print("\n[4] 環境資訊:")
    print(f"   WebDriver: {page.evaluate('navigator.webdriver')}")
    print(f"   Platform: {page.evaluate('navigator.platform')}")
    
    print("\n" + "=" * 60)
    print("✓ 瀏覽器已啟動，請手動操作遊戲")
    print("按 Enter 關閉瀏覽器")
    print("=" * 60)
    
    try:
        input()
    except:
        pass
    
    browser.close()
    playwright.stop()

if __name__ == "__main__":
    run_game_test()
