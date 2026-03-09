#!/usr/bin/env python3
"""
AI 視覺識別點擊系統
使用視覺模型識別遊戲中的按鈕位置
"""
import cv2
import numpy as np
import base64
import json
import os
import sys

class AIVisionClicker:
    def __init__(self):
        self.model = None
        self.loaded = False
        
    def load_model(self):
        """加載視覺識別模型"""
        try:
            # 嘗試加載 YOLO 或其他模型
            import torch
            print("PyTorch 可用")
            
            # 檢查是否有本地模型
            model_path = os.path.expanduser("~/.openclaw/ai-operator/models/button_detector.onnx")
            if os.path.exists(model_path):
                print(f"找到本地模型: {model_path}")
            else:
                print("沒有本地模型，將使用 API")
                
            self.loaded = True
        except ImportError:
            print("PyTorch 不可用")
    
    def encode_image(self, image_path):
        """將圖片編碼為 base64"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def call_vision_api(self, image_path, prompt):
        """調用視覺 API 識別按鈕"""
        # 這裡可以替換為實際的 API 調用
        # 例如 OpenAI GPT-4V, Claude Vision, 或本地模型
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
            
        import requests
        
        # 編碼圖片
        with open(image_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        # 調用 OpenAI API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{prompt}\n\n請回覆 JSON 格式: {{\"button_name\": \"按鈕名稱\", \"x\": 中心X座標, \"y\": 中心Y座標, \"confidence\": 0.0-1.0}}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # 解析 JSON
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                    
        except Exception as e:
            print(f"API 調用失敗: {e}")
            
        return None
    
    def find_button_ai(self, image_path, button_name=None):
        """使用 AI 識別按鈕"""
        prompt = f"這是一個遊戲截圖。請識別以下內容:\n"
        
        if button_name:
            prompt += f"1. 找到 '{button_name}' 按鈕的位置 (中心 X, Y 座標)\n"
        else:
            prompt += f"1. 找到所有可點擊的按鈕位置\n"
        
        prompt += """
2. 如果找到按鈕，請提供:
   - 按鈕名稱
   - 中心 X 座標 (圖片寬度範圍內)
   - 中心 Y 座標 (圖片高度範圍內)
   - 信心度 (0-1)

圖片分辨率大約是 1920x1080。
"""
        
        # 嘗試調用 API
        result = self.call_vision_api(image_path, prompt)
        
        if result:
            print(f"AI 識別結果: {result}")
            return result
        
        return None
    
    def find_button_heuristic(self, image_path):
        """使用啟發式方法識別按鈕"""
        img = cv2.imread(image_path)
        if img is None:
            return None
            
        h, w = img.shape[:2]
        
        # 使用顏色識別常見的按鈕顏色
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 按鈕常見顏色範圍
        color_ranges = {
            'green': (np.array([35, 50, 50]), np.array([85, 255, 255])),
            'blue': (np.array([100, 50, 50]), np.array([130, 255, 255])),
            'red': (np.array([0, 50, 50]), np.array([10, 255, 255])),
            'yellow': (np.array([20, 50, 50]), np.array([30, 255, 255])),
        }
        
        buttons_found = []
        
        for color_name, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, lower, upper)
            
            # 找輪廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                x, y, cw, ch = cv2.boundingRect(cnt)
                
                # 過濾太小的區域
                if cw < 50 or ch < 20:
                    continue
                    
                # 計算中心點
                cx, cy = x + cw // 2, y + ch // 2
                
                buttons_found.append({
                    'color': color_name,
                    'x': cx,
                    'y': cy,
                    'width': cw,
                    'height': ch,
                    'position': 'bottom_center' if cy > h * 0.7 else 'center'
                })
        
        # 優先返回底部中央的按鈕（通常是 SPIN）
        bottom_buttons = [b for b in buttons_found if b['position'] == 'bottom_center']
        
        if bottom_buttons:
            # 返回最寬的按鈕（通常是 SPIN）
            bottom_buttons.sort(key=lambda x: x['width'], reverse=True)
            return bottom_buttons[0]
        
        return buttons_found[0] if buttons_found else None

def main():
    clicker = AIVisionClicker()
    clicker.load_model()
    
    if len(sys.argv) < 2:
        print("使用方法: python ai_vision_clicker.py <圖片路徑> [按鈕名稱]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    button_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"分析圖片: {image_path}")
    
    # 方法1: AI API 識別
    if button_name:
        print(f"\n[方法1] AI 識別 '{button_name}'...")
        result = clicker.find_button_ai(image_path, button_name)
        if result:
            print(f"  結果: {result}")
        else:
            print(f"  API 不可用或識別失敗")
    
    # 方法2: 啟發式識別
    print(f"\n[方法2] 啟發式識別...")
    result = clicker.find_button_heuristic(image_path)
    if result:
        print(f"  結果: {result}")
        
        # 保存座標
        coords = {button_name or 'BUTTON': result}
        with open('/tmp/ai_button_coords.json', 'w') as f:
            json.dump(coords, f, indent=2)
        print(f"  已保存到 /tmp/ai_button_coords.json")
    else:
        print("  未找到按鈕")

if __name__ == "__main__":
    main()
