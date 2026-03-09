#!/usr/bin/env python3
"""
簡化穩定性測試
專注測試核心功能
"""
import sys
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def simple_stability_test():
    """簡化穩定性測試"""
    print("=" * 60)
    print("Selenium 核心功能穩定性測試")
    print("=" * 60)
    
    tests = {
        "connection": {"name": "Chrome 連接", "passed": False, "time": 0},
        "navigation": {"name": "網頁導航", "passed": False, "time": 0},
        "screenshot": {"name": "截圖功能", "passed": False, "time": 0},
        "reconnect": {"name": "重新連接", "passed": False, "time": 0},
    }
    
    driver = None
    
    try:
        # 測試 1: 連接
        print("\n[1] 測試 Chrome 連接...")
        start = time.time()
        options = Options()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:18800")
        driver = webdriver.Chrome(options=options)
        tests["connection"]["time"] = round((time.time() - start) * 1000)
        tests["connection"]["passed"] = True
        print(f"   ✓ 連接成功 ({tests['connection']['time']}ms)")
        
        # 測試 2: 導航
        print("\n[2] 測試網頁導航...")
        start = time.time()
        driver.get("https://gp001-qa1-simulation.xwautc.online/index")
        time.sleep(2)
        tests["navigation"]["time"] = round((time.time() - start) * 1000)
        tests["navigation"]["passed"] = True
        print(f"   ✓ 導航成功 ({tests['navigation']['time']}ms)")
        
        # 測試 3: 截圖
        print("\n[3] 測試截圖功能...")
        start = time.time()
        driver.save_screenshot("/tmp/test_screenshot.png")
        tests["screenshot"]["time"] = round((time.time() - start) * 1000)
        tests["screenshot"]["passed"] = os.path.exists("/tmp/test_screenshot.png")
        print(f"   ✓ 截圖成功 ({tests['screenshot']['time']}ms)")
        
        # 關閉並重新連接
        print("\n[4] 測試重新連接...")
        driver.quit()
        time.sleep(1)
        
        start = time.time()
        driver = webdriver.Chrome(options=options)
        tests["reconnect"]["time"] = round((time.time() - start) * 1000)
        tests["reconnect"]["passed"] = True
        print(f"   ✓ 重新連接成功 ({tests['reconnect']['time']}ms)")
        
        # 總結
        print("\n" + "=" * 60)
        print("測試結果總結")
        print("=" * 60)
        
        passed = sum(1 for t in tests.values() if t["passed"])
        total = len(tests)
        
        for key, test in tests.items():
            status = "✅" if test["passed"] else "❌"
            print(f"  {status} {test['name']}: {test['time']}ms")
        
        print(f"\n通過率: {passed}/{total} ({passed/total*100:.0f}%)")
        
        if passed == total:
            print("\n🎉 方案穩定！所有核心功能正常")
            return True
        else:
            print(f"\n⚠️  通過率 {passed/total*100:.0f}%")
            return False
        
    except Exception as e:
        print(f"\n✗ 測試失敗: {e}")
        return False
    
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    success = simple_stability_test()
    sys.exit(0 if success else 1)
