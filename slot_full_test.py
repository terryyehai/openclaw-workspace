#!/usr/bin/env python3
"""
完整遊戲自動化腳本
登入 → PLAY REAL → SPIN 10 次
"""
import sys
import os
import time

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_and_click(driver, selector, by=By.XPATH, timeout=10):
    """等待元素出現并點擊"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        element.click()
        return True
    except Exception as e:
        print(f"   點擊失敗: {e}")
        return False

def run_full_test():
    """執行完整測試"""
    print("=" * 60)
    print("Slot Game 自動化測試")
    print("=" * 60)
    
    # 連接 Chrome
    print("\n[1] 連接 Chrome...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:18800")
    driver = webdriver.Chrome(options=options)
    print("   ✓ 已連接")
    
    # 前往遊戲頁面
    print("\n[2] 前往遊戲測試工具...")
    driver.get("https://gp001-qa1-simulation.xwautc.online/index")
    time.sleep(3)
    
    # 截圖登錄頁面
    driver.save_screenshot("/tmp/slot_login.png")
    
    # 填寫表單
    print("\n[3] 填寫登入資訊...")
    
    # 選擇 Agent - 點擊第一個 combobox
    try:
        comboboxes = driver.find_elements(By.CSS_SELECTOR, '[role="combobox"]')
        if comboboxes:
            comboboxes[0].click()
            time.sleep(1)
            
            # 選擇 Jmeter總控台
            options = driver.find_elements(By.CSS_SELECTOR, '[role="option"]')
            for opt in options:
                if "Jmeter總控台" in opt.text:
                    opt.click()
                    break
            time.sleep(0.5)
    except Exception as e:
        print(f"   Agent: {e}")
    
    # 選擇 Sub Agent
    try:
        comboboxes = driver.find_elements(By.CSS_SELECTOR, '[role="combobox"]')
        if len(comboboxes) > 1:
            comboboxes[1].click()
            time.sleep(1)
            
            options = driver.find_elements(By.CSS_SELECTOR, '[role="option"]')
            for opt in options:
                if "PHP" in opt.text:
                    opt.click()
                    break
            time.sleep(0.5)
    except Exception as e:
        print(f"   Sub Agent: {e}")
    
    # 填寫 Account
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
        for inp in inputs:
            if inp.is_displayed():
                inp.clear()
                inp.send_keys("PHP123456789")
                break
    except Exception as e:
        print(f"   Account: {e}")
    
    # 選擇 Game ID
    try:
        comboboxes = driver.find_elements(By.CSS_SELECTOR, '[role="combobox"]')
        if len(comboboxes) > 2:
            comboboxes[2].click()
            time.sleep(1)
            
            options = driver.find_elements(By.CSS_SELECTOR, '[role="option"]')
            for opt in options:
                if "230001" in opt.text:
                    opt.click()
                    break
            time.sleep(0.5)
    except Exception as e:
        print(f"   Game ID: {e}")
    
    # 選擇 Language
    try:
        comboboxes = driver.find_elements(By.CSS_SELECTOR, '[role="combobox"]')
        if len(comboboxes) > 3:
            comboboxes[3].click()
            time.sleep(1)
            
            options = driver.find_elements(By.CSS_SELECTOR, '[role="option"]')
            for opt in options:
                if "English" in opt.text:
                    opt.click()
                    break
            time.sleep(0.5)
    except Exception as e:
        print(f"   Language: {e}")
    
    driver.save_screenshot("/tmp/slot_form.png")
    print("   ✓ 表單填寫完成")
    
    # 點擊 Login
    print("\n[4] 點擊 Login...")
    try:
        login_btns = driver.find_elements(By.TAG_NAME, "button")
        for btn in login_btns:
            if "Login" in btn.text:
                btn.click()
                break
    except Exception as e:
        print(f"   Login: {e}")
    
    # 等待遊戲頁面加載
    print("\n[5] 等待遊戲加載...")
    time.sleep(10)
    
    # 截圖登錄後頁面
    driver.save_screenshot("/tmp/slot_after_login.png")
    
    # 點擊 Play Now
    print("\n[6] 點擊 Play Now...")
    try:
        # 嘗試多種選擇器
        selectors = [
            "//button[contains(text(), 'Play')]",
            "//div[contains(text(), 'Play')]",
            "//button[contains(@class, 'play')]"
        ]
        
        for sel in selectors:
            try:
                elements = driver.find_elements(By.XPATH, sel)
                for el in elements:
                    if el.is_displayed():
                        el.click()
                        print("   ✓ Play Now 點擊成功")
                        break
            except:
                continue
    except Exception as e:
        print(f"   Play Now: {e}")
    
    time.sleep(10)
    driver.save_screenshot("/tmp/slot_game.png")
    
    # SPIN 10 次
    print("\n[7] SPIN 10 次...")
    results = []
    
    for i in range(10):
        print(f"   SPIN #{i+1}...", end=" ", flush=True)
        
        try:
            spin_btns = driver.find_elements(By.TAG_NAME, "button")
            for btn in spin_btns:
                if btn.text == "SPIN" and btn.is_displayed():
                    btn.click()
                    results.append("OK")
                    print("✓")
                    break
        except Exception as e:
            print(f"錯誤: {e}")
            results.append("FAIL")
        
        time.sleep(3)
        driver.save_screenshot(f"/tmp/slot_spin_{i+1}.png")
    
    # 總結
    print("\n" + "=" * 60)
    print("測試結果")
    print("=" * 60)
    
    success = sum(1 for r in results if r == "OK")
    print(f"成功: {success}/10")
    
    print("\n截圖:")
    print("  /tmp/slot_login.png - 登入頁面")
    print("  /tmp/slot_form.png - 表單填寫")
    print("  /tmp/slot_after_login.png - 登入後")
    print("  /tmp/slot_game.png - 遊戲頁面")
    for i in range(10):
        print(f"  /tmp/slot_spin_{i+1}.png")
    
    driver.quit()

if __name__ == "__main__":
    run_full_test()
