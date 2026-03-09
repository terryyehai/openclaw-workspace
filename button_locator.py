#!/usr/bin/env python3
"""
遊戲按鈕座標識別系統
使用 OCR + 影像辨識 找到遊戲中的按鈕位置
"""
import cv2
import pytesseract
import numpy as np
from PIL import Image
import json
import os

class GameButtonLocator:
    def __init__(self):
        self.coords_file = "/tmp/game_button_coords.json"
        self.buttons = self.load_coords()
        
    def load_coords(self):
        """載入已保存的座標"""
        if os.path.exists(self.coords_file):
            with open(self.coords_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_coords(self):
        """保存座標"""
        with open(self.coords_file, 'w') as f:
            json.dump(self.buttons, f, indent=2)
    
    def find_button_ocr(self, image_path, button_name):
        """使用 OCR 找按鈕"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pil_img = Image.fromarray(gray)
        
        data = pytesseract.image_to_data(pil_img, lang='eng', output_type=pytesseract.Output.DICT)
        
        for i, txt in enumerate(data['text']):
            if button_name.upper() in txt.upper():
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                conf = float(data['conf'][i])
                if conf > 30:
                    cx, cy = x + w//2, y + h//2
                    return {'x': cx, 'y': cy, 'width': w, 'height': h, 'confidence': conf}
        return None
    
    def find_button_color(self, image_path, button_name):
        """使用顏色找按鈕"""
        img = cv2.imread(image_path)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 根據按鈕名稱選擇顏色範圍
        color_ranges = {
            'SPIN': {'lower': np.array([0, 100, 100]), 'upper': np.array([10, 255, 255])},  # 紅色
            'PLAY': {'lower': np.array([100, 100, 100]), 'upper': np.array([130, 255, 255])},  # 藍色
        }
        
        if button_name.upper() not in color_ranges:
            return None
            
        lower = color_ranges[button_name.upper()]['lower']
        upper = color_ranges[button_name.upper()]['upper']
        mask = cv2.inRange(hsv, lower, upper)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if 50 < w < 400 and 20 < h < 150:
                cx, cy = x + w//2, y + h//2
                return {'x': cx, 'y': cy, 'width': w, 'height': h}
        
        return None
    
    def find_button_template(self, image_path, template_path):
        """使用模板匹配找按鈕"""
        img = cv2.imread(image_path)
        template = cv2.imread(template_path)
        
        if template is None:
            return None
            
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.8:
            w, h = template.shape[1], template.shape[0]
            cx, cy = max_loc[0] + w//2, max_loc[1] + h//2
            return {'x': cx, 'y': cy, 'width': w, 'height': h, 'confidence': max_val}
        
        return None
    
    def register_button(self, name, x, y, width=None, height=None):
        """手動註冊按鈕座標"""
        self.buttons[name] = {
            'x': x,
            'y': y,
            'width': width or 100,
            'height': height or 50
        }
        self.save_coords()
        print(f"✓ 已註冊按鈕: {name} at ({x}, {y})")
    
    def get_button(self, name):
        """取得按鈕座標"""
        return self.buttons.get(name)

def main():
    locator = GameButtonLocator()
    
    # 測試
    import sys
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        button_name = sys.argv[2] if len(sys.argv) > 2 else 'SPIN'
        
        # 嘗試 OCR
        result = locator.find_button_ocr(image_path, button_name)
        if result:
            print(f"OCR 找到 {button_name}: {result}")
            locator.register_button(button_name, result['x'], result['y'], result.get('width'), result.get('height'))
        else:
            print(f"OCR 未找到 {button_name}")
    else:
        print("使用方法: python button_locator.py <圖片路徑> [按鈕名稱]")
        print(f"\\n已保存的按鈕: {list(locator.buttons.keys())}")

if __name__ == "__main__":
    main()
