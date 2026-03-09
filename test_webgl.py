#!/usr/bin/env python3
"""
遊戲自動化 - 多種 WebGL 渲染方案測試
嘗試不同的渲染參數來解決黑屏問題
"""
import sys
import os

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

from playwright.sync_api import sync_playwright

def test_different_webgl_modes():
    """測試不同的 WebGL 渲染模式"""
    
    webgl_modes = [
        {
            "name": "Desktop OpenGL",
            "args": [
                '--use-gl=desktop',
                '--ignore-gpu-blocklist',
                '--enable-webgl',
            ]
        },
        {
            "name": "EGL",
            "args": [
                '--use-gl=egl',
                '--ignore-gpu-blocklist',
                '--enable-webgl',
            ]
        },
        {
            "name": "ANGLE (Direct3D on Windows, OpenGL on others)",
            "args": [
                '--use-angle=default',
                '--ignore-gpu-blocklist',
                '--enable-webgl',
            ]
        },
        {
            "name": "Swiftshader (Software Rendering)",
            "args": [
                '--use-gl=swiftshader',
                '--enable-webgl',
            ]
        },
        {
            "name": "Disabled GPU (for comparison)",
            "args": [
                '--disable-gpu',
                '--disable-software-rasterizer',
            ]
        },
    ]
    
    for mode in webgl_modes:
        print(f"\n{'='*60}")
        print(f"測試模式: {mode['name']}")
        print(f"{'='*60}")
        
        playwright = sync_playwright().start()
        
        try:
            browser = playwright.chromium.launch(
                headless=False,
                executable_path='/usr/bin/google-chrome-stable',
                args=mode['args'] + [
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )
            
            context = browser.new_context()
            page = context.new_page()
            
            # 前往遊戲
            page.goto("https://gp001-qa1-simulation.xwautc.online/index")
            page.wait_for_timeout(3000)
            
            # 截圖
            screenshot_path = f"/tmp/game_{mode['name'].replace(' ', '_')}.png"
            page.screenshot(path=screenshot_path)
            print(f"截圖: {screenshot_path}")
            
            print("瀏覽器將保持打開 30 秒，請觀察遊戲是否正常顯示...")
            page.wait_for_timeout(30000)
            
            browser.close()
            
        except Exception as e:
            print(f錯誤: {e}")
        
        playwright.stop()
        
        response = input(f"模式 {mode['name']} 是否正常顯示? (y/n/q 離開): ")
        if response.lower() == 'q':
            break
        elif response.lower() == 'y':
            print(f"✓ 找到有效的模式: {mode['name']}")
            print(f"參數: {mode['args']}")
            break

def test_with_network_logging():
    """測試並記錄網路請求"""
    print("\n" + "="*60)
    print("測試網路請求日誌")
    print("="*60)
    
    playwright = sync_playwright().start()
    
    browser = playwright.chromium.launch(
        headless=False,
        executable_path='/usr/bin/google-chrome-stable',
        args=[
            '--use-gl=desktop',
            '--ignore-gpu-blocklist',
            '--enable-webgl',
            '--no-sandbox',
        ]
    )
    
    context = browser.new_context()
    page = context.new_page()
    
    # 記錄所有請求
    requests = []
    page.on("request", lambda req: requests.append({
        "url": req.url,
        "method": req.method,
        "status": req.response.status if req.response else "pending"
    }))
    
    page.goto("https://gp001-qa1-simulation.xwautc.online/index")
    page.wait_for_timeout(5000)
    
    # 打印請求
    print(f"\n總請求數: {len(requests)}")
    
    # 過濾遊戲相關請求
    game_requests = [r for r in requests if 'game' in r['url'].lower() or '230001' in r['url']]
    
    print(f"\n遊戲相關請求:")
    for req in game_requests[:10]:
        print(f"  [{req['status']}] {req['method']} {req['url'][:80]}")
    
    # 檢查失敗的請求
    failed = [r for r in requests if r['status'] >= 400]
    if failed:
        print(f"\n失敗的請求:")
        for req in failed[:5]:
            print(f"  [{req['status']}] {req['url'][:80]}")
    
    print("\n瀏覽器保持打開，按 Enter 關閉...")
    input()
    
    browser.close()
    playwright.stop()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "network":
            test_with_network_logging()
        else:
            test_different_webgl_modes()
    else:
        test_different_webgl_modes()
