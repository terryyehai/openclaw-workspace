#!/usr/bin/env python3
"""
AI 視覺識別點擊系統
使用 PIL + 簡單的圖像處理識別按鈕
"""
import os
import sys
import json

# 使用 PIL 代替 cv2
from PIL import Image, ImageDraw, ImageEnhance
import numpy as np

class SimpleVisionClicker:
    def __init__(self):
        self.buttons = {}
        
    def find_button_by_color(self, image_path):
        """使用顏色識別按鈕"""
        img = Image.open(image_path)
        img = img.convert('RGB')
        width, height = img.size
        
        # 獲取像素數據
        pixels = np.array(img)
        
        # 找底部中央的亮色區域 (常見的 SPIN 按鈕位置)
        # 假設按鈕在底部 1/3 區域
        
        bottom_region = pixels[height*2//3:height, :]
        
        # 找亮度高的區域
        brightness = np.mean(bottom_region, axis=2)
        
        # 找到最亮的區域中心
        max_pos = np.unravel_index(np.argmax(brightness), brightness.shape)
        
        # 轉換座標
        x = int(max_pos[1])
        y = int(max_pos[0] + height*2//3)
        
        return {
            'x': x,
            'y': y,
            'method': 'brightness',
            'confidence': 0.5
        }
    
    def find_button_by_template(self, image_path):
        """簡單的模板匹配"""
        img = Image.open(image_path)
        width, height = img.size
        
        # 根據統計，SPIN 按鈕通常在底部中央
        # 典型位置: x ~ width/2, y ~ height * 0.85
        
        spin_x = width // 2
        spin_y = int(height * 0.85)
        
        return {
            'x': spin_x,
            'y': spin_y,
            'method': 'statistical',
            'confidence': 0.6,
            'note': '根據統計學預測的 SPIN 按鈕位置'
        }
    
    def analyze_image(self, image_path):
        """分析圖像"""
        img = Image.open(image_path)
        width, height = img.size
        
        print(f"圖片大小: {width} x {height}")
        
        # 分析底部區域
        bottom = img.crop((0, height*2//3, width, height))
        bottom_width, bottom_height = bottom.size
        
        # 轉為灰度
        gray = bottom.convert('L')
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(2)
        
        # 找亮斑
        pixels = np.array(enhanced)
        
        # 找高於閾值的區域
        threshold = np.mean(pixels) + np.std(pixels)
        bright = pixels > threshold
        
        # 找輪廓
        from scipy import ndimage
        
        labeled, num_features = ndimage.label(bright)
        
        if num_features > 0:
            # 找到最大的區域
            sizes = ndimage.sum(bright, labeled, range(1, num_features + 1))
            largest = np.argmax(sizes) + 1
            
            # 找到該區域的中心
            region = (labeled == largest)
            y_indices, x_indices = np.where(region)
            
            cx = int(np.mean(x_indices))
            cy = int(np.mean(y_indices))
            
            # 轉換到完整圖片座標
            x = cx
            y = cy + height*2//3
            
            return {
                'x': x,
                'y': y,
                'method': 'brightness_detection',
                'confidence': 0.7,
                'note': '檢測到底部亮區，可能是按鈕'
            }
        
        # 如果沒找到，使用統計預測
        return self.find_button_by_template(image_path)
    
    def get_click_position(self, image_path):
        """獲取點擊位置"""
        result = self.analyze_image(image_path)
        
        if result:
            print(f"\n識別結果:")
            print(f"  方法: {result['method']}")
            print(f"  座標: ({result['x']}, {result['y']})")
            print(f"  信心度: {result['confidence']}")
            if 'note' in result:
                print(f"  備註: {result['note']}")
            
            return (result['x'], result['y'])
        
        return None

def main():
    clicker = SimpleVisionClicker()
    
    if len(sys.argv) < 2:
        # 使用最新的截圖
        import glob
        screenshots = sorted(glob.glob('/home/terry/.openclaw/media/browser/*.png'))
        if screenshots:
            image_path = screenshots[-1]
        else:
            print("沒有找到截圖")
            sys.exit(1)
    else:
        image_path = sys.argv[1]
    
    print(f"分析圖片: {image_path}")
    
    position = clicker.get_click_position(image_path)
    
    if position:
        # 保存座標
        coords = {'SPIN': {'x': position[0], 'y': position[1]}}
        with open('/tmp/vision_button_coords.json', 'w') as f:
            json.dump(coords, f, indent=2)
        print(f"\n座標已保存到 /tmp/vision_button_coords.json")
    else:
        print("無法識別按鈕位置")

if __name__ == "__main__":
    main()
