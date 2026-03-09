"""
Vision Engine - 螢幕截圖與 OCR 文字辨識
"""
import cv2
import pytesseract
from PIL import Image
import numpy as np

def read_text(image_path):
    """從圖片讀取文字"""
    img = cv2.imread(image_path)
    text = pytesseract.image_to_string(img, lang='eng+chi_tra')
    return text

def detect_elements(image_path):
    """偵測 UI 元素"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 簡單的邊緣偵測
    edges = cv2.Canny(gray, 100, 200)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    elements = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 20 and h > 10:  # 過濾太小區域
            elements.append({'x': x, 'y': y, 'width': w, 'height': h})
    
    return elements

def get_screen_size():
    """取得螢幕大小"""
    import subprocess
    result = subprocess.run(['xrandr'], capture_output=True, text=True)
    # 解析螢幕解析度
    for line in result.stdout.split('\n'):
        if '*' in line:
            res = line.split()[0]
            width, height = res.split('x')
            return int(width), int(height)
    return 1920, 1080  # 預設
