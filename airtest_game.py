#!/usr/bin/env python3
"""
Airtest 遊戲自動化
使用影像辨識和 OCR 點擊遊戲按鈕
"""
import sys
import os
import time
import json

sys.path.insert(0, os.path.expanduser("~/.openclaw/ai-operator"))

from airtest.core.api import *
from airtest.aircv import *
import cv2
import pytesseract
import numpy as np

class GameAutoPlayer:
    def __init__(self):
        self.coords_file = "/tmp/game_button_coords.json"
        self.buttons = self.load_coords()
        
    def load_coords(self):
        """載入按鈕座標"""
        if os.path.exists(self.coords_file):
            with open(self.coords_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_coords(self):
        """保存按鈕座標"""
        with open(self.coords_file, 'w') as f:
            json.dump(self.buttons, f, indent=2)
    
    def ocr_find_button(self, screenshot_path, button_name):
        """使用 OCR 找按鈕"""
        img = cv2.imread(screenshot_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 增強對比
        equ = cv2.equalizeHist(gray)
        
        # OCR
        data = pytesseract.image_to_data(equ, lang='eng', output_type=pytesseract.Output.DICT)
        
        for i, txt in enumerate(data['text']):
            if button_name.upper() in txt.upper():
                conf = float(data['conf'][i])
                if conf > 30:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    return (x + w//2, y + h//2)
        return None
    
    def template_match(self, screenshot_path, template_path, threshold=0.8):
        """模板匹配"""
        img = cv2.imread(screenshot_path)
        template = cv2.imread(template_path)
        
        if template is None:
            return None
            
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > threshold:
            w, h = template.shape[1], template.shape[0]
            return (max_loc[0] + w//2, max_loc[1] + h//2)
        return None
    
    def click_button(self, button_name, screenshot_path):
        """點擊按鈕"""
        # 1. 先檢查已保存的座標
        if button_name in self.buttons:
            coords = self.buttons[button_name]
            x, y = coords['x'], coords['y']
            print(f"使用保存的座標: ({x}, {y})")
            touch(Template(f"/tmp/{button_name}_btn.png"))
            return True
        
        # 2. 嘗試 OCR
        coords = self.ocr_find_button(screenshot_path, button_name)
        if coords:
            print(f"OCR 找到 {button_name}: {coords}")
            touch(Template(screenshot_path, record_pos=coords, resolution=(1920, 1080)))
            return True
        
        # 3. 嘗試模板匹配
        template_path = f"/tmp/{button_name}_btn.png"
        coords = self.template_match(screenshot_path, template_path)
        if coords:
            print(f"模板匹配找到 {button_name}: {coords}")
            touch(Template(screenshot_path, record_pos=coords, resolution=(1920, 1080)))
            return True
        
        print(f"無法找到按鈕: {button_name}")
        return False
    
    def register_button(self, button_name, x, y):
        """手動註冊按鈕"""
        self.buttons[button_name] = {'x': x, 'y': y}
        self.save_coords()
        print(f"✓ 已註冊按鈕: {button_name} at ({x}, {y})")

def run_game_test():
    """執行遊戲測試"""
    print("=" * 60)
    print("Airtest 遊戲自動化測試")
    print("=" * 60)
    
    # 連接設備 - 使用 Selenium WebDriver
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    print("\n[1] 連接 Chrome...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:18800")
    driver = webdriver.Chrome(options=options)
    print("   ✓ 已連接")
    
    # 前往遊戲
    print("\n[2] 前往遊戲...")
    driver.get("https://gp001-qa1-simulation.xwautc.online/index")
    time.sleep(5)
    
    # 填寫表單、登入、進入遊戲 (省略詳細過程)
    # ...
    
    # 等待遊戲載入
    time.sleep(15)
    
    # 截圖
    screenshot_path = "/tmp/airtest_game.png"
    driver.save_screenshot(screenshot_path)
    
    # 使用 Airtest 點擊
    print("\n[3] 使用 Airtest 點擊 SPIN...")
    player = GameAutoPlayer()
    
    # 嘗試點擊
    # 注意: 這需要 Selenium 和 Airtest 結合
    # 目前階段，游戲在 iframe 中，需要特殊處理
    
    driver.quit()

if __name__ == "__main__":
    # 測試 OCR 功能
    player = GameAutoPlayer()
    result = player.ocr_find_button("/tmp/test.png", "SPIN")
    print(f"OCR 結果: {result}")
