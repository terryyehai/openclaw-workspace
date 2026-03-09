#!/usr/bin/env python3
"""
完整遊戲自動化流程 - 使用 JavaScript 直接操作表單
"""
import sys
import os

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

from playwright.sync_api import sync_playwright

def run_full_flow():
    """執行完整流程"""
    print("=" * 60)
    print("遊戲自動化 - 完整流程")
    print("=" * 60)
    
    playwright = sync_playwright().start()
    
    try:
        # 連接到已存在的 Chrome
        browser = playwright.chromium.connect_over_cdp(
            "http://127.0.0.1:18800"
        )
        print("✓ 已連接到 Chrome")
        
        # 創建新分頁
        page = browser.contexts[0].new_page()
        
        # 1. 前往遊戲測試工具
        print("\n[1] 前往遊戲測試工具...")
        page.goto("https://gp001-qa1-simulation.xwautc.online/index")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)
        
        print("[2] 使用 JavaScript 填寫表單...")
        
        # 使用 JavaScript 直接操作表單
        js_code = """
            // 選擇 Agent - 點擊第一個 combobox
            var combos = document.querySelectorAll('[role="combobox"]');
            if (combos[0]) {
                combos[0].click();
            }
        """
        page.evaluate(js_code)
        
        page.wait_for_timeout(1000)
        
        # 點擊 Agent 選項
        js_code2 = """
            var options = document.querySelectorAll('[role="option"]');
            for (var i = 0; i < options.length; i++) {
                if (options[i].textContent.includes('Jmeter總控台')) {
                    options[i].click();
                    break;
                }
            }
        """
        page.evaluate(js_code2)
        
        page.wait_for_timeout(500)
        
        # 選擇 Sub Agent
        js_code3 = """
            var combos = document.querySelectorAll('[role="combobox"]');
            if (combos[1]) {
                combos[1].click();
            }
        """
        page.evaluate(js_code3)
        
        page.wait_for_timeout(1000)
        
        js_code4 = """
            var options = document.querySelectorAll('[role="option"]');
            for (var i = 0; i < options.length; i++) {
                if (options[i].textContent.includes('PHP')) {
                    options[i].click();
                    break;
                }
            }
        """
        page.evaluate(js_code4)
        
        page.wait_for_timeout(500)
        
        # 填寫 Account
        js_code5 = """
            var inputs = document.querySelectorAll('input[type="text"]');
            for (var i = 0; i < inputs.length; i++) {
                inputs[i].value = 'PHP123456789';
                inputs[i].dispatchEvent(new Event('input', {bubbles: true}));
            }
        """
        page.evaluate(js_code5)
        
        page.wait_for_timeout(500)
        
        # 選擇 Game ID
        js_code6 = """
            var combos = document.querySelectorAll('[role="combobox"]');
            if (combos[2]) {
                combos[2].click();
            }
        """
        page.evaluate(js_code6)
        
        page.wait_for_timeout(1000)
        
        js_code7 = """
            var options = document.querySelectorAll('[role="option"]');
            for (var i = 0; i < options.length; i++) {
                if (options[i].textContent.includes('230001')) {
                    options[i].click();
                    break;
                }
            }
        """
        page.evaluate(js_code7)
        
        page.wait_for_timeout(500)
        
        # 選擇 Language
        js_code8 = """
            var combos = document.querySelectorAll('[role="combobox"]');
            if (combos[3]) {
                combos[3].click();
            }
        """
        page.evaluate(js_code8)
        
        page.wait_for_timeout(1000)
        
        js_code9 = """
            var options = document.querySelectorAll('[role="option"]');
            for (var i = 0; i < options.length; i++) {
                if (options[i].textContent.includes('English (en)')) {
                    options[i].click();
                    break;
                }
            }
        """
        page.evaluate(js_code9)
        
        page.wait_for_timeout(1000)
        
        # 截圖
        page.screenshot(path="/tmp/login_form.png")
        print("[3] 登入表單截圖: /tmp/login_form.png")
        
        # 點擊 Login
        print("[4] 點擊 Login...")
        js_code10 = """
            var buttons = document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {
                if (buttons[i].textContent.includes('Login')) {
                    buttons[i].click();
                    break;
                }
            }
        """
        page.evaluate(js_code10)
        
        # 等待新分頁
        page.wait_for_timeout(8000)
        
        # 切換到遊戲分頁
        if len(browser.contexts[0].pages) > 1:
            page = browser.contexts[0].pages[-1]
            print("[5] 遊戲分頁已打開")
        
        # 等待遊戲載入
        print("[6] 等待遊戲載入...")
        page.wait_for_timeout(15000)
        
        # 截圖
        page.screenshot(path="/tmp/game_loaded.png")
        print("[7] 遊戲截圖: /tmp/game_loaded.png")
        
        # 點擊 Play Now
        print("[8] 點擊 Play Now...")
        js_code11 = """
            var elements = document.querySelectorAll('button, div');
            for (var i = 0; i < elements.length; i++) {
                if (elements[i].textContent.includes('Play Now')) {
                    elements[i].click();
                    break;
                }
            }
        """
        page.evaluate(js_code11)
        
        page.wait_for_timeout(10000)
        
        # 截圖遊戲畫面
        page.screenshot(path="/tmp/game_screen.png")
        print("[9] 遊戲畫面截圖: /tmp/game_screen.png")
        
        # SPIN 5 次
        print("\n[10] SPIN 5 次...")
        
        for i in range(5):
            print(f"   SPIN #{i+1}...")
            
            js_spin = """
                var elements = document.querySelectorAll('button, div');
                for (var i = 0; i < elements.length; i++) {
                    if (elements[i].textContent === 'SPIN') {
                        elements[i].click();
                        break;
                    }
                }
            """
            page.evaluate(js_spin)
            
            page.wait_for_timeout(3000)
            page.screenshot(path=f"/tmp/spin_{i+1}.png")
            print(f"   ✓ SPIN #{i+1} 完成")
        
        print("\n" + "=" * 60)
        print("✓ 流程完成!")
        print("=" * 60)
        
        print("\n請確認遊戲畫面是否正常顯示（沒有黑屏）")
        print("按 Enter 關閉...")
        input()
        
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            browser.close()
        except:
            pass
        playwright.stop()

if __name__ == "__main__":
    run_full_flow()
