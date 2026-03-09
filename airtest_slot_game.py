#!/usr/bin/env python3
"""
Selenium + Chrome 遊戲自動化測試
登入 → PLAY REAL → SPIN 10 次
"""
import sys
import os
import time

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

def run_slot_game_test():
    """執行 Slot Game 自動化測試"""
    print("=" * 60)
    print("Slot Game 自動化測試")
    print("=" * 60)
    
    try:
        # 使用 Selenium 連接 Chrome
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("\n[1] 連接 Chrome...")
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:18800")
        driver = webdriver.Chrome(options=options)
        print("   ✓ 已連接 Chrome")
        
        # 2. 前往遊戲測試工具
        print("\n[2] 前往遊戲測試工具...")
        driver.get("https://gp001-qa1-simulation.xwautc.online/index")
        time.sleep(3)
        driver.save_screenshot("/tmp/airtest_login.png")
        
        # 3. 填寫表單
        print("\n[3] 填寫登入資訊...")
        
        # 選擇 Agent
        driver.execute_script("document.querySelectorAll('[role=\"combobox\"]')[0].click()")
        time.sleep(500)
        driver.execute_script("""
            const opts = document.querySelectorAll('[role="option"]');
            for(let o of opts) { if(o.textContent.includes('Jmeter總控台')) { o.click(); break; } }
        """)
        time.sleep(500)
        
        # 選擇 Sub Agent
        driver.execute_script("document.querySelectorAll('[role=\"combobox\"]')[1].click()")
        time.sleep(500)
        driver.execute_script("""
            const opts = document.querySelectorAll('[role="option"]');
            for(let o of opts) { if(o.textContent.includes('PHP')) { o.click(); break; } }
        """)
        time.sleep(500)
        
        # 填寫 Account
        driver.execute_script("""
            const inputs = document.querySelectorAll('input[type="text"]');
            for(let inp of inputs) { inp.value = 'PHP123456789'; }
        """)
        time.sleep(500)
        
        # 選擇 Game ID
        driver.execute_script("document.querySelectorAll('[role=\"combobox\"]')[2].click()")
        time.sleep(500)
        driver.execute_script("""
            const opts = document.querySelectorAll('[role="option"]');
            for(let o of opts) { if(o.textContent.includes('230001')) { o.click(); break; } }
        """)
        time.sleep(500)
        
        # 選擇 Language
        driver.execute_script("document.querySelectorAll('[role=\"combobox\"]')[3].click()")
        time.sleep(500)
        driver.execute_script("""
            const opts = document.querySelectorAll('[role="option"]');
            for(let o of opts) { if(o.textContent.includes('English')) { o.click(); break; } }
        """)
        time.sleep(500)
        
        driver.save_screenshot("/tmp/airtest_form_filled.png")
        print("   ✓ 表單填寫完成")
        
        # 4. 點擊 Login
        print("\n[4] 點擊 Login...")
        driver.execute_script("""
            const btns = document.querySelectorAll('button');
            for(let b of btns) { if(b.textContent.includes('Login')) { b.click(); break; } }
        """)
        time.sleep(8)
        driver.save_screenshot("/tmp/airtest_logged_in.png")
        
        # 5. 進入遊戲
        print("\n[5] 進入遊戲...")
        time.sleep(10)
        
        try:
            driver.execute_script("""
                const els = document.querySelectorAll('button, div');
                for(let e of els) { if(e.textContent.includes('Play Now')) { e.click(); break; } }
            """)
            time.sleep(10)
        except Exception as e:
            print(f"   ⚠️ Play Now: {e}")
        
        driver.save_screenshot("/tmp/airtest_game_loaded.png")
        
        # 6. SPIN 10 次
        print("\n[6] 開始 SPIN 10 次...")
        
        results = []
        
        for i in range(10):
            print(f"   SPIN #{i+1}...", end=" ", flush=True)
            
            try:
                driver.execute_script("""
                    const btns = document.querySelectorAll('button');
                    for(let b of btns) { if(b.textContent === 'SPIN') { b.click(); break; } }
                """)
                time.sleep(3)
                driver.save_screenshot(f"/tmp/airtest_spin_{i+1}.png")
                print("✓")
                results.append("SPIN")
            except Exception as e:
                print(f"⚠️ {e}")
                results.append("FAIL")
        
        # 總結
        print("\n" + "=" * 60)
        print("測試結果")
        print("=" * 60)
        
        success = sum(1 for r in results if r == "SPIN")
        print(f"成功: {success}/10")
        
        print("\n截圖列表:")
        print("  /tmp/airtest_login.png")
        print("  /tmp/airtest_form_filled.png")
        print("  /tmp/airtest_logged_in.png")
        print("  /tmp/airtest_game_loaded.png")
        for i in range(10):
            print(f"  /tmp/airtest_spin_{i+1}.png")
        
        print("\n請確認遊戲畫面是否正常顯示")
        
        driver.quit()
        
    except Exception as e:
        print(f"✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_slot_game_test()
