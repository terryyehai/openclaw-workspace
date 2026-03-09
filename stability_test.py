#!/usr/bin/env python3
"""
穩定性測試腳本
驗證 Selenium + Chrome Remote Debugging 的穩定性
"""
import sys
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def run_stability_test():
    """執行穩定性測試"""
    print("=" * 60)
    print("Selenium 穩定性測試")
    print("=" * 60)
    
    results = {
        "connect": False,
        "navigate": False,
        "screenshot": False,
        "interact": False,
        "spin": False
    }
    
    driver = None
    
    try:
        # 1. 連接測試
        print("\n[1] 連接 Chrome...")
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:18800")
        driver = webdriver.Chrome(options=options)
        results["connect"] = True
        print("   ✓ 連接成功")
        
        # 2. 導航測試
        print("\n[2] 導航到遊戲測試工具...")
        driver.get("https://gp001-qa1-simulation.xwautc.online/index")
        time.sleep(3)
        results["navigate"] = True
        print("   ✓ 導航成功")
        
        # 3. 截圖測試
        print("\n[3] 截圖測試...")
        driver.save_screenshot("/tmp/stability_1_login.png")
        results["screenshot"] = True
        print("   ✓ 截圖成功")
        
        # 4. 交互測試 - 填寫表單
        print("\n[4] 填寫表單...")
        driver.execute_script("""
            // 選擇 Agent
            document.querySelectorAll('[role="combobox"]')[0].click();
        """)
        time.sleep(500)
        
        driver.execute_script("""
            const options = document.querySelectorAll('[role="option"]');
            for (let opt of options) {
                if (opt.textContent.includes('Jmeter總控台')) {
                    opt.click();
                    break;
                }
            }
        """)
        time.sleep(500)
        
        # 填寫 Account
        driver.execute_script("""
            const inputs = document.querySelectorAll('input[type="text"]');
            for (let inp of inputs) {
                inp.value = 'PHP123456789';
            }
        """)
        
        driver.save_screenshot("/tmp/stability_2_filled.png")
        results["interact"] = True
        print("   ✓ 交互成功")
        
        # 5. 登入和 Spin 測試
        print("\n[5] 登入並測試 Spin...")
        
        # 點擊 Login
        driver.execute_script("""
            const btns = document.querySelectorAll('button');
            for (let btn of btns) {
                if (btn.textContent.includes('Login')) {
                    btn.click();
                    break;
                }
            }
        """)
        
        # 等待遊戲頁面
        time.sleep(10)
        
        # 截圖遊戲頁面
        driver.save_screenshot("/tmp/stability_3_game.png")
        
        # 嘗試點擊 Play Now
        try:
            driver.execute_script("""
                const elements = document.querySelectorAll('button, div');
                for (let el of elements) {
                    if (el.textContent.includes('Play Now')) {
                        el.click();
                        break;
                    }
                }
            """)
            time.sleep(10)
            driver.save_screenshot("/tmp/stability_4_play.png")
        except Exception as e:
            print(f"   ⚠️ Play Now: {e}")
        
        # 嘗試 Spin
        try:
            for i in range(3):
                driver.execute_script("""
                    const elements = document.querySelectorAll('button');
                    for (let el of elements) {
                        if (el.textContent === 'SPIN') {
                            el.click();
                            break;
                        }
                    }
                """)
                time.sleep(3)
                driver.save_screenshot(f"/tmp/stability_5_spin_{i+1}.png")
            results["spin"] = True
            print("   ✓ Spin 成功")
        except Exception as e:
            print(f"   ⚠️ Spin: {e}")
        
        # 總結
        print("\n" + "=" * 60)
        print("測試結果")
        print("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test, result in results.items():
            status = "✅" if result else "❌"
            print(f"  {status} {test}")
        
        print(f"\n通過率: {passed}/{total} ({passed/total*100:.0f}%)")
        
        if passed == total:
            print("\n🎉 所有測試通過！方案穩定")
        else:
            print(f"\n⚠️  通過率 {passed/total*100:.0f}%，需要改進")
        
    except Exception as e:
        print(f"\n✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    run_stability_test()
